# src/topics/career/learning_platforms/base_prompts.py

from ..base_prompts import CareerBasePrompts, CAREER_PROMPT_GUIDELINES


class LearningPlatformsPrompts(CareerBasePrompts):
    """
    Prompts for learning platforms / skill roadmaps.
    """

    TOOL_EXTRACTION_SYSTEM = f"""You are a career research assistant focusing on learning platforms:
online course sites, bootcamps, structured roadmaps for career transitions or upskilling.

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_extraction_user(self, query: str, content: str) -> str:
        return f"""Career Query: {query}
Article Content:
{content}

Extract learning platforms that:
- provide courses, bootcamps, or structured paths, and
- are clearly relevant to this career query (e.g. "learn data engineering", "move into ML", etc.).

Examples: "Coursera", "Udemy", "DataCamp", "Educative", "Frontend Masters", "LeetCode courses".

Return up to 5 platform names, one per line, no extra text.
"""

    TOOL_ANALYSIS_SYSTEM = f"""You are analyzing learning platforms (courses, bootcamps, online schools)
from a career-mobility perspective.

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_analysis_user(self, company_name: str, content: str) -> str:
        return f"""Learning Platform: {company_name}
Website Content (partial):
{content[:2500]}

Return JSON with:
- pricing_model: "Free", "Freemium", "Paid", "Enterprise", or "Unknown".
- pricing_details: Example price info ("courses from $10", "subscription $39/month").
- description: One sentence summarizing what they teach and for whom.
- tech_stack: e.g. "Web platform", "Mobile app", "Video + projects".
- api_available: true/false/null if they expose APIs or integrations.
- language_support: Supported languages if mentioned.
- integration_capabilities: e.g. "integrates with company LMS", "Slack", "GitHub".
- target_roles: e.g. "data scientists", "frontend devs", "product managers".
- seniority_focus: e.g. "Beginners", "Intermediate", "Advanced", "All levels".
- course_formats: e.g. ["video lectures", "quizzes", "projects", "live classes"].
- certificates_offered: true if they offer certificates/credentials.
- time_commitment: Short string summarizing time expectations ("self-paced", "6-month program").

Return valid JSON only.
"""

    RECOMMENDATIONS_SYSTEM = f"""You are a senior career coach recommending learning platforms
for upskilling or switching careers.

{CAREER_PROMPT_GUIDELINES}

Keep responses brief (3-4 sentences).
"""

    def recommendations_user(self, query: str, company_data: str) -> str:
        return f"""Career Query: {query}
Learning Platforms Analyzed (JSON):
{company_data}

Provide a concise recommendation:
- Which 1-2 platforms look best for this person's goals.
- Why they are a good fit (content depth, structure, cost).
- Any warnings (e.g. expensive, heavy time commitment).

Be specific, not generic.
"""
