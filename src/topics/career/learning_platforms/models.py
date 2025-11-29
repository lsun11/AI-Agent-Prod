# src/topics/career/learning_platforms/base_models.py

from typing import List, Optional
from ..base_models import (
    CareerBaseCompanyAnalysis,
    CareerBaseCompanyInfo,
    CareerBaseResearchState,
)


class LearningPlatformAnalysis(CareerBaseCompanyAnalysis):
    """
    Analysis for learning platforms / bootcamps / course sites.
    """
    course_formats: List[str] = []          # e.g. "video courses", "live classes", "projects"
    certificates_offered: Optional[bool] = None
    time_commitment: Optional[str] = None   # e.g. "self-paced", "10 weeks", etc.


class LearningPlatformInfo(CareerBaseCompanyInfo):
    course_formats: List[str] = []
    certificates_offered: Optional[bool] = None
    time_commitment: Optional[str] = None


class LearningPlatformResearchState(CareerBaseResearchState):
    companies: List[LearningPlatformInfo] = []
