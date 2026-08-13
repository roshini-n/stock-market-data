# Stock Market Data Pipeline

End-to-end **medallion architecture** (Bronze → Silver → Gold) for stock market data on **AWS S3** and **Databricks**, with both **batch** (S&P 500 historical) and **realtime** (Finnhub) paths.

---

## Overview

| Path | Source | Landing | Processing | Analytics |
|------|--------|---------|------------|-----------|
| **Batch** | S&P 500 OHLCV CSV | S3 Bronze (CSV) | Databricks → Silver **Delta Lake** | Gold star schema (dims + fact) |
| **Realtime** | Finnhub quotes via NiFi | S3 Bronze (JSON) | Auto Loader → Silver Parquet | Gold realtime fact + date dim |

**Goal:** Ingest, clean, and model market data so it is analytics-ready for SQL, dashboards, and feature engineering (returns, moving averages, volatility).

---

## Architecture

```text
                         ┌──────────────────────────────┐
                         │         DATA SOURCES         │
                         │  S&P 500 CSV  │  Finnhub API │
                         └───────┬───────┴───────┬──────┘
                                 │               │
                    boto3 upload │               │ Apache NiFi
                                 ▼               ▼
              s3://stocks-bronze-layer/    raw/batch/*.csv
                                           raw/realtime_finnhub/*.json
                                 │               │
                                 ▼               ▼
                         ┌──────────────────────────────┐
                         │     DATABRICKS (PySpark)      │
                         │  validate · clean · transform│
                         │  Auto Loader (AvailableNow)  │
                         └───────┬───────────────┬──────┘
                                 │               │
                                 ▼               ▼
              s3://stocks-silver-layer/   processed/batch/   (Delta)
                                          processed/realtime/ (Parquet)
                                 │               │
                                 ▼               ▼
              s3://stocks-gold-layer/     dim_stock · dim_date
                                          fact_stock_prices
                                          fact_stock_prices_realtime
                                          dim_date_realtime
```

### Medallion layers

| Layer | Bucket | What lives here |
|-------|--------|-----------------|
| **Bronze** | `stocks-bronze-layer` | Raw CSV (batch) and Finnhub JSON (realtime) |
| **Silver** | `stocks-silver-layer` | Cleaned, typed, deduplicated data (batch as **Delta**) |
| **Gold** | `stocks-gold-layer` | Star schema + engineered features for analytics |

---

## Tech stack

- **Compute:** Databricks, Apache Spark (PySpark)
- **Storage:** AWS S3
- **Table format:** Delta Lake (batch silver), Parquet (gold / realtime silver)
- **Streaming ingest:** Databricks Auto Loader (`cloudFiles`)
- **External ingest:** Apache NiFi (Finnhub → S3)
- **APIs:** Finnhub REST quote API
- **Local tooling:** Python, pandas, boto3, requests
- **WIP:** Amazon Kinesis producer (`stock-market-realtime`, `us-east-1`)

---

## Repository structure

```text
stock-market-data/
├── data/raw/                    # Local S&P 500 CSV (gitignored)
├── notebooks/
│   ├── Stocks_Project.ipynb           # Batch bronze → silver (early Parquet path)
│   ├── Silver_Layer_Delta_Lake.ipynb  # Batch silver as Delta + SQL table
│   ├── pyspark_transformations.ipynb  # Silver → gold star schema + features
│   ├── realtime_stock_pipeline.ipynb  # Unified realtime Auto Loader pipeline
│   ├── realtime-silver.ipynb          # Exploratory realtime silver / gold
│   └── realtime_gold.ipynb            # Realtime gold experiments
├── src/
│   ├── inspect_data.py          # Local CSV profiling with pandas
│   ├── upload_s3.py             # Upload CSV to bronze S3
│   ├── finnhub_test.py          # Finnhub quote smoke test
│   └── kinesis_producer.py      # Finnhub → Kinesis (scaffolded)
├── .gitignore
└── README.md
```

---

## Batch pipeline

### 1. Ingest (local → Bronze)

```bash
python src/inspect_data.py   # profile data/raw/SP500_Historical_Data.csv
python src/upload_s3.py      # → s3://stocks-bronze-layer/raw/batch/
```

### 2. Clean (Bronze → Silver Delta)

Run `notebooks/Silver_Layer_Delta_Lake.ipynb` on Databricks:

- Read bronze CSV
- Data quality: nulls, duplicate ticker/date, invalid OHLC
- Preprocess: typed dates, snake_case columns, dedupe, `year` / `month` partitions, `processed_at`
- Write **Delta** to `s3://stocks-silver-layer/processed/batch/`
- Register SQL table: `silver.sp500_historical`

### 3. Model (Silver → Gold)

Run `notebooks/pyspark_transformations.ipynb`:

| Gold table | Description |
|------------|-------------|
| `dim_stock` | Stock dimension |
| `dim_date` | Date dimension |
| `fact_stock_prices` | Prices + `daily_return`, MA 7/30, `daily_range`, `volatility_30d` |

Paths under `s3://stocks-gold-layer/`.

---

## Realtime pipeline

```text
Finnhub → NiFi → s3://stocks-bronze-layer/raw/realtime_finnhub/
       → Databricks Auto Loader (AvailableNow)
       → Silver:  s3://stocks-silver-layer/processed/realtime/
       → Gold:    fact_stock_prices_realtime / dim_date_realtime
```

Primary notebook: `notebooks/realtime_stock_pipeline.ipynb`  
Checkpoints: `s3://stocks-bronze-layer/checkpoints/realtime_stock_pipeline/`

---

## Key resources

| Resource | Name |
|----------|------|
| Bronze bucket | `stocks-bronze-layer` |
| Silver bucket | `stocks-silver-layer` |
| Gold bucket | `stocks-gold-layer` |
| Batch silver table | `silver.sp500_historical` |
| Kinesis stream (WIP) | `stock-market-realtime` (`us-east-1`) |

---

## Features & transformations (Gold)

- Previous close & **daily return (%)**
- **Moving averages** (7-day, 30-day)
- **Daily range** (high − low)
- **30-day volatility**
- Surrogate keys for star-schema joins (`stock_key`, `date_key`)

---

## Getting started

### Prerequisites

- AWS account with the three S3 buckets above
- Databricks workspace with access to those buckets
- Python 3 + `pandas`, `boto3`, `requests` (for local scripts)
- Finnhub API key (store in `.env`; do not commit secrets)
- Optional: Apache NiFi for realtime landing

### Local setup

```bash
git clone <your-repo-url>
cd stock-market-data
# Place SP500_Historical_Data.csv under data/raw/
# Configure AWS credentials for boto3
python src/upload_s3.py
```

Then open the Databricks notebooks in order: **Silver Delta** → **Gold transformations** (batch), and **realtime_stock_pipeline** for streaming.

---

## Project highlights

- Medallion lakehouse design on S3 with clear Bronze / Silver / Gold separation
- Batch silver upgraded to **Delta Lake** (`_delta_log`, time travel, SQL table)
- Realtime path with **Auto Loader** and S3 checkpoints
- Analytics-ready gold layer with returns, MAs, and volatility
- Local + cloud workflow: inspect/upload locally, process at scale in Databricks

---

<!-- ## License

Private project — update this section if you publish under an open-source license. -->
