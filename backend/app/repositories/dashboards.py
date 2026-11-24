import json
import uuid

from app.core.database import get_meta_pool
from app.schemas.models import DashboardCreate


async def list_dashboards() -> list[dict]:
    pool = await get_meta_pool()
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            "SELECT id::text, name, description, definition, "
            "created_at, updated_at "
            "FROM bi_dashboard "
            "ORDER BY updated_at DESC"
        )
        return [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "definition": row[3],
                "created_at": row[4].isoformat(),
                "updated_at": row[5].isoformat(),
            }
            for row in await cur.fetchall()
        ]


async def create_dashboard(body: DashboardCreate) -> dict:
    dashboard_id = str(uuid.uuid4())
    pool = await get_meta_pool()
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO bi_dashboard (
                id,
                name,
                description,
                definition
            )
            VALUES (%s, %s, %s, %s::jsonb)
            RETURNING
                id::text,
                name,
                description,
                definition,
                created_at,
                updated_at
            """,
            (
                dashboard_id,
                body.name,
                body.description,
                json.dumps(body.definition, ensure_ascii=False),
            ),
        )
        row = await cur.fetchone()

    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "definition": row[3],
        "created_at": row[4].isoformat(),
        "updated_at": row[5].isoformat(),
    }


async def delete_dashboard(dashboard_id: str) -> bool:
    pool = await get_meta_pool()
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute(
            "DELETE FROM bi_dashboard WHERE id = %s::uuid",
            (dashboard_id,),
        )
        return cur.rowcount > 0