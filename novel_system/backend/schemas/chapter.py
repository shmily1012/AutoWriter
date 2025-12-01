from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChapterCreate(BaseModel):
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None


class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None


class ChapterRead(BaseModel):
    id: int
    project_id: int
    volume_id: Optional[int] = None
    title: str
    index: int
    summary: Optional[str] = None
    content: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChapterListItem(ChapterRead):
    pass
