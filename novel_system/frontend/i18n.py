from dataclasses import dataclass
from typing import Any, Dict

SUPPORTED_LANGS = ("en", "zh")

STAGE_LABELS: Dict[str, Dict[str, str]] = {
    "Plan": {"en": "Plan", "zh": "规划"},
    "Draft": {"en": "Draft", "zh": "起草"},
    "Revise": {"en": "Revise", "zh": "修订"},
    "Library": {"en": "Library", "zh": "资料库"},
}

OPTION_TRANSLATIONS: Dict[str, Dict[str, Dict[str, str]]] = {
    "persona": {
        "Neutral": {"en": "Neutral", "zh": "中性"},
        "Cinematic": {"en": "Cinematic", "zh": "电影感"},
        "Wry narrator": {"en": "Wry narrator", "zh": "冷幽默旁白"},
    },
    "tone": {
        "Balanced": {"en": "Balanced", "zh": "平衡"},
        "Darker": {"en": "Darker", "zh": "更阴郁"},
        "Lighter": {"en": "Lighter", "zh": "更轻快"},
    },
    "status": {
        "Draft": {"en": "Draft", "zh": "草稿"},
        "Pending": {"en": "Pending", "zh": "待开始"},
    },
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "app_title": {"en": "AI Writing Command Center", "zh": "AI写作指挥中心"},
    "app_subtitle": {
        "en": "Linear Plan → Draft → Revise flow with contextual AI support.",
        "zh": "线性“规划→起草→修订”流程，配合上下文 AI 辅助。",
    },
    "language_toggle_label": {"en": "中文 / EN", "zh": "中文 / EN"},
    "language_toggle_help": {"en": "Switch between English and Chinese UI", "zh": "在中英文界面间切换"},
    "stage_label": {"en": "Stage", "zh": "阶段"},
    "project_label": {"en": "Project", "zh": "项目"},
    "chapter_label": {"en": "Chapter", "zh": "章节"},
    "create_project_prompt": {"en": "Create a project to start.", "zh": "创建一个项目以开始。"},
    "no_chapters_plan": {"en": "No chapters yet. Add one in Plan.", "zh": "暂未创建章节，请在“规划”中添加。"},
    "ai_model_label": {"en": "AI model", "zh": "AI 模型"},
    "author_voice_label": {"en": "Author voice", "zh": "作者风格"},
    "tone_label": {"en": "Tone guide", "zh": "语气指引"},
    "sidebar_create_project": {"en": "Create project", "zh": "创建项目"},
    "sidebar_project_name": {"en": "Project name", "zh": "项目名称"},
    "sidebar_description": {"en": "Description", "zh": "描述"},
    "sidebar_create_project_button": {"en": "Create project", "zh": "创建项目"},
    "sidebar_project_created": {"en": "Project created.", "zh": "项目已创建。"},
    "sidebar_create_failed": {"en": "Create failed: {error}", "zh": "创建失败：{error}"},
    "load_projects_error": {"en": "Unable to load projects: {error}", "zh": "项目加载失败：{error}"},
    "load_chapters_error": {"en": "Unable to load chapters: {error}", "zh": "章节加载失败：{error}"},
    "heading_plan": {"en": "Plan", "zh": "规划"},
    "heading_draft": {"en": "Draft", "zh": "起草"},
    "heading_revise": {"en": "Revise", "zh": "修订"},
    "heading_library": {"en": "Library", "zh": "资料库"},
    "info_select_project_plan": {"en": "Select or create a project to start planning.", "zh": "请选择或创建项目后再规划。"},
    "outline_board": {"en": "Outline board", "zh": "大纲面板"},
    "beats_notes": {"en": "Beats and notes", "zh": "情节点与笔记"},
    "send_beats_label": {"en": "Send beats to chapter summary", "zh": "将这些情节发送到章节摘要"},
    "send_to_draft": {"en": "Send to Draft", "zh": "发送到起草"},
    "summary_sent_success": {"en": "Summary sent to Draft.", "zh": "摘要已发送到起草。"},
    "send_failed": {"en": "Send failed: {error}", "zh": "发送失败：{error}"},
    "no_chapters_plan_below": {
        "en": "No chapters yet. Add one below to start drafting.",
        "zh": "还没有章节，请先在下方创建再开始起草。",
    },
    "new_chapter_title": {"en": "New chapter title", "zh": "新章节标题"},
    "short_summary": {"en": "Short summary", "zh": "简要摘要"},
    "create_chapter_button": {"en": "Create chapter", "zh": "创建章节"},
    "chapter_created_prompt": {"en": "Chapter created. Refresh to load it into the list.", "zh": "章节已创建，请刷新载入列表。"},
    "create_failed": {"en": "Create failed: {error}", "zh": "创建失败：{error}"},
    "ai_outline_coach": {"en": "AI outline coach", "zh": "AI 大纲助理"},
    "prompt_label": {"en": "Prompt", "zh": "提示词"},
    "default_outline_prompt": {
        "en": "Draft 5-7 beats that escalate conflict and end on a hook. Keep POV consistent.",
        "zh": "拟定 5-7 条推进冲突并以悬念结尾的情节点，保持 POV 一致。",
    },
    "replace_outline_checkbox": {"en": "Replace outline with result", "zh": "用结果替换当前大纲"},
    "propose_beats_button": {"en": "Propose next beats", "zh": "生成下一组情节点"},
    "outline_updated": {"en": "Outline updated.", "zh": "大纲已更新。"},
    "ai_failed": {"en": "AI failed: {error}", "zh": "AI 生成失败：{error}"},
    "info_pick_project_chapter": {"en": "Pick a project and chapter to open the Draft workspace.", "zh": "请选择项目和章节以打开起草工作区。"},
    "load_chapter_error": {"en": "Unable to load chapter: {error}", "zh": "章节加载失败：{error}"},
    "context_rail": {"en": "Context rail", "zh": "上下文栏"},
    "summary_label": {"en": "Summary", "zh": "摘要"},
    "no_summary": {"en": "No summary yet.", "zh": "暂无摘要。"},
    "cast_on_stage": {"en": "Cast on stage", "zh": "当前角色"},
    "insert": {"en": "Insert", "zh": "插入"},
    "unknown": {"en": "Unknown", "zh": "未知"},
    "world_notes": {"en": "World notes", "zh": "世界观"},
    "item_label": {"en": "item", "zh": "条目"},
    "foreshadow": {"en": "Foreshadow", "zh": "伏笔"},
    "chapter_editor": {"en": "Chapter editor", "zh": "章节编辑器"},
    "title_label": {"en": "Title", "zh": "标题"},
    "beat_summary": {"en": "Beat summary", "zh": "情节概要"},
    "chapter_markdown": {"en": "Chapter markdown", "zh": "章节正文（Markdown）"},
    "tag_turning_point": {"en": "Tag turning point", "zh": "标记转折点"},
    "turning_point_marker": {"en": "[TURNING POINT]", "zh": "[转折点]"},
    "insert_beat_checklist": {"en": "Insert beat checklist", "zh": "插入情节核对清单"},
    "mark_for_polish": {"en": "Mark for polish", "zh": "标记为需润色"},
    "checklist_setup": {"en": "Setup", "zh": "铺垫"},
    "checklist_tension": {"en": "Tension", "zh": "张力"},
    "checklist_payoff": {"en": "Payoff", "zh": "回报"},
    "polish_marker": {"en": "[POLISH ME]", "zh": "[需要润色]"},
    "save_chapter_button": {"en": "Save chapter", "zh": "保存章节"},
    "chapter_saved": {"en": "Chapter saved.", "zh": "章节已保存。"},
    "save_failed": {"en": "Save failed: {error}", "zh": "保存失败：{error}"},
    "run_diagnostics_button": {"en": "Run diagnostics", "zh": "运行诊断"},
    "analysis_ready": {"en": "Analysis ready in Revise.", "zh": "分析已准备好，可在修订查看。"},
    "diagnostics_failed": {"en": "Diagnostics failed: {error}", "zh": "诊断失败：{error}"},
    "writer_loop": {"en": "Writer Loop", "zh": "写作循环"},
    "working_prompt": {"en": "Working prompt", "zh": "工作提示词"},
    "default_working_prompt": {
        "en": "Keep POV consistent, honor tone, surface tension between leads.",
        "zh": "保持 POV 一致，遵循语气，突出主角之间的张力。",
    },
    "replace_editor_text": {"en": "Replace editor text", "zh": "用结果替换编辑器内容"},
    "skeleton_button": {"en": "Skeleton", "zh": "骨架草稿"},
    "rewrite_tone_button": {"en": "Rewrite tone", "zh": "调整语气"},
    "expand_scene_button": {"en": "Expand scene", "zh": "扩展场景"},
    "polish_style_button": {"en": "Polish style", "zh": "润色风格"},
    "ai_action_success": {"en": "{label} ready and sent to editor.", "zh": "{label} 已生成并发送到编辑器。"},
    "ai_action_failed": {"en": "{label} failed: {error}", "zh": "{label} 失败：{error}"},
    "ai_history": {"en": "AI history", "zh": "AI 历史"},
    "ai_history_item": {"en": "{label} #{index}", "zh": "{label} #{index}"},
    "replace": {"en": "Replace", "zh": "替换"},
    "history_empty": {"en": "Run AI actions to see history here.", "zh": "运行 AI 动作后会显示历史记录。"},
    "info_pick_project_revise": {"en": "Pick a project and chapter to revise.", "zh": "请选择项目和章节以开始修订。"},
    "quality_checks": {"en": "Quality checks", "zh": "质量检查"},
    "run_quality_report": {"en": "Run quality report", "zh": "运行质量报告"},
    "report_failed": {"en": "Report failed: {error}", "zh": "报告失败：{error}"},
    "report_caption": {"en": "Run a report to see pacing, OOC, and duplicate beats.", "zh": "运行报告以查看节奏、人物 OOC 和重复情节。"},
    "stash": {"en": "Stash", "zh": "草稿区"},
    "targeted_rewrites": {"en": "Targeted rewrites", "zh": "定向改写"},
    "text_to_rewrite": {"en": "Text to rewrite", "zh": "待改写文本"},
    "rewrite_instruction": {"en": "Rewrite instruction", "zh": "改写说明"},
    "default_rewrite_instruction": {"en": "Tighten prose, keep POV, raise tension.", "zh": "收紧文字，保持 POV，提高张力。"},
    "rewrite_selection": {"en": "Rewrite selection", "zh": "改写所选"},
    "rewrite_added_history": {"en": "Rewrite added to AI history.", "zh": "改写结果已加入 AI 历史。"},
    "rewrite_failed": {"en": "Rewrite failed: {error}", "zh": "改写失败：{error}"},
    "targeted_polish": {"en": "Targeted polish", "zh": "定向润色"},
    "polish_prompt": {"en": "Polish prompt", "zh": "润色提示词"},
    "default_polish_prompt": {"en": "Polish the latest draft for rhythm and clarity.", "zh": "润色最新草稿的节奏和清晰度。"},
    "polish_passage": {"en": "Polish passage", "zh": "润色段落"},
    "polish_added_history": {"en": "Polish added to AI history.", "zh": "润色结果已加入 AI 历史。"},
    "polish_failed": {"en": "Polish failed: {error}", "zh": "润色失败：{error}"},
    "issue_label": {"en": "Issue {index}", "zh": "问题 {index}"},
    "projects_heading": {"en": "Projects", "zh": "项目列表"},
    "no_projects": {"en": "No projects yet.", "zh": "暂无项目。"},
    "chapters_heading": {"en": "Chapters", "zh": "章节列表"},
    "no_description": {"en": "No description yet.", "zh": "暂无描述。"},
    "no_chapters_library": {"en": "No chapters yet. Add one from Plan.", "zh": "还没有章节，请在“规划”中添加。"},
    "select_project_to_see_chapters": {"en": "Select a project to see its chapters.", "zh": "选择一个项目以查看其章节。"},
    "target_label": {"en": "Target", "zh": "目标"},
    "words_unit": {"en": "words", "zh": "字"},
    "steady_pace_delta": {"en": "+ steady pace", "zh": "+ 稳定节奏"},
    "current_label": {"en": "Current", "zh": "当前"},
    "goal_percent": {"en": "{percent}% of goal", "zh": "已完成 {percent}%"},
    "rhythm_label": {"en": "Rhythm", "zh": "节奏"},
    "on_track": {"en": "On track", "zh": "进度正常"},
    "warm_up": {"en": "Warm-up", "zh": "热身中"},
    "live_delta": {"en": "Live", "zh": "实时"},
}


@dataclass(frozen=True)
class I18n:
    lang: str = "en"

    def __post_init__(self) -> None:
        object.__setattr__(self, "lang", self.lang if self.lang in SUPPORTED_LANGS else "en")

    def t(self, key: str, **kwargs: Any) -> str:
        template = TRANSLATIONS.get(key, {}).get(self.lang) or TRANSLATIONS.get(key, {}).get("en") or key
        try:
            return template.format(**kwargs)
        except Exception:
            return template

    def stage_label(self, stage_key: str) -> str:
        return STAGE_LABELS.get(stage_key, {}).get(self.lang) or stage_key

    def option(self, category: str, value: str) -> str:
        return OPTION_TRANSLATIONS.get(category, {}).get(value, {}).get(self.lang) or value

    def status(self, value: str) -> str:
        return OPTION_TRANSLATIONS.get("status", {}).get(value, {}).get(self.lang) or value
