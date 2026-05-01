import os
import shopify
import glob
from dotenv import load_dotenv

load_dotenv("../../../.env")
session = shopify.Session(os.getenv("SHOP_URL"), "2026-04", os.getenv("SHOPIFY_ACCESS_TOKEN"))
shopify.ShopifyResource.activate_session(session)

vault_path = "../../../Store_Assets/Digital_Downloads/"
files = glob.glob(vault_path + "*_transparent.png")

print(f"🔍 Found {len(files)} actual transparent files on your hard drive.")
print("🏗️ Building exact matching products on Shopify...")

count = 0
for file_path in files:
    filename = os.path.basename(file_path)
    # Clean up the name (e.g., "daily_trend_1_transparent.png" -> "Daily Trend 1")
    clean_name = filename.replace("_transparent.png", "").replace("_", " ").title()
    title = clean_name + " Sticker"
    
    new_product = shopify.Product()
    new_product.title = title
    new_product.status = "active"
    new_product.vendor = "SDS Supplies"
    new_product.tags = "Digital"
    
    variant = shopify.Variant()
    variant.price = "3.00"
    variant.requires_shipping = False
    new_product.variants = [variant]
    
    new_product.save()
    print(f"✅ Created perfect match: {title}")
    count += 1

print(f"🏁 Done! Created {count} new products that exactly match your files.")
