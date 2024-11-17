import os
from PIL import Image

sizes = [1024,512,256,128,64,32,16]

this_directory = os.path.dirname(__file__)
fullsize_image_path = os.path.join(this_directory, "../DesignAssets/AppIcon-FullSize.png")

img = Image.open(fullsize_image_path)

for size in sizes:
    print(f"Resizing icon image to {size}x{size}")
    resized_img = img.resize( (size,size) )
    resized_image_path = os.path.join(this_directory, f"../DesignAssets/AppIcon-{size}.png")
    resized_img.save(resized_image_path)
