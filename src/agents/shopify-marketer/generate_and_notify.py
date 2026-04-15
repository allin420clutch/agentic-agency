import os
import requests
import datetime
import google.generativeai as genai
from optimum.intel import OVDiffusionPipeline
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

genai.configure(api_key=GEMINI_KEY)
llm = genai.GenerativeModel('gemini-2.5-flash-lite')

# 2. Brainstorm (The Brain)
print("🧠 Gemini is dreaming up a design...")
prompt_request = "You are a POD expert. Generate a short, highly detailed prompt for a high-quality die-cut sticker of a 'Succulent Plant in a Coffee Cup' theme. Minimalist, clean lines, white background. Output ONLY the prompt."
ai_response = llm.generate_content(prompt_request)
art_prompt = ai_response.text.strip()

# 3. Generate (The Artist)
print(f"🎨 Drawing: {art_prompt}")
# Using a fast, CPU-optimized model
model_id = "OpenVINO/stable-diffusion-v1-5-fp16-ov"
pipeline = OVDiffusionPipeline.from_pretrained(model_id, compile=True, safety_checker=None)
image = pipeline(prompt=art_prompt, num_inference_steps=20).images[0]

# 4. Save
image_path = "./daily_trend.png"
image.save(image_path)

# 5. Notify (The Messenger)
# Grab Chat ID
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
chat_id = requests.get(url).json()["result"][-1]["message"]["chat"]["id"]

# Send Image to Telegram
msg_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
with open(image_path, 'rb') as photo:
    requests.post(msg_url, data={'chat_id': chat_id, 'caption': f"🚀 LIVE TREND GENERATED\nPrompt: {art_prompt}"}, files={'photo': photo})

print("✅ Success! Check your phone.")
