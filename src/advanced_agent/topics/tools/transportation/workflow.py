from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import (
    TransportationResearchState,
    TransportationCompanyInfo,
    TransportationCompanyAnalysis,
)
from .prompts import TransportationPrompts


class TransportationWorkflow(
    BaseCSWorkflow[TransportationResearchState, TransportationCompanyInfo, TransportationCompanyAnalysis]
):
    """
    Workflow specialized for transportation / mobility apps
    (e.g. Uber, Lyft, Bolt, Didi).
    """

    state_model = TransportationResearchState
    company_model = TransportationCompanyInfo
    analysis_model = TransportationCompanyAnalysis
    prompts_cls = TransportationPrompts

    topic_tag = "[Transportation]"
    article_query_template = (
        "{query} ride sharing apps comparison pricing regions safety"
    )
