from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from novel_system.frontend import api, stages
from novel_system.frontend.ui_styles import inject_base_styles

st.set_page_config(page_title="AutoWriter Studio", page_icon="AW", layout="wide")


def init_state() -> None:
    st.session_state.setdefault("ui_stage", "Plan")
    st.session_state.setdefault("selected_project_id", None)
    st.session_state.setdefault("selected_chapter_id", None)


def render_top_bar(projects: List[Dict[str, Any]]) -> Tuple[str, Optional[int], Optional[int], List[Dict[str, Any]], Dict[str, Optional[str]]]:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    col_stage, col_project, col_ai = st.columns([1.2, 2.4, 2.2])

    with col_stage:
        stage = st.radio(
            "Stage",
            options=["Plan", "Draft", "Revise", "Library"],
            horizontal=True,
            index=["Plan", "Draft", "Revise", "Library"].index(st.session_state.get("ui_stage", "Plan")),
        )
        st.session_state["ui_stage"] = stage

    project_id: Optional[int] = None
    chapter_id: Optional[int] = None
    chapter_list: List[Dict[str, Any]] = []

    with col_project:
        if projects:
            proj_options = {f"{p['name']} (#{p['id']})": p["id"] for p in projects}
            default_project = st.session_state.get("selected_project_id")
            default_index = list(proj_options.values()).index(default_project) if default_project in proj_options.values() else 0
            project_label = st.selectbox("Project", options=list(proj_options.keys()), index=default_index)
            project_id = proj_options[project_label]
            st.session_state["selected_project_id"] = project_id
            try:
                chapter_list = api.load_chapters(project_id)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Unable to load chapters: {exc}")
                chapter_list = []

            if chapter_list:
                chapter_options = {f"{c.get('index', idx) + 1}. {c['title']} (#{c['id']})": c["id"] for idx, c in enumerate(chapter_list)}
                default_chapter = st.session_state.get("selected_chapter_id")
                default_chapter_index = list(chapter_options.values()).index(default_chapter) if default_chapter in chapter_options.values() else 0
                chapter_label = st.selectbox("Chapter", options=list(chapter_options.keys()), index=default_chapter_index)
                chapter_id = chapter_options[chapter_label]
                st.session_state["selected_chapter_id"] = chapter_id
            else:
                st.caption("No chapters yet. Add one in Plan.")
        else:
            st.info("Create a project to start.")

    with col_ai:
        ai_model = st.selectbox("AI model", ["GPT-4.1", "Claude 3.5", "Local draft model"], index=0)
        persona = st.selectbox("Author voice", ["Neutral", "Cinematic", "Wry narrator"], index=0)
        tone = st.selectbox("Tone guide", ["Balanced", "Darker", "Lighter"], index=0)

    st.markdown("</div>", unsafe_allow_html=True)
    ai_profile = {"model": ai_model, "persona": persona, "tone": tone}
    return stage, project_id, chapter_id, chapter_list, ai_profile


def render_sidebar_create_project() -> None:
    st.sidebar.subheader("Create project")
    with st.sidebar.form("new_project_form"):
        proj_name = st.text_input("Project name")
        proj_desc = st.text_area("Description", height=80)
        if st.form_submit_button("Create project"):
            try:
                proj = api.create_project(proj_name, proj_desc)
                st.session_state["selected_project_id"] = proj["id"]
                st.sidebar.success("Project created.")
            except Exception as exc:  # noqa: BLE001
                st.sidebar.error(f"Create failed: {exc}")


def main() -> None:
    init_state()
    inject_base_styles()
    st.title("AI Writing Command Center")
    st.caption("Linear Plan → Draft → Revise flow with contextual AI support.")

    render_sidebar_create_project()

    try:
        projects = api.load_projects()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load projects: {exc}")
        projects = []

    stage, project_id, chapter_id, chapter_list, ai_profile = render_top_bar(projects)

    if stage == "Plan":
        stages.render_plan_stage(project_id, chapter_list, ai_profile=ai_profile)
    elif stage == "Draft":
        stages.render_draft_stage(project_id, chapter_id, ai_profile=ai_profile)
    elif stage == "Revise":
        stages.render_revise_stage(project_id, chapter_id, ai_profile=ai_profile)
    else:
        stages.render_library_stage(projects, project_id, chapter_list)


if __name__ == "__main__":
    main()
