import time

from app.repositories.query_history import save_query_history
from app.schemas.models import QueryRequest, QueryResponse
from app.services.cache import get_cached, set_cached
from app.services.text2sql import compiled_graph


async def run_query(body: QueryRequest) -> QueryResponse:
    started = time.perf_counter()
    #判断缓存条件
    question = body.question
    # 假如页面上说强制刷新，那就是不使用缓存
    use_cache = not body.force_refresh
    # use_cache=True
    #缓存命中直接返回
    if use_cache:
        item = await get_cached(question)
        
        if item:
            print("这一次是从缓存中获取的值.....")
            item["from_cache"] = True
            return QueryResponse(**item)
    
    print("这一次是执行数据库获取的值.....")
    history = [item.model_dump() for item in body.history]
    #第三步：执行LangGraph
    # BIState
    final = await compiled_graph.ainvoke({"question": question,"history":history})
   
    #第四步  统一响应
    error = final.get("error")
    rows = final.get("rows", [])
    if error:
        answer = error
        success = False
    elif not rows:
        answer = "查询成功，但没有符合条件的数据。"
        success = True
    else:
        answer = f"查询成功，共返回 {len(rows)} 条结果。"
        success = True
    
    duration_ms = round((time.perf_counter() - started) * 1000)
    chart = final['chart']
    # 如何获取图表的类型呢？
    pay_load = QueryResponse(
        question=question,
        answer=answer,
        sql=final.get("sql", ""),
        success=success,
        columns=final.get("columns", []),
        rows=final.get("rows", []),
        row_count=final.get("row_count", 0),
        duration_ms=duration_ms,
        error=error,
        chart=chart
    )
    if success:
        # 保存的是问答的历史
        await save_query_history(
            question, final['sql'], final['chart_type'], duration_ms
        )
        await set_cached(question, pay_load.model_dump(
            mode="json"
        ))
    
    return pay_load
