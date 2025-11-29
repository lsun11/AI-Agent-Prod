# src/topics/career/job_search/base_workflow.py

from ..base_workflow import CareerBaseWorkflow
from .models import (
    JobSearchCompanyAnalysis,
    JobSearchCompanyInfo,
    JobSearchResearchState,
)
from .prompts import JobSearchPrompts


class JobSearchWorkflow(
    CareerBaseWorkflow[
        JobSearchResearchState,
        JobSearchCompanyInfo,
        JobSearchCompanyAnalysis,
        JobSearchPrompts,
    ]
):
    topic_tag = "Job Search Platforms & Market Analysis"
    article_query_suffix = "job search platforms job boards remote job sites salary insights comparison"
    official_site_suffix = "jobs platform official site"

    state_cls = JobSearchResearchState
    info_cls = JobSearchCompanyInfo
    analysis_cls = JobSearchCompanyAnalysis
    prompts_cls = JobSearchPrompts
