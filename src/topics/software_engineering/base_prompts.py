from __future__ import annotations

from abc import ABC

from ..root_prompts import BaseRootPrompts


class BaseSoftwareEngPrompts(BaseRootPrompts, ABC):
    """Base prompt set for software-engineering research & on-the-job guidance.

    Subclasses can override the SYSTEM strings and user message builders
    to specialize for particular subtopics (architecture, testing, CI/CD, etc.).
    """

    TOOL_EXTRACTION_SYSTEM: str = (
        "You are a senior software engineer and researcher.\n"
        "Given some articles, documentation, or notes about a project, extract the most important\n"
        "concepts, techniques, tools, and practices that a developer or DevOps engineer should know\n"
        "for this topic.\n"
        "Focus especially on things that influence how we design, test, deploy, or maintain systems."
    )

    TOOL_ANALYSIS_SYSTEM: str = (
        "You are analyzing software-engineering resources. Focus on extracting:\n"
        "- concrete best practices\n"
        "- trade-offs and pitfalls\n"
        "- tools or patterns that can be applied in real projects\n"
        "Your output will be used to guide an engineer on an actual codebase or service."
    )

    RECOMMENDATIONS_SYSTEM: str = (
        "You are a staff-level engineer mentoring a team.\n"
        "Based on the collected information and the project description, provide concise,\n"
        "actionable recommendations that can be applied in the next 1–4 weeks.\n"
        "Emphasize specific steps, not generic advice."
    )

    COMPATIBILITY_NOTE: str = (
        "This prompt set is fully compatible with the agent's expectations.\n\n"
        "NOTE: All attribute and method names are kept the same as the original\n"
        "developer tools prompts: TOOL_EXTRACTION_SYSTEM, tool_extraction_user,\n"
        "TOOL_ANALYSIS_SYSTEM, tool_analysis_user, RECOMMENDATIONS_SYSTEM,\n"
        "and recommendations_user. This allows the same calling code to work\n"
        "for all subtopics without modification."
    )

    @staticmethod
    def tool_extraction_user(query: str, content: str) -> str:
        return (
            "Developer Query: {query}\n\n"
            "Project/Context Content:\n{content_snippet}\n\n"
            "Extract a concise list of 5–10 key concepts, techniques, tools, or practices\n"
            "that are most relevant for answering this query. These might include testing strategies,\n"
            "CI/CD patterns, architecture patterns, code quality practices, agile practices, etc.\n"
            "Return only one item per line without extra commentary."
        ).format(query=query, content_snippet=content[:4000])

    @staticmethod
    def tool_analysis_user(topic_label: str, content: str) -> str:
        return (
            "Software Engineering Topic: {topic}\n\n"
            "Content:\n{content_snippet}\n\n"
            "Analyze this content for a practicing software engineer / DevOps / PM and provide\n"
            "- summary: a 2–3 sentence summary of the core idea or recommended approach.\n"
            "- best_practices: bullet-style array of concrete best practices to follow.\n"
            "- pitfalls: bullet-style array of common mistakes, risks, or anti-patterns.\n"
            "- suggested_action_plan: bullet-style array of 5–10 next steps the team can take\n"
            "  in the current project over the next 1–4 weeks.\n"
            "- suggested_tools: (optional) array of tools/services that could help.\n"
            "- applicable_scenarios: (optional) array of scenarios where this guidance is most relevant.\n\n"
            " Do NOT return JSON explicitly; the system will handle formatting."
        ).format(topic=topic_label, content_snippet=content[:2500])

    @staticmethod
    def recommendations_user(query: str, serialized_resources: str) -> str:
        return (
            "Developer Query: {query}\n\n"
            "Aggregated Resource Data (JSON-like, may include multiple analyzed resources):\n"
            "{resources}\n\n"
            "Provide a short but actionable recommendation for the team using the schema:\n"
            "- summary: 2–3 sentence summary of the best approach.\n"
            "- best_practices: list of 5–10 concrete best practices.\n"
            "- pitfalls: list of 3–7 main pitfalls or risks to avoid.\n"
            "- suggested_action_plan: list of 5–10 steps the team can take in the next 1–4 weeks,\n"
            "  written as imperative tasks (e.g. \"Add contract tests around the payment API\").\n"
            "- suggested_tools: optional list of tools/services that would help.\n"
            "- applicable_scenarios: optional list of scenarios where this plan is most suitable.\n\n"
            "Return ONLY a valid JSON object."
        ).format(query=query, resources=serialized_resources[:4000])
