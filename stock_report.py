import os
import datetime
import yfinance as yf
import requests

stocks = [
    {"ticker": "3099.T", "name": "Mitsukoshi Isetan"},
    {"ticker": "3086.T", "name": "J Front"},
    {"ticker": "4755.T", "name": "Rakuten"},
    {"ticker": "8233.T", "name": "Takashimaya"},
    {"ticker": "3778.T", "name": "Sakura Internet"},
    {"ticker": "5803.T", "name": "Fujikura"},
    {"ticker": "6857.T", "name": "Advantest"},
    {"ticker": "9984.T", "name": "SoftBank Group"},
    {"ticker": "AAPL", "name": "Apple"},
    {"ticker": "AMD", "name": "AMD"},
    {"ticker": "ARM", "name": "Arm"},
    {"ticker": "META", "name": "Meta"},
    {"ticker": "MSFT", "name": "Microsoft"},
    {"ticker": "MSTR", "name": "MicroStrategy"},
    {"ticker": "NFLX", "name": "Netflix"},
    {"ticker": "NVDA", "name": "NVIDIA"},
    {"ticker": "RDDT", "name": "Reddit"},
    {"ticker": "SMCI", "name": "Super Micro"},
    {"ticker": "TSM", "name": "TSMC"},
    {"ticker": "ALAB", "name": "Astera Labs"},
    {"ticker": "CRWD", "name": "CrowdStrike"},
    {"ticker": "NOW", "name": "ServiceNow"},
    {"ticker": "PLTR", "name": "Palantir"},
    {"ticker": "RBRK", "name": "Rubrik"},
    {"ticker": "TEM", "name": "TempusAI"},
    {"ticker": "TSLA", "name": "Tesla"},
    {"ticker": "VST", "name": "Vistra"},
    {"ticker": "PG", "name": "Procter & Gamble"},
    {"ticker": "KO", "name": "Coca-Cola"},
]

japan_stocks = [s for s in stocks if s["ticker"].endswith(".T")]
us_stocks = [s for s in stocks if not s["ticker"].endswith(".T")]
today = datetime.date.today()

def fetch_price(ticker):
    data = yf.download(ticker, period="2d", interval="1d", progress=False)
    if len(data) < 2 or "Close" not in data:
        return None
    prev_close = data["Close"][-2]
    last_close = data["Close"][-1]
    diff = last_close - prev_close
    percent = (diff / prev_close) * 100
    return last_close, diff, percent

def format_section(title, stock_list):
    section = f"{title}\n" if title else ""
    for stock in stock_list:
        res = fetch_price(stock["ticker"])
        if res:
            price, diff, percent = res
            section += f"- {stock['name']} ({stock['ticker']}): {price:.2f} (change {diff:+.2f}, {percent:+.2f}%)\n\n"
    return section

funds = {
    "Nomura Semiconductor": +1.23,
    "eMAXIS US": -0.45,
    "eMAXIS Space": +0.30,
    "SBI S&P500": +0.10,
    "SBI Gold": -0.55,
}
fund_section = "Funds (daily % change)\n"
for name, change in funds.items():
    fund_section += f"- {name}: {change:+.2f}%\n"

message = f"""Stock Report ({today})\n
Japan Stocks
{format_section("", japan_stocks)}
US Stocks
{format_section("", us_stocks)}
{fund_section}
"""

url = os.getenv("SLACK_WEBHOOK_URL")
requests.post(url, json={"text": message})
