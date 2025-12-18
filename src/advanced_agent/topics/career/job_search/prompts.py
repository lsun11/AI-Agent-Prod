# src/topics/career/job_search/base_prompts.py

from ..base_prompts import CareerBasePrompts, CAREER_PROMPT_GUIDELINES


class JobSearchPrompts(CareerBasePrompts):
    """
    Prompts for job boards & job search platforms.
    """

    TOOL_EXTRACTION_SYSTEM = f"""You are a career research assistant focusing on job search platforms:
job boards, remote job sites, and salary/market insight sites.

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_extraction_user(self, query: str, content: str) -> str:
        return f"""Career Query: {query}
Article Content:
{content}

Extract platforms that:
- list jobs, or
- help discover job opportunities, or
- provide salary & market insights relevant to job search.

Examples: "LinkedIn Jobs", "Indeed", "Otta", "Glassdoor", "Levels.fyi".

Return:
- 3-5 platform names,
- one per line,
- no descriptions or extra text.
"""

    TOOL_ANALYSIS_SYSTEM = f"""You are analyzing job search platforms and job market tools (job boards,
remote job sites, salary insight platforms).

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_analysis_user(self, company_name: str, content: str) -> str:
        return f"""Job Search Platform: {company_name}
Website Content (partial):
{content[:2500]}

Provide JSON with:
- pricing_model: "Free", "Freemium", "Paid", "Enterprise", or "Unknown".
- pricing_details: Any concrete pricing info (e.g. "Job seekers free, companies pay").
- description: One sentence on how this helps with job search.
- tech_stack: High-level ("Web app", "Mobile app", "Chrome extension") if mentioned.
- api_available: true/false/null.
- language_support: Supported languages, if any.
- integration_capabilities: Integrations like "LinkedIn", "GitHub", "Google", etc.
- target_roles: Primary roles (e.g. "tech roles", "all roles", "early career").
- seniority_focus: e.g. "Entry-level/grad", "Mid-senior", "All levels".
- remote_friendly: true if platform focuses on remote roles or provides explicit remote filters.
- geo_focus: if it clearly focuses on a region (e.g. "US", "Europe", "India").
- salary_transparency: true if it emphasizes salary info before applying.

Return valid JSON only.
"""

    RECOMMENDATIONS_SYSTEM = f"""You are a senior career coach specializing in job search strategy.

{CAREER_PROMPT_GUIDELINES}

You will recommend which job boards/platforms a user should focus on.
Keep replies under 4 sentences.
"""

    def recommendations_user(self, query: str, company_data: str) -> str:
        return f"""Career Query: {query}
Job Platforms Analyzed (JSON array):
{company_data}

Provide a short recommendation:
- Which 1-3 job platforms are best suited.
- Any geographic or remote-work considerations.
- Any important pricing or limitations.

Be concrete and actionable.
"""
