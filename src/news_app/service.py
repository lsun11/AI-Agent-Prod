from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

from src.news_app.models import NewsReport, NewsArticle
from src.advanced_agent.firecrawl import FirecrawlService
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ✅ CONSTANTS
CACHE_FILE = "news_cache.json"


@dataclass
class CacheItem:
    value: Dict  # Store as dict for JSON serialization
    expires_at: float


class PersistentCache:
    def __init__(self, filename: str = CACHE_FILE):
        self.filename = filename
        self._store: Dict[str, CacheItem] = {}
        self._load_from_disk()

    def _load_from_disk(self):
        """Load cache from JSON file on startup."""
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    # Restore items, discard if expired already
                    if v["expires_at"] > time.time():
                        self._store[k] = CacheItem(value=v["value"], expires_at=v["expires_at"])
            print(f"[Cache] Loaded {len(self._store)} valid items from disk.")
        except Exception as e:
            print(f"[Cache] Failed to load cache: {e}")

    def _save_to_disk(self):
        """Save current in-memory store to JSON file."""
        try:
            # Convert CacheItems to simple dicts
            serializable = {
                k: {"value": v.value, "expires_at": v.expires_at}
                for k, v in self._store.items()
            }
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2)
        except Exception as e:
            print(f"[Cache] Failed to save cache: {e}")

    def get(self, key: str) -> Optional[NewsReport]:
        item = self._store.get(key)
        if not item:
            return None

        # Check expiry
        if time.time() > item.expires_at:
            self._store.pop(key, None)
            self._save_to_disk()  # Cleanup disk
            return None

        # Reconstruct Pydantic model from dict
        try:
            return NewsReport.model_validate(item.value)
        except:
            return None

    def set(self, key: str, value: NewsReport, ttl_seconds: int) -> None:
        # Store as dict (Pydantic .model_dump()) so it's JSON serializable
        self._store[key] = CacheItem(
            value=value.model_dump(),
            expires_at=time.time() + ttl_seconds
        )
        self._save_to_disk()


class NewsService:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.cache = PersistentCache()  # ✅ Use new persistent cache

    def _cache_key(self, category: str, lang: str) -> str:
        return f"{category.lower().strip()}:{lang.lower().strip()}"

    def _build_query(self, category: str, lang: str) -> str:
        if lang.lower().startswith("zh"):
            return f"最新 {category} 新闻"
        return f"latest {category} news"

    def _normalize_search_results(self, raw_response: Any) -> List[Any]:
        if isinstance(raw_response, list):
            return raw_response
        if isinstance(raw_response, dict):
            if "news" in raw_response: return raw_response["news"]
            if "web" in raw_response: return raw_response["web"]
            if "data" in raw_response: return raw_response["data"]
            return []

        # Object inspection
        if hasattr(raw_response, "news") and raw_response.news:
            return raw_response.news
        if hasattr(raw_response, "web") and raw_response.web:
            return raw_response.web
        if hasattr(raw_response, "data"):
            return raw_response.data

        return []

    def _pick_urls(self, web_results: List[Any], limit: int = 6) -> List[Tuple[str, str]]:
        urls: List[Tuple[str, str]] = []
        for r in web_results:
            title = ""
            url = ""
            if isinstance(r, dict):
                title = r.get("title", "")
                url = r.get("url", "")
            else:
                title = getattr(r, "title", "")
                url = getattr(r, "url", "")
                if not url:
                    meta = getattr(r, "metadata", None)
                    if meta:
                        title = getattr(meta, "title", "")
                        url = getattr(meta, "url", "")

            title = str(title).strip()
            url = str(url).strip()

            if not url: continue
            if "google.com" in url or "bing.com" in url: continue

            urls.append((title, url))
            if len(urls) >= limit: break

        return urls

    def _scrape_urls(self, urls: List[Tuple[str, str]]) -> str:
        chunks: List[str] = []
        for title, url in urls:
            try:
                # Direct wrapper or SDK call
                if hasattr(self.firecrawl, 'scrape'):
                    doc = self.firecrawl.scrape(url)
                else:
                    try:
                        doc = self.firecrawl.app.scrape_url(url, params={'formats': ['markdown']})
                    except AttributeError:
                        doc = self.firecrawl.app.scrape(url)

                markdown = ""
                if isinstance(doc, dict):
                    markdown = doc.get("markdown", "")
                else:
                    markdown = getattr(doc, "markdown", "")

                if not markdown: continue

                chunks.append(f"## SOURCE: {title}\nURL: {url}\nCONTENT:\n{str(markdown)[:2500]}\n")
            except Exception:
                continue

        return ("\n---\n".join(chunks)).strip()

    def _extract_with_llm(self, all_content: str, category: str, lang: str) -> NewsReport:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        system_prompt = (
            "You are a professional news editor. Extract top 5 distinct stories.\n"
            "Output STRICT JSON: [{'headline': '', 'summary': '', 'source': '', 'url': '', 'date': ''}].\n"
            f"Rules: Today is {current_date}. Language: {lang}.\n"
        )
        user_prompt = f"CATEGORY: {category}\n\nSCRAPED CONTENT:\n{all_content[:15000]}"

        try:
            resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            raw = resp.content.strip()
            if raw.startswith("```"):
                raw = raw.strip("`").replace("json", "", 1).strip()
            data = json.loads(raw)
            report = NewsReport.model_validate({"category": category, "articles": data})
            report.updated_at_iso = datetime.now(timezone.utc).isoformat()
            return report
        except Exception as e:
            print(f"[NewsService] LLM Error: {e}")
            return NewsReport(category=category, articles=[])

    def get_news(self, category: str, lang: str = "en", ttl_seconds: int = 14400) -> NewsReport:
        """
        ttl_seconds default: 14400 (4 hours).
        """
        key = self._cache_key(category, lang)

        # 1. Try persistent cache first
        cached = self.cache.get(key)
        if cached:
            print(f"[NewsService] ✅ Loaded {category} from DISK cache.")
            return cached

        print(f"[NewsService] 🔄 Fetching fresh news for {category}...")
        query = self._build_query(category, lang)

        try:
            raw_response = self.firecrawl.search_news(query, num_results=15)
            web_results = self._normalize_search_results(raw_response)
            urls = self._pick_urls(web_results, limit=5)

            if not urls:
                print(f"[NewsService] WARN: No URLs. Returning Mock.")
                return NewsReport(
                    category=category,
                    updated_at_iso=datetime.now(timezone.utc).isoformat(),
                    articles=[NewsArticle(headline="No live news found", summary="Search returned 0 results.",
                                          source="System", url="#", date=datetime.now().strftime("%Y-%m-%d"))]
                )

            all_content = self._scrape_urls(urls)
            if not all_content:
                return NewsReport(category=category, articles=[])

            report = self._extract_with_llm(all_content, category, lang)

            # 2. Save to persistent cache
            self.cache.set(key, report, ttl_seconds)
            return report

        except Exception as e:
            print(f"[NewsService] Fatal error: {e}")
            return NewsReport(category=category, articles=[])