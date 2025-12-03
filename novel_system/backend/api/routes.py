from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from novel_system.backend.api.deps import get_db
from novel_system.backend.models import (
    Chapter,
    ChapterCharacter,
    Character,
    Clue,
    Project,
    WorldElement,
)
from novel_system.backend.schemas import (
    AIGenerateRequest,
    AIGenerateResponse,
    ChapterAnalysisResult,
    ClueCreate,
    ClueRead,
    ClueUpdate,
    ChapterCreate,
    ChapterListItem,
    ChapterRead,
    ChapterUpdate,
    ProjectCreate,
    ProjectListItem,
    ProjectRead,
    CharacterCreate,
    CharacterRead,
    CharacterUpdate,
    WorldElementCreate,
    WorldElementRead,
    WorldElementUpdate,
)
from novel_system.backend.services import generate_text
from novel_system.backend.services.vector_store import search_related_text, upsert_embedding
from novel_system.backend.services.prompts import (
    CHARACTER_EXTRACT_PROMPT,
    CHAPTER_ANALYSIS_PROMPT,
    PLOT_SUGGEST_PROMPT,
)

router = APIRouter()


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    db.delete(project)
    db.commit()
    return None


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


@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    try:
        upsert_embedding(project_id=chapter.project_id, ref_type="chapter", ref_id=chapter.id, content="")
    except Exception:
        pass
    db.delete(chapter)
    db.commit()
    return None


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

    # Try to extract appearing characters and sync chapter_characters.
    if chapter.content:
        try:
            names = extract_characters_from_text(chapter.project_id, chapter.content)
            sync_chapter_characters(db, chapter, names)
        except Exception:
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


@router.delete("/world-elements/{element_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_world_element(element_id: int, db: Session = Depends(get_db)):
    we = db.get(WorldElement, element_id)
    if not we:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World element not found")
    try:
        upsert_embedding(project_id=we.project_id, ref_type="world", ref_id=we.id, content="")
    except Exception:
        pass
    db.delete(we)
    db.commit()
    return None


@router.post(
    "/projects/{project_id}/characters",
    response_model=CharacterRead,
    status_code=status.HTTP_201_CREATED,
)
def create_character(
    project_id: int, payload: CharacterCreate, db: Session = Depends(get_db)
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    character = Character(
        project_id=project_id,
        name=payload.name,
        role=payload.role,
        description=payload.description,
        traits=payload.traits,
        arc=payload.arc,
    )
    db.add(character)
    db.commit()
    db.refresh(character)
    try:
        upsert_embedding(
            project_id=project_id,
            ref_type="character",
            ref_id=character.id,
            content=character.description or "",
        )
    except Exception:
        pass
    return character


@router.get("/projects/{project_id}/characters", response_model=list[CharacterRead])
def list_characters(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return (
        db.query(Character)
        .filter(Character.project_id == project_id)
        .order_by(Character.id.desc())
        .all()
    )


@router.put("/characters/{character_id}", response_model=CharacterRead)
def update_character(character_id: int, payload: CharacterUpdate, db: Session = Depends(get_db)):
    ch = db.get(Character, character_id)
    if not ch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    if payload.name is not None:
        ch.name = payload.name
    if payload.role is not None:
        ch.role = payload.role
    if payload.description is not None:
        ch.description = payload.description
    if payload.traits is not None:
        ch.traits = payload.traits
    if payload.arc is not None:
        ch.arc = payload.arc

    db.add(ch)
    db.commit()
    db.refresh(ch)
    try:
        upsert_embedding(
            project_id=ch.project_id,
            ref_type="character",
            ref_id=ch.id,
            content=ch.description or "",
        )
    except Exception:
        pass
    return ch


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: int, db: Session = Depends(get_db)):
    ch = db.get(Character, character_id)
    if not ch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    try:
        upsert_embedding(project_id=ch.project_id, ref_type="character", ref_id=ch.id, content="")
    except Exception:
        pass
    db.delete(ch)
    db.commit()
    return None


@router.post("/characters/{character_id}/ai/improve", response_model=AIGenerateResponse)
def ai_improve_character(character_id: int, payload: AIGenerateRequest, db: Session = Depends(get_db)):
    ch = db.get(Character, character_id)
    if not ch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    base = (
        f"Character: {ch.name}\nRole: {ch.role or ''}\nSnapshot: {ch.description or ''}\nArc: {ch.arc or ''}\n"
    )
    prompt = f"{base}\n\nUser request: {payload.prompt}"
    system_prompt = payload.system_prompt
    persona_tone = []
    if payload.persona:
        persona_tone.append(f"Author persona: {payload.persona}.")
    if payload.tone:
        persona_tone.append(f"Tone: {payload.tone}.")
    if persona_tone:
        system_prompt = f"{system_prompt or ''} {' '.join(persona_tone)}".strip()

    text = generate_text(
        prompt=prompt,
        mode=payload.mode or "character_improve",
        system_prompt=system_prompt,
        model=payload.model,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
        role=payload.role,
    )
    return AIGenerateResponse(generated_text=text)


# -------- Clues --------
@router.post(
    "/projects/{project_id}/clues",
    response_model=ClueRead,
    status_code=status.HTTP_201_CREATED,
)
def create_clue(project_id: int, payload: ClueCreate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    clue = Clue(
        project_id=project_id,
        description=payload.description,
        status=payload.status or "unresolved",
        introduced_chapter_id=payload.introduced_chapter_id,
        resolved_chapter_id=payload.resolved_chapter_id,
        tags=payload.tags,
    )
    db.add(clue)
    db.commit()
    db.refresh(clue)
    return clue


@router.get("/projects/{project_id}/clues", response_model=list[ClueRead])
def list_clues(project_id: int, status_filter: str | None = None, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    q = db.query(Clue).filter(Clue.project_id == project_id)
    if status_filter in {"unresolved", "resolved"}:
        q = q.filter(Clue.status == status_filter)
    return q.order_by(Clue.id.desc()).all()


@router.put("/clues/{clue_id}", response_model=ClueRead)
def update_clue(clue_id: int, payload: ClueUpdate, db: Session = Depends(get_db)):
    clue = db.get(Clue, clue_id)
    if not clue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clue not found")
    if payload.description is not None:
        clue.description = payload.description
    if payload.status is not None:
        clue.status = payload.status
    if payload.introduced_chapter_id is not None:
        clue.introduced_chapter_id = payload.introduced_chapter_id
    if payload.resolved_chapter_id is not None:
        clue.resolved_chapter_id = payload.resolved_chapter_id
    if payload.tags is not None:
        clue.tags = payload.tags
    db.add(clue)
    db.commit()
    db.refresh(clue)
    return clue


@router.delete("/clues/{clue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_clue(clue_id: int, db: Session = Depends(get_db)):
    clue = db.get(Clue, clue_id)
    if not clue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clue not found")
    db.delete(clue)
    db.commit()
    return None


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

    system_prompt = payload.system_prompt
    persona_tone = []
    if payload.persona:
        persona_tone.append(f"Author persona: {payload.persona}.")
    if payload.tone:
        persona_tone.append(f"Tone: {payload.tone}.")
    if persona_tone:
        system_prompt = f"{system_prompt or ''} {' '.join(persona_tone)}".strip()

    try:
        text = generate_text(
            prompt=base_prompt,
            mode=mode,
            system_prompt=system_prompt,
            model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            role=payload.role,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return AIGenerateResponse(generated_text=text)


@router.post("/ai/search", response_model=list[dict])
def ai_search(project_id: int, query: str, top_k: int = 5):
    raw = search_related_text(project_id=project_id, query=query, top_k=top_k)
    formatted = []
    for item in raw:
        content = item.get("content") or ""
        ref_type = item.get("type") or "note"
        ref_id = item.get("ref_id")
        title = f"{ref_type.title()} #{ref_id}" if ref_id is not None else ref_type.title()
        formatted.append(
            {
                "title": title,
                "snippet": content[:200],
                "content": content,
                "type": ref_type,
                "ref_id": ref_id,
                "score": item.get("score"),
            }
        )
    return formatted


@router.post("/chapters/{chapter_id}/ai/expand", response_model=AIGenerateResponse)
def ai_expand(chapter_id: int, payload: AIGenerateRequest, db: Session = Depends(get_db)):
    return _chapter_ai_action(chapter_id, mode="expand", payload=payload, db=db)


@router.post("/chapters/{chapter_id}/ai/rewrite", response_model=AIGenerateResponse)
def ai_rewrite(chapter_id: int, payload: AIGenerateRequest, db: Session = Depends(get_db)):
    return _chapter_ai_action(chapter_id, mode="rewrite", payload=payload, db=db)


@router.post("/chapters/{chapter_id}/ai/draft", response_model=AIGenerateResponse)
def ai_draft(chapter_id: int, payload: AIGenerateRequest, db: Session = Depends(get_db)):
    return _chapter_ai_action(chapter_id, mode="draft", payload=payload, db=db)


@router.post("/chapters/{chapter_id}/ai/polish", response_model=AIGenerateResponse)
def ai_polish(chapter_id: int, payload: AIGenerateRequest, db: Session = Depends(get_db)):
    return _chapter_ai_action(chapter_id, mode="polish", payload=payload, db=db)


def analyze_chapter_content(chapter: Chapter, project: Project, db: Session) -> dict:
    # Prepare context
    chars = db.query(Character).filter(Character.project_id == project.id).all()
    worlds = db.query(WorldElement).filter(WorldElement.project_id == project.id).all()
    char_brief = [
        f"{c.name} ({c.role or 'role unknown'}): {(c.description or '')[:80]}"
        for c in chars
    ]
    world_brief = [
        f"{w.type or 'world'} - {w.title}: {(w.content or '')[:80]}"
        for w in worlds
    ]
    prompt = CHAPTER_ANALYSIS_PROMPT.format(
        character_brief="\n".join(char_brief) or "None",
        world_brief="\n".join(world_brief) or "None",
        chapter_content=chapter.content,
    )
    text = generate_text(
        prompt=prompt,
        mode="analyze_chapter",
        role="world_consultant",
        temperature=0,
    )
    return parse_json_response(text)


def upsert_world_facts(db: Session, project_id: int, facts: list[str]) -> None:
    for fact in facts:
        if not fact.strip():
            continue
        title = fact[:50]
        exists = (
            db.query(WorldElement)
            .filter(WorldElement.project_id == project_id, WorldElement.title == title)
            .first()
        )
        if exists:
            continue
        we = WorldElement(project_id=project_id, type="fact", title=title, content=fact)
        db.add(we)
        db.commit()
        db.refresh(we)
        try:
            upsert_embedding(project_id=project_id, ref_type="world", ref_id=we.id, content=fact)
        except Exception:
            pass


def upsert_clues(db: Session, project_id: int, chapter_id: int, clues: list[str]) -> None:
    for clue in clues:
        if not clue.strip():
            continue
        c = Clue(
            project_id=project_id,
            description=clue,
            status="unresolved",
            introduced_chapter_id=chapter_id,
        )
        db.add(c)
    db.commit()


@router.post("/chapters/{chapter_id}/analyze", response_model=dict)
def analyze_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    project = db.get(Project, chapter.project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if not chapter.content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chapter has no content")

    raw = analyze_chapter_content(chapter, project, db)
    result = ChapterAnalysisResult.from_dict(raw)
    characters_appeared = result.characters_appeared
    world_facts = result.world_facts
    possible_clues = result.possible_clues

    try:
        sync_chapter_characters(db, chapter, characters_appeared)
    except Exception:
        pass
    try:
        upsert_world_facts(db, project.id, world_facts)
    except Exception:
        pass
    try:
        upsert_clues(db, project.id, chapter.id, possible_clues)
    except Exception:
        pass

    return {
        "characters_appeared": characters_appeared,
        "world_facts": world_facts,
        "possible_clues": possible_clues,
    }


# -------- Characters --------
def extract_characters_from_text(project_id: int, content: str) -> list[str]:
    prompt = CHARACTER_EXTRACT_PROMPT.format(chapter_content=content)
    text = generate_text(prompt=prompt, mode="extract_characters", model=None, temperature=0, role="world_consultant")
    names = [line.strip() for line in text.splitlines() if line.strip()]
    return names


def sync_chapter_characters(db: Session, chapter: Chapter, names: list[str]) -> None:
    if not names:
        return
    chars = (
        db.query(Character)
        .filter(Character.project_id == chapter.project_id, Character.name.in_(names))
        .all()
    )
    # Clear existing links
    db.query(ChapterCharacter).filter(ChapterCharacter.chapter_id == chapter.id).delete()
    for ch in chars:
        db.add(ChapterCharacter(chapter_id=chapter.id, character_id=ch.id))
    db.commit()


def parse_json_response(text: str) -> dict:
    import json
    import re

    # Try raw JSON first
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to extract JSON block from code fences
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return {}


@router.post("/ai/generate", response_model=AIGenerateResponse)
def ai_generate(payload: AIGenerateRequest):
    system_prompt = payload.system_prompt
    persona_tone = []
    if payload.persona:
        persona_tone.append(f"Author persona: {payload.persona}.")
    if payload.tone:
        persona_tone.append(f"Tone: {payload.tone}.")
    if persona_tone:
        system_prompt = f"{system_prompt or ''} {' '.join(persona_tone)}".strip()

    try:
        text = generate_text(
            prompt=payload.prompt,
            mode=payload.mode,
            system_prompt=system_prompt,
            model=payload.model,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            role=payload.role,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    return AIGenerateResponse(generated_text=text)
