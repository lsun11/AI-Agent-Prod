from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class MessagingCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model for messaging / chat / communication tools.
    """

    # Encryption details (e.g. “end-to-end”, “transport-level only”)
    encryption_type: Optional[str] = None

    # Mentioned max group size / channel size limits
    max_group_size: Optional[str] = None

    # Business / team features (e.g. “channels”, “threads”, “admin controls”)
    business_features: List[str] = Field(default_factory=list)


class MessagingCompanyInfo(BaseCompanyInfo):
    """
    Info model for messaging apps / platforms.
    """

    # Whether a phone number is required for account creation
    phone_number_required: Optional[bool] = None

    # Multi-device / multi-platform support
    multi_device_support: Optional[bool] = None

    # Rough description of primary use (e.g. “team chat”, “consumer messaging”)
    primary_messaging_use_case: Optional[str] = None


class MessagingResearchState(BaseResearchState):
    """
    Research state for messaging tools.
    """
    pass
