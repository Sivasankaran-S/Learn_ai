from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate


llm = ChatOllama(model="gemma3:1b")

chat_prompt = """
You are a document-based assistant.

Answer ONLY using the docment summary,document type,extracted document data.

PLEASE check also before answer the question is relevant to the chat history.

If the question cannot be relevant from the summary,document type,extracted document data,chat history reply EXACTLY:
"I'm assist only document related question."

RULES:
- Max 5 lines
- Simple points
- No assumptions

DOCUMENT TYPE:
{document_type}

EXTRACTED DOCUMENT DATA (JSON):
{extracted_data}

DOCUMENT SUMMARY:
{summary}

CHAT HISTORY:
{chat_history}

USER QUESTION:
{question}

ANSWER:
"""

chat_template = PromptTemplate(
    template=chat_prompt,
    input_variables=["extracted_data","summary","chat_history","question","document_type"]
)

        
def response_from_ai(ocr_txt,chat_history,question):


    formatted_prompt = chat_template.format(
        extracted_data = ocr_txt["Extracted_text"],
        summary = ocr_txt["Summarize"],
        document_type = ocr_txt["Doc_type"],
        chat_history = chat_history,
        question = question
    )


    result = llm.invoke(formatted_prompt)

    return result.content.strip()