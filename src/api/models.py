# src/api/models.py
from typing import Optional, List
from pydantic import BaseModel


class TopicRequest(BaseModel):
    message: str


class TopicResponse(BaseModel):
    topic_key: str
    topic_label: str


class ChatRequest(BaseModel):
    message: str
    # Optional manual override; if provided and valid, we use it.
    topic: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    download_url: Optional[str] = None
    topic_used: Optional[str] = None
    logs: List[str] = []
