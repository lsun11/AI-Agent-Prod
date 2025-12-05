# src/topics/career/base_workflow.py
from __future__ import annotations

import json
from concurrent.futures import as_completed, ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from ..tools.base_workflow import CompanyT
from .base_models import (
    CareerBaseCompanyAnalysis,
    CareerBaseCompanyInfo,
    CareerBaseResearchState,
    CareerGoal,
    CareerActionPlan,
)
from .base_prompts import CareerBasePrompts, HasToolPrompts
from ..root_workflow import RootWorkflow

TState = TypeVar("TState", bound=CareerBaseResearchState)
TInfo = TypeVar("TInfo", bound=CareerBaseCompanyInfo)
TAnalysis = TypeVar("TAnalysis", bound=CareerBaseCompanyAnalysis)
TPrompts = TypeVar("TPrompts", bound=CareerBasePrompts)


class CareerBaseWorkflow(RootWorkflow, Generic[TState, TInfo, TAnalysis, TPrompts]):
    """
    Generic workflow for career-related topics.

    7-step pipeline:
      1) interpret_query         – normalize goal
      2) collect_articles        – multi-pass article search
      3) extract_tools           – extract platforms/resources
      4) research                – per-platform research
      5) extract_knowledge       – global entities/pros/cons/risks/timeline
      6) analyze                 – structured CareerActionPlan
      7) generate_analysis       – final analysis string (kept JSON for compatibility)
    """

    state_cls: Type[TState] = CareerBaseResearchState  # type: ignore
    info_cls: Type[TInfo] = CareerBaseCompanyInfo      # type: ignore
    analysis_cls: Type[TAnalysis] = CareerBaseCompanyAnalysis  # type: ignore
    prompts_cls: Type[TPrompts] = CareerBasePrompts    # type: ignore

    topic_label: str = "Career"
    article_query_suffix: str = "career tools comparison best alternatives"
    official_site_suffix: str = "official site"

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
    ) -> None:
        super().__init__(default_model=model, default_temperature=temperature)
        self.prompts = self.prompts_cls()
        self.workflow = self._build_workflow()

    # ------------------------------------------------------------------ #
    # Graph building (7 steps)
    # ------------------------------------------------------------------ #
    def _build_workflow(self):
        graph = StateGraph(self.state_cls)

        graph.add_node("interpret_query", self._interpret_query_step)
        graph.add_node("collect_articles", self._collect_articles_step)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("extract_knowledge", self._extract_knowledge_step)
        graph.add_node("analyze", self._analyze_step)
        graph.add_node("generate_analysis", self._generate_analysis_step)

        graph.set_entry_point("interpret_query")
        graph.add_edge("interpret_query", "collect_articles")
        graph.add_edge("collect_articles", "extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "extract_knowledge")
        graph.add_edge("extract_knowledge", "analyze")
        graph.add_edge("analyze", "generate_analysis")
        graph.add_edge("generate_analysis", END)

        return graph.compile()

    # ------------------------------------------------------------------ #
    # Step 1: interpret_query – normalize goal
    # ------------------------------------------------------------------ #
    def _interpret_query_step(self, state: TState) -> Dict[str, Any]:
        self._log(f"🎯 Starting career workflow for query: {state.query}")

        # Minimal: create a CareerGoal shell. You can later replace this
        # with an LLM-based goal interpreter if you want.
        if state.goal is None:
            goal = CareerGoal(raw_query=state.query)
            return {"goal": goal}
        return {}

    # ------------------------------------------------------------------ #
    # Step 2: collect_articles – multi-pass search
    # ------------------------------------------------------------------ #
    def _collect_articles_step(self, state: TState) -> Dict[str, Any]:
        self._log(f"Finding articles/resources about: {state.query}")

        article_query = f"{state.query} {self.article_query_suffix}"
        query_variants = [
            article_query,
            f"{state.query} interview prep platforms comparison",
            f"{state.query} career resources overview",
        ]

        merged_content, meta_items = self._multi_pass_articles(
            state.query,
            num_results=3,
            snippet_len=1500,
            query_variants=query_variants,
        )

        if not merged_content.strip():
            self._log("multi-pass search returned no content, falling back to single search")
            search_results = self.firecrawl.search_companies(article_query, num_results=3)
            web_results = self._get_web_results(search_results)
            merged_content, meta_items = self._collect_content_from_web_results(web_results)

        self._log(f"Collected {len(meta_items)} sources for career research.")
        return {
            "aggregated_markdown": merged_content,
            "sources": meta_items,
        }

    # ------------------------------------------------------------------ #
    # Step 3: extract_tools – extract platforms/resources from content
    # ------------------------------------------------------------------ #
    def _extract_tools_step(self, state: TState) -> Dict[str, Any]:
        merged_content = state.aggregated_markdown or ""

        if not merged_content.strip():
            self._log("No aggregated content to extract platforms from; returning empty list.")
            return {"extracted_tools": []}

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, merged_content)),
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
                self._log(f"Extracted career platforms/resources: {', '.join(tool_names[:5])}")
            else:
                self._log("No platforms/resources extracted from content.")
            return {"extracted_tools": tool_names}
        except Exception as e:
            self._log(f"Extraction error: {e}")
            return {"extracted_tools": []}

    # ------------------------------------------------------------------ #
    # Shared helpers: analyze + research single tool
    # ------------------------------------------------------------------ #
    def _analyze_company_content(self, name: str, content: str) -> TAnalysis:
        structured_llm = self.llm.with_structured_output(self.analysis_cls)

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(name, content)),
        ]
        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            self._log(f"Analysis error for {name}: {e}")
            # Provide a minimal default
            return self.analysis_cls(
                pricing_model="Unknown",
                pricing_details=None,
                is_open_source=None,
                tech_stack=[],
                description="Analysis failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[],
                target_roles=[],
                seniority_focus=None,
            )

    def _research_single_tool(self, tool_name: str) -> Optional[CompanyT]:
        self._log(f"researching: {tool_name}")
        tool_query = f"{tool_name} {self.official_site_suffix}"

        tool_search_results = self.firecrawl.search_companies(tool_query, num_results=1)
        web_results = self._get_web_results(tool_search_results)

        if not web_results:
            self._log(f"no web results for {tool_name}")
            return None

        doc = web_results[0]

        url = getattr(doc, "url", "") or ""
        desc = ""

        meta = getattr(doc, "metadata", None)
        if meta:
            desc = getattr(meta, "description", "") or desc
            if not url:
                url = getattr(meta, "url", "") or url

        if not url:
            self._log(f"no URL for {tool_name}, skipping")
            return None

        company = self.info_cls(  # type: ignore
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

        if not content:
            self._log(f"no markdown in search result for {tool_name}, scraping {url}")
            scraped = self.firecrawl.scrape_company_pages(url)
            if scraped and getattr(scraped, "markdown", None):
                content = scraped.markdown

        if content:
            self._log(f"Checking: {company.name}")
            analysis = self._analyze_company_content(company.name, content)
            self._log(f"Done checking: {company.name}")
            company.pricing_model = analysis.pricing_model
            company.pricing_details = analysis.pricing_details
            company.is_open_source = analysis.is_open_source
            company.tech_stack = analysis.tech_stack
            company.description = analysis.description
            company.api_available = analysis.api_available
            company.language_support = analysis.language_support
            company.integration_capabilities = analysis.integration_capabilities
            company.target_roles = analysis.target_roles
            company.seniority_focus = analysis.seniority_focus
        else:
            self._log(f"no content (markdown/scrape) for {tool_name}, skipping analysis")

        if primary_color:
            company.primary_color = primary_color
        if brand_colors:
            company.brand_colors = brand_colors
        if logo_url:
            company.logo_url = logo_url

        return company

    # ------------------------------------------------------------------ #
    # Step 4: research – per-platform research (parallel)
    # ------------------------------------------------------------------ #
    def _research_step(self, state: TState) -> Dict[str, Any]:
        extracted = getattr(state, "extracted_tools", [])

        if not extracted:
            self._log("⚠️ No extracted tools found, falling back to direct search")
            search_results = self.firecrawl.search_companies(state.query, num_results=4)
            web_results = self._get_web_results(search_results)

            tool_names = [
                getattr(doc, "metadata", None).title
                if getattr(doc, "metadata", None) and getattr(doc.metadata, "title", None)
                else getattr(doc, "title", None) or "Unknown"
                for doc in web_results
            ]
        else:
            tool_names = extracted[:4]

        self._log(f"🔬 Researching specific resources: {', '.join(tool_names)}")

        companies: List[TInfo] = []

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
                    self._log(f"error while researching {tool_name}: {e}")
        return {"companies": companies}

    # ------------------------------------------------------------------ #
    # Step 5: extract_knowledge – global entities/pros/cons/risks/timeline
    # ------------------------------------------------------------------ #
    def _extract_knowledge_step(self, state: TState) -> Dict[str, Any]:
        aggregated = (state.aggregated_markdown or "").strip()

        if state.companies:
            blocks: List[str] = []
            for c in state.companies:
                blocks.append(f"# {c.name}\n{c.description}\n")
            company_block = "\n\n".join(blocks).strip()
            if company_block:
                aggregated = (aggregated + "\n\n---\n\n" + company_block) if aggregated else company_block

        if not aggregated:
            self._log("No aggregated content available; skipping knowledge extraction.")
            return {}

        result = self._extract_knowledge_from_markdown(
            aggregated_markdown=aggregated,
            prompts=self.prompts,
        )
        if result is None:
            return {}

        return {"knowledge": result}

    # ------------------------------------------------------------------ #
    # Step 6: analyze – structured CareerActionPlan (kept mostly as-is)
    # ------------------------------------------------------------------ #
    def _analyze_step(self, state: TState) -> Dict[str, Any]:
        self._log("Generating career action plan and recommendations")

        # Include companies + knowledge (if present) in the payload
        payload = {
            "companies": [c.model_dump() for c in state.companies],
            "knowledge": state.knowledge.model_dump() if state.knowledge else None,
        }
        company_data = json.dumps(payload, ensure_ascii=False)

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data)),
        ]

        structured_llm = self.llm.with_structured_output(CareerActionPlan)

        try:
            plan: CareerActionPlan = structured_llm.invoke(messages)  # type: ignore[assignment]
            self._log("Successfully generated CareerActionPlan")

            goal = state.goal or CareerGoal(raw_query=state.query)

            return {
                # Keep analysis as JSON string for compatibility with existing to_document()
                "analysis": plan.model_dump_json(indent=2, ensure_ascii=False),
                "plan": plan,
                "goal": goal,
            }

        except Exception as e:
            self._log(f"❌ Error generating CareerActionPlan: {e}")
            try:
                fallback = self.llm.invoke(messages)
                goal = state.goal or CareerGoal(raw_query=state.query)
                return {
                    "analysis": getattr(fallback, "content", str(fallback)),
                    "plan": None,
                    "goal": goal,
                }
            except Exception as inner_e:
                self._log(f"❌ Fallback recommendation error: {inner_e}")
                goal = state.goal or CareerGoal(raw_query=state.query)
                return {
                    "analysis": "Failed to generate a structured career plan.",
                    "plan": None,
                    "goal": goal,
                }

    # ------------------------------------------------------------------ #
    # Step 7: generate_analysis – final analysis string (no-op for now)
    # ------------------------------------------------------------------ #
    def _generate_analysis_step(self, state: TState) -> Dict[str, Any]:
        """
        For now, keep analysis as returned by _analyze_step (JSON string or fallback text).
        This step exists to match the 7-step pipeline and can later be extended
        to build a human-readable summary or markdown document if needed.
        """
        # You could, for example, wrap the JSON in a markdown code block,
        # or generate a short natural-language summary from `state.plan`.
        return {}

    # ------------------------------------------------------------------ #
    # Public entry – used by chat.py
    # ------------------------------------------------------------------ #
    def run(self, query: str) -> TState:
        initial_state = self.state_cls(query=query)
        final_state = self.workflow.invoke(initial_state)
        return self.state_cls(**final_state)
