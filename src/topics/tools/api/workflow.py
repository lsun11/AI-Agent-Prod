from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import APIResearchState, APICompanyInfo, APICompanyAnalysis
from .prompts import APIPlatformPrompts


class APIWorkflow(
    BaseCSWorkflow[APIResearchState, APICompanyInfo, APICompanyAnalysis]
):
    """
    Workflow specialized for researching API platforms and developer APIs.
    """

    state_model = APIResearchState
    company_model = APICompanyInfo
    analysis_model = APICompanyAnalysis
    prompts_cls = APIPlatformPrompts

    topic_tag = "[API Platforms]"
    article_query_template = "{query} API platform comparison pricing docs"
