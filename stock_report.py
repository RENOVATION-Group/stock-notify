import os
import datetime
import yfinance as yf
import requests

stocks = [
    {"ticker": "3099.T", "name": "ミツコシイセタン"},
    {"ticker": "3086.T", "name": "Jフロント"},
    {"ticker": "4755.T", "name": "楽天グループ"},
    {"ticker": "8233.T", "name": "高島屋"},
    {"ticker": "3778.T", "name": "さくらインターネット"},
    {"ticker": "5803.T", "name": "フジクラ"},
    {"ticker": "6857.T", "name": "アドバンテスト"},
    {"ticker": "9984.T", "name": "ソフトバンクグループ"},
    {"ticker": "AAPL", "name": "Apple"},
    {"ticker": "AMD", "name": "AMD"},
    {"ticker": "ARM", "name": "Arm"},
    {"ticker": "META", "name": "Meta Platforms"},
    {"ticker": "MSFT", "name": "Microsoft"},
    {"ticker": "MSTR", "name": "MicroStrategy"},
    {"ticker": "NFLX", "name": "Netflix"},
    {"ticker": "NVDA", "name": "NVIDIA"},
    {"ticker": "RDDT", "name": "Reddit"},
    {"ticker": "SMCI", "name": "Super Micro Computer"},
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
    if len(data) < 2:
        return None
    prev = data["Close"][-2]
    last = data["Close"][-1]
    return last, last - prev, (last - prev) / prev * 100

def format_section(title, stock_list):
    text = f"{title}\n"
    for stock in stock_list:
        result = fetch_price(stock["ticker"])
        if result:
            last, diff, percent = result
            text += f"- {stock['name']}（{stock['ticker']}）\n  {last:.2f}（前日比 {diff:+.2f}, {percent:+.2f}%）\n\n"
    return text

funds = {
    "野村世界半導体株投資": +1.23,
    "eMAXIS Slim 米国株式": -0.45,
    "eMAXIS Neo 宇宙開発": +0.30,
    "SBI・V・S&P500": +0.10,
    "SBI・ゴールド": -0.55,
    "SBIインド株式": +0.65,
    "SBI日本配当株式": +0.75,
    "eMAXIS Slim 全世界株式": +0.38,
}

fund_section = "📊 投資信託（前日比）\n"
for name, pct in funds.items():
    fund_section += f"- {name}：{pct:+.2f}%\n"

message = f"""📈 株式レポート（{today}）

🇯🇵 日本株
{format_section("", japan_stocks)}

🇺🇸 米国株
{format_section("", us_stocks)}

{fund_section}
"""

url = os.getenv("SLACK_WEBHOOK_URL")
requests.post(url, json={"text": message})
