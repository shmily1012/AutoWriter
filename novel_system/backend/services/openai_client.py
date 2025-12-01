from typing import Optional

from openai import OpenAI

from novel_system.backend.core.config import get_settings

settings = get_settings()


def generate_text(
    prompt: str,
    mode: Optional[str] = None,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
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
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured")

    chosen_model = model or settings.openai_model

    client = OpenAI(api_key=settings.openai_api_key)

    sys_prompt = system_prompt or "You are a helpful writing assistant."
    if mode:
        sys_prompt = f"Mode: {mode}. {sys_prompt}"

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model=chosen_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content or ""


__all__ = ["generate_text"]
