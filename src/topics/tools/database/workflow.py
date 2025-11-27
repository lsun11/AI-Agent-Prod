from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import DatabaseResearchState, DatabaseCompanyInfo, DatabaseCompanyAnalysis
from .prompts import DatabasePrompts


class DatabaseWorkflow(
    BaseCSWorkflow[DatabaseResearchState, DatabaseCompanyInfo, DatabaseCompanyAnalysis]
):
    """
    Workflow specialized for databases and data platforms.
    """

    state_model = DatabaseResearchState
    company_model = DatabaseCompanyInfo
    analysis_model = DatabaseCompanyAnalysis
    prompts_cls = DatabasePrompts

    topic_tag = "[Database]"
    article_query_template = "{query} database or data platform comparison performance pricing"
