# src/topics/career/resume_tools/base_workflow.py

from ..base_workflow import CareerBaseWorkflow
from .models import (
    ResumeToolsCompanyAnalysis,
    ResumeToolsCompanyInfo,
    ResumeToolsResearchState,
)
from .prompts import ResumeToolsPrompts


class ResumeToolsWorkflow(
    CareerBaseWorkflow[
        ResumeToolsResearchState,
        ResumeToolsCompanyInfo,
        ResumeToolsCompanyAnalysis,
    ]
):
    topic_tag = "Resume Optimization & ATS Tools"
    article_query_suffix = "resume builder ATS optimization tools comparison best alternatives"
    official_site_suffix = "resume tool official site"

    state_cls = ResumeToolsResearchState
    info_cls = ResumeToolsCompanyInfo
    analysis_cls = ResumeToolsCompanyAnalysis
    prompts_cls = ResumeToolsPrompts
