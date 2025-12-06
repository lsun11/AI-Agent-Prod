# src/diagrams/flowchart_from_plan.py
from __future__ import annotations

from typing import Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI  # or whatever you're already using

from .flowchart_models import FlowchartSpec
from ..topics.software_engineering import BaseSoftwareEngRecommendation  # or whatever topic you prefer


FLOWCHART_SYSTEM_PROMPT = """
You are an assistant that converts step-by-step action plans into simple flowcharts.

Rules:
- Create 1 start node and 1 end node.
- Use short labels (max ~8 words).
- If the plan is mostly linear, make a straight flow: start -> step1 -> step2 -> ... -> end.
- If there are obvious branches (e.g. 'if X, do Y'), you may use 'decision' nodes.
"""


def build_flowchart_from_se_recommendation(
    llm: ChatOpenAI,
    recommendation: BaseSoftwareEngRecommendation,
) -> Optional[FlowchartSpec]:
    """
    Given a SoftwareEng recommendation (with suggested_action_plan),
    ask the LLM to produce a FlowchartSpec.
    """
    # Fallback: if no steps, don't bother
    if not recommendation.suggested_action_plan:
        return None

    structured_llm = llm.with_structured_output(FlowchartSpec)

    steps_text = "\n".join(
        f"- {step}" for step in recommendation.suggested_action_plan
    )

    user_prompt = (
        "Here is an action plan:\n"
        f"{steps_text}\n\n"
        "Create a flowchart with nodes and edges that represent this plan. "
        "Keep it fairly small and readable for a PDF slide."
    )

    messages = [
        SystemMessage(content=FLOWCHART_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    try:
        spec: FlowchartSpec = structured_llm.invoke(messages)
        # Basic sanity check
        if not spec.nodes or not spec.edges:
            return None
        return spec
    except Exception as e:
        print("Error generating FlowchartSpec:", e)
        return None
