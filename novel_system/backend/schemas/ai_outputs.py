from typing import List

from pydantic import BaseModel


class ChapterAnalysisResult(BaseModel):
    characters_appeared: List[str] = []
    world_facts: List[str] = []
    possible_clues: List[str] = []

    @classmethod
    def from_dict(cls, data: dict) -> "ChapterAnalysisResult":
        return cls(
            characters_appeared=data.get("characters_appeared") or [],
            world_facts=data.get("world_facts") or [],
            possible_clues=data.get("possible_clues") or [],
        )


__all__ = ["ChapterAnalysisResult"]
