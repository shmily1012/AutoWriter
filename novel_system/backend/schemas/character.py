from typing import Optional

from pydantic import BaseModel


class CharacterCreate(BaseModel):
    name: str
    role: Optional[str] = None
    description: Optional[str] = None
    traits: Optional[dict] = None
    arc: Optional[str] = None


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    traits: Optional[dict] = None
    arc: Optional[str] = None


class CharacterRead(BaseModel):
    id: int
    project_id: int
    name: str
    role: Optional[str]
    description: Optional[str]
    traits: Optional[dict]
    arc: Optional[str]

    class Config:
        from_attributes = True
