# src/topics/tools/base_models.py

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..knowledge_extraction import KnowledgeExtractionResult


class ToolComparisonRecommendation(BaseModel):
    """
    Structured comparison + recommendation across multiple tools/services.
    Used as the final, aggregated output for the 'tools' workflow.
    """

    primary_choice: Optional[str] = None  # The single best option for this query
    backup_options: List[str] = Field(default_factory=list)  # 1–3 reasonable alternatives

    summary: str = ""  # High-level comparison summary in 2–4 sentences

    selection_criteria: List[str] = Field(
        default_factory=list
    )  # e.g. "Budget sensitivity", "Team size", "Tech stack"
    tradeoffs: List[str] = Field(
        default_factory=list
    )  # e.g. "Tool A is simpler, Tool B scales better"

    step_by_step_decision_guide: List[str] = Field(
        default_factory=list
    )  # Bullet list guiding user on how to choose


class BaseCompanyAnalysis(BaseModel):
    """
    Generic structured output for LLM analysis of a product/service/platform.
    """

    # Pricing and licensing
    pricing_model: str  # Free, Freemium, Paid, Enterprise, Unknown
    pricing_details: Optional[str] = None

    is_open_source: Optional[bool] = None

    # Category and positioning
    category: Optional[str] = None
    primary_use_case: Optional[str] = None
    target_users: List[str] = Field(default_factory=list)

    # Technical aspects
    tech_stack: List[str] = Field(default_factory=list)
    description: str = ""

    api_available: Optional[bool] = None
    language_support: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)

    strengths: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    ideal_for: List[str] = Field(default_factory=list)
    not_suited_for: List[str] = Field(default_factory=list)


class BaseCompanyInfo(BaseModel):
    """
    Generic representation of a tool/service/platform being researched.
    """

    name: str
    description: str
    website: str

    # Business / licensing
    pricing_model: Optional[str] = None
    pricing_details: Optional[str] = None
    is_open_source: Optional[bool] = None

    # Positioning
    category: Optional[str] = None
    primary_use_case: Optional[str] = None
    target_users: List[str] = Field(default_factory=list)

    # Technical aspects
    tech_stack: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    api_available: Optional[bool] = None
    language_support: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)

    # From analysis layer
    strengths: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    ideal_for: List[str] = Field(default_factory=list)
    not_suited_for: List[str] = Field(default_factory=list)

    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    brand_colors: Optional[Dict[str, str]] = None


class BaseResearchState(BaseModel):
    """
    Shared runtime state for any 'tool / product research' workflow.
    """

    # Original user query
    query: str

    # Raw aggregated markdown from multi-pass article search
    aggregated_markdown: Optional[str] = None

    # Names extracted from search/scraped content
    extracted_tools: List[str] = Field(default_factory=list)

    # Structured info about each candidate
    companies: List[BaseCompanyInfo] = Field(default_factory=list)

    # Raw search results / intermediate info (optional)
    search_results: List[Dict[str, Any]] = Field(default_factory=list)

    # Final overall analysis / recommendation text (for UI display)
    analysis: Optional[str] = None

    # Structured comparison + recommendation
    recommendation: Optional[ToolComparisonRecommendation] = None

    # Debug logs, trace messages, etc.
    log_messages: List[str] = Field(default_factory=list)

    # Simple list of sources {title, url}
    sources: List[Dict[str, str]] = Field(default_factory=list)

    # Global structured knowledge (entities, relationships, pros/cons, risks, timeline)
    knowledge: Optional[KnowledgeExtractionResult] = None
