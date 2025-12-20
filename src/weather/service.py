from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

from src.weather.models import WeatherReport, WeatherSource
from src.advanced_agent.firecrawl import FirecrawlService  # <-- reuse yours
from langchain_openai import ChatOpenAI

@dataclass
class CacheItem:
    value: WeatherReport
    expires_at: float


class TTLCache:
    def __init__(self):
        self._store: Dict[str, CacheItem] = {}

    def get(self, key: str) -> Optional[WeatherReport]:
        item = self._store.get(key)
        if not item:
            return None
        if time.time() > item.expires_at:
            self._store.pop(key, None)
            return None
        return item.value

    def set(self, key: str, value: WeatherReport, ttl_seconds: int) -> None:
        self._store[key] = CacheItem(value=value, expires_at=time.time() + ttl_seconds)


class WeatherService:
    """
    Firecrawl → scrape candidate pages → LLM extracts into WeatherReport.
    """
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.cache = TTLCache()

    def _cache_key(self, lat: float, lon: float, lang: str) -> str:
        # round to reduce cache churn while still correct enough
        return f"{round(lat, 2)}:{round(lon, 2)}:{lang.lower()}"

    def _build_query(self, lat: float, lon: float, lang: str) -> str:
        # keep it search-engine friendly; many weather pages rank well for “forecast <lat> <lon>”
        if lang.lower().startswith("zh"):
            return f"天气 预报 {lat} {lon} 每小时 今日 明日"
        return f"weather forecast {lat} {lon} hourly today tomorrow"

    def _pick_urls(self, web_results: List[Any], limit: int = 5) -> List[Tuple[str, str]]:
        """
        Return [(title,url)] top results, skipping empty entries.
        Matches the defensive style you used in root_workflow.
        """
        urls: List[Tuple[str, str]] = []
        for r in web_results:
            meta = getattr(r, "metadata", None)
            title = (getattr(meta, "title", "") if meta else "") or ""
            url = (getattr(meta, "url", "") if meta else "") or ""

            title = title.strip() if isinstance(title, str) else ""
            url = url.strip() if isinstance(url, str) else ""

            if not url:
                if isinstance(r, dict):
                    url = (r.get("url") or "").strip()
                    title = (r.get("title") or "").strip()

            if not url:
                continue

            # very light filtering (optional)
            if "google.com" in url:
                continue

            urls.append((title, url))
            if len(urls) >= limit:
                break
        return urls

    def _scrape_urls(self, urls: List[Tuple[str, str]]) -> Tuple[str, List[WeatherSource]]:
        """
        Scrape pages and return combined markdown + sources.
        """
        chunks: List[str] = []
        sources: List[WeatherSource] = []

        for title, url in urls:
            try:
                doc = self.firecrawl.scrape(url)  # assume your service returns an object with .markdown
                markdown = getattr(doc, "markdown", None) or ""
                markdown = markdown.strip()
                if not markdown:
                    continue

                sources.append(WeatherSource(title=title or "", url=url, snippet=markdown[:160].replace("\n", " ")))
                # don’t feed massive pages
                chunks.append(f"## SOURCE: {title}\nURL: {url}\n\n{markdown[:3500]}\n")
            except Exception:
                # ignore one bad domain, keep going
                continue

        return ("\n\n".join(chunks)).strip(), sources

    def _extract_with_llm(self, all_content: str, lat: float, lon: float, lang: str, sources: List[WeatherSource]) -> WeatherReport:
        """
        LLM converts messy scraped content → structured WeatherReport.
        """
        # choose your model the same way the agent does
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)  # or pass from query

        # IMPORTANT: make it robust. Many pages contain multiple locations; insist on matching coords.
        sys = (
            "You are a weather data extractor.\n"
            "Given scraped web page text, output STRICT JSON matching the WeatherReport schema.\n"
            "Rules:\n"
            "- Prefer the location that best matches the provided coordinates.\n"
            "- If exact city name missing, use 'Lat {lat}, Lon {lon}' label.\n"
            "- Provide a concise summary_line suitable for a compact widget.\n"
            "- If hourly data missing, return an empty list.\n"
            "- If daily forecast missing, return an empty list.\n"
            "- Use the language requested.\n"
        )

        # We’ll ask for JSON only; then Pydantic validate.
        user = {
            "lat": lat,
            "lon": lon,
            "lang": lang,
            "scraped_text": all_content[:12000],  # keep bounded
        }

        prompt = f"{sys}\n\nINPUT:\n{json.dumps(user, ensure_ascii=False)}\n\nOUTPUT JSON ONLY:"
        resp = llm.invoke(prompt)  # adapt if you use messages

        raw = getattr(resp, "content", resp)
        raw = raw.strip()

        # If your models sometimes wrap ```json fences:
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.replace("json", "", 1).strip()

        data = json.loads(raw)

        report = WeatherReport.model_validate(data)
        report.sources = sources
        report.updated_at_iso = datetime.now(timezone.utc).isoformat()
        return report

    def get_weather(self, lat: float, lon: float, lang: str = "en", ttl_seconds: int = 1800) -> WeatherReport:
        key = self._cache_key(lat, lon, lang)
        cached = self.cache.get(key)
        if cached:
            return cached

        query = self._build_query(lat, lon, lang)

        # 1) search
        web_results = self.firecrawl.search(query, limit=8)  # mirror your agent call signature
        urls = self._pick_urls(web_results, limit=5)

        # 2) scrape
        all_content, sources = self._scrape_urls(urls)

        # 3) extract
        if not all_content:
            # create a minimal report with sources only
            report = WeatherReport(
                location_label=f"Lat {lat:.2f}, Lon {lon:.2f}",
                summary_line="Weather unavailable (no sources)",
                sources=sources,
                updated_at_iso=datetime.now(timezone.utc).isoformat(),
            )
            self.cache.set(key, report, ttl_seconds)
            return report

        report = self._extract_with_llm(all_content, lat, lon, lang, sources)

        # 4) cache
        self.cache.set(key, report, ttl_seconds)
        return report
