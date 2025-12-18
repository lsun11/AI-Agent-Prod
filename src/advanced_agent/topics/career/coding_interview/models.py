# src/topics/career/coding_interview_platforms/base_models.py

from typing import List, Optional
from ..base_models import (
    CareerBaseCompanyAnalysis,
    CareerBaseCompanyInfo,
    CareerBaseResearchState,
)


class CodingInterviewPlatformAnalysis(CareerBaseCompanyAnalysis):
    """
    Analysis for coding interview practice platforms.
    """
    supports_live_interviews: Optional[bool] = None
    problem_difficulty_range: List[str] = []   # e.g. ["Easy", "Medium", "Hard"]
    languages_supported: List[str] = []        # programming languages for coding problems


class CodingInterviewPlatformInfo(CareerBaseCompanyInfo):
    supports_live_interviews: Optional[bool] = None
    problem_difficulty_range: List[str] = []
    languages_supported: List[str] = []


class CodingInterviewPlatformResearchState(CareerBaseResearchState):
    companies: List[CodingInterviewPlatformInfo] = []
