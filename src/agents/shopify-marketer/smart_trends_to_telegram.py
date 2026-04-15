import os
import requests
import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load your tokens
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_KEY:
    print("ERROR: Gemini API Key not found in .env file.")
    exit()

# Connect to the AI Brain
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

current_month = datetime.datetime.now().strftime("%B %Y")
print("Thinking... The AI is generating today's designs...")

# Instructions for the AI
prompt_instructions = f"""
You are a Print on Demand marketing expert for R&B Enterprises. The current date is {current_month}.
Generate 3 highly profitable, unique graphic design concepts tailored for this specific time of year.
Include one Die-Cut Sticker, one Coffee Mug, and one T-Shirt.

Format your response EXACTLY like this (use these exact emojis and Markdown):
1️⃣ *Die-Cut Sticker*
_Theme:_ [Insert Theme]
_Prompt:_ [Insert a highly detailed Midjourney/image generator prompt to create this graphic on a white background]

2️⃣ *Coffee Mug*
_Theme:_ [Insert Theme]
_Prompt:_ [Insert detailed prompt]

3️⃣ *T-Shirt*
_Theme:_ [Insert Theme]
_Prompt:_ [Insert detailed prompt]
"""

# Get the response from the LLM
ai_response = model.generate_content(prompt_instructions)
generated_text = ai_response.text

# Grab your Telegram Chat ID
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
telegram_data = requests.get(url).json()

if telegram_data.get("ok") and len(telegram_data["result"]) > 0:
    chat_id = telegram_data["result"][-1]["message"]["chat"]["id"]
    
    # Build and send the final message
    message_header = f"🚀 *R&B ENTERPRISES LIVE AI TRENDS*\n_Generated for: {current_month}_\n\n"
    final_message = message_header + generated_text

    msg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(msg_url, json={"chat_id": chat_id, "text": final_message, "parse_mode": "Markdown"})

    print("Done! The AI has sent the fresh concepts to your Telegram.")
else:
    print("ERROR: Could not find your chat ID. Send 'Wake up' to the bot on Telegram again and retry.")
