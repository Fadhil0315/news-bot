from dotenv import load_dotenv
import os
import requests
import feedparser

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

url = "https://news.google.com/rss/search?q=geopolitics+OR+war+OR+conflict&hl=en-IN&gl=IN&ceid=IN:en"

feed = feedparser.parse(url)

message = "🌍 Geopolitical Headlines:\n\n"

for i, entry in enumerate(feed.entries[:10], start=1):
    message += f"{i}. {entry.title}\n\n"

telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"

payload = {
    "chat_id": chat_id,
    "text": message
}

response = requests.post(telegram_url, data=payload)

print(response.json())