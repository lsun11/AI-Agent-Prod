from ..base_prompts import BaseCSResearchPrompts

class TransportationPrompts(BaseCSResearchPrompts):
    TOPIC_LABEL = "transportation app, delivery platform, or mobility service"
    ANALYSIS_SUBJECT = "transportation software, delivery apps, logistics services, and mobility solutions"
    RECOMMENDER_ROLE = "mobility technology analyst"
class TransportationPrompts(BaseCSResearchPrompts):
    """
    Transportation, mobility, and delivery services where the
    *core value* is moving people or things.

    Examples:
      - Ride-share: Uber, Lyft, Didi, Grab
      - Micromobility: Lime, Bird, Tier
      - Food / parcel delivery when framed as logistics (Uber Eats, DoorDash)
      - Airport transfer and shuttle services

    Border rules:
      - If query is about “ordering food as a consumer app” it may overlap with
        consumer_and_social, but if the focus is on logistics / fleet / routing,
        keep it here (transportation).
    """

    TOPIC_LABEL = "transportation app, delivery platform, or mobility/logistics service"
    ANALYSIS_SUBJECT = (
        "transportation software, ride-share platforms, delivery and logistics services, and mobility apps"
    )
    RECOMMENDER_ROLE = "mobility technology analyst"