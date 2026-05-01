import os
from rembg import remove
from PIL import Image

print("⚙️ Starting RB Enterprises Label Conversion...")

for file in os.listdir("."):
    if file.lower().endswith(".jpg") or file.lower().endswith(".jpeg"):
        print(f"✂️ Processing {file}...")
        
        # Open the JPEG
        input_image = Image.open(file)
        
        # Remove background and convert to PNG (this makes it transparent)
        output_image = remove(input_image)
        
        # Save as a high-quality PNG
        new_name = os.path.splitext(file)[0] + "_transparent.png"
        output_image.save(new_name)
        print(f"✅ Created: {new_name}")

print("✨ Done. Upload the '_transparent.png' files to Shopify now.")
