from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class ConsumerAndSocialCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model for consumer & social apps:
    - dating apps
    - social networks
    - community platforms
    """

    # Who primarily uses this product (e.g. “general consumers”, “young adults”)
    audience_type: Optional[str] = None

    # Monetization style (e.g. “ads”, “subscription”, “freemium”, “in-app purchases”)
    monetization_model: Optional[str] = None

    # Platforms where the app is available
    platforms: List[str] = Field(default_factory=list)

    # Safety / privacy / moderation features mentioned
    safety_privacy_features: List[str] = Field(default_factory=list)


class ConsumerAndSocialCompanyInfo(BaseCompanyInfo):
    """
    Info model for consumer & social apps.
    Extends BaseCompanyInfo with user + region metadata.
    """

    # Very rough textual estimate (e.g. “> 100M MAU”)
    monthly_active_users: Optional[str] = None

    # Region or country focus (e.g. “Global”, “US + Europe”)
    region_focus: Optional[str] = None

    # Age restriction notes (e.g. “18+”, “13+”)
    age_restrictions: Optional[str] = None


class ConsumerAndSocialResearchState(BaseResearchState):
    """
    Research state for consumer & social apps.
    """
    pass
