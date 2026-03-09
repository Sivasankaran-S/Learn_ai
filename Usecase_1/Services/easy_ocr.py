from PIL import Image ,ImageEnhance
import easyocr
import io
import numpy as np
#easyocr
txt_read = easyocr.Reader(['en'])

#img-preprocess

def ocr_img(img_byes:bytes) -> str:
    #byes to img
    img = Image.open(io.BytesIO(img_byes))

    #now img preprocess

    #1.resize
    img = img.resize((img.width * 2,img.height * 2))
    
    #2.Contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)

    img_np  = np.array(img)
    #text Extarction
    result = txt_read.readtext(img_np)
    print("Result:",result)
    extraxtion = []
    for _,text,conf in result:
        if conf > 0.5:
            extraxtion.append(text)
    print("Extraction:",extraxtion)
    return extraxtion