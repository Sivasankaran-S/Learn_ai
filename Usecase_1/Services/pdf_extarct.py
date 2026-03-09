import fitz
from PIL import Image, ImageEnhance
import numpy as np
import cv2
import easyocr
from Services.easy_ocr import ocr_img

# txt_read =PaddleOCR(use_angle_cls = True,lang="en",show_log= False)
esay_ocr = easyocr.Reader(["en"])

def preprocess_np(img_np: np.ndarray) -> np.ndarray:
    """
    Takes OpenCV/Numpy image and returns enhanced grayscale image
    """
    img = Image.fromarray(img_np).convert("L")   # grayscale
    img = img.resize((img.width * 2, img.height * 2))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    return np.array(img)



def txt_from_pdf(pdf_bytes:bytes) -> str:
    #bytes conversion
    pdf = fitz.open(stream=pdf_bytes,filetype="pdf")

    #doc checking
    is_digital = False
    page_wise: dict[int, list[str]] = {}
    ocr_text: list[str] = []
    for i, page in enumerate(pdf,start=1):
        text = page.get_text()
    
        if text.strip():
            is_digital = True
            lines = text.splitlines()
            page_wise[i] = lines
            ocr_text.extend(lines)

    #didgital pdf
    if is_digital:
        return ocr_text
    
    #scanned pdf(img) -> ocr
    
    #preprocessing
    zoom = 4
    mat = fitz.Matrix(zoom,zoom)
    page_wise_txt = {}

    for i,p in enumerate(pdf,start=1):
        
        pix = p.get_pixmap(matrix= mat)

        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 3:
            img_np = cv2.cvtColor(img_np,cv2.COLOR_RGB2BGR)
        else:
            img_np = preprocess_np(img_np)

        result = esay_ocr.readtext(img_np, detail=1)
        print("OCR_READED_DATA:",result)
        clean_lines = []

        for bbox,text,conf in result:
            if conf >= 0.5:          
                clean_lines.append(text)

        page_wise_txt[i] = clean_lines
        ocr_text.extend(clean_lines)
        print({"pdf_extracted_data":page_wise_txt[i],
               "ocr_txt":ocr_text})
    return ocr_text,pdf_bytes