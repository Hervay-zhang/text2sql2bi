#读取 PG 系统表，整理每张表的 schema 文本
import uuid

from qdrant_client import models

from app.core.clients import get_qdrant, embed_texts
from app.core.config import settings
from app.core.database import get_meta_pool
import asyncio
import selectors
from collections import defaultdict

async def _schema_documents() -> list[dict]:
    pool = await get_meta_pool()
    
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            """
             SELECT
                    c.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    tc.constraint_type,
                    kcu2.table_name AS foreign_table,
                    kcu2.column_name AS foreign_column
                FROM information_schema.columns c
                LEFT JOIN information_schema.key_column_usage kcu
                  ON c.table_schema = kcu.table_schema
                 AND c.table_name = kcu.table_name
                 AND c.column_name = kcu.column_name
                LEFT JOIN information_schema.table_constraints tc
                  ON kcu.constraint_name = tc.constraint_name
                 AND kcu.table_schema = tc.table_schema
                LEFT JOIN information_schema.referential_constraints rc
                  ON tc.constraint_name = rc.constraint_name
                 AND tc.constraint_schema = rc.constraint_schema
                LEFT JOIN information_schema.key_column_usage kcu2
                  ON rc.unique_constraint_name = kcu2.constraint_name
                 AND rc.unique_constraint_schema = kcu2.constraint_schema
                WHERE c.table_schema = 'public'
                  AND c.table_name NOT LIKE 'bi_%'
                ORDER BY c.table_name, c.ordinal_position
        """)
        rows = await cur.fetchall()
        
        # 按**表名做 key**，把同一个表的所有行（各个字段）归为一组。
        grouped: dict[str, list[tuple]] = defaultdict(list)
        for row in rows:
            # key = 表名  value = 一行的所有字段
            grouped[row[0]].append(row)
        
        # 把数据库元数据拼接成**人类可读的文本字符串**，用于向量化。
        result_list = []
        for table, columns in grouped.items():
            lines = [f"TABLE {table}"]
            
            for (
                        _,
                        column,
                        data_type,
                        nullable,
                        constraint,
                        foreign_table,
                        foreign_column,
            ) in columns:
                flags = []
                
                if constraint == "PRIMARY KEY":
                    flags.append("PRIMARY KEY")
                
                if constraint == "FOREIGN KEY" and foreign_table:
                    flags.append(
                        f"REFERENCES {foreign_table}({foreign_column})"
                    )
                
                if nullable == "NO":
                    flags.append("NOT NULL")
                #name:str REFERENCES customers(id) NOT NULL
                suffix = " " + " ".join(flags) if flags else ""
                lines.append(f"- {column}: {data_type}{suffix}")
            content="\n".join(lines)
            result_list.append(
                {
                        "table_name": table,
                        "content": content,
                }
            )
        
        return result_list


# 检查 Qdrant 集合是否存在；不存在就新建。
async def ensure_collection() -> None:
    client = get_qdrant()
    
    if not await client.collection_exists(
            settings.QDRANT_COLLECTION
    ):
        await client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=models.VectorParams(
                size=settings.EMBEDDING_DIM,
                distance=models.Distance.COSINE,
            ),
        )
        
# 全量同步数据库表结构到 Qdrant 向量库（全量索引）
async def sync_schema() -> int:
    documents=await _schema_documents()
    if not documents:
        return 0

    await ensure_collection()
    
    vector_list = await embed_texts([document['content'] for document in documents])
    points = [
            models.PointStruct(
                id=str(
                    uuid.uuid5(
                        uuid.NAMESPACE_URL,
                        f"text2sql2bi:{document['table_name']}",
                    )
                ),
                vector=vector,
                payload=document
            )
            for document, vector in zip(documents, vector_list, strict=True)
    ]
    
    # `upsert`：存在就更新，不存在就插入。
    await get_qdrant().upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points,
        # `wait=True`：等待 Qdrant 写入完成再返回，不异步后台执行。
        
        wait=True,
    )
    
    # 返回值：成功写入多少张表。
    return len(points)

#检查schema
# 业务调用入口：用户自然语言问题，检索相关表结构。
async def search_schema(
    question: str,
    limit: int = 6,
) -> list[dict]:
    await ensure_collection()

    vector = (await embed_texts([question]))[0]

    result = await get_qdrant().query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=vector,
        limit=limit,
        # 是否返回 point 的 payload（元数据字典）。
        #  True：检索结果带回 payload（table_name、content 等业务字段） `False`：只返回 id、score，不带业务数据
        with_payload=True,
        # `with_vectors=False`：不需要把向量返回，减少传输；
        with_vectors=False,
    )
    # 把 payload 和相似度 score 拼装返回
    return [
        {
            **(point.payload or {}),
            "score": point.score,
        }
        for point in result.points
    ]





if __name__ == '__main__':
    #print(asyncio.run(_schema_documents()))
    print(asyncio.run(
        # _schema_documents(),
        # sync_schema(),
        search_schema("按月份统计已支付订单的销售额",2),
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
    ))
