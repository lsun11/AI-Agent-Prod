from ..base_prompts import BaseCSResearchPrompts


class SaaSPrompts(BaseCSResearchPrompts):
    """
    Prompts specialized for researching SaaS products.
    """
    TOPIC_LABEL = "SaaS product, CRM/ERP system, or business operations platform"
    ANALYSIS_SUBJECT = "business SaaS platforms for sales, operations, HR, finance, and enterprise workflows"
    RECOMMENDER_ROLE = "enterprise solutions architect"

