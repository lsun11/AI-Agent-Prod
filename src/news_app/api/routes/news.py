from fastapi import APIRouter, HTTPException, Query
from src.news_app.service import NewsService
from src.news_app.models import NewsReport

router = APIRouter()

# Instantiate the service once (it handles its own caching)
news_service = NewsService()

@router.get("/news", response_model=NewsReport)
def get_latest_news(
    category: str = Query("tech", description="Category of news to fetch (e.g. tech, sports)"),
    language: str = Query("en", description="Language code (en, zh)")
):
    """
    Fetches the latest news for a specific category.
    Delegates to NewsService for caching, searching (Firecrawl), and extraction (LLM).
    """
    try:
        # We use a synchronous 'def' route here so FastAPI runs this
        # in a threadpool, preventing the blocking Firecrawl/LLM calls
        # from freezing the main event loop.
        report = news_service.get_news(category=category, lang=language)
        return report
    except Exception as e:
        print(f"[News API Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))