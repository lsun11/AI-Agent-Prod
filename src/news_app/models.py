from typing import List, Optional
from pydantic import BaseModel

class NewsArticle(BaseModel):
    headline: str
    summary: str
    source: str
    url: str
    date: str

class NewsReport(BaseModel):
    category: str
    articles: List[NewsArticle]
    updated_at_iso: Optional[str] = None