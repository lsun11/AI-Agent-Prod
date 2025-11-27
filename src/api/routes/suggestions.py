# ----- Sample question suggestions -----
from datetime import datetime
import json
import random
from typing import Optional, List
from fastapi import APIRouter, FastAPI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from ..translate import translate_text
from ..data.suggestions_pool import DEFAULT_POOL_CHN, DEFAULT_POOL_EN

router = APIRouter()

SUGGESTIONS_CACHE: List[str] | None = None


class SuggestionsResponse(BaseModel):
    suggestions: List[str]


def generate_sample_questions(n: int = 5) -> List[str]:
    """
    Use a quick LLM to generate example queries this app can answer.
    - We ask for JSON array.
    - We robustly extract the JSON portion (between [ and ]).
    - If anything fails, we fall back to a default pool.
    - We also inject a random 'seed' into the prompt so each call tends to differ.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)  # higher temp for more variety

    # 🎲 randomizer to avoid provider/model caching and encourage variety
    rand_seed = random.randint(0, 10_000)
    now_iso = datetime.now().isoformat(timespec="seconds")

    system = (
        "You generate example user questions for a research assistant that helps "
        "software developers with:\n"
        "- developer tools & IDEs comparison and recommendation\n"
        "- APIs & backend services comparison and recommendation\n"
        "- cloud & databases comparison and recommendation\n"
        "- SaaS products comparison and recommendation\n"
        "- software engineering practices\n"
        "- software devOps\n"
        "- developer careers (interviews, resumes, learning roadmaps)\n\n"
        "Write short questions, do not include questioning words. For example:"
        "`Best Python IDEs` is good. `What's the best Python IDE in 2024?` is bad."
        "Return ONLY a JSON array of strings. No explanation, no code fences."
    )

    user = (
        f"Generate {n} diverse example questions a developer might ask this assistant.\n"
        f"Randomizer token: {rand_seed} at {now_iso}.\n"
        "Return strictly JSON like:\n"
        '["question1", "question2", ...]'
    )

    resp = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]
    )

    raw = resp.content.strip()
    print(raw)
    questions: List[str] = []
    # ---- Try to extract a JSON array substring between [ and ] ----
    try:
        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end != -1 and start < end:
            json_str = raw[start: end + 1]
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                questions = [str(q).strip() for q in parsed if str(q).strip()]
    except Exception as e:
        print("Failed to parse JSON array from LLM output:", e)

    if not questions:
        # no valid LLM result → random sample from defaults
        questions = random.sample(DEFAULT_POOL_EN, k=min(n, len(DEFAULT_POOL_EN)))
    else:
        # if LLM gave more than n, trim; if fewer, keep them as-is
        questions = questions[:n]

    return questions


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(language: str = "Eng", mode: str = "slow"):
    """
    Return a small list of sample questions.

    - mode="fast": return only defaults (no LLM, instant)
    - mode="fresh": call LLM to generate new questions (slower)
    """
    if mode == "fast":
        # instant defaults
        questions = random.sample(DEFAULT_POOL_EN, k=5) if language == "Eng" else random.sample(DEFAULT_POOL_CHN, k=5)
    else:
        # LLM-generated (slower)
        questions = generate_sample_questions(5)

    translated_questions = []
    for question in questions:
        if mode == "slow" and language == "Chn":
            question = translate_text(question, "Chinese")
        translated_questions.append(question)

    return SuggestionsResponse(suggestions=translated_questions)
