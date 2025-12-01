# AutoWriter

A lightweight prototype for managing single-author web novel projects with Python.

## Features
- File-based project storage with JSON serialization
- CLI for creating projects, adding characters/chapters/foreshadows, and inspecting project data
- Extensible service layer matching the system design document for future AI integrations

## Installation
```
pip install -e .
```

## Usage
Create a project stored under the default `~/.autowriter` directory:
```
autowriter create-project "My Novel" "Author Name" --description "Epic saga"
```

List and inspect projects:
```
autowriter list
autowriter show <project_id>
```

Add core data:
```
autowriter add-character <project_id> "Hero" --bio "Protagonist" --tags brave loyal
autowriter add-chapter <project_id> 1 "Prologue" --outline "Setup" --content "Once upon a time"
autowriter add-foreshadow <project_id> "Mysterious key" --status hinted --first-chapter-id <chapter_id>
```

## Development
Run tests with:
```
python -m pytest
```

## Novel system scaffold (FastAPI + Streamlit)
- Backend: FastAPI app lives under `novel_system/backend`. Run from repo root with `uvicorn novel_system.backend.main:app --reload --host 0.0.0.0 --port 8000`.
- Healthcheck: `GET /ping` returns `{"status": "ok"}` when the server is up.
- Frontend: Streamlit UI at `novel_system/frontend/app.py`, run with `streamlit run novel_system/frontend/app.py`. Supports project/chapters CRUD and AI 写作（扩写/润色/草稿）操作。
- Configuration: Copy/edit `.env` for `POSTGRES_DSN`, `REDIS_URL`, `OPENAI_API_KEY`, etc. Defaults are included for local development.

## Database & migrations
- SQLAlchemy models live in `novel_system/backend/models/entities.py`; Base/engine/session helpers in `novel_system/backend/db/`.
- Alembic is configured under `migrations/` with `alembic.ini` in repo root; ensure `POSTGRES_DSN` is set in `.env`.
- Run migrations: `alembic upgrade head` (from repo root, using the virtualenv where dependencies are installed). Alembic uses the DSN from `.env` via `pydantic-settings`; ensure it’s reachable.
- Quick insert example (Python REPL):
  ```python
  from novel_system.backend.db import SessionLocal, engine, Base
  from novel_system.backend.models import Project, Chapter

  Base.metadata.create_all(bind=engine)  # optional; migrations preferred
  with SessionLocal() as session:
      project = Project(name="Test Project")
      chapter = Chapter(title="Chapter 1", project=project, summary="Hello")
      session.add(project)
      session.commit()
```

## Local Postgres + Redis via Docker
- Script: `novel_system/scripts/start_services.sh` (uses Docker; defaults to Postgres 16 and Redis Stack).
- Environment overrides: set in `.env` or export before running (e.g., `PG_PORT`, `REDIS_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `REDIS_IMAGE`).
- Start services: `bash novel_system/scripts/start_services.sh`
- After containers are up, run `alembic upgrade head`, then start FastAPI/Streamlit as above.

## API quick refs
- Projects/Chapters: `POST /projects`, `GET /projects`, `POST /projects/{id}/chapters`, `PUT /chapters/{id}`, etc.
- AI generation: `POST /ai/generate` (prompt/mode), or chapter-specific `POST /chapters/{id}/ai/{expand|rewrite|draft}` (uses OpenAI key from `.env`).
- Vector search: embeddings stored in Redis (RediSearch index `idx_novel_chunks`) per chapter chunks. Helper service: `novel_system/backend/services/vector_store.py` with `search_related_text(project_id, query, top_k=5)`.
