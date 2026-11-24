from langchain_openai import ChatOpenAI

from app.core.config import settings



_llm: ChatOpenAI | None = None   #_llm用于复用模型客户端；
def get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            model=settings.LLM_MODEL,
            temperature=0,
            timeout=settings.LLM_TIMEOUT_SECONDS,
            max_retries=2,
        )
    return _llm


async def invoke_text(prompt: str) -> str:
    message = await get_llm().ainvoke(prompt)
    if isinstance(message.content, str):
        return message.content.strip()
    return "".join(
        str(part)
        for part in message.content
    ).strip()