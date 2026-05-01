from dotenv import load_dotenv
import os
import sys
import requests
import feedparser
import yfinance as yf
from groq import Groq

load_dotenv()

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
groq_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_key)

mode = "normal"
if len(sys.argv) > 1:
    mode = sys.argv[1].lower()

STATE_FILE = "state/last_headlines.txt"

# ----------------------
# Brent Price
# ----------------------
try:
    brent = yf.Ticker("BZ=F")
    hist = brent.history(period="2d")

    latest = round(hist["Close"].iloc[-1], 2)
    prev = round(hist["Close"].iloc[-2], 2)

    diff = round(latest - prev, 2)

    if diff > 0:
        trend = "Up"
    elif diff < 0:
        trend = "Down"
    else:
        trend = "Stable"

    brent_text = f"${latest} ({trend} {diff})"

except:
    brent_text = "Unavailable"

# ----------------------
# Fetch News
# ----------------------
query = "Brent crude OR oil prices OR Strait of Hormuz OR Hormuz OR Iran OR Trump OR sanctions OR OPEC OR IOC OR HPCL OR BPCL OR fuel prices India"

url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"

feed = feedparser.parse(url)

headlines = []
for entry in feed.entries[:15]:
    item = entry.title

    if hasattr(entry, "summary"):
        item += " | " + entry.summary

    headlines.append(item)

headline_text = "\n".join(headlines)

# ----------------------
# Memory Compare
# ----------------------
if mode == "normal":
    previous = []

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            previous = [line.strip() for line in f.readlines()]

    same_count = len(set(headlines) & set(previous))

    if same_count >= 10:
        telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": "🟢 No major new OMC-relevant developments since last update.\nBrent stable / no fresh catalyst."
        }

        requests.post(telegram_url, data=payload)

        print("No new news message sent.")
        sys.exit()   

# ----------------------
# Prompt
# ----------------------
if mode == "morning":
    prompt = f"""
You are an equity analyst tracking IOC, HPCL, BPCL.

Current Brent Price: {brent_text}

Create a premium MORNING BRIEF covering overnight developments.

Focus on:
- US / Iran / Hormuz / sanctions
- Oil price moves
- OPEC developments
- Global cues for Indian market open
- Impact on IOC / HPCL / BPCL

Format:

🌅 Morning OMC Brief

• Brent: ...
• Overnight key event ...
• OMC Impact: Positive/Negative/Neutral
• Market Open Setup: Bullish/Bearish/Neutral
• Urgency: Low/Medium/High
"""

else:
    prompt = f"""
You are an equity analyst tracking IOC, HPCL, BPCL.

Current Brent Price: {brent_text}

Create a concise investor alert.

Format:

🛢️ OMC Intelligence Report

• Brent: ...
• Key development ...
• OMC Impact: Positive/Negative/Neutral
• Urgency: Low/Medium/High
• One action note
"""

prompt += f"\n\nHeadlines:\n{headline_text}"

# ----------------------
# AI Generate
# ----------------------
chat = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2
)

report = chat.choices[0].message.content.strip()

# ----------------------
# Send Telegram
# ----------------------
telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

payload = {
    "chat_id": chat_id,
    "text": report
}

requests.post(telegram_url, data=payload)

# ----------------------
# Save Memory
# ----------------------
with open(STATE_FILE, "w", encoding="utf-8") as f:
    for h in headlines:
        f.write(h + "\n")

print("Done.")