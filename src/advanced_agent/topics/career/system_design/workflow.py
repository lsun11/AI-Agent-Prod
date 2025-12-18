# src/topics/career/system_design_platforms/base_workflow.py

from ..base_workflow import CareerBaseWorkflow
from .models import (
    SystemDesignPlatformAnalysis,
    SystemDesignPlatformInfo,
    SystemDesignPlatformResearchState,
)
from .prompts import SystemDesignPlatformsPrompts


class SystemDesignPlatformsWorkflow(
    CareerBaseWorkflow[
        SystemDesignPlatformResearchState,
        SystemDesignPlatformInfo,
        SystemDesignPlatformAnalysis,
    ]
):
    topic_tag = "System Design Interview Platforms"
    article_query_suffix = "system design interview preparation platforms courses case study comparison"
    official_site_suffix = "system design interview platform official site"

    state_cls = SystemDesignPlatformResearchState
    info_cls = SystemDesignPlatformInfo
    analysis_cls = SystemDesignPlatformAnalysis
    prompts_cls = SystemDesignPlatformsPrompts
