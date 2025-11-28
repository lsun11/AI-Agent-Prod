from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import (
    ECommerceResearchState,
    ECommerceCompanyInfo,
    ECommerceCompanyAnalysis,
)
from .prompts import ECommercePrompts


class ECommerceWorkflow(
    BaseCSWorkflow[ECommerceResearchState, ECommerceCompanyInfo, ECommerceCompanyAnalysis]
):
    """
    Workflow specialized for e-commerce platforms / tooling.
    """

    state_model = ECommerceResearchState
    company_model = ECommerceCompanyInfo
    analysis_model = ECommerceCompanyAnalysis
    prompts_cls = ECommercePrompts

    topic_tag = "[E-Commerce]"
    article_query_template = (
        "{query} ecommerce platforms comparison pricing transaction fees"
    )
