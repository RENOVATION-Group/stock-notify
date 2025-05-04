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

    # データが不十分、または取得失敗時
    if data is None or data.empty or "Close" not in data.columns or len(data["Close"]) < 2:
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

def post_to_slack(text):
    token = os.getenv("SLACK_BOT_TOKEN")
    channel = os.getenv("SLACK_CHANNEL_ID")
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": text,
        "mrkdwn": True
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Slack response:", response.status_code, response.text)

# 各セクション作成
japan_section = format_section("🇯🇵 *日本株*", japan_stocks)
us_section = format_section("🇺🇸 *米国株*", us_stocks)

# 取得失敗銘柄の表示
fail_section = ""
if failed_stocks:
    fail_section = "\n⚠️ *取得失敗銘柄：*\n" + "\n".join(f"- {name}" for name in failed_stocks)

# メッセージ組み立て
message = (
    f"📊 *株式レポート（{today}）*\n\n"
    f"{japan_section}\n"
    f"{us_section}\n"
    f"{fail_section}"
)

# Slackに投稿
post_to_slack(message)
