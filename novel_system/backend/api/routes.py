from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from novel_system.backend.api.deps import get_db
from novel_system.backend.models import Chapter, Project, WorldElement
from novel_system.backend.schemas import (
    AIGenerateRequest,
    AIGenerateResponse,
    ChapterCreate,
    ChapterListItem,
    ChapterRead,
    ChapterUpdate,
    ProjectCreate,
    ProjectListItem,
    ProjectRead,
    WorldElementCreate,
    WorldElementRead,
    WorldElementUpdate,
)
from novel_system.backend.services import generate_text
from novel_system.backend.services.vector_store import search_related_text, upsert_embedding

router = APIRouter()


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=list[ProjectListItem])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.id.desc()).all()


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post(
    "/projects/{project_id}/chapters",
    response_model=ChapterRead,
    status_code=status.HTTP_201_CREATED,
)
def create_chapter(project_id: int, payload: ChapterCreate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # index: simple append by count; for real use consider ordering updates.
    existing_count = (
        db.query(Chapter).filter(Chapter.project_id == project_id).count()
    )
    chapter = Chapter(
        project_id=project_id,
        title=payload.title,
        summary=payload.summary,
        content=payload.content,
        index=existing_count,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    # Initial embedding if content present.
    if chapter.content:
        try:
            upsert_embedding(
                project_id=chapter.project_id,
                ref_type="chapter",
                ref_id=chapter.id,
                content=chapter.content,
            )
        except Exception:
            pass
    return chapter


@router.get("/projects/{project_id}/chapters", response_model=list[ChapterListItem])
def list_chapters(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return (
        db.query(Chapter)
        .filter(Chapter.project_id == project_id)
        .order_by(Chapter.index.asc(), Chapter.id.asc())
        .all()
    )


@router.get("/chapters/{chapter_id}", response_model=ChapterRead)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return chapter


@router.put("/chapters/{chapter_id}", response_model=ChapterRead)
def update_chapter(chapter_id: int, payload: ChapterUpdate, db: Session = Depends(get_db)):
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    if payload.title is not None:
        chapter.title = payload.title
    if payload.summary is not None:
        chapter.summary = payload.summary
    if payload.content is not None:
        chapter.content = payload.content

    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    # Update embeddings for this chapter content (best effort).
    try:
        upsert_embedding(
            project_id=chapter.project_id,
            ref_type="chapter",
            ref_id=chapter.id,
            content=chapter.content or "",
        )
    except Exception:
        # Do not block API on embedding failure; log if needed.
        pass

    return chapter


@router.post(
    "/projects/{project_id}/world-elements",
    response_model=WorldElementRead,
    status_code=status.HTTP_201_CREATED,
)
def create_world_element(
    project_id: int, payload: WorldElementCreate, db: Session = Depends(get_db)
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    we = WorldElement(
        project_id=project_id,
        type=payload.type,
        title=payload.title,
        content=payload.content,
        extra=payload.extra,
    )
    db.add(we)
    db.commit()
    db.refresh(we)
    try:
        upsert_embedding(
            project_id=project_id,
            ref_type="world",
            ref_id=we.id,
            content=we.content or "",
        )
    except Exception:
        pass
    return we


@router.get("/projects/{project_id}/world-elements", response_model=list[WorldElementRead])
def list_world_elements(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return (
        db.query(WorldElement)
        .filter(WorldElement.project_id == project_id)
        .order_by(WorldElement.id.desc())
        .all()
    )


@router.put("/world-elements/{element_id}", response_model=WorldElementRead)
def update_world_element(element_id: int, payload: WorldElementUpdate, db: Session = Depends(get_db)):
    we = db.get(WorldElement, element_id)
    if not we:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World element not found")

    if payload.type is not None:
        we.type = payload.type
    if payload.title is not None:
        we.title = payload.title
    if payload.content is not None:
        we.content = payload.content
    if payload.extra is not None:
        we.extra = payload.extra

    db.add(we)
    db.commit()
    db.refresh(we)
    try:
        upsert_embedding(
            project_id=we.project_id,
            ref_type="world",
            ref_id=we.id,
            content=we.content or "",
        )
    except Exception:
        pass
    return we


def _chapter_ai_action(
    chapter_id: int,
    mode: str,
    payload: AIGenerateRequest,
    db: Session,
) -> AIGenerateResponse:
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    base_prompt = payload.prompt or ""
    # Optionally prepend existing chapter content to give context.
    if chapter.content:
        base_prompt = f"Existing content:\n{chapter.content}\n\nUser prompt:\n{base_prompt}"

    try:
        text = generate_text(
            prompt=base_prompt,
            mode=mode,
            system_prompt=payload.system_prompt,
            model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return AIGenerateResponse(generated_text=text)


@router.post("/ai/search", response_model=list[dict])
def ai_search(project_id: int, query: str, top_k: int = 5):
    return search_related_text(project_id=project_id, query=query, top_k=top_k)


@router.post("/chapters/{chapter_id}/ai/expand", response_model=AIGenerateResponse)
def ai_expand(chapter_id: int, payload: AIGenerateRequest, db: Session = Depends(get_db)):
    return _chapter_ai_action(chapter_id, mode="expand", payload=payload, db=db)


@router.post("/chapters/{chapter_id}/ai/rewrite", response_model=AIGenerateResponse)
def ai_rewrite(chapter_id: int, payload: AIGenerateRequest, db: Session = Depends(get_db)):
    return _chapter_ai_action(chapter_id, mode="rewrite", payload=payload, db=db)


@router.post("/chapters/{chapter_id}/ai/draft", response_model=AIGenerateResponse)
def ai_draft(chapter_id: int, payload: AIGenerateRequest, db: Session = Depends(get_db)):
    return _chapter_ai_action(chapter_id, mode="draft", payload=payload, db=db)


@router.post("/ai/generate", response_model=AIGenerateResponse)
def ai_generate(payload: AIGenerateRequest):
    try:
        text = generate_text(
            prompt=payload.prompt,
            mode=payload.mode,
            system_prompt=payload.system_prompt,
            model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    return AIGenerateResponse(generated_text=text)
