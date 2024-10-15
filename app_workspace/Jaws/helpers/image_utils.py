from PIL import Image

def getImageWidth(image_path:str) -> int:
    with Image.open(image_path) as img:
        return img.width