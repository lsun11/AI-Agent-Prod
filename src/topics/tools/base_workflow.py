# src/topics/base_workflow.py
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Type, TypeVar, Generic, Dict, Any, List, Callable, Optional

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from ...firecrawl import FirecrawlService
from .base_prompts import BaseCSResearchPrompts
from .base_models import BaseResearchState, BaseCompanyInfo, BaseCompanyAnalysis
from pydantic import BaseModel

StateT = TypeVar("StateT", bound=BaseResearchState)
CompanyT = TypeVar("CompanyT", bound=BaseCompanyInfo)
AnalysisT = TypeVar("AnalysisT", bound=BaseCompanyAnalysis)
PromptsT = TypeVar("PromptsT", bound=BaseCSResearchPrompts)
from ..root_workflow import RootWorkflow

class BaseCSWorkflow(RootWorkflow, Generic[StateT, CompanyT, AnalysisT]):
    """
    Generic workflow for CS-product research topics.

    Shared behavior:
    - Search + scrape with Firecrawl
    - Extract product/tool/service names
    - Research specific companies/tools
    - Analyze company content into structured fields
    - Produce final recommendations via LLM
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
        # initialize RootWorkflow (sets self.llm and _log_callback)
        super().__init__(
            default_model=default_model,
            default_temperature=default_temperature,
        )
        self.prompts: PromptsT = self.prompts_cls()
        self.workflow = self._build_workflow()


    # ------------------------------------------------------------------ #
    # Graph setup
    # ------------------------------------------------------------------ #
    def _build_workflow(self):
        graph = StateGraph(self.state_model)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()

    # ------------------------------------------------------------------ #
    # Node: extract_tools
    # ------------------------------------------------------------------ #
    def _extract_tools_step(self, state: StateT) -> Dict[str, Any]:
        self._log(f"Finding articles/resources about: {state.query}")

        article_query = self.article_query_template.format(query=state.query)
        search_results = self.firecrawl.search_companies(article_query, num_results=3)
        print("_extract_tools_step, check0")
        web_results = self._get_web_results(search_results)
        print("_extract_tools_step, check1")
        all_content, _ = self._collect_content_from_web_results(web_results)

        print("_extract_tools_step, check2")
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

            if tool_names:
                self._log(f"Extracted tools/platforms: {', '.join(tool_names[:5])}")
            return {"extracted_tools": tool_names}
        except Exception as e:
            self._log(f"Extraction error: {e}")
            return {"extracted_tools": []}

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
            #print("!!!!!!!!!!!!!!!!!!", analysis)
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

    # ------------------------------------------------------------------ #
    # Node: research
    # ------------------------------------------------------------------ #        ...

    def _apply_analysis_to_company(self, company: CompanyT, analysis: AnalysisT) -> CompanyT:
        """
        Copy any matching fields from the analysis model onto the company model.

        - Only copies fields that exist on `company`.
        - Skips None values so we don't overwrite existing info with empties.
        """
        # Pydantic v2: model_dump; fallback for dict/other
        if isinstance(analysis, BaseModel):
            data = analysis.model_dump()
        elif isinstance(analysis, dict):
            data = analysis
        else:
            data = getattr(analysis, "__dict__", {}) or {}

        # Optional: protect a few identity fields from being overwritten
        protected = {"name", "website"}

        for field_name, value in data.items():
            if value is None:
                continue
            if field_name in protected:
                continue
            if hasattr(company, field_name):
                setattr(company, field_name, value)

        return company


    def _research_single_tool(self, tool_name: str) -> Optional[CompanyT]:
        self._log(f"researching: {tool_name}")
        tool_query = f"{tool_name} (computer software/platform/service/product) official site"

        tool_search_results = self.firecrawl.search_companies(tool_query, num_results=1)
        print("Pre-pre-pre checking", tool_name)
        web_results = self._get_web_results(tool_search_results)
        if not web_results:
            self._log(f"no web results for {tool_name}")
            return None
        print("Pre-pre checking", tool_name)
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
        company: CompanyT = self.company_model(
            name=tool_name,
            description=desc,
            website=url,
            tech_stack=[],
            competitors=[],
        )
        print("Pre checking", company.name)
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
            if getattr(analysis, "description", None):
                company.description = analysis.description
            company = self._apply_analysis_to_company(company, analysis)
        else:
            self._log(f"no content (markdown/scrape) for {tool_name}, skipping analysis")
        print("Finished:", company.name, company)
        return company

    def _research_step(self, state: StateT) -> Dict[str, Any]:
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools:
            self._log("⚠️ No extracted names found, falling back to direct search")
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

        self._log(f"{self.topic_label} 🔬 Researching specific tools/products: {', '.join(tool_names)}")

        companies: List[CompanyT] = []

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

    # ------------------------------------------------------------------ #
    # Node: analyze (final recommendations)
    # ------------------------------------------------------------------ #
    def _analyze_step(self, state: StateT) -> Dict[str, Any]:
        self._log("Generating recommendations")

        company_data = ", ".join(
            [company.model_dump_json() for company in state.companies]
        )

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data)),
        ]

        response = self.llm.invoke(messages)
        return {"analysis": response.content}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def run(self, query: str) -> StateT:
        initial_state = self.state_model(query=query)
        final_state = self.workflow.invoke(initial_state)
        return self.state_model(**final_state)
