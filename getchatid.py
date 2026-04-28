from dotenv import load_dotenv
import os
import requests

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")

url = f"https://api.telegram.org/bot{token}/getUpdates"

response = requests.get(url)
data = response.json()

print(data)