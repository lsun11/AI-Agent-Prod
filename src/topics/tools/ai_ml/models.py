# src/topics/ai_ml/base_models.py
from __future__ import annotations

from typing import List, Optional
from pydantic import Field

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class AICompanyAnalysis(BaseCompanyAnalysis):
    """
    Analysis model specialized for AI/ML platforms:
    - LLM providers
    - model hosting
    - vector DBs
    - training/inference platforms
    """

    # What kinds of models / tasks this platform supports
    model_types_supported: List[str] = Field(
        default_factory=list
    )  # e.g. ["LLM", "vision", "embedding"]

    # Does it support fine-tuning or custom training?
    fine_tuning_support: Optional[bool] = None

    # Hosting/running options (e.g., "SaaS only", "Self-hosted", "Hybrid")
    deployment_options: List[str] = Field(default_factory=list)

    # Hardware / performance-related notes (e.g., "A100 GPUs", "CPU-only", "GPU/TPU")
    hardware_profile: Optional[str] = None

    # Any notable compliance / privacy features (e.g., "HIPAA", "SOC2", "EU data residency")
    compliance_features: List[str] = Field(default_factory=list)


class AICompanyInfo(BaseCompanyInfo):
    """
    AI/ML platform info model.
    Extends BaseCompanyInfo with AI-specific flags.
    """

    # Whether the provider offers hosted models only, or can deploy into customer VPC/on-prem
    on_prem_or_vpc_deployments: Optional[bool] = None

    # Whether model weights or checkpoints are available to download
    open_weights_available: Optional[bool] = None

    # Typical use cases (e.g., "chatbots", "search", "RAG", "classification")
    primary_use_cases: List[str] = Field(default_factory=list)


class AIResearchState(BaseResearchState):
    """
    Research state for AI/ML platform comparisons.
    Uses the same base structure as other topics.
    """
    pass
