from PIL import Image, ImageEnhance
import easyocr
import numpy as np

img = Image.open('IN.jpeg')

# Resize
img = img.resize((img.width * 2, img.height * 2))

# Contrast
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.5)

img_np = np.array(img)

# ✅ Correct EasyOCR usage
reader = easyocr.Reader(['en'], gpu=False)
result = reader.readtext(img_np, detail=0)

print("img to string:", result)
