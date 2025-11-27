from ..base_prompts import BaseCSResearchPrompts


class DatabasePrompts(BaseCSResearchPrompts):
    """
    Prompts specialized for databases, data warehouses, and data platforms.
    """
    TOPIC_LABEL = "database, data warehouse, data lake, or analytics engine"
    ANALYSIS_SUBJECT = "databases, analytics platforms, data processing engines, and storage systems"
    RECOMMENDER_ROLE = "data infrastructure architect"

