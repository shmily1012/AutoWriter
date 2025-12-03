import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

st.set_page_config(page_title="AutoWriter Studio", page_icon="AW", layout="wide")


def inject_base_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');
        :root {
            --bg: #0e1116;
            --panel: rgba(255,255,255,0.04);
            --muted: #9aa2b1;
            --accent: #7c8cff;
            --accent-2: #74d4ff;
            --border: rgba(255,255,255,0.08);
        }
        body, input, textarea, select, button {
            font-family: 'Space Grotesk', 'IBM Plex Sans', sans-serif;
            color: #e7ecf5;
        }
        .block-container { padding-top: 1.5rem; }
        .glass-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1.2rem;
            box-shadow: 0 14px 50px rgba(0,0,0,0.25);
        }
        .pill {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.35rem 0.7rem;
            border-radius: 12px;
            background: rgba(124,140,255,0.18);
            color: #e7ecf5;
            font-size: 0.85rem;
            margin-right: 0.35rem;
        }
        .muted { color: var(--muted); font-size: 0.9rem; }
        .metric-card {
            padding: 0.75rem 1rem;
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--border);
            border-radius: 12px;
        }
        .step-list { padding-left: 1.2rem; line-height: 1.6; }
        .step-list li { margin-bottom: 0.4rem; }
        .mono { font-family: 'IBM Plex Mono', monospace; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@lru_cache(maxsize=1)
def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8000")


def api_get(path: str) -> requests.Response:
    return requests.get(f"{api_base_url()}{path}")


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


def analyze_chapter_api(chapter_id: int) -> Dict[str, Any]:
    resp = api_post(f"/chapters/{chapter_id}/analyze", {})
    resp.raise_for_status()
    return resp.json()


def list_clues(project_id: int, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    url = f"{api_base_url()}/projects/{project_id}/clues"
    params = {"status_filter": status_filter} if status_filter else {}
    resp = requests.get(url, params=params)
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


# ---------------- UI Helpers -----------------


def render_top_bar() -> Dict[str, Any]:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    col_logo, col_mode, col_controls = st.columns([1.2, 2.8, 2.6])
    modes = [
        ("Writing Studio", "writing"),
        ("Worldbuilding", "world"),
        ("Characters", "characters"),
        ("Outline", "outline"),
        ("Quality", "quality"),
    ]

    with col_logo:
        st.markdown("#### AutoWriter Studio")
        st.caption("Writing IDE + notebook for long-form fiction.")

    with col_mode:
        labels = [label for label, _ in modes]
        default_mode = st.session_state.get("ui_mode", "writing")
        default_index = next((i for i, (_, val) in enumerate(modes) if val == default_mode), 0)
        selected_label = st.radio(
            "Work mode",
            labels,
            index=default_index,
            horizontal=True,
            label_visibility="collapsed",
        )
        selected_mode = dict(modes)[selected_label]
        st.session_state["ui_mode"] = selected_mode

    with col_controls:
        ai_model = st.selectbox("AI model", ["GPT-4.1", "Claude 3.5", "Local draft model"], index=0)
        persona = st.selectbox("Author voice", ["Neutral", "Cinematic", "Wry narrator"], index=0)
        tone = st.selectbox("Tone guide", ["Balanced", "Darker", "Lighter"], index=0)

    st.markdown("</div>", unsafe_allow_html=True)
    return {"mode": selected_mode, "ai_model": ai_model, "persona": persona, "tone": tone}


def render_project_switcher(projects: List[Dict[str, Any]]) -> Optional[int]:
    if not projects:
        st.info("No projects yet. Create one to start your workspace.")
        return None

    proj_options = {f"{p['name']} (#{p['id']})": p["id"] for p in projects}
    selected_project_id = st.session_state.get("selected_project_id")
    index = 0
    if selected_project_id and selected_project_id in proj_options.values():
        index = list(proj_options.values()).index(selected_project_id)
    label = st.selectbox("Active project", options=list(proj_options.keys()), index=index)
    st.session_state["selected_project_id"] = proj_options[label]
    return proj_options[label]


def render_project_tree_sidebar(projects: List[Dict[str, Any]], chapter_list: List[Dict[str, Any]]) -> None:
    st.sidebar.header("Project Map")
    st.sidebar.caption("World | Characters | Outline | Writing | Quality")

    if projects:
        for proj in projects:
            with st.sidebar.expander(f"[Project] {proj['name']} (#{proj['id']})", expanded=proj["id"] == st.session_state.get("selected_project_id")):
                st.markdown("**Summary**")
                st.caption(proj.get("description") or "No description yet.")
                st.markdown("**Sections**")
                st.write("- World: settings, factions, places")
                st.write("- Characters: cast, arcs, relationships")
                st.write("- Outline: volumes, arcs, beats")
                st.write("- Chapters: drafts and versions")
                st.write("- Quality: diagnostics and reports")
    else:
        st.sidebar.info("Create a project to unlock navigation.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Chapters")
    if chapter_list:
        chapter_options = {f"{c.get('index', idx) + 1}. {c['title']} (#{c['id']})": c["id"] for idx, c in enumerate(chapter_list)}
        current_label = st.sidebar.radio("Switch chapter", options=list(chapter_options.keys()))
        st.session_state["selected_chapter_id"] = chapter_options[current_label]
    else:
        st.sidebar.caption("No chapters yet.")


# ---------------- Feature Panels -----------------


def chapter_progress(content: str, expected: int = 2000) -> None:
    words = len((content or "").split())
    pct = min(words / expected, 1.2)
    col_goal, col_progress, col_pace = st.columns(3)
    col_goal.metric("Target", f"{expected} words", "+ steady pace")
    col_progress.metric("Current", f"{words} words", f"{int(pct * 100)}% of goal")
    pace_label = "On track" if pct >= 0.5 else "Warm-up"
    col_pace.metric("Rhythm", pace_label, "Live")
    st.progress(min(pct, 1.0))


def render_context_panel(current_project_id: int, chapter_data: Dict[str, Any]) -> None:
    st.markdown("#### Context & References")
    st.markdown("**Summary**")
    st.write(chapter_data.get("summary") or "No summary yet.")

    st.markdown("**Cast on stage**")
    try:
        chars = list_characters(current_project_id)
        for ch in chars[:5]:
            st.write(f"- {ch.get('name', 'Unknown')} - {ch.get('description', '')[:80]}")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Characters unavailable: {exc}")

    st.markdown("**World notes**")
    try:
        elements = list_world_elements(current_project_id)
        for item in elements[:5]:
            st.write(f"- [{item.get('type', 'item')}] {item.get('title')}")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"World data unavailable: {exc}")

    st.markdown("**Foreshadow & loose threads**")
    try:
        clues = list_clues(current_project_id, status_filter="unresolved")
        for clue in clues[:5]:
            st.write(f"- {clue.get('description', '')[:90]}")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Clues unavailable: {exc}")

    st.markdown("**Related pulls**")
    query = st.text_input("Search project memory", value="", placeholder="e.g., rival faction, missing heir, cursed blade")
    if query:
        try:
            hits = search_related(current_project_id, query)
            for hit in hits:
                title = hit.get("title") or f"{hit.get('type', 'Note')} #{hit.get('ref_id')}"
                snippet = hit.get("snippet") or hit.get("content", "")
                st.write(f"- {title}: {snippet[:140]}")
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Search failed: {exc}")


def render_ai_assistant(
    chapter_id: int,
    chapter_content: str,
    *,
    model: Optional[str],
    persona: Optional[str],
    tone: Optional[str],
) -> None:
    st.markdown("#### AI Companion")
    loop_tab, chat_tab, diagnostics_tab, stash_tab = st.tabs(["Writer Loop", "Dialogue", "Diagnostics", "Stash"])

    with loop_tab:
        st.markdown("The Writer Loop steps: skeleton -> three drafts -> human edits -> style unify.")
        prompt = st.text_area(
            "Working prompt",
            value=st.session_state.get(f"loop_prompt_{chapter_id}", "Keep POV consistent, honor tone, surface tension between leads."),
            height=140,
            key=f"loop_prompt_{chapter_id}",
        )
        replace = st.checkbox("Replace editor text instead of appending", key=f"ai_replace_{chapter_id}", value=False)
        status_placeholder = st.empty()

        def run_ai(action: str, label: str) -> None:
            try:
                generated = chapter_ai_action(
                    chapter_id,
                    action,
                    prompt,
                    model=model,
                    persona=persona,
                    tone=tone,
                )
                content_key = f"chapter_content_{chapter_id}"
                if replace:
                    st.session_state[content_key] = generated
                else:
                    base = st.session_state.get(content_key, chapter_content)
                    st.session_state[content_key] = f"{base}\n\n{generated}".strip()
                status_placeholder.success(f"{label} ready and sent to editor.")
            except Exception as exc:  # noqa: BLE001
                status_placeholder.error(f"{label} failed: {exc}")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Skeleton"):
                run_ai("draft", "Skeleton")
        with col2:
            if st.button("Expand scene"):
                run_ai("expand", "Expansion")
        with col3:
            if st.button("Rewrite tone"):
                run_ai("rewrite", "Rewrite")
        if st.button("Polish style"):
            run_ai("polish", "Polish")

    with chat_tab:
        chat_prompt = st.text_area(
            "Ask about this chapter",
            value="What is the strongest conflict in this scene?",
            height=110,
            key=f"chat_prompt_{chapter_id}",
        )
        if st.button("Send chat", key=f"chat_btn_{chapter_id}"):
            try:
                reply = ai_generate(
                    chat_prompt,
                    mode="chat",
                    model=model,
                    persona=persona,
                    tone=tone,
                )
                st.session_state["chat_reply"] = reply
            except Exception as exc:  # noqa: BLE001
                st.error(f"Chat failed: {exc}")
        if st.session_state.get("chat_reply"):
            st.info(st.session_state["chat_reply"])

    with diagnostics_tab:
        st.markdown("Run quick checks for pacing, OOC lines, and duplicate beats.")
        if st.button("Analyze chapter", key=f"analysis_btn_{chapter_id}"):
            try:
                analysis = analyze_chapter_api(chapter_id)
                st.session_state[f"analysis_{chapter_id}"] = analysis
            except Exception as exc:  # noqa: BLE001
                st.error(f"Analysis failed: {exc}")
        if st.session_state.get(f"analysis_{chapter_id}"):
            st.json(st.session_state[f"analysis_{chapter_id}"])

    with stash_tab:
        st.caption("Hold unused lines or alt versions; drag into the editor when needed.")
        st.text_area("Scratchpad", key=f"stash_{chapter_id}", height=160)


def render_writing_mode(
    current_project_id: int,
    chapter_id: Optional[int],
    *,
    model: Optional[str],
    persona: Optional[str],
    tone: Optional[str],
) -> None:
    if not current_project_id or not chapter_id:
        st.info("Select a project and chapter to open Chapter Studio.")
        return

    try:
        chapter_data = load_chapter(chapter_id)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load chapter: {exc}")
        return

    st.markdown("### Chapter Studio")
    chapter_progress(chapter_data.get("content") or "")

    col_context, col_editor, col_ai = st.columns([1.2, 2.4, 1.4], gap="large")

    with col_context:
        render_context_panel(current_project_id, chapter_data)

    with col_editor:
        st.markdown("#### Draft workspace")
        title = st.text_input("Title", value=chapter_data.get("title", ""))
        summary = st.text_area("Beat summary", value=chapter_data.get("summary") or "", height=90)
        content_key = f"chapter_content_{chapter_id}"
        content = st.text_area(
            "Chapter markdown",
            value=st.session_state.get(content_key, chapter_data.get("content") or ""),
            height=420,
            key=content_key,
        )

        quick_cols = st.columns(3)
        with quick_cols[0]:
            if st.button("Tag turning point"):
                st.session_state[content_key] = f"{content}\n\n[TURNING POINT]\n"
        with quick_cols[1]:
            if st.button("Insert beat checklist"):
                st.session_state[content_key] = f"{content}\n\n- Setup\n- Tension\n- Payoff\n"
        with quick_cols[2]:
            if st.button("Mark for polish"):
                st.session_state[content_key] = f"{content}\n\n[POLISH ME]\n"

        save_cols = st.columns(2)
        with save_cols[0]:
            if st.button("Save chapter"):
                try:
                    save_chapter(
                        chapter_id,
                        title=title,
                        summary=summary,
                        content=st.session_state.get(content_key, content),
                    )
                    st.success("Chapter saved.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Save failed: {exc}")
        with save_cols[1]:
            if st.button("Run diagnostics"):
                try:
                    analysis = analyze_chapter_api(chapter_id)
                    st.session_state[f"analysis_{chapter_id}"] = analysis
                    st.success("Analysis ready in the AI panel.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Diagnostics failed: {exc}")

    with col_ai:
        render_ai_assistant(
            chapter_id,
            st.session_state.get(content_key, chapter_data.get("content") or ""),
            model=model,
            persona=persona,
            tone=tone,
        )


# ---------------- Other Modes -----------------


def render_world_mode(current_project_id: int, *, model: Optional[str], persona: Optional[str], tone: Optional[str]) -> None:
    st.markdown("### Worldbuilding Desk")
    if not current_project_id:
        st.info("Select a project to explore the world map.")
        return

    col_tree, col_detail, col_ai = st.columns([1.2, 1.8, 1.2], gap="large")
    with col_tree:
        st.markdown("#### World tree")
        try:
            elements = list_world_elements(current_project_id)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to load world elements: {exc}")
            elements = []
        for el in elements:
            st.write(f"- [{el.get('type', 'item')}] {el.get('title')} (#{el.get('id')})")

    with col_detail:
        st.markdown("#### Add / edit element")
        with st.form("create_world_element_form"):
            we_type = st.text_input("Type", key="we_type_new")
            we_title = st.text_input("Title", key="we_title_new")
            we_content = st.text_area("Notes", height=140, key="we_content_new")
            if st.form_submit_button("Save element"):
                try:
                    create_world_element(current_project_id, {"type": we_type, "title": we_title, "content": we_content})
                    st.success("World element saved.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Save failed: {exc}")

    with col_ai:
        st.markdown("#### AI world helper")
        prompt = st.text_area("Prompt", value="Generate three tensions for the ruling faction.", height=120)
        if st.button("Generate world beats"):
            try:
                result = ai_generate(prompt, mode="world", model=model, persona=persona, tone=tone, role="world_consultant")
                st.session_state["world_ai"] = result
            except Exception as exc:  # noqa: BLE001
                st.error(f"AI generation failed: {exc}")
        if st.session_state.get("world_ai"):
            st.info(st.session_state["world_ai"])


def render_character_mode(current_project_id: int, *, model: Optional[str], persona: Optional[str], tone: Optional[str]) -> None:
    st.markdown("### Character Desk")
    if not current_project_id:
        st.info("Select a project to manage characters.")
        return

    try:
        characters = list_characters(current_project_id)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load characters: {exc}")
        characters = []

    cols = st.columns(3)
    for idx, ch in enumerate(characters):
        with cols[idx % 3]:
            st.markdown(f"**{ch.get('name', 'Unknown')}** - {ch.get('role') or ''}")
            st.caption(ch.get("description") or "")
            arc = ch.get("arc") or "Arc not set"
            st.caption(f"Arc: {arc}")

    st.markdown("---")
    st.markdown("#### Create / update character")
    with st.form("character_edit_form"):
        ch_name = st.text_input("Name")
        ch_role = st.text_input("Role")
        ch_desc = st.text_area("Snapshot", height=110)
        ch_arc = st.text_area("Arc notes", height=80)
        if st.form_submit_button("Save character"):
            try:
                create_character(current_project_id, {"name": ch_name, "role": ch_role, "description": ch_desc, "arc": ch_arc})
                st.success("Character saved.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Save failed: {exc}")

    st.markdown("#### Consistency check")
    ai_prompt = st.text_area("Prompt", value="Check if the protagonist voice drifts across chapters.", height=80)
    if st.button("Run character check"):
        try:
            result = ai_generate(ai_prompt, mode="character_check", model=model, persona=persona, tone=tone, role="world_consultant")
            st.session_state["character_ai"] = result
        except Exception as exc:  # noqa: BLE001
            st.error(f"AI failed: {exc}")
    if st.session_state.get("character_ai"):
        st.info(st.session_state["character_ai"])

    st.markdown("#### AI improve selected character")
    if characters:
        options = {f"{c.get('name', 'Unknown')} (#{c.get('id')})": c["id"] for c in characters}
        selected_label = st.selectbox("Character", options=list(options.keys()), key="improve_character_select")
        improve_prompt = st.text_area(
            "Improvement prompt",
            value="Sharpen their voice, add a signature line, and surface one flaw.",
            height=90,
            key="improve_character_prompt",
        )
        if st.button("Improve character", key="improve_character_btn"):
            try:
                result = ai_improve_character(
                    options[selected_label],
                    improve_prompt,
                    model=model,
                    persona=persona,
                    tone=tone,
                )
                st.session_state["character_improve_result"] = result
            except Exception as exc:  # noqa: BLE001
                st.error(f"AI failed: {exc}")
        if st.session_state.get("character_improve_result"):
            st.info(st.session_state["character_improve_result"])
    else:
        st.caption("Add a character to run targeted improvements.")


def render_outline_mode(current_project_id: int, chapter_list: List[Dict[str, Any]], *, model: Optional[str], persona: Optional[str], tone: Optional[str]) -> None:
    st.markdown("### Outline Board")
    if not current_project_id:
        st.info("Select a project to view the outline.")
        return

    col_tree, col_detail, col_ai = st.columns([1.2, 1.8, 1.2], gap="large")
    with col_tree:
        st.markdown("#### Volumes / chapters")
        if chapter_list:
            for c in chapter_list:
                status = "Draft" if c.get("content") else "Pending"
                st.write(f"- {c.get('index', 0) + 1}. {c['title']} - {status}")
        else:
            st.caption("No chapters yet.")

    with col_detail:
        st.markdown("#### Outline detail")
        st.text_area("Outline focus", height=180, key="outline_detail")

    with col_ai:
        st.markdown("#### AI outline planner")
        prompt = st.text_area(
            "Prompt",
            value="Draft a beat map for the next chapter that escalates the rivalry and ends on a hook.",
            height=120,
        )
        if st.button("Generate outline ideas"):
            try:
                suggestion = ai_generate(prompt, mode="outline", model=model, persona=persona, tone=tone, role="plot_coach")
                st.session_state["outline_ai"] = suggestion
            except Exception as exc:  # noqa: BLE001
                st.error(f"AI failed: {exc}")
        if st.session_state.get("outline_ai"):
            st.info(st.session_state["outline_ai"])


def render_quality_mode(current_project_id: int, chapter_id: Optional[int]) -> None:
    st.markdown("### Quality Check")
    if not current_project_id or not chapter_id:
        st.info("Pick a project and chapter to run quality checks.")
        return

    if st.button("Generate quality report"):
        try:
            result = analyze_chapter_api(chapter_id)
            st.session_state["quality_report"] = result
        except Exception as exc:  # noqa: BLE001
            st.error(f"Report failed: {exc}")

    if st.session_state.get("quality_report"):
        st.json(st.session_state["quality_report"])
    else:
        st.caption("Quality report highlights OOC lines, world clashes, repeats, and pacing.")


# ---------------- Main -----------------


def main() -> None:
    inject_base_styles()
    st.title("AI Writing Command Center")
    st.caption("Three-panel Chapter Studio with world, character, outline, and quality views.")

    ui_state = render_top_bar()

    # Sidebar: project creation
    st.sidebar.subheader("Create project")
    with st.sidebar.form("new_project_form"):
        proj_name = st.text_input("Project name")
        proj_desc = st.text_area("Description", height=80)
        if st.form_submit_button("Create project"):
            try:
                proj = create_project(proj_name, proj_desc)
                st.session_state["selected_project_id"] = proj["id"]
                st.sidebar.success("Project created.")
            except Exception as exc:  # noqa: BLE001
                st.sidebar.error(f"Create failed: {exc}")

    # Load projects and chapters
    try:
        projects = load_projects()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load projects: {exc}")
        projects = []

    current_project_id = render_project_switcher(projects)

    chapter_list: List[Dict[str, Any]] = []
    if current_project_id:
        try:
            chapter_list = load_chapters(current_project_id)
            st.session_state["chapter_list_for_tabs"] = chapter_list
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to load chapters: {exc}")
            chapter_list = []

    render_project_tree_sidebar(projects, chapter_list)

    st.markdown("---")

    if current_project_id:
        with st.expander("Add a new chapter", expanded=False):
            with st.form("new_chapter_form"):
                new_chapter_title = st.text_input("Chapter title")
                new_chapter_summary = st.text_area("Summary", height=80)
                if st.form_submit_button("Create chapter"):
                    try:
                        chap = create_chapter(current_project_id, new_chapter_title, new_chapter_summary)
                        st.session_state["selected_chapter_id"] = chap["id"]
                        st.success("Chapter created.")
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"Create failed: {exc}")

    current_chapter_id = st.session_state.get("selected_chapter_id")

    if ui_state["mode"] == "writing":
        render_writing_mode(
            current_project_id,
            current_chapter_id,
            model=ui_state["ai_model"],
            persona=ui_state["persona"],
            tone=ui_state["tone"],
        )
    elif ui_state["mode"] == "world":
        render_world_mode(current_project_id, model=ui_state["ai_model"], persona=ui_state["persona"], tone=ui_state["tone"])
    elif ui_state["mode"] == "characters":
        render_character_mode(current_project_id, model=ui_state["ai_model"], persona=ui_state["persona"], tone=ui_state["tone"])
    elif ui_state["mode"] == "outline":
        render_outline_mode(current_project_id, chapter_list, model=ui_state["ai_model"], persona=ui_state["persona"], tone=ui_state["tone"])
    else:
        render_quality_mode(current_project_id, current_chapter_id)


if __name__ == "__main__":
    main()
