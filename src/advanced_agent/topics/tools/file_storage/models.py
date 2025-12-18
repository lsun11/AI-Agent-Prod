from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class FileStorageCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model for file sync / backup / cloud storage tools.
    """

    # Names or descriptions of storage tiers (e.g. “Free 5 GB”, “2 TB plan”)
    storage_limit_tiers: List[str] = Field(default_factory=list)

    # Sync features (e.g. “block-level sync”, “LAN sync”)
    sync_features: List[str] = Field(default_factory=list)

    # How sharing / permissions are handled
    sharing_permissions_model: Optional[str] = None


class FileStorageCompanyInfo(BaseCompanyInfo):
    """
    Info model for cloud file storage / sync services.
    """

    # Whether zero-knowledge or end-to-end encryption is mentioned
    zero_knowledge_encryption: Optional[bool] = None

    # Maximum file size (if mentioned)
    max_file_size: Optional[str] = None

    # Offline access capabilities
    offline_access_support: Optional[bool] = None


class FileStorageResearchState(BaseResearchState):
    """
    Research state for file storage / sync / backup tools.
    """
    pass
