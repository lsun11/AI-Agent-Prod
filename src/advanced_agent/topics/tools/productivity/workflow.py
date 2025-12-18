from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import (
    ProductivityResearchState,
    ProductivityCompanyInfo,
    ProductivityCompanyAnalysis,
)
from .prompts import ProductivityPrompts


class ProductivityWorkflow(
    BaseCSWorkflow[ProductivityResearchState, ProductivityCompanyInfo, ProductivityCompanyAnalysis]
):
    """
    Workflow for productivity tools (e.g. Notion, Todoist, ClickUp).
    """

    state_model = ProductivityResearchState
    company_model = ProductivityCompanyInfo
    analysis_model = ProductivityCompanyAnalysis
    prompts_cls = ProductivityPrompts

    topic_tag = "[Productivity]"
    article_query_template = (
        "{query} productivity tools comparison collaboration workflow"
    )
