import requests

API_KEY = "Finnhub_API_KEY"

symbol = "AAPL"

url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"

response = requests.get(url, timeout=30)

print("Status:", response.status_code)
print(response.json())