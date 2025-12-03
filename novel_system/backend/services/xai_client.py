from typing import Optional

from openai import OpenAI

from novel_system.backend.core.config import get_settings

settings = get_settings()


class XAIService:
    def __init__(self, api_key: str, base_url: str):
        if not api_key:
            raise ValueError("XAI_API_KEY is not configured")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def chat(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        sys_prompt = system_prompt or "You are a creative writing assistant."
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt},
        ]
        response = self.client.chat.completions.create(
            model=model or settings.xai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""


_service: Optional[XAIService] = None


def get_service() -> XAIService:
    global _service
    if _service is None:
        _service = XAIService(api_key=settings.xai_api_key, base_url=settings.xai_base_url)
    return _service


def generate_text(
    prompt: str,
    *,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> str:
    service = get_service()
    return service.chat(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


__all__ = ["generate_text"]
