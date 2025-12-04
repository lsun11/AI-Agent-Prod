# src/saving/layout_llm.py
from __future__ import annotations

import json
from typing import List, Literal, Optional, Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

# -----------------------------
# LLM client
# -----------------------------
layout_llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)

LanguageCode = Literal["Eng", "Chn"]


class Slide(BaseModel):
    title: str = Field(..., description="Slide title (plain text)")
    bullets: List[str] = Field(
        default_factory=list,
        description="Plain text bullets (no markdown, no numbering)",
    )


class DocumentLayout(BaseModel):
    title: str
    report_markdown: str
    slides: List[Slide] = Field(default_factory=list)


# -----------------------------
# Main function
# -----------------------------
def generate_document_and_slides(
        query: str,
        raw_text: str,
        language: LanguageCode = "Chn",
        sources: Optional[List[Dict[str, Any]]] = None,
        entities: Optional[List[Dict[str, Any]]] = None,
) -> DocumentLayout:
    """
    Given some raw analysis text (any format), ask an LLM to:

    1) Rewrite it as a clean, professional Markdown report in the same language.
    2) Produce a simple slide outline (4–8 slides).

    The report_markdown will later be rendered into PDF/DOCX/TXT.
    The slides list will later be rendered into PPTX.
    """

    if language == "Chn":
        lang_label = "Chinese"
        example_sections = (
            "例如可以包含这些章节：\n"
            "## 📌 概览\n"
            "## 🧩 关键要点\n"
            "## 🔍 详细分析\n"
            "## ✅ 建议\n"
            "## 🚀 后续步骤\n"
        )
        bullet_hint = "使用清晰、简短的句子，适合在演示文稿中展示。"
        color_hint = (
            "适当使用二级标题（##）和三级标题（###），并在标题开头加上 Emoji "
            "（例如：📌、🔍、✅、🚀），让报告在导出为 PDF 时既专业又有视觉层次感。"
        )
    else:
        lang_label = "English"
        example_sections = (
            "For example, you might include sections like:\n"
            "## 📌 Overview\n"
            "## 🧩 Key Findings\n"
            "## 🔍 Detailed Analysis\n"
            "## ✅ Recommendations\n"
            "## 🚀 Next Steps\n"
        )
        bullet_hint = "Use short, readable sentences suitable for presentation slides."
        color_hint = (
            "Use second-level headings (##) and third-level headings (###), and you may "
            "prefix section titles with emojis (e.g. 📌, 🔍, ✅, 🚀) so that when the "
            "Markdown is rendered to PDF the document looks structured, colorful, and professional."
        )

    # -----------------------------
    # Build sources description (for citations)
    # -----------------------------
    sources = sources or []
    if sources:
        # Assign stable numeric ids [1], [2], ...
        numbered_sources = []
        for idx, src in enumerate(sources, start=1):
            title = (src.get("title") or "").strip() or f"Source {idx}"
            url = (src.get("url") or "").strip() or ""
            numbered_sources.append((idx, title, url))

        if language == "Chn":
            sources_header = "参考资料（供你添加引用使用）："
        else:
            sources_header = "Reference sources (for you to use as citations):"

        sources_block_lines = [sources_header, ""]
        for idx, title, url in numbered_sources:
            if url:
                sources_block_lines.append(f"[{idx}] {title} — {url}")
            else:
                sources_block_lines.append(f"[{idx}] {title}")
        sources_block = "\n".join(sources_block_lines)
    else:
        sources_block = ""

    # -----------------------------
    # Build the prompt
    # -----------------------------
    prompt = f"""
You are a professional technical writer and slide designer.

The raw analysis text (already in {lang_label}) is:

```RAW_ANALYSIS
{raw_text}

Original user query:
{query}
{sources_block}
Your job is to turn this into a CLEAN, PROFESSIONAL document package.

============================================================
MARKDOWN REPORT

Rewrite and reformat the RAW_ANALYSIS into a well-structured Markdown report
in {lang_label}. The content can be about ANY topic (tools, architecture,
concepts, research, etc.), so adapt the structure to the content.

VERY IMPORTANT LAYOUT RULES (for correct PDF rendering):

DO NOT use top-level "# " headings in report_markdown.

The top title is injected separately by another system.

You MUST NOT start any line with "# ".

Use "## " for main sections and "### " for subsections.

The first line of report_markdown MUST NOT start with "# ".

It can be a short introductory paragraph,
or a "## " heading such as "## 📌 Overview".

All headings should be "## " or "### " only.

No "#", "####", or deeper levels.

You MAY start section titles with an emoji (e.g. "## 📌 Overview")
to make the final PDF more visually appealing while staying professional.

Content & style guidelines:

Keep the language as {lang_label} (do NOT translate).

Use Markdown headings ("##", "###") to organize sections logically.

Use bullet lists where appropriate.

Use bold sparingly for important concepts, terms, or section labels.

DO NOT invent new factual content; everything must come from RAW_ANALYSIS.

You may reorder, merge, or slightly rewrite sentences to improve clarity, flow,
and professionalism.

Remove filler, duplication, and chatty phrases. Make it read like a polished,
structured report that someone would export to PDF.

=== COMPARISON TABLE REQUIREMENTS (VERY IMPORTANT) ===

If RAW_ANALYSIS contains multiple comparable entities (e.g., tools, APIs,
cloud services, frameworks, databases, products), you MUST:

1) KEEP a detailed subsection for EACH entity, in bullet form, with fields like:
   - Website
   - Pricing
   - Features / Capabilities
   - Target Users
   - Strengths
   - Limitations
   - Ideal For / Not Suitable For
   (Use whatever fields are actually present in RAW_ANALYSIS; do NOT delete or
   over-summarize them.)

2) AFTER those per-entity bullet subsections, create ONE OR MORE comparison tables
   that summarize the same information in a compact way.

Rules for comparison tables:

- Use GitHub-flavored Markdown tables.
- The first column is the attribute/feature name.
- Remaining columns are the entity names.
- Only include rows when the information is explicitly available in RAW_ANALYSIS.
- DO NOT invent data. Only reorganize and rewrite what exists.
- Place comparison tables at the end of the Detailed Analysis section, but BEFORE
  any Recommendations / Final Analysis / Next Steps sections.
- If only one entity exists, skip the table entirely.

You may use the provided entity list to help identify comparable items:
{entities}

Structure the document into clear sections such as:
    {example_sections}
    
    {color_hint}
    
Citations rules (VERY IMPORTANT):

When a sentence or paragraph clearly depends on a specific source from the
list above, append a citation marker like [1] or [2] at the END of that
sentence or paragraph (before the final period is also acceptable).

If multiple sources support the same statement, you may combine them, e.g. [1][3].

Only use citation numbers that exist in the source list you were given.

At the END of the report, add a Markdown section:

Sources

And list each source in the form:
[n] Title — URL

Where n is the number of the source in the list. should go from 1 to number of citations.
example: [1] citation 1
         [2] citation 2
         ...

    ============================================================
    SLIDE OUTLINE
    
    Create a slide deck outline that summarizes the key points of the report.
    
    Requirements:
    
    4–8 slides total.
    
    Each slide must be an object with:
    "title": a short, descriptive title (plain text, no markdown, no emojis required)
    "bullets": 3–6 plain-text bullets (no "-", no numbers, no markdown)
    
    Focus slides on:
    
    Overall context or problem
    
    Key findings or main ideas
    
    Important comparisons / options / trade-offs (if any)
    
    Recommendations or conclusions
    
    Possible next steps or implementation ideas
    
    Bullets should be concise and informative. {bullet_hint}
    
    ============================================================
    OUTPUT FORMAT (VERY IMPORTANT)
    
    Return ONLY valid JSON (no comments, no extra text) with this exact schema:
    
    {{
    "title": "<overall title for the report>",
    "report_markdown": "<full markdown report in {lang_label}, including citations and a final ## Sources section if sources were provided>",
    "slides": [
    {{
    "title": "<slide title>",
    "bullets": ["bullet 1", "bullet 2", "..."]
    }},
    ...
    ]
    }}
    """

    # -----------------------------
    # Call LLM
    # -----------------------------
    response = layout_llm.invoke(prompt)
    raw_content = response.content

    # -----------------------------
    # Parse JSON or fall back
    # -----------------------------
    try:
        data = json.loads(raw_content)
        return DocumentLayout.model_validate(data)

    except (json.JSONDecodeError, ValidationError) as e:
        print("generate_document_and_slides: JSON error, fallback used:", e)

        # Minimal usable fallback if the LLM returns bad JSON
        fallback_title = (query or "").strip() or (
            "研究结果" if language == "Chn" else "Research Result"
        )

        if language == "Chn":
            fallback_intro = "以下为原始分析内容的整理版本："
            fallback_bullet = "请查看报告正文以获取详细信息。"
        else:
            fallback_intro = "Below is the cleaned-up version of the original analysis:"
            fallback_bullet = "Please refer to the main report for details."

        # Note: even in fallback, we obey the “no # heading” rule
        # by starting with a "## " section instead of "# ".
        fallback_markdown = (
            f"## 📌 {fallback_title}\n\n"
            f"{fallback_intro}\n\n"
            f"{raw_text}"
        )

        return DocumentLayout(
            title=fallback_title,
            report_markdown=fallback_markdown,
            slides=[
                Slide(
                    title=fallback_title,
                    bullets=[fallback_bullet],
                )
            ],
        )
