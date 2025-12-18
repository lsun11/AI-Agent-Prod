# src/topics/root_models.py
from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from .knowledge_extraction import KnowledgeExtractionResult


class RootCompanyAnalysis(BaseModel):
    """
    Common subset of fields for company/resource analysis across topics.
    """

    # Pricing / licensing
    pricing_model: str = "Unknown"
    pricing_details: Optional[str] = None
    is_open_source: Optional[bool] = None

    # Technical aspects / description
    description: str = ""
    tech_stack: List[str] = Field(default_factory=list)

    api_available: Optional[bool] = None
    language_support: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)

    # Qualitative aspects
    strengths: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class RootCompanyInfo(BaseModel):
    """
    Common subset of fields for a company/tool/platform across topics.
    """

    name: str
    description: str
    website: str

    # Pricing / licensing
    pricing_model: Optional[str] = None
    pricing_details: Optional[str] = None
    is_open_source: Optional[bool] = None

    # Technical / integration
    tech_stack: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    api_available: Optional[bool] = None
    language_support: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)

    # Branding (shared with SE resource summaries)
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    brand_colors: Optional[Dict[str, str]] = None


class RootResearchState(BaseModel):
    """
    Core runtime state shared across different topic workflows.

    Each topic-specific state can subclass this and add extra fields.
    """

    # Original user query
    query: str

    # Raw aggregated markdown from article search / scraping
    aggregated_markdown: Optional[str] = None

    # Simple list of sources {title, url}
    sources: List[Dict[str, str]] = Field(default_factory=list)

    # Raw search results / intermediate info (optional)
    search_results: List[Dict[str, Any]] = Field(default_factory=list)

    # Global structured knowledge (entities, relationships, pros/cons, risks, timeline)
    knowledge: Optional[KnowledgeExtractionResult] = None

    # Debug logs, trace messages, etc.
    log_messages: List[str] = Field(default_factory=list)

    # Speed control: when True, skip heavy multi-pass + knowledge extraction.
    fast_mode: bool = False
