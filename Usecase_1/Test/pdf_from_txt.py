from PIL import Image, ImageEnhance
import fitz
import easyocr
import numpy as np
pdf_file = "invoice_document _flip-slop.pdf"

def preprocess(img_path):
    img = Image.open(img_path).convert("L")  # grayscale
    img = img.resize((img.width * 2, img.height * 2))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    return np.array(img)

img = fitz.open(pdf_file)
zoom = 4
mat = fitz.Matrix(zoom,zoom)
count = 0
images = []
for p in img:
    count += 1
for i in range(count):
    val = f"image_{i+1}.png"
    page = img.load_page(i)
    pix = page.get_pixmap(matrix= mat)
    pix.save(val)
    images.append(val)

img.close()

reader = easyocr.Reader(['en'],gpu=False)
all_text = []

for img in images:
    img_np = preprocess(img)
    text = reader.readtext(img_np, detail=0)
    all_text.extend(text)

print("images_txt",all_text)



    # for p in pdf:
    #     # val = f"image_{i+1}.png"
    #     # page = pdf.load_page(i)
    #     pix = p.get_pixmap(matrix= mat)
    #     img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    #     if pix.n == 3:
    #         img = cv2.cvtColor(img_np,cv2.COLOR_RGB2BGR)
    #     else:
    #         img = img_np
    # for page in pdf:
    #     pix = page.get_pixmap(matrix=mat)
    #     img_np = np.frombuffer(pix.samples, dtype=np.uint8)
    #     img_np = img_np.reshape(pix.height,pix.width,pix.n)
        # img_bytes = pix.tobytes("png")
        # ocr_text += ocr_img(img_bytes)