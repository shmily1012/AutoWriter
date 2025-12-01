from typing import Optional

from pydantic import BaseModel, Field


class AIGenerateRequest(BaseModel):
    prompt: str = Field(..., description="User prompt content")
    mode: Optional[str] = Field(
        default=None, description="Optional mode hint (outline/expand/rewrite/etc.)"
    )
    system_prompt: Optional[str] = Field(
        default=None, description="Override system prompt; default is a writing assistant"
    )
    model: Optional[str] = Field(default=None, description="Override model")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(
        default=None, description="Optional max tokens for the response"
    )


class AIGenerateResponse(BaseModel):
    generated_text: str
