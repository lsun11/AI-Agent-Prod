# src/topics/cloud/base_models.py
from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class CloudCompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model specialized for cloud platforms and infrastructure:
    - compute (VMs, containers, serverless)
    - storage
    - networking
    - managed services
    """

    # Compute offerings (e.g., "VMs", "Kubernetes", "Serverless")
    compute_services: List[str] = Field(default_factory=list)

    # Storage options (e.g., "object", "block", "file")
    storage_services: List[str] = Field(default_factory=list)

    # Networking / edge offerings (e.g., "CDN", "Load Balancer", "Private Link")
    networking_features: List[str] = Field(default_factory=list)

    # Uptime SLA string, if mentioned (e.g., "99.9%", "99.99%")
    sla_uptime: Optional[str] = None

    # Compliance/certifications relevant to infra (e.g., "SOC2", "FedRAMP")
    compliance_certifications: List[str] = Field(default_factory=list)


class CloudCompanyInfo(BaseCompanyInfo):
    """
    Cloud provider / infrastructure platform info.
    Extends BaseCompanyInfo with cloud-specific dimensions.
    """

    # Whether there is a free tier / always-free usage
    free_tier_available: Optional[bool] = None

    # Regions and/or multi-region support note (can be coarse summary text)
    regions_coverage: Optional[str] = None

    # Whether the provider offers managed Kubernetes
    managed_kubernetes_available: Optional[bool] = None


class CloudResearchState(BaseResearchState):
    """
    Research state for cloud service comparisons.
    """
    pass
