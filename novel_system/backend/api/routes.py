from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from novel_system.backend.api.deps import get_db
from novel_system.backend.models import Chapter, Project
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
)
from novel_system.backend.services import generate_text

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
    return chapter


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
