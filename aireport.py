from dotenv import load_dotenv
import os
import sys
import requests
import feedparser
import yfinance as yf
from groq import Groq
import trafilatura

load_dotenv()

# -------------------------
# ENV
# -------------------------
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
groq_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_key)

# -------------------------
# MODE
# -------------------------
mode = "normal"
if len(sys.argv) > 1:
    mode = sys.argv[1].lower()

STATE_FILE = "state/last_headlines.txt"

# -------------------------
# ARTICLE COUNTS
# -------------------------
if mode == "morning":
    TARGET_ARTICLES = 18
else:
    TARGET_ARTICLES = 12

# -------------------------
# BRENT PRICE
# -------------------------
try:
    brent = yf.Ticker("BZ=F")
    hist = brent.history(period="2d")

    latest = round(hist["Close"].iloc[-1], 2)
    prev = round(hist["Close"].iloc[-2], 2)
    diff = round(latest - prev, 2)

    if diff > 0:
        trend = f"Up {diff}"
    elif diff < 0:
        trend = f"Down {abs(diff)}"
    else:
        trend = "Flat"

    brent_text = f"${latest} ({trend})"

except:
    brent_text = "Unavailable"

# -------------------------
# HIGH QUALITY FEEDS
# -------------------------
feeds = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://www.oilprice.com/rss/main",
    "https://feeds.reuters.com/reuters/topNews",
]

entries = []

for url in feeds:
    try:
        parsed = feedparser.parse(url)
        entries.extend(parsed.entries[:12])
    except:
        pass

# -------------------------
# KEYWORDS (RELEVANCE FILTER)
# -------------------------
keywords = [
    "oil", "crude", "brent", "wti", "energy",
    "hormuz", "iran", "tehran", "middle east",
    "trump", "sanction", "shipping", "tankers",
    "opec", "gasoline", "diesel", "petrol", "lpg",
    "jet fuel", "refinery",
    "india", "indian oil", "ioc", "bpcl", "hpcl"
]

# -------------------------
# BUILD CLEAN NEWS ITEMS
# TITLE + REAL ARTICLE TEXT ONLY
# -------------------------
news_items = []
headline_keys = []
seen_titles = set()

for entry in entries:
    if len(news_items) >= TARGET_ARTICLES:
        break

    title = entry.get("title", "").strip()
    link = entry.get("link", "").strip()

    if not title or not link:
        continue

    clean_title = " ".join(title.split())

    if clean_title.lower() in seen_titles:
        continue

    text_check = clean_title.lower()

    # relevance check from title
    if not any(word in text_check for word in keywords):
        continue

    article_text = ""

    try:
        downloaded = trafilatura.fetch_url(link)
        extracted = trafilatura.extract(downloaded)

        if extracted:
            extracted = " ".join(extracted.split())

            # Remove title if repeated at start
            if extracted.lower().startswith(clean_title.lower()):
                extracted = extracted[len(clean_title):].strip()

            # Use first 220 words (efficient + strong context)
            words = extracted.split()[:500]
            article_text = " ".join(words)

    except:
        pass

    # If extraction failed, skip low-quality item
    if len(article_text) < 80:
        continue

    blob = f"""TITLE: {clean_title}
TEXT: {article_text}"""

    news_items.append(blob)
    headline_keys.append(clean_title)
    seen_titles.add(clean_title.lower())

# -------------------------
# FALLBACK IF TOO FEW ARTICLES
# -------------------------
if len(news_items) == 0:
    news_items.append("TITLE: No major feed items found\nTEXT: Markets quiet. No strong oil catalyst detected.")

# -------------------------
# MEMORY CHECK (NORMAL MODE ONLY)
# -------------------------
if mode == "normal":
    previous = []

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            previous = [line.strip() for line in f.readlines()]

    same_count = len(set(headline_keys) & set(previous))

    # If almost same set, send no-news ping
    overlap_ratio = same_count / max(len(headline_keys), 1)

    if overlap_ratio >= 0.70:
        telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": "🟢 No major new OMC-relevant developments.\nMonitoring continues."
        }

        requests.post(telegram_url, data=payload)
        sys.exit()

# -------------------------
# BUILD NEWS BLOB
# -------------------------
news_blob = "\n\n".join(news_items)

# -------------------------
# PROMPTS
# -------------------------
if mode == "morning":
    prompt = f"""
You are an elite macro + equity analyst focused on Indian OMC stocks:
IOC, HPCL, BPCL.

Current Brent Price: {brent_text}

Use all news provided below and generate a sharp, natural morning intelligence brief.

Your response must cover:

1. Expected direction for IOC / HPCL / BPCL today (bullish / bearish / mixed) and why
2. Exact Strait of Hormuz / Iran / US developments
3. Brent crude likely near-term direction and reasons
4. Concise summary of all developments
5. Any key risk or opportunity for Indian OMC investors today

Be direct, intelligent, concise, and practical.
Do NOT use filler language.
Use readable paragraphs or bullets naturally.

NEWS:
{news_blob}
"""
else:
    prompt = f"""
You are an elite macro + equity analyst focused on Indian OMC stocks:
IOC, HPCL, BPCL.

Current Brent Price: {brent_text}



 generate a sharp investor update covering:

1. OMC stock direction from this development
2. Exact Hormuz / Iran / US update if relevant
3. Brent crude likely direction and why
4. Summary of what changed and why it matters
5. Immediate takeaway for an Indian OMC investor

Be concise, high-signal, and practical.
Avoid robotic templates.

NEWS:
{news_blob}
"""

# -------------------------
# OPTIONAL DEBUG
# -------------------------
# with open("debug_prompt.txt", "w", encoding="utf-8") as f:
#     f.write(prompt)

# -------------------------
# GROQ CALL
# -------------------------
chat = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2
)

report = chat.choices[0].message.content.strip()

# -------------------------
# TELEGRAM SEND
# -------------------------
if report != "NO_SIGNAL":
    telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": report
    }

    requests.post(telegram_url, data=payload)

# -------------------------
# SAVE STATE
# -------------------------
with open(STATE_FILE, "w", encoding="utf-8") as f:
    for h in headline_keys:
        f.write(h + "\n")

print("Done.")
