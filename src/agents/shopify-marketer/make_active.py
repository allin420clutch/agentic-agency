import os
import shopify
from dotenv import load_dotenv

load_dotenv("../../../.env")
session = shopify.Session(os.getenv("SHOP_URL"), "2026-04", os.getenv("SHOPIFY_ACCESS_TOKEN"))
shopify.ShopifyResource.activate_session(session)

print("🟢 Flipping Draft Stickers to Active...")
products = shopify.Product.find(limit=250)
for p in products:
    if p.status == "draft" and ("Sticker" in p.title or "Design" in p.title):
        p.status = "active"
        p.save()
        print(f"✅ Made Active: {p.title}")
print("Done.")
