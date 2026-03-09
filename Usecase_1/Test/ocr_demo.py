from PIL import Image,ImageFilter,ImageEnhance
import pytesseract
import easyocr
import numpy as np
from pytesseract import Output
img = Image.open('aadhar1.jpeg')

img = img.resize((img.width * 2,img.height * 2))
    
#2.Contrast
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.5)

img_np  = np.array(img)

# img = img.convert('L')
# print("Grayscal:","\n",img)

# img = img.filter(ImageFilter.MedianFilter())
# print("Image Filter:","\n",img)

# enhancer = ImageEnhance.Contrast(img)
# print("Before Enhanced","\n",enhancer)

# img = enhancer.enhance(3)
# print("After Enhace:","\n",img)

txt = easyocr.Reader(['ta'],gpu=False)
result = txt.readtext(img_np,detail=0)
print("img to string:",result)
#result = pytesseract.image_to_data(txt,output_type=Output.DICT)
#print(result)
# img = Image.open('img.png')

# txt = pytesseract.image_to_string(img)

# print(txt)