from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class BaseSoftwareEngResourceSummary(BaseModel):
    """
    Generic summary of a software-engineering resource (article, doc, blog, RFC, etc.).

    This is used to capture useful references or patterns that can help with:
      - testing strategies
      - CI/CD pipelines
      - architecture / design
      - code quality and refactoring
      - agile / process improvements
    """

    title: str
    url: str

    key_points: List[str] = Field(default_factory=list)  # main takeaways
    concepts: List[str] = Field(default_factory=list)  # named patterns, ideas, practices
    recommended_tools: List[str] = Field(default_factory=list)  # tools mentioned

    # Optional: focus area, e.g. "Testing", "CI/CD", "Architecture", "Agile"
    focus_areas: List[str] = Field(default_factory=list)


class BaseSoftwareEngRecommendation(BaseModel):
    """
    High-level recommendation for the query within a software-engineering topic.

    This is intended to guide a working engineer/PM/DevOps in:
      - what to do
      - how to do it
      - what to watch out for
    """

    summary: str  # 2–3 sentence summary of the best approach

    best_practices: List[str] = Field(
        default_factory=list
    )  # actionable best practices / patterns
    pitfalls: List[str] = Field(
        default_factory=list
    )  # common mistakes, anti-patterns, risks
    suggested_action_plan: List[str] = Field(
        default_factory=list
    )  # 5–10 concrete steps to apply in the current project

    # Optional: recommended tools / techniques
    suggested_tools: List[str] = Field(default_factory=list)
    applicable_scenarios: List[str] = Field(default_factory=list)  # where this advice applies


class BaseSoftwareEngState(BaseModel):
    """
    Workflow state used by the base SE workflow and subtopic workflows.

    Designed for questions like:
      - "How to design CI/CD for this microservices repo?"
      - "How should we structure integration tests for a service with Kafka?"
      - "How to maintain code quality in a fast-moving monorepo?"
      - "What agile practices should we adopt for this team?"
    """

    query: str

    # extracted ideas / keywords / techniques from content
    extracted_keywords: List[str] = Field(default_factory=list)

    # useful resources (articles, docs, etc.) that were summarized
    resources: List[BaseSoftwareEngResourceSummary] = Field(default_factory=list)

    # final actionable recommendation for the current project/team
    analysis: Optional[BaseSoftwareEngRecommendation] = None
