from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class ECommerceCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model for e_commerce platforms and tooling.
    """

    # Types of stores (e.g. “DTC”, “marketplace”, “digital goods”)
    store_types_supported: List[str] = Field(default_factory=list)

    # Built-in payment providers (e.g. “Stripe”, “PayPal”, “Shopify Payments”)
    payment_providers_supported: List[str] = Field(default_factory=list)

    # Marketplace / channel integrations (e.g. “Amazon”, “eBay”, “Instagram Shopping”)
    marketplace_integrations: List[str] = Field(default_factory=list)


class ECommerceCompanyInfo(BaseCompanyInfo):
    """
    Info model for e_commerce platforms.
    """

    # Any mention of transaction fees (e.g. “2.9% + 30¢ per transaction”)
    transaction_fees: Optional[str] = None

    # Support for multiple currencies / locales
    multi_currency_support: Optional[bool] = None

    # Short note about inventory / catalog tools
    inventory_management_features: Optional[str] = None


class ECommerceResearchState(BaseResearchState):
    """
    Research state for e_commerce tools.
    """
    pass
