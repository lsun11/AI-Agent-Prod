# src/topics/career/resume_tools/base_models.py

from typing import List, Optional
from pydantic import BaseModel

from ..base_models import (
    CareerBaseCompanyAnalysis,
    CareerBaseCompanyInfo,
    CareerBaseResearchState,
)


class ResumeToolsCompanyAnalysis(CareerBaseCompanyAnalysis):
    """
    Analysis for resume builders / ATS optimization tools.
    """
    ats_friendly: Optional[bool] = None
    resume_formats_supported: List[str] = []  # e.g. PDF, DOCX, etc.
    keyword_optimization_support: Optional[bool] = None


class ResumeToolsCompanyInfo(CareerBaseCompanyInfo):
    ats_friendly: Optional[bool] = None
    resume_formats_supported: List[str] = []
    keyword_optimization_support: Optional[bool] = None


class ResumeToolsResearchState(CareerBaseResearchState):
    companies: List[ResumeToolsCompanyInfo] = []
