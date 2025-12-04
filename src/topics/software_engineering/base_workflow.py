from typing import Dict, Any, Callable, Optional, List, Type

from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from ...firecrawl import FirecrawlService
from .base_models import (
    BaseSoftwareEngState,
    BaseSoftwareEngResourceSummary,
    BaseSoftwareEngRecommendation,
)
from .base_prompts import BaseSoftwareEngPrompts
from ..root_workflow import RootWorkflow

LogCallback = Callable[[str], None]


class BaseSoftwareEngWorkflow(RootWorkflow):
    state_model: Type[BaseSoftwareEngState] = BaseSoftwareEngState
    resource_model: Type[BaseSoftwareEngResourceSummary] = BaseSoftwareEngResourceSummary
    recommendation_model: Type[BaseSoftwareEngRecommendation] = BaseSoftwareEngRecommendation
    prompts_cls: Type[BaseSoftwareEngPrompts] = BaseSoftwareEngPrompts
    topic_label: str = "Software Engineering"
    article_query_template: str = "{query} best practices guide"

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
    ) -> None:
        super().__init__(
            default_model=model,
            default_temperature=temperature,
        )
        self.prompts = self.prompts_cls()
        self.workflow = self._build_workflow()

    # ------------------------------------------------------------------ #
    # Graph setup
    # ------------------------------------------------------------------ #
    def _build_workflow(self):
        graph = StateGraph(self.state_model)
        graph.add_node("extract_resources", self._extract_resources_step)
        graph.add_node("analyze", self._analyze_step)
        graph.add_node("recommend", self._recommend_step)
        graph.set_entry_point("extract_resources")
        graph.add_edge("extract_resources", "analyze")
        graph.add_edge("analyze", "recommend")
        graph.add_edge("recommend", END)
        return graph.compile()

    # ------------------------------------------------------------------ #
    # Node: extract_resources
    # ------------------------------------------------------------------ #
    def _extract_resources_step(self, state: BaseSoftwareEngState) -> Dict[str, Any]:
        self._log(f"Finding articles/resources about: {state.query}")

        article_query = self.article_query_template.format(query=state.query)

        query_variants = [
            article_query,  # keep your original comparison template
            f"{state.query} developer tools overview",
            f"{state.query} SaaS platform comparison",
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

        # Build resource objects with empty branding fields for now
        resources: List[BaseSoftwareEngResourceSummary] = [
            self.resource_model(
                title=(meta.get("title") or "Untitled resource"),
                url=meta.get("url") or "",
                key_points=[],
                concepts=[],
                recommended_tools=[],
                logo_url=None,
                primary_color=None,
                brand_colors=None,
            )
            for meta in meta_items
        ]

        if not merged_content:
            self._log("No content found; continuing with empty extraction.")
            return {"resources": resources, "extracted_keywords": []}

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, merged_content)),
        ]

        try:
            response = self.llm.invoke(messages)
            lines = [
                ln.strip()
                for ln in response.content.split("\n")
                if ln.strip()
            ]
            self._log(f"Extracted keywords/concepts: {', '.join(lines[:10])}")
            return {
                "resources": resources,
                "extracted_keywords": lines,
            }
        except Exception as e:
            self._log(f"Extraction failed: {e}")
            return {"resources": resources, "extracted_keywords": []}

    # ------------------------------------------------------------------ #
    # Node: analyze
    #   - Scrape each resource URL
    #   - Aggregate markdown content
    #   - Populate logo_url / primary_color / brand_colors on each resource
    # ------------------------------------------------------------------ #
    def _analyze_step(self, state: BaseSoftwareEngState) -> Dict[str, Any]:
        self._log("Analyzing aggregated resources")

        combined = ""

        for res in state.resources[:3]:
            if not res.url:
                continue

            scraped = self.firecrawl.scrape_company_pages(res.url)
            if not scraped:
                continue

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
                combined += scraped_markdown[:2000] + "\n\n"

            branding = (
                data.get("branding")
                if isinstance(data, dict)
                else getattr(data, "branding", None)
            )

            local_primary_color = None
            local_brand_colors = None
            local_logo_url = None

            if branding is not None:
                if isinstance(branding, dict):
                    colors = branding.get("colors")
                    images = branding.get("images")
                else:
                    colors = getattr(branding, "colors", None)
                    images = getattr(branding, "images", None)

                if isinstance(colors, dict) and colors:
                    local_brand_colors = colors
                    local_primary_color = colors.get("primary")

                if isinstance(images, dict) and images:
                    local_logo_url = (
                            images.get("favicon")
                            or images.get("ogImage")
                            or images.get("logo")
                    )

            # write back onto this resource
            if local_primary_color:
                res.primary_color = local_primary_color
            if local_brand_colors:
                res.brand_colors = local_brand_colors
            if local_logo_url:
                res.logo_url = local_logo_url

        if not combined:
            self._log("No detailed content to analyze; skipping analysis.")
            # still return resources so they carry branding to final state
            return {"resources": state.resources}

        structured_llm = self.llm.with_structured_output(self.recommendation_model)
        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(self.topic_label, combined)),
        ]
        try:
            analysis = structured_llm.invoke(messages)
            self._log("Analysis step completed")
            # 🔑 return both analysis AND resources
            return {"analysis": analysis, "resources": state.resources}
        except Exception as e:
            self._log(f"Analysis failed: {e}")
            fallback = self.recommendation_model(
                summary="Analysis failed.",
                best_practices=[],
                pitfalls=[],
                suggested_action_plan=[],
            )
            return {"analysis": fallback, "resources": state.resources}

    # ------------------------------------------------------------------ #
    # Node: recommend
    # ------------------------------------------------------------------ #
    def _recommend_step(self, state: BaseSoftwareEngState) -> Dict[str, Any]:
        self._log("Generating final recommendations")

        import json

        resources_json = json.dumps(
            [r.model_dump() for r in state.resources],
            ensure_ascii=False,
        )

        structured_llm = self.llm.with_structured_output(self.recommendation_model)

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(
                content=self.prompts.recommendations_user(
                    state.query,
                    resources_json,
                )
            ),
        ]

        try:
            new_analysis = structured_llm.invoke(messages)
            return {"analysis": new_analysis}
        except Exception as e:
            self._log(f"Recommendation step failed: {e}")
            if state.analysis:
                return {"analysis": state.analysis}
            fallback = self.recommendation_model(
                summary="Recommendation step failed.",
                best_practices=[],
                pitfalls=[],
                suggested_action_plan=[],
            )
            return {"analysis": fallback}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def run(self, query: str) -> BaseSoftwareEngState:
        initial_state = self.state_model(query=query)
        final_state = self.workflow.invoke(initial_state)
        return self.state_model(**final_state)
