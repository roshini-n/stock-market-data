# import json
# import time
# import requests
# import boto3
# from datetime import datetime, timezone

# # FINNHUB_API_KEY = "Kinesis"

# STREAM_NAME = "stock-market-realtime"
# REGION = "us-east-1"

# TICKERS = ["AAPL"]

# kinesis = boto3.client(
#     "kinesis",
#     region_name=REGION
# )


# def get_stock(ticker):
#     url = (
#         "https://finnhub.io/api/v1/quote"
#         f"?symbol={ticker}"
#         f"&token={FINNHUB_API_KEY}"
#     )

#     response = requests.get(url, timeout=30)
#     response.raise_for_status()

#     data = response.json()

#     if not data or data.get("c") is None:
#         print(f"No quote returned for {ticker}")
#         return None

#     return {
#         "ticker": ticker,
#         "timestamp": datetime.now(timezone.utc).isoformat(),
#         "open": data["o"],
#         "high": data["h"],
#         "low": data["l"],
#         "close": data["c"],
#         "previous_close": data["pc"],
#         "change": data["d"],
#         "change_percent": data["dp"],
#         "volume": None,
#         "source": "Finnhub"
#     }


# for ticker in TICKERS:

#     stock = get_stock(ticker)

#     if stock:
#         response = kinesis.put_record(
#             StreamName=STREAM_NAME,
#             Data=json.dumps(stock).encode("utf-8"),
#             PartitionKey=ticker
#         )

#         print(
#             f"Sent {ticker} to Kinesis | "
#             f"SequenceNumber: {response['SequenceNumber']}"
#         )

#     time.sleep(1)