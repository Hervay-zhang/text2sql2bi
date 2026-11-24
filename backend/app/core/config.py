from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        extra="ignore",
        case_sensitive=False,
    )

    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_MODEL: str = "deepseek-v4-flash"
    LLM_TIMEOUT_SECONDS: int = 60
    
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_BASE_URL: str = (
        "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    EMBEDDING_MODEL: str = "text-embedding-v4"
    EMBEDDING_DIM: int = 1536

    POSTGRES_DSN: str = (
        "postgresql://bi:local_bi_owner_only@localhost:54320/text2sql2bi"   #bi-账户---系统自身数据的读写操作
    )
    QUERY_POSTGRES_DSN: str = (
        "postgresql://bi_reader:local_bi_reader_only@localhost:54320/text2sql2bi"   #bi-readewr账户--- 只执行大模型生成的业务查询
    )
    QDRANT_URL: str = "http://localhost:56333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "schema_catalog"
    
    SQL_MAX_ROWS: int = 500
    SQL_TIMEOUT_SECONDS: int = 15
    SQL_MAX_RETRY: int = 2
    
    #redis和缓存时间
    REDIS_URL: str = "redis://localhost:56379/0"
    CACHE_TTL_SECONDS :int= 600

    @property
    def allowed_origins(self) -> list[str]:
        return [
            item.strip()
            for item in self.ALLOWED_ORIGINS.split(",")
            if item.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings() 
