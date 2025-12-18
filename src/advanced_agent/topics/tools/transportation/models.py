from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class TransportationCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model for transportation / mobility apps:
    - ride-share
    - scooters / bikes
    - food delivery (if transportation-focused)
    """

    # Types of services (e.g. “ride-share”, “scooter rentals”, “carpooling”)
    service_types: List[str] = Field(default_factory=list)

    # Coverage notes (e.g. “major US cities”, “global”, “Europe only”)
    city_coverage: Optional[str] = None

    # Pricing model (e.g. “distance-based”, “time-based”, “flat zones”)
    pricing_model_transport: Optional[str] = None


class TransportationCompanyInfo(BaseCompanyInfo):
    """
    Info model for transportation / ride-share apps.
    """

    # From analysis
    service_types: List[str] = Field(default_factory=list)
    city_coverage: Optional[str] = None
    pricing_model_transport: Optional[str] = None

    # Extra, info-only fields
    surge_pricing_policy: Optional[str] = None
    safety_features: List[str] = Field(default_factory=list)
    driver_model: Optional[str] = None



class TransportationResearchState(BaseResearchState):
    """
    Research state for transportation / mobility apps.
    """
    pass
