from typing import Any, Dict, List, Optional

import streamlit as st

from . import api
from .i18n import I18n

AIProfile = Dict[str, Optional[str]]


def _set_status(i18n: I18n, action_label: str) -> None:
    st.session_state["action_status"] = i18n.t("status_working", action=action_label)


def _clear_status() -> None:
    st.session_state["action_status"] = None


def _word_progress(content: str, expected: int = 2000, *, i18n: I18n) -> None:
    words = len((content or "").split())
    pct = min(words / expected, 1.2) if expected else 0
    col_goal, col_progress, col_pace = st.columns(3)
    col_goal.metric(i18n.t("target_label"), f"{expected} {i18n.t('words_unit')}", i18n.t("steady_pace_delta"))
    col_progress.metric(i18n.t("current_label"), f"{words} {i18n.t('words_unit')}", i18n.t("goal_percent", percent=int(pct * 100)))
    pace_label = i18n.t("on_track") if pct >= 0.5 else i18n.t("warm_up")
    col_pace.metric(i18n.t("rhythm_label"), pace_label, i18n.t("live_delta"))
    st.progress(min(pct, 1.0))


def _fetch_context(project_id: int) -> Dict[str, List[Dict[str, Any]]]:
    data: Dict[str, List[Dict[str, Any]]] = {"characters": [], "world": [], "clues": []}
    try:
        data["characters"] = api.list_characters(project_id)
    except Exception:
        data["characters"] = []
    try:
        data["world"] = api.list_world_elements(project_id)
    except Exception:
        data["world"] = []
    try:
        data["clues"] = api.list_clues(project_id, status_filter="unresolved")
    except Exception:
        data["clues"] = []
    return data


def _push_ai_history(chapter_id: int, label: str, text: str) -> None:
    key = f"ai_history_{chapter_id}"
    history: List[Dict[str, str]] = st.session_state.get(key, [])
    history.insert(0, {"label": label, "text": text})
    st.session_state[key] = history[:5]


def render_plan_stage(
    project_id: Optional[int],
    chapter_list: List[Dict[str, Any]],
    *,
    ai_profile: AIProfile,
    i18n: I18n,
) -> None:
    st.markdown(f"### {i18n.t('heading_plan')}")
    if not project_id:
        st.info(i18n.t("info_select_project_plan"))
        return

    outline_key = f"plan_outline_{project_id}"
    outline_value = st.session_state.get(outline_key, "")

    col_board, col_ai = st.columns([2.2, 1.1], gap="large")
    with col_board:
        st.markdown(f"#### {i18n.t('outline_board')}")
        st.text_area(i18n.t("beats_notes"), value=outline_value, height=260, key=outline_key)

        if chapter_list:
            options = {f"{c.get('index', idx) + 1}. {c['title']} (#{c['id']})": c["id"] for idx, c in enumerate(chapter_list)}
            target_label = st.selectbox(
                i18n.t("send_beats_label"),
                options=list(options.keys()),
                key=f"plan_target_{project_id}",
            )
            if st.button(i18n.t("send_to_draft"), key=f"plan_send_{project_id}"):
                _set_status(i18n, i18n.t("send_to_draft"))
                try:
                    chapter = api.load_chapter(options[target_label])
                    summary_text = st.session_state.get(outline_key, "")
                    api.save_chapter(
                        options[target_label],
                        title=chapter.get("title", ""),
                        summary=summary_text,
                        content=chapter.get("content", ""),
                    )
                    st.success(i18n.t("summary_sent_success"))
                except Exception as exc:  # noqa: BLE001
                    st.error(i18n.t("send_failed", error=exc))
                finally:
                    _clear_status()
        else:
            st.caption(i18n.t("no_chapters_plan_below"))

        st.markdown("---")
        with st.form(f"new_chapter_plan_{project_id}"):
            new_title = st.text_input(i18n.t("new_chapter_title"))
            new_summary = st.text_area(i18n.t("short_summary"), height=80)
            if st.form_submit_button(i18n.t("create_chapter_button")):
                _set_status(i18n, i18n.t("create_chapter_button"))
                try:
                    api.create_chapter(project_id, new_title, new_summary)
                    st.success(i18n.t("chapter_created_prompt"))
                except Exception as exc:  # noqa: BLE001
                    st.error(i18n.t("create_failed", error=exc))
                finally:
                    _clear_status()

    with col_ai:
        st.markdown(f"#### {i18n.t('ai_outline_coach')}")
        prompt_key = f"plan_ai_prompt_{project_id}"
        st.text_area(
            i18n.t("prompt_label"),
            value=st.session_state.get(
                prompt_key,
                i18n.t("default_outline_prompt"),
            ),
            height=140,
            key=prompt_key,
        )
        replace_outline = st.checkbox(i18n.t("replace_outline_checkbox"), key=f"plan_replace_{project_id}", value=False)
        if st.button(i18n.t("propose_beats_button"), key=f"plan_ai_{project_id}"):
            _set_status(i18n, i18n.t("propose_beats_button"))
            try:
                suggestion = api.ai_generate(
                    st.session_state[prompt_key],
                    mode="outline",
                    model=ai_profile.get("model"),
                    persona=ai_profile.get("persona"),
                    tone=ai_profile.get("tone"),
                    role="plot_coach",
                )
                base = st.session_state.get(outline_key, "")
                st.session_state[outline_key] = suggestion if replace_outline else f"{base}\n\n{suggestion}".strip()
                st.success(i18n.t("outline_updated"))
            except Exception as exc:  # noqa: BLE001
                st.error(i18n.t("ai_failed", error=exc))
            finally:
                _clear_status()


