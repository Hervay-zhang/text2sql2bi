from typing import Any, Literal

from pydantic import BaseModel, Field


#定义查询模型

class QueryRequest(BaseModel):
    question: str = Field(
        min_length=2,
        max_length=2000,
    )


class QueryResponse(BaseModel):
    question: str
    answer: str
    sql: str
    success: bool
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    row_count: int = 0
    duration_ms: int = 0
    error: str | None = None

class SchemaSyncResponse(BaseModel):
    tables: int
    collection: str
    
#定义历史记录响应模型
class QueryHistoryRecord(BaseModel):
    id: int
    question: str
    sql: str
    chart_type: str
    duration_ms: int
    created_at: str
    
#支持多轮对话模型

class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)
    
class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    history: list[HistoryItem] = Field(
        default_factory=list,
        max_length=10,
    )
    force_refresh: bool = False
    

class QueryResponse(BaseModel):
    question: str
    answer: str
    sql: str
    success: bool
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    row_count: int = 0
    duration_ms: int = 0
    from_cache: bool = False
    error: str | None = None
    
#定义图标响应模型
class ChartSpec(BaseModel):
    type:Literal["kpi","bar","line","pie","table"]
    title:str
    option:dict[str,Any] = Field(default_factory=dict)
    
class QueryResponse(BaseModel):
    question:str
    answer:str
    sql:str
    success: bool
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    row_count:int = 0
    chart:ChartSpec |None= None
    duration_ms: int = 0
    curation_ms:int = 0
    from_cache:bool = False
    error:str | None = None
    
    
#定义看板模型
from typing import Any

from pydantic import BaseModel, Field


class DashboardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    definition: dict[str, Any] = Field(default_factory=dict)


class Dashboard(BaseModel):
    id: str
    name: str
    description: str
    definition: dict[str, Any]
    created_at: str
    updated_at: str
    
