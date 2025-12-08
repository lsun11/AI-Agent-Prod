from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..root_models import RootCompanyAnalysis, RootCompanyInfo, RootResearchState
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


class CareerBaseCompanyAnalysis(RootCompanyAnalysis):
    """
    Analysis schema for *career-related resources/platforms*.
    Extends the root analysis schema.
    """

    resource_type: Optional[str] = None

    target_roles: List[str] = Field(default_factory=list)
    seniority_focus: Optional[str] = None

    best_use_cases: List[str] = Field(default_factory=list)


class CareerBaseCompanyInfo(RootCompanyInfo):
    """
    Generic info about a career-related platform/resource.
    Extends the root company info schema.
    """

    target_roles: List[str] = Field(default_factory=list)
    seniority_focus: Optional[str] = None

    extra: Dict[str, Any] = Field(default_factory=dict)


class CareerBaseResearchState(RootResearchState):
    """
    Base state used by all career workflows.
    Extends RootResearchState with career-specific fields.
    """

    # Parsed goal
    goal: Optional[CareerGoal] = None

    # Resources / platforms found along the way
    extracted_tools: List[str] = Field(default_factory=list)
    companies: List[CareerBaseCompanyInfo] = Field(default_factory=list)

    # Final outputs
    plan: Optional[CareerActionPlan] = None
    analysis: Optional[str] = None  # JSON string or human summary
