from __future__ import annotations

from ..base_workflow import BaseCSWorkflow
from .models import (
    FileStorageResearchState,
    FileStorageCompanyInfo,
    FileStorageCompanyAnalysis,
)
from .prompts import FileStoragePrompts


class FileStorageWorkflow(
    BaseCSWorkflow[FileStorageResearchState, FileStorageCompanyInfo, FileStorageCompanyAnalysis]
):
    """
    Workflow for file sync / backup / cloud storage (e.g. Dropbox, Google Drive).
    """

    state_model = FileStorageResearchState
    company_model = FileStorageCompanyInfo
    analysis_model = FileStorageCompanyAnalysis
    prompts_cls = FileStoragePrompts

    topic_tag = "[File Storage]"
    article_query_template = (
        "{query} cloud storage services comparison pricing security"
    )
