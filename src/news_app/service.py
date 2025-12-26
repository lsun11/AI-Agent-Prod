from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

from src.news_app.models import NewsReport, NewsArticle
from src.advanced_agent.firecrawl import FirecrawlService
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


@dataclass
class CacheItem:
    value: NewsReport
    expires_at: float


class TTLCache:
    def __init__(self):
        self._store: Dict[str, CacheItem] = {}

    def get(self, key: str) -> Optional[NewsReport]:
        item = self._store.get(key)
        if not item:
            return None
        if time.time() > item.expires_at:
            self._store.pop(key, None)
            return None
        return item.value

    def set(self, key: str, value: NewsReport, ttl_seconds: int) -> None:
        self._store[key] = CacheItem(value=value, expires_at=time.time() + ttl_seconds)


class NewsService:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.cache = TTLCache()

    def _cache_key(self, category: str, lang: str) -> str:
        return f"{category.lower().strip()}:{lang.lower().strip()}"

    def _build_query(self, category: str, lang: str) -> str:
        if lang.lower().startswith("zh"):
            return f"最新 {category} 新闻"
        return f"latest {category} news"

    def _normalize_search_results(self, raw_response: Any) -> List[Any]:
        """
        ✅ FIX: Extract list from Firecrawl v2 'news' or 'web' attributes.
        """
        # 1. If it's already a list, return it
        if isinstance(raw_response, list):
            return raw_response

        # 2. If it's a dict, look for standard keys
        if isinstance(raw_response, dict):
            if "news" in raw_response: return raw_response["news"]
            if "web" in raw_response: return raw_response["web"]
            if "data" in raw_response: return raw_response["data"]
            return []

        # 3. If it's an Object (SDK Class), inspect known attributes
        # Based on your logs: ['news', 'web', 'images', ...]
        if hasattr(raw_response, "news") and raw_response.news:
            return raw_response.news

        if hasattr(raw_response, "web") and raw_response.web:
            return raw_response.web

        if hasattr(raw_response, "data"):
            return raw_response.data

        print("[NewsService] WARN: Could not find 'news', 'web', or 'data' in SearchData object.")
        return []

    def _pick_urls(self, web_results: List[Any], limit: int = 6) -> List[Tuple[str, str]]:
        urls: List[Tuple[str, str]] = []

        print(f"[NewsService] Processing {len(web_results)} raw items...")

        for r in web_results:
            title = ""
            url = ""

            # Dictionary access
            if isinstance(r, dict):
                title = r.get("title", "")
                url = r.get("url", "")
            # Object access
            else:
                # Firecrawl v2 items usually have 'title' and 'url' directly on the object
                title = getattr(r, "title", "")
                url = getattr(r, "url", "")

                # Fallback to metadata if direct access fails
                if not url:
                    meta = getattr(r, "metadata", None)
                    if meta:
                        title = getattr(meta, "title", "")
                        url = getattr(meta, "url", "")

            title = str(title).strip()
            url = str(url).strip()

            if not url:
                continue

            urls.append((title, url))
            if len(urls) >= limit:
                break

        return urls

    def _scrape_urls(self, urls: List[Tuple[str, str]]) -> str:
        chunks: List[str] = []

        for title, url in urls:
            try:
                doc = self.firecrawl.scrape(url)

                markdown = ""
                if isinstance(doc, dict):
                    markdown = doc.get("markdown", "")
                else:
                    markdown = getattr(doc, "markdown", "")

                if not markdown:
                    continue

                markdown = str(markdown).strip()
                chunks.append(f"## SOURCE: {title}\nURL: {url}\nCONTENT:\n{markdown[:2500]}\n")
            except Exception as e:
                print(f"[NewsService] Scrape failed for {url}: {e}")
                continue

        return ("\n---\n".join(chunks)).strip()

    def _extract_with_llm(self, all_content: str, category: str, lang: str) -> NewsReport:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        system_prompt = (
            "You are a professional news editor.\n"
            "Given scraped web page text, extract the top 5 most distinct and important stories.\n"
            "Output STRICT JSON matching: [{'headline': '', 'summary': '', 'source': '', 'url': '', 'date': ''}].\n"
            f"Rules: Today is {current_date}. Prefer recent news. Language: {lang}.\n"
        )

        user_prompt = f"CATEGORY: {category}\n\nSCRAPED CONTENT:\n{all_content[:15000]}"

        try:
            resp = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            raw = resp.content.strip()
            if raw.startswith("```"):
                raw = raw.strip("`").replace("json", "", 1).strip()

            data = json.loads(raw)
            report = NewsReport.model_validate({"category": category, "articles": data})
            report.updated_at_iso = datetime.now(timezone.utc).isoformat()
            return report

        except Exception as e:
            print(f"[NewsService] LLM Extraction failed: {e}")
            return NewsReport(category=category, articles=[])

    def get_news(self, category: str, lang: str = "en", ttl_seconds: int = 3600) -> NewsReport:
        key = self._cache_key(category, lang)
        cached = self.cache.get(key)
        if cached:
            print(f"[NewsService] Serving cached news for {category}")
            return cached

        print(f"[NewsService] Fetching fresh news for {category}...")
        query = self._build_query(category, lang)

        try:
            # 1) Search (Raw Object)
            raw_response = self.firecrawl.search_news(query, num_results=15)

            # 2) Normalize (Handles 'news' and 'web' attributes now)
            web_results = self._normalize_search_results(raw_response)

            # 3) Pick
            urls = self._pick_urls(web_results, limit=5)

            if not urls:
                print(f"[NewsService] WARN: No URLs found. Returning Mock Data.")
                return NewsReport(
                    category=category,
                    updated_at_iso=datetime.now(timezone.utc).isoformat(),
                    articles=[
                        NewsArticle(
                            headline=f"Sample {category.title()} News (Mock)",
                            summary="Real news search returned 0 results. This is a placeholder.",
                            source="System",
                            url="#",
                            date=datetime.now().strftime("%Y-%m-%d")
                        )
                    ]
                )

            # 4) Scrape
            all_content = self._scrape_urls(urls)
            if not all_content:
                print(f"[NewsService] No content scraped for {category}")
                return NewsReport(category=category, articles=[])

            # 5) Extract
            report = self._extract_with_llm(all_content, category, lang)

            # 6) Cache
            self.cache.set(key, report, ttl_seconds)
            return report

        except Exception as e:
            print(f"[NewsService] Fatal error: {e}")
            return NewsReport(category=category, articles=[])