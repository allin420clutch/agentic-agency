from rembg import remove
import os

print("✂️ Initializing Background Removal Agent...")
for file in os.listdir("."):
    if file.endswith(".png") and "transparent" not in file and "sticker" in file:
        with open(file, 'rb') as i:
            input_data = i.read()
            output_data = remove(input_data)
            output_path = f"transparent_{file}"
            with open(output_path, 'wb') as o:
                o.write(output_data)
        print(f"✅ Created paste-ready version: {output_path}")
