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
    try:
        data = yf.download(ticker, period="2d", interval="1d", progress=False)
        if data is None or len(data) < 2 or "Close" not in data.columns:
            return None
        prev_close = data["Close"].iloc[-2]
        last_close = data["Close"].iloc[-1]
        diff = last_close - prev_close
        percent = (diff / prev_close) * 100
        return last_close, diff, percent
    except Exception:
        return None

def format_section(title, stock_list):
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*"}}]
    for stock in stock_list:
        result = fetch_price(stock["ticker"])
        if result:
            price, diff, percent = result
            text = f"*{stock['name']}*（{stock['ticker']}）\n{price:,.2f}（前日比 {diff:+,.2f}, {percent:+.2f}%）"
        else:
            text = f"*{stock['name']}*（{stock['ticker']}）\n取得失敗"
            failed_stocks.append(stock["name"])
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
    return blocks

# セクション生成
blocks = []
blocks.append({"type": "header", "text": {"type": "plain_text", "text": f"📊 株式レポート（{today}）"}})
blocks += format_section("🇯🇵 日本株", japan_stocks)
blocks += [{"type": "divider"}]
blocks += format_section("🇺🇸 米国株", us_stocks)

# エラーセクション
if failed_stocks:
    fail_text = "*⚠️ 取得失敗銘柄：*\n" + "\n".join(f"- {name}" for name in failed_stocks)
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": fail_text}})

# Slack投稿
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
url = "https://slack.com/api/chat.postMessage"

headers = {
    "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "channel": SLACK_CHANNEL_ID,
    "blocks": blocks,
    "text": f"📊 株式レポート（{today}）"
}

res = requests.post(url, headers=headers, json=payload)
print(res.status_code, res.text)
