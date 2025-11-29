from ..base_prompts import BaseCSResearchPrompts


class DatabasePrompts(BaseCSResearchPrompts):
    """
    Databases, analytics engines, and data platforms.

    Examples:
      - OLTP DBs (Postgres, MySQL, MongoDB)
      - Data warehouses (Snowflake, BigQuery, Redshift)
      - Data lakes, lakehouses, OLAP engines
      - Managed DBaaS / analytics SaaS

    NOT:
      - Pure BI/reporting tools without storage (Looker, Metabase → saas)
    """
    TOPIC_LABEL = "database, data warehouse, data lake, or analytics engine"
    ANALYSIS_SUBJECT = (
        "databases, analytics platforms, data processing engines, and managed data services"
    )
    RECOMMENDER_ROLE = "data infrastructure architect"

