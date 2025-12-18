# src/saving/highlight.py
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

renderer_llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)


def ai_highlight(text: str) -> str:
    prompt = f"""
You are a formatter. Given the following text:

{text}

Task:
- Do NOT change the wording, punctuation, or sentence order.
- Do NOT add or remove content.
- Wrap the title (e.g "Recommendations") with **double asterisks**.
- Wrap important tools, frameworks, apps, software, and key concepts with **double asterisks**.
- Use Markdown bold: **like this**.
- Return ONLY the modified text.
"""
    response = renderer_llm.invoke(prompt)
    candidate = response.content.strip()

    def strip_bold(s: str) -> str:
        return s.replace("**", "")

    base_original = strip_bold(text)
    base_candidate = strip_bold(candidate)

    if base_original != base_candidate:
        print("ai_highlight: content mismatch, falling back to original")
        return text

    return candidate
