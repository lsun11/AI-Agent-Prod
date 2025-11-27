# src/topics/api/base_models.py
from __future__ import annotations

from typing import Optional

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class APICompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model specialized for API platforms (Stripe, Twilio, etc.).
    """
    rate_limit_policies: Optional[str] = None    # brief text like "100 req/s per key"
    auth_methods: Optional[str] = None           # e.g., "API key, OAuth2, JWT"
    sdk_coverage: Optional[str] = None           # e.g., "Good (Python, JS, Go, Java)"


class APICompanyInfo(BaseCompanyInfo):
    """
    API platform info model.
    Extends BaseCompanyInfo with API-centric metadata.
    """
    docs_quality_rating: Optional[str] = None    # e.g. "Poor", "OK", "Great"
    sandbox_available: Optional[bool] = None
    webhook_support: Optional[bool] = None


class APIResearchState(BaseResearchState):
    """
    Research state for API platform comparisons.
    """
    pass
