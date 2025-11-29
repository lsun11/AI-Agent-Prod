from ..base_models import (
    BaseSoftwareEngResourceSummary,
    BaseSoftwareEngRecommendation,
    BaseSoftwareEngState,
)


class CICDResource(BaseSoftwareEngResourceSummary):
    pipeline_steps: list[str] = []
    infra_tools: list[str] = []
    deployment_strategies: list[str] = []


class CICDRecommendation(BaseSoftwareEngRecommendation):
    pipeline_improvements: list[str] = []
    reliability_measures: list[str] = []
    rollback_strategies: list[str] = []


class CICDState(BaseSoftwareEngState):
    resources: list[CICDResource] = []
    analysis: CICDRecommendation | None = None

