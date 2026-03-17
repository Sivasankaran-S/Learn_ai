from fastapi import FastAPI,UploadFile,File,Form,HTTPException
from Services.easy_ocr import ocr_img
from Services.pdf_extarct import txt_from_pdf
# from Services.langchain_llm import extract_details
from fastapi.middleware.cors import CORSMiddleware
from Services.Memory.store_session import (create_session,get_cor_txt,add_chat,get_chat_history,session_exist)    
from pydantic import BaseModel
from Services.chat import response_from_ai
from Services.vision_pdf import extract_pdf_text,extract_image_text
from Services.llm import extract_details
from Services.doc_check import verify_document

app = FastAPI(title="test docai")

class Chat_AI(BaseModel):
    session_id : str
    question : str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow Angular
    allow_credentials=True,
    allow_methods=["*"],          # allow POST, OPTIONS
    allow_headers=["*"],          # allow Content-Type, Authorization
)

@app.post("/uploadfiles")
async def create_upload_file(file: UploadFile = File(...),
    doctype: str = Form(...)):
    file_type = file.filename.lower()
    file_bytes = await file.read()
    images = (".png",".jpg",".jpeg")

    if file_type.endswith(images):
        text =extract_image_text(file_bytes)
    
    elif file_type.endswith(".pdf"):
        text = extract_pdf_text(file_bytes)

    else:
        raise HTTPException(status_code=400,detail="UnsupportedFile")
    
    validation = verify_document(text, doctype)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])
    
    result = extract_details(text,doctype)
    session_id = create_session(extracted_data= result["Extracted_text"],
                                summary=result["Summary"],
                                document_type=result["Doc_type"])
    return {"Final_result":result,
            "status":"SUCCESS",
            "session_id":session_id}


@app.post("/chat")
async def Chat_Response(req:Chat_AI):
    userquery = req.question.lower()

    if not session_exist(req.session_id):
        raise HTTPException (status_code=404,detail="Invalid Session")
    
    ocr_txt = get_cor_txt(req.session_id)
    chat_history = get_chat_history(req.session_id)

    user_res = response_from_ai(
        ocr_txt=ocr_txt,
        chat_history= chat_history,
        question=userquery)
    
    add_chat(req.session_id,req.question,user_res)

    return {
        "ai_res":user_res,
        "chat_history":get_chat_history(req.session_id)
    }
