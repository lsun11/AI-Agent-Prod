# src/topics/multi_pass_engine.py
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .multi_pass_search import WebResult, dedup_web_results

# Import your Firecrawl service (adjust path if needed)
from ..firecrawl import FirecrawlService  # ← adjust to your actual module


def _results_from_firecrawl_docs(
    docs: List[Any],
    pass_id: str,
    source_type: str,
) -> List[WebResult]:
    """
    Convert Firecrawl docs (or dicts) to WebResult instances.
    We assume each item is either:
      - Firecrawl Document with .markdown, .metadata
      - or a dict with keys 'markdown', 'metadata' or 'url'.
    """
    results: List[WebResult] = []

    for idx, doc in enumerate(docs):
        markdown = getattr(doc, "markdown", None)
        meta = getattr(doc, "metadata", None)

        if markdown is None and isinstance(doc, dict):
            markdown = doc.get("markdown")

        if not markdown:
            continue

        title = ""
        url = ""

        if meta is not None:
            title = getattr(meta, "title", "") or getattr(meta, "name", "") or ""
            url = getattr(meta, "url", "") or ""
        elif isinstance(doc, dict):
            meta = doc.get("metadata") or {}
            title = meta.get("title") or meta.get("name") or doc.get("title") or ""
            url = meta.get("url") or doc.get("url") or ""

        results.append(
            WebResult(
                url=url or "",
                title=title or "",
                markdown=markdown,
                source_type=source_type,
                rank=idx,
                pass_id=pass_id,
            )
        )

    return results


def multi_pass_collect(
    firecrawl: FirecrawlService,
    query: str,
    *,
    max_per_pass: int = 5,
) -> Tuple[str, List[Dict[str, str]]]:
    """
    Run several search passes, deduplicate results, and return:

    - merged_markdown: a single big markdown string (truncated)
    - sources: a list of {title, url, pass_id, source_type}

    You can feed `merged_markdown` into your analysis LLM,
    and pass `sources` into generate_document_and_slides(...) for citations.
    """

    # 1) Define passes (tweak / extend as you like)
    passes: List[Dict[str, str]] = [
        {
            "id": "general",
            "source_type": "general_search",
            "query": query,
        },
        {
            "id": "docs",
            "source_type": "docs_search",
            "query": f"{query} official documentation site",
        },
        {
            "id": "reviews",
            "source_type": "blog_search",
            "query": f"{query} vs alternatives comparison review",
        },
    ]

    all_results: List[WebResult] = []

    # 2) Run each pass with Firecrawl (adapt API names if needed)
    for p in passes:
        q = p["query"]
        pass_id = p["id"]
        source_type = p["source_type"]

        try:
            # Example: adjust to your actual call:
            # docs = firecrawl.search_web(q, limit=max_per_pass)
            docs = firecrawl.search_web(q, limit=max_per_pass)  # ← change if your API differs
        except Exception as e:
            print(f"multi_pass_collect: pass {pass_id} failed:", e)
            continue

        all_results.extend(
            _results_from_firecrawl_docs(docs, pass_id=pass_id, source_type=source_type)
        )

    # 3) Deduplicate across all passes
    deduped = dedup_web_results(all_results)

    # 4) Build merged markdown (truncated to avoid insane prompts)
    chunks: List[str] = []
    sources: List[Dict[str, str]] = []

    for r in deduped:
        # Build a nice header for each source block
        header_lines = []
        if r.title:
            header_lines.append(f"### {r.title}")
        if r.url:
            header_lines.append(f"{r.url}")
        header = "\n".join(header_lines)

        # Take only first N chars per doc to control size
        body = r.markdown.strip()
        if len(body) > 4000:
            body = body[:4000] + "\n\n...[truncated]..."

        block = f"{header}\n\n{body}".strip()
        chunks.append(block)

        sources.append(
            {
                "title": r.title or r.url or "Untitled page",
                "url": r.url or "",
                "source_type": r.source_type,
                "pass_id": r.pass_id,
            }
        )

    merged_markdown = "\n\n\n---\n\n\n".join(chunks)

    return merged_markdown, sources
