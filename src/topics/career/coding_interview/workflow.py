# src/topics/career/coding_interview_platforms/base_workflow.py

from ..base_workflow import CareerBaseWorkflow
from .models import (
    CodingInterviewPlatformAnalysis,
    CodingInterviewPlatformInfo,
    CodingInterviewPlatformResearchState,
)
from .prompts import CodingInterviewPlatformsPrompts


class CodingInterviewPlatformsWorkflow(
    CareerBaseWorkflow[
        CodingInterviewPlatformResearchState,
        CodingInterviewPlatformInfo,
        CodingInterviewPlatformAnalysis,
        CodingInterviewPlatformsPrompts,
    ]
):
    topic_tag = "Coding Interview Platforms"
    article_query_suffix = "coding interview practice platforms leetcode alternatives comparison"
    official_site_suffix = "coding interview platform official site"

    state_cls = CodingInterviewPlatformResearchState
    info_cls = CodingInterviewPlatformInfo
    analysis_cls = CodingInterviewPlatformAnalysis
    prompts_cls = CodingInterviewPlatformsPrompts
