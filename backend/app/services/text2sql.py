import json
from numbers import Number
from typing import Any, TypedDict

from fastapi.encoders import jsonable_encoder
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.core.config import settings
from app.core.database import get_query_pool
from app.services.llm import invoke_text
from app.services.schema_catalog import search_schema
from app.services.sql_guard import secure_sql

# State 供LangGraph使用
class BIState(TypedDict, total=False):
    question: str
    schema_context: str
    sql: str
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    error: str | None
    attempt: int  # 记录重试次数的
    history: list[dict]
    chart: dict[str, Any]
    chart_type: str | None
    # answer: str
    # success: bool
    # started_at: float
    # duration_ms: int
    
# 根据问题查询相关的表结构
async def retrieve_schema(state: BIState) -> dict:
    try:
        documents = await search_schema(state['question'])
    except Exception as exc:
        return {
                "error": f"Schema 检索失败：{exc}",
        }
    context = "\n".join([
            doc['content']
            for doc in documents
    ])
    if not context:
        return {
                "error": "尚未同步数据源 Schema，请先同步数据源",
        }
    return {
            "schema_context": context,
            "error": None
    }

# {"sql": "SELECT * FROM customers"}
# 该函数的作用是判断大模型返回的结果是否为有效的sql语句
def extract_sql(text: str) -> str:
    try:
        data = json.loads(text)
    except Exception as e:
        raise ValueError(
            "模型没有返回合法JSON"
        )
    if not isinstance(data, dict):
        raise ValueError(
            "模型返回结果必须是JSON对象"
        )
    sql = data.get("sql")
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError(
            "模型返回结果缺少有效的sql字段"
        )
    
    return sql.strip()

# 根据表结构和问题，调用大模型，返回sql语句
async def generate_sql(state: BIState) -> dict:
    error_hint = state['error']
    attempt = state.get("attempt", 0) + 1
    
    history = state['history']  # list[dict]
    history_str = "\n".join(
        [
                f"{item['role']}: {item['content']}"
                for item in history[-6:]
        ]
    )
    
    prompt = f"""你是资深 BI 数据分析师。根据 PostgreSQL Schema，把用户问题转换成一条只读 SELECT SQL。

        规则：
        1. 只输出JSON：{{"sql":"..."}}，不要解释。
        2. 只能使用Schema中存在的表和字段。
        3. 收入金额使用order_items.quantity * order_items.unit_price。
        4. 除非用户明确要求，否则订单分析只统计status='paid'。
        5. 使用PostgreSQL方言。
        6. 只生成一条SELECT查询，不得生成写操作和DDL。

        Schema：
        {state.get('schema_context', '')}
        
        最近对话消息:{history_str or '无'}
        
        用户问题：
        {state['question']}

        上一次错误：{error_hint}

        """
    # print("prompt",prompt)
    content = await invoke_text(prompt)
    # print("content",content)
    try:
        sql = extract_sql(content)
    except Exception as e:
        return {
                "attempt": attempt,
                "error": f"SQL 生成失败：{e}",
        }
    if not sql:
        return {
                "attempt": attempt,
                "error": "模型没有返回SQL",
        }
    return {
            "sql": sql,
            "attempt": attempt,
            'error': None
    }

# 执行sql语句
async def execute_sql(state: BIState) -> dict:
    try:
        pool = await get_query_pool()
        async with  pool.connection() as conn, conn.transaction(), conn.cursor() as cur:
            await cur.execute("SET TRANSACTION READ ONLY")
            await cur.execute(
                f"SET LOCAL statement_timeout = {settings.SQL_TIMEOUT_SECONDS * 1000}"
            )
            await cur.execute(state['sql'])
            rows = await cur.fetchall()
            columns = [descript.name for descript in cur.description]
        return {
                "columns": columns,
                # jsonable_encoder 将 数据中的一些特殊数据类型转换为json 可以序列化 的类型，比如Decimal,DateTime,UUID
                "rows": jsonable_encoder([list(row) for row in rows]),
                "row_count": len(rows),
                "error": None
        }
    except Exception as e:
        return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "error": f"执行sql失败，原因是{e}"
        }

# 两个路由函数

def route_after_schema(state: BIState) -> str:
    if state['error']:
        return "visualize"
    return "generate_sql"

#
# def route_after_generate(state: BIState) -> str:
#     if state['error']:
#         return "end"
#     return "validate_sql"

# def route_after_validate(state: BIState) -> str:
#     if state['error']:
#         return "end"
#     return "execute_sql"

# 该节点的作用是：返回一个安全的sql语句
async def validate_sql(state: BIState) -> dict:
    try:
        safe_sql = secure_sql(state['sql'], settings.SQL_MAX_ROWS)
        return {
                'sql': safe_sql,
                'error': None
        }
    except Exception as e:
        return {"error": f"SQL 校验失败：{e}"}

# 这个节点是一个核心节点，需要进入很多次
def _after_step(state: BIState, success_node: str) -> str:
    if not state.get("error"):
        return success_node
    return (
        "generate_sql"
        if state.get("attempt", 0) <= settings.SQL_MAX_RETRY
        else "visualize"
    )

