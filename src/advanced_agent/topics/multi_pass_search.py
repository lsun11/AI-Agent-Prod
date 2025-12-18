# src/topics/multi_pass_search.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


@dataclass
class WebResult:
    """
    A normalized representation of a scraped page.

    `markdown` is the main text content (from Firecrawl or your scraper).
    """
    url: str
    title: str
    markdown: str
    source_type: str  # e.g. "general_search", "docs_search", "blog_search"
    rank: int         # rank within that pass (0 = best)
    pass_id: str      # identifier of which pass this came from


def _normalize_url(url: str) -> str:
    """
    Normalize a URL for deduping:
    - lowercase scheme/host
    - strip fragments
    - drop common tracking query params
    """
    if not url:
        return ""
    parsed = urlparse(url)

    scheme = (parsed.scheme or "").lower()
    netloc = (parsed.netloc or "").lower()

    # Strip fragment
    path = parsed.path or ""
    params = parsed.params or ""
    query = parsed.query or ""

    # Clean query: drop known tracking params
    if query:
        pairs = parse_qsl(query, keep_blank_values=True)
        drop_keys = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "fbclid"}
        filtered = [(k, v) for (k, v) in pairs if k not in drop_keys]
        query = urlencode(filtered)

    return urlunparse((scheme, netloc, path, params, query, ""))


def _normalize_title(title: str) -> str:
    """
    Normalize a title for approximate deduping:
    - lowercase
    - collapse whitespace
    - strip common suffixes like "| Company" etc. (simple heuristic)
    """
    t = (title or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    # Drop very common useless suffixes (you can extend this)
    t = re.sub(r"\s*\|\s*home$", "", t)
    t = re.sub(r"\s*\|\s*docs$", "", t)
    t = re.sub(r"\s*\|\s*documentation$", "", t)
    return t


def dedup_web_results(results: Iterable[WebResult]) -> List[WebResult]:
    """
    Deduplicate results across all passes by:
    - canonical URL (strong key)
    - fallback: (domain + normalized title)

    Keep the "best" ranked version of each page.
    """
    by_canonical: Dict[str, WebResult] = {}
    by_domain_title: Dict[Tuple[str, str], WebResult] = {}

    def better(a: WebResult, b: WebResult) -> WebResult:
        # Lower rank is better; if tie, prefer general_search > docs_search > blog_search
        if a.rank < b.rank:
            return a
        if a.rank > b.rank:
            return b
        prio = {"general_search": 0, "docs_search": 1, "blog_search": 2}
        return a if prio.get(a.source_type, 99) <= prio.get(b.source_type, 99) else b

    for r in results:
        canon = _normalize_url(r.url)
        if canon:
            existing = by_canonical.get(canon)
            if existing is None:
                by_canonical[canon] = r
            else:
                by_canonical[canon] = better(existing, r)
            continue

        # Fallback: domain + normalized title
        parsed = urlparse(r.url or "")
        domain = (parsed.netloc or "").lower()
        norm_title = _normalize_title(r.title)
        key = (domain, norm_title)
        if not any(key):
            # nothing to key on, just skip dedup and add as is
            by_domain_title[id(r)] = r  # unique key
            continue

        existing = by_domain_title.get(key)
        if existing is None:
            by_domain_title[key] = r
        else:
            by_domain_title[key] = better(existing, r)

    merged: Dict[str, WebResult] = {}
    merged.update({f"url:{k}": v for k, v in by_canonical.items()})
    merged.update({f"dt:{id_}": v for id_, v in by_domain_title.items()})

    # Sort final results by (rank, source_type) for stability
    def sort_key(r: WebResult) -> Tuple[int, str]:
        return (r.rank, r.source_type)

    return sorted(merged.values(), key=sort_key)
