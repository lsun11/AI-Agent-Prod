from ..base_prompts import BaseCSResearchPrompts

class DesignPrompts(BaseCSResearchPrompts):
    """
    Design, creative, and media tools.

    Examples:
      - Figma, Sketch, Adobe XD, Framer
      - Photoshop, Illustrator, Canva
      - Video/audio tools (Premiere, DaVinci, Final Cut, Audition)
    """

    TOPIC_LABEL = "design tool, creative software, or media production platform"
    ANALYSIS_SUBJECT = (
        "design platforms, creative suites, multimedia software, and content creation tools"
    )
    RECOMMENDER_ROLE = "creative tooling specialist"