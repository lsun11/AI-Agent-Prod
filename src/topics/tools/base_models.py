# src/topics/tools/base_models.py

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


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

    This now covers *any* CS-related tools:
      - dev tools and SDKs
      - hosted SaaS/services
      - APIs and platforms
      - cloud infra, monitoring, CI, etc.
      - even career platforms / learning tools (from a product angle)
    """

    # Pricing and licensing
    pricing_model: str  # Free, Freemium, Paid, Enterprise, Unknown
    pricing_details: Optional[str] = None  # e.g. "from $20/month"

    is_open_source: Optional[bool] = None  # true / false / null if unclear

    # Category and positioning
    category: Optional[str] = None  # e.g. "Cloud database", "CI/CD platform"
    primary_use_case: Optional[str] = None  # short phrase, e.g. "API monitoring"
    target_users: List[str] = Field(
        default_factory=list
    )  # e.g. ["Backend engineers", "Small startups"]

    # Technical aspects
    tech_stack: List[str] = Field(
        default_factory=list
    )  # languages, frameworks, infra, etc.
    description: str = ""  # 1-sentence developer-focused description

    api_available: Optional[bool] = None  # REST/GraphQL/SDK etc.
    language_support: List[str] = Field(default_factory=list)  # programming languages
    integration_capabilities: List[str] = Field(
        default_factory=list
    )  # e.g. GitHub, VS Code, AWS, Slack

    # Recommendation-related fields
    strengths: List[str] = Field(
        default_factory=list
    )  # what this tool is especially good at
    limitations: List[str] = Field(
        default_factory=list
    )  # notable gaps / downsides
    ideal_for: List[str] = Field(
        default_factory=list
    )  # ideal scenarios, team types, workloads
    not_suited_for: List[str] = Field(
        default_factory=list
    )  # where this is probably a bad fit


class BaseCompanyInfo(BaseModel):
    """
    Generic representation of a tool/service/platform being researched.

    This is intentionally broad: dev tools, SaaS, APIs, infra, learning platforms,
    career platforms viewed as *products*, etc.
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


class BaseResearchState(BaseModel):
    """
    Shared runtime state for any 'tool / product research' workflow.

    This now supports broad CS queries and expects:
      - multiple candidate tools/services
      - structured comparison
      - final recommendation
    """

    # Original user query
    query: str

    # Names extracted from search/scraped content
    extracted_tools: List[str] = Field(default_factory=list)

    # Structured info about each candidate
    companies: List[BaseCompanyInfo] = Field(default_factory=list)

    # Raw search results / intermediate info
    search_results: List[Dict[str, Any]] = Field(default_factory=list)

    # Final overall analysis / recommendation text (for UI display)
    analysis: Optional[str] = None

    # Structured comparison + recommendation
    recommendation: Optional[ToolComparisonRecommendation] = None

    # Debug logs, trace messages, etc.
    log_messages: List[str] = Field(default_factory=list)
