# src/topics/developer_tools/base_models.py
from __future__ import annotations

from typing import Optional

from ..base_models import (
    BaseCompanyAnalysis,
    BaseCompanyInfo,
    BaseResearchState,
)


class DeveloperToolCompanyAnalysis(BaseCompanyAnalysis):
    """
    Structured output for LLM company analysis focused on DEVELOPER TOOLS.
    Inherits generic fields from BaseCompanyAnalysis.
    """
    # For now, we just reuse the base fields.
    # If later you want dev-tool-specific metrics (e.g. DX_score),
    # you can add them here.
    pass


class DeveloperToolCompanyInfo(BaseCompanyInfo):
    """
    Developer-tools-specific company/tool info.
    Extends BaseCompanyInfo with developer experience metrics.
    """
    # Developer-specific fields
    developer_experience_rating: Optional[str] = None  # Poor, Good, Excellent


class DeveloperToolResearchState(BaseResearchState):
    """
    Runtime state for the developer tools research workflow.
    Inherits fields from BaseResearchState, which already match your original:
    - query
    - extracted_tools
    - companies
    - search_results
    - analysis
    """
    # If you want dev-tools-specific state later, add fields here.
    pass
