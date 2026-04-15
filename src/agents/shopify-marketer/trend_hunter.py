import datetime

def generate_seasonal_prompts():
    current_month = datetime.datetime.now().strftime("%B")
    
    print(f"--- R&B ENTERPRISES SEASONAL PROMPT GENERATOR ---")
    print(f"Current Baseline: {current_month} 2026")
    print("Target Markets: Late Spring, Summer Outdoors, Father's Day\n")
    
    print("--- READY-TO-USE IMAGE PROMPTS ---")
    
    # Concept 1: The Sticker
    print("1. [Die-Cut Sticker]")
    print("   THEME: Summer Outdoors / Nature")
    print("   PROMPT: A retro 1970s sunset with silhouetted pine trees and a campfire, vintage distressed style, vector illustration, bold flat colors, solid white background, highly detailed --v 6.0")
    
    # Concept 2: The Coffee Mug
    print("\n2. [Coffee Mug]")
    print("   THEME: Father's Day / Comedy")
    print("   PROMPT: Minimalist typography design, bold athletic font reading 'Professional Grill Master', distressed texture, small vector spatula graphic beneath the text, black text on clean white background")
    
    # Concept 3: The Digital Print / T-Shirt
    print("\n3. [T-Shirt / Digital Print]")
    print("   THEME: Modern Nostalgia / Summer Vacation")
    print("   PROMPT: 90s geometric Memphis style pattern, neon summer colors (teal, hot pink, yellow), vaporwave aesthetic, clean lines, high resolution t-shirt graphic design, isolated on white")

if __name__ == "__main__":
    generate_seasonal_prompts()
