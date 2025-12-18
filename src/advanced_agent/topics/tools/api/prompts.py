from ..base_prompts import BaseCSResearchPrompts


class APIPlatformPrompts(BaseCSResearchPrompts):
    """
    Developer-facing APIs and integration services where the *primary product*
    is an API/SDK.

    Examples:
      - Twilio, Stripe API, SendGrid, Clerk, Auth0-as-API
      - API gateways, integration hubs, webhooks platforms

    NOT:
      - Generic SaaS apps that merely offer an API (Salesforce → saas)
      - Core cloud providers (AWS API Gateway → cloud, not api)
    """

    TOPIC_LABEL = "API platform, developer API, or integration service"
    ANALYSIS_SUBJECT = (
        "developer APIs, integration services, webhooks platforms, and API gateways"
    )
    RECOMMENDER_ROLE = "API integration specialist"

