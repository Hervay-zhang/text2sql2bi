import httpx
import asyncio
import os

API_KEY = os.environ["LLM_API_KEY"]
BASE_URL = "https://api.nexarelayapi.com/v1"

async def main():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/models", headers=headers)
        print("status_code:", resp.status_code)
        print(resp.json())

if __name__ == "__main__":
    asyncio.run(main())
