# src/topics/career/system_design_platforms/base_models.py

from typing import List, Optional
from ..base_models import (
    CareerBaseCompanyAnalysis,
    CareerBaseCompanyInfo,
    CareerBaseResearchState,
)


class SystemDesignPlatformAnalysis(CareerBaseCompanyAnalysis):
    """
    Analysis for system design interview preparation platforms.
    """
    includes_diagrams: Optional[bool] = None
    includes_case_studies: Optional[bool] = None
    live_mentorship_available: Optional[bool] = None


class SystemDesignPlatformInfo(CareerBaseCompanyInfo):
    includes_diagrams: Optional[bool] = None
    includes_case_studies: Optional[bool] = None
    live_mentorship_available: Optional[bool] = None


class SystemDesignPlatformResearchState(CareerBaseResearchState):
    companies: List[SystemDesignPlatformInfo] = []
