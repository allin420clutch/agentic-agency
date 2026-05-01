import os
import requests
import time
import shopify
import gc
import base64
import json
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv

# 1. SETUP
env_path = "/home/menackie/Workflows/OpenClaw/.env"
load_dotenv(dotenv_path=env_path)

# Configure the Client with Automatic Retries for 503/429 errors
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            attempts=5, initial_delay=2.0, http_status_codes=[408, 429, 500, 502, 503, 504]
        ),
        timeout=60000,  # 60 Seconds
    ),
)

TEXT_MODEL = "gemini-1.5-flash"
IMAGE_MODEL = "gemini-3.1-flash-image-preview"

# 2. CONNECTIONS
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
shop_url = os.getenv("SHOP_URL", "sdssupplies.myshopify.com")
client_id = os.getenv("SHOPIFY_CLIENT_ID")
client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")

# OAuth client_credentials flow
auth_resp = requests.post(
    f"https://{shop_url}/admin/oauth/access_token",
    json={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    },
    timeout=15,
)
if auth_resp.status_code != 200:
    raise Exception(f"Shopify auth failed: {auth_resp.text}")
shop_token = auth_resp.json()["access_token"]
shopify.ShopifyResource.activate_session(shopify.Session(shop_url, "2024-01", shop_token))

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
try:
    updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=10).json()
    if updates.get("ok") and updates["result"]:
        chat_id = updates["result"][-1]["message"]["chat"]["id"]
    else:
        chat_id = None
except Exception as e:
    print(f"⚠️ Could not get Telegram chat_id: {e}")
    chat_id = None


def calculate_automated_price(base_cost=0.50, target_margin=0.90):
    return round(base_cost / (1 - target_margin), 2)


# 3. RESEARCH
print(f"🚀 SDS Agency: Resilient Cloud Mode Active")
research_prompt = "Identify 3 music and pop culture niches. Output ONLY: Trend:Style:CollectionName"


def safe_generate_text(prompt):
    try:
        response = client.models.generate_content(model=TEXT_MODEL, contents=prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ Text Gen Error (Retrying later): {e}")
        return "Technical:Modern:General"


raw_response = safe_generate_text(research_prompt)
lines = [line.strip() for line in raw_response.split("\n") if ":" in line]

# 4. DRAFT TRACKING
DRAFT_IDS_FILE = "/home/menackie/Workflows/OpenClaw/src/agents/shopify-marketer/draft_ids.json"
with open(DRAFT_IDS_FILE, "w") as f:
    json.dump([], f)
draft_ids = []

# 5. PRODUCTION LOOP
for i, line in enumerate(lines[:3]):
    try:
        parts = [p.strip() for p in line.split(":")]
        trend = parts[0]
        style = parts[1] if len(parts) > 1 else "Modern"

        print(f"\n📡 Requesting {trend} ({style})...")

        # IMAGE GEN — Pollinations.ai (free, no API key)
        # Use more descriptive, random and exciting prompts
        themes = ["Cyberpunk neon aesthetic", "Surreal dreamcore landscape", "Retro-futuristic synthwave", "Ethereal dark fantasy", "Abstract liquid gold flow"]
        import random
        theme = random.choice(themes)
        art_prompt = f"{trend} {theme}, {style} art style, intricate details, high contrast, cinematic lighting, 8k resolution, trending on ArtStation, no humans, no faces"
        print(f"🎨 Generating image via Pollinations (Theme: {theme})...")
        image_path = f"./digital_{i + 1}.png"
        encoded_prompt = requests.utils.quote(art_prompt)
        # Add a random seed to avoid caching
        seed = int(time.time()) + i + random.randint(0, 1000000)
        # Add a more robust negative prompt
        encoded_neg = requests.utils.quote("human, person, face, man, woman, mask, statue, bust, eyes, sketchy, pencil, portrait, ugly, blurry, low quality")
        img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true&negative_prompt={encoded_neg}"
        try:
            img_resp = requests.get(img_url, timeout=120)
            if img_resp.status_code == 200 and len(img_resp.content) > 1000:
                with open(image_path, "wb") as f:
                    f.write(img_resp.content)
                image_data = img_resp.content
                print(f"✅ Image saved: {image_path} ({len(img_resp.content) // 1024}KB)")
            else:
                print(f"⚠️ Pollinations Error: Status {img_resp.status_code}")
                image_data = None
        except Exception as e:
            print(f"⚠️ Pollinations Connection Error: {e}")
            image_data = None

        # SHOPIFY + TELEGRAM — only if we have an image
        if image_data:
            mkt_html = safe_generate_text(f"HTML for {trend}. 30 words.")
            prod = shopify.Product()
            prod.title, prod.body_html, prod.status = f"{trend} Digital Design", mkt_html, "draft"
            prod.vendor = "RB Enterprises"
            variant = shopify.Variant(
                {"price": calculate_automated_price(), "inventory_management": None, "requires_shipping": False}
            )
            prod.variants = [variant]

            with open(image_path, "rb") as f_img:
                img = shopify.Image()
                img.attach_image(f_img.read(), filename=f"digital_{i + 1}.png")
                prod.images = [img]
            prod.save()

            draft_id = prod.id
            draft_ids.append(draft_id)
            draft_url = f"https://{shop_url}/admin/products/{draft_id}"
            print(f"📋 Draft saved: {draft_url}")

            if chat_id:
                print(f"📲 Sending to Telegram (Chat: {chat_id})...")
                tel_res = requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                    data={
                        "chat_id": chat_id,
                        "caption": f"🌀 {trend} Ready for Review!\n🔗 {draft_url}\n\nReply 'approve' to publish all drafts.",
                    },
                    files={"photo": open(image_path, "rb")},
                )
                if tel_res.status_code != 200:
                    print(f"⚠️ Telegram Error: {tel_res.text}")
                else:
                    print(f"✅ Sent to Telegram")
            else:
                print(f"⚠️ Skipping Telegram — no chat_id (send a message to the bot first)")
        else:
            print(f"⚠️ No image returned for {trend}")

        gc.collect()

    except Exception as e:
        print(f"⚠️ Loop Error on {line}: {e}")

print("\n✨ SDS Supplies cycle complete. Check Shopify & Telegram.")
print(f"📋 {len(draft_ids)} drafts saved. Reply 'approve' to publish.")

# Save final draft IDs
with open(DRAFT_IDS_FILE, "w") as f:
    json.dump(draft_ids, f)
