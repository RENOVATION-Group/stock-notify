import os
import datetime
import yfinance as yf
import requests

# 保有銘柄リスト
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
    prev_close = data["Close"].iloc[-2]
    last_close = data["Close"].iloc[-1]
    diff = last_close - prev_close
    percent = (diff / prev_close) * 100
    return last_close, diff, percent

def format_section(title, stock_list):
    section = f"{title}\n"
    for stock in stock_list:
        res = fetch_price(stock["ticker"])
        if res:
            price, diff, percent = res
            section += f"- {stock['name']}（{stock['ticker']}）\n  {price:.2f}（前日比 {diff:+.2f}, {percent:+.2f}%）\n\n"
    return section

# 投資信託（ダミー）
funds = {
    "野村世界半導体株投資": +1.23,
    "eMAXIS Slim 米国株式": -0.45,
    "eMAXIS Neo 宇宙開発": +0.30,
    "SBI・V・S&P500": +0.10,
    "SBI・ゴールド": -0.55,
}

fund_section = "📊 投資信託（前日比 %）\n"
for name, change in funds.items():
    fund_section += f"- {name}：{change:+.2f}%\n"

# Slack送信
message = f"📊 株式レポート（{today}）\n\n🇯🇵 日本株\n{format_section('', japan_stocks)}\n🇺🇸 米国株\n{format_section('', us_stocks)}\n{fund_section}"

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
requests.post(SLACK_WEBHOOK_URL, json={"text": message})
