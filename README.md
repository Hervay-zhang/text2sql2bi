# Text2SQL2BI

经营指标分析应用。后端提供表结构与指标检索、SQL 生成和只读校验，前端展示查询结果和图表。在线展示使用 PostgreSQL。

## 本地运行

1. 在项目根目录执行 `docker compose up -d`，启动 PostgreSQL、Redis 和 Qdrant。
2. 复制 `.env.example` 为 `.env`，按需配置模型服务。
3. 在项目根目录用 Python 3.12 建立虚拟环境，执行 `pip install -e ./backend` 和 `uvicorn app.main:app --port 8001`。
4. 进入 `frontend`，执行 `npm ci` 和 `npm run dev`。

服务探针为 `/api/v1/health`。
