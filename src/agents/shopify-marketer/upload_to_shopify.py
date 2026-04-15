import os
import shopify
from dotenv import load_dotenv

# Setup
load_dotenv()
token = os.getenv("SHOPIFY_ACCESS_TOKEN")
# Failsafe: If the .env forgets the URL, it defaults to your actual store
shop_url = os.getenv("SHOP_URL", "sdssupplies.myshopify.com")

print(f"🔐 Connecting to {shop_url} using shpat_ token...")

if not token or not token.startswith("shpat_"):
    print("❌ ERROR: Your SHOPIFY_ACCESS_TOKEN in the .env file is missing or incorrect. It MUST start with 'shpat_'")
    exit()

# Connect to Store
api_version = '2024-01'
session = shopify.Session(shop_url, api_version, token)
shopify.ShopifyResource.activate_session(session)

def upload_sticker(image_path, title, description):
    if not os.path.exists(image_path):
        print(f"⚠️ Skipping {title}: Could not find {image_path}")
        return

    print(f"📦 Uploading '{title}' to Shopify...")
    
    new_product = shopify.Product()
    new_product.title = title
    new_product.body_html = description
    new_product.vendor = "R&B Enterprises"
    new_product.product_type = "Sticker"
    new_product.status = "draft"
    
    # FIX: Hand Shopify the raw image file, let it do the translation
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    image = shopify.Image()
    image.attach_image(image_data, filename=os.path.basename(image_path))
    new_product.images = [image]
    
    if new_product.save():
        print(f"✅ Success! Product ID: {new_product.id} is now in Drafts.")
    else:
        print(f"❌ Error: {new_product.errors.full_messages()}")

# Upload the 3 designs
upload_sticker("./daily_trend_1.png", "2026 Trend Design 1", "High-contrast minimalist die-cut sticker.")
upload_sticker("./daily_trend_2.png", "2026 Trend Design 2", "High-contrast minimalist die-cut sticker.")
upload_sticker("./daily_trend_3.png", "2026 Trend Design 3", "High-contrast minimalist die-cut sticker.")
