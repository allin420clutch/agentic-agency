import os
import requests
import base64
import json
import time

env_vars = {}
try:
    with open("/home/menackie/Workflows/OpenClaw/.env") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip('"').strip("'")
except FileNotFoundError:
    print("Could not find .env file!")
    pass

SHOP_URL = env_vars.get("SHOP_URL", "")
CLIENT_ID = env_vars.get("SHOPIFY_CLIENT_ID", "")
CLIENT_SECRET = env_vars.get("SHOPIFY_CLIENT_SECRET", "")

if not CLIENT_ID or not CLIENT_SECRET or not SHOP_URL:
    print(f"Error: Missing SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET, or SHOP_URL in .env.")
    exit(1)

print(f"Authenticating with {SHOP_URL} using Custom App Credentials...")

# Shopify Custom Apps use the Admin API token, not the OAuth flow.
# But since you have the Client ID/Secret from the Partner Dashboard, 
# we need to execute the OAuth flow to get the access token.
# To bypass the web browser loop, we will use the `client_credentials` grant type
# which allows server-to-server auth without a user login screen.

auth_url = f"https://{SHOP_URL}/admin/oauth/access_token"
auth_payload = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials"
}

auth_response = requests.post(auth_url, json=auth_payload)

if auth_response.status_code != 200:
    print(f"❌ Authentication Failed: {auth_response.status_code}")
    print("Shopify requires a human to click 'Install' on this specific app before it will give out the keys.")
    print(f"\n👉 PLEASE COPY AND PASTE THIS EXACT LINK INTO YOUR BROWSER AND CLICK INSTALL:")
    print(f"https://{SHOP_URL}/admin/oauth/authorize?client_id={CLIENT_ID}&scope=write_products,read_products,write_files,read_files&redirect_uri=https://shopify.dev/apps/default-app-home/api/auth")
    print("\nAfter you click Install on that page, the browser will say 'localhost refused to connect' or redirect to the Shopify Dev docs. THAT IS PERFECTLY FINE.")
    print("Once you click install, run this script again and it will work immediately.")
    exit(1)

access_token = auth_response.json().get("access_token")

HEADERS = {
    "X-Shopify-Access-Token": access_token,
    "Content-Type": "application/json"
}

ASSETS_DIR = "/home/menackie/Workflows/OpenClaw/Store_Assets/Raw_Generations"

if not os.path.exists(ASSETS_DIR):
    print(f"Error: Directory {ASSETS_DIR} not found.")
    exit(1)

files_to_sync = [f for f in os.listdir(ASSETS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg'))]

if not files_to_sync:
    print(f"No image files found in {ASSETS_DIR} to sync.")
    exit(0)

print(f"✅ Authenticated! Syncing {len(files_to_sync)} files...")

for filename in files_to_sync:
    filepath = os.path.join(ASSETS_DIR, filename)
    print(f"\nProcessing {filename}...")
    
    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        
    title = filename.rsplit(".", 1)[0].replace("_", " ").title()
    
    payload = {
        "product": {
            "title": f"Viral Sticker: {title}",
            "body_html": f"<strong>High-quality trending sticker design: {title}</strong>",
            "vendor": "OpenClaw AI",
            "product_type": "Digital Download",
            "status": "draft",
            "images": [
                {
                    "attachment": encoded_string,
                    "filename": filename
                }
            ]
        }
    }
    
    endpoint = f"https://{SHOP_URL}/admin/api/2024-01/products.json"
    response = requests.post(endpoint, headers=HEADERS, json=payload)
    
    if response.status_code == 201:
        print(f"✅ Success! Created draft product for {filename}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
    
    time.sleep(1) # Prevent rate limiting

print("\nSync complete! Check your Shopify Drafts.")
