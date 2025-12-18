from ..base_prompts import BaseCSResearchPrompts


class SecurityPrompts(BaseCSResearchPrompts):
    """
    Security, identity, and protection tooling.

    Examples:
      - Auth / identity: Auth0, Okta, Keycloak
      - IAM, SSO, MFA providers
      - WAF, bot/fraud detection, DDoS protection
      - SIEM, EDR/XDR, vulnerability scanning

    NOT:
      - Generic access control on a SaaS app (Jira permissions → saas/productivity)
    """

    TOPIC_LABEL = "security tool, identity platform, authentication service, or cybersecurity product"
    ANALYSIS_SUBJECT = (
        "security tools, identity and access management systems, and cyber defense platforms"
    )
    RECOMMENDER_ROLE = "security engineer"
