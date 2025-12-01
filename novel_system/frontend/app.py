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


st.title("AI 写作器")
st.caption("选择章节，编辑内容，使用 AI 按钮扩写/润色/生成草稿。")

col_projects, col_editor = st.columns([1.2, 2.8], gap="large")

# -------- Left column: projects & chapters ----------
with col_projects:
    st.subheader("作品 / 章节 / 世界观")

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

# -------- Right column: editor & AI ----------
with col_editor:
    tabs = st.tabs(["章节编辑", "世界观"])

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
