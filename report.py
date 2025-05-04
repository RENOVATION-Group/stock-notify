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
failed_stocks = []

def fetch_price(ticker):
    data = yf.download(ticker, period="2d", interval="1d", progress=False)

    if data is None or len(data) < 2 or "Close" not in data.columns:
        return None

    try:
        prev_close = float(data["Close"].iloc[-2])
        last_close = float(data["Close"].iloc[-1])
        diff = last_close - prev_close
        percent = (diff / prev_close) * 100
        return last_close, diff, percent
    except Exception:
        return None

def format_section(title, stock_list):
    section = f"{title}\n"
    for stock in stock_list:
        res = fetch_price(stock["ticker"])
        if res:
            price, diff, percent = res
            section += (
                f"- *{stock['name']}*（{stock['ticker']}）\n"
                f"  {price:,.2f}（前日比 {diff:+,.2f}, {percent:+.2f}%）\n\n"
            )
        else:
            failed_stocks.append(stock["name"])
    return section

# 株価セクション（投資信託なし）
japan_section = format_section("🇯🇵 日本株", japan_stocks)
us_section = format_section("🇺🇸 米国株", us_stocks)

# 失敗銘柄セクション
fail_section = ""
if failed_stocks:
    fail_section = "\n⚠️ 取得失敗銘柄：\n" + "\n".join(f"- {name}" for name in failed_stocks)

# Slack送信メッセージ
message = (
    f"📊 株式レポート（{today}）\n\n"
    f"{japan_section}\n"
    f"{us_section}\n"
    f"{fail_section}"
)

# Slack送信（mrkdwn を有効にする）
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
requests.post(SLACK_WEBHOOK_URL, json={
    "text": message,
    "mrkdwn": True
})
