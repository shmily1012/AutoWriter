from typing import Optional

from pydantic import BaseModel


class ClueCreate(BaseModel):
    description: str
    status: Optional[str] = None  # unresolved / resolved
    introduced_chapter_id: Optional[int] = None
    resolved_chapter_id: Optional[int] = None
    tags: Optional[list[str]] = None


class ClueUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    introduced_chapter_id: Optional[int] = None
    resolved_chapter_id: Optional[int] = None
    tags: Optional[list[str]] = None


class ClueRead(BaseModel):
    id: int
    project_id: int
    description: str
    status: str
    introduced_chapter_id: Optional[int] = None
    resolved_chapter_id: Optional[int] = None
    tags: Optional[list[str]] = None

    class Config:
        from_attributes = True
