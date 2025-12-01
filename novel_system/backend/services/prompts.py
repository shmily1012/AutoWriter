"""Reusable prompt templates."""

CHAPTER_ANALYSIS_PROMPT = """请分析以下章节文本，输出 JSON，格式为：
{{
  "characters_appeared": ["角色名1", "角色名2"],
  "world_facts": ["设定条目1", "设定条目2"],
  "possible_clues": ["伏笔描述1", "伏笔描述2"]
}}
仅返回 JSON，不要其他解释。characters_appeared 必须是名字列表；world_facts 以一句话描述；possible_clues 用一句话描述潜在伏笔。

已知角色：
{character_brief}

已知世界观：
{world_brief}

章节内容：
{chapter_content}
"""

PLOT_SUGGEST_PROMPT = """当前章节内容：
{chapter_content}

请给出 3 条下一步剧情/改进建议，使用简短要点。"""

WORLD_SKELETON_PROMPT = """题材：{genre}
设想：{idea}
请用列表列出世界观骨架，包含：世界背景、主要势力、关键城市或地点、科技/修炼体系等，每项一条。"""

CHARACTER_EXTRACT_PROMPT = """从以下章节内容中提取出现的角色名字，按行输出，每行一个名字，不要附加说明。

章节内容：
{chapter_content}
"""

__all__ = [
    "CHAPTER_ANALYSIS_PROMPT",
    "PLOT_SUGGEST_PROMPT",
    "WORLD_SKELETON_PROMPT",
    "CHARACTER_EXTRACT_PROMPT",
]
