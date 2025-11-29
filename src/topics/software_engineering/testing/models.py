from ..base_models import (
    BaseSoftwareEngResourceSummary,
    BaseSoftwareEngRecommendation,
    BaseSoftwareEngState,
)


class TestingResource(BaseSoftwareEngResourceSummary):
    testing_methods: list[str] = []
    tools_mentioned: list[str] = []
    flakiness_causes: list[str] = []


class TestingRecommendation(BaseSoftwareEngRecommendation):
    test_strategy_outline: list[str] = []
    coverage_goals: list[str] = []
    automation_suggestions: list[str] = []


class TestingState(BaseSoftwareEngState):
    resources: list[TestingResource] = []
    analysis: TestingRecommendation | None = None

