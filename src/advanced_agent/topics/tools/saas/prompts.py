from ..base_prompts import BaseCSResearchPrompts


class SaaSPrompts(BaseCSResearchPrompts):
    """
    Business-focused SaaS / line-of-business systems.

    Examples:
      - CRM: Salesforce, HubSpot, Pipedrive
      - ERP: NetSuite, SAP S/4HANA Cloud
      - HR / payroll: Workday, Gusto, Rippling
      - Support / ITSM: Zendesk, ServiceNow, Freshdesk

    Border rules:
      - If the main purpose is *operating a function of a business* (sales, HR, finance, support) → saas
      - If main purpose is generic personal/team productivity → productivity
      - If main purpose is payments/checkout/banking → e_commerce
    """
    TOPIC_LABEL = "business SaaS product, CRM/ERP platform, or line-of-business application"
    ANALYSIS_SUBJECT = (
        "business SaaS platforms across sales, marketing, support, HR, finance, and operations"
    )
    RECOMMENDER_ROLE = "enterprise solutions architect"

