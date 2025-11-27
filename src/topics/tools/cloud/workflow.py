from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import CloudResearchState, CloudCompanyInfo, CloudCompanyAnalysis
from .prompts import CloudServicePrompts


class CloudWorkflow(
    BaseCSWorkflow[CloudResearchState, CloudCompanyInfo, CloudCompanyAnalysis]
):
    """
    Workflow specialized for cloud / infra providers.
    """

    state_model = CloudResearchState
    company_model = CloudCompanyInfo
    analysis_model = CloudCompanyAnalysis
    prompts_cls = CloudServicePrompts

    topic_tag = "[Cloud]"
    article_query_template = "{query} cloud providers comparison pricing regions"
