"""create core tables

Revision ID: a461b42a2b01
Revises:
Create Date: 2024-01-01 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a461b42a2b01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum only if it does not exist to avoid failures on reruns.
    op.execute(
        "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'clue_status') "
        "THEN CREATE TYPE clue_status AS ENUM ('unresolved', 'resolved'); END IF; END $$;"
    )
    # Reuse existing enum without trying to (re)create it during table creation.
    clue_status = postgresql.ENUM(
        "unresolved", "resolved", name="clue_status", create_type=False
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "volumes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE", name="fk_volumes_project"
        ),
        sa.UniqueConstraint("project_id", "index", name="uq_volumes_project_index"),
    )

    op.create_table(
        "chapters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("volume_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE", name="fk_chapters_project"
        ),
        sa.ForeignKeyConstraint(
            ["volume_id"], ["volumes.id"], ondelete="SET NULL", name="fk_chapters_volume"
        ),
        sa.UniqueConstraint("project_id", "index", name="uq_chapters_project_index"),
    )

    op.create_table(
        "characters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("traits", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("arc", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE", name="fk_characters_project"
        ),
        sa.UniqueConstraint("project_id", "name", name="uq_characters_project_name"),
    )

    op.create_table(
        "world_elements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("extra", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            ondelete="CASCADE",
            name="fk_world_elements_project",
        ),
        sa.UniqueConstraint("project_id", "title", name="uq_world_elements_project_title"),
    )

    op.create_table(
        "clues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
        "status",
        clue_status,
        nullable=False,
        server_default="unresolved",
        ),
        sa.Column("introduced_chapter_id", sa.Integer(), nullable=True),
        sa.Column("resolved_chapter_id", sa.Integer(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE", name="fk_clues_project"
        ),
        sa.ForeignKeyConstraint(
            ["introduced_chapter_id"],
            ["chapters.id"],
            ondelete="SET NULL",
            name="fk_clues_introduced_chapter",
        ),
        sa.ForeignKeyConstraint(
            ["resolved_chapter_id"],
            ["chapters.id"],
            ondelete="SET NULL",
            name="fk_clues_resolved_chapter",
        ),
        sa.CheckConstraint(
            "(resolved_chapter_id IS NULL) OR (status = 'resolved')",
            name="ck_clues_resolved_requires_status",
        ),
    )

    op.create_table(
        "chapter_characters",
        sa.Column("chapter_id", sa.Integer(), primary_key=True),
        sa.Column("character_id", sa.Integer(), primary_key=True),
        sa.Column("role_in_chapter", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["chapter_id"], ["chapters.id"], ondelete="CASCADE", name="fk_chapter_characters_chapter"
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
            ondelete="CASCADE",
            name="fk_chapter_characters_character",
        ),
    )


def downgrade() -> None:
    op.drop_table("chapter_characters")
    op.drop_table("clues")
    op.drop_table("world_elements")
    op.drop_table("characters")
    op.drop_table("chapters")
    op.drop_table("volumes")
    op.drop_table("projects")
    op.execute("DROP TYPE IF EXISTS clue_status")
