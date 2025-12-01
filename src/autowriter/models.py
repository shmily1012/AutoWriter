"""Domain models used by the AutoWriter prototype."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


@dataclass
class Character:
    name: str
    bio: str = ""
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=_uuid)


@dataclass
class Setting:
    type: str
    name: str
    description: str = ""
    id: str = field(default_factory=_uuid)


@dataclass
class Relationship:
    source_id: str
    target_id: str
    relation_type: str
    id: str = field(default_factory=_uuid)


@dataclass
class Chapter:
    index: int
    title: str
    outline: str = ""
    content: str = ""
    id: str = field(default_factory=_uuid)


@dataclass
class Foreshadow:
    description: str
    status: str = "planned"
    first_chapter_id: Optional[str] = None
    resolve_chapter_id: Optional[str] = None
    id: str = field(default_factory=_uuid)


@dataclass
class Project:
    name: str
    author: str
    description: str = ""
    created_at: str = field(default_factory=_now)
    id: str = field(default_factory=_uuid)
    characters: List[Character] = field(default_factory=list)
    settings: List[Setting] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    chapters: List[Chapter] = field(default_factory=list)
    foreshadows: List[Foreshadow] = field(default_factory=list)
