from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from novel_system.backend.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    volumes: Mapped[List["Volume"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    chapters: Mapped[List["Chapter"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    characters: Mapped[List["Character"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    world_elements: Mapped[List["WorldElement"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    clues: Mapped[List["Clue"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Volume(Base):
    __tablename__ = "volumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    project: Mapped["Project"] = relationship(back_populates="volumes")
    chapters: Mapped[List["Chapter"]] = relationship(
        back_populates="volume", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("project_id", "index", name="uq_volumes_project_index"),
    )


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    volume_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("volumes.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    project: Mapped["Project"] = relationship(back_populates="chapters")
    volume: Mapped[Optional["Volume"]] = relationship(back_populates="chapters")
    characters: Mapped[List["ChapterCharacter"]] = relationship(
        back_populates="chapter", cascade="all, delete-orphan"
    )
    introduced_clues: Mapped[List["Clue"]] = relationship(
        foreign_keys="Clue.introduced_chapter_id",
        back_populates="introduced_in",
    )
    resolved_clues: Mapped[List["Clue"]] = relationship(
        foreign_keys="Clue.resolved_chapter_id", back_populates="resolved_in"
    )

    __table_args__ = (
        UniqueConstraint("project_id", "index", name="uq_chapters_project_index"),
    )


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    traits: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    arc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="characters")
    chapters: Mapped[List["ChapterCharacter"]] = relationship(
        back_populates="character", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_characters_project_name"),
    )


class WorldElement(Base):
    __tablename__ = "world_elements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="world_elements")

    __table_args__ = (
        UniqueConstraint("project_id", "title", name="uq_world_elements_project_title"),
    )


ClueStatus = Enum("unresolved", "resolved", name="clue_status")


class Clue(Base):
    __tablename__ = "clues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(ClueStatus, nullable=False, server_default="unresolved")
    introduced_chapter_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )
    resolved_chapter_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )
    tags: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="clues")
    introduced_in: Mapped[Optional["Chapter"]] = relationship(
        foreign_keys=[introduced_chapter_id], back_populates="introduced_clues"
    )
    resolved_in: Mapped[Optional["Chapter"]] = relationship(
        foreign_keys=[resolved_chapter_id], back_populates="resolved_clues"
    )

    __table_args__ = (
        CheckConstraint(
            "(resolved_chapter_id IS NULL) OR (status = 'resolved')",
            name="ck_clues_resolved_requires_status",
        ),
    )


class ChapterCharacter(Base):
    __tablename__ = "chapter_characters"

    chapter_id: Mapped[int] = mapped_column(
        ForeignKey("chapters.id", ondelete="CASCADE"), primary_key=True
    )
    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True
    )
    role_in_chapter: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    chapter: Mapped["Chapter"] = relationship(back_populates="characters")
    character: Mapped["Character"] = relationship(back_populates="chapters")


__all__ = [
    "Project",
    "Volume",
    "Chapter",
    "Character",
    "WorldElement",
    "Clue",
    "ChapterCharacter",
    "ClueStatus",
]
