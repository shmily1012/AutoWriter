from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

from novel_system.backend.services import gemini_client, openai_client, xai_client


@dataclass(frozen=True)
class ModelSpec:
    name: str
    provider: str
    tier: str  # e.g., strong/fast/cheap/style
    roles: Sequence[str] = field(default_factory=tuple)
    max_context: Optional[int] = None
    price: Optional[Dict[str, float]] = None  # {"in": float, "out": float}


class ModelUnavailable(RuntimeError):
    """Raised when a provider/model cannot be invoked."""


MODEL_REGISTRY: Dict[str, ModelSpec] = {
    # OpenAI
    "gpt-5.1": ModelSpec(
        name="gpt-5.1",
        provider="openai",
        tier="strong",
        roles=("default", "draft", "rewrite", "quality", "outline", "chapter"),
        max_context=196_000,
        price={"in": 1.25, "out": 10.0},
    ),
    "gpt-5-mini": ModelSpec(
        name="gpt-5-mini",
        provider="openai",
        tier="cheap",
        roles=("short", "classify", "tag", "outline", "blurb"),
        max_context=128_000,
        price={"in": 0.25, "out": 2.0},
    ),
    # Gemini
    "gemini-3.0-pro": ModelSpec(
        name="gemini-3.0-pro",
        provider="gemini",
        tier="strong",
        roles=("analysis", "multimodal", "long"),
        max_context=2_000_000,
        price={"in": 2.0, "out": 12.0},
    ),
    "gemini-1.5-flash": ModelSpec(
        name="gemini-1.5-flash",
        provider="gemini",
        tier="fast",
        roles=("short", "classify", "outline"),
        max_context=1_000_000,
        price=None,
    ),
    # Grok
    "grok-4.1": ModelSpec(
        name="grok-4.1",
        provider="grok",
        tier="strong",
        roles=("creative", "dialogue", "style"),
        max_context=2_000_000,
        price={"in": 3.0, "out": 15.0},
    ),
    "grok-2-mini": ModelSpec(
        name="grok-2-mini",
        provider="grok",
        tier="fast",
        roles=("short", "chat"),
        max_context=512_000,
        price=None,
    ),
}

# Task → default preference order (novel-focused)
TASK_DEFAULTS: Dict[str, List[str]] = {
    # Fast, cheap scaffolding
    "outline": ["gpt-5-mini", "gpt-5.1", "gemini-3.0-pro"],
    "short": ["gpt-5-mini", "gemini-1.5-flash", "gpt-5.1"],
    # Chapter/scene generation
    "draft": ["gpt-5-mini", "gpt-5.1", "gemini-3.0-pro"],
    "chapter": ["gpt-5.1", "gemini-3.0-pro"],
    # Revision and quality
    "rewrite": ["gpt-5.1", "grok-4.1"],
    "polish": ["gpt-5.1", "grok-4.1"],
    "quality": ["gpt-5.1", "gemini-3.0-pro"],
    # Worldbuilding and long-context reasoning
    "world": ["gemini-3.0-pro", "gpt-5.1"],
    "lore": ["gemini-3.0-pro", "gpt-5.1"],
    # Dialogue and emotion-heavy passages
    "dialogue": ["grok-4.1", "gpt-5.1"],
    "emotional": ["grok-4.1", "gpt-5.1"],
    # General chat fallback
    "chat": ["gpt-5-mini", "gpt-5.1", "grok-4.1"],
}

# Strategy presets (user/session preferences)
STRATEGY_PRESETS: Dict[str, List[str]] = {
    "default": ["gpt-5-mini", "gpt-5.1"],
    "creative": ["grok-4.1", "gpt-5.1"],
    "grok": ["grok-4.1", "gpt-5.1"],
    "gemini": ["gemini-3.0-pro", "gpt-5.1", "gpt-5-mini"],
    "long_context": ["gemini-3.0-pro", "gpt-5.1"],
    "cheap": ["gpt-5-mini", "gemini-1.5-flash", "gpt-5.1"],
}


def _unique(seq: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in seq:
        if item not in seen and item in MODEL_REGISTRY:
            seen.add(item)
            out.append(item)
    return out


def select_models(
    task: Optional[str] = None,
    *,
    strategy: Optional[str] = None,
    preferred_models: Optional[Sequence[str]] = None,
) -> List[str]:
    if preferred_models:
        return [m for m in preferred_models if m in MODEL_REGISTRY]

    base = TASK_DEFAULTS.get(task or "", []) + STRATEGY_PRESETS.get(strategy or "default", [])

    # Short tasks should prioritize cheap/fast even if strategy says otherwise.
    if task == "short":
        base = TASK_DEFAULTS["short"] + STRATEGY_PRESETS.get(strategy or "default", [])

    models = _unique(base)
    return models or STRATEGY_PRESETS["default"]


def invoke_model(
    model_name: str,
    *,
    prompt: str,
    mode: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    if model_name not in MODEL_REGISTRY:
        raise ModelUnavailable(f"Unknown model: {model_name}")
    spec = MODEL_REGISTRY[model_name]

    if spec.provider == "openai":
        text = openai_client.generate_text(
            prompt=prompt,
            mode=mode,
            system_prompt=system_prompt,
            model=spec.name,
            temperature=temperature,
            max_tokens=max_tokens,
            role=role,
        )
        return {
            "text": text,
            "model_used": spec.name,
            "provider": spec.provider,
            "from_fallback": False,
        }

    if spec.provider == "gemini":
        text = gemini_client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model=spec.name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {
            "text": text,
            "model_used": spec.name,
            "provider": spec.provider,
            "from_fallback": False,
        }

    if spec.provider == "grok":
        text = xai_client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model=spec.name,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {
            "text": text,
            "model_used": spec.name,
            "provider": spec.provider,
            "from_fallback": False,
        }

    raise ModelUnavailable(f"Provider '{spec.provider}' not implemented yet for model '{spec.name}'")


def generate_text(
    prompt: str,
    *,
    task: Optional[str] = None,
    strategy: Optional[str] = None,
    preferred_models: Optional[Sequence[str]] = None,
    compare_models: Optional[Sequence[str]] = None,
    allow_fallback: bool = True,
    mode: Optional[str] = None,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    role: Optional[str] = None,
    return_meta: bool = False,
) -> Any:
    """
    Route a generation request through the model registry.

    - task: logical task label (outline/draft/chapter/rewrite/polish/quality/chat/short/world/dialogue)
    - strategy: user/session preference (default/creative/grok/gemini/long_context/cheap)
    - preferred_models: explicit priority list; overrides strategy/task defaults
    - compare_models: if provided, run multiple models and return list of results
    - allow_fallback: if True, try next model on failure
    - return_meta: if True, return dict with model info; otherwise return plain text
    """
    if compare_models:
        results = []
        for m in compare_models:
            try:
                res = invoke_model(
                    m,
                    prompt=prompt,
                    mode=mode,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    role=role,
                )
                results.append(res if return_meta else res["text"])
            except Exception as exc:  # noqa: BLE001
                if allow_fallback and m != "gpt-5.1":
                    try:
                        fb = invoke_model(
                            "gpt-5.1",
                            prompt=prompt,
                            mode=mode,
                            system_prompt=system_prompt,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            role=role,
                        )
                        fb["from_fallback"] = True
                        results.append(fb if return_meta else fb["text"])
                        continue
                    except Exception:
                        pass
                results.append({"error": str(exc), "model_used": m} if return_meta else str(exc))
        return results

    candidates = select_models(task=task, strategy=strategy, preferred_models=preferred_models)
    # If the caller explicitly provided `model`, prepend it.
    if model:
        candidates = _unique([model] + candidates)

    last_err: Optional[Exception] = None
    for idx, m in enumerate(candidates):
        try:
            res = invoke_model(
                m,
                prompt=prompt,
                mode=mode,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                role=role,
            )
            if return_meta:
                return res
            return res["text"]
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if not allow_fallback:
                break
            # Try fallback (always attempt gpt-5.1 if not already tried).
            if m != "gpt-5.1" and "gpt-5.1" in candidates[idx + 1 :]:
                continue
    if last_err:
        raise last_err
    raise ModelUnavailable("No model available to fulfill the request")


__all__ = ["generate_text", "select_models", "invoke_model", "ModelSpec", "MODEL_REGISTRY", "ModelUnavailable"]
