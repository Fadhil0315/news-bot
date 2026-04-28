from dotenv import load_dotenv
import os
import requests

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

url = f"https://api.telegram.org/bot{token}/sendMessage"

payload = {
    "chat_id": chat_id,
    "text": "🚨 Geo News Bot is now ONLINE."
}

response = requests.post(url, data=payload)

print(response.json())