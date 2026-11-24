from app.core.database import get_meta_pool


async def save_query_history(
    question: str,
    sql: str,
    chart_type: str,
    duration_ms: int,
) -> None:
    pool = await get_meta_pool()
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO bi_query_history "
            "(question, sql, chart_type, duration_ms) "
            "VALUES (%s, %s, %s, %s)",
            (question, sql, chart_type, duration_ms),
        )


async def list_query_history(limit: int = 100) -> list[dict]:
    pool = await get_meta_pool()
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            "SELECT id, question, sql, chart_type, "
            "duration_ms, created_at "
            "FROM bi_query_history "
            "ORDER BY created_at DESC LIMIT %s",
            (limit,),
        )
        return [
            {
                "id": row[0],
                "question": row[1],
                "sql": row[2],
                "chart_type": row[3],
                "duration_ms": row[4],
                "created_at": row[5].isoformat(),
            }
            for row in await cur.fetchall()
        ]


async def delete_query_history(history_id: int) -> bool:
    pool = await get_meta_pool()
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            "DELETE FROM bi_query_history WHERE id = %s",
            (history_id,),
        )
        return cur.rowcount > 0