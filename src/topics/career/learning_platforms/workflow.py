# src/topics/career/learning_platforms/base_workflow.py

from ..base_workflow import CareerBaseWorkflow
from .models import (
    LearningPlatformAnalysis,
    LearningPlatformInfo,
    LearningPlatformResearchState,
)
from .prompts import LearningPlatformsPrompts


class LearningPlatformsWorkflow(
    CareerBaseWorkflow[
        LearningPlatformResearchState,
        LearningPlatformInfo,
        LearningPlatformAnalysis,
        LearningPlatformsPrompts,
    ]
):
    topic_tag = "Learning Platforms & Skill Roadmaps"
    article_query_suffix = "learning platforms online courses bootcamps skill roadmaps comparison"
    official_site_suffix = "learning platform official site"

    state_cls = LearningPlatformResearchState
    info_cls = LearningPlatformInfo
    analysis_cls = LearningPlatformAnalysis
    prompts_cls = LearningPlatformsPrompts
