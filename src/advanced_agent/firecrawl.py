import os
import concurrent.futures
from typing import Any
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()


class FirecrawlService:
    def __init__(self, timeout_seconds: float = 90.0):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("Environment variable FIRECRAWL_API_KEY not found")

        self.app = FirecrawlApp(api_key=api_key)

        # Caches to avoid unnecessary external calls
        self._search_cache: dict[tuple[str, int], Any] = {}
        self._scrape_cache: dict[str, Any] = {}

        self.timeout_seconds = timeout_seconds

    # ------------------------------------------------------------
    # 🌐 SCRAPE with forced timeout
    # ------------------------------------------------------------
    def scrape_company_pages(self, url: str):
        if url in self._scrape_cache:
            return self._scrape_cache[url]
        def _do_scrape():
            return self.app.scrape(
                url=url,
                formats=["markdown", "branding", "images"],
            )
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_do_scrape)
                result = future.result(timeout=self.timeout_seconds)
        except concurrent.futures.TimeoutError:
            print(f"[TIMEOUT] scrape took longer than {self.timeout_seconds}s for {url}")
            executor.shutdown(wait=False, cancel_futures=True)
            return None
        except Exception as e:
            print(f"[ERROR] scrape failed for {url}: {e}")
            executor.shutdown(wait=False, cancel_futures=True)
            return None
        if not result:
            print(f"[WARN] scrape returned empty result for {url}")
            return None

        self._scrape_cache[url] = result
        return result

    # ------------------------------------------------------------
    # 📰 NEWS SEARCH (Fast, no inline scraping)
    # ------------------------------------------------------------
    def search_news(self, query: str, num_results: int = 10):
        """
        Optimized for News:
        - No 'scrape_options' (faster response, just gets SERP).
        - Higher default limit (to filter out irrelevant results later).
        - Distinct cache key.
        """
        # Cache key distinguishes this from company searches
        key = (query, num_results, "news")
        if key in self._search_cache:
            return self._search_cache[key]

        def _do_search():
            # Pure search. Lightweight.
            return self.app.search(
                query=query,
                limit=num_results
            )

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_do_search)
                # Shorter timeout (30s) because we aren't scraping yet
                result = future.result(timeout=30.0)
        except concurrent.futures.TimeoutError:
            print(f"[TIMEOUT] News search timed out for '{query}'")
            return []
        except Exception as e:
            print(f"[ERROR] News search failed for '{query}': {e}")
            return []
        # No 'finally shutdown' strictly needed for context manager, but safe to add if you prefer.

        if not result:
            print(f"[WARN] News search returned empty for '{query}'")
            return []

        # Firecrawl v1 sometimes wraps results in a 'data' key or returns a list directly
        # Normalize it here if needed, or return as is.
        final_data = result.get('data', result) if isinstance(result, dict) else result

        self._search_cache[key] = final_data
        return final_data

    # ------------------------------------------------------------
    # 📄 SCRAPE (Wrapper)
    # ------------------------------------------------------------
    def scrape(self, url: str):
        """
        Direct wrapper for FirecrawlApp.scrape
        """
        # Check cache if you implemented one, otherwise direct call
        if hasattr(self, "_scrape_cache") and url in self._scrape_cache:
            return self._scrape_cache[url]
        try:
            # Call the underlying SDK
            result = self.app.scrape_url(url, params={"formats": ["markdown"]})

            # Firecrawl SDK methods might be named 'scrape_url' or 'scrape' depending on version.
            # If the above fails, try: return self.app.scrape(url)

            if hasattr(self, "_scrape_cache"):
                self._scrape_cache[url] = result
            return result
        except AttributeError:
            # Fallback for different SDK versions
            return self.app.scrape(url)
        except Exception as e:
            print(f"[Firecrawl] Scrape error for {url}: {e}")
            raise e