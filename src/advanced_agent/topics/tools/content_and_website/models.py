from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class ContentAndWebsiteCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model for:
    - CMS platforms
    - blogging tools
    - website builders
    - simple hosting platforms
    """

    # Types of sites supported (e.g. “blog”, “portfolio”, “landing page”, “store”)
    site_types_supported: List[str] = Field(default_factory=list)

    # Hosting model (e.g. “fully hosted SaaS”, “self-hosted”, “hybrid”)
    hosting_model: Optional[str] = None

    # Rough note on customization (e.g. “drag-and-drop only”, “full code access”)
    customization_flexibility: Optional[str] = None


class ContentAndWebsiteCompanyInfo(BaseCompanyInfo):
    """
    Info model for content/website tools & platforms.
    """

    # True if they include a free custom domain or subdomain options
    free_domain_available: Optional[bool] = None

    # Any mention of bandwidth / traffic limits
    bandwidth_limits: Optional[str] = None

    # Whether built-in SEO tooling is emphasized
    has_built_in_seo_tools: Optional[bool] = None


class ContentAndWebsiteResearchState(BaseResearchState):
    """
    Research state for content / website platforms.
    """
    pass
