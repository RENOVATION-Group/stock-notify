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

# 日本株・米国株に分ける
japan_stocks = [s for s in stocks if s["ticker"].endswith(".T")]
us_stocks = [s for s in stocks if not s["ticker"].endswith(".T")]

today = datetime.date.today()
failed_stocks = []

# 株価取得関数（float 変換付き）
def fetch_price(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1d", progress=False, auto_adjust=False)
        if data is None or len(data) < 2 or "Close" not in data.columns:
            return None
        prev_close = float(data["Close"].iloc[-2])
        last_close = float(data["Close"].iloc[-1])
        diff = last_close - prev_close
        percent = (diff / prev_close) * 100
        return last_close, diff, percent
    except Exception:
        return None

# Slack Block Kit形式で出力を構築
def format_section(title, stock_list):
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*{title}*"}}
    ]
    for stock in stock_list:
        res = fetch_price(stock["ticker"])
        if res:
            price, diff, percent = res
            text = f"- *{stock['name']}*（{stock['ticker']}）\n{price:,.2f}（前日比 {diff:+,.2f}, {percent:+.2f}%）"
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
        else:
            failed_stocks.append(stock["name"])
    return blocks

# Slack投稿メッセージの構築
blocks = [
    {"type": "header", "text": {"type": "plain_text", "text": f"📈 株式レポート（{today}）"}}
]
blocks += format_section("🇯🇵 日本株", japan_stocks)
blocks += format_section("🇺🇸 米国株", us_stocks)

# エラーがある場合
if failed_stocks:
    fail_text = "⚠️ 取得失敗銘柄：\n" + "\n".join(f"- {name}" for name in failed_stocks)
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": fail_text}})

# Slack送信
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
requests.post(SLACK_WEBHOOK_URL, json={"blocks": blocks})
