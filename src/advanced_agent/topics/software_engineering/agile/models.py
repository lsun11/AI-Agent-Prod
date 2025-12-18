from ..base_models import (
    BaseSoftwareEngResourceSummary,
    BaseSoftwareEngRecommendation,
    BaseSoftwareEngState,
)


class AgileResource(BaseSoftwareEngResourceSummary):
    methodologies: list[str] = []
    ceremonies: list[str] = []
    anti_patterns: list[str] = []


class AgileRecommendation(BaseSoftwareEngRecommendation):
    process_improvements: list[str] = []
    communication_tips: list[str] = []
    team_habits: list[str] = []


class AgileState(BaseSoftwareEngState):
    resources: list[AgileResource] = []
    analysis: AgileRecommendation | None = None

