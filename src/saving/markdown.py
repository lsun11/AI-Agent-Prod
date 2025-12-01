# src/saving/markdown.py
import re
from html import escape
from typing import Dict
from .fonts import EMOJI_FONT_NAME_EMOJI

_URL_RE = re.compile(r"(https?://[^\s]+)")
_EMOJI_RE = re.compile(r"([\U0001F300-\U0001FAFF])")


def markdown_inline_to_html(text: str, uses_cjk: bool) -> str:
    """
    Tiny markdown → ReportLab-HTML converter:
    - **bold**
    - URLs → clickable blue <link>
    - Emojis → emoji font
    """

    # Normalize problematic emojis to simpler ones that render reliably in PDFs
    text = text.replace("🧑‍💻", "👤")
    text = text.replace("🧩", "📦")
    text = text.replace("🛠️", "🔧")
    text = text.replace("✅", "✔")

    # 1) **bold**
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    # 2) URLs → <link href="...">
    def _url_repl(match: re.Match) -> str:
        url = match.group(1)
        return f'<link href="{url}" color="blue">{url}</link>'

    text = _URL_RE.sub(_url_repl, text)

    # 3) Emojis → emoji font
    def _emoji_repl(m: re.Match) -> str:
        ch = m.group(1)
        return f'<font name="{EMOJI_FONT_NAME_EMOJI}">{ch}</font>'

    text = _EMOJI_RE.sub(_emoji_repl, text)

    # 4) Escape everything except our formatting/link tags
    placeholders: Dict[str, str] = {}

    def _keep_tag(m: re.Match) -> str:
        key = f"__TAG{len(placeholders)}__"
        placeholders[key] = m.group(0)
        return key

    # Keep <b>, </b>, <strong>, </strong>, <font ...>, </font>, <link ...>, </link>
    text = re.sub(r"</?(b|strong|font|link)(?: [^>]+)?>", _keep_tag, text)

    # Escape the rest safely (including CJK)
    text = escape(text)

    # Restore our tags
    for key, tag in placeholders.items():
        text = text.replace(key, tag)

    return text
