"""Service layer implementing basic project workflows."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from . import models, storage


class AutoWriterService:
    """High level operations for working with AutoWriter data."""

    def __init__(self, storage_root: Path):
        self.store = storage.FileStorage(storage_root)

    def create_project(self, name: str, author: str, description: str = "") -> models.Project:
        project = models.Project(name=name, author=author, description=description)
        self.store.save_project(project)
        return project

    def list_projects(self) -> list[models.Project]:
        return self.store.list_projects()

    def get_project(self, project_id: str) -> models.Project:
        return self.store.load_project(project_id)

    def add_character(self, project_id: str, name: str, bio: str = "", tags: Optional[Iterable[str]] = None) -> models.Character:
        project = self.get_project(project_id)
        character = models.Character(name=name, bio=bio, tags=list(tags or []))
        project.characters.append(character)
        self.store.save_project(project)
        return character

    def add_setting(self, project_id: str, type: str, name: str, description: str = "") -> models.Setting:
        project = self.get_project(project_id)
        setting = models.Setting(type=type, name=name, description=description)
        project.settings.append(setting)
        self.store.save_project(project)
        return setting

    def add_relationship(self, project_id: str, source_id: str, target_id: str, relation_type: str) -> models.Relationship:
        project = self.get_project(project_id)
        relationship = models.Relationship(source_id=source_id, target_id=target_id, relation_type=relation_type)
        project.relationships.append(relationship)
        self.store.save_project(project)
        return relationship

    def add_chapter(self, project_id: str, index: int, title: str, outline: str = "", content: str = "") -> models.Chapter:
        project = self.get_project(project_id)
        chapter = models.Chapter(index=index, title=title, outline=outline, content=content)
        project.chapters.append(chapter)
        project.chapters.sort(key=lambda c: c.index)
        self.store.save_project(project)
        return chapter

    def update_chapter(self, project_id: str, chapter_id: str, *, outline: Optional[str] = None, content: Optional[str] = None) -> models.Chapter:
        project = self.get_project(project_id)
        for chapter in project.chapters:
            if chapter.id == chapter_id:
                if outline is not None:
                    chapter.outline = outline
                if content is not None:
                    chapter.content = content
                self.store.save_project(project)
                return chapter
        raise ValueError(f"Chapter {chapter_id} not found in project {project_id}")

    def add_foreshadow(self, project_id: str, description: str, status: str = "planned", *, first_chapter_id: str | None = None, resolve_chapter_id: str | None = None) -> models.Foreshadow:
        project = self.get_project(project_id)
        foreshadow = models.Foreshadow(
            description=description,
            status=status,
            first_chapter_id=first_chapter_id,
            resolve_chapter_id=resolve_chapter_id,
        )
        project.foreshadows.append(foreshadow)
        self.store.save_project(project)
        return foreshadow
