import asyncio
import selectors

from psycopg_pool import AsyncConnectionPool
from win32timezone import now

from app.core.config import settings

pool =AsyncConnectionPool(
    settings.POSTGRES_DSN, #读取账号DSN
    min_size=10, #池最小保持1个连接
    max_size=10, #池最大10个数据库连接
    open=False, # 创建对象的时候  不要自动打开连接，手动await.open()
    
)

async  def create_table():
    async with pool.connection() as conn,conn.cursor() as cur:
        await cur.execute("""
        CREATE TABLE IF NOT EXISTS articles(
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            content TEXT,
            create_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        print("表创建成功")

#新增一条数据
async def insert_data(title,content):
    async with pool.connection() as conn,conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO articles(title,content) VALUES(%s,%s) RETURNING id;",
            (title,content)
    )
        row = await cur.fetchone()
        #row其实是一个元组(2,)
        # print(now)
        return row[0]

# 批量插入
async def batch_insert(items: list[tuple]):
    """批量插入"""
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.executemany(
                "INSERT INTO articles(title, content) VALUES(%s, %s)",
                items
            )
            await conn.commit()
            
async def query_all():
    """查询全部"""
    async with pool.connection() as conn, conn.cursor() as cur:
        await cur.execute("SELECT id, title, content FROM articles ORDER BY id DESC;")
        rows = await cur.fetchall()
        print(rows)
        #[(1, '俄乌战争', '即将结束.....'), (2, '俄乌战争', '即将结束.....'), (3, '标题A', '内容A'), (4, '标题B', '内容B')]
        
        cols = [describe.name for describe in cur.description]
        print(cols) #['id', 'title', 'content']
        for row in rows:
            for tup1 in zip(cols, row, strict=True):
                print(tup1)
     
     
     
#修改数据
async def update_article(art_id: int, new_title: str):
    async with pool.connection() as conn, conn.cursor() as cur:
            await cur.execute(
                "UPDATE articles SET title=%s WHERE id=%s",
                (new_title, art_id)
            )
            await conn.commit()
            return cur.rowcount
    
#删除数据
async def delete_article(art_id:int):
    async with pool.connection() as conn,conn.cursor() as cur:
        await cur.execute("DELETE FROM articles WHERE id=%s", (art_id,))
        await conn.commit()
        return cur.rowcount
    
    
async def main():
    # 手动开启连接池，wait=True：如果拿不到资源就阻塞等待，不抛异常
    await pool.open(wait=True)
    # await create_table()    # 创建表
    
    #在表中新增一条数据
    # print(await insert_data("俄乌战争","即将结束....."))
    
    #批量插入
    # await batch_insert([
    #     ("标题A", "内容A"),
    #     ("标题B", "内容B"),
    # ])
    
    #查询全部
    # await query_all()
    
    #修改数据
    # num=await update_article(2,'新三国演义')
   
   
    num=await delete_article(2)
    print(num)
if __name__ =="__main__":
   
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())
    )