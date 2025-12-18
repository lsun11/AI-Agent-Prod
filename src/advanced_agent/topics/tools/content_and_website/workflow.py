from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import (
    ContentAndWebsiteResearchState,
    ContentAndWebsiteCompanyInfo,
    ContentAndWebsiteCompanyAnalysis,
)
from .prompts import ContentAndWebsitePrompts


class ContentAndWebsiteWorkflow(
    BaseCSWorkflow[
        ContentAndWebsiteResearchState,
        ContentAndWebsiteCompanyInfo,
        ContentAndWebsiteCompanyAnalysis,
    ]
):
    """
    Workflow for CMS, website builders, blogging platforms, etc.
    """

    state_model = ContentAndWebsiteResearchState
    company_model = ContentAndWebsiteCompanyInfo
    analysis_model = ContentAndWebsiteCompanyAnalysis
    prompts_cls = ContentAndWebsitePrompts

    topic_tag = "[Content & Websites]"
    article_query_template = (
        "{query} platforms comparison pricing features templates"
    )
