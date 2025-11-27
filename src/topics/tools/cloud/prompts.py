from ..base_prompts import BaseCSResearchPrompts


class CloudServicePrompts(BaseCSResearchPrompts):
    """
    Prompts specialized for API-based platforms, developer APIs, and integrations.
    """

    TOPIC_LABEL = "cloud service, infrastructure platform, or DevOps tool"
    ANALYSIS_SUBJECT = "cloud platforms, infrastructure services, DevOps tooling, and runtime environments"
    RECOMMENDER_ROLE = "cloud infrastructure architect"
