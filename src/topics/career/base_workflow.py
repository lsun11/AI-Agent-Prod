# src/topics/career/base_workflow.py
from concurrent.futures import as_completed, ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable
from langgraph.graph import StateGraph, END


from langchain_core.messages import HumanMessage, SystemMessage

from ..tools.base_workflow import CompanyT
# from ..software_engineering.base_workflow import LogCallback
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
    Subclasses customize:
      - state_cls, info_cls, analysis_cls, prompts_cls
      - topic_label
      - article_query_suffix
      - official_site_suffix
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
        # initialize RootWorkflow (sets self.llm and _log_callback)
        super().__init__(
            default_model=model,
            default_temperature=temperature,
        )
        self.prompts = self.prompts_cls()
        self.workflow = self._build_workflow()

    # ---- Graph building ----

    def _build_workflow(self):
        graph = StateGraph(self.state_cls)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()


    # ---- Steps ----
    def _extract_tools_step(self, state: TState) -> Dict[str, Any]:
        self._log(f"Finding articles/resources about: {state.query}")

        article_query = f"{state.query} {self.article_query_suffix}"
        search_results = self.firecrawl.search_companies(article_query, num_results=3)

        # Normalize Firecrawl search results → web_results (list of docs)
        if hasattr(search_results, "web"):
            web_results = search_results.web
        elif isinstance(search_results, dict):
            web_results = search_results.get("web", [])
        else:
            web_results = search_results

        all_content, _ = self._collect_content_from_web_results(web_results)
        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content)),
        ]

        try:
            response = self.llm.invoke(messages)
            tool_names = [
                name.strip()
                for name in response.content.strip().split("\n")
                if name.strip()
            ]
            self._log(f"Extracted tools/platforms: {', '.join(tool_names[:5])}")
            return {"extracted_tools": tool_names}
        except Exception as e:
            self._log(f"Extraction error: {e}")
            return {"extracted_tools": []}

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
        tool_query = f"{tool_name} official site"

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

        # Prefer search markdown if available
        content = getattr(doc, "markdown", None)

        if not content:
            self._log(f"no markdown in search result for {tool_name}, scraping {url}")
            scraped = self.firecrawl.scrape_company_pages(url)
            if scraped and getattr(scraped, "markdown", None):
                content = scraped.markdown

        if content:
            print("Checking:", company.name)
            analysis = self._analyze_company_content(company.name, content)
            print("Done checking:", company.name)
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

        return company

    def _research_step(self, state: TState) -> Dict[str, Any]:
        extracted = getattr(state, "extracted_tools", [])

        if not extracted:
            self._log("⚠️ No extracted tools found, falling back to direct search")
            search_results = self.firecrawl.search_companies(state.query, num_results=4)
            if hasattr(search_results, "web"):
                web_results = search_results.web
            elif isinstance(search_results, dict):
                web_results = search_results.get("web", [])
            else:
                web_results = search_results

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

        max_workers = min(4, len(tool_names))  # cap to avoid too many parallel calls
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

    import json  # make sure this is at the top of the file

    def _analyze_step(self, state: TState) -> Dict[str, Any]:
        self._log("Generating career action plan and recommendations")

        company_data = ", ".join([c.model_dump_json() for c in state.companies])

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data)),
        ]

        structured_llm = self.llm.with_structured_output(CareerActionPlan)

        try:
            plan: CareerActionPlan = structured_llm.invoke(messages)  # type: ignore[assignment]
            self._log("Successfully generated CareerActionPlan")

            goal = CareerGoal(raw_query=state.query)

            return {
                # 🔹 Keep `analysis` as a string – JSON-serialized plan
                #    (your to_document() will parse and pretty-print this)
                "analysis": plan.model_dump_json(indent=2, ensure_ascii=False),
                "plan": plan,
                "goal": goal,
            }

        except Exception as e:
            self._log(f"❌ Error generating CareerActionPlan: {e}")
            # Fallback: plain-text analysis string, as before
            try:
                fallback = self.llm.invoke(messages)
                return {
                    "analysis": fallback.content,
                    "plan": None,
                    "goal": CareerGoal(raw_query=state.query),
                }
            except Exception as inner_e:
                self._log(f"❌ Fallback recommendation error: {inner_e}")
                return {
                    "analysis": "Failed to generate a structured career plan.",
                    "plan": None,
                    "goal": CareerGoal(raw_query=state.query),
                }

    # Public entry
    def run(self, query: str) -> TState:
        initial_state = self.state_cls(query=query)
        final_state = self.workflow.invoke(initial_state)
        return self.state_cls(**final_state)