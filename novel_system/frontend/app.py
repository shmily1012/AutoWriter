import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

st.set_page_config(page_title="Novel System", page_icon="📚", layout="wide")


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


def chapter_ai_action(chapter_id: int, action: str, prompt: str) -> str:
    resp = api_post(
        f"/chapters/{chapter_id}/ai/{action}",
        {"prompt": prompt},
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


def ai_improve_character(character_id: int, prompt: str) -> str:
    resp = api_post(f"/characters/{character_id}/ai/improve", {"prompt": prompt})
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


def ai_generate(prompt: str, mode: Optional[str] = None) -> str:
    payload: Dict[str, Any] = {"prompt": prompt}
    if mode:
        payload["mode"] = mode
    resp = api_post("/ai/generate", payload)
    resp.raise_for_status()
    return resp.json().get("generated_text", "")


st.title("AI 写作器")
st.caption("选择章节，编辑内容，使用 AI 按钮扩写/润色/生成草稿。")

col_projects, col_editor = st.columns([1.2, 2.8], gap="large")

# -------- Left column: projects & chapters ----------
with col_projects:
    st.subheader("作品 / 章节 / 世界观 / 人物 / 伏笔")

    # Project creation form
    with st.expander("新建作品", expanded=False):
        with st.form(key="new_project_form"):
            proj_name = st.text_input("作品名称", key="proj_name")
            proj_desc = st.text_area("简介", height=80, key="proj_desc")
            proj_submit = st.form_submit_button("创建作品")
            if proj_submit:
                try:
                    proj = create_project(proj_name, proj_desc)
                    st.session_state["selected_project_id"] = proj["id"]
                    st.success(f"已创建：{proj['name']}")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"创建失败: {exc}")

    # Load projects
    try:
        projects = load_projects()
    except Exception as exc:  # noqa: BLE001
        st.error(f"加载作品失败: {exc}")
        projects = []

    if projects:
        proj_options = {f"{p['name']} (#{p['id']})": p["id"] for p in projects}
        selected_project_id = st.session_state.get("selected_project_id")
        project_labels = list(proj_options.keys())
        if selected_project_id and selected_project_id in proj_options.values():
            default_index = list(proj_options.values()).index(selected_project_id)
        else:
            default_index = 0
        selected_project = st.selectbox(
            "选择作品",
            options=project_labels,
            index=default_index,
        )
        current_project_id = proj_options[selected_project]
        st.session_state["selected_project_id"] = current_project_id
    else:
        st.info("暂无作品，请先创建。")
        current_project_id = None

    chapter_list: List[Dict[str, Any]] = []
    current_chapter_id: Optional[int] = None
    if current_project_id:
        try:
            chapter_list = load_chapters(current_project_id)
        except Exception as exc:  # noqa: BLE001
            st.error(f"加载章节失败: {exc}")
            chapter_list = []

        if chapter_list:
            chapter_options = {
                f"{c['index']+1}. {c['title']} (#{c['id']})": c["id"]
                for c in chapter_list
            }
            selected_chapter_id = st.session_state.get("selected_chapter_id")
            selected_label = None
            if selected_chapter_id:
                for label, cid in chapter_options.items():
                    if cid == selected_chapter_id:
                        selected_label = label
                        break
            selected_label = selected_label or list(chapter_options.keys())[0]
            current_chapter_label = st.radio(
                "章节列表", options=list(chapter_options.keys()), index=list(chapter_options.keys()).index(selected_label)
            )
            current_chapter_id = chapter_options[current_chapter_label]
            st.session_state["selected_chapter_id"] = current_chapter_id
        else:
            st.info("暂无章节，请新建。")
            current_chapter_id = None

        with st.form(key="new_chapter_form"):
            new_chapter_title = st.text_input("新建章节标题", key="new_chapter_title")
            new_chapter_summary = st.text_area("章节摘要（可选）", key="new_chapter_summary", height=80)
            if st.form_submit_button("创建章节"):
                try:
                    chap = create_chapter(current_project_id, new_chapter_title, new_chapter_summary)
                    st.session_state["selected_chapter_id"] = chap["id"]
                    st.success(f"章节已创建：{chap['title']}")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"创建章节失败: {exc}")

        # Save chapter list in session for other tabs
        st.session_state["chapter_list_for_tabs"] = chapter_list

        # World elements list
        st.markdown("---")
        st.caption("世界观条目")
        world_elements = []
        if current_project_id:
            try:
                world_elements = list_world_elements(current_project_id)
            except Exception as exc:  # noqa: BLE001
                st.error(f"加载世界观失败: {exc}")
                world_elements = []

        if world_elements:
            for we in world_elements:
                with st.expander(f"{we['type']} - {we['title']} (#{we['id']})", expanded=False):
                    st.write(we.get("content") or "")
                    extra = we.get("extra")
                    if extra:
                        st.json(extra)
                    new_type = st.text_input("类型", value=we["type"], key=f"we_type_{we['id']}")
                    new_title = st.text_input("标题", value=we["title"], key=f"we_title_{we['id']}")
                    new_content = st.text_area("内容", value=we.get("content") or "", key=f"we_content_{we['id']}")
                    new_extra = st.text_area("额外信息（JSON）", value="", key=f"we_extra_{we['id']}")
                    if st.button("保存修改", key=f"we_save_{we['id']}"):
                        payload: Dict[str, Any] = {
                            "type": new_type,
                            "title": new_title,
                            "content": new_content,
                        }
                        if new_extra.strip():
                            try:
                                import json
                                payload["extra"] = json.loads(new_extra)
                            except Exception:
                                st.error("额外信息需为 JSON 格式")
                                payload = None
                        if payload:
                            try:
                                update_world_element(we["id"], payload)
                                st.success("已更新")
                            except Exception as exc:  # noqa: BLE001
                                st.error(f"更新失败: {exc}")

        with st.expander("新建世界观条目", expanded=False):
            with st.form(key="new_world_element_form"):
                we_type = st.text_input("类型（如 势力/地点/科技）", key="we_type_new")
                we_title = st.text_input("标题", key="we_title_new")
                we_content = st.text_area("内容", height=120, key="we_content_new")
                if st.form_submit_button("创建世界观条目"):
                    try:
                        create_world_element(
                            current_project_id,
                            {"type": we_type, "title": we_title, "content": we_content},
                        )
                        st.success("已创建世界观条目")
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"创建失败: {exc}")

        # Characters list
        st.markdown("---")
        st.caption("人物角色")
        characters = []
        if current_project_id:
            try:
                characters = list_characters(current_project_id)
            except Exception as exc:  # noqa: BLE001
                st.error(f"加载人物失败: {exc}")
                characters = []

        if characters:
            for ch in characters:
                with st.expander(f"{ch['name']} (#{ch['id']}) - {ch.get('role') or ''}", expanded=False):
                    st.write(ch.get("description") or "")
                    new_name = st.text_input("姓名", value=ch["name"], key=f"ch_name_{ch['id']}")
                    new_role = st.text_input("角色定位", value=ch.get("role") or "", key=f"ch_role_{ch['id']}")
                    new_desc = st.text_area("设定", value=ch.get("description") or "", key=f"ch_desc_{ch['id']}")
                    new_arc = st.text_area("弧线", value=ch.get("arc") or "", key=f"ch_arc_{ch['id']}")
                    if st.button("保存角色", key=f"ch_save_{ch['id']}"):
                        try:
                            update_character(
                                ch["id"],
                                {"name": new_name, "role": new_role, "description": new_desc, "arc": new_arc},
                            )
                            st.success("已更新角色")
                        except Exception as exc:  # noqa: BLE001
                            st.error(f"更新失败: {exc}")

        with st.expander("新建角色", expanded=False):
            with st.form(key="new_character_form"):
                ch_name = st.text_input("姓名", key="ch_name_new")
                ch_role = st.text_input("角色定位", key="ch_role_new")
                ch_desc = st.text_area("设定", height=100, key="ch_desc_new")
                ch_arc = st.text_area("弧线", height=100, key="ch_arc_new")
                if st.form_submit_button("创建角色"):
                    try:
                        create_character(
                            current_project_id,
                            {"name": ch_name, "role": ch_role, "description": ch_desc, "arc": ch_arc},
                        )
                        st.success("已创建角色")
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"创建失败: {exc}")

