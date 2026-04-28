from dotenv import load_dotenv
import os
import requests
import feedparser
from groq import Groq

# Load environment variables
load_dotenv()

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
groq_key = os.getenv("GROQ_API_KEY")

# Groq client
client = Groq(api_key=groq_key)

# ===============================
# NEWS SOURCE (Tailored for OMCs)
# ===============================
url = "https://news.google.com/rss/search?q=Brent+crude+OR+oil+prices+OR+Strait+of+Hormuz+OR+Hormuz+OR+Iran+OR+Trump+OR+sanctions+OR+OPEC+OR+IOC+OR+HPCL+OR+BPCL+OR+fuel+prices+India&hl=en-IN&gl=IN&ceid=IN:en"

feed = feedparser.parse(url)

# Get top 15 headlines
headlines = []

for entry in feed.entries[:15]:
    headlines.append(entry.title)

headline_text = "\n".join(headlines)

# ===============================
# AI PROMPT
# ===============================
prompt = f"""
You are an equity analyst tracking Indian Oil Marketing Companies:
IOC, HPCL, BPCL.

Analyze these headlines and create a short investor report.

Format EXACTLY:

🛢️ OMC Intelligence Report

• Summarize key developments in crude oil / Hormuz / Iran / Trump / OPEC / India fuel policy
• Mention likely impact on IOC / HPCL / BPCL as Positive / Negative / Neutral
• Mention Brent crude risk direction: Up / Down / Stable
• Mention urgency level: Low / Medium / High
• Max 5 bullet points
• Be concise and factual
• Ignore irrelevant headlines

Headlines:
{headline_text}
"""

# ===============================
# AI GENERATION
# ===============================
chat = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=0.2
)

report = chat.choices[0].message.content

# ===============================
# SEND TO TELEGRAM
# ===============================
telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

payload = {
    "chat_id": chat_id,
    "text": report
}

requests.post(telegram_url, data=payload)

print("OMC report sent.")