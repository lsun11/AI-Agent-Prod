from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import (
    ConsumerAndSocialResearchState,
    ConsumerAndSocialCompanyInfo,
    ConsumerAndSocialCompanyAnalysis,
)
from .prompts import ConsumerAndSocialPrompts


class ConsumerAndSocialWorkflow(
    BaseCSWorkflow[
        ConsumerAndSocialResearchState,
        ConsumerAndSocialCompanyInfo,
        ConsumerAndSocialCompanyAnalysis,
    ]
):
    """
    Workflow specialized for consumer & social apps
    (dating, social networks, communities, etc.).
    """

    state_model = ConsumerAndSocialResearchState
    company_model = ConsumerAndSocialCompanyInfo
    analysis_model = ConsumerAndSocialCompanyAnalysis
    prompts_cls = ConsumerAndSocialPrompts

    topic_tag = "[Consumer & Social]"
    article_query_template = (
        "{query} apps comparison popularity features safety reviews"
    )
