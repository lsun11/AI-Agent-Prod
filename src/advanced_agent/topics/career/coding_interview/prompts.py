# src/topics/career/coding_interview_platforms/base_prompts.py

from ..base_prompts import CareerBasePrompts, CAREER_PROMPT_GUIDELINES


class CodingInterviewPlatformsPrompts(CareerBasePrompts):
    """
    Prompts for coding interview practice platforms (LeetCode, HackerRank, etc.).
    """

    TOOL_EXTRACTION_SYSTEM = f"""You are a career research assistant focused on coding interview
practice platforms (e.g. LeetCode, HackerRank, CodeSignal, AlgoExpert).

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_extraction_user(self, query: str, content: str) -> str:
        return f"""Career Query: {query}
Article Content:
{content}

Extract platforms that:
- are primarily used for coding interview practice, mock interviews,
  or algorithm/data structure preparation.

Examples: "LeetCode", "HackerRank", "CodeSignal", "AlgoExpert", "Interviewing.io" (for live).

Return up to 5 platform names, one per line, no extra text.
"""

    TOOL_ANALYSIS_SYSTEM = f"""You are analyzing coding interview practice platforms.

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_analysis_user(self, company_name: str, content: str) -> str:
        return f"""Coding Interview Platform: {company_name}
Website Content (partial):
{content[:2500]}

Return JSON with:
- pricing_model: "Free", "Freemium", "Paid", "Enterprise", or "Unknown".
- pricing_details: Example pricing info if available.
- description: One sentence summarizing what this platform offers for coding interviews.
- tech_stack: e.g. "Online coding environment", "web app", "video + code editor".
- api_available: true/false/null if they mention APIs for companies.
- language_support: list of human languages for UI if mentioned.
- integration_capabilities: e.g. ATS integration for companies, or calendar/Zoom integration.
- target_roles: e.g. "software engineers", "data scientists".
- seniority_focus: e.g. "students", "all levels".
- supports_live_interviews: true if they host live mock/real interviews.
- problem_difficulty_range: e.g. ["Easy", "Medium", "Hard"] if mentioned.
- languages_supported: list of programming languages available for coding problems.

Return valid JSON only.
"""

    RECOMMENDATIONS_SYSTEM = f"""You are a senior engineering mentor helping someone prepare
for coding interviews.

{CAREER_PROMPT_GUIDELINES}

Keep responses under 4 sentences.
"""

    def recommendations_user(self, query: str, company_data: str) -> str:
        return f"""Career Query: {query}
Coding Interview Platforms Analyzed (JSON):
{company_data}

Provide a concise recommendation:
- Which 1-2 platforms to focus on and why.
- If some are better for beginners vs experienced candidates.
- Any cost considerations.

Be concrete and focused on interview success.
"""