# -------- Right column: editor & AI ----------
with col_editor:
    tabs = st.tabs(["章节编辑", "世界观", "人物", "伏笔/线索"])

    # -------- Tab: Chapter editing --------
    with tabs[0]:
        st.subheader("章节编辑")
        if not current_project_id or not st.session_state.get("selected_chapter_id"):
            st.info("请选择作品和章节后开始编辑。")
        else:
            cid = st.session_state["selected_chapter_id"]
            try:
                chapter_data = load_chapter(cid)
            except Exception as exc:  # noqa: BLE001
                st.error(f"加载章节内容失败: {exc}")
                chapter_data = None

            if chapter_data:
                title = st.text_input("标题", value=chapter_data.get("title", ""))
                summary = st.text_area("摘要", value=chapter_data.get("summary") or "", height=100)
                content = st.text_area(
                    "正文",
                    value=chapter_data.get("content") or "",
                    height=400,
                    key=f"chapter_content_{cid}",
                )

                ai_prompt = st.text_area(
                    "AI 提示词", value="继续写下去", height=120, key=f"ai_prompt_{cid}"
                )
                replace_mode = st.checkbox("用 AI 结果替换正文（默认追加）", value=False)

                col_btn1, col_btn2, col_btn3, col_btn_save = st.columns([1, 1, 1, 1])
                ai_result_placeholder = st.empty()
                analysis_placeholder = st.empty()

                def handle_ai(action: str):
                    try:
                        generated = chapter_ai_action(cid, action, ai_prompt)
                        new_content = (
                            generated
                            if replace_mode
                            else (content + "\n\n" + generated if content else generated)
                        )
                        st.session_state[f"chapter_content_{cid}"] = new_content
                        ai_result_placeholder.success("AI 生成完成，已写入正文框。")
                    except Exception as exc:  # noqa: BLE001
                        ai_result_placeholder.error(f"AI 调用失败: {exc}")

                with col_btn1:
                    if st.button("用 AI 扩写"):
                        handle_ai("expand")
                with col_btn2:
                    if st.button("用 AI 润色"):
                        handle_ai("rewrite")
                with col_btn3:
                    if st.button("根据大纲生成草稿"):
                        handle_ai("draft")

                with col_btn_save:
                    if st.button("保存章节"):
                        try:
                            updated = save_chapter(
                                cid,
                                title=title,
                                summary=summary,
                                content=st.session_state.get(f"chapter_content_{cid}", content),
                            )
                            st.success(f"已保存：{updated.get('title')}")
                        except Exception as exc:  # noqa: BLE001
                            st.error(f"保存失败: {exc}")
                with st.expander("标记伏笔"):
                    clue_desc = st.text_area("伏笔描述", height=80, key=f"clue_desc_{cid}")
                    if st.button("创建伏笔记录", key=f"create_clue_{cid}"):
                        try:
                            create_clue(
                                current_project_id,
                                {
                                    "description": clue_desc or (content[:80] if content else "伏笔"),
                                    "introduced_chapter_id": cid,
                                    "status": "unresolved",
                                },
                            )
                            st.success("伏笔已创建")
                        except Exception as exc:  # noqa: BLE001
                            st.error(f"创建失败: {exc}")
                if st.button("分析本章（提取人物/设定/伏笔）"):
                    try:
                        result = analyze_chapter_api(cid)
                        st.session_state[f"chapter_analysis_{cid}"] = result
                        analysis_placeholder.success("分析完成，结果如下：")
                    except Exception as exc:  # noqa: BLE001
                        analysis_placeholder.error(f"分析失败: {exc}")

                analysis_data = st.session_state.get(f"chapter_analysis_{cid}")
                if analysis_data:
                    st.markdown("**分析结果**")
                    st.json(analysis_data)

                # Intelligent hints
                st.markdown("---")
                st.subheader("AI 智能提示栏")
                hint_placeholder = st.empty()
                if st.button("获取智能提示", key=f"smart_hints_{cid}"):
                    hints = {}
                    # Related world/chapters via vector search
                    try:
                        hints["world_related"] = search_related(
                            current_project_id, (summary or "") + "\n" + (content or ""), top_k=5
                        )
                    except Exception:
                        hints["world_related"] = []
                    # Characters matched by name occurrence
                    try:
                        chars = list_characters(current_project_id)
                        matched = [
                            {"name": c["name"], "role": c.get("role"), "description": c.get("description")}
                            for c in chars
                            if c["name"] and c["name"] in (content or "")
                        ]
                        hints["characters"] = matched[:5]
                    except Exception:
                        hints["characters"] = []
                    # Clues unresolved, filter by keyword
                    try:
                        clues = list_clues(current_project_id, status_filter="unresolved")
                        key = summary or content or ""
                        filtered = [
                            c for c in clues if (key and key[:200].lower() in (c.get("description") or "").lower())
                            or any(ch.get("name") in (c.get("description") or "") for ch in hints.get("characters", []))
                        ]
                        hints["clues"] = filtered[:5]
                    except Exception:
                        hints["clues"] = []
                    # Plot suggestions via GPT
                    try:
                        prompt = (
                            "当前章节内容：\n"
                            f"{content[:1200] if content else ''}\n\n"
                            "请给出 3 条下一步剧情/改进建议，使用简短要点。"
                        )
                        hints["plot_suggestions"] = ai_generate(prompt, mode="plot_suggestions")
                    except Exception:
                        hints["plot_suggestions"] = ""
                    st.session_state[f"hints_{cid}"] = hints

                hints = st.session_state.get(f"hints_{cid}")
                if hints:
                    with hint_placeholder.container():
                        st.markdown("**相关世界观/片段**")
                        if hints.get("world_related"):
                            for item in hints["world_related"]:
                                st.write(f"- [{item.get('type')}] {item.get('content')}")
                        else:
                            st.caption("暂无")
                        st.markdown("**相关人物**")
                        if hints.get("characters"):
                            for ch in hints["characters"]:
                                st.write(f"- {ch.get('name')}：{(ch.get('description') or '')[:80]}")
                        else:
                            st.caption("暂无")
                        st.markdown("**未回收伏笔提醒**")
                        if hints.get("clues"):
                            for cl in hints["clues"]:
                                st.write(f"- {cl.get('description')}")
                        else:
                            st.caption("暂无")
                        st.markdown("**AI 剧情建议**")
                        if hints.get("plot_suggestions"):
                            st.write(hints["plot_suggestions"])
                        else:
                            st.caption("暂无")

    # -------- Tab: World elements --------
    with tabs[1]:
        st.subheader("世界观管理")
        if not current_project_id:
            st.info("请选择作品")
        else:
            search_query = st.text_input("相似检索关键词", key="we_search_query")
            if st.button("相似检索", key="we_search_btn"):
                try:
                    res = search_related(current_project_id, search_query, top_k=5)
                    st.write(res)
                except Exception as exc:  # noqa: BLE001
                    st.error(f"检索失败: {exc}")

            st.markdown("### AI 生成世界观骨架")
            with st.form(key="we_ai_form"):
                genre = st.text_input("题材/风格", value="仙侠", key="we_ai_genre")
                idea = st.text_area("简短设想", value="一个关于赤霄宗与世家之争的世界", height=120, key="we_ai_idea")
                if st.form_submit_button("生成世界观骨架"):
                    try:
                        prompt = (
                            f"题材：{genre}\n设想：{idea}\n"
                            "请用列表列出世界观骨架，包含：世界背景、主要势力、关键城市或地点、科技/修炼体系等，每项一条。"
                        )
                        generated = chapter_ai_action(
                            st.session_state.get("selected_chapter_id", 0) or 0,
                            "world_skeleton",
                            prompt,
                        )
                        st.session_state["we_ai_result"] = generated
                        st.success("已生成，请在下方拆分保存。")
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"生成失败: {exc}")

            ai_result = st.session_state.get("we_ai_result")
            if ai_result:
                st.text_area("AI 生成结果（请按行拆分保存）", value=ai_result, height=200, key="we_ai_result_area")
                if st.button("将生成结果拆分保存为世界观条目"):
                    lines = [line.strip(" -") for line in ai_result.splitlines() if line.strip()]
                    success_count = 0
                    for line in lines:
                        try:
                            create_world_element(
                                current_project_id,
                                {"type": "world", "title": line[:40], "content": line},
                            )
                            success_count += 1
                        except Exception:
                            pass
                    st.success(f"已保存 {success_count} 条世界观条目")

    # -------- Tab: Characters --------
    with tabs[2]:
        st.subheader("人物角色")
        if not current_project_id:
            st.info("请选择作品")
        else:
            # reload characters for editing context
            chars = []
            try:
                chars = list_characters(current_project_id)
            except Exception as exc:  # noqa: BLE001
                st.error(f"加载人物失败: {exc}")

            if chars:
                selected_char = st.selectbox(
                    "选择角色",
                    options=[f"{c['name']} (#{c['id']})" for c in chars],
                )
                selected_id = int(selected_char.split("#")[-1].rstrip(")"))
                current_char = next((c for c in chars if c["id"] == selected_id), None)
            else:
                current_char = None

            if current_char:
                name = st.text_input("姓名", value=current_char.get("name", ""))
                role = st.text_input("角色定位", value=current_char.get("role") or "")
                desc = st.text_area("设定", value=current_char.get("description") or "", height=160)
                arc = st.text_area("弧线", value=current_char.get("arc") or "", height=160)
                ai_prompt_char = st.text_area("AI 优化提示词", value="帮我丰富人物性格与背景", height=120)

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("保存角色信息"):
                        try:
                            update_character(
                                current_char["id"],
                                {"name": name, "role": role, "description": desc, "arc": arc},
                            )
                            st.success("已保存角色")
                        except Exception as exc:  # noqa: BLE001
                            st.error(f"保存失败: {exc}")
                with col_c2:
                    if st.button("AI 优化设定"):
                        try:
                            improved = ai_improve_character(current_char["id"], ai_prompt_char)
                            st.session_state["ai_char_improved"] = improved
                            st.success("AI 已生成，请酌情写入设定框。")
                        except Exception as exc:  # noqa: BLE001
                            st.error(f"AI 调用失败: {exc}")
                if st.session_state.get("ai_char_improved"):
                    st.text_area(
                        "AI 生成结果",
                        value=st.session_state["ai_char_improved"],
                        height=180,
                        key="ai_char_improved_area",
                    )

            st.markdown("---")
            with st.expander("新建角色"):
                with st.form(key="new_character_form_tab"):
                    ch_name = st.text_input("姓名", key="ch_name_new_tab")
                    ch_role = st.text_input("角色定位", key="ch_role_new_tab")
                    ch_desc = st.text_area("设定", height=100, key="ch_desc_new_tab")
                    ch_arc = st.text_area("弧线", height=100, key="ch_arc_new_tab")
                    if st.form_submit_button("创建角色", key="create_char_btn_tab"):
                        try:
                            create_character(
                                current_project_id,
                                {"name": ch_name, "role": ch_role, "description": ch_desc, "arc": ch_arc},
                            )
                            st.success("已创建角色")
                        except Exception as exc:  # noqa: BLE001
                            st.error(f"创建失败: {exc}")

    # -------- Tab: Clues --------
    with tabs[3]:
        st.subheader("伏笔 & 线索")
        if not current_project_id:
            st.info("请选择作品")
        else:
            status_filter = st.selectbox("按状态过滤", options=["all", "unresolved", "resolved"], index=0)
            search_term = st.text_input("搜索描述关键词", key="clue_search")
            try:
                clues = list_clues(
                    current_project_id,
                    status_filter=None if status_filter == "all" else status_filter,
                )
            except Exception as exc:  # noqa: BLE001
                st.error(f"加载伏笔失败: {exc}")
                clues = []

            if search_term:
                clues = [c for c in clues if search_term.lower() in (c.get("description") or "").lower()]

            chapter_options = {c["id"]: f"{c['index']+1}. {c['title']}" for c in st.session_state.get("chapter_list_for_tabs", [])}
            chapter_labels = list(chapter_options.values())
            label_to_id = {v: k for k, v in chapter_options.items()}

            for clue in clues:
                with st.expander(f"{clue['description'][:40]} (#{clue['id']}) - {clue['status']}", expanded=False):
                    desc = st.text_area("描述", value=clue.get("description") or "", key=f"clue_desc_edit_{clue['id']}")
                    status_val = st.selectbox(
                        "状态",
                        options=["unresolved", "resolved"],
                        index=0 if clue.get("status") == "unresolved" else 1,
                        key=f"clue_status_{clue['id']}",
                    )
                    intro_default = 0
                    res_default = 0
                    if clue.get("introduced_chapter_id") in chapter_options:
                        intro_default = chapter_labels.index(chapter_options[clue["introduced_chapter_id"]]) + 1
                    if clue.get("resolved_chapter_id") in chapter_options:
                        res_default = chapter_labels.index(chapter_options[clue["resolved_chapter_id"]]) + 1
                    introduced_val = st.selectbox(
                        "埋伏章节",
                        options=["未设置"] + chapter_labels,
                        index=intro_default,
                        key=f"clue_intro_{clue['id']}",
                    )
                    resolved_val = st.selectbox(
                        "回收章节",
                        options=["未设置"] + chapter_labels,
                        index=res_default,
                        key=f"clue_resolved_{clue['id']}",
                    )
                    if st.button("保存伏笔", key=f"clue_save_{clue['id']}"):
                        payload = {
                            "description": desc,
                            "status": status_val,
                        }
                        if introduced_val != "未设置":
                            payload["introduced_chapter_id"] = label_to_id[introduced_val]
                        if resolved_val != "未设置":
                            payload["resolved_chapter_id"] = label_to_id[resolved_val]
                        try:
                            update_clue(clue["id"], payload)
                            st.success("已更新伏笔")
                        except Exception as exc:  # noqa: BLE001
                            st.error(f"更新失败: {exc}")
