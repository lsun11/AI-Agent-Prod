# src/api/routes/topics.py
from fastapi import APIRouter

from ..models import TopicRequest, TopicResponse
from ..deps import classify_topic_with_llm

router = APIRouter()


@router.post("/classify_topic", response_model=TopicResponse)
async def classify_topic(req: TopicRequest) -> TopicResponse:
    key, label = classify_topic_with_llm(req.message)
    return TopicResponse(topic_key=key, topic_label=label)
