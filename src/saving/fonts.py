from pathlib import Path
import re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# src/saving/fonts.py

# BASE_DIR points to src/
BASE_DIR = Path(__file__).resolve().parent

# ---- CJK + Noto fonts ----
FONTS_DIR_KAI = BASE_DIR / "fonts" / "KaiShu"
CJK_FONT_PATH_KAI = FONTS_DIR_KAI / "KaiShu.ttf"
CJK_FONT_NAME_KAI = "KaiShu"

FONTS_DIR_SONG = BASE_DIR / "fonts" / "SongTi"
CJK_FONT_PATH_SONG = FONTS_DIR_SONG / "songti.ttf"
CJK_FONT_NAME_SONG = "SongTi"

CJK_FONT_PATH_SONG_2 = FONTS_DIR_SONG / "songti2.ttf"
CJK_FONT_NAME_SONG_2 = "SongTi2"

FONTS_DIR_NOTO = BASE_DIR / "fonts" / "Noto"
NOTO_FONT_PATH_SERIF = FONTS_DIR_NOTO / "noto_serif.ttf"
NOTO_FONT_NAME_SERIF = "NotoSerif"

PRIMARY_CJK_FONT_NAME = CJK_FONT_NAME_KAI

# ---- Emoji font ----
EMOJI_FONT_PATH = BASE_DIR / "fonts" / "Emoji" / "NotoEmoji-Regular.ttf"
EMOJI_FONT_NAME_EMOJI = "OpenEmojiBlack"

# All CJK / Noto fonts we want to register
CJK_FONTS = [
    (CJK_FONT_NAME_KAI, CJK_FONT_PATH_KAI),
    (CJK_FONT_NAME_SONG, CJK_FONT_PATH_SONG),
    (CJK_FONT_NAME_SONG_2, CJK_FONT_PATH_SONG_2),
    (NOTO_FONT_NAME_SERIF, NOTO_FONT_PATH_SERIF),
]


def register_cjk_fonts() -> None:
    """Register all configured CJK-capable fonts (idempotent)."""
    for font_name, font_path in CJK_FONTS:
        if not font_path.exists():
            print(f"[WARN] CJK font file not found at {font_path} (font '{font_name}').")
            continue

        try:
            pdfmetrics.getFont(font_name)
            continue  # already registered
        except KeyError:
            pass

        try:
            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
            print(f"[INFO] Registered CJK font '{font_name}' from {font_path}")
        except Exception as e:
            print(f"[ERROR] Failed to register CJK font '{font_name}' from {font_path}: {e}")


def register_emoji_font() -> None:
    """Register the emoji font (idempotent)."""
    if EMOJI_FONT_NAME_EMOJI in pdfmetrics.getRegisteredFontNames():
        return
    try:
        pdfmetrics.registerFont(TTFont(EMOJI_FONT_NAME_EMOJI, str(EMOJI_FONT_PATH)))
        print(f"[INFO] Registered emoji font '{EMOJI_FONT_NAME_EMOJI}' from {EMOJI_FONT_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to register emoji font from {EMOJI_FONT_PATH}: {e}")


def contains_cjk(text: str) -> bool:
    """Return True if the text contains any CJK characters."""
    if not text:
        return False
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text))
