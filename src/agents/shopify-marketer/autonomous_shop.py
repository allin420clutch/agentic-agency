import os
import requests
import time
import shopify
import gc
from google import genai
from optimum.intel import OVDiffusionPipeline
from dotenv import load_dotenv

# 1. SETUP
env_path = os.path.expanduser("~/Workflows/OpenClaw/.env")
load_dotenv(dotenv_path=env_path)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-3.1-flash-lite-preview"

# 2. CONNECTIONS
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
shop_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
shop_url = os.getenv("SHOP_URL", "sdssupplies.myshopify.com")
shopify.ShopifyResource.activate_session(shopify.Session(shop_url, '2024-01', shop_token))
chat_id = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates").json()["result"][-1]["message"]["chat"]["id"]

def calculate_automated_price(base_cost=0.50, target_margin=0.90):
    return round(base_cost / (1 - target_margin), 2)

# 3. RESEARCH
print(f"🚀 Sniper Active (Model: {MODEL_ID})")
research_prompt = "Identify 3 technical niches (Cybersecurity, Construction, AI). Output ONLY: Trend:Style:CollectionName"

def safe_generate(prompt):
    while True:
        try:
            return client.models.generate_content(model=MODEL_ID, contents=prompt).text
        except:
            time.sleep(60)

raw_response = safe_generate(research_prompt)
lines = [line.strip() for line in raw_response.split('\n') if ':' in line]

# 4. ARTIST
pipeline = OVDiffusionPipeline.from_pretrained("OpenVINO/stable-diffusion-v1-5-fp16-ov", compile=True, safety_checker=None)

# 5. PRODUCTION
for i, line in enumerate(lines[:3]):
    try:
        parts = [p.strip() for p in line.split(':')]
        trend = parts[0]
        style = parts[1] if len(parts) > 1 else "Modern"
        category = parts[2] if len(parts) > 2 else "Technical"
        
        print(f"\n🚀 Creating: {trend}")
        
        # DRAW
        art_desc = safe_generate(f"Sticker: {trend}. Style: {style}. White background. 10 words.")
        image = pipeline(prompt=art_desc, num_inference_steps=20).images[0]
        image_path = f"./sticker_{i+1}.png"
        image.save(image_path)

        # MARKET (Fixed description parsing)
        mkt_prompt = f"Write a professional Shopify HTML description for a '{trend}' sticker for {category} pros. Use <strong> and <ul> tags. Max 40 words. Output ONLY HTML."
        mkt_html = safe_generate(mkt_prompt)

        # UPLOAD
        prod = shopify.Product()
        prod.title = f"{trend} Technical Sticker"
        prod.body_html = mkt_html
        prod.status = "draft"
        prod.vendor = "RB Enterprises"
        
        # VARIANT (Fixed Inventory Management)
        variant = shopify.Variant({
            'price': calculate_automated_price(),
            'inventory_management': None,    # <--- This stops the "0 in stock" error
            'inventory_policy': 'continue',  # <--- Allows sales without tracking
            'requires_shipping': True,
            'taxable': True
        })
        prod.variants = [variant]

        with open(image_path, "rb") as f:
            img = shopify.Image()
            img.attach_image(f.read(), filename=f"stk_{i+1}.png")
            prod.images = [img]
        prod.save()

        # TELEGRAM
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto", 
                      data={'chat_id': chat_id, 'caption': f"✅ {trend} Live!\n💰 Price: $5.00\n📂 {category}\n📦 Stock: Infinite (Un-tracked)"}, 
                      files={'photo': open(image_path, 'rb')})
        gc.collect()

    except Exception as e:
        print(f"⚠️ Error: {e}")

print("\n✨ Clean listings active. Ready for sales.")
