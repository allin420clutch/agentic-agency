import os
import requests
import time
import shopify
import gc
import base64
from google import genai
from dotenv import load_dotenv

# 1. SETUP
env_path = os.path.expanduser("~/Workflows/OpenClaw/.env")
load_dotenv(dotenv_path=env_path)

# NEW 3.1 SDK Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
TEXT_MODEL = "gemini-3.1-flash-lite-preview"
IMAGE_MODEL = "gemini-3.1-flash-image-preview"

# 2. CONNECTIONS
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
shop_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
shop_url = os.getenv("SHOP_URL", "sdssupplies.myshopify.com")
shopify.ShopifyResource.activate_session(shopify.Session(shop_url, '2024-01', shop_token))
chat_id = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates").json()["result"][-1]["message"]["chat"]["id"]

def calculate_automated_price(base_cost=0.50, target_margin=0.90):
    return round(base_cost / (1 - target_margin), 2)

# 3. RESEARCH
print(f"🚀 SDS Agency: Cloud Mode (Models: 3.1 Flash Text & Image)")
research_prompt = "Identify 3 technical niches (Cybersecurity, Construction, AI). Output: Trend:Style:CollectionName"

def safe_generate_text(prompt):
    while True:
        try:
            return client.models.generate_content(model=TEXT_MODEL, contents=prompt).text
        except:
            time.sleep(60)

raw_response = safe_generate_text(research_prompt)
lines = [line.strip() for line in raw_response.split('\n') if ':' in line]

# 4. PRODUCTION LOOP (Zero Local CPU Usage)
for i, line in enumerate(lines[:3]):
    try:
        parts = [p.strip() for p in line.split(':')]
        trend = parts[0]
        style = parts[1] if len(parts) > 1 else "Modern"
        
        print(f"\n✨ Generating Cloud-Art: {trend}...")
        
        # CLOUD IMAGE GENERATION (Nano Banana 2)
        art_prompt = f"Professional die-cut sticker: {trend}. Style: {style}. White background. Vector art. High detail."
        
        # Use generate_content with the image model
        img_response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[art_prompt]
        )
        
        # Extract image data from response
        image_data = None
        for part in img_response.candidates[0].content.parts:
            if part.inline_data:
                image_data = part.inline_data.data
                break
        
        if not image_data:
            print("⚠️ No image data returned from API.")
            continue

        image_path = f"./sticker_{i+1}.png"
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_data))

        # MARKET & UPLOAD
        mkt_html = safe_generate_text(f"Shopify HTML description for {trend}. 40 words. ONLY HTML.")
        
        prod = shopify.Product()
        prod.title, prod.body_html, prod.status = f"{trend} Sticker", mkt_html, "active"
        prod.vendor = "RB Enterprises"
        
        variant = shopify.Variant({'price': calculate_automated_price(), 'inventory_management': None})
        prod.variants = [variant]

        with open(image_path, "rb") as f_img:
            img = shopify.Image()
            img.attach_image(f_img.read(), filename=f"stk_{i+1}.png")
            prod.images = [img]
        prod.save()

        # TELEGRAM
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                      data={'chat_id': chat_id, 'caption': f"✅ {trend} (Cloud Rendered)"}, 
                      files={'photo': open(image_path, 'rb')})

    except Exception as e:
        print(f"⚠️ Error: {e}")

print("\n✨ SDS Supplies is now 100% Cloud-Powered. CPU is cool.")
