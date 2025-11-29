from ..base_models import (
    BaseSoftwareEngResourceSummary,
    BaseSoftwareEngRecommendation,
    BaseSoftwareEngState,
)


class ArchitectureDesignResource(BaseSoftwareEngResourceSummary):
    architectural_patterns: list[str] = []
    system_components: list[str] = []
    tradeoffs: list[str] = []


class ArchitectureDesignRecommendation(BaseSoftwareEngRecommendation):
    key_arch_decisions: list[str] = []
    scalability_considerations: list[str] = []
    reliability_strategies: list[str] = []


class ArchitectureDesignState(BaseSoftwareEngState):
    resources: list[ArchitectureDesignResource] = []
    analysis: ArchitectureDesignRecommendation | None = None

