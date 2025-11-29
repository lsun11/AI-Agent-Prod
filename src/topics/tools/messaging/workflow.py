from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import (
    MessagingResearchState,
    MessagingCompanyInfo,
    MessagingCompanyAnalysis,
)
from .prompts import MessagingPrompts


class MessagingWorkflow(
    BaseCSWorkflow[MessagingResearchState, MessagingCompanyInfo, MessagingCompanyAnalysis]
):
    """
    Workflow specialized for messaging / communication apps.
    """

    state_model = MessagingResearchState
    company_model = MessagingCompanyInfo
    analysis_model = MessagingCompanyAnalysis
    prompts_cls = MessagingPrompts

    topic_tag = "[Messaging]"
    article_query_template = (
        "{query} messaging apps comparison privacy encryption features"
    )
