import os
import shopify
from dotenv import load_dotenv

# 1. Connect to the Store
load_dotenv("../../../.env")
shop_url = os.getenv("SHOP_URL", "kev1fr-q4.myshopify.com")
token = os.getenv("SHOPIFY_ACCESS_TOKEN")
api_version = "2026-04"

session = shopify.Session(shop_url, api_version, token)
shopify.ShopifyResource.activate_session(session)

# 2. Grab all products
print(f"🔐 Connected to {shop_url}. Scanning products...")
products = shopify.Product.find(limit=250)

for product in products:
    title = product.title
    updated = False
    
    # Is this a digital file or physical merch?
    is_digital = "Sticker" in title or "Design" in title or "Digital" in title

    for variant in product.variants:
        # Fix Missing Prices (Sets default to $3.00)
        if not variant.price or float(variant.price) == 0.00:
            variant.price = "3.00"
            updated = True
            
        # Fix the "Physical Product" warning for Digital Items
        if is_digital and variant.requires_shipping:
            variant.requires_shipping = False
            variant.weight = 0.0
            updated = True
            
    if updated:
        product.save()
        print(f"✅ Fixed Pricing/Shipping for: {title}")

print("🏁 Store cleanup complete!")
