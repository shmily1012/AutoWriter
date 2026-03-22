# Repository Guidelines

## Project Overview
AutoWriter 是一个基于 Claude Code Skill 的多 Agent 网文创作系统。无传统后端/前端，完全通过 Claude Code 对话驱动。

## Structure
- `.claude/skills/write-novel/` — 主编排 Skill
- `.claude/agents/` — 6 个 Agent 定义（architect, screenwriter, stylist, editor, reader, researcher）
- `references/` — 模板文件（状态、人物、大纲、蓝图、剧本、审阅、反馈、风格指南）
- `books/{书名}/` — 每本书的独立工作目录

## How It Works
1. 用户通过 `/write-novel` 命令触发 Skill
2. Skill 按流水线调度 Agent：架构师 → 编剧 → 文体家 → 编辑 → 读者
3. 每步支持作者 brainstorm 互动
4. 研究员可在任何阶段按需调用
5. 状态通过 markdown 文件持久化

## Conventions
- 所有状态文件使用中文
- Agent 定义文件使用中英混合（指令英文，示例中文）
- 章节文件命名：`chapter-001.md`, `chapter-002.md`, ...
- 草稿命名：`chapter-{N}-{stage}.md`（blueprint/script/draft/review/feedback）

## Testing
- 使用 `/write-novel init "测试"` 初始化测试项目
- 运行完整流水线验证各 Agent 产出格式
- 检查状态文件更新是否正确
