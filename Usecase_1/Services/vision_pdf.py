import fitz
import base64
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

vision_model = ChatOllama(model="qwen3-vl:4b-instruct")
prompt = "Extract the all possible text with accurately"

def extract_pdf_text(pdf_bytes:bytes):
    doc = fitz.open(stream=pdf_bytes,filetype="pdf")
    page = doc.load_page(0) #open the first page
    pix = page.get_pixmap(matrix=fitz.Matrix(2,2))
    img =  pix.tobytes("jpg")

    img_base = base64.b64encode(img).decode("utf-8")

    message = HumanMessage(
        content = [
            {"type":"text","text":prompt},
            {"type":"image_url","image_url":f"data:image/jpg;base64,{img_base}"}
        ]
    )

    response = vision_model.invoke([message])

    result = response.content

    print(result)
    return result

def extract_image_text(image_bytes:bytes):
    img_base = base64.b64encode(image_bytes).decode("utf-8")
    message = HumanMessage(
        content = [
            {"type":"text","text":prompt},
            {"type":"image_url","image_url":f"data:image/jpg;base64,{img_base}"}
        ]
    )

    response = vision_model.invoke([message])

    result = response.content

    print("Img",result)
    return result