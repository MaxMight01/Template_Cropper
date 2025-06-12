from PIL import Image

def load_image(path):
    return Image.open(path)

def crop_image(image, x, y, box_size):
    half = box_size // 2
    left = x - half
    top = y - half
    right = x + half
    bottom = y + half

    if left < 0 or top < 0 or right > image.width or bottom > image.height:
        return None  # out of bounds
    return image.crop((left, top, right, bottom))

def save_image(image, path):
    image.save(path)
