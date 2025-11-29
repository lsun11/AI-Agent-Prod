# src/topics/career/behavioral_interview_tools/base_prompts.py

from ..base_prompts import CareerBasePrompts, CAREER_PROMPT_GUIDELINES


class BehavioralInterviewToolsPrompts(CareerBasePrompts):
    """
    Prompts for behavioral interview and career coaching tools.
    """

    TOOL_EXTRACTION_SYSTEM = f"""You are a career research assistant focusing on
behavioral interview practice tools and career coaching platforms.

These may include:
- AI mock interview tools,
- platforms with example answers + feedback,
- video-based practice systems,
- structured behavioral question banks.

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_extraction_user(self, query: str, content: str) -> str:
        return f"""Career Query: {query}
Article Content:
{content}

Extract tools/platforms that clearly:
- help practice behavioral/soft-skill questions, or
- provide structured interview coaching, feedback, or mock sessions.

Return up to 5 platform names, one per line.
"""

    TOOL_ANALYSIS_SYSTEM = f"""You are analyzing behavioral interview and career coaching tools.

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_analysis_user(self, company_name: str, content: str) -> str:
        return f"""Behavioral Interview / Coaching Tool: {company_name}
Website Content (partial):
{content[:2500]}

Return JSON with:
- pricing_model: "Free", "Freemium", "Paid", "Enterprise", or "Unknown".
- pricing_details: Example pricing info if available.
- description: One sentence describing how it helps with behavioral interviews or career coaching.
- tech_stack: e.g. "web app", "video practice", "AI coach".
- api_available: true/false/null.
- language_support: human languages if mentioned.
- integration_capabilities: e.g. Zoom/Meet integration, LMS integrations, etc.
- target_roles: e.g. "new grads", "managers", "tech roles".
- seniority_focus: e.g. "Entry-level", "Mid-level", "All levels".
- uses_ai_feedback: true if the tool uses AI to give feedback.
- video_practice_supported: true if it supports video mock interviews or recording.
- includes_example_answers: true if it provides model answers or answer templates.

Return valid JSON only.
"""

    RECOMMENDATIONS_SYSTEM = f"""You are a senior career coach helping someone improve
their behavioral interview performance.

{CAREER_PROMPT_GUIDELINES}

Keep replies short and practical.
"""

    def recommendations_user(self, query: str, company_data: str) -> str:
        return f"""Career Query: {query}
Behavioral Interview Tools Analyzed (JSON):
{company_data}

Provide a concise recommendation:
- Which 1-2 tools to use first.
- Who they are best suited for (role/seniority).
- Any cost or time caveats.

Be very concrete and focused on real-world usage.
"""
