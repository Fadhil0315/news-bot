from dotenv import load_dotenv
import os
import requests
import feedparser
from groq import Groq

# Load env
load_dotenv()

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
groq_key = os.getenv("GROQ_API_KEY")

# Groq client
client = Groq(api_key=groq_key)

# Fetch headlines
url = "https://news.google.com/rss/search?q=geopolitics+OR+war+OR+conflict&hl=en-IN&gl=IN&ceid=IN:en"
feed = feedparser.parse(url)

headlines = []
for entry in feed.entries[:10]:
    headlines.append(entry.title)

headline_text = "\n".join(headlines)

prompt = f"""
You are a geopolitical analyst.

Turn these headlines into a concise report.

Format exactly:

🌍 Geo Intelligence Report

• Max 4 bullet points
• Mention key tensions/conflicts
• Mention likely market/regional impact
• Be factual
• No fluff

Headlines:
{headline_text}
"""

chat = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=0.3
)

report = chat.choices[0].message.content

# Send Telegram
telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"

payload = {
    "chat_id": chat_id,
    "text": report
}

requests.post(telegram_url, data=payload)

print("Report sent.")