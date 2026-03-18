import os
import requests

API_KEY = os.environ["ALPHAVANTAGE_API_KEY"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

WATCHLIST = ["AAPL", "NVDA", "TSLA"]

GOOD_KEYWORDS = [
    "earnings", "guidance", "revenue", "profit", "forecast",
    "upgrade", "downgrade", "price target", "sec", "lawsuit",
    "acquisition", "merger", "fed", "cpi", "partnership"
]

BAD_SOURCES = {"Polymarket"}
BAD_TITLE_KEYWORDS = ["trading odds", "prediction"]

def fetch_news():
    tickers = ",".join(WATCHLIST)
    url = (
        "https://www.alphavantage.co/query"
        f"?function=NEWS_SENTIMENT&tickers={tickers}&limit=20&apikey={API_KEY}"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def related_watchlist_tickers(item):
    related = []
    for t in item.get("ticker_sentiment", []):
        ticker = t.get("ticker", "")
        if ticker in WATCHLIST and ticker not in related:
            related.append(ticker)
    return related

def is_good_item(item):
    title = item.get("title", "").lower()
    summary = item.get("summary", "").lower()
    source = item.get("source", "")

    if source in BAD_SOURCES:
        return False

    if any(bad in title for bad in BAD_TITLE_KEYWORDS):
        return False

    text = f"{title} {summary}"
    if any(word in text for word in GOOD_KEYWORDS):
        return True

    tickers = related_watchlist_tickers(item)
    return len(tickers) > 0 and source in {"Reuters", "Yahoo Finance", "MarketWatch", "CNBC"}

def format_message(data):
    feed = data.get("feed", [])
    selected = []

    for item in feed:
        tickers = related_watchlist_tickers(item)
        if not tickers:
            continue
        if not is_good_item(item):
            continue

        selected.append({
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "tickers": tickers,
            "url": item.get("url", "")
        })

    if not selected:
        return "No high-value watchlist news right now."

    msg = "📈 High-Value Stock News\n"
    for item in selected[:5]:
        ticker_text = ", ".join(item["tickers"])
        msg += f"\n- [{ticker_text}] {item['title']} ({item['source']})"
    return msg

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text
    }, timeout=30)
    r.raise_for_status()

def main():
    data = fetch_news()
    msg = format_message(data)
    send_telegram(msg)

if __name__ == "__main__":
    main()
