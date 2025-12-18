# src/topics/career/resume_tools/base_prompts.py

from ..base_prompts import CareerBasePrompts, CAREER_PROMPT_GUIDELINES


class ResumeToolsPrompts(CareerBasePrompts):
    """
    Prompts specialized for Resume Optimization & ATS Tools.
    """

    TOOL_EXTRACTION_SYSTEM = f"""You are a career research assistant focused on resume optimization
and ATS-friendly resume tools (resume builders, keyword checkers, etc.).

Your job is to extract specific platforms/tools that help users:
- build resumes,
- optimize resumes for ATS,
- match resumes to job descriptions.

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_extraction_user(self, query: str, content: str) -> str:
        return f"""Career Query: {query}
Article Content:
{content}

Extract platforms/services that are clearly resume-related, such as:
- resume builders,
- ATS checkers,
- keyword optimization tools,
- resume templates with AI suggestions.

Rules:
- Only include actual product/platform names (e.g. "Jobscan", "Teal", "Resume.io").
- Exclude generic advice or generic phrases like "use an ATS-friendly resume".
- Limit to the 5 most relevant tools.
- Return just the names, one per line.
"""

    TOOL_ANALYSIS_SYSTEM = f"""You are analyzing resume optimization / ATS tools.
Focus on how the tool helps someone improve their resume and get past ATS filters.

{CAREER_PROMPT_GUIDELINES}
"""

    def tool_analysis_user(self, company_name: str, content: str) -> str:
        return f"""Resume Tool: {company_name}
Website Content (partial):
{content[:2500]}

Analyze this resume/ATS tool and provide:
- pricing_model: One of "Free", "Freemium", "Paid", "Enterprise", or "Unknown".
- pricing_details: Any concrete pricing info (e.g. "Free tier + Pro from $19/month").
- description: One sentence on how it helps with resumes/ATS.
- tech_stack: Generic tech descriptor (e.g. "Web app", "Chrome extension", "Mobile app") if mentioned.
- api_available: true if they mention an API or integration for companies; false or null otherwise.
- language_support: List of supported human languages if mentioned.
- integration_capabilities: List of integrations (e.g. "LinkedIn", "Indeed", "Google Drive").
- target_roles: Roles they explicitly target, if any (e.g. "software engineers", "students", "managers").
- seniority_focus: Short string like "Students/entry-level", "All levels", etc.
- ats_friendly: true if they explicitly emphasize ATS friendliness.
- resume_formats_supported: Formats like ["PDF", "DOCX"] if mentioned.
- keyword_optimization_support: true if they explicitly optimize keywords vs job descriptions.

Return a valid JSON object only.
"""

    RECOMMENDATIONS_SYSTEM = f"""You are a senior career coach specializing in resume optimization.
You will recommend resume/ATS tools that best fit the user's needs.

{CAREER_PROMPT_GUIDELINES}

Keep responses brief (3-4 sentences).
"""

    def recommendations_user(self, query: str, company_data: str) -> str:
        return f"""Career Query: {query}
Resume Tools Analyzed (JSON):
{company_data}

Provide a concise recommendation:
- Which 1-2 tools are best for this person and why.
- Any important pricing or limitations.
- Which roles/seniority levels they are best for.

Do not repeat long marketing copy. Be practical and direct.
"""
