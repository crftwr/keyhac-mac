from PIL import Image

sizes = [1024,512,256,128,64,32,16]

img = Image.open("../DesignAssets/AppIcon-FullSize.png")

for size in sizes:
    print(f"Resizing icon image to {size}x{size}")
    resized_img = img.resize( (size,size) )
    resized_img.save(f"../DesignAssets/AppIcon-{size}.png")
