import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import re
from Services.prompts import (
    PAN_PROMPT,
    AADHAAR_PROMPT,
    VOTERID_PROMPT,
    DRIVING_PROMPT,
    BANK_PROMPT,
)
#llm model 
llm = ChatOllama(model="gemma3:1b")

# doc_type_template = """
#     you are a document type classifier.

#     Identify the document type using ONLY the OCR TEXT:
#     {ocr_txt}

#     RULES:
#     DON'T mind text as uppercase or lowercase
#     - If OCR text contain:
#         "Permanent Account Number Card" OR "Income Tax Department",
#         classify as: PAN

#     - If OCR text contain:
#         "Aadhaar" OR 12-digit numeric number,
#         classify as: AADHAAR

#     -Otherwise classify as : UNKNOWN

#     Retrun ONLY one word
    
#     Example:
#     PAN
#     AADHAAR
#     UNKNOWN


# """

TMPT = """ You are helpful assistant and Expert

Extarct the details from text
OCR TEXT:
{ocr_txt}

Extarct rules:
- NAME: Appears in uppercase letters.
- DATE OF BIRTH: Format DD/MM/YYYY
- PAN NUMBER: Exactly 10 characters (5 letters, 4 digits, 1 letter)

Do not guess.
If a value is present, extract it.
If missing, return null.


Return exactly this structure:

{{
  "NAME": "",
  "DATE_OF_BIRTH": "",
  "PAN_NUMBER": "{pan_number}"
}}

"""

Summary_template = """

You are great Summarizer

Summarize Rule:
Use ONLY the extracted data below.
-Maximum 5 lines.
-Each line have proper context.
-Easy to understand
-Use Bold for keywords.
-NOT a paragraph or Article.
-

Extracted Data:
- Name: {name}
- Date of Birth: {dob}



OUTPUT EXAMPLE:
1.This is a Pancard Apporved by GOVT.OF.INDIA.
2.Used for INCOME TAX Regulations.
3.Issued by INCOME TAX DEPARTMENT.
4.Your Permanent Account Number Card is : {pan_number}
5.It's Considered OFFICIAl DOCUMENT in INDIA.

"""

voter_id_template = """
You are an Expert Voter-ID document extractor.

Extract ONLY what is present in the OCR text.
Do NOT guess or assume.

OCR TEXT:
{ocr_txt}

RULES:
- NAME: Person name
- DATE_OF_BIRTH: DD-MM-YYYY
- GENDER: MALE / FEMALE / OTHER


If a field is missing, return null.

Return EXACT JSON (no markdown):

{{
  "NAME": null,
  "DATE_OF_BIRTH": null,
  "GENDER": null,
  "VOTERID_NUMBER": "{voter_id}"

}}

"""

voterid_summary_template = """
 You are a great summarizer 

Summarize Rule:
Use ONLY the {ocr_txt} data.
-Maximum 3 lines.
-Each line have proper context.
-Easy to understand
-Use Bold for keywords.
-NOT a paragraph or Article.


OUTPUT EXAMPLE:
1.This is a Voter-id Apporved by GOVT.OF.INDIA.
2.Its Used for votting purpose in INDIA.
3.It's Considered OFFICIAl DOCUMENT in INDIA.
"""

driving_template = """
You are an Expert Driving Licence document extractor.

Extract ONLY what is present in the OCR text.
Do NOT guess or assume.

OCR TEXT:
{ocr_txt}

RULES:
- NAME: A person name written in capital letters.
- DATE_OF_BIRTH: A date near keywords like DOB or a date formatted like DD-MM-YYYY or DD-MMYYYY.
- Driving_Licence_id: Starts with 2 capital letters followed by 2 digits and 11 digits (spaces allowed).
- If more than one NAME exists, choose the first alphabetic name.
- If a value is not found, return null.

OUTPUT FORMAT (JSON only, no markdown):

Keys:
NAME
DATE_OF_BIRTH
Driving_Licence_id

"""

driving_summary_template = """
 You are a great summarizer 

Summarize Rule:
Use ONLY the {ocr_txt} data.
-Maximum 3 lines.
-Each line have proper context.
-Easy to understand
-Use Bold for keywords.
-NOT a paragraph or Article.
- If more than one NAME exists, choose the first alphabetic name.

OUTPUT EXAMPLE:
1.This is a Driving License Apporved by GOVT.OF.INDIA.
2.Its Used for Driving purpose in INDIA.
3.It's Considered OFFICIAl DOCUMENT in INDIA.

enough 3 lines
no need extra content.
"""
aadhaar_template = """

You are an Aadhaar document extractor.

Extract ONLY what is present in the OCR text.
Do NOT guess or assume.

OCR TEXT:
{ocr_txt}

RULES:
- NAME: 
- Person name usually appears near the top.
- It may appear in regional language and English.
- If two names exist, prefer the English name.

- DATE_OF_BIRTH: DD/MM/YYYY
- GENDER: MALE / FEMALE / OTHER



If a field is missing, return null.

Return EXACT JSON (no markdown):

{{
  "NAME": ,
  "DATE_OF_BIRTH": ,
  "GENDER": ,
  "AADHAAR_NUMBER": "{aadhaar_no}",
  "ADDRESS":"{address}"

}}

"""
AADHAAR_SUMMARY_TMPT = """
Summarize using ONLY extracted data.
Max 3 bullet points.
No assumptions.

Extracted Data:
- Name: {name}
- Date of Birth: {dob}
- Gender: {gender}
- Aadhaar Number: {aadhaar_no}

Example format:
1. This is an **Aadhaar Card**.
2. Issued by **UIDAI**.
3. Used as **identity proof** in India.
"""