def render_draft_stage(
    project_id: Optional[int],
    chapter_id: Optional[int],
    *,
    ai_profile: AIProfile,
    i18n: I18n,
) -> None:
    st.markdown(f"### {i18n.t('heading_draft')}")
    if not project_id or not chapter_id:
        st.info(i18n.t("info_pick_project_chapter"))
        return

    try:
        chapter = api.load_chapter(chapter_id)
    except Exception as exc:  # noqa: BLE001
        st.error(i18n.t("load_chapter_error", error=exc))
        return

    content_key = f"chapter_content_{chapter_id}"
    if content_key not in st.session_state:
        st.session_state[content_key] = chapter.get("content") or ""

    context_data = _fetch_context(project_id)

    _word_progress(st.session_state.get(content_key, ""), i18n=i18n)

    col_ctx, col_editor, col_ai = st.columns([1.2, 2.3, 1.3], gap="large")

    with col_ctx:
        st.markdown(f"#### {i18n.t('context_rail')}")
        st.markdown(f"**{i18n.t('summary_label')}**")
        st.write(chapter.get("summary") or i18n.t("no_summary"))
        st.markdown(f"**{i18n.t('cast_on_stage')}**")
        for ch in context_data["characters"][:5]:
            label = f"- {ch.get('name') or i18n.t('unknown')} — {ch.get('description', '')[:80]}"
            if st.button(i18n.t("insert"), key=f"ctx_char_{chapter_id}_{ch.get('id')}"):
                st.session_state[content_key] = f"{st.session_state.get(content_key, '')}\n\n{label}".strip()
            st.caption(label)
        st.markdown(f"**{i18n.t('world_notes')}**")
        for el in context_data["world"][:5]:
            label = f"[{el.get('type', i18n.t('item_label'))}] {el.get('title')} — {el.get('content', '')[:80]}"
            if st.button(i18n.t("insert"), key=f"ctx_world_{chapter_id}_{el.get('id')}"):
                st.session_state[content_key] = f"{st.session_state.get(content_key, '')}\n\n{label}".strip()
            st.caption(label)
        st.markdown(f"**{i18n.t('foreshadow')}**")
        for clue in context_data["clues"][:5]:
            label = clue.get("description", "")[:120]
            if st.button(i18n.t("insert"), key=f"ctx_clue_{chapter_id}_{clue.get('id')}"):
                st.session_state[content_key] = f"{st.session_state.get(content_key, '')}\n\n{label}".strip()
            st.caption(label)

    with col_editor:
        st.markdown(f"#### {i18n.t('chapter_editor')}")
        title = st.text_input(i18n.t("title_label"), value=chapter.get("title", ""))
        summary = st.text_area(i18n.t("beat_summary"), value=chapter.get("summary") or "", height=90)
        content = st.text_area(
            i18n.t("chapter_markdown"),
            value=st.session_state.get(content_key, ""),
            height=420,
            key=content_key,
        )

        quick_cols = st.columns(3)
        with quick_cols[0]:
            if st.button(i18n.t("tag_turning_point"), key=f"turn_{chapter_id}"):
                st.session_state[content_key] = f"{content}\n\n{i18n.t('turning_point_marker')}\n"
        with quick_cols[1]:
            if st.button(i18n.t("insert_beat_checklist"), key=f"checklist_{chapter_id}"):
                st.session_state[content_key] = (
                    f"{content}\n\n- {i18n.t('checklist_setup')}\n- {i18n.t('checklist_tension')}\n- {i18n.t('checklist_payoff')}\n"
                )
        with quick_cols[2]:
            if st.button(i18n.t("mark_for_polish"), key=f"polish_{chapter_id}"):
                st.session_state[content_key] = f"{content}\n\n{i18n.t('polish_marker')}\n"

        save_cols = st.columns(2)
        with save_cols[0]:
            if st.button(i18n.t("save_chapter_button"), key=f"save_{chapter_id}"):
                _set_status(i18n, i18n.t("save_chapter_button"))
                try:
                    api.save_chapter(
                        chapter_id,
                        title=title,
                        summary=summary,
                        content=st.session_state.get(content_key, ""),
                    )
                    st.success(i18n.t("chapter_saved"))
                except Exception as exc:  # noqa: BLE001
                    st.error(i18n.t("save_failed", error=exc))
                finally:
                    _clear_status()
        with save_cols[1]:
            if st.button(i18n.t("run_diagnostics_button"), key=f"diag_{chapter_id}"):
                _set_status(i18n, i18n.t("run_diagnostics_button"))
                try:
                    analysis = api.analyze_chapter_api(chapter_id)
                    st.session_state[f"analysis_{chapter_id}"] = analysis
                    st.success(i18n.t("analysis_ready"))
                except Exception as exc:  # noqa: BLE001
                    st.error(i18n.t("diagnostics_failed", error=exc))
                finally:
                    _clear_status()

    with col_ai:
        st.markdown(f"#### {i18n.t('writer_loop')}")
        prompt_key = f"loop_prompt_{chapter_id}"
        st.text_area(
            i18n.t("working_prompt"),
            value=st.session_state.get(
                prompt_key,
                i18n.t("default_working_prompt"),
            ),
            height=140,
            key=prompt_key,
        )
        replace = st.checkbox(i18n.t("replace_editor_text"), key=f"ai_replace_{chapter_id}", value=False)
        status_placeholder = st.empty()

        def run_ai(action: str, label_key: str) -> None:
            label_text = i18n.t(label_key)
            _set_status(i18n, label_text)
            try:
                generated = api.chapter_ai_action(
                    chapter_id,
                    action,
                    st.session_state[prompt_key],
                    model=ai_profile.get("model"),
                    persona=ai_profile.get("persona"),
                    tone=ai_profile.get("tone"),
                )
                if replace:
                    st.session_state[content_key] = generated
                else:
                    base = st.session_state.get(content_key, "")
                    st.session_state[content_key] = f"{base}\n\n{generated}".strip()
                _push_ai_history(chapter_id, label_text, generated)
                status_placeholder.success(i18n.t("ai_action_success", label=label_text))
            except Exception as exc:  # noqa: BLE001
                status_placeholder.error(i18n.t("ai_action_failed", label=label_text, error=exc))
            finally:
                _clear_status()

        col1, col2 = st.columns(2)
        with col1:
            if st.button(i18n.t("skeleton_button"), key=f"skeleton_{chapter_id}"):
                run_ai("draft", "skeleton_button")
            if st.button(i18n.t("rewrite_tone_button"), key=f"rewrite_{chapter_id}"):
                run_ai("rewrite", "rewrite_tone_button")
        with col2:
            if st.button(i18n.t("expand_scene_button"), key=f"expand_{chapter_id}"):
                run_ai("expand", "expand_scene_button")
            if st.button(i18n.t("polish_style_button"), key=f"polish_{chapter_id}"):
                run_ai("polish", "polish_style_button")

        st.markdown(f"##### {i18n.t('ai_history')}")
        history_key = f"ai_history_{chapter_id}"
        history: List[Dict[str, str]] = st.session_state.get(history_key, [])
        if history:
            for idx, item in enumerate(history):
                with st.expander(i18n.t("ai_history_item", label=item["label"], index=idx + 1)):
                    st.write(item["text"])
                    col_ins, col_rep = st.columns(2)
                    with col_ins:
                        if st.button(i18n.t("insert"), key=f"hist_ins_{chapter_id}_{idx}"):
                            base = st.session_state.get(content_key, "")
                            st.session_state[content_key] = f"{base}\n\n{item['text']}".strip()
                    with col_rep:
                        if st.button(i18n.t("replace"), key=f"hist_rep_{chapter_id}_{idx}"):
                            st.session_state[content_key] = item["text"]
        else:
            st.caption(i18n.t("history_empty"))


