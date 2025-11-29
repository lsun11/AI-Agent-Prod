# src/topics/career/behavioral_interview_tools/base_workflow.py

from ..base_workflow import CareerBaseWorkflow
from .models import (
    BehavioralInterviewToolAnalysis,
    BehavioralInterviewToolInfo,
    BehavioralInterviewToolResearchState,
)
from .prompts import BehavioralInterviewToolsPrompts


class BehavioralInterviewToolsWorkflow(
    CareerBaseWorkflow[
        BehavioralInterviewToolResearchState,
        BehavioralInterviewToolInfo,
        BehavioralInterviewToolAnalysis,
        BehavioralInterviewToolsPrompts,
    ]
):
    topic_tag = "Behavioral Interview & Coaching Tools"
    article_query_suffix = "behavioral interview practice tools AI mock interview career coaching comparison"
    official_site_suffix = "behavioral interview tool official site"

    state_cls = BehavioralInterviewToolResearchState
    info_cls = BehavioralInterviewToolInfo
    analysis_cls = BehavioralInterviewToolAnalysis
    prompts_cls = BehavioralInterviewToolsPrompts
