from ..base_workflow import BaseSoftwareEngWorkflow
from .models import (
    TestingState,
    TestingResource,
    TestingRecommendation,
)
from .prompts import TestingPrompts


class TestingWorkflow(BaseSoftwareEngWorkflow):
    topic_tag = "Testing & QA"
    state_model = TestingState
    resource_model = TestingResource
    recommendation_model = TestingRecommendation
    prompts_cls = TestingPrompts
