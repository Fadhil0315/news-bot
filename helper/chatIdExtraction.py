import requests

# Replace with your bot token from BotFather
BOT_TOKEN = "8842139651:AAG-AgGRLHmgDf27THYMjGxFGtFjXKtcIn8"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

response = requests.get(url)
data = response.json()

print(data)

# Extract chat IDs nicely
if data["ok"]:
    for update in data["result"]:
        chat_id = update["message"]["chat"]["id"]
        username = update["message"]["chat"].get("username", "No username")
        print(f"Chat ID: {chat_id} | Username: {username}")
else:
    print("Error fetching updates")