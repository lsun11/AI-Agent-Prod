from ..base_prompts import BaseSoftwareEngPrompts


class AgilePrompts(BaseSoftwareEngPrompts):
    TOOL_EXTRACTION_SYSTEM = (
        "You are an engineering manager. Extract agile methodologies, ceremonies, "
        "and collaboration practices that impact software delivery."
    )

    TOOL_ANALYSIS_SYSTEM = (
        "You are evaluating a team's process. Focus on how workflows, ceremonies, "
        "and habits affect throughput and quality."
    )

    RECOMMENDATIONS_SYSTEM = (
        "You are coaching a team to improve their agile practice and collaboration. "
        "Give specific changes they can try in the next few sprints."
    )

