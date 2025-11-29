from ..base_workflow import BaseSoftwareEngWorkflow
from .models import (
    CodeQualityState,
    CodeQualityResource,
    CodeQualityRecommendation,
)
from .prompts import CodeQualityPrompts


class CodeQualityWorkflow(BaseSoftwareEngWorkflow):
    topic_tag = "Code Quality & Refactoring"
    state_model = CodeQualityState
    resource_model = CodeQualityResource
    recommendation_model = CodeQualityRecommendation
    prompts_cls = CodeQualityPrompts