#图标推荐函数完整代码
# 传递一些查询结果，我给帮你选一种图表，并且图表的js也返回给你
def chart_spec(
    question: str,
    columns: list[str],
    rows: list[list[Any]],
) -> dict:
    #获取title
    title=question.rstrip("？?")
    # 假如要是没有数据，走table
    if not rows:
        return {
            "type": "table",
            "title": title,
            "option": {},
        }
    numeric_indexes = [
        i
        for i, value in enumerate(rows[0])
        if isinstance(value, Number)
    ]

    # 这个判断不能说错误，而是不太严谨，比如我举个例子  [['zs',19,'nan']]

    if len(rows) == 1 and len(numeric_indexes) == 1:
        return {
            "type": "kpi",
            "title": title,
            "option": {
                "value": rows[0][numeric_indexes[0]],
            },
        }
    """
           [
              [
                 '手机',198, 19000
              ],[
                 '电脑',19,54000
              ]
           ]

        """

    if len(columns) >= 2 and numeric_indexes:
        # numeric_indexes= [1,2]
        value_index = numeric_indexes[-1]  # 2
        dimension_index = 0 if value_index != 0 else 1  # 0

        # 标签
        labels = [str(row[dimension_index]) for row in rows]  # ['手机','电脑']

        # 求数值
        values = [row[value_index] for row in rows]  # [19000,54000]

        # 求列名的
        dimension_name = columns[dimension_index].lower()  # category

        if len(rows) <= 8 and any(
                key in dimension_name
                for key in ("region", "status", "category", "channel")
        ):
            return {
                "type": "pie",
                "title": title,
                "option": {
                    "tooltip": {"trigger": "item"},
                    "legend": {"bottom": 0},
                    "series": [
                        {
                            "type": "pie",
                            "radius": ["45%", "70%"],
                            "data": [
                                {"name": label, "value": value}
                                for label, value in zip(
                                    labels,
                                    values,
                                    strict=True,
                                )
                            ],
                        }
                    ],
                },
            }
        chart_type = (
            "line"
            if any(
                key in dimension_name
                for key in ("date", "month", "year", "week")
            )
            else "bar"
        )

        return {
            "type": chart_type,
            "title": title,
            "option": {
                "tooltip": {"trigger": "axis"},
                "grid": {
                    "left": 48,
                    "right": 24,
                    "top": 24,
                    "bottom": 48,
                },
                "xAxis": {
                    "type": "category",
                    "data": labels,
                    "axisLabel": {"rotate": 20},
                },
                "yAxis": {
                    "type": "value",
                    "splitLine": {
                        "lineStyle": {"color": "#edf0f4"},
                    },
                },
                "series": [
                    {
                        "name": columns[value_index],
                        "type": chart_type,
                        "smooth": True,
                        "data": values,
                    }
                ],
            },
        }

    return {
        "type": "table",
        "title": title,
        "option": {},
    }

#在LangGraph中生成最终结果
#visualize节点既生成图表描述，也生成面向用户的简短回答：
# 根据用户的查询结果生成可视化的内容
async def visualize(state: BIState) -> dict:
    columns=state.get('columns',[])
    rows=state.get('rows',[])
    chart=chart_spec(
        state["question"],
        columns,
        rows,
    )
    chart_type = chart['type']
    
    # 还可以更新别的一些字段
    error = state.get("error")

    if error:
        answer = error
        success = False
    elif not rows:
        answer = "查询成功，但没有符合条件的数据。"
        success = True
    elif chart["type"] == "kpi":
        answer = f"查询结果为 {chart['option']['value']}。"
        success = True
    else:
        answer = (
            f"查询成功，共返回 {len(rows)} 条结果，"
            f"已生成 {chart['type']} 图。"
        )
        success = True

    return {
        "chart":chart,
        "answer": answer,
        "success": success,
        "chart_type": chart_type
    }

# 制作graph的时候：
def build_graph():
    builder=StateGraph(BIState)

    builder.add_node(retrieve_schema)
    builder.add_node(generate_sql)
    builder.add_node(validate_sql)
    builder.add_node(execute_sql)
    builder.add_node(visualize)


    builder.add_edge(START,"retrieve_schema")


    builder.add_conditional_edges("retrieve_schema",route_after_schema,
                                  {
                                      "visualize": "visualize",

                                      "generate_sql":"generate_sql"
                                  })

    builder.add_conditional_edges("generate_sql",
                                  lambda state: _after_step(state, "validate_sql")
    ,{
        "visualize":"visualize",
        "validate_sql":"validate_sql",
        "generate_sql":"generate_sql"
    })

    builder.add_conditional_edges("validate_sql",
          lambda state: _after_step(state, "execute_sql"),
                                  {
        "visualize":"visualize",
        "execute_sql":"execute_sql",
        "generate_sql": "generate_sql"
    } )

    builder.add_conditional_edges("execute_sql",
      lambda state: _after_step(state, "visualize"),
                                  {
                                      "visualize":"visualize",
                                      "generate_sql": "generate_sql"
                                  })

    builder.add_edge("visualize",END)

    return builder.compile()

compiled_graph = build_graph()
