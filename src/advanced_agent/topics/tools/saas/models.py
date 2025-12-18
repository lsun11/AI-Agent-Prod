# src/topics/saas/base_models.py
from __future__ import annotations

from typing import Optional

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class SaaSCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model specialized for SaaS products.
    Reuses core pricing/tech fields from BaseCompanyAnalysis, but you can
    add SaaS-specific fields here.
    """
    # Example SaaS-specific attributes (optional; you can expand later):
    sla_guarantee: Optional[str] = None          # e.g. "99.9% uptime", "None"
    hosting_model: Optional[str] = None          # e.g. "Single-tenant", "Multi-tenant"
    onboarding_complexity: Optional[str] = None  # e.g. "Low", "Medium", "High"


class SaaSCompanyInfo(BaseCompanyInfo):
    """
    SaaS product/company information model.
    Extends BaseCompanyInfo with SaaS-specific attributes.
    """
    # e.g., whether there's a free trial, seat-based pricing, etc.
    free_trial_available: Optional[bool] = None
    billing_model: Optional[str] = None  # e.g. "Per seat", "Usage-based", "Flat fee"


class SaaSResearchState(BaseResearchState):
    """
    Research state for SaaS product comparisons.
    You can add SaaS-specific state fields here if needed.
    """
    pass