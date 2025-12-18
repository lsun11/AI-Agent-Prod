from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import AIResearchState, AICompanyInfo, AICompanyAnalysis
from .prompts import AIPlatformPrompts


class AIWorkflow(
    BaseCSWorkflow[AIResearchState, AICompanyInfo, AICompanyAnalysis]
):
    """
    Workflow specialized for researching AI/ML platforms & model providers.
    """

    state_model = AIResearchState
    company_model = AICompanyInfo
    analysis_model = AICompanyAnalysis
    prompts_cls = AIPlatformPrompts

    topic_tag = "[AI / ML]"
    article_query_template = "{query} AI platform comparison model hosting pricing"
