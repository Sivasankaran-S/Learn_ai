from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import pytesseract
from PIL import Image , ImageFilter,ImageEnhance
import easyocr
import re
#OCR
img = Image.open("pan.png")
img = img.resize((img.width * 2,img.height * 2))

# w,h = img.size
# crop = img.crop((0, int(h*0.35), w*0.65, h*0.85))
# crop = crop.convert('L')
# crop = crop.filter(ImageFilter.MedianFilter(size=3))
enhancer = ImageEnhance.Contrast(img)
crop = enhancer.enhance(2.5)

# crop = crop.point(lambda x:0 if x < 140 else 255, "1")
# custom_config = r'''
# --oem 3
# --psm 4
# -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/
# '''
save_img = img.save("after_pre.png")
txt = easyocr.Reader(['en'])
results = txt.readtext("after_pre.png")
ocr_extarcted = []
for _,text,conf in results:
    if conf > 0.5:
        ocr_extarcted.append(text)
cleaned_txt = "\n".join(ocr_extarcted)
print("ocr_txt:","\n",cleaned_txt)

pan_check = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',cleaned_txt)
pan_number = pan_check.group(0) if pan_check else None 

#Langchain llm
llm = ChatOllama(model="gemma3:1b")

#Prompt
tmplt = """
Extarct the details from text
OCR TEXT:
{ocr_txt}

Extraction rules:
- NAME: Appears in uppercase letters.
- DATE OF BIRTH: Format DD/MM/YYYY
- PAN NUMBER: Exactly 10 characters (5 letters, 4 digits, 1 letter)

Do not guess.
If a value is present, extract it.
If missing, return null.

Return ONLY JSON:

{{
  "name": "",
  "date_of_birth": "",
  "pan_number": "{{pan_number}}"
}}
"""

prompt = PromptTemplate(
    template=tmplt,
    input_variables=["ocr_txt"]
)

format_prompt = prompt.format(ocr_txt = cleaned_txt)

#llm call 
result = llm.invoke(format_prompt)

print(result.content)