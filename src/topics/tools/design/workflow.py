from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import DesignResearchState, DesignCompanyInfo, DesignCompanyAnalysis
from .prompts import DesignPrompts


class DesignWorkflow(
    BaseCSWorkflow[DesignResearchState, DesignCompanyInfo, DesignCompanyAnalysis]
):
    """
    Workflow specialized for design tools (e.g. Figma, Sketch, Adobe XD).
    """

    state_model = DesignResearchState
    company_model = DesignCompanyInfo
    analysis_model = DesignCompanyAnalysis
    prompts_cls = DesignPrompts

    topic_tag = "[Design]"
    article_query_template = "{query} design tools comparison collaboration pricing"
