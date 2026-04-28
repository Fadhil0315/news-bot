import schedule
import time
import os

def run_bot():
    os.system("python aireport.py")

schedule.every(30).minutes.do(run_bot)

print("Bot running every 30 mins...")

run_bot()  # run once now

while True:
    schedule.run_pending()
    time.sleep(10)