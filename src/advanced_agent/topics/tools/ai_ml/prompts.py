from ..base_prompts import BaseCSResearchPrompts


class AIPlatformPrompts(BaseCSResearchPrompts):
    """
    AI / ML platforms, model APIs, and ML infrastructure.

    Examples:
      - OpenAI, Anthropic, DeepSeek, Gemini
      - Hugging Face, Replicate, Together AI
      - Vector DBs (Pinecone, Weaviate, Milvus)
      - Managed training / inference platforms

    NOT:
      - Generic developer tools (VS Code → developer_tools)
      - Generic cloud platforms (AWS, GCP → cloud)
    """
    TOPIC_LABEL = "AI/ML platform, model API, or machine-learning infrastructure service"
    ANALYSIS_SUBJECT = (
        "AI platforms, model hosting, vector databases, ML pipelines, and inference services"
    )
    RECOMMENDER_ROLE = "machine learning systems engineer"

