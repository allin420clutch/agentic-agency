import os

import requests
from dotenv import load_dotenv

# Load the keys from your .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN or TOKEN == "PASTE_YOUR_REAL_TOKEN_HERE" or TOKEN == "your_bot_father_token":
    print("ERROR: It looks like the real token isn't in the .env file yet.")
    exit()

print("Looking for your 'Wake up' message on Telegram...")
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
response = requests.get(url).json()

if response.get("ok") and len(response["result"]) > 0:
    # Grab your hidden Chat ID from the message you just sent
    chat_id = response["result"][-1]["message"]["chat"]["id"]
    print(f"Connection made! Saving your Chat ID: {chat_id}")

    # Send a message back to your phone
    msg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    message_text = "✅ Boss, the OpenClaw agent is online and ready to hunt trends!"
    requests.post(msg_url, json={"chat_id": chat_id, "text": message_text})

    print("Success! Check your phone.")
else:
    print("I didn't see any messages. Make sure you sent 'Wake up' to the bot on your phone first!")
