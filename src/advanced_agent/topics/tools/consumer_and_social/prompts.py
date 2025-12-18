from ..base_prompts import BaseCSResearchPrompts

class ConsumerAndSocialPrompts(BaseCSResearchPrompts):
    """
    Consumer-facing apps whose primary goal is social interaction, dating,
    entertainment, or community — not commerce or business workflows.

    Examples:
      - TikTok, Instagram, Snapchat
      - Tinder, Bumble (dating)
      - Reddit, Discord (community / fandom)
      - Entertainment / lifestyle apps without strong “work” use cases

    Border rules:
      - Shopping-first → e_commerce (Temu, Shein, Amazon)
      - Banking / payments-first → e_commerce (Venmo, Cash App)
    """

    TOPIC_LABEL = "consumer social app, dating platform, or digital community service"
    ANALYSIS_SUBJECT = (
        "consumer-facing social networks, dating apps, entertainment platforms, and online communities"
    )
    RECOMMENDER_ROLE = "consumer technology analyst"
