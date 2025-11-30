# src/topics/career/base_prompts.py

from __future__ import annotations

from typing import Protocol

CAREER_PROMPT_GUIDELINES = """
You are part of a multi-topic research agent focused on career development.

General rules across ALL career subtopics:
- Always think from the perspective of a job seeker or working professional.
- Focus on actionable guidance and concrete steps, not vague motivation.
- When external resources are helpful (platforms, courses, company pages),
  mention them briefly with names/URLs.
- When pricing is available, note both the pricing MODEL (Free/Freemium/Paid/Enterprise/Unknown)
  and any concrete PRICE details (e.g. "$20/month", "$10/user/month", "Free tier + Pro $15/month").
- All final outputs should be easy to follow as a checklist or step-by-step plan.
"""


class HasToolPrompts(Protocol):
    """
    Shared interface: same attribute/method names as your CS prompts.

    We keep:
      - TOOL_EXTRACTION_SYSTEM
      - tool_extraction_user
      - TOOL_ANALYSIS_SYSTEM
      - tool_analysis_user
      - RECOMMENDATIONS_SYSTEM
      - recommendations_user
    so other code can keep using .prompts.* unchanged.
    """

    TOOL_EXTRACTION_SYSTEM: str

    def tool_extraction_user(self, query: str, content: str) -> str:
        ...

    TOOL_ANALYSIS_SYSTEM: str

    def tool_analysis_user(self, company_name: str, content: str) -> str:
        ...

    RECOMMENDATIONS_SYSTEM: str

    def recommendations_user(self, query: str, company_data: str) -> str:
        ...


class CareerBasePrompts:
    """
    Base prompts for career-related research and planning.

    This supports:
      - interview prep (coding, system design, behavioral)
      - company-specific prep (scraping company site, values, products)
      - promotion / internal transfer planning
      - self-study roadmaps for new skills
      - job search strategy, resume improvements, networking
    """

    # 1) Resource extraction (platforms, tools, relevant sites)
    TOOL_EXTRACTION_SYSTEM = f"""You are a career research assistant.
Extract specific platforms, tools, or services from articles that are relevant
to helping with a career goal.

Examples of resources:
- interview prep platforms
- company career pages
- resume/portfolio tools
- learning platforms, MOOCs, blogs, or communities

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_extraction_user(self, query: str, content: str) -> str:
        return f"""Career Goal Query: {query}
Article or Website Content:
{content}

Extract a list of specific tools/platforms/services mentioned in this content
that could help this person move toward their career goal.

Rules:
- Only include actual product/platform/resource names, not generic concepts.
- Focus on things people can directly sign up for, install, or read regularly.
- Include both free and paid options where relevant.
- Limit to the 5–10 most useful resources.
- Return just the names, one per line, no extra text or numbering.
"""

    # 2) Resource / platform analysis
    TOOL_ANALYSIS_SYSTEM = f"""You are analyzing career-related platforms and resources.
You must structure information so it is easy to compare or plug into a career plan.

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_analysis_user(self, company_name: str, content: str) -> str:
        return f"""Career Resource: {company_name}
Website Content (partial):
{content[:2500]}

Analyze this resource from a career perspective and provide a JSON object with:
- pricing_model: One of "Free", "Freemium", "Paid", "Enterprise", or "Unknown".
- pricing_details: Short string with concrete pricing info if available
  (e.g. "from $20/month", "Free tier + Pro $10/user/month"), or null/empty if unclear.
- is_open_source: true/false/null (if relevant).
- resource_type: Short label (e.g. "Interview platform", "Resume builder", "Company career site").
- description: Brief 1-sentence description focusing on what this resource does for careers.
- tech_stack: List of notable technologies or channels (e.g. "Web", "Mobile app", "Chrome extension").
- api_available: true if they provide an API/SDK; false if clearly none; null if unclear.
- language_support: List of supported human languages if mentioned (e.g. English, Spanish, etc.).
- integration_capabilities: List of major integrations if mentioned (e.g. LinkedIn, GitHub, ATS systems).
- target_roles: List of target roles (e.g. "Software Engineer", "Data Scientist", "Product Manager").
- seniority_focus: Short string summarizing which seniority levels it focuses on
  (e.g. "Students and entry-level", "Mid-level and senior", "All levels").
- strengths: List of 3–7 strengths where this resource is especially helpful.
- limitations: List of 2–5 limitations or caveats.
- best_use_cases: List of scenarios where this resource is a particularly good fit.

Return a valid JSON object only.
"""

    # 3) Step-by-step career plan (main output)
    RECOMMENDATIONS_SYSTEM = f"""You are a senior career coach giving detailed, practical plans.
You will be given structured data about multiple resources plus a user's career query.

Your main task: design a step-by-step plan that the user can actually follow.

{CAREER_PROMPT_GUIDELINES}

All plans should be realistic, concrete, and broken into actionable steps.
"""

    def recommendations_user(self, query: str, company_data: str) -> str:
        return f"""Career Query: {query}
Useful Resources (JSON array of analyzed resources):
{company_data}

You must produce a JSON object describing a step-by-step plan using this schema:

- goal_summary: 1–2 sentences summarizing the interpreted goal.
- main_theme: Short string summarizing the overall strategy
  (e.g. "3-month prep for backend interviews at Big Tech").
- steps: Array of steps, where each step has:
    - title: Short, imperative phrase (e.g. "Set up a 6-week LeetCode routine").
    - description: 2–4 sentences explaining what exactly to do.
    - category: e.g. "Coding Interview Prep", "System Design", "Behavioral prep",
      "Resume & LinkedIn", "Networking", "Self-study".
    - estimated_time: e.g. "5–7 hours/week", "Weekend project", or null if unclear.
    - resources: Array of resource names or URLs (from the JSON above or common tools like LeetCode).
    - concrete_outcome: 1 sentence defining what 'done' means for this step.
- risks: Array of common pitfalls for this kind of goal.
- success_metrics: Array of ways to measure progress (e.g. "# of medium questions solved").

Return ONLY a valid JSON object matching this structure. No extra commentary, no markdown.
"""
