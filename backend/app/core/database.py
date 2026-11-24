from psycopg_pool import AsyncConnectionPool

from app.core.config import settings

# 全局变量，保存连接池实例；初始None代表还没初始化
_meta_pool: AsyncConnectionPool | None = None
_query_pool: AsyncConnectionPool | None = None


# 设计模式：**异步懒加载单例**，第一次调用才创建池子；后续调用直接复用已经建好的池。
async def get_meta_pool() -> AsyncConnectionPool:
    global _meta_pool   # 声明使用全局变量，不是函数内局部变量
    if _meta_pool is None: # 单例模式：池子只初始化一次
        _meta_pool = AsyncConnectionPool(
            settings.POSTGRES_DSN, # 读写账号DSN
            min_size=1,     # 池最少保持1个连接
            max_size=10,    # 池最大10个数据库连接
            open=False,     # 创建对象的时候**不要自动打开连接**，手动await .open()
        )
        # 手动开启连接池，wait=True：如果拿不到资源就阻塞等待，不抛异常
        await _meta_pool.open(wait=True)
    return _meta_pool

# 逻辑完全同上，只是使用**只读数据库账号**，用于业务查询，实现读写分离。
async def get_query_pool() -> AsyncConnectionPool:
    global _query_pool
    if _query_pool is None:
        _query_pool = AsyncConnectionPool(
            settings.QUERY_POSTGRES_DSN,
            min_size=1,
            max_size=10,
            open=False,
        )
        await _query_pool.open(wait=True)
    return _query_pool

# - **生命周期函数**，项目退出时调用（例如 FastAPI lifespan 事件）
#- 关闭池子并且把全局变量置为`None`；置空后，如果后续又调用`get_meta_pool()`，会重新新建连接池。
async def close_pools() -> None:
    global _meta_pool, _query_pool
    if _query_pool:
        await _query_pool.close() # 优雅关闭连接池，释放所有数据库连接
        _query_pool = None        # 置空，下次调用get_xxx_pool会重新初始化
    if _meta_pool:
        await _meta_pool.close()
        _meta_pool = None


# - 健康检查接口用：返回 True 数据库正常，False 数据库异常。
# - `async with pool.connection()`：从连接池借出连接，离开 with 块自动归还连接，**不要手动 close 连接**，连接还给池子复用
async def ping_database() -> bool:
    try:
        pool = await get_meta_pool()
        # 从池子拿一个连接，再拿到cursor游标
        async with pool.connection() as conn, conn.cursor() as cur:
            await cur.execute("SELECT 1") # 最简单心跳SQL，验证数据库活的
            await cur.fetchone()
        return True
    except Exception: # 任何异常：连不上、超时、权限错全部捕获
        return False
