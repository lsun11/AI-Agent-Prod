from __future__ import annotations

from typing import List, Optional, Dict
from pydantic import BaseModel, Field

from ..root_models import RootResearchState
from ..knowledge_extraction import KnowledgeExtractionResult


class BaseSoftwareEngResourceSummary(BaseModel):
    """
    Generic summary of a software-engineering resource (article, doc, blog, RFC, etc.).
    """

    title: str
    url: str

    key_points: List[str] = Field(default_factory=list)
    concepts: List[str] = Field(default_factory=list)
    recommended_tools: List[str] = Field(default_factory=list)

    focus_areas: List[str] = Field(default_factory=list)
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    brand_colors: Optional[Dict[str, str]] = None


class BaseSoftwareEngRecommendation(BaseModel):
    """
    High-level recommendation for the query within a software-engineering topic.
    """

    summary: str

    best_practices: List[str] = Field(default_factory=list)
    pitfalls: List[str] = Field(default_factory=list)
    suggested_action_plan: List[str] = Field(default_factory=list)

    suggested_tools: List[str] = Field(default_factory=list)
    applicable_scenarios: List[str] = Field(default_factory=list)


class BaseSoftwareEngState(RootResearchState):
    """
    Workflow state used by the base SE workflow and subtopic workflows.
    Extends RootResearchState with SE-specific fields.
    """

    # extracted ideas / keywords / techniques from content
    extracted_keywords: List[str] = Field(default_factory=list)

    # useful resources (articles, docs, etc.) that were summarized
    resources: List[BaseSoftwareEngResourceSummary] = Field(default_factory=list)

    # structured knowledge is already inherited as `knowledge`

    # final actionable recommendation
    analysis: Optional[BaseSoftwareEngRecommendation] = None

    # optional: final markdown report
    final_markdown: Optional[str] = None