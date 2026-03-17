import fitz
import base64
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

vision_model = ChatOllama(model="qwen3-vl:4b-instruct")
VISION_PROMPT = """You are a text extraction system.
 
Your ONLY job is to read and return the text exactly as it appears in the image.
 
STRICT RULES:
1. Extract English text only.
2. If text is in any regional language (Tamil, Hindi, Telugu, etc.), SKIP that line entirely.
3. If any English text is unclear or unreadable, write [UNCLEAR] in its place. Do NOT guess.
4. Do NOT translate, transliterate, or interpret any text.
5. Do NOT correct spelling or assume missing characters.
6. Do NOT add any explanation, heading, or summary.
7. Preserve the exact layout — output one line of text per line.
8. Return ONLY the extracted text. Nothing else.
"""

def extract_pdf_text(pdf_bytes:bytes):
    doc = fitz.open(stream=pdf_bytes,filetype="pdf")
    page = doc.load_page(0) #open the first page
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5,1.5))
    img =  pix.tobytes("jpg")

    img_base = base64.b64encode(img).decode("utf-8")

    message = HumanMessage(
        content = [
            {"type":"text","text":VISION_PROMPT},
            {"type":"image_url","image_url":f"data:image/jpg;base64,{img_base}"}
        ]
    )

    response = vision_model.invoke([message])

    result = response.content

    print("pdf-data:",result)
    return result

def extract_image_text(image_bytes:bytes):
    img_base = base64.b64encode(image_bytes).decode("utf-8")
    message = HumanMessage(
        content = [
            {"type":"text","text":VISION_PROMPT},
            {"type":"image_url","image_url":f"data:image/jpg;base64,{img_base}"}
        ]
    )

    response = vision_model.invoke([message])

    result = response.content

    print("Img",result)
    return result