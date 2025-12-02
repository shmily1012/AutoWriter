# AutoWriter – AI 辅助长篇创作工作台

一个集项目管理、章节写作、世界观与人物设定、伏笔追踪、向量检索与 OpenAI 能力于一体的原型工具。后端 FastAPI + PostgreSQL + Redis(含向量索引)，前端 Streamlit。

## 快速开始
### 安装
```bash
pip install -e .
```
准备 `.env`（参考 `.env.example`），至少配置：
- `POSTGRES_DSN` 连接可用的 Postgres
- `REDIS_URL` 指向 Redis Stack（需支持 RediSearch）
- `OPENAI_API_KEY`（可选，启用 AI/嵌入）

本地依赖（可选）：`bash novel_system/scripts/start_services.sh` 启动 Postgres16 + Redis Stack 容器。

### 运行
后端：
```bash
uvicorn novel_system.backend.main:app --host 0.0.0.0 --port 8000
```
前端：
```bash
streamlit run novel_system/frontend/app.py
```
首个健康检查：`GET /ping` 应返回 `{"status":"ok"}`。

### 数据库
- 迁移：`alembic upgrade head`（确保 `.env` DSN 可用）
- SQLAlchemy 模型：`novel_system/backend/models/entities.py`
- Alembic 配置：`alembic.ini` + `migrations/`

### 从本地 FileStorage 迁移
旧版 CLI 将项目存放在 `~/.autowriter/projects/*.json` 下。为了迁移到当前 FastAPI + Postgres 模型，可使用管理脚本：

```bash
# 将 legacy JSON 导入数据库（依赖 .env 中的 POSTGRES_DSN）
python -m novel_system.backend.management.legacy_bridge import --root ~/.autowriter

# 从数据库导出为 legacy 结构，方便回滚/备份
python -m novel_system.backend.management.legacy_bridge export --output ~/.autowriter_export
```

导入时会尝试保留章节顺序、角色标签（写入 traits.tags）、设定（转换为 WorldElement）、伏笔状态等信息；导出时会重新生成 legacy JSON 以便老版 CLI 继续读取。

## 功能总览
- 项目/章节：CRUD，章节编辑支持 AI 扩写/润色/草稿，章节分析自动提取人物/设定/伏笔并写入关联表。
- 世界观：创建/编辑条目，嵌入存入 Redis，支持相似检索。
- 人物：角色卡与弧线，AI 优化设定，章节自动抽取人物出场并关联。
- 伏笔中心：创建/过滤/更新状态，标记埋伏/回收章节，章节内可一键标记伏笔。
- 向量检索：章节/设定/人物描述分块嵌入 Redis（HNSW，索引 `idx_novel_chunks`），`/ai/search` 返回相关片段。
- AI 服务：统一封装 OpenAI（角色可选：world_consultant/plot_coach/style_polish 等），prompt 模板集中管理。
- 写作 UI：Streamlit 多 Tab（章节、世界观、人物、伏笔），右侧“智能提示栏”提供相关设定/人物/伏笔提醒与剧情建议。

## 主要 API（摘选）
- 项目/章节：`POST /projects`，`GET /projects/{id}`，`POST /projects/{id}/chapters`，`PUT /chapters/{id}`
- 章节 AI：`POST /chapters/{id}/ai/{expand|rewrite|draft}`，分析 `POST /chapters/{id}/analyze`
- 世界观：`POST /projects/{id}/world-elements`，`GET /projects/{id}/world-elements`，`PUT /world-elements/{id}`
- 人物：`POST /projects/{id}/characters`，`GET /projects/{id}/characters`，`PUT /characters/{id}`，AI 优化 `POST /characters/{id}/ai/improve`
- 伏笔：`POST /projects/{id}/clues`，`GET /projects/{id}/clues?status_filter=...`，`PUT /clues/{id}`
- 通用生成与检索：`POST /ai/generate`，`POST /ai/search`

## 目录结构（节选）
```
novel_system/
  backend/
    main.py                  # FastAPI 入口
    api/routes.py            # API 路由
    models/entities.py       # ORM 模型
    schemas/                 # Pydantic 模型
    services/
      openai_client.py       # OpenAI 封装（角色化）
      prompts.py             # 大 prompt 模板
      vector_store.py        # Redis 向量索引封装
  frontend/
    app.py                   # Streamlit UI
  scripts/
    start_services.sh        # 本地 PG/Redis
```

## 开发小贴士
- 需要 AI 功能请提供有效 `OPENAI_API_KEY`；嵌入模型可调 `OPENAI_EMBEDDING_MODEL`。
- Redis 需为 Redis Stack（支持 RediSearch/HNSW）；索引自动按维度创建。
- 章节编辑右侧“获取智能提示”会调向量检索与 GPT，若无 key 会报错提示。***
