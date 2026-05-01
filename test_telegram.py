import os
import requests
from dotenv import load_dotenv

load_dotenv()
# Check the most common names for the Telegram key
token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")

if not token:
    print("❌ ERROR: Could not find a Telegram token in your .env file.")
    exit()

print("📡 Pinging Telegram servers...")
url = f"https://api.telegram.org/bot{token}/getMe"
response = requests.get(url).json()

if response.get("ok"):
    print(f"✅ Connection successful! Bot is alive on Telegram as: @{response['result']['username']}")
    print("Checking if it can actually read your messages...")
    
    updates_url = f"https://api.telegram.org/bot{token}/getUpdates?limit=1"
    updates = requests.get(updates_url).json()
    
    if updates.get("ok") and updates.get("result"):
        print("📩 SUCCESS: The bot can see your chat queue!")
    elif updates.get("ok"):
        print("📭 The connection is good, but there are no pending messages in the queue.")
    else:
        print(f"⚠️ Webhook Conflict: {updates.get('description')}")
        print("If it says 'webhook is active', your bot is trying to receive messages the wrong way.")
else:
    print(f"❌ Telegram API Error: {response.get('description')}")
