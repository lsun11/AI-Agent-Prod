from ..base_prompts import BaseCSResearchPrompts

class ProductivityPrompts(BaseCSResearchPrompts):
    """
    Productivity, collaboration, and work management.

    Examples:
      - Notion, Coda, Confluence, Evernote
      - Jira, Asana, Trello, Monday.com, ClickUp
      - Todoist, Things, motion planners
      - Internal knowledge bases and wikis

    Border rules:
      - If primarily “tasks, docs, planning, organizing work” → productivity
      - If primarily direct chat/video → messaging
      - If primarily line-of-business (CRM/ERP/HRIS) → saas
    """

    TOPIC_LABEL = "productivity tool, collaboration suite, or work/project management platform"
    ANALYSIS_SUBJECT = (
        "productivity apps, collaboration software, work management tools, and knowledge bases"
    )
    RECOMMENDER_ROLE = "productivity systems consultant"