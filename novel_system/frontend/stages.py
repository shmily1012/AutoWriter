from typing import Any, Dict, List, Optional

import streamlit as st

from . import api

AIProfile = Dict[str, Optional[str]]


def _word_progress(content: str, expected: int = 2000) -> None:
    words = len((content or "").split())
    pct = min(words / expected, 1.2) if expected else 0
    col_goal, col_progress, col_pace = st.columns(3)
    col_goal.metric("Target", f"{expected} words", "+ steady pace")
    col_progress.metric("Current", f"{words} words", f"{int(pct * 100)}% of goal")
    pace_label = "On track" if pct >= 0.5 else "Warm-up"
    col_pace.metric("Rhythm", pace_label, "Live")
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
) -> None:
    st.markdown("### Plan")
    if not project_id:
        st.info("Select or create a project to start planning.")
        return

    outline_key = f"plan_outline_{project_id}"
    outline_value = st.session_state.get(outline_key, "")

    col_board, col_ai = st.columns([2.2, 1.1], gap="large")
    with col_board:
        st.markdown("#### Outline board")
        st.text_area("Beats and notes", value=outline_value, height=260, key=outline_key)

        if chapter_list:
            options = {f"{c.get('index', idx) + 1}. {c['title']} (#{c['id']})": c["id"] for idx, c in enumerate(chapter_list)}
            target_label = st.selectbox("Send beats to chapter summary", options=list(options.keys()), key=f"plan_target_{project_id}")
            if st.button("Send to Draft", key=f"plan_send_{project_id}"):
                try:
                    chapter = api.load_chapter(options[target_label])
                    summary_text = st.session_state.get(outline_key, "")
                    api.save_chapter(
                        options[target_label],
                        title=chapter.get("title", ""),
                        summary=summary_text,
                        content=chapter.get("content", ""),
                    )
                    st.success("Summary sent to Draft.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Send failed: {exc}")
        else:
            st.caption("No chapters yet. Add one below to start drafting.")

        st.markdown("---")
        with st.form(f"new_chapter_plan_{project_id}"):
            new_title = st.text_input("New chapter title")
            new_summary = st.text_area("Short summary", height=80)
            if st.form_submit_button("Create chapter"):
                try:
                    api.create_chapter(project_id, new_title, new_summary)
                    st.success("Chapter created. Refresh to load it into the list.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Create failed: {exc}")

    with col_ai:
        st.markdown("#### AI outline coach")
        prompt_key = f"plan_ai_prompt_{project_id}"
        st.text_area(
            "Prompt",
            value=st.session_state.get(
                prompt_key,
                "Draft 5-7 beats that escalate conflict and end on a hook. Keep POV consistent.",
            ),
            height=140,
            key=prompt_key,
        )
        replace_outline = st.checkbox("Replace outline with result", key=f"plan_replace_{project_id}", value=False)
        if st.button("Propose next beats", key=f"plan_ai_{project_id}"):
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
                st.success("Outline updated.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"AI failed: {exc}")


def render_draft_stage(
    project_id: Optional[int],
    chapter_id: Optional[int],
    *,
    ai_profile: AIProfile,
) -> None:
    st.markdown("### Draft")
    if not project_id or not chapter_id:
        st.info("Pick a project and chapter to open the Draft workspace.")
        return

    try:
        chapter = api.load_chapter(chapter_id)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load chapter: {exc}")
        return

    content_key = f"chapter_content_{chapter_id}"
    if content_key not in st.session_state:
        st.session_state[content_key] = chapter.get("content") or ""

    context_data = _fetch_context(project_id)

    _word_progress(st.session_state.get(content_key, ""))

    col_ctx, col_editor, col_ai = st.columns([1.2, 2.3, 1.3], gap="large")

    with col_ctx:
        st.markdown("#### Context rail")
        st.markdown("**Summary**")
        st.write(chapter.get("summary") or "No summary yet.")
        st.markdown("**Cast on stage**")
        for ch in context_data["characters"][:5]:
            label = f"- {ch.get('name', 'Unknown')} — {ch.get('description', '')[:80]}"
            if st.button("Insert", key=f"ctx_char_{chapter_id}_{ch.get('id')}"):
                st.session_state[content_key] = f"{st.session_state.get(content_key, '')}\n\n{label}".strip()
            st.caption(label)
        st.markdown("**World notes**")
        for el in context_data["world"][:5]:
            label = f"[{el.get('type', 'item')}] {el.get('title')} — {el.get('content', '')[:80]}"
            if st.button("Insert", key=f"ctx_world_{chapter_id}_{el.get('id')}"):
                st.session_state[content_key] = f"{st.session_state.get(content_key, '')}\n\n{label}".strip()
            st.caption(label)
        st.markdown("**Foreshadow**")
        for clue in context_data["clues"][:5]:
            label = clue.get("description", "")[:120]
            if st.button("Insert", key=f"ctx_clue_{chapter_id}_{clue.get('id')}"):
                st.session_state[content_key] = f"{st.session_state.get(content_key, '')}\n\n{label}".strip()
            st.caption(label)

    with col_editor:
        st.markdown("#### Chapter editor")
        title = st.text_input("Title", value=chapter.get("title", ""))
        summary = st.text_area("Beat summary", value=chapter.get("summary") or "", height=90)
        content = st.text_area(
            "Chapter markdown",
            value=st.session_state.get(content_key, ""),
            height=420,
            key=content_key,
        )

        quick_cols = st.columns(3)
        with quick_cols[0]:
            if st.button("Tag turning point", key=f"turn_{chapter_id}"):
                st.session_state[content_key] = f"{content}\n\n[TURNING POINT]\n"
        with quick_cols[1]:
            if st.button("Insert beat checklist", key=f"checklist_{chapter_id}"):
                st.session_state[content_key] = f"{content}\n\n- Setup\n- Tension\n- Payoff\n"
        with quick_cols[2]:
            if st.button("Mark for polish", key=f"polish_{chapter_id}"):
                st.session_state[content_key] = f"{content}\n\n[POLISH ME]\n"

        save_cols = st.columns(2)
        with save_cols[0]:
            if st.button("Save chapter", key=f"save_{chapter_id}"):
                try:
                    api.save_chapter(
                        chapter_id,
                        title=title,
                        summary=summary,
                        content=st.session_state.get(content_key, ""),
                    )
                    st.success("Chapter saved.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Save failed: {exc}")
        with save_cols[1]:
            if st.button("Run diagnostics", key=f"diag_{chapter_id}"):
                try:
                    analysis = api.analyze_chapter_api(chapter_id)
                    st.session_state[f"analysis_{chapter_id}"] = analysis
                    st.success("Analysis ready in Revise.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Diagnostics failed: {exc}")

    with col_ai:
        st.markdown("#### Writer Loop")
        prompt_key = f"loop_prompt_{chapter_id}"
        st.text_area(
            "Working prompt",
            value=st.session_state.get(
                prompt_key,
                "Keep POV consistent, honor tone, surface tension between leads.",
            ),
            height=140,
            key=prompt_key,
        )
        replace = st.checkbox("Replace editor text", key=f"ai_replace_{chapter_id}", value=False)
        status_placeholder = st.empty()

        def run_ai(action: str, label: str) -> None:
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
                _push_ai_history(chapter_id, label, generated)
                status_placeholder.success(f"{label} ready and sent to editor.")
            except Exception as exc:  # noqa: BLE001
                status_placeholder.error(f"{label} failed: {exc}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Skeleton", key=f"skeleton_{chapter_id}"):
                run_ai("draft", "Skeleton")
            if st.button("Rewrite tone", key=f"rewrite_{chapter_id}"):
                run_ai("rewrite", "Rewrite")
        with col2:
            if st.button("Expand scene", key=f"expand_{chapter_id}"):
                run_ai("expand", "Expansion")
            if st.button("Polish style", key=f"polish_{chapter_id}"):
                run_ai("polish", "Polish")

        st.markdown("##### AI history")
        history_key = f"ai_history_{chapter_id}"
        history: List[Dict[str, str]] = st.session_state.get(history_key, [])
        if history:
            for idx, item in enumerate(history):
                with st.expander(f"{item['label']} #{idx + 1}"):
                    st.write(item["text"])
                    col_ins, col_rep = st.columns(2)
                    with col_ins:
                        if st.button("Insert", key=f"hist_ins_{chapter_id}_{idx}"):
                            base = st.session_state.get(content_key, "")
                            st.session_state[content_key] = f"{base}\n\n{item['text']}".strip()
                    with col_rep:
                        if st.button("Replace", key=f"hist_rep_{chapter_id}_{idx}"):
                            st.session_state[content_key] = item["text"]
        else:
            st.caption("Run AI actions to see history here.")


def render_revise_stage(
    project_id: Optional[int],
    chapter_id: Optional[int],
    *,
    ai_profile: AIProfile,
) -> None:
    st.markdown("### Revise")
    if not project_id or not chapter_id:
        st.info("Pick a project and chapter to revise.")
        return

    col_checks, col_actions = st.columns([1.4, 1.6], gap="large")
    with col_checks:
        st.markdown("#### Quality checks")
        if st.button("Run quality report", key=f"revise_diag_{chapter_id}"):
            try:
                analysis = api.analyze_chapter_api(chapter_id)
                st.session_state[f"analysis_{chapter_id}"] = analysis
            except Exception as exc:  # noqa: BLE001
                st.error(f"Report failed: {exc}")
        analysis_data = st.session_state.get(f"analysis_{chapter_id}")
        if analysis_data:
            issues = analysis_data.get("issues") if isinstance(analysis_data, dict) else None
            if issues and isinstance(issues, list):
                for idx, issue in enumerate(issues):
                    with st.expander(f"Issue {idx + 1}"):
                        st.write(issue)
            else:
                st.json(analysis_data)
        else:
            st.caption("Run a report to see pacing, OOC, and duplicate beats.")

        st.markdown("#### Stash")
        st.text_area("Scratchpad", key=f"stash_{chapter_id}", height=180)

    with col_actions:
        st.markdown("#### Targeted rewrites")
        snippet = st.text_area("Text to rewrite", height=160, key=f"revise_snippet_{chapter_id}")
        instruction = st.text_area(
            "Rewrite instruction",
            value="Tighten prose, keep POV, raise tension.",
            height=100,
            key=f"revise_instruction_{chapter_id}",
        )
        if st.button("Rewrite selection", key=f"revise_rewrite_{chapter_id}"):
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
                _push_ai_history(chapter_id, "Rewrite", result)
                st.success("Rewrite added to AI history.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Rewrite failed: {exc}")

        st.markdown("#### Targeted polish")
        polish_prompt = st.text_area(
            "Polish prompt",
            value="Polish the latest draft for rhythm and clarity.",
            height=100,
            key=f"revise_polish_prompt_{chapter_id}",
        )
        if st.button("Polish passage", key=f"revise_polish_{chapter_id}"):
            try:
                result = api.ai_generate(
                    polish_prompt,
                    mode="quality",
                    model=ai_profile.get("model"),
                    persona=ai_profile.get("persona"),
                    tone=ai_profile.get("tone"),
                )
                _push_ai_history(chapter_id, "Polish", result)
                st.success("Polish added to AI history.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Polish failed: {exc}")


def render_library_stage(
    projects: List[Dict[str, Any]],
    project_id: Optional[int],
    chapter_list: List[Dict[str, Any]],
) -> None:
    st.markdown("### Library")
    col_projects, col_chapters = st.columns([1.2, 1.8], gap="large")

    with col_projects:
        st.markdown("#### Projects")
        if projects:
            for proj in projects:
                st.markdown(f"**{proj.get('name', 'Untitled')}**")
                st.caption(proj.get("description") or "No description yet.")
                st.markdown("---")
        else:
            st.info("No projects yet.")

    with col_chapters:
        st.markdown("#### Chapters")
        if project_id and chapter_list:
            for c in chapter_list:
                status = "Draft" if c.get("content") else "Pending"
                words = len((c.get("content") or "").split())
                st.markdown(f"**{c.get('index', 0) + 1}. {c['title']}** — {status} — {words} words")
                st.caption(c.get("summary") or "No summary yet.")
                st.markdown("---")
        elif project_id:
            st.caption("No chapters yet. Add one from Plan.")
        else:
            st.info("Select a project to see its chapters.")
