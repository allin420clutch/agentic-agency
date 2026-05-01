import os
import base64
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load API keys
load_dotenv(dotenv_path=os.path.expanduser("~/Workflows/OpenClaw/.env"))

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=60000)
)

def generate_with_retry(prompt):
    print(f"📡 Requesting: {prompt}")
    try:
        # Using the Gemini 3.1 Flash Image model
        response = client.models.generate_content(
            model='gemini-3.1-flash-image-preview',
            contents=[f"Die-cut sticker: {prompt}. White background. Vector art."]
        )
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return part.inline_data.data
    except Exception as e:
        if "429" in str(e):
            print("⏳ Quota hit! Cooling down for 15 seconds...")
            time.sleep(15)
        else:
            print(f"🛑 Error on '{prompt}': {e}")
    return None

stickers = ["Cybersecurity Hacker", "TIG Welder", "AI Neural Brain"]

for s in stickers:
    img_data = generate_with_retry(s)
    if img_data:
        filename = f"{s.replace(' ', '_').lower()}.png"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(img_data))
        print(f"✅ Saved: {filename}")
        # Gap to stay under free-tier limits
        time.sleep(10) 

print("\n✨ Generation attempt finished.")
