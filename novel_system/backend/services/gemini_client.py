from typing import Optional

from novel_system.backend.core.config import get_settings

settings = get_settings()


def _get_model(model: Optional[str] = None):
    try:
        import google.generativeai as genai
    except ImportError as exc:  # pragma: no cover - dependency optional
        raise RuntimeError(
            "google-generativeai is not installed; install it to use Gemini models."
        ) from exc

    api_key = settings.gemini_api_key
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    genai.configure(api_key=api_key)
    model_name = model or settings.gemini_model
    return genai.GenerativeModel(model_name)


def generate_text(
    prompt: str,
    *,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generate text via Gemini (Google AI Studio).
    """
    gen_model = _get_model(model=model)
    # Gemini supports a system prompt via the "system_instruction" field on the model instantiation,
    # but to keep alignment with OpenAI-style prompts we prepend it explicitly.
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    resp = gen_model.generate_content(
        full_prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        },
    )
    return resp.text or ""


__all__ = ["generate_text"]
