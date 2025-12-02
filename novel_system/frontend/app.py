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


# ---------------- UI Helpers -----------------


def render_top_bar() -> Dict[str, Any]:
    st.markdown(
        """
        <style>
        .topbar {padding: 0.5rem 0; border-bottom: 1px solid #e5e5e5;}
        .pill {padding: 0.25rem 0.75rem; border-radius: 12px; background: #f5f5f5; margin-right: 0.5rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_logo, col_mode, col_controls = st.columns([1.2, 2.6, 2.2])
    with col_logo:
        st.markdown("### 📖 AutoWriter Studio")
        st.caption("写作 IDE · 深色模式友好 · 键盘快捷键支持")

    with col_mode:
        mode = st.radio(
            "当前模式",
            options=[
                "世界观模式",
                "角色模式",
                "大纲模式",
                "写作模式",
                "审稿 / 质量检查模式",
            ],
            horizontal=True,
        )

    with col_controls:
        st.selectbox("AI 模型", options=["GPT-5.x (质量优先)", "速度优先", "通用"], index=0)
        st.selectbox("作者偏好", options=["爽文风格 A", "推理风格 B", "自定义"], index=0)
        st.selectbox("主题", options=["浅色", "深色"], index=1)

    return {"mode": mode}


def render_project_switcher(projects: List[Dict[str, Any]]) -> Optional[int]:
    if not projects:
        st.info("暂无作品，请先在侧栏创建新项目。")
        return None

    proj_options = {f"{p['name']} (#{p['id']})": p["id"] for p in projects}
    selected_project_id = st.session_state.get("selected_project_id")
    index = 0
    if selected_project_id and selected_project_id in proj_options.values():
        index = list(proj_options.values()).index(selected_project_id)
    label = st.selectbox("当前作品", options=list(proj_options.keys()), index=index)
    st.session_state["selected_project_id"] = proj_options[label]
    return proj_options[label]


def render_project_tree_sidebar(projects: List[Dict[str, Any]], chapter_list: List[Dict[str, Any]]) -> None:
    st.sidebar.header("工程树")
    st.sidebar.caption("快速定位世界观 / 角色 / 大纲 / 写作")

    if projects:
        for proj in projects:
            with st.sidebar.expander(f"📁 {proj['name']} (#{proj['id']})", expanded=proj["id"] == st.session_state.get("selected_project_id")):
                st.markdown("**项目概览**")
                st.caption(proj.get("description") or "")
                st.markdown("**模块**")
                st.write("🌍 世界观")
                st.write("👤 角色")
                st.write("📜 大纲")
                st.write("✍️ 章节写作")
                st.write("🧩 伏笔 & 线索")
                st.write("🕒 版本 & 历史")

    st.sidebar.markdown("---")
    st.sidebar.subheader("章节树")
    if chapter_list:
        chapter_options = {f"{c['index']+1}. {c['title']} (#{c['id']})": c["id"] for c in chapter_list}
        selected_label = st.sidebar.radio("章节列表", options=list(chapter_options.keys()))
        st.session_state["selected_chapter_id"] = chapter_options[selected_label]
    else:
        st.sidebar.caption("暂无章节")


# ---------------- Feature Panels -----------------


def chapter_progress(content: str, expected: int = 2000) -> None:
    word_count = len(content or "")
    pct = min(int((word_count / expected) * 100), 120)
    col_goal, col_progress, col_pace = st.columns(3)
    col_goal.metric("本章目标", "推进主线 + 埋伏笔", "AI 动态建议")
    col_progress.metric("进度", f"{word_count} / {expected} 字", f"{pct}%")
    col_pace.metric("节奏", "正常", "实时评估")


def render_context_panel(current_project_id: int, chapter_data: Dict[str, Any]) -> None:
    st.markdown("#### 📌 上下文 / 资料")
    st.markdown("**本章大纲**")
    st.write(chapter_data.get("summary") or "暂无纲要")

    st.markdown("**相关角色**")
    try:
        chars = list_characters(current_project_id)
        for ch in chars[:5]:
            st.write(f"- {ch.get('name')}：{(ch.get('description') or '')[:60]}")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"角色加载失败：{exc}")

    st.markdown("**世界观条目**")
    try:
        elements = list_world_elements(current_project_id)
        for item in elements[:5]:
            st.write(f"- [{item.get('type')}] {item.get('title')}")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"世界观加载失败：{exc}")

    st.markdown("**伏笔提示**")
    try:
        clues = list_clues(current_project_id, status_filter="unresolved")
        for clue in clues[:5]:
            st.write(f"- {clue.get('description')[:80]}")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"伏笔加载失败：{exc}")

    st.markdown("**历史版本**")
    st.caption("版本快照即将接入，当前暂存于后端。")


def render_ai_assistant(chapter_id: int, chapter_content: str) -> None:
    st.markdown("#### 🤖 本章助手")
    st.markdown("AI Writer Loop")
    steps = [
        "生成本章骨架",
        "三版本初稿",
        "人工修改",
        "风格统一 & 润色",
    ]
    for i, step in enumerate(steps, start=1):
        st.markdown(f"- ✅ Step {i}：{step}")

    ai_prompt = st.text_area("AI 提示词", value="继续写下去，保持节奏紧凑", height=120)
    col1, col2, col3 = st.columns(3)
    placeholder = st.empty()

    def run_ai(action: str) -> None:
        try:
            generated = chapter_ai_action(chapter_id, action, ai_prompt)
            st.session_state[f"chapter_content_{chapter_id}"] = (
                generated if st.session_state.get("ai_replace", False) else f"{chapter_content}\n\n{generated}".strip()
            )
            placeholder.success("AI 生成完成，已写入正文区域。")
        except Exception as exc:  # noqa: BLE001
            placeholder.error(f"AI 调用失败: {exc}")

    with col1:
        if st.button("生成骨架"):
            run_ai("draft")
    with col2:
        if st.button("三版本初稿"):
            run_ai("expand")
    with col3:
        if st.button("风格统一"):
            run_ai("rewrite")

    st.checkbox("生成结果替换正文", value=False, key="ai_replace")

    st.markdown("---")
    st.markdown("#### 💬 对话模式")
    chat_prompt = st.text_area("快速对话", value="帮我想 3 个反转点", height=80)
    if st.button("发送对话"):
        try:
            reply = ai_generate(chat_prompt, mode="chat")
            st.session_state["chat_reply"] = reply
        except Exception as exc:  # noqa: BLE001
            st.error(f"对话失败: {exc}")
    if st.session_state.get("chat_reply"):
        st.info(st.session_state["chat_reply"])

    st.markdown("---")
    st.markdown("#### 🩺 诊断 & 建议")
    if st.button("运行质量分析"):
        try:
            analysis = analyze_chapter_api(chapter_id)
            st.session_state[f"analysis_{chapter_id}"] = analysis
            st.success("分析完成")
        except Exception as exc:  # noqa: BLE001
            st.error(f"分析失败: {exc}")

    if st.session_state.get(f"analysis_{chapter_id}"):
        st.json(st.session_state[f"analysis_{chapter_id}"])

    st.markdown("---")
    st.markdown("#### 📚 备选片段库")
    st.caption("保留未采用的桥段，便于回填")
    st.text_area("片段存档", key=f"stash_{chapter_id}", height=160)


def render_writing_mode(current_project_id: int, chapter_id: Optional[int]) -> None:
    if not current_project_id or not chapter_id:
        st.info("请选择作品与章节后进入写作模式。")
        return

    try:
        chapter_data = load_chapter(chapter_id)
    except Exception as exc:  # noqa: BLE001
        st.error(f"加载章节失败: {exc}")
        return

    st.markdown("### ✍️ 章节写作工作台 (Chapter Studio)")
    chapter_progress(chapter_data.get("content") or "")

    col_context, col_editor, col_ai = st.columns([1.2, 2.4, 1.4], gap="large")

    with col_context:
        render_context_panel(current_project_id, chapter_data)

    with col_editor:
        st.markdown("#### 正文编辑区")
        title = st.text_input("标题", value=chapter_data.get("title", ""))
        summary = st.text_area("摘要", value=chapter_data.get("summary") or "", height=100)
        content_key = f"chapter_content_{chapter_id}"
        content = st.text_area(
            "正文 (Markdown)",
            value=st.session_state.get(content_key, chapter_data.get("content") or ""),
            height=420,
            key=content_key,
        )

        col_tools = st.columns(3)
        with col_tools[0]:
            if st.button("✨ 一键润色"):
                st.session_state[content_key] = f"【润色草案】\n{content}"
        with col_tools[1]:
            if st.button("➕ 续写本段"):
                st.session_state[content_key] = f"{content}\n\n[续写占位]"
        with col_tools[2]:
            if st.button("🎭 换情绪版本"):
                st.session_state[content_key] = f"{content}\n\n[情绪版草稿]"

        col_save = st.columns([1, 1])
        with col_save[0]:
            if st.button("保存章节"):
                try:
                    save_chapter(
                        chapter_id,
                        title=title,
                        summary=summary,
                        content=st.session_state.get(content_key, content),
                    )
                    st.success("章节已保存")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"保存失败: {exc}")
        with col_save[1]:
            if st.button("分析节奏"):
                try:
                    analysis = analyze_chapter_api(chapter_id)
                    st.session_state[f"analysis_{chapter_id}"] = analysis
                    st.success("节奏图已更新")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"分析失败: {exc}")

    with col_ai:
        render_ai_assistant(chapter_id, st.session_state.get(content_key, chapter_data.get("content") or ""))


# ---------------- Other Modes -----------------


def render_world_mode(current_project_id: int) -> None:
    st.markdown("### 🌍 世界观工作台")
    if not current_project_id:
        st.info("请选择作品以管理世界观")
        return

    col_tree, col_detail, col_ai = st.columns([1.2, 1.8, 1.2], gap="large")
    with col_tree:
        st.markdown("#### 结构树")
        try:
            elements = list_world_elements(current_project_id)
        except Exception as exc:  # noqa: BLE001
            st.error(f"加载失败: {exc}")
            elements = []
        for el in elements:
            st.write(f"- [{el.get('type')}] {el.get('title')} (#{el.get('id')})")

    with col_detail:
        st.markdown("#### 条目详情 / 新建")
        with st.form("create_world_element_form"):
            we_type = st.text_input("类型", key="we_type_new")
            we_title = st.text_input("标题", key="we_title_new")
            we_content = st.text_area("内容", height=140, key="we_content_new")
            if st.form_submit_button("创建世界观条目"):
                try:
                    create_world_element(current_project_id, {"type": we_type, "title": we_title, "content": we_content})
                    st.success("已创建世界观条目")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"创建失败: {exc}")

    with col_ai:
        st.markdown("#### AI 世界观助手")
        prompt = st.text_area("提示", value="根据世界观生成 10 个地名", height=120)
        if st.button("生成建议"):
            try:
                result = ai_generate(prompt, mode="world")
                st.session_state["world_ai"] = result
            except Exception as exc:  # noqa: BLE001
                st.error(f"生成失败: {exc}")
        if st.session_state.get("world_ai"):
            st.info(st.session_state["world_ai"])


def render_character_mode(current_project_id: int) -> None:
    st.markdown("### 👤 角色管理")
    if not current_project_id:
        st.info("请选择作品以管理角色")
        return

    try:
        characters = list_characters(current_project_id)
    except Exception as exc:  # noqa: BLE001
        st.error(f"加载角色失败: {exc}")
        characters = []

    cols = st.columns(3)
    for idx, ch in enumerate(characters):
        with cols[idx % 3]:
            st.markdown(f"**{ch.get('name')}** · {ch.get('role') or ''}")
            st.caption(ch.get("description") or "")
            st.caption(f"状态：{ch.get('arc') or '未设置'}")

    st.markdown("---")
    st.markdown("#### 编辑 / 新建角色")
    with st.form("character_edit_form"):
        ch_name = st.text_input("姓名")
        ch_role = st.text_input("角色定位")
        ch_desc = st.text_area("设定", height=120)
        ch_arc = st.text_area("成长路线", height=80)
        if st.form_submit_button("保存角色"):
            try:
                create_character(current_project_id, {"name": ch_name, "role": ch_role, "description": ch_desc, "arc": ch_arc})
                st.success("角色已保存")
            except Exception as exc:  # noqa: BLE001
                st.error(f"保存失败: {exc}")

    st.markdown("#### AI 人物检测")
    ai_prompt = st.text_area("提示", value="检查此角色是否人格不一致", height=80)
    if st.button("运行检测"):
        try:
            result = ai_generate(ai_prompt, mode="character_check")
            st.session_state["character_ai"] = result
        except Exception as exc:  # noqa: BLE001
            st.error(f"AI 失败: {exc}")
    if st.session_state.get("character_ai"):
        st.info(st.session_state["character_ai"])


def render_outline_mode(current_project_id: int, chapter_list: List[Dict[str, Any]]) -> None:
    st.markdown("### 📜 大纲视图")
    if not current_project_id:
        st.info("请选择作品以查看大纲")
        return

    col_tree, col_detail, col_ai = st.columns([1.2, 1.8, 1.2], gap="large")
    with col_tree:
        st.markdown("#### 卷/篇/章")
        if chapter_list:
            for c in chapter_list:
                st.write(f"- 第 {c['index'] + 1} 章 · {c['title']} ({'已完成' if c.get('content') else '草稿'})")
        else:
            st.caption("暂无章节")

    with col_detail:
        st.markdown("#### 大纲详情")
        st.text_area("本卷目标 / 冲突结构", height=180, key="outline_detail")

    with col_ai:
        st.markdown("#### AI 排序建议")
        prompt = st.text_area("提示", value="帮我重排最近几章的顺序以增强节奏", height=120)
        if st.button("生成大纲建议"):
            try:
                suggestion = ai_generate(prompt, mode="outline")
                st.session_state["outline_ai"] = suggestion
            except Exception as exc:  # noqa: BLE001
                st.error(f"生成失败: {exc}")
        if st.session_state.get("outline_ai"):
            st.info(st.session_state["outline_ai"])


def render_quality_mode(current_project_id: int, chapter_id: Optional[int]) -> None:
    st.markdown("### 🧪 质量检查模式")
    if not current_project_id or not chapter_id:
        st.info("请选择作品与章节后运行质量检查")
        return

    if st.button("生成质量报告"):
        try:
            result = analyze_chapter_api(chapter_id)
            st.session_state["quality_report"] = result
        except Exception as exc:  # noqa: BLE001
            st.error(f"质量分析失败: {exc}")

    if st.session_state.get("quality_report"):
        st.json(st.session_state["quality_report"])
    else:
        st.caption("将生成角色 OOC、世界观冲突、重复桥段、节奏分析等报告。")


# ---------------- Main -----------------


def main() -> None:
    st.title("AI 写作器")
    st.caption("左侧工程树快速导航，右侧是核心工作台。")

    ui_state = render_top_bar()

    # Sidebar: project creation
    st.sidebar.subheader("新建作品")
    with st.sidebar.form("new_project_form"):
        proj_name = st.text_input("作品名称")
        proj_desc = st.text_area("简介", height=80)
        if st.form_submit_button("创建作品"):
            try:
                proj = create_project(proj_name, proj_desc)
                st.session_state["selected_project_id"] = proj["id"]
                st.sidebar.success("作品已创建")
            except Exception as exc:  # noqa: BLE001
                st.sidebar.error(f"创建失败: {exc}")

    # Load projects and chapters
    try:
        projects = load_projects()
    except Exception as exc:  # noqa: BLE001
        st.error(f"加载作品失败: {exc}")
        projects = []

    current_project_id = render_project_switcher(projects)

    chapter_list: List[Dict[str, Any]] = []
    if current_project_id:
        try:
            chapter_list = load_chapters(current_project_id)
            st.session_state["chapter_list_for_tabs"] = chapter_list
        except Exception as exc:  # noqa: BLE001
            st.error(f"加载章节失败: {exc}")
            chapter_list = []

    render_project_tree_sidebar(projects, chapter_list)

    st.markdown("---")

    if current_project_id:
        with st.expander("快速新建章节", expanded=False):
            with st.form("new_chapter_form"):
                new_chapter_title = st.text_input("章节标题")
                new_chapter_summary = st.text_area("章节摘要", height=80)
                if st.form_submit_button("创建章节"):
                    try:
                        chap = create_chapter(current_project_id, new_chapter_title, new_chapter_summary)
                        st.session_state["selected_chapter_id"] = chap["id"]
                        st.success("章节已创建")
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"创建失败: {exc}")

    current_chapter_id = st.session_state.get("selected_chapter_id")

    if ui_state["mode"] == "写作模式":
        render_writing_mode(current_project_id, current_chapter_id)
    elif ui_state["mode"] == "世界观模式":
        render_world_mode(current_project_id)
    elif ui_state["mode"] == "角色模式":
        render_character_mode(current_project_id)
    elif ui_state["mode"] == "大纲模式":
        render_outline_mode(current_project_id, chapter_list)
    else:
        render_quality_mode(current_project_id, current_chapter_id)


if __name__ == "__main__":
    main()