def render_revise_stage(
    project_id: Optional[int],
    chapter_id: Optional[int],
    *,
    ai_profile: AIProfile,
    i18n: I18n,
) -> None:
    st.markdown(f"### {i18n.t('heading_revise')}")
    if not project_id or not chapter_id:
        st.info(i18n.t("info_pick_project_revise"))
        return

    col_checks, col_actions = st.columns([1.4, 1.6], gap="large")
    with col_checks:
        st.markdown(f"#### {i18n.t('quality_checks')}")
        if st.button(i18n.t("run_quality_report"), key=f"revise_diag_{chapter_id}"):
            _set_status(i18n, i18n.t("run_quality_report"))
            try:
                analysis = api.analyze_chapter_api(chapter_id)
                st.session_state[f"analysis_{chapter_id}"] = analysis
            except Exception as exc:  # noqa: BLE001
                st.error(i18n.t("report_failed", error=exc))
            finally:
                _clear_status()
        analysis_data = st.session_state.get(f"analysis_{chapter_id}")
        if analysis_data:
            issues = analysis_data.get("issues") if isinstance(analysis_data, dict) else None
            if issues and isinstance(issues, list):
                for idx, issue in enumerate(issues):
                    with st.expander(i18n.t("issue_label", index=idx + 1)):
                        st.write(issue)
            else:
                st.json(analysis_data)
        else:
            st.caption(i18n.t("report_caption"))

        st.markdown(f"#### {i18n.t('stash')}")
        st.text_area(i18n.t("stash"), key=f"stash_{chapter_id}", height=180)

    with col_actions:
        st.markdown(f"#### {i18n.t('targeted_rewrites')}")
        snippet = st.text_area(i18n.t("text_to_rewrite"), height=160, key=f"revise_snippet_{chapter_id}")
        instruction = st.text_area(
            i18n.t("rewrite_instruction"),
            value=i18n.t("default_rewrite_instruction"),
            height=100,
            key=f"revise_instruction_{chapter_id}",
        )
        if st.button(i18n.t("rewrite_selection"), key=f"revise_rewrite_{chapter_id}"):
            _set_status(i18n, i18n.t("rewrite_selection"))
            try:
                prompt = f"{instruction}\n\n---\n{snippet}"
                result = api.chapter_ai_action(
                    chapter_id,
                    "rewrite",
                    prompt,
                    model=ai_profile.get("model"),
                    persona=ai_profile.get("persona"),
                    tone=ai_profile.get("tone"),
                )
                _push_ai_history(chapter_id, i18n.t("rewrite_selection"), result)
                st.success(i18n.t("rewrite_added_history"))
            except Exception as exc:  # noqa: BLE001
                st.error(i18n.t("rewrite_failed", error=exc))
            finally:
                _clear_status()

        st.markdown(f"#### {i18n.t('targeted_polish')}")
        polish_prompt = st.text_area(
            i18n.t("polish_prompt"),
            value=i18n.t("default_polish_prompt"),
            height=100,
            key=f"revise_polish_prompt_{chapter_id}",
        )
        if st.button(i18n.t("polish_passage"), key=f"revise_polish_{chapter_id}"):
            _set_status(i18n, i18n.t("polish_passage"))
            try:
                result = api.ai_generate(
                    polish_prompt,
                    mode="quality",
                    model=ai_profile.get("model"),
                    persona=ai_profile.get("persona"),
                    tone=ai_profile.get("tone"),
                )
                _push_ai_history(chapter_id, i18n.t("polish_passage"), result)
                st.success(i18n.t("polish_added_history"))
            except Exception as exc:  # noqa: BLE001
                st.error(i18n.t("polish_failed", error=exc))
            finally:
                _clear_status()


def render_library_stage(
    projects: List[Dict[str, Any]],
    project_id: Optional[int],
    chapter_list: List[Dict[str, Any]],
    i18n: I18n,
) -> None:
    st.markdown(f"### {i18n.t('heading_library')}")
    col_projects, col_chapters = st.columns([1.2, 1.8], gap="large")

    with col_projects:
        st.markdown(f"#### {i18n.t('projects_heading')}")
        if projects:
            for proj in projects:
                st.markdown(f"**{proj.get('name', 'Untitled')}**")
                st.caption(proj.get("description") or i18n.t("no_description"))
                st.markdown("---")
        else:
            st.info(i18n.t("no_projects"))

    with col_chapters:
        st.markdown(f"#### {i18n.t('chapters_heading')}")
        if project_id and chapter_list:
            for c in chapter_list:
                status = i18n.status("Draft" if c.get("content") else "Pending")
                words = len((c.get("content") or "").split())
                st.markdown(f"**{c.get('index', 0) + 1}. {c['title']}** — {status} — {words} {i18n.t('words_unit')}")
                st.caption(c.get("summary") or i18n.t("no_summary"))
                st.markdown("---")
        elif project_id:
            st.caption(i18n.t("no_chapters_library"))
        else:
            st.info(i18n.t("select_project_to_see_chapters"))
