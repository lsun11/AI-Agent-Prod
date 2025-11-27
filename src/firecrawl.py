import os
import concurrent.futures
from typing import Any

from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

class FirecrawlService:
    def __init__(self, timeout_seconds: float = 30.0):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("Environment variable FIRECRAWL_API_KEY not found")

        self.app = FirecrawlApp(api_key=api_key)

        # Caches to avoid unnecessary external calls
        self._search_cache: dict[tuple[str, int], Any] = {}
        self._scrape_cache: dict[str, Any] = {}

        self.timeout_seconds = timeout_seconds

    # ------------------------------------------------------------
    # 🔍 SEARCH with forced timeout
    # ------------------------------------------------------------
    def search_companies(self, query: str, num_results: int = 5):
        """
        General web search to find the most relevant pages for a tool / company.
        Used for:
          - discovering the official website
          - getting general docs/marketing content

        Does NOT force 'pricing' into the query.
        """
        key = (query, num_results)
        if key in self._search_cache:
            return self._search_cache[key]

        print(f"[Firecrawl] Searching web for: {query}")

        def _do_search():
            return self.app.search(
                query=query,  # 👈 use query as-is
                limit=num_results,
                scrape_options={"formats": ["markdown"]},
            )

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_do_search)
                result = future.result(timeout=self.timeout_seconds)
        except concurrent.futures.TimeoutError:
            print(f"[TIMEOUT] search took longer than {self.timeout_seconds}s for '{query}'")
            return []
        except Exception as e:
            print(f"[ERROR] search failed for '{query}': {e}")
            return []
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        if not result:
            print(f"[WARN] search returned empty result for '{query}'")
            return []

        self._search_cache[key] = result
        return result

    # ------------------------------------------------------------
    # 🌐 SCRAPE with forced timeout
    # ------------------------------------------------------------
    def scrape_company_pages(self, url: str):
        if url in self._scrape_cache:
            return self._scrape_cache[url]

        print("Scraping", url)

        def _do_scrape():
            return self.app.scrape(
                url=url,
                formats=["markdown"],
            )
        print("Scraping2")
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
        print("Scraping3")
        if not result:
            print(f"[WARN] scrape returned empty result for {url}")
            return None

        self._scrape_cache[url] = result
        return result



