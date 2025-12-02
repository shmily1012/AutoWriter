"""Simple file-based storage for AutoWriter projects."""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Iterable, List, Type, TypeVar

from . import models

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _dump_dataclass(obj) -> dict:
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError("Object is not a dataclass instance")


def _load_dataclass(data: dict, cls: Type[T]) -> T:
    return cls(**data)


class FileStorage:
    """Persist projects as JSON files under a root directory."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "projects").mkdir(exist_ok=True)
        logger.info("Initialized FileStorage at %s", self.root)

    def _project_path(self, project_id: str) -> Path:
        return self.root / "projects" / f"{project_id}.json"

    def save_project(self, project: models.Project) -> None:
        path = self._project_path(project.id)
        payload = _dump_dataclass(project)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        logger.info("Saved project %s to %s", project.id, path)

    def load_project(self, project_id: str) -> models.Project:
        path = self._project_path(project_id)
        if not path.exists():
            raise FileNotFoundError(f"Project '{project_id}' not found")
        data = json.loads(path.read_text())
        logger.info("Loaded project %s from %s", project_id, path)
        return self._project_from_dict(data)

    def list_projects(self) -> List[models.Project]:
        projects: List[models.Project] = []
        for project_file in (self.root / "projects").glob("*.json"):
            data = json.loads(project_file.read_text())
            projects.append(self._project_from_dict(data))
        logger.info("Discovered %d project files under %s", len(projects), self.root)
        return sorted(projects, key=lambda p: p.created_at)

    @staticmethod
    def _project_from_dict(data: dict) -> models.Project:
        def load_list(items: Iterable[dict], cls):
            return [
                _load_dataclass(item, cls)
                for item in items
            ]

        return models.Project(
            name=data["name"],
            author=data["author"],
            description=data.get("description", ""),
            created_at=data.get("created_at"),
            id=data.get("id"),
            characters=load_list(data.get("characters", []), models.Character),
            settings=load_list(data.get("settings", []), models.Setting),
            relationships=load_list(data.get("relationships", []), models.Relationship),
            chapters=load_list(data.get("chapters", []), models.Chapter),
            foreshadows=load_list(data.get("foreshadows", []), models.Foreshadow),
        )
