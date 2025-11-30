# src/topics/career/base_models.py

from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CareerGoal(BaseModel):
    """
    Normalized representation of the user's career goal.

    This can be:
      - prepare for interviews at company X
      - switch from role A to role B
      - get promoted to senior/staff
      - break into a new domain (e.g. ML, infra)
    """

    raw_query: str  # original user query in free text

    target_role: Optional[str] = None  # e.g. "Senior Backend Engineer"
    target_company: Optional[str] = None  # e.g. "NVIDIA"
    target_location: Optional[str] = None  # optional location preference

    seniority: Optional[str] = None  # e.g. "Entry-level", "Mid-level", "Senior"
    timeframe: Optional[str] = None  # e.g. "3 months", "6–12 months"

    constraints: List[str] = Field(
        default_factory=list
    )  # e.g. "full-time job now", "limited weekends", etc.


class CareerActionStep(BaseModel):
    """
    One concrete, actionable step in a career plan.
    Intended to be 'followable' by the user.
    """

    title: str  # e.g. "Build a 4-week LeetCode routine"
    description: str  # 2–4 sentence explanation of what to do

    category: str  # e.g. "Coding Interview Prep", "System Design", "Networking"
    estimated_time: Optional[str] = None  # e.g. "5–7 hours/week", "Weekend project"

    resources: List[str] = Field(
        default_factory=list
    )  # names/URLs of tools/platforms/courses/etc.

    concrete_outcome: Optional[str] = None  # e.g. "Be comfortable with medium-level problems"


class CareerActionPlan(BaseModel):
    """
    Detailed, step-by-step plan to achieve the user's goal.
    This is the main output of the career workflow.
    """

    goal_summary: str  # 1–2 sentences summarizing the interpreted goal
    main_theme: str  # e.g. "Prepare for E5 backend interview at Meta"

    steps: List[CareerActionStep] = Field(default_factory=list)

    risks: List[str] = Field(
        default_factory=list
    )  # pitfalls, common mistakes for this goal
    success_metrics: List[str] = Field(
        default_factory=list
    )  # how the user knows they are on track (e.g. "solve 80+ LeetCode mediums")


class CareerBaseCompanyAnalysis(BaseModel):
    """
    Analysis schema for *career-related resources/platforms*.

    This is kept structurally compatible with CS-style analysis, but the
    semantics are career-focused: interview prep platforms, resume tools,
    company career pages, learning platforms, etc.
    """

    pricing_model: str = "Unknown"
    pricing_details: Optional[str] = None

    is_open_source: Optional[bool] = None

    # Resource perspective
    resource_type: Optional[str] = None  # e.g. "Interview platform", "Course", "Company career site"
    description: str = ""

    tech_stack: List[str] = Field(
        default_factory=list
    )  # e.g. "Web", "Mobile app", "Chrome extension"
    api_available: Optional[bool] = None
    language_support: List[str] = Field(default_factory=list)
    integration_capabilities: List[str] = Field(default_factory=list)

    # Career-specific
    target_roles: List[str] = Field(default_factory=list)  # "Software Engineer", etc.
    seniority_focus: Optional[str] = None  # "Entry-level", "All levels", etc.

    strengths: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    best_use_cases: List[str] = Field(default_factory=list)


class CareerBaseCompanyInfo(BaseModel):
    """
    Generic info about a career-related platform/resource.

    Examples:
      - LeetCode, HackerRank, Interviewing.io
      - Resume review tools
      - Company's official career page
      - Online degree / bootcamp sites
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
    primary_color: Optional[str] = None       # e.g. "#0B5FFF"
    brand_colors: Optional[Dict[str, str]] = None  # full color map if you want

class CareerBaseResearchState(BaseModel):
    """
    Base state used by all career workflows.

    This now supports:
      - extracting career-related tools/resources
      - analyzing them
      - building a detailed, step-by-step action plan
    """

    query: str

    # Parsed goal
    goal: Optional[CareerGoal] = None

    # Resources / platforms found along the way
    extracted_tools: List[str] = Field(default_factory=list)
    companies: List[CareerBaseCompanyInfo] = Field(default_factory=list)
    search_results: List[Dict[str, Any]] = Field(default_factory=list)

    # Final output
    plan: Optional[CareerActionPlan] = None
    analysis: Optional[str] = None  # free-form summary if needed

