from typing import Optional

from pydantic import BaseModel


class WorldElementCreate(BaseModel):
    type: str
    title: str
    content: Optional[str] = None
    extra: Optional[dict] = None


class WorldElementUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    extra: Optional[dict] = None


class WorldElementRead(BaseModel):
    id: int
    project_id: int
    type: str
    title: str
    content: Optional[str] = None
    extra: Optional[dict] = None

    class Config:
        from_attributes = True
