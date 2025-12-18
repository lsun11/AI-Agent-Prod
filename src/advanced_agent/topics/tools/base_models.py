from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..root_models import RootCompanyAnalysis, RootCompanyInfo, RootResearchState
from ..knowledge_extraction import KnowledgeExtractionResult


class ToolComparisonRecommendation(BaseModel):
    """
    Structured comparison + recommendation across multiple tools/services.
    Used as the final, aggregated output for the 'tools' workflow.
    """

    primary_choice: Optional[str] = None
    backup_options: List[str] = Field(default_factory=list)

    summary: str = ""

    selection_criteria: List[str] = Field(default_factory=list)
    tradeoffs: List[str] = Field(default_factory=list)

    step_by_step_decision_guide: List[str] = Field(default_factory=list)


class BaseCompanyAnalysis(RootCompanyAnalysis):
    """
    Generic structured output for LLM analysis of a product/service/platform.
    Extends the root analysis with tools-specific fields.
    """

    # Category and positioning
    category: Optional[str] = None
    primary_use_case: Optional[str] = None
    target_users: List[str] = Field(default_factory=list)

    ideal_for: List[str] = Field(default_factory=list)
    not_suited_for: List[str] = Field(default_factory=list)


class BaseCompanyInfo(RootCompanyInfo):
    """
    Generic representation of a tool/service/platform being researched.
    Extends the root company info with tools-specific fields.
    """

    # Positioning
    category: Optional[str] = None
    primary_use_case: Optional[str] = None
    target_users: List[str] = Field(default_factory=list)

    # From analysis layer
    strengths: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    ideal_for: List[str] = Field(default_factory=list)
    not_suited_for: List[str] = Field(default_factory=list)


class BaseResearchState(RootResearchState):
    """
    Shared runtime state for any 'tool / product research' workflow.
    Extends RootResearchState with tools-specific fields.
    """

    # Names extracted from search/scraped content
    extracted_tools: List[str] = Field(default_factory=list)

    # Structured info about each candidate
    companies: List[BaseCompanyInfo] = Field(default_factory=list)

    # Final overall analysis / recommendation text (for UI display)
    analysis: Optional[str] = None

    # Structured comparison + recommendation
    recommendation: Optional[ToolComparisonRecommendation] = None
