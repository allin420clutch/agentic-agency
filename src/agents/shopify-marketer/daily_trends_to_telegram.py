import os
import requests
import datetime
from dotenv import load_dotenv

# Load your token
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Check recent messages to grab your Chat ID
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
response = requests.get(url).json()
chat_id = response["result"][-1]["message"]["chat"]["id"]

# Build the message with the Image Prompts
current_month = datetime.datetime.now().strftime("%B")
message = f"🚀 *R&B ENTERPRISES DAILY TRENDS*\n_Target: {current_month} 2026 - Late Spring & Father's Day_\n\n"

message += "1️⃣ *Die-Cut Sticker*\n_Theme:_ Summer Outdoors\n_Prompt:_ A retro 1970s sunset with silhouetted pine trees and a campfire, vintage distressed style, vector illustration, bold flat colors, solid white background --v 6.0\n\n"

message += "2️⃣ *Coffee Mug*\n_Theme:_ Father's Day / Comedy\n_Prompt:_ Minimalist typography design, bold athletic font reading 'Professional Grill Master', distressed texture, small vector spatula graphic beneath the text, black text on clean white background\n\n"

message += "3️⃣ *T-Shirt / Digital Print*\n_Theme:_ Modern Nostalgia\n_Prompt:_ 90s geometric Memphis style pattern, neon summer colors (teal, hot pink, yellow), vaporwave aesthetic, clean lines, high resolution t-shirt graphic design, isolated on white"

# Send the message to your phone
msg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
requests.post(msg_url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})

print("Done! Check your Telegram.")
