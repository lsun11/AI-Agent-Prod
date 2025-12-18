from ..base_workflow import BaseSoftwareEngWorkflow
from .models import (
    AgileState,
    AgileResource,
    AgileRecommendation,
)
from .prompts import AgilePrompts


class AgileWorkflow(BaseSoftwareEngWorkflow):
    topic_tag = "Agile, Process & Collaboration"
    state_model = AgileState
    resource_model = AgileResource
    recommendation_model = AgileRecommendation
    prompts_cls = AgilePrompts
