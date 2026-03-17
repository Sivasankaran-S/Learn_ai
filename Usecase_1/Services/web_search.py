"""
Web Search Service — DuckDuckGo integration for action questions.

When the user asks about how to add/change/update/delete something
in a document, this module searches DuckDuckGo for real answers.
"""

from duckduckgo_search import DDGS

# Keywords that indicate the user wants to perform an action on the document
ACTION_KEYWORDS = [
    "how to", "change", "update", "modify", "correct",
    "add", "delete", "remove", "edit", "apply",
    "renew", "replace", "register", "link", "unlink"
]


def is_action_question(question: str) -> bool:
    """
    Check if the user's question is about performing an action
    (add/change/update/delete etc.) on the document.
    """
    q_lower = question.lower()
    return any(keyword in q_lower for keyword in ACTION_KEYWORDS)


def search_web(query: str, max_results: int = 3) -> str:
    """
    Search DuckDuckGo and return formatted results as plain text.
    Returns the top snippets combined into a single string.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "No search results found."

        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            formatted.append(f"{i}. {title}: {body}")

        return "\n".join(formatted)

    except Exception as e:
        return f"Search failed: {str(e)}"
