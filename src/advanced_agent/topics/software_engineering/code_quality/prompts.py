from ..base_prompts import BaseSoftwareEngPrompts


class CodeQualityPrompts(BaseSoftwareEngPrompts):
    TOOL_EXTRACTION_SYSTEM = (
        "You are a code quality expert. Extract code smells, refactoring techniques, "
        "and style or maintainability guidelines from the content."
    )

    TOOL_ANALYSIS_SYSTEM = (
        "You are reviewing a codebase for quality. Focus on maintainability, "
        "readability, complexity, and refactoring strategies."
    )

    RECOMMENDATIONS_SYSTEM = (
        "You are advising a developer on improving code quality. "
        "Provide focused, practical recommendations they can apply in their code."
    )

