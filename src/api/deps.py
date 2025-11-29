# src/api/deps.py
from typing import Tuple

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from ..topics.registry import (
    build_workflows,
    get_topic_descriptions,
    get_topic_labels,
    TOPIC_CONFIGS,
)

# Build workflows & topic metadata once at import time
TOPIC_WORKFLOWS = build_workflows()
TOPIC_LABELS = get_topic_labels()
TOPIC_DESCRIPTIONS = get_topic_descriptions()
TOPIC_KEYS = list(TOPIC_CONFIGS.keys())

# LLM used for classification (small, deterministic)
topic_classifier_llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)


def classify_topic_with_llm(query: str) -> Tuple[str, str, str]:
    """
    Returns (key, label)
    - key: internal name (e.g. 'database')
    - label: user-facing display (e.g. 'Databases & Data Platforms')
    """
    topic_list_text = "\n".join(
        f"- {cfg.label}: {cfg.description}"
        for cfg in TOPIC_CONFIGS.values()
    )

    system_prompt = (
        "You are a topic router. You classify user queries into categories.\n\n"
        "Available research categories:\n"
        f"{topic_list_text}\n\n"
        "Your job:\n"
        "- Read the query.\n"
        "- Choose EXACTLY one category.\n"
        "- Return ONLY the category *label*, nothing else.\n"
        "If ambiguous, choose the closest match."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User query: {query}"),
    ]

    try:
        response = topic_classifier_llm.invoke(messages)
        label = response.content.strip()

        # Find which config matches this label
        for key, cfg in TOPIC_CONFIGS.items():
            if cfg.label.lower() == label.lower():
                return key, cfg.label, cfg.domain

        # fallback — shouldn't happen
        default_key = next(iter(TOPIC_CONFIGS.keys()))
        return default_key, TOPIC_CONFIGS[default_key].label, TOPIC_CONFIGS[default_key].domain

    except Exception as e:
        print("Topic classification error:", e)
        default_key = next(iter(TOPIC_CONFIGS.keys()))
        return default_key, TOPIC_CONFIGS[default_key].label
