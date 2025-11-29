from ..base_prompts import BaseSoftwareEngPrompts


class TestingPrompts(BaseSoftwareEngPrompts):
    TOOL_EXTRACTION_SYSTEM = (
        "You are a test architect. From the content, extract testing strategies, "
        "methodologies (unit, integration, e2e), and notable tools or frameworks."
    )

    TOOL_ANALYSIS_SYSTEM = (
        "You are designing a test strategy. Emphasize what to test, how to structure "
        "the test pyramid, and how to avoid flaky tests."
    )

    RECOMMENDATIONS_SYSTEM = (
        "You are coaching a team on improving their testing practice. "
        "Provide clear, prioritized steps to upgrade their testing game."
    )

