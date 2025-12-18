from ..base_prompts import BaseCSResearchPrompts

class FileStoragePrompts(BaseCSResearchPrompts):
    """
    File storage, sync, and backup.

    Examples:
      - Dropbox, Google Drive, OneDrive, iCloud
      - Box, Sync.com, Backblaze
      - Backup / archival tools

    NOT:
      - Pure project-management or doc collaboration (Notion → productivity)
    """

    TOPIC_LABEL = "file storage service, cloud sync tool, or backup platform"
    ANALYSIS_SUBJECT = "cloud storage systems, sync services, backup and recovery tools"
    RECOMMENDER_ROLE = "data operations engineer"
