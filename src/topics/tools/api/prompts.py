from ..base_prompts import BaseCSResearchPrompts


class APIPlatformPrompts(BaseCSResearchPrompts):
    """
    Prompts specialized for API-based platforms, developer APIs, and integrations.
    """

    TOPIC_LABEL = "API platform, developer API, or integration service"
    ANALYSIS_SUBJECT = "API platforms, integration services, and programmable interfaces"
    RECOMMENDER_ROLE = "API integration specialist"

