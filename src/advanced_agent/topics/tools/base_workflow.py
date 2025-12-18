# src/topics/base_workflow.py
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Type, TypeVar, Generic, Dict, Any, List, Callable, Optional

import json

from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from ...firecrawl import FirecrawlService
from .base_prompts import BaseCSResearchPrompts
from .base_models import (
    BaseResearchState,
    BaseCompanyInfo,
    BaseCompanyAnalysis,
    ToolComparisonRecommendation,
)
from ..root_workflow import RootWorkflow

StateT = TypeVar("StateT", bound=BaseResearchState)
CompanyT = TypeVar("CompanyT", bound=BaseCompanyInfo)
AnalysisT = TypeVar("AnalysisT", bound=BaseCompanyAnalysis)
PromptsT = TypeVar("PromptsT", bound=BaseCSResearchPrompts)


class BaseCSWorkflow(RootWorkflow, Generic[StateT, CompanyT, AnalysisT]):
    """
    Generic workflow for CS-product research topics (tools, platforms, services).

    7-step clean pipeline:

      1) interpret_query           – log / prepare
      2) collect_articles          – multi-pass article search, aggregated_markdown + sources
      3) extract_tools             – extract candidate tool names from aggregated content
      4) research_tools            – per-tool scraping + structured company analysis
      5) extract_knowledge         – global entities/pros/cons/risks/timeline
      6) compare_and_recommend     – structured ToolComparisonRecommendation
      7) generate_analysis         – final human-readable analysis string for UI
    """

    # Subclasses must override these:
    state_model: Type[StateT]
    company_model: Type[CompanyT]
    analysis_model: Type[AnalysisT]
    prompts_cls: Type[PromptsT] = BaseCSResearchPrompts  # default
    topic_label: str = "Tool Search"

    # How to search for comparison articles given the query
    article_query_template: str = "{query} comparison best alternatives"

    def __init__(
        self,
        default_model: str = "gpt-4o-mini",
        default_temperature: float = 0.1,
    ) -> None:
        # initialize RootWorkflow (sets self.llm, knowledge_llm, firecrawl, _log_callback)
        super().__init__(
            default_model=default_model,
            default_temperature=default_temperature,
        )
        self.prompts: PromptsT = self.prompts_cls()
        self.workflow = self._build_workflow()

    # ------------------------------------------------------------------ #
    # Graph setup (7 steps) – now state-in / state-out like SoftwareEng
    # ------------------------------------------------------------------ #
    def _build_workflow(self):
        graph = StateGraph(self.state_model)

        graph.add_node("interpret_query", self._interpret_query_step)
        graph.add_node("collect_articles", self._collect_articles_step)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research_tools", self._research_tools_step)
        graph.add_node("extract_knowledge", self._extract_knowledge_step)
        graph.add_node("compare_and_recommend", self._compare_and_recommend_step)
        graph.add_node("generate_analysis", self._generate_analysis_step)

        graph.set_entry_point("interpret_query")
        graph.add_edge("interpret_query", "collect_articles")
        graph.add_edge("collect_articles", "extract_tools")
        graph.add_edge("extract_tools", "research_tools")
        graph.add_edge("research_tools", "extract_knowledge")
        graph.add_edge("extract_knowledge", "compare_and_recommend")
        graph.add_edge("compare_and_recommend", "generate_analysis")
        graph.set_finish_point("generate_analysis")

        return graph.compile()

    # ------------------------------------------------------------------ #
    # Step 1: interpret_query
    # ------------------------------------------------------------------ #
    def _interpret_query_step(self, state: StateT) -> StateT:
        self._log(f"🔍 Starting tool/product research for query: {state.query}")
        # In the future you can add intent classification here.
        return state

    # ------------------------------------------------------------------ #
    # Step 2: collect_articles – multi-pass Firecrawl search
    # ------------------------------------------------------------------ #
    def _collect_articles_step(self, state: StateT) -> StateT:
        self._log(f"Finding comparison articles/resources about: {state.query}")

        article_query = self.article_query_template.format(query=state.query)
        query_variants = [
            article_query,
            f"{state.query} developer tools overview",
            f"{state.query} SaaS platform comparison",
        ]

        # Multi-pass
        fast = self._is_fast(state)

        merged_content, meta_items = self._multi_pass_articles(
            state.query,
            num_results=3,
            snippet_len=1500,
            query_variants=query_variants,
            fast=fast,
        )

        # Fallback: single search if multi-pass returned nothing
        if not merged_content.strip():
            self._log("Multi-pass search returned no content, falling back to single search.")
            search_results = self.firecrawl.search_companies(article_query, num_results=3)
            web_results = self._get_web_results(search_results)
            merged_content, meta_items = self._collect_content_from_web_results(web_results)

        self._log(f"Collected {len(meta_items)} sources for tools research.")

        return state.model_copy(
            update={
                "aggregated_markdown": merged_content,
                "sources": meta_items,
            }
        )

    # ------------------------------------------------------------------ #
    # Step 3: extract_tools – use LLM to extract candidate tool names
    # ------------------------------------------------------------------ #
    def _extract_tools_step(self, state: StateT) -> StateT:
        content = state.aggregated_markdown or ""

        # If for some reason aggregated_markdown is empty, do a quick direct search.
        if not content.strip():
            self._log("No aggregated article content; doing fallback search to extract tool names.")
            article_query = self.article_query_template.format(query=state.query)
            search_results = self.firecrawl.search_companies(article_query, num_results=3)
            web_results = self._get_web_results(search_results)
            content, _ = self._collect_content_from_web_results(web_results)

        if not content.strip():
            self._log("Still no content found to extract tool names from.")
            return state.model_copy(update={"extracted_tools": []})

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, content)),
        ]

        try:
            response = self.llm.invoke(messages)
            text = response.content if hasattr(response, "content") else str(response)
            tool_names = [
                name.strip()
                for name in text.split("\n")
                if name.strip()
            ]

            if tool_names:
                self._log(f"Extracted tools/platforms: {', '.join(tool_names[:5])}")
            else:
                self._log("No tool names extracted from content.")

            return state.model_copy(update={"extracted_tools": tool_names})
        except Exception as e:
            self._log(f"Extraction error: {e}")
            return state.model_copy(update={"extracted_tools": []})

    # ------------------------------------------------------------------ #
    # Helper: analyze one company's content into structured fields
    # ------------------------------------------------------------------ #
    def _analyze_company_content(self, company_name: str, content: str) -> AnalysisT:
        structured_llm = self.llm.with_structured_output(self.analysis_model)

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content)),
        ]

        try:
            analysis: AnalysisT = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            print(f"{self.topic_label} Error analyzing company content:", e)
            # Fall back to a minimal object
            return self.analysis_model(
                pricing_model="Unknown",
                pricing_details="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Analysis failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[],
            )

    def _apply_analysis_to_company(self, company: CompanyT, analysis: AnalysisT) -> CompanyT:
        """
        Copy any matching fields from the analysis model onto the company model.
        """
        if isinstance(analysis, BaseModel):
            data = analysis.model_dump()
        elif isinstance(analysis, dict):
            data = analysis
        else:
            data = getattr(analysis, "__dict__", {}) or {}

        protected = {"name", "website"}

        for field_name, value in data.items():
            if value is None:
                continue
            if field_name in protected:
                continue
            if hasattr(company, field_name):
                setattr(company, field_name, value)

        return company

    # ------------------------------------------------------------------ #
    # Helper: research a single tool
    # ------------------------------------------------------------------ #
    def _research_single_tool(self, tool_name: str) -> Optional[CompanyT]:
        self._log(f"🔬 Researching: {tool_name}")
        tool_query = f"{tool_name} (computer software/platform/service/product) official site"

        tool_search_results = self.firecrawl.search_companies(tool_query, num_results=1)
        web_results = self._get_web_results(tool_search_results)
        if not web_results:
            self._log(f"No web results for {tool_name}")
            return None

        doc = web_results[0]

        # Basic info from search result
        url = getattr(doc, "url", "") or ""
        desc = ""
        meta = getattr(doc, "metadata", None)
        if meta:
            desc = getattr(meta, "description", "") or desc
            if not url:
                url = getattr(meta, "url", "") or url

        if not url:
            self._log(f"No URL for {tool_name}, skipping.")
            return None

        company: CompanyT = self.company_model(
            name=tool_name,
            description=desc,
            website=url,
            tech_stack=[],
            competitors=[],
        )

        content = getattr(doc, "markdown", None)

        primary_color = None
        brand_colors = None
        logo_url = None

        # Always scrape the official site for richer data + branding
        scraped = self.firecrawl.scrape_company_pages(url)
        if scraped:
            if isinstance(scraped, dict):
                data = scraped.get("data", scraped)
            else:
                data = scraped

            scraped_markdown = (
                data.get("markdown")
                if isinstance(data, dict)
                else getattr(data, "markdown", None)
            )
            if scraped_markdown:
                content = scraped_markdown

            if isinstance(data, dict):
                branding = data.get("branding")
            else:
                branding = getattr(data, "branding", None)

            if branding is not None:
                if isinstance(branding, dict):
                    colors = branding.get("colors")
                    images = branding.get("images")
                else:
                    colors = getattr(branding, "colors", None)
                    images = getattr(branding, "images", None)

                if isinstance(colors, dict) and colors:
                    brand_colors = colors
                    primary_color = colors.get("primary") or primary_color

                if isinstance(images, dict) and images:
                    logo_url = (
                        images.get("favicon")
                        or images.get("ogImage")
                        or images.get("logo")
                        or logo_url
                    )

        # Run LLM analysis if we have content
        if content:
            analysis = self._analyze_company_content(company.name, content)
            if getattr(analysis, "description", None):
                company.description = analysis.description
            company = self._apply_analysis_to_company(company, analysis)
        else:
            self._log(f"No content (markdown/scrape) for {tool_name}, skipping analysis.")

        if primary_color:
            company.primary_color = primary_color
        if brand_colors:
            company.brand_colors = brand_colors
        if logo_url:
            company.logo_url = logo_url

        return company

    # ------------------------------------------------------------------ #
    # Step 4: research_tools – run per-tool research in parallel
    # ------------------------------------------------------------------ #
    def _research_tools_step(self, state: StateT) -> StateT:
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools:
            self._log("⚠️ No extracted names found, falling back to direct search.")
            search_results = self.firecrawl.search_companies(state.query, num_results=4)
            web_results = self._get_web_results(search_results)

            tool_names: List[str] = []
            for doc in web_results:
                meta = getattr(doc, "metadata", None)
                if meta and getattr(meta, "title", None):
                    tool_names.append(meta.title)
            if not tool_names:
                tool_names = ["Unknown"]
        else:
            tool_names = extracted_tools[:4]

        self._log(
            f"{self.topic_label} 🔬 Researching specific tools/products: {', '.join(tool_names)}"
        )

        companies: List[CompanyT] = []

        max_workers = min(4, len(tool_names))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_name = {
                executor.submit(self._research_single_tool, name): name
                for name in tool_names
            }

            for fut in as_completed(future_to_name):
                tool_name = future_to_name[fut]
                try:
                    comp = fut.result()
                    if comp is not None:
                        companies.append(comp)
                except Exception as e:
                    self._log(f"Error while researching {tool_name}: {e}")

        return state.model_copy(update={"companies": companies})

    # ------------------------------------------------------------------ #
    # Step 5: extract_knowledge – global entities/pros/cons/risks/timeline
    # ------------------------------------------------------------------ #
    def _extract_knowledge_step(self, state: StateT) -> StateT:
        # Prefer aggregated_markdown from articles; extend with company info where helpful.
        aggregated = (state.aggregated_markdown or "").strip()
        fast = self._is_fast(state)

        if state.companies:
            parts: List[str] = []
            for c in state.companies:
                parts.append(f"# {c.name}\n{c.description}\n")
                if c.strengths:
                    parts.append("## Strengths\n" + "\n".join(f"- {s}" for s in c.strengths))
                if c.limitations:
                    parts.append("## Limitations\n" + "\n".join(f"- {l}" for l in c.limitations))
            company_block = "\n\n".join(parts).strip()
            if company_block:
                aggregated = (aggregated + "\n\n---\n\n" + company_block) if aggregated else company_block

        if not aggregated:
            self._log("No aggregated content available; skipping knowledge extraction.")
            return state

        result = self._extract_knowledge_from_markdown(
            aggregated_markdown=aggregated,
            prompts=self.prompts,
            fast=fast,
        )
        if result is None:
            return state

        return state.model_copy(update={"knowledge": result})

    # ------------------------------------------------------------------ #
    # Step 6: compare_and_recommend – structured ToolComparisonRecommendation
    # ------------------------------------------------------------------ #
    def _compare_and_recommend_step(self, state: StateT) -> StateT:
        if not state.companies:
            self._log("No companies found; skipping structured recommendation.")
            return state.model_copy(update={"recommendation": None})

        payload = {
            "query": state.query,
            "companies": [c.model_dump() for c in state.companies],
            "knowledge": state.knowledge.model_dump() if state.knowledge else None,
        }
        serialized = json.dumps(payload, ensure_ascii=False)

        structured_llm = self.llm.with_structured_output(ToolComparisonRecommendation)

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, serialized)),
        ]

        try:
            recommendation: ToolComparisonRecommendation = structured_llm.invoke(messages)
            self._log(
                f"Primary choice from recommendation: {recommendation.primary_choice or 'None'}"
            )
            return state.model_copy(update={"recommendation": recommendation})
        except Exception as e:
            self._log(f"Error generating structured recommendation: {e}")
            return state.model_copy(update={"recommendation": None})

    # ------------------------------------------------------------------ #
    # Step 7: generate_analysis – final human-readable text for UI
    # ------------------------------------------------------------------ #
    def _generate_analysis_step(self, state: StateT) -> Dict[str, Any]:
        """
        Build the final markdown/string for the tools workflow.

        - In BOTH fast & deep modes:
            * Overview
            * Detailed per-tool sections
            * Comparison table
            * Recommendations based on ToolComparisonRecommendation

        - In deep mode (fast_mode == False) ONLY:
            * Extra section summarizing structured knowledge
              from state.knowledge (entities, pros, cons, risks, timeline)
        """
        rec = state.recommendation
        companies = state.companies or []
        knowledge = getattr(state, "knowledge", None)
        fast_mode: bool = getattr(state, "fast_mode", True)

        parts: List[str] = []

        # ------------------ Overview ------------------ #
        parts.append("## 📌 Overview")
        if rec and rec.summary:
            parts.append(rec.summary)
        else:
            parts.append(
                f"This report evaluates leading tools/services related to: **{state.query}** "
                "and compares their strengths, limitations, and ideal use cases."
            )
        parts.append("")  # blank line

        # ------------------ Detailed per-company analysis ------------------ #
        if companies:
            parts.append("## 🧩 Detailed Analysis\n")
            for c in companies:
                parts.append(f"### {c.name}")
                if c.website:
                    parts.append(f"- Website: {c.website}")
                if getattr(c, "pricing_model", None):
                    parts.append(f"- Pricing: {c.pricing_model}")
                if getattr(c, "pricing_details", None):
                    parts.append(f"- Pricing Details: {c.pricing_details}")
                if getattr(c, "is_open_source", None) is not None:
                    parts.append(
                        f"- Open Source: {'Yes' if c.is_open_source else 'No'}"
                    )
                if getattr(c, "category", None):
                    parts.append(f"- Category: {c.category}")
                if getattr(c, "primary_use_case", None):
                    parts.append(f"- Primary Use Case: {c.primary_use_case}")
                if getattr(c, "target_users", None):
                    if c.target_users:
                        parts.append(
                            f"- Target Users: {', '.join(c.target_users)}"
                        )
                if getattr(c, "strengths", None):
                    if c.strengths:
                        parts.append(
                            "- Strengths: "
                            + "; ".join(c.strengths)
                        )
                if getattr(c, "limitations", None):
                    if c.limitations:
                        parts.append(
                            "- Limitations: "
                            + "; ".join(c.limitations)
                        )
                if getattr(c, "ideal_for", None):
                    if c.ideal_for:
                        parts.append(
                            "- Ideal For: "
                            + "; ".join(c.ideal_for)
                        )
                if getattr(c, "not_suited_for", None):
                    if c.not_suited_for:
                        parts.append(
                            "- Not Suitable For: "
                            + "; ".join(c.not_suited_for)
                        )
                parts.append("")  # blank line between companies

        # ------------------ Comparison table ------------------ #
        if companies:
            parts.append("### Comparison Table")
            # Header
            header_cells = ["Attribute"] + [c.name for c in companies]
            header = "| " + " | ".join(header_cells) + " |"
            sep = "|" + " --- |" * len(header_cells)
            parts.append(header)
            parts.append(sep)

            def row(label: str, getter):
                row_cells = [label]
                for c in companies:
                    try:
                        val = getter(c) or ""
                    except Exception:
                        val = ""
                    # avoid vertical bars breaking the table
                    val = str(val).replace("|", "\\|")
                    row_cells.append(val)
                parts.append("| " + " | ".join(row_cells) + " |")

            row("Website", lambda c: c.website)
            row("Pricing", lambda c: c.pricing_model or "Unknown")
            row(
                "Open Source",
                lambda c: (
                    "Yes"
                    if c.is_open_source
                    else "No"
                    if c.is_open_source is False
                    else ""
                ),
            )
            row("Category", lambda c: c.category or "")
            row("Primary Use Case", lambda c: c.primary_use_case or "")
            row(
                "Target Users",
                lambda c: ", ".join(c.target_users) if c.target_users else "",
            )

            parts.append("")  # blank line after table

        # ------------------ Recommendations from ToolComparisonRecommendation ------------------ #
        if rec:
            parts.append("## ✅ Recommendations")
            if rec.primary_choice:
                parts.append(
                    f"- **Recommended primary choice:** {rec.primary_choice}"
                )
            elif rec.backup_options:
                parts.append(
                    "- **Recommended primary choice:** (no clear single winner)"
                )

            if rec.backup_options:
                parts.append("\n- **Alternative options:**")
                for alt in rec.backup_options:
                    parts.append(f"  - {alt}")

            if rec.summary:
                parts.append("\n- **Summary:**")
                parts.append(f"  {rec.summary}")

            if rec.selection_criteria:
                parts.append("\n- **Selection criteria to consider:**")
                for c in rec.selection_criteria:
                    parts.append(f"  - {c}")

            if rec.tradeoffs:
                parts.append("\n- **Key trade-offs:**")
                for t in rec.tradeoffs:
                    parts.append(f"  - {t}")

            if rec.step_by_step_decision_guide:
                parts.append("\n- **Step-by-step decision guide:**")
                for step in rec.step_by_step_decision_guide:
                    parts.append(f"  - {step}")

            parts.append("")

        else:
            # If we somehow have no rec but do have companies
            if companies:
                parts.append(
                    "## ✅ Recommendations\n"
                    "Based on the analyzed tools above, choose the option whose strengths "
                    "best match your requirements (budget, tech stack, team experience)."
                )
                parts.append("")

        # ------------------ Deep-only: knowledge graph highlights ------------------ #
        if not fast_mode and knowledge:
            parts.append("## 📚 Knowledge Graph Highlights")

            if knowledge.entities:
                parts.append("### Entities")
                for e in knowledge.entities:
                    t = f" ({e.type})" if getattr(e, "type", None) else ""
                    desc = getattr(e, "description", "") or ""
                    parts.append(f"- **{e.name}**{t}: {desc}")
                parts.append("")

            if getattr(knowledge, "pros", None):
                parts.append("### Pros")
                for p in knowledge.pros:
                    parts.append(f"- {p}")
                parts.append("")

            if getattr(knowledge, "cons", None):
                parts.append("### Cons")
                for c in knowledge.cons:
                    parts.append(f"- {c}")
                parts.append("")

            if getattr(knowledge, "risks", None):
                parts.append("### Risks")
                for r in knowledge.risks:
                    parts.append(f"- {r.text if hasattr(r, 'text') else r}")
                parts.append("")

            if getattr(knowledge, "timeline", None):
                parts.append("### Timeline / Evolution")
                for t in knowledge.timeline:
                    parts.append(f"- {t}")
                parts.append("")

        # Final string
        analysis_text = "\n".join(parts).strip()
        return {"analysis": analysis_text}


    # ------------------------------------------------------------------ #
    # Public API (kept for compatibility – used by chat.py)
    # ------------------------------------------------------------------ #
    def run(self, query: str, fast_mode: bool = True) -> StateT:
        """
        Keeps your existing contract: chat.py calls workflow.run(query).

        Returns a StateT (BaseResearchState subclass) – same as before.
        """
        initial_state = self.state_model(query=query, fast_mode=fast_mode)
        final_state = self.workflow.invoke(initial_state)

        # Handle both dict and model returns safely
        if isinstance(final_state, self.state_model):
            return final_state
        if isinstance(final_state, BaseModel):
            return self.state_model(**final_state.model_dump())
        if isinstance(final_state, dict):
            return self.state_model(**final_state)

        # Fallback: best-effort conversion
        data = getattr(final_state, "model_dump", None)
        if callable(data):
            return self.state_model(**data())
        return self.state_model(**getattr(final_state, "__dict__", {}))
