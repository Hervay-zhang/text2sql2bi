import asyncio
import hashlib
import json

from app.core.clients import get_redis
from app.core.config import settings


def _key(question: str) -> str:
    normalized=" ".join([item for item in question.lower().split()])

    return "t2bi:query:"+hashlib.sha256( normalized.encode() ).hexdigest()

async def get_cached(question: str) -> dict | None:
    client=get_redis()
    # 协程
    value=await client.get(_key(question))
    return json.loads(value) if value else None

async def set_cached(question: str, payload: dict) -> None:
    client = get_redis()
    await client.set(_key(question),
                 json.dumps(payload,ensure_ascii=False),
                     settings.CACHE_TTL_SECONDS
                 )

async def main():
    await set_cached("统计   每个地区  的销售额", {
        "name": "zhangsan",
        "age": 18
    })
    print(await get_cached("统计   每个地区  的销售额"))

if __name__ == '__main__':
    #_key("统计   每个地区  的销售额")
    #_key("统计   每个地区  的销售额 统计 每个地区 的销售额 统计 每个地区 的销售额")

    asyncio.run(main())