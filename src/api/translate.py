# --- Translation helpers ---
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import json

# use the cheapest model for small jobs like this
translator_llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)

def is_chinese(text: str) -> bool:
    """Heuristic: check if there's at least one CJK character."""
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)

def translate_text(text: str, target_lang: str) -> str:
    """
    Translate arbitrary text into target_lang ("English", "Chinese", etc.)
    """
    text = text.strip()
    if not text:
        return text

    system = (
        f"You are a precise translator. "
        f"Translate the user's text into {target_lang}. "
        f"Preserve technical terms, emojis and formatting. "
        f"Do NOT add explanations or commentary."
    )
    messages = [
        SystemMessage(content=system),
        HumanMessage(content=text),
    ]
    resp = translator_llm.invoke(messages)
    return resp.content.strip()
