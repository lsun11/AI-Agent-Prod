# src/topics/career/behavioral_interview_tools/base_models.py

from typing import List, Optional
from ..base_models import (
    CareerBaseCompanyAnalysis,
    CareerBaseCompanyInfo,
    CareerBaseResearchState,
)


class BehavioralInterviewToolAnalysis(CareerBaseCompanyAnalysis):
    """
    Analysis for behavioral interview & soft-skill tools.
    """
    uses_ai_feedback: Optional[bool] = None
    video_practice_supported: Optional[bool] = None
    includes_example_answers: Optional[bool] = None


class BehavioralInterviewToolInfo(CareerBaseCompanyInfo):
    uses_ai_feedback: Optional[bool] = None
    video_practice_supported: Optional[bool] = None
    includes_example_answers: Optional[bool] = None


class BehavioralInterviewToolResearchState(CareerBaseResearchState):
    companies: List[BehavioralInterviewToolInfo] = []
