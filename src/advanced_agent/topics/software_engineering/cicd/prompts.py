from ..base_prompts import BaseSoftwareEngPrompts


class CICDPrompts(BaseSoftwareEngPrompts):
    TOOL_EXTRACTION_SYSTEM = (
        "You are a DevOps engineer. Extract CI/CD practices, pipeline stages, "
        "deployment strategies, and key tools from the content."
    )

    TOOL_ANALYSIS_SYSTEM = (
        "You are optimizing a CI/CD pipeline. Focus on reliability, performance, "
        "security checks, and developer experience."
    )

    RECOMMENDATIONS_SYSTEM = (
        "You are guiding a team to improve their CI/CD and release process. "
        "Provide concrete steps to reduce friction and failures."
    )

