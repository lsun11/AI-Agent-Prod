# src/topics/career/job_search/base_models.py

from typing import List, Optional
from ..base_models import (
    CareerBaseCompanyAnalysis,
    CareerBaseCompanyInfo,
    CareerBaseResearchState,
)


class JobSearchCompanyAnalysis(CareerBaseCompanyAnalysis):
    """
    Analysis for job boards / job search platforms.
    """
    remote_friendly: Optional[bool] = None
    geo_focus: Optional[str] = None  # e.g. "US", "EU", "Global"
    salary_transparency: Optional[bool] = None


class JobSearchCompanyInfo(CareerBaseCompanyInfo):
    remote_friendly: Optional[bool] = None
    geo_focus: Optional[str] = None
    salary_transparency: Optional[bool] = None


class JobSearchResearchState(CareerBaseResearchState):
    companies: List[JobSearchCompanyInfo] = []
