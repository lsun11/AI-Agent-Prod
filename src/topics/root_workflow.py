# src/topics/root_workflow.py
from __future__ import annotations
from typing import Optional, Callable, Any, List, Dict, Tuple
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_anthropic import ChatAnthropic
from ..firecrawl import FirecrawlService


class RootWorkflow:
    """
    Root workflow class shared by all specific topic/base workflows.

    Common responsibilities:
    - Hold the primary LLM instance (`self.llm`)
    - Manage log callbacks (`set_log_callback`, `_log`)
    - Switch models dynamically (`set_llm`)
    """

    # Subclasses are expected to define a topic_label if they want nicer logs.
    topic_label: str = "GenericTopic"
    topic_tag: str = "GenericSubTopic"
    def __init__(
        self,
        default_model: str = "gpt-4o-mini",
        default_temperature: float = 0.1,
    ) -> None:
        self.llm = ChatOpenAI(model=default_model, temperature=default_temperature)
        self._log_callback: Optional[Callable[[str], None]] = None
        self.firecrawl = FirecrawlService()

    # ---------------------------
    # LLM switching / configuration
    # ---------------------------
    def set_llm(self, model_name: str, temperature: float) -> None:
        """
        Dynamically change the underlying chat model.

        Subclasses still use `self.llm`, but how it's constructed is centralized here.
        """
        print(f"Setting LLM... model: {model_name} temperature: {temperature}")
        timeout = 20,  # <--- real HTTP timeout in seconds

        if "deepseek" in model_name:
            self.llm = ChatDeepSeek(model=model_name, temperature=temperature, timeout=60, max_retries=1)
        elif "claude" in model_name:
            self.llm = ChatAnthropic(model=model_name, temperature=temperature, timeout=60, max_retries=1)
        else:
            self.llm = ChatOpenAI(model=model_name, temperature=temperature, timeout=100, max_retries=1)

    # ---------------------------
    # Logging
    # ---------------------------
    def set_log_callback(self, cb: Optional[Callable[[str], None]]) -> None:
        """
        Set a callback that will receive log lines (e.g. to stream to UI).
        """
        self._log_callback = cb

    def _log(self, msg: str) -> None:
        """
        Log a message with the topic label. Prints to console and, if set,
        forwards a simplified message to `_log_callback`.
        """
        text = f"[{self.topic_label} - {self.topic_tag}] {msg}"
        print(text)
        if self._log_callback:
            # If you prefer the full text, use `text` instead of `msg`
            self._log_callback(msg)


    # ------------------------------------------------------------------ #
    # Helper: normalize Firecrawl search results
    # ------------------------------------------------------------------ #
    def _get_web_results(self, search_results: Any) -> List[Any]:
        """Normalize Firecrawl search results into a list-like `web_results`."""
        if hasattr(search_results, "web"):
            return search_results.web  # SearchData.web
        if isinstance(search_results, dict):
            # Some docs/examples use dict-like shapes
            return search_results.get("web", []) or search_results.get("data", [])
        if isinstance(search_results, list):
            return search_results
        return []

    # ------------------------------------------------------------------ #
    # Helper: build article context from search results
    # ------------------------------------------------------------------ #
    def _collect_content_from_web_results(
            self,
            web_results: List[Any],
            *,
            snippet_len: int = 1500,
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Normalize `web_results` (Firecrawl docs or dicts), optionally fetch missing
        markdown, and return:

          all_content: concatenated markdown snippets
          meta_items:  list of {"title": str, "url": str}

        No child-specific resource types are used here.
        """

        all_content = ""
        meta_items: List[Dict[str, str]] = []

        for result in web_results:
            markdown: Optional[str] = None
            title = ""
            url = ""

            # -------------------------------
            # 1) Normalize shape: dict vs obj
            # -------------------------------
            if isinstance(result, dict):
                markdown = result.get("markdown")
                title = (result.get("title") or "").strip()
                url = (result.get("url") or "").strip()
            else:
                # Firecrawl-like object
                markdown = getattr(result, "markdown", None)
                meta = getattr(result, "metadata", None)

                if isinstance(meta, dict):
                    title = (meta.get("title") or "").strip()
                    url = (meta.get("url") or "").strip()
                else:
                    title = getattr(meta, "title", "") if meta else ""
                    url = getattr(meta, "url", "") if meta else ""
                    title = title.strip()
                    url = url.strip()

            # ------------------------------------
            # 2) Fallback: fetch/scrape if needed
            # ------------------------------------
            if not markdown and url:
                # Prefer a generic fetch_page if you’ve added MCP:
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
                                title = getattr(getattr(fetched, "metadata", None), "title", "") or title
                # Fallback: direct Firecrawl if still present
                elif hasattr(self, "firecrawl"):
                    scraped = self.firecrawl.scrape_company_pages(url)
                    if scraped and getattr(scraped, "markdown", None):
                        markdown = scraped.markdown

            # ------------------------------------
            # 3) Build combined content
            # ------------------------------------
            if markdown:
                all_content += markdown[:snippet_len] + "\n\n"

            # ------------------------------------
            # 4) Collect simple metadata
            # ------------------------------------
            if url or title:
                meta_items.append({"title": title, "url": url})

        return all_content, meta_items