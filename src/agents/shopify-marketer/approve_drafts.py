#!/usr/bin/env python3
"""
approve_drafts.py — Publish all draft products to Shopify
Run manually or triggered by Telegram 'approve' reply.
"""
import os
import json
import requests
import shopify
from dotenv import load_dotenv

env_path = os.path.expanduser("~/Workflows/OpenClaw/.env")
load_dotenv(dotenv_path=env_path)

shop_url = os.getenv("SHOP_URL", "sdssupplies.myshopify.com")
client_id = os.getenv("SHOPIFY_CLIENT_ID")
client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")

auth_resp = requests.post(
    f"https://{shop_url}/admin/oauth/access_token",
    json={"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"},
    timeout=15
)
if auth_resp.status_code != 200:
    raise Exception(f"Shopify auth failed: {auth_resp.text}")
shop_token = auth_resp.json()["access_token"]
shopify.ShopifyResource.activate_session(shopify.Session(shop_url, '2024-01', shop_token))

DRAFT_IDS_FILE = os.path.expanduser("~/Workflows/OpenClaw/src/agents/shopify-marketer/draft_ids.json")

if not os.path.exists(DRAFT_IDS_FILE):
    print("❌ No drafts found to approve.")
    exit(1)

with open(DRAFT_IDS_FILE) as f:
    draft_ids = json.load(f)

if not draft_ids:
    print("ℹ️  No drafts pending. Nothing to approve.")
    exit(0)

print(f"🚀 Publishing {len(draft_ids)} drafts to Shopify...")
for pid in draft_ids:
    product = shopify.Product.find(pid)
    product.status = "active"
    product.save()
    print(f"  ✅ Published: {product.title} (https://{shop_url}/admin/products/{pid})")

# Clear the queue
with open(DRAFT_IDS_FILE, "w") as f:
    json.dump([], f)

print(f"\n✨ All {len(draft_ids)} products are now LIVE on Shopify!")
