from ..base_prompts import BaseCSResearchPrompts


class ContentAndWebsitePrompts(BaseCSResearchPrompts):
    """
    Content management, site building, and publishing platforms.

    Examples:
      - WordPress, Ghost, Drupal
      - Webflow, Wix, Squarespace
      - Headless CMS (Contentful, Sanity)
      - Blog/newsletter tools (Substack, Medium)

    NOT:
      - Commerce-first storefronts (Shopify → e_commerce)
      - Internal knowledge bases for teams (Confluence → productivity)
    """

    TOPIC_LABEL = "content management system, website builder, or publishing platform"
    ANALYSIS_SUBJECT = (
        "CMS platforms, site builders, headless CMSs, and digital publishing tools"
    )
    RECOMMENDER_ROLE = "web platform strategist"
