from typing import Dict, List, Optional

from openai import OpenAI

from novel_system.backend.core.config import get_settings

settings = get_settings()


ROLE_SYSTEM_PROMPTS: Dict[str, str] = {
    "default": "You are a helpful writing assistant.",
    "world_consultant": "You are a worldbuilding consultant. Provide concise, coherent setting advice.",
    "plot_coach": "You are a story coach. Provide concise plot development suggestions.",
    "style_polish": "You are a line editor. Polish text while keeping meaning.",
}


class OpenAIService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        self.client = OpenAI(api_key=api_key)

    def chat(
        self,
        prompt: str,
        mode: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        role: Optional[str] = None,
    ) -> str:
        chosen_model = model or settings.openai_model
        sys_prompt = (
            system_prompt
            or ROLE_SYSTEM_PROMPTS.get(role or "default")
            or ROLE_SYSTEM_PROMPTS["default"]
        )
        if mode:
            sys_prompt = f"Mode: {mode}. {sys_prompt}"

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt},
        ]

        request_kwargs = {
            "model": chosen_model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            request_kwargs["max_tokens"] = max_tokens

        response = self.client.chat.completions.create(**request_kwargs)
        return response.choices[0].message.content or ""

    def embed(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        embedding_model = model or settings.openai_embedding_model
        resp = self.client.embeddings.create(input=texts, model=embedding_model)
        return [item.embedding for item in resp.data]


_service: Optional[OpenAIService] = None


def get_service() -> OpenAIService:
    global _service
    if _service is None:
        _service = OpenAIService(api_key=settings.openai_api_key)
    return _service


def generate_text(
    prompt: str,
    mode: Optional[str] = None,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    role: Optional[str] = None,
) -> str:
    """
    Generate text via OpenAI chat completions.
    Args:
        prompt: user prompt
        mode: optional mode hint (e.g., outline/expand/rewrite) to prepend to system prompt
        system_prompt: base system instruction
        model: override model name (defaults to settings)
        temperature: sampling temperature
        max_tokens: optional cap on tokens in response
        role: optional named role from ROLE_SYSTEM_PROMPTS
    """
    service = get_service()
    return service.chat(
        prompt=prompt,
        mode=mode,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        role=role,
    )


def embed_texts(texts: List[str], model: Optional[str] = None) -> List[List[float]]:
    """Return embeddings for a list of texts using OpenAI embeddings API."""
    service = get_service()
    return service.embed(texts, model=model)


__all__ = ["generate_text", "embed_texts", "get_service", "ROLE_SYSTEM_PROMPTS"]
