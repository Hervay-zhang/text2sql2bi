from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis
from app.core.config import settings

_qdrant: AsyncQdrantClient | None = None
_embedding_client: AsyncOpenAI | None = None
_redis: Redis | None = None
"""

qdrant就是之前学的milvus
对qdrant以及envedding客户端进行创建，关闭，以及进行向量数据化
"""
def get_redis() ->Redis:
    #单例
    global _redis
    if _redis is None:
        _redis = Redis.from_url(
            settings.REDIS_URL,
            decode_responses= True,
        )
    return _redis

def get_qdrant() -> AsyncQdrantClient:
    global _qdrant
    if _qdrant is None:
        _qdrant = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
        )
    return _qdrant


def get_embedding_client() -> AsyncOpenAI:
    global _embedding_client
    if _embedding_client is None:
        _embedding_client = AsyncOpenAI(
            api_key=settings.EMBEDDING_API_KEY,
            base_url=settings.EMBEDDING_BASE_URL,
            timeout=30,
        )
    return _embedding_client


async def embed_texts(texts: list[str]) -> list[list[float]]:
    response = await get_embedding_client().embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
        dimensions=settings.EMBEDDING_DIM,
    )
    return [item.embedding for item in response.data]


async def close_clients() -> None:
    global _redis,_qdrant, _embedding_client
    if _redis:
        await _redis.aclose()
        _redis  =None
    if _qdrant:
        await _qdrant.close()
        _qdrant = None
    if _embedding_client:
        await _embedding_client.close()
        _embedding_client = None