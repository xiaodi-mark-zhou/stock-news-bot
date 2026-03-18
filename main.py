import os
import requests

API_KEY = os.environ["ALPHAVANTAGE_API_KEY"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

WATCHLIST = ["AAPL", "NVDA", "TSLA"]

def fetch_news():
    tickers = ",".join(WATCHLIST)
    url = (
        "https://www.alphavantage.co/query"
        f"?function=NEWS_SENTIMENT&tickers={tickers}&limit=10&apikey={API_KEY}"
    )
    r = requests.get(url)
    return r.json()

def format_message(data):
    feed = data.get("feed", [])
    if not feed:
        return "No important news today."

    msg = "📈 Stock News Update\n"
    for item in feed[:3]:
        title = item.get("title", "")
        source = item.get("source", "")
        msg += f"\n- {title} ({source})"
    return msg

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    })

def main():
    data = fetch_news()
    msg = format_message(data)
    send_telegram(msg)

if __name__ == "__main__":
    main()
