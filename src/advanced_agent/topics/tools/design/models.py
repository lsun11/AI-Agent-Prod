from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class DesignCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model for design tools (UI/UX, graphics, prototyping).
    """

    # Types of design supported (e.g. “UI/UX”, “vector graphics”, “photo editing”)
    design_categories_supported: List[str] = Field(default_factory=list)

    # Collaboration capabilities (e.g. “live multi-user”, “commenting”, “handoff”)
    collaboration_features: List[str] = Field(default_factory=list)

    # Prototyping / interaction design features
    prototyping_capabilities: List[str] = Field(default_factory=list)


class DesignCompanyInfo(BaseCompanyInfo):
    """
    Info model for design tools.
    """

    # Supported OS / platforms (e.g. “Web”, “macOS”, “Windows”)
    platform_support: List[str] = Field(default_factory=list)

    # Whether there is a browser-based version
    has_browser_version: Optional[bool] = None


class DesignResearchState(BaseResearchState):
    """
    Research state for design tools.
    """
    pass
