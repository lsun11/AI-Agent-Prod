# src/topics/root_workflow.py
from __future__ import annotations
from typing import Optional, Callable, Any, List, Dict, Tuple, Type, TypeVar, Generic
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from ..firecrawl import FirecrawlService
from .root_prompts import BaseRootPrompts
from .knowledge_extraction import KnowledgeExtractionResult

from urllib.parse import urlparse
import re


StateT = TypeVar("StateT", bound=BaseModel)

class RootWorkflow(Generic[StateT]):
    topic_label: str = "GenericTopic"
    topic_tag: str = "GenericSubTopic"

    def __init__(
        self,
        default_model: str = "gpt-4o-mini",
        default_temperature: float = 0.1,
    ) -> None:
        self.llm = ChatOpenAI(model=default_model, temperature=default_temperature)
        self.knowledge_llm = self.llm.with_structured_output(KnowledgeExtractionResult)
        self._log_callback: Optional[Callable[[str], None]] = None
        self.firecrawl = FirecrawlService()

    # ---------------------------
    # LLM switching / configuration
    # ---------------------------
    def set_llm(self, model_name: str, temperature: float) -> None:
        print(f"Setting LLM... model: {model_name} temperature: {temperature}")

        if "gpt" in model_name:
            self.llm = ChatOpenAI(model=model_name, temperature=temperature, timeout=100, max_retries=1)
        elif "deepseek" in model_name:
            self.llm = ChatDeepSeek(model=model_name, temperature=temperature, timeout=100, max_retries=1)
        elif "claude" in model_name:
            self.llm = ChatAnthropic(model=model_name, temperature=temperature, timeout=100, max_retries=1)
        else:
            self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature, timeout=100, max_retries=1)

        self.knowledge_llm = self.llm.with_structured_output(KnowledgeExtractionResult)

    # ---------------------------
    # Logging
    # ---------------------------
    def set_log_callback(self, cb: Optional[Callable[[str], None]]) -> None:
        self._log_callback = cb

    def _log(self, msg: str) -> None:
        text = f"[{self.topic_label} - {self.topic_tag}] {msg}"
        print(text)
        if self._log_callback:
            self._log_callback(msg)

    # ---------------------------
    # Shared knowledge extraction helper
    # ---------------------------
    def _extract_knowledge_from_markdown(
        self,
        aggregated_markdown: str,
        prompts: BaseRootPrompts,
    ) -> Optional[KnowledgeExtractionResult]:
        if not aggregated_markdown or not aggregated_markdown.strip():
            return None

        self._log("Running knowledge extraction...")
        user_msg = prompts.knowledge_extraction_user(aggregated_markdown)

        result: KnowledgeExtractionResult = self.knowledge_llm.invoke(
            [
                {"role": "system", "content": prompts.KNOWLEDGE_EXTRACTION_SYSTEM},
                {"role": "user", "content": user_msg},
            ]
        )

        self._log(
            f"Knowledge extraction done: "
            f"{len(result.entities)} entities, "
            f"{len(result.relationships)} relationships, "
            f"{len(result.pros)} pros, "
            f"{len(result.cons)} cons, "
            f"{len(result.risks)} risks, "
            f"{len(result.timeline)} timeline items."
        )
        return result

    # ------------------------------------------------------------------ #
    # Firecrawl helpers (same as you already have, shortened for brevity)
    # ------------------------------------------------------------------ #
    def _get_web_results(self, search_results: Any) -> List[Any]:
        if hasattr(search_results, "web"):
            return search_results.web
        if isinstance(search_results, dict):
            return search_results.get("web", []) or search_results.get("data", [])
        if isinstance(search_results, list):
            return search_results
        return []

    def _collect_content_from_web_results(
        self,
        web_results: List[Any],
        *,
        snippet_len: int = 1500,
    ) -> Tuple[str, List[Dict[str, str]]]:
        all_content = ""
        meta_items: List[Dict[str, str]] = []

        for result in web_results:
            markdown: Optional[str] = None
            title = ""
            url = ""

            if isinstance(result, dict):
                markdown = result.get("markdown")
                title = (result.get("title") or "").strip()
                url = (result.get("url") or "").strip()
            else:
                markdown = getattr(result, "markdown", None)
                meta = getattr(result, "metadata", None)

                if isinstance(meta, dict):
                    title = (meta.get("title") or "").strip()
                    url = (meta.get("url") or "").strip()
                else:
                    raw_title = getattr(meta, "title", None)
                    raw_url = getattr(meta, "url", None)
                    title = (raw_title or "").strip()
                    url = (raw_url or "").strip()

            if not markdown and url:
                if hasattr(self, "fetch_page"):
                    fetched = self.fetch_page(url)
                    if fetched:
                        if isinstance(fetched, dict):
                            markdown = fetched.get("markdown") or ""
                            if not title:
                                title = (fetched.get("title") or "").strip()
                        else:
                            markdown = getattr(fetched, "markdown", None)
                            if not title:
                                meta2 = getattr(fetched, "metadata", None)
                                if meta2:
                                    title = getattr(meta2, "title", "") or title
                elif hasattr(self, "firecrawl"):
                    scraped = self.firecrawl.scrape_company_pages(url)
                    if scraped and getattr(scraped, "markdown", None):
                        markdown = scraped.markdown

            if markdown:
                all_content += markdown[:snippet_len] + "\n\n"

            if url or title:
                meta_items.append({"title": title, "url": url})

        return all_content, meta_items

    def _dedupe_meta_items(self, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        seen_url_keys = set()
        seen_domain_title = set()
        deduped: List[Dict[str, str]] = []

        def canon_url(url: str) -> str:
            if not url:
                return ""
            parsed = urlparse(url)
            scheme = (parsed.scheme or "").lower()
            netloc = (parsed.netloc or "").lower()
            path = parsed.path or ""
            return f"{scheme}://{netloc}{path}"

        def norm_title(title: str) -> str:
            t = (title or "").strip().lower()
            return re.sub(r"\s+", " ", t)

        for item in items:
            title = (item.get("title") or "").strip()
            url = (item.get("url") or "").strip()

            key_url = canon_url(url)
            if key_url:
                if key_url in seen_url_keys:
                    continue
                seen_url_keys.add(key_url)
                deduped.append(item)
                continue

            domain = ""
            if url:
                parsed = urlparse(url)
                domain = (parsed.netloc or "").lower()

            t_norm = norm_title(title)
            if domain or t_norm:
                key_dt = (domain, t_norm)
                if key_dt in seen_domain_title:
                    continue
                seen_domain_title.add(key_dt)
                deduped.append(item)
                continue

            deduped.append(item)

        return deduped

    def _multi_pass_articles(
        self,
        query: str,
        *,
        num_results: int = 3,
        snippet_len: int = 1500,
        query_variants: Optional[List[str]] = None,
    ) -> Tuple[str, List[Dict[str, str]]]:
        if query_variants is None:
            query_variants = [
                "{query} comparison best practices",
                "{query} architecture vs alternatives",
                "{query} pros and cons",
            ]

        all_content_blocks: List[str] = []
        all_meta_items: List[Dict[str, str]] = []

        for idx, tmpl in enumerate(query_variants):
            pass_query = tmpl.format(query=query)
            self._log(f"Multi-pass search [pass {idx+1}/{len(query_variants)}]: {pass_query}")

            try:
                web_results = self.firecrawl.search_companies(pass_query, num_results=num_results)
            except Exception as e:
                self._log(f"multi-pass search error in pass {idx+1}: {e}")
                continue

            ### web_results = self._get_web_results(search_results)
            if not web_results:
                self._log(f"multi-pass search pass {idx+1}: no web results")
                continue

            pass_content, pass_meta = self._collect_content_from_web_results(
                web_results,
                snippet_len=snippet_len,
            )

            if pass_content.strip():
                header = f"### Pass {idx+1}: {pass_query}\n\n"
                all_content_blocks.append(header + pass_content.strip())

            all_meta_items.extend(pass_meta)

        deduped_meta = self._dedupe_meta_items(all_meta_items)
        merged_content = "\n\n---\n\n".join(all_content_blocks).strip()
        return merged_content, deduped_meta

    # ---------------------------
    # Public entrypoint: run a full workflow
    # ---------------------------
    def run(self, query: str) -> StateT:
        """
        Main entrypoint used by chat.py and other callers.

        - Builds an initial state from the query using the topic-specific state_model
        - Invokes the compiled LangGraph workflow
        - Normalizes the final result back into the correct state_model type
        """
        if not hasattr(self, "state_model"):
            raise RuntimeError("state_model is not set on this workflow.")
        if self.workflow is None:
            raise RuntimeError("workflow is not built/compiled on this workflow.")

        # 1) build initial state
        initial_state: StateT = self.state_model(query=query)

        # 2) run the graph
        final_state = self.workflow.invoke(initial_state)

        # 3) normalize output
        # LangGraph may return:
        # - an instance of the state model
        # - a plain dict
        # - another BaseModel
        if isinstance(final_state, self.state_model):
            return final_state  # type: ignore[return-value]

        if isinstance(final_state, dict):
            return self.state_model(**final_state)  # type: ignore[call-arg,return-value]

        if isinstance(final_state, BaseModel):
            # Other BaseModel: use its dict
            return self.state_model(**final_state.dict())  # type: ignore[call-arg,return-value]

        # Fallback: try to treat it as mapping-like
        try:
            return self.state_model(**dict(final_state))  # type: ignore[call-arg,return-value]
        except Exception as e:
            raise RuntimeError(f"Unexpected workflow result type: {type(final_state)}") from e
