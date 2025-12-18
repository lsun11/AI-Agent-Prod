from ..base_models import (
    BaseSoftwareEngResourceSummary,
    BaseSoftwareEngRecommendation,
    BaseSoftwareEngState,
)


class CodeQualityResource(BaseSoftwareEngResourceSummary):
    smells: list[str] = []
    refactoring_methods: list[str] = []


class CodeQualityRecommendation(BaseSoftwareEngRecommendation):
    refactor_targets: list[str] = []
    style_guidelines: list[str] = []
    review_focus_areas: list[str] = []


class CodeQualityState(BaseSoftwareEngState):
    resources: list[CodeQualityResource] = []
    analysis: CodeQualityRecommendation | None = None

