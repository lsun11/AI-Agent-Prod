# src/topics/career/base_models.py

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ..knowledge_extraction import KnowledgeExtractionResult


class CareerGoal(BaseModel):
    """
    Normalized representation of the user's career goal.
    """
    raw_query: str
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    target_location: Optional[str] = None
    seniority: Optional[str] = None
    timeframe: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)


class CareerActionStep(BaseModel):
    """
    One concrete, actionable step in a career plan.
    """
    title: str
    description: str
    category: str
    estimated_time: Optional[str] = None
    resources: List[str] = Field(default_factory=list)
    concrete_outcome: Optional[str] = None


class CareerActionPlan(BaseModel):
    """
    Detailed, step-by-step plan to achieve the user's goal.
    """
    goal_summary: str
    main_theme: str
    steps: List[CareerActionStep] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)


class CareerBaseCompanyAnalysis(BaseModel):
    """
    Analysis schema for *career-related resources/platforms*.
    """
    pricing_model: str = "Unknown"
    pricing_details: Optional[str] = None
    is_open_source: Optional[bool] = None

    resource_type: Optional[str] = None
    description: str = ""

    tech_stack: List[str] = Field(default_factory=list)
    api_available: Optional[bool] = None
    language_support: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)

    target_roles: List[str] = Field(default_factory=list)
    seniority_focus: Optional[str] = None

    strengths: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    best_use_cases: List[str] = Field(default_factory=list)


class CareerBaseCompanyInfo(BaseModel):
    """
    Generic info about a career-related platform/resource.
    """
    name: str
    description: str
    website: str

    pricing_model: Optional[str] = None
    pricing_details: Optional[str] = None
    is_open_source: Optional[bool] = None

    tech_stack: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)

    api_available: Optional[bool] = None
    language_support: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)

    target_roles: List[str] = Field(default_factory=list)
    seniority_focus: Optional[str] = None

    extra: Dict[str, Any] = Field(default_factory=dict)

    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    brand_colors: Optional[Dict[str, str]] = None


class CareerBaseResearchState(BaseModel):
    """
    Base state used by all career workflows.

    Pipeline supports:
      - collecting articles
      - extracting career-related tools/resources
      - analyzing them
      - building a detailed, step-by-step action plan
      - optional knowledge graph extraction
    """

    query: str

    # Parsed goal
    goal: Optional[CareerGoal] = None

    # Raw aggregated markdown from article search
    aggregated_markdown: Optional[str] = None

    # Simple list of sources {title, url}
    sources: List[Dict[str, str]] = Field(default_factory=list)

    # Resources / platforms found along the way
    extracted_tools: List[str] = Field(default_factory=list)
    companies: List[CareerBaseCompanyInfo] = Field(default_factory=list)
    search_results: List[Dict[str, Any]] = Field(default_factory=list)

    # Final outputs
    plan: Optional[CareerActionPlan] = None
    analysis: Optional[str] = None  # can be JSON string or human summary
    knowledge: Optional[KnowledgeExtractionResult] = None
