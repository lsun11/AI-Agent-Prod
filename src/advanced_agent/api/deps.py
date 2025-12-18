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
topic_classifier_llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)


def classify_topic_with_llm(query: str) -> Tuple[str, str, str]:
    """
    Returns (key, label)
    - key: internal name (e.g. 'database')
    - label: user-facing display (e.g. 'Databases & Data Platforms')
    """
    topic_list_text = "\n".join(
        f"- {cfg.label} (domain: {cfg.domain}): {cfg.description}"
        for cfg in TOPIC_CONFIGS.values()
    )

    system_prompt = (
        "You are a topic router for a research agent. You classify user queries into categories.\n\n"
        "Available research categories:\n"
        f"{topic_list_text}\n\n"
        "Important disambiguation rules:\n"
        "- If the user is asking how to design, scale, or architect a real system "
        "  (e.g. throughput, RPS, latency, consistency, queues, caching, databases, "
        "  microservices vs monolith), choose **Architecture Design Suggestions** "
        "  in the software_engineering domain.\n"
        "- Only choose **System Design Interview Platforms** if the user is asking "
        "  about interview preparation tools/resources (courses, platforms, mock interviews), "
        "  not about designing production systems.\n"
        "- Prefer software_engineering topics when the question is about coding, architecture, "
        "  testing, CI/CD, or developer practices, even if some words overlap with career topics.\n\n"
        "Examples:\n"
        "1) Query: 'How should I design a system that supports 10k rps with eventual consistency?'\n"
        "   → Category label: Architecture Design Suggestions\n\n"
        "2) Query: 'What are the best resources to practice system design interviews for FAANG?'\n"
        "   → Category label: System Design Interview Platforms\n\n"
        "3) Query: 'How can I reduce latency in a microservices architecture for a trading app?'\n"
        "   → Category label: Architecture Design Suggestions\n\n"
        "4) Query: 'Which websites let me do mock system design interviews with feedback?'\n"
        "   → Category label: System Design Interview Platforms\n\n"
        "Your job:\n"
        "- Read the query.\n"
        "- First, decide whether the user is mainly asking about: "
        "  (a) specific products/tools/platforms, "
        "  (b) architecture / implementation of a system, or "
        "  (c) career / interview / learning.\n"
        "- Then, within that area, choose EXACTLY one category label from the list.\n"
        "- Many queries include words like 'tradeoff', 'vs', 'compare', 'which should I choose'. "
        "  These are still routed by *what* they are about:\n"
        "  - If it’s about how to design or scale a system, route to an architecture/engineering topic.\n"
        "  - If it’s about APIs / DBs / clouds, route to the corresponding tools topic.\n"
        "  - If it’s about interview prep platforms or mock interviews, route to the career topics.\n"
        "- Return ONLY the category label, nothing else.\n"
        "If ambiguous, choose the closest match based on the underlying subject, "
        "not the surface words (e.g. 'system design' in a question that is actually about real system architecture)."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User query: {query}"),
    ]

    try:
        response = topic_classifier_llm.invoke(messages)
        label = response.content.strip()

        # --- Safety net: fix common misroute for architecture vs interview prep ---
        normalized_query = query.lower()
        normalized_label = label.lower()

        looks_like_real_arch_question = any(
            kw in normalized_query
            for kw in [
                "rps", "requests per second", "throughput", "latency",
                "eventual consistency", "strong consistency",
                "microservice", "micro-services", "event-driven",
                "message queue", "kafka", "rabbitmq",
                "load balancer", "sharding", "replication",
            ]
        )
        looks_like_interview_prep = any(
            kw in normalized_query
            for kw in [
                "interview", "interviews", "mock interview", "mock system design",
                "prep", "preparation", "practice platform", "practice site",
                "course", "bootcamp", "coaching",
            ]
        )

        if (
            normalized_label == "system design interview platforms"
            and looks_like_real_arch_question
            and not looks_like_interview_prep
        ):
            # Force route to architecture design if semantics clearly match
            arch_cfg = TOPIC_CONFIGS["architecture_design"]
            return "architecture_design", arch_cfg.label, arch_cfg.domain

        # Find which config matches this label
        for key, cfg in TOPIC_CONFIGS.items():
            if cfg.label.lower() == label.lower():
                return key, cfg.label, cfg.domain

        # fallback — shouldn't happen
        default_key = next(iter(TOPIC_CONFIGS.keys()))
        default_cfg = TOPIC_CONFIGS[default_key]
        return default_key, default_cfg.label, default_cfg.domain

    except Exception as e:
        print("Topic classification error:", e)
        default_key = next(iter(TOPIC_CONFIGS.keys()))
        default_cfg = TOPIC_CONFIGS[default_key]
        return default_key, default_cfg.label, default_cfg.domain