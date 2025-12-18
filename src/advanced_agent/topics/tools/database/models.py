# src/topics/database/base_models.py
from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class DatabaseCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model specialized for databases / data platforms:
    - OLTP/OLAP DBs
    - data warehouses
    - analytical engines
    - managed DB services
    """

    # Data model (e.g., "relational", "document", "key-value", "graph", "columnar")
    data_model_types: List[str] = Field(default_factory=list)

    # Consistency model (e.g., "strong", "eventual", "tunable")
    consistency_model: Optional[str] = None

    # Scalability pattern (e.g., "vertical", "horizontal", "sharding", "distributed")
    scalability_pattern: Optional[str] = None

    # Whether it's optimized for OLTP, OLAP, or both
    workload_type: Optional[str] = None


class DatabaseCompanyInfo(BaseCompanyInfo):
    """
    Database / data platform info.
    Extends BaseCompanyInfo with data-centric metadata.
    """

    # Managed service vs self-managed only vs both
    managed_service_available: Optional[bool] = None

    # Backup / restore features summary
    backup_and_recovery_capabilities: Optional[str] = None

    # Data residency / multi-region replication note
    multi_region_replication: Optional[bool] = None


class DatabaseResearchState(BaseResearchState):
    """
    Research state for database / data platform comparisons.
    """
    pass
