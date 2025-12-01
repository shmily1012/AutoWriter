# Repository Guidelines

## Project Structure & Module Organization
- Core CLI and service code lives in `src/autowriter` (dataclass models, file-based storage, and CLI entrypoint `autowriter`).
- FastAPI/Streamlit scaffold sits under `novel_system`: backend API in `novel_system/backend` (settings in `core/config.py`, routers/models/services folders stubbed), frontend UI in `novel_system/frontend/app.py`, with shared config in `novel_system/config`.
- Tests reside in `tests/` (pytest configured via `pyproject.toml`). Primary system design reference: `docs/system design.md` (read this first); other docs live in `docs/`.
- Packaging is managed by `pyproject.toml`; dependencies and console script wiring are defined there.

## Build, Test, and Development Commands
- Install editable deps: `pip install -e .`
- Run CLI locally (defaults to `~/.autowriter/projects` storage): `autowriter create-project "Title" "Author" --description "..."`.
- Execute tests: `python -m pytest` (uses `tests/` and adds `src/` to `PYTHONPATH`).
- Start backend API: `uvicorn novel_system.backend.main:app --reload --host 0.0.0.0 --port 8000` (honors `.env`).
- Launch Streamlit UI: `streamlit run novel_system/frontend/app.py`.

## Coding Style & Naming Conventions
- Python 3.10+ with type hints everywhere; prefer dataclasses for domain models (see `src/autowriter/models.py`).
- Follow PEP 8 defaults: 4-space indentation, snake_case for functions/variables, PascalCase for classes, UPPER_SNAKE_CASE for constants.
- Keep services thin and storage pure; persist JSON via `FileStorage` to avoid side effects elsewhere.
- No formatter is enforced in config—run `ruff`/`black` locally if desired, but keep diffs minimal and readable.

## Testing Guidelines
- Use pytest; mirror existing patterns in `tests/test_services.py` (tmp_path fixtures for filesystem work).
- Add tests alongside new features or bug fixes; name files `test_*.py` and functions `test_*` with clear assertions.
- For backend additions, prefer fast unit tests over integration; stub network/DB calls where possible.

## Commit & Pull Request Guidelines
- Match existing conventional commit style (`feat: ...`, `docs: ...`, etc.) seen in `git log`.
- PRs should include: concise summary, linked issue (if any), test results (`python -m pytest`), and CLI/API examples when behavior changes. Screenshots welcome for UI updates.
- Keep changes focused and small; update docs and examples when altering CLI flags, storage layout, or API contracts.

## Security & Configuration Tips
- Backend reads config from `.env` (see defaults in `novel_system/backend/core/config.py`); avoid committing real secrets.
- CLI writes user data to `~/.autowriter/projects/*.json`; back up before running destructive scripts.
- When adding external integrations (DB, OpenAI), gate credentials via environment variables and document required values.
