import os
import requests
import base64
import json

# Read .env robustly
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
CLIENT_ID = env_vars.get("SHOPIFY_API_KEY", "")
CLIENT_SECRET = env_vars.get("SHOPIFY_API_SECRET", "")

if not CLIENT_ID or not CLIENT_SECRET or not SHOP_URL:
    print(f"Error: Missing SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET, or SHOP_URL in .env.")
    print(f"Found variables: {list(env_vars.keys())}")
    exit(1)

print(f"Authenticating with {SHOP_URL} using CLI App Credentials...")

# We are going to attempt to exchange the Client ID/Secret for an access token.
# Note: For custom apps built via the CLI, you usually still need to install them
# through the Shopify admin URL to get a permanent token. This tries the standard OAuth flow.

auth_url = f"https://{SHOP_URL}/admin/oauth/access_token"
auth_payload = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials"
}

auth_response = requests.post(auth_url, json=auth_payload)

if auth_response.status_code != 200:
    print(f"❌ Authentication Failed: {auth_response.status_code}")
    print(auth_response.text)
    print("\nThis usually means your CLI app needs to be manually installed on the store.")
    print(f"Go to this URL to install it: https://{SHOP_URL}/admin/oauth/authorize?client_id={CLIENT_ID}&scope=write_products,write_files&redirect_uri=https://localhost:3000/auth/callback")
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
            "status": "active",
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
        print(f"✅ Success! Published ACTIVE product for {filename}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)

print("\nSync complete! Check your Shopify Drafts.")
