# src/topics/root_workflow.py
from __future__ import annotations
from typing import Optional, Callable, Any, List, Dict, Tuple
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from ..firecrawl import FirecrawlService
from urllib.parse import urlparse


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

        if "gpt" in model_name:
            self.llm = ChatOpenAI(model=model_name, temperature=temperature, timeout=100, max_retries=1)
        elif "deepseek" in model_name:
            self.llm = ChatDeepSeek(model=model_name, temperature=temperature, timeout=100, max_retries=1)
        elif "claude" in model_name:
            self.llm = ChatAnthropic(model=model_name, temperature=temperature, timeout=100, max_retries=1)
        else:
            self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature, timeout=100, max_retries=1)

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
                    raw_title = getattr(meta, "title", None)
                    raw_url = getattr(meta, "url", None)

                    title = (raw_title or "").strip()
                    url = (raw_url or "").strip()

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
    # ------------------------------------------------------------------ #
    # Helper: dedupe meta items (by URL + title)
    # ------------------------------------------------------------------ #
    def _dedupe_meta_items(self, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Deduplicate simple metadata items from multiple passes:
        - Canonicalize URL (scheme+netloc+path, ignore fragments/most params)
        - fallback: domain + normalized title

        Keep the first occurrence (you can tweak this later if you want
        to prefer certain passes).
        """
        seen_url_keys = set()
        seen_domain_title = set()
        deduped: List[Dict[str, str]] = []

        def canon_url(url: str) -> str:
            if not url:
                return ""
            parsed = urlparse(url)
            # Lowercase host + scheme; keep path; drop fragment
            scheme = (parsed.scheme or "").lower()
            netloc = (parsed.netloc or "").lower()
            path = parsed.path or ""
            return f"{scheme}://{netloc}{path}"

        def norm_title(title: str) -> str:
            t = (title or "").strip().lower()
            # collapse whitespace
            import re
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

            # fallback: domain + normalized title
            if url:
                parsed = urlparse(url)
                domain = (parsed.netloc or "").lower()
            else:
                domain = ""

            t_norm = norm_title(title)
            if domain or t_norm:
                key_dt = (domain, t_norm)
                if key_dt in seen_domain_title:
                    continue
                seen_domain_title.add(key_dt)
                deduped.append(item)
                continue

            # no usable key -> just keep it
            deduped.append(item)

        return deduped

    # ------------------------------------------------------------------ #
    # Helper: multi-pass article search + dedup
    # ------------------------------------------------------------------ #
    def _multi_pass_articles(
        self,
        query: str,
        *,
        num_results: int = 3,
        snippet_len: int = 1500,
        query_variants: Optional[List[str]] = None,
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Multi-pass web search for *articles/resources* related to `query`.

        Strategy:
        - Run several related queries (passes)
        - For each pass, run `firecrawl.search_companies(...)`
        - Use `_get_web_results` + `_collect_content_from_web_results`
        - Deduplicate metadata (URLs/titles)
        - Merge content blocks into a single markdown string

        Returns:
            merged_content: str   # concatenated markdown from all passes
            meta_items: List[{"title": ..., "url": ...}]  # deduped sources
        """
        if query_variants is None:
            # Default: 3-pass strategy focused on comparison & alternatives
            query_variants = [
                "{query} comparison best alternatives",
                "{query} vs competitors overview",
                "{query} pros and cons review",
            ]

        all_content_blocks: List[str] = []
        all_meta_items: List[Dict[str, str]] = []

        for idx, tmpl in enumerate(query_variants):
            pass_query = tmpl.format(query=query)
            self._log(f"Multi-pass search [pass {idx+1}/{len(query_variants)}]: {pass_query}")

            try:
                search_results = self.firecrawl.search_companies(
                    pass_query,
                    num_results=num_results,
                )
            except Exception as e:
                self._log(f"multi-pass search error in pass {idx+1}: {e}")
                continue

            web_results = self._get_web_results(search_results)
            if not web_results:
                self._log(f"multi-pass search pass {idx+1}: no web results")
                continue

            pass_content, pass_meta = self._collect_content_from_web_results(
                web_results,
                snippet_len=snippet_len,
            )

            if pass_content.strip():
                # Tag each block with a small header, useful if you ever debug the merged context
                header = f"### Pass {idx+1}: {pass_query}\n\n"
                all_content_blocks.append(header + pass_content.strip())

            all_meta_items.extend(pass_meta)

        deduped_meta = self._dedupe_meta_items(all_meta_items)

        merged_content = "\n\n---\n\n".join(all_content_blocks).strip()

        return merged_content, deduped_meta
