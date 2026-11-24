# ---------------------- Qdrant 业务操作示例 ----------------------
import asyncio
from typing import List

from qdrant_client import models

from app.core.clients import get_qdrant, embed_texts
from app.core.config import settings

COLLECTION_NAME = "async_demo_collection"

# 创建向量数据库中的表
async def init_collection():
    qdrant=get_qdrant()
    exists=await qdrant.collection_exists(COLLECTION_NAME)
    if exists:
        await qdrant.delete_collection(COLLECTION_NAME)

    # 创建一个表
    await qdrant.create_collection(
        COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=settings.EMBEDDING_DIM,
            distance=models.Distance.COSINE
        )
    )

    print(f"成功创建了{COLLECTION_NAME}表")


async def insert_docs(text_list: List[str]):
    """文档文本 -> embedding -> 写入Qdrant，携带payload元数据"""
    qdrant = get_qdrant()
    embeddings = await embed_texts(text_list)

    points=[]
    for index,(text,vec) in enumerate(zip(text_list,embeddings)):
        point=models.PointStruct(
            id=index,
            vector=vec,
            payload={
                "content":text,
                "source":"demo"
            }
        )
        points.append(point)

    await qdrant.upsert(
        COLLECTION_NAME,
        points
    )
    print(f"成功写入 {len(points)} 条向量数据")

async def search_docs(query_text: str, top_k: int = 2):
    """异步向量检索(gRPC AsyncQdrantClient 使用 query_points)"""
    qdrant = get_qdrant()
    query_embedding = (await embed_texts([query_text]))[0]
    hits=await qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k
    )

    return hits.points


if __name__ == '__main__':
    #创建
    # asyncio.run(init_collection())

    # 插入数据
    docs = [
        "Milvus 是Go语言开发开源向量数据库，国内项目使用广泛",
        "Qdrant 使用Rust开发，过滤查询性能优秀，支持qdrant‑lite本地模式",
        "Pinecone 云托管向量数据库，无需运维，按用量计费",
        "Chroma 轻量级向量库，适合本地原型与学习测试"
    ]
    asyncio.run(insert_docs(docs))
    
    
    #查询数据
    # hits=asyncio.run(search_docs("Rust开发的向量数据库有哪些",4))
    # for hit in hits:
    #     print(f"score={hit.score:.4f} | content: {hit.payload.get('content')}")