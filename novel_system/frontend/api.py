from functools import lru_cache
import os
from typing import Any, Dict, List, Optional

import requests


@lru_cache(maxsize=1)
def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8000")


def api_get(path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
    return requests.get(f"{api_base_url()}{path}", params=params)


def api_post(path: str, json: Dict[str, Any]) -> requests.Response:
    return requests.post(f"{api_base_url()}{path}", json=json)


def api_put(path: str, json: Dict[str, Any]) -> requests.Response:
    return requests.put(f"{api_base_url()}{path}", json=json)


def api_post_with_params(path: str, params: Dict[str, Any], json: Dict[str, Any]) -> requests.Response:
    return requests.post(f"{api_base_url()}{path}", params=params, json=json)


def load_projects() -> List[Dict[str, Any]]:
    resp = api_get("/projects")
    resp.raise_for_status()
    return resp.json()


def create_project(name: str, description: str) -> Dict[str, Any]:
    resp = api_post("/projects", {"name": name, "description": description})
    resp.raise_for_status()
    return resp.json()


def load_chapters(project_id: int) -> List[Dict[str, Any]]:
    resp = api_get(f"/projects/{project_id}/chapters")
    resp.raise_for_status()
    return resp.json()


def load_chapter(chapter_id: int) -> Dict[str, Any]:
    resp = api_get(f"/chapters/{chapter_id}")
    resp.raise_for_status()
    return resp.json()


def save_chapter(chapter_id: int, title: str, summary: str, content: str) -> Dict[str, Any]:
    payload = {"title": title, "summary": summary, "content": content}
    resp = api_put(f"/chapters/{chapter_id}", payload)
    resp.raise_for_status()
    return resp.json()


def create_chapter(project_id: int, title: str, summary: str) -> Dict[str, Any]:
    resp = api_post(
        f"/projects/{project_id}/chapters",
        {"title": title, "summary": summary, "content": ""},
    )
    resp.raise_for_status()
    return resp.json()


def chapter_ai_action(
    chapter_id: int,
    action: str,
    prompt: str,
    *,
    model: Optional[str] = None,
    persona: Optional[str] = None,
    tone: Optional[str] = None,
) -> str:
    payload: Dict[str, Any] = {"prompt": prompt}
    if model:
        payload["model"] = model
    if persona:
        payload["persona"] = persona
    if tone:
        payload["tone"] = tone
    resp = api_post(
        f"/chapters/{chapter_id}/ai/{action}",
        payload,
    )
    resp.raise_for_status()
    return resp.json().get("generated_text", "")


def analyze_chapter_api(chapter_id: int) -> Dict[str, Any]:
    resp = api_post(f"/chapters/{chapter_id}/analyze", {})
    resp.raise_for_status()
    return resp.json()


def list_world_elements(project_id: int) -> List[Dict[str, Any]]:
    resp = api_get(f"/projects/{project_id}/world-elements")
    resp.raise_for_status()
    return resp.json()


def create_world_element(project_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = api_post(f"/projects/{project_id}/world-elements", payload)
    resp.raise_for_status()
    return resp.json()


def update_world_element(element_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = api_put(f"/world-elements/{element_id}", payload)
    resp.raise_for_status()
    return resp.json()


def search_related(project_id: int, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    resp = api_post_with_params("/ai/search", params={"project_id": project_id, "query": query, "top_k": top_k}, json={})
    resp.raise_for_status()
    return resp.json()


def list_characters(project_id: int) -> List[Dict[str, Any]]:
    resp = api_get(f"/projects/{project_id}/characters")
    resp.raise_for_status()
    return resp.json()


def create_character(project_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = api_post(f"/projects/{project_id}/characters", payload)
    resp.raise_for_status()
    return resp.json()


def update_character(character_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = api_put(f"/characters/{character_id}", payload)
    resp.raise_for_status()
    return resp.json()


def ai_improve_character(
    character_id: int,
    prompt: str,
    *,
    model: Optional[str] = None,
    persona: Optional[str] = None,
    tone: Optional[str] = None,
) -> str:
    payload: Dict[str, Any] = {"prompt": prompt}
    if model:
        payload["model"] = model
    if persona:
        payload["persona"] = persona
    if tone:
        payload["tone"] = tone
    resp = api_post(f"/characters/{character_id}/ai/improve", payload)
    resp.raise_for_status()
    return resp.json().get("generated_text", "")


def list_clues(project_id: int, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    params = {"status_filter": status_filter} if status_filter else None
    resp = api_get(f"/projects/{project_id}/clues", params=params)
    resp.raise_for_status()
    return resp.json()


def create_clue(project_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = api_post(f"/projects/{project_id}/clues", payload)
    resp.raise_for_status()
    return resp.json()


def update_clue(clue_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = api_put(f"/clues/{clue_id}", payload)
    resp.raise_for_status()
    return resp.json()


def ai_generate(
    prompt: str,
    mode: Optional[str] = None,
    *,
    model: Optional[str] = None,
    persona: Optional[str] = None,
    tone: Optional[str] = None,
    role: Optional[str] = None,
) -> str:
    payload: Dict[str, Any] = {"prompt": prompt}
    if mode:
        payload["mode"] = mode
    if model:
        payload["model"] = model
    if persona:
        payload["persona"] = persona
    if tone:
        payload["tone"] = tone
    if role:
        payload["role"] = role
    resp = api_post("/ai/generate", payload)
    resp.raise_for_status()
    return resp.json().get("generated_text", "")
