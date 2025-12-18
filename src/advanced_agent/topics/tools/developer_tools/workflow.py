from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import (
    DeveloperToolResearchState,
    DeveloperToolCompanyInfo,
    DeveloperToolCompanyAnalysis,
)
from .prompts import DeveloperToolsPrompts


class DeveloperToolsWorkflow(
    BaseCSWorkflow[DeveloperToolResearchState, DeveloperToolCompanyInfo, DeveloperToolCompanyAnalysis]
):
    """
    Workflow specialized for researching developer tools.

    Uses:
    - DeveloperToolResearchState
    - DeveloperToolCompanyInfo
    - DeveloperToolCompanyAnalysis
    - DeveloperToolsPrompts
    """

    state_model = DeveloperToolResearchState
    company_model = DeveloperToolCompanyInfo
    analysis_model = DeveloperToolCompanyAnalysis
    prompts_cls = DeveloperToolsPrompts

    topic_tag = "[Developer Tools]"
    article_query_template = "{query} developer tools comparison best alternatives"

