import os
from openai import OpenAI
from dotenv import load_dotenv

# Loads the keys from your main OpenClaw .env file two directories up
load_dotenv('../../.env')

# Initialize the AI client. 
# NOTE: If you are routing this through your OpenClaw gateway on GCP, 
# you will add base_url="http://YOUR_GATEWAY_IP:PORT/v1" inside OpenAI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_design(trend_keyword):
    """Takes a trending keyword and generates a POD-ready graphic."""
    print(f"\nCreative Director agent designing concept for: '{trend_keyword}'...")
    
    # The prompt forces the AI to design for physical merch
    design_prompt = (
        f"A clean, isolated vector-style graphic for a die-cut sticker or coffee mug "
        f"based on the concept: {trend_keyword}. "
        f"Solid white background, bold lines, striking colors, no text."
    )
    
    try:
        print("Graphic Designer agent rendering image...")
        response = client.images.generate(
            model="dall-e-3",
            prompt=design_prompt,
            size="1024x1024",
            quality="hd",
            n=1,
        )
        
        image_url = response.data[0].url
        print(f"Success! Image ready at: {image_url}")
        return image_url
        
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

if __name__ == "__main__":
    # Test the agent with a fake trend
    generate_design("Retro Cyberpunk Cryptocurrency")
