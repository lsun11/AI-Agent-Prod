from ..base_prompts import BaseCSResearchPrompts


class CloudServicePrompts(BaseCSResearchPrompts):
    """
    Cloud, infrastructure, and DevOps tooling.

    Examples:
      - AWS, Azure, GCP, DigitalOcean
      - Kubernetes platforms, serverless (Lambda, Cloud Functions)
      - CI/CD infra, observability/monitoring, logging, APM
      - IaC tools (Terraform, Pulumi) if framed as infra tooling

    NOT:
      - Databases as products (Postgres services → database)
      - Generic SaaS business apps (Salesforce → saas)
    """

    TOPIC_LABEL = "cloud platform, infrastructure service, or DevOps tool"
    ANALYSIS_SUBJECT = (
        "cloud providers, compute/storage/networking, DevOps tooling, and infrastructure management"
    )
    RECOMMENDER_ROLE = "cloud infrastructure architect"
