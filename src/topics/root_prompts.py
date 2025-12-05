# src/topics/root_prompts.py
from __future__ import annotations

from abc import ABC


class BaseRootPrompts(ABC):
    """
    Root prompt base class shared by all topics.

    Currently only provides:
      - KNOWLEDGE_EXTRACTION_SYSTEM
      - knowledge_extraction_user()

    This keeps knowledge-extraction logic consistent across topics
    (developer tools, software engineering, cloud/infra, etc.).
    """

    KNOWLEDGE_EXTRACTION_SYSTEM: str = (
        "You are an AI research assistant helping build a structured knowledge base "
        "from technical resources such as documentation, blog posts, articles, RFCs, "
        "and product pages.\n"
        "Your goal is to extract:\n"
        "- entities (companies, products, tools, APIs, services, concepts)\n"
        "- relationships (offers, integrates_with, competes_with, depends_on, uses, etc.)\n"
        "- pros and cons (per entity/aspect)\n"
        "- risks (technical, integration, security, compliance, maintainability, "
        "business, reliability)\n"
        "- timeline events (releases, major updates, roadmap items, funding, deprecations).\n"
        "Be concise and deduplicate similar entries. Use neutral, factual language."
    )

    @staticmethod
    def knowledge_extraction_user(aggregated_markdown: str) -> str:
        """
        Build the user message for knowledge extraction.

        This is intentionally topic-agnostic so all domains (dev tools, SE, cloud, etc.)
        can reuse it without modification.
        """
        return (
            "You are given aggregated research notes in markdown format. "
            "These notes may include multiple tools, services, companies, products, and "
            "technical concepts.\n\n"
            "Your job is to extract structured knowledge that can be stored in a knowledge "
            "graph or JSON schema. Focus on:\n"
            "1) Entities: important companies, tools, products, APIs, services, and concepts.\n"
            "2) Relationships: how these entities relate (offers, uses, integrates_with, "
            "   depends_on, competes_with, replaces, etc.).\n"
            "3) Pros: advantages, strengths, or benefits, tied to entities/aspects when possible.\n"
            "4) Cons: limitations, trade-offs, or weaknesses, tied to entities/aspects when possible.\n"
            "5) Risks: technical, integration, security, compliance, maintainability, business, "
            "   or reliability risks.\n"
            "6) Timeline: important events with best-guess dates (releases, major updates, "
            "   roadmap items, funding, deprecations).\n\n"
            "Source content:\n"
            "----------------\n"
            f"{aggregated_markdown[:8000]}\n"
            "----------------\n"
            "Be concise and deduplicate similar or overlapping items."
        )
