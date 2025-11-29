# src/topics/career/system_design_platforms/base_prompts.py

from ..base_prompts import CareerBasePrompts, CAREER_PROMPT_GUIDELINES


class SystemDesignPlatformsPrompts(CareerBasePrompts):
    """
    Prompts for system design interview prep platforms.
    """

    TOOL_EXTRACTION_SYSTEM = f"""You are a career research assistant focusing on
system design interview preparation platforms and resources (e.g. ByteByteGo, system design courses).

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_extraction_user(self, query: str, content: str) -> str:
        return f"""Career Query: {query}
Article Content:
{content}

Extract platforms that:
- teach system design,
- provide structured system design interview prep,
- or offer collections of system design case studies.

Examples: "ByteByteGo", "Exponent", "Educative system design course", etc.

Return up to 5 platform names, one per line.
"""

    TOOL_ANALYSIS_SYSTEM = f"""You are analyzing system design interview prep platforms.

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_analysis_user(self, company_name: str, content: str) -> str:
        return f"""System Design Platform: {company_name}
Website Content (partial):
{content[:2500]}

Return JSON with:
- pricing_model: "Free", "Freemium", "Paid", "Enterprise", or "Unknown".
- pricing_details: Example pricing info if available.
- description: One sentence summarizing what the platform offers for system design.
- tech_stack: e.g. "video course", "animated diagrams", "interactive lessons".
- api_available: true/false/null.
- language_support: human languages if mentioned.
- integration_capabilities: if it integrates with any other tools.
- target_roles: e.g. "backend engineers", "senior engineers".
- seniority_focus: e.g. "Mid/senior", "Staff-level", "All levels".
- includes_diagrams: true if they emphasize diagrams or visual explanations.
- includes_case_studies: true if they focus on case studies, example systems.
- live_mentorship_available: true if they provide live Q&A, coaching, or mentoring.

Return valid JSON only.
"""

    RECOMMENDATIONS_SYSTEM = f"""You are a senior engineer helping someone prepare for system design interviews.

{CAREER_PROMPT_GUIDELINES}

Keep responses under 4 sentences.
"""

    def recommendations_user(self, query: str, company_data: str) -> str:
        return f"""Career Query: {query}
System Design Platforms Analyzed (JSON):
{company_data}

Provide a succinct recommendation:
- Which 1-2 platforms to prioritize.
- If they are better for mid/senior-level vs beginners.
- Any cost/time tradeoffs worth noting.
"""
