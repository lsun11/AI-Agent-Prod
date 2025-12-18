from ..base_workflow import BaseSoftwareEngWorkflow
from .models import (
    ArchitectureDesignState,
    ArchitectureDesignResource,
    ArchitectureDesignRecommendation,
)
from .prompts import ArchitectureDesignPrompts


class ArchitectureDesignWorkflow(BaseSoftwareEngWorkflow):
    topic_tag = "Architecture & System Design"
    state_model = ArchitectureDesignState
    resource_model = ArchitectureDesignResource
    recommendation_model = ArchitectureDesignRecommendation
    prompts_cls = ArchitectureDesignPrompts
