from dotenv import load_dotenv
import os
import sys
import requests
import feedparser
import yfinance as yf
from groq import Groq
from bs4 import BeautifulSoup
import trafilatura

load_dotenv()

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
groq_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_key)

mode = "normal"
if len(sys.argv) > 1:
    mode = sys.argv[1].lower()

STATE_FILE = "state/last_headlines.txt"

# -------------------------
# Brent Price
# -------------------------
try:
    brent = yf.Ticker("BZ=F")
    hist = brent.history(period="2d")

    latest = round(hist["Close"].iloc[-1], 2)
    prev = round(hist["Close"].iloc[-2], 2)
    diff = round(latest - prev, 2)

    trend = "Stable"
    if diff > 0:
        trend = "Up"
    elif diff < 0:
        trend = "Down"

    brent_text = f"${latest} ({trend} {diff})"

except:
    brent_text = "Unavailable"

# -------------------------
# Better RSS Feeds
# -------------------------
feeds = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://www.oilprice.com/rss/main",
]

entries = []

for url in feeds:
    try:
        parsed = feedparser.parse(url)
        entries.extend(parsed.entries[:5])
    except:
        pass

# -------------------------
# Extract Content
# -------------------------
news_items = []

for entry in entries[:12]:
    title = entry.get("title", "").strip()
    link = entry.get("link", "").strip()

    if not title or not link:
        continue

    # Clean summary if exists
    summary = entry.get("summary", "")
    summary = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)

    # Get real article text
    article_text = ""

    try:
        downloaded = trafilatura.fetch_url(link)
        extracted = trafilatura.extract(downloaded)

        if extracted:
            article_text = extracted[:600]

    except:
        pass

    combined = f"""
TITLE: {title}
SUMMARY: {summary}
CONTENT: {article_text}
"""

    news_items.append(combined.strip())

# -------------------------
# Memory Compare
# -------------------------
headline_keys = [item.split("\n")[0] for item in news_items]

if mode == "normal":
    previous = []

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            previous = [line.strip() for line in f.readlines()]

    same_count = len(set(headline_keys) & set(previous))

    if same_count >= 8:
        telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": "🟢 No major new OMC-relevant developments.\nMonitoring continues."
        }

        requests.post(telegram_url, data=payload)
        sys.exit()

# -------------------------
# Prompt
# -------------------------
news_blob = "\n\n".join(news_items)

if mode == "morning":
    prompt = f"""
You are an elite equity analyst tracking IOC, HPCL, BPCL.

Current Brent Price: {brent_text}

Use the news below to create a sharp MORNING BRIEF.

Focus on:
- Hormuz / Iran / US
- Crude oil moves
- Supply disruptions
- India macro impact
- IOC HPCL BPCL impact

Format:

🌅 Morning OMC Brief

• Brent: ...
• Biggest overnight development ...
• OMC Impact: Positive/Negative/Neutral
• Market Open Setup: Bullish/Bearish/Neutral
• Urgency: Low/Medium/High

NEWS:
{news_blob}
"""
else:
    prompt = f"""
You are an elite equity analyst tracking IOC, HPCL, BPCL.

Current Brent Price: {brent_text}

If no meaningful oil/geopolitical/India catalyst exists, say only:

NO_SIGNAL

Else format:

🛢️ OMC Intelligence Report

• Brent: ...
• Key development ...
• OMC Impact: Positive/Negative/Neutral
• Urgency: Low/Medium/High
• One investor action note

NEWS:
{news_blob}
"""

# -------------------------
# AI Call
# -------------------------
chat = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2
)

report = chat.choices[0].message.content.strip()

# -------------------------
# Send Telegram
# -------------------------
if report != "NO_SIGNAL":
    telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": report
    }

    requests.post(telegram_url, data=payload)

# -------------------------
# Save Memory
# -------------------------
with open(STATE_FILE, "w", encoding="utf-8") as f:
    for h in headline_keys:
        f.write(h + "\n")

print("Done.")