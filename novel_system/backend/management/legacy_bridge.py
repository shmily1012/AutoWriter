"""Utilities to bridge legacy FileStorage data with the SQLAlchemy database."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from autowriter import models as legacy_models
from autowriter.storage import FileStorage
from sqlalchemy.orm import Session

from novel_system.backend.db.session import SessionLocal
from novel_system.backend.models import entities

LEGACY_DEFAULT_ROOT = Path.home() / ".autowriter"
EXPORT_DEFAULT_ROOT = Path.home() / ".autowriter_export"


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _character_from_legacy(character: legacy_models.Character) -> entities.Character:
    traits = {"tags": character.tags} if character.tags else None
    return entities.Character(
        name=character.name,
        description=character.bio or None,
        traits=traits,
    )


def _world_elements_from_settings(settings: Iterable[legacy_models.Setting]) -> List[entities.WorldElement]:
    elements: List[entities.WorldElement] = []
    for setting in settings:
        elements.append(
            entities.WorldElement(
                type=setting.type,
                title=setting.name,
                content=setting.description or None,
                extra={"legacy_id": setting.id},
            )
        )
    return elements


def _relationships_to_world_elements(
    relationships: Iterable[legacy_models.Relationship],
) -> List[entities.WorldElement]:
    elements: List[entities.WorldElement] = []
    for relation in relationships:
        elements.append(
            entities.WorldElement(
                type="relationship",
                title=f"{relation.source_id} -> {relation.target_id}",
                content=relation.relation_type,
                extra={
                    "legacy_id": relation.id,
                    "source_id": relation.source_id,
                    "target_id": relation.target_id,
                },
            )
        )
    return elements


def _chapters_from_legacy(
    chapters: Iterable[legacy_models.Chapter],
) -> tuple[List[entities.Chapter], Dict[str, entities.Chapter]]:
    chapter_models: List[entities.Chapter] = []
    chapter_lookup: Dict[str, entities.Chapter] = {}
    for chapter in sorted(chapters, key=lambda c: c.index):
        orm_chapter = entities.Chapter(
            title=chapter.title,
            index=chapter.index,
            content=chapter.content or None,
            summary=chapter.outline or None,
        )
        chapter_models.append(orm_chapter)
        chapter_lookup[chapter.id] = orm_chapter
    return chapter_models, chapter_lookup


def _clues_from_legacy(
    foreshadows: Iterable[legacy_models.Foreshadow],
    chapter_lookup: Dict[str, entities.Chapter],
) -> List[entities.Clue]:
    clues: List[entities.Clue] = []
    for clue in foreshadows:
        status = "resolved" if clue.status == "resolved" else "unresolved"
        introduced = chapter_lookup.get(clue.first_chapter_id) if clue.first_chapter_id else None
        resolved = chapter_lookup.get(clue.resolve_chapter_id) if clue.resolve_chapter_id else None
        clues.append(
            entities.Clue(
                description=clue.description,
                status=status,
                introduced_in=introduced,
                resolved_in=resolved,
                tags=[clue.status] if clue.status else None,
            )
        )
    return clues


def convert_project_from_legacy(legacy_project: legacy_models.Project) -> entities.Project:
    project = entities.Project(
        name=legacy_project.name,
        description=legacy_project.description or None,
    )

    created_at = _parse_datetime(legacy_project.created_at)
    if created_at:
        project.created_at = created_at

    if legacy_project.author:
        project.world_elements.append(
            entities.WorldElement(
                type="meta",
                title="author",
                content=legacy_project.author,
                extra={"legacy_project_id": legacy_project.id},
            )
        )

    project.characters = [_character_from_legacy(c) for c in legacy_project.characters]
    project.world_elements.extend(
        _world_elements_from_settings(legacy_project.settings)
    )
    project.world_elements.extend(
        _relationships_to_world_elements(legacy_project.relationships)
    )

    chapters, lookup = _chapters_from_legacy(legacy_project.chapters)
    project.chapters = chapters
    project.clues = _clues_from_legacy(legacy_project.foreshadows, lookup)
    return project


def _legacy_author(project: entities.Project) -> str:
    for element in project.world_elements:
        if element.type == "meta" and element.title == "author" and element.content:
            return element.content
    return ""


def _legacy_settings(project: entities.Project) -> List[legacy_models.Setting]:
    settings: List[legacy_models.Setting] = []
    for element in project.world_elements:
        if element.type in {"meta", "relationship"}:
            continue
        settings.append(
            legacy_models.Setting(
                type=element.type,
                name=element.title,
                description=element.content or "",
                id=str(element.id) if element.id is not None else None,
            )
        )
    return settings


def _legacy_relationships(project: entities.Project) -> List[legacy_models.Relationship]:
    relationships: List[legacy_models.Relationship] = []
    for element in project.world_elements:
        if element.type != "relationship":
            continue
        extra = element.extra or {}
        source_id = extra.get("source_id")
        target_id = extra.get("target_id")
        relation_type = element.content or extra.get("relation_type")
        if not source_id or not target_id or not relation_type:
            continue
        relationships.append(
            legacy_models.Relationship(
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                id=extra.get("legacy_id"),
            )
        )
    return relationships


def _legacy_characters(project: entities.Project) -> List[legacy_models.Character]:
    characters: List[legacy_models.Character] = []
    for character in project.characters:
        tags: List[str] = []
        if isinstance(character.traits, dict):
            tags_value = character.traits.get("tags")
            if isinstance(tags_value, list):
                tags = [str(tag) for tag in tags_value]
        characters.append(
            legacy_models.Character(
                name=character.name,
                bio=character.description or "",
                tags=tags,
                id=str(character.id),
            )
        )
    return characters


def _legacy_chapters(project: entities.Project) -> tuple[List[legacy_models.Chapter], Dict[int, str]]:
    chapters: List[legacy_models.Chapter] = []
    id_lookup: Dict[int, str] = {}
    for chapter in sorted(project.chapters, key=lambda c: c.index):
        legacy_id = str(chapter.id)
        chapters.append(
            legacy_models.Chapter(
                index=chapter.index,
                title=chapter.title,
                outline=chapter.summary or "",
                content=chapter.content or "",
                id=legacy_id,
            )
        )
        id_lookup[chapter.id] = legacy_id
    return chapters, id_lookup


def _legacy_clues(
    project: entities.Project, id_lookup: Dict[int, str]
) -> List[legacy_models.Foreshadow]:
    clues: List[legacy_models.Foreshadow] = []
    for clue in project.clues:
        status = "resolved" if clue.status == "resolved" else "planned"
        first_chapter = id_lookup.get(clue.introduced_chapter_id) if clue.introduced_chapter_id else None
        resolved = id_lookup.get(clue.resolved_chapter_id) if clue.resolved_chapter_id else None
        clues.append(
            legacy_models.Foreshadow(
                description=clue.description,
                status=status,
                first_chapter_id=first_chapter,
                resolve_chapter_id=resolved,
                id=str(clue.id),
            )
        )
    return clues


def convert_project_to_legacy(project: entities.Project) -> legacy_models.Project:
    chapters, id_lookup = _legacy_chapters(project)
    return legacy_models.Project(
        name=project.name,
        author=_legacy_author(project),
        description=project.description or "",
        created_at=(project.created_at.isoformat() if project.created_at else None),
        id=str(project.id),
        characters=_legacy_characters(project),
        settings=_legacy_settings(project),
        relationships=_legacy_relationships(project),
        chapters=chapters,
        foreshadows=_legacy_clues(project, id_lookup),
    )


def import_legacy_projects(
    root: Path | str | None = None, session: Session | None = None
) -> List[entities.Project]:
    storage = FileStorage(Path(root) if root else LEGACY_DEFAULT_ROOT)
    legacy_projects = storage.list_projects()

    managed_session = session is None
    working_session = session or SessionLocal()
    created: List[entities.Project] = []
    try:
        with working_session.begin():
            for legacy_project in legacy_projects:
                project = convert_project_from_legacy(legacy_project)
                working_session.add(project)
                created.append(project)
    finally:
        if managed_session:
            working_session.close()
    return created


def export_projects_to_legacy_json(
    output_root: Path | str | None = None, session: Session | None = None
) -> List[legacy_models.Project]:
    storage = FileStorage(Path(output_root) if output_root else EXPORT_DEFAULT_ROOT)

    managed_session = session is None
    working_session = session or SessionLocal()
    exported: List[legacy_models.Project] = []
    try:
        projects = working_session.query(entities.Project).all()
        for project in projects:
            legacy_project = convert_project_to_legacy(project)
            storage.save_project(legacy_project)
            exported.append(legacy_project)
    finally:
        if managed_session:
            working_session.close()
    return exported


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Import/export bridge between legacy FileStorage and SQLAlchemy database",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    import_parser = subparsers.add_parser("import", help="Import legacy FileStorage projects into Postgres")
    import_parser.add_argument(
        "--root",
        type=Path,
        default=LEGACY_DEFAULT_ROOT,
        help="Legacy storage root (default: ~/.autowriter)",
    )

    export_parser = subparsers.add_parser("export", help="Export database projects back to legacy JSON")
    export_parser.add_argument(
        "--output",
        type=Path,
        default=EXPORT_DEFAULT_ROOT,
        help="Output directory for legacy-compatible JSON (default: ~/.autowriter_export)",
    )

    args = parser.parse_args(argv)

    if args.command == "import":
        created = import_legacy_projects(root=args.root)
        print(f"Imported {len(created)} legacy project(s) into the database.")
        return 0

    if args.command == "export":
        exported = export_projects_to_legacy_json(output_root=args.output)
        print(f"Exported {len(exported)} project(s) to {args.output}/projects")
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
