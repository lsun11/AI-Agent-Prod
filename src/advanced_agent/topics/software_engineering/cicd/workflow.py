from ..base_workflow import BaseSoftwareEngWorkflow
from .models import (
    CICDState,
    CICDResource,
    CICDRecommendation,
)
from .prompts import CICDPrompts


class CICDWorkflow(BaseSoftwareEngWorkflow):
    topic_tag = "CI/CD & DevOps"
    state_model = CICDState
    resource_model = CICDResource
    recommendation_model = CICDRecommendation
    prompts_cls = CICDPrompts
