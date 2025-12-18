from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import SaaSResearchState, SaaSCompanyInfo, SaaSCompanyAnalysis
from .prompts import SaaSPrompts


class SaaSWorkflow(
    BaseCSWorkflow[SaaSResearchState, SaaSCompanyInfo, SaaSCompanyAnalysis]
):
    """
    Workflow specialized for researching SaaS products.
    """

    state_model = SaaSResearchState
    company_model = SaaSCompanyInfo
    analysis_model = SaaSCompanyAnalysis
    prompts_cls = SaaSPrompts

    topic_tag = "[SaaS]"
    article_query_template = "{query} SaaS product comparison pricing features"
