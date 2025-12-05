from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import sys

import streamlit as st

# Ensure project root is importable when run via `streamlit run`
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from novel_system.frontend import api, stages
from novel_system.frontend.i18n import I18n
from novel_system.frontend.ui_styles import inject_base_styles

st.set_page_config(page_title="AutoWriter Studio", page_icon="AW", layout="wide")


def init_state() -> None:
    st.session_state.setdefault("ui_stage", "Plan")
    st.session_state.setdefault("selected_project_id", None)
    st.session_state.setdefault("selected_chapter_id", None)
    st.session_state.setdefault("language", "en")
    st.session_state.setdefault("action_status", None)


def render_status_bar(i18n: I18n) -> None:
    status = st.session_state.get("action_status") or i18n.t("status_idle")
    st.markdown(
        f"""
        <div class="status-bar">
            <span class="status-dot"></span>
            <div><strong>{i18n.t('status_label')}:</strong> {status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_bar(
    projects: List[Dict[str, Any]],
    i18n: I18n,
) -> Tuple[str, Optional[int], Optional[int], List[Dict[str, Any]], Dict[str, Optional[str]]]:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    col_stage, col_project, col_ai = st.columns([1.2, 2.4, 2.2])

    with col_stage:
        stage_options = ["Plan", "Draft", "Revise", "Library"]
        current_stage = st.session_state.get("ui_stage", "Plan")
        default_stage_index = stage_options.index(current_stage) if current_stage in stage_options else 0
        stage = st.radio(
            i18n.t("stage_label"),
            options=stage_options,
            horizontal=True,
            index=default_stage_index,
            format_func=i18n.stage_label,
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
            project_label = st.selectbox(i18n.t("project_label"), options=list(proj_options.keys()), index=default_index)
            project_id = proj_options[project_label]
            st.session_state["selected_project_id"] = project_id
            try:
                chapter_list = api.load_chapters(project_id)
            except Exception as exc:  # noqa: BLE001
                st.error(i18n.t("load_chapters_error", error=exc))
                chapter_list = []

            if chapter_list:
                chapter_options = {f"{c.get('index', idx) + 1}. {c['title']} (#{c['id']})": c["id"] for idx, c in enumerate(chapter_list)}
                default_chapter = st.session_state.get("selected_chapter_id")
                default_chapter_index = list(chapter_options.values()).index(default_chapter) if default_chapter in chapter_options.values() else 0
                chapter_label = st.selectbox(i18n.t("chapter_label"), options=list(chapter_options.keys()), index=default_chapter_index)
                chapter_id = chapter_options[chapter_label]
                st.session_state["selected_chapter_id"] = chapter_id
            else:
                st.caption(i18n.t("no_chapters_plan"))
        else:
            st.info(i18n.t("create_project_prompt"))

    with col_ai:
        ai_model = st.selectbox(i18n.t("ai_model_label"), ["GPT-4.1", "Claude 3.5", "Local draft model"], index=0)
        persona = st.selectbox(
            i18n.t("author_voice_label"),
            ["Neutral", "Cinematic", "Wry narrator"],
            index=0,
            format_func=lambda value: i18n.option("persona", value),
        )
        tone = st.selectbox(
            i18n.t("tone_label"),
            ["Balanced", "Darker", "Lighter"],
            index=0,
            format_func=lambda value: i18n.option("tone", value),
        )

    st.markdown("</div>", unsafe_allow_html=True)
    ai_profile = {"model": ai_model, "persona": persona, "tone": tone}
    return stage, project_id, chapter_id, chapter_list, ai_profile


def render_sidebar_create_project(i18n: I18n) -> None:
    st.sidebar.subheader(i18n.t("sidebar_create_project"))
    with st.sidebar.form("new_project_form"):
        proj_name = st.text_input(i18n.t("sidebar_project_name"))
        proj_desc = st.text_area(i18n.t("sidebar_description"), height=80)
        if st.form_submit_button(i18n.t("sidebar_create_project_button")):
            try:
                proj = api.create_project(proj_name, proj_desc)
                st.session_state["selected_project_id"] = proj["id"]
                st.session_state["ui_stage"] = "Plan"
                st.sidebar.success(i18n.t("sidebar_project_created"))
            except Exception as exc:  # noqa: BLE001
                st.sidebar.error(i18n.t("sidebar_create_failed", error=exc))


def main() -> None:
    init_state()
    inject_base_styles()

    i18n = I18n(st.session_state.get("language", "en"))

    top_cols = st.columns([7.4, 1])
    with top_cols[1]:
        lang_toggle = st.toggle(
            i18n.t("language_toggle_label"),
            value=st.session_state.get("language") == "zh",
            help=i18n.t("language_toggle_help"),
        )
        new_lang = "zh" if lang_toggle else "en"
        if new_lang != st.session_state.get("language"):
            st.session_state["language"] = new_lang
            st.rerun()

    with top_cols[0]:
        st.title(i18n.t("app_title"))
        st.caption(i18n.t("app_subtitle"))
        render_status_bar(i18n)

    render_sidebar_create_project(i18n)

    try:
        projects = api.load_projects()
    except Exception as exc:  # noqa: BLE001
        st.error(i18n.t("load_projects_error", error=exc))
        projects = []

    stage, project_id, chapter_id, chapter_list, ai_profile = render_top_bar(projects, i18n)

    if stage == "Plan":
        stages.render_plan_stage(project_id, chapter_list, ai_profile=ai_profile, i18n=i18n)
    elif stage == "Draft":
        stages.render_draft_stage(project_id, chapter_id, ai_profile=ai_profile, i18n=i18n)
    elif stage == "Revise":
        stages.render_revise_stage(project_id, chapter_id, ai_profile=ai_profile, i18n=i18n)
    else:
        stages.render_library_stage(projects, project_id, chapter_list, i18n=i18n)


if __name__ == "__main__":
    main()
