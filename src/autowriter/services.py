"""Service layer implementing basic project workflows."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import logging

from . import models, storage


logger = logging.getLogger(__name__)


class AutoWriterService:
    """High level operations for working with AutoWriter data."""

    def __init__(self, storage_root: Path):
        self.store = storage.FileStorage(storage_root)
        logger.info("Initialized AutoWriterService with storage root %s", storage_root)

    def create_project(self, name: str, author: str, description: str = "") -> models.Project:
        logger.info("Creating project '%s' for author '%s'", name, author)
        project = models.Project(name=name, author=author, description=description)
        self.store.save_project(project)
        logger.info("Project created with id %s", project.id)
        return project

    def list_projects(self) -> list[models.Project]:
        projects = self.store.list_projects()
        logger.info("Retrieved %d projects from storage", len(projects))
        return projects

    def get_project(self, project_id: str) -> models.Project:
        logger.info("Loading project %s", project_id)
        return self.store.load_project(project_id)

    def add_character(self, project_id: str, name: str, bio: str = "", tags: Optional[Iterable[str]] = None) -> models.Character:
        project = self.get_project(project_id)
        character = models.Character(name=name, bio=bio, tags=list(tags or []))
        project.characters.append(character)
        self.store.save_project(project)
        logger.info("Added character %s (%s) to project %s", character.name, character.id, project_id)
        return character

    def add_setting(self, project_id: str, type: str, name: str, description: str = "") -> models.Setting:
        project = self.get_project(project_id)
        setting = models.Setting(type=type, name=name, description=description)
        project.settings.append(setting)
        self.store.save_project(project)
        logger.info("Added setting %s (%s) to project %s", setting.name, setting.id, project_id)
        return setting

    def add_relationship(self, project_id: str, source_id: str, target_id: str, relation_type: str) -> models.Relationship:
        project = self.get_project(project_id)
        relationship = models.Relationship(source_id=source_id, target_id=target_id, relation_type=relation_type)
        project.relationships.append(relationship)
        self.store.save_project(project)
        logger.info(
            "Added relationship %s between %s and %s in project %s",
            relation_type,
            source_id,
            target_id,
            project_id,
        )
        return relationship

    def add_chapter(self, project_id: str, index: int, title: str, outline: str = "", content: str = "") -> models.Chapter:
        project = self.get_project(project_id)
        chapter = models.Chapter(index=index, title=title, outline=outline, content=content)
        project.chapters.append(chapter)
        project.chapters.sort(key=lambda c: c.index)
        self.store.save_project(project)
        logger.info("Added chapter #%d '%s' (%s) to project %s", chapter.index, chapter.title, chapter.id, project_id)
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
                logger.info("Updated chapter %s in project %s", chapter_id, project_id)
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
        logger.info("Added foreshadow '%s' (%s) to project %s", description, foreshadow.id, project_id)
        return foreshadow