summarize_prompt = PromptTemplate(template=Summary_template,input_variables=["ocr_txt","pan_number"])


prompt = PromptTemplate(
    template= TMPT,
    input_variables=["ocr_txt","pan_number"])

# doc_type_prompt = PromptTemplate(
#      template=doc_type_template,
#      input_variables=["ocr_txt"])
bank_template = """

You are an OCR system.

TASK:
this is data {ocr_txt} for extraction.
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
bank_summary_tempalte = """

You are a great summarizer 

Summarize Rule:
Use ONLY the {ocr_txt} data.
-Maximum 3 lines.
-Each line have proper context.
-Easy to understand
-Use Bold for keywords.
-NOT a paragraph or Article.
- If more than one NAME exists, choose the first alphabetic name.

Example format:
1. This is an **Bank Pass Book**.
2. Issued by **the bank name**.
3. Used as **identity proof** in India.
"""


def text_normalize(lines:str):
    normalized = []

    for line in lines:
        line = line.upper()

        # Fix common OCR mistakes
        line = line.replace("RADHAAR", "AADHAAR")
        line = line.replace("RADDHAAR", "AADHAAR")
        line = line.replace("UNQJE", "UNIQUE")

        # Remove junk characters
        line = re.sub(r"[^A-Z0-9:/\- ]", " ", line)
        line = re.sub(r"\s+", " ", line).strip()

        if len(line) >= 3:
            normalized.append(line)

    return normalized

def doc_type_check(doc:str):
    # normalized_lines = text_normalize(ocr_txt)
    # text = " ".join(normalized_lines).upper()
    # text = " ".join(ocr_txt).upper()

    #DOC_TYPE CHECK
    if "P" in doc:
       return "PAN"
    elif "A" in doc:
        return "AADHAAR"
    # elif re.search(r"\b\d{12}\b",text.replace(" "," ")):
    #     return "AADHAAR"
    elif "V" in doc:
        return "VOTERID"
    elif "D" in doc:
        return "DRIVING"
    elif "B" in doc:
        return "BANK"
    else:
        return "UNKNOWN"

def extract_details(ocr_txt:str,doc:str):
    
    # doc_formatted_prompt = doc_type_template.format(ocr_txt = ocr_txt)
    # doc_result = llm.invoke(doc_formatted_prompt)
    # document_type = doc_result.content.strip().upper()
    document_type = doc_type_check(doc)
    ocr_txt = ocr_txt.splitlines()
    if document_type == "PAN":
    
        pan_number = None
        for i,line in enumerate(ocr_txt):
            if "Permanent Account Number Card" in line:
                next_line = ocr_txt[i+1:i+3]
                for pan_no in next_line:
                    if len(pan_no) >= 10:
                        pan_list = list(pan_no)
                        pan_digit_check = {
                            "O":"0",
                            "I":"1",
                            "S":"5"
                        }

                        for j in range(5,9):
                            if pan_list[j] in pan_digit_check:
                                pan_list[j] = pan_digit_check[pan_list[j]]
                        pan_number = "".join(pan_list)
                        break
                    if pan_number:
                        break
        # pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',ocr_txt)
        # pan_number = pan_match.group(0) if pan_match else None
        formatted = prompt.format(ocr_txt = ocr_txt,pan_number=pan_number)
        result = llm.invoke(formatted)
        
        raw_content = result.content.strip()
        clean = re.sub(r"```json|```","",raw_content).strip()
        json_match = re.search(r"\{.*\}",clean,re.DOTALL)
        if not json_match:
            raise ValueError("No JSON returned by LLM")

        parsed_data = json.loads(json_match.group())
        
        
        summarize_format = summarize_prompt.format( ocr_txt = ocr_txt,name=parsed_data.get("NAME"),
        dob=parsed_data.get("DATE_OF_BIRTH"),
        pan_number = pan_number)

        summarize_result = llm.invoke(summarize_format)
        
        return {
            "Doc_type":document_type,
            "Extracted_text": result.content,
            "Summarize":summarize_result.content
        }
    elif document_type == "AADHAAR":
        #ocr_txt = ocr_txt.splitlines()
        text = "\n".join(ocr_txt).upper()

        aadhaar_no = None
        for line in ocr_txt:
            upper_line = line.upper()

            #Skip DOB / date lines
            if "DOB" in upper_line or "/" in line:
                continue

            # Keep only digits
            digits = re.sub(r"\D", "", line)

            # Aadhaar must be EXACTLY 12 digits
            if len(digits) == 12:
                aadhaar_no = digits
                break

        print("Final Aadhaar:", aadhaar_no)
        # capture = False
        # address_lines = []
        # for i,line in enumerate(ocr_txt):
        #     if "Address:" in line:
        #         capture = True
        #         continue
        #     if capture:
        #         digits = re.sub(r"\D", "", line)
        #         if len(digits) == 12 or line == "" or len(line) < 3:
        #             break
        #         address = ", ".join(address_lines) if address_lines else None
        #         print("Final Address:", address)
        
        #llm extraction
        extract_prompt = PromptTemplate(template=aadhaar_template,
                                        input_variables=["ocr_txt","aadhaar_no","address"])
        address = ""
        formatted_prompt = extract_prompt.format(ocr_txt=text,aadhaar_no = aadhaar_no,address = address)
        result = llm.invoke(formatted_prompt)

        raw = result.content.strip()

        clean = re.sub(r"```json|```","",raw).strip()
        json_match = re.search(r"\{.*\}",clean,re.DOTALL)
        if not json_match:
            raise ValueError("No JSON returned by LLM")

        parsed_data_aadhar = json.loads(json_match.group())


        summary_aadhar_prompt = PromptTemplate(
            template=AADHAAR_SUMMARY_TMPT,
            input_variables=["name","dob","gender","aadhaar_no"]
        )

        summary_text_aadhar = summary_aadhar_prompt.format(
            name = parsed_data_aadhar.get("NAME"),
            dob = parsed_data_aadhar.get("DATE_OF_BIRTH"),
            gender = parsed_data_aadhar.get("GENDER"),
            aadhaar_no = aadhaar_no
        )

        summary_result = llm.invoke(summary_text_aadhar)

        return {
            "Doc_type":document_type,
            "Extracted_text": result.content,
            "Summarize":summary_result.content
        }
    
    elif document_type == "VOTERID":
        voter_id = None
        text = "\n".join(ocr_txt)
        for line in ocr_txt:
            voter_pattern = re.fullmatch(r"[A-Z]{3}[0-9]{7}",line.strip())    
            if voter_pattern:
                voter_id = voter_pattern.group()
                break
                
            
        voter_prompt = PromptTemplate(
            template=voter_id_template,
            input_variables=["ocr_txt","voter_id"])

        voter_id_formatted = voter_prompt.format(ocr_txt = text,voter_id = voter_id)
        voter_result = llm.invoke(voter_id_formatted)
        print("Votter_data",voter_result.content)

        voter_summary_prompt = PromptTemplate(template=voterid_summary_template,input_variables=["ocr_txt"])
        voter_summary_formatted = voter_summary_prompt.format(ocr_txt = text)
        voter_summary_result = llm.invoke(voter_summary_formatted)
        print("Summary_result",voter_summary_result)
        return {
            "Doc_type":document_type,
            "Extracted_text": voter_result.content,
            "Summarize":voter_summary_result.content
        }
    
    elif document_type == "DRIVING":
        text = "\n".join(ocr_txt)

        Driving_prompt = PromptTemplate(
            template=driving_template,
            input_variables=["ocr_txt"])
        
        Driving_format = Driving_prompt.format(ocr_txt = text)

        driving_result = llm.invoke(Driving_format)
        print("DRIVING:",driving_result)

        Driving_summary = PromptTemplate(
            template=driving_summary_template,input_variables=[("ocr_txt")]
        )

        driving_summary_format = Driving_summary.format(ocr_txt = ocr_txt)

        driving_summary_result = llm.invoke(driving_summary_format)
        return {
            "Doc_type":document_type,
            "Extracted_text":driving_result.content,
            "Summarize":driving_summary_result.content
        }
    elif document_type == "BANK":
         text = "\n".join(ocr_txt)

         Bank_prompt = PromptTemplate(
            template=bank_template,
            input_variables=["ocr_txt"])
        
         Bank_format = Bank_prompt.format(ocr_txt = text)

         bank_result = llm.invoke(Bank_format)
         print("DRIVING:",bank_result)

         Bank_summary = PromptTemplate(
            template=bank_summary_tempalte,input_variables=[("ocr_txt")]
         )

         Bank_summary_format = Bank_summary.format(ocr_txt = ocr_txt)

         bank_summary_result = llm.invoke(Bank_summary_format)
         return {
            "Doc_type":document_type,
            "Extracted_text":bank_result.content,
            "Summarize":bank_summary_result.content
        }
    else:
        return {
            "Doc_type":"UNKNOWN",
            "Extracted_text":None,
            "Summarize":"Not Identified"
        }