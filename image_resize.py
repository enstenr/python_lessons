import os
from PIL import Image, ImageOps

# Root folder containing images
ROOT_DIR = "/home/btcchl0040/Documents/Internship-KSB/Photos"

# Walk through all subfolders
for root, dirs, files in os.walk(ROOT_DIR):
    for filename in files:
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(root, filename)
            with Image.open(img_path) as img:
                # Apply EXIF rotation to get correct orientation
                img = ImageOps.exif_transpose(img)

                w, h = img.size
                print(f"{filename}: {w}x{h}")

                # Rotate portrait images
                if h > w:
                    print(f"Rotating {filename} to landscape")
                    img = img.rotate(90, expand=True)
                    # Overwrite original image
                    img.save(img_path)

print("All images processed!")
