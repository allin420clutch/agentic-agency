import os
from openai import OpenAI
from dotenv import load_dotenv

# Load the keys from the main .env file
load_dotenv('../../.env')

# Initialize the AI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_design(trend_keyword):
    """Generates a POD-ready graphic."""
    print(f"\nCreative Director agent designing concept for: '{trend_keyword}'...")
    
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
    generate_design("Retro Cyberpunk Cryptocurrency")
