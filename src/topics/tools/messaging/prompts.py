from ..base_prompts import BaseCSResearchPrompts

class MessagingPrompts(BaseCSResearchPrompts):
    """
    Real-time communication: chat, voice, video.

    Examples:
      - WhatsApp, Telegram, Signal, Messenger
      - Slack, Microsoft Teams (communication aspect)
      - Zoom, Google Meet, Webex

    Border rules:
      - If the product is primarily “talk/chat/meet now” → messaging
      - If it’s mostly async knowledge / task tracking → productivity
    """

    TOPIC_LABEL = "communication tool, messaging app, or video conferencing platform"
    ANALYSIS_SUBJECT = (
        "communication platforms, chat applications, team messaging, and real-time collaboration tools"
    )
    RECOMMENDER_ROLE = "communication systems analyst"
