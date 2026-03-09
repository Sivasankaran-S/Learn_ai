from ollama import chat
from PIL import Image
import base64

def img_to_base64(path):
    with open(path,"rb") as f:
        return base64.b64encode(f.read()).decode()
    
img = img_to_base64("SBI.jpeg")

prompt = """

You are an OCR system.

TASK:
Extract details ONLY if their exact label is present.


FIELDS:
- name - mentioned as labeled "Name"
- cif_number - mentioend as labeled "CIF No".
- account_number - mentioned as label such as "Account No", "A/C No", or "Account Number".
- ifsc_code
- branch_code

RULES:
- Do NOT confused between cif_number and account_number.
- Must Check the Label for Identify the cif_number and account_number.
- Do NOT guess.
- If more than one NAME exists, choose the first alphabetic name.
- If unsure, return null.

No need extra details

"""

response = chat(
    model="qwen3-vl:4b-instruct",
    messages=[
        {
            "role":"user",
            "content":prompt,
            "images":[img]
                
        }
    ]
)


print(response["message"]["content"])