import uuid

#OCR_TXT --> STORE
ocr_data_store = {}

#CHAT --> STORE [ {question,answer}]
chat_store = {} 


def create_session(extracted_data,summary,document_type):
    session_id = str(uuid.uuid4())
    ocr_data_store[session_id] = {
        "Doc_type":document_type,
        "Extracted_text":extracted_data,
        "Summarize":summary
    }
    chat_store[session_id] = []
    return session_id

def get_cor_txt(session_id):
    return ocr_data_store.get(session_id)
#[session_id]["Extarcted_text"],ocr_data_store[session_id]["Summarize"]

def add_chat(session_id,question,answer):
    chat_store[session_id].append({
        "question":question,
        "answer":answer
    })

def get_chat_history(session_id):
    return chat_store.get(session_id,[])


def session_exist(session_id):
    return session_id in ocr_data_store