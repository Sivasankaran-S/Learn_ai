import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from Services.web_search import is_action_question, search_web


llm = ChatOllama(model="gemma3:1b")

# ── Prompt for normal document Q&A ──
chat_prompt = """You are a helpful assistant. Answer the user's question using the document information below.

--- DOCUMENT INFO ---
Type: {document_type}

Data:
{extracted_data}

Summary:
{summary}

--- PREVIOUS CONVERSATION ---
{chat_history}

--- QUESTION ---
{question}

Answer the question using the document info above. Keep it short (max 5 lines). If the question is NOT about this document, say "I can only help with document-related questions."
"""

chat_template = PromptTemplate(
    template=chat_prompt,
    input_variables=["extracted_data", "summary", "chat_history", "question", "document_type"]
)

# ── Prompt for action questions (uses web search results) ──
search_prompt = """You are a helpful assistant. The user asked how to do something with their {document_type} document. Use the web search results below to answer.

--- WEB SEARCH RESULTS ---
{search_results}

--- PREVIOUS CONVERSATION ---
{chat_history}

--- QUESTION ---
{question}

Give a clear answer in 3-4 lines maximum. Use plain text only, no markdown, no bullet points, no bold text. Write simple sentences.
"""

search_template = PromptTemplate(
    template=search_prompt,
    input_variables=["search_results", "chat_history", "question", "document_type"]
)


def _format_extracted_data(data):
    """Convert extracted data dict into a readable string for the LLM."""
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    return str(data)


def _format_summary(summary):
    """Convert summary (list or string) into a readable string."""
    if isinstance(summary, list):
        return "\n".join(f"- {item}" for item in summary)
    return str(summary)


def _format_chat_history(chat_history):
    """Format chat history list into readable text."""
    recent = chat_history[-5:] if len(chat_history) > 5 else chat_history
    if not recent:
        return "None yet."
    formatted = ""
    for turn in recent:
        formatted += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"
    return formatted.strip()


def response_from_ai(ocr_txt, chat_history, question):
    formatted_history = _format_chat_history(chat_history)

    # ── ACTION QUESTION → Web Search + LLM Refine ──
    if is_action_question(question):
        doc_type = ocr_txt["Doc_type"]
        search_query = f"{question} {doc_type} India"
        search_results = search_web(search_query)

        formatted_prompt = search_template.format(
            search_results=search_results,
            chat_history=formatted_history,
            question=question,
            document_type=doc_type
        )

        result = llm.invoke(formatted_prompt)
        return result.content.strip()

    # ── NORMAL DOCUMENT QUESTION → Existing flow ──
    readable_data = _format_extracted_data(ocr_txt["Extracted_text"])
    readable_summary = _format_summary(ocr_txt["Summarize"])

    formatted_prompt = chat_template.format(
        extracted_data=readable_data,
        summary=readable_summary,
        document_type=ocr_txt["Doc_type"],
        chat_history=formatted_history,
        question=question
    )

    result = llm.invoke(formatted_prompt)
    return result.content.strip()