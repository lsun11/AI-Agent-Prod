from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class ProductivityCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model for productivity tools (notes, task managers, all-in-one workspaces).
    """

    # High-level focus (e.g. “notes”, “tasks”, “all-in-one workspace”)
    primary_productivity_focus: Optional[str] = None

    # Collaboration style (e.g. “synchronous”, “asynchronous”, “comment-based”)
    collaboration_style: Optional[str] = None

    # Presence / quality of template libraries
    templates_library: Optional[str] = None


class ProductivityCompanyInfo(BaseCompanyInfo):
    """
    Info model for productivity tools (Notion, Todoist, etc.).
    """

    # Offline capabilities (e.g. “full offline”, “partial”, “online only”)
    offline_capabilities: Optional[str] = None

    # Automation / integration features (e.g. “Zapier”, “native automations”)
    automation_integrations: List[str] = Field(default_factory=list)


class ProductivityResearchState(BaseResearchState):
    """
    Research state for productivity tools.
    """
    pass
