from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import SecurityResearchState, SecurityCompanyInfo, SecurityCompanyAnalysis
from .prompts import SecurityPrompts


class SecurityWorkflow(
    BaseCSWorkflow[SecurityResearchState, SecurityCompanyInfo, SecurityCompanyAnalysis]
):
    """
    Workflow specialized for security / authentication / identity providers.
    """

    state_model = SecurityResearchState
    company_model = SecurityCompanyInfo
    analysis_model = SecurityCompanyAnalysis
    prompts_cls = SecurityPrompts

    topic_tag = "[Security]"
    article_query_template = "{query} security platform comparison SSO IAM pricing"
