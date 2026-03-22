# Repository Guidelines

## Project Overview
AutoWriter 是一个基于 Claude Code Skill 的工程化多 Agent 网文创作系统，融合了 [Superpowers](https://github.com/obra/superpowers) 软件工程工作流的核心理念。无传统后端/前端，完全通过 Claude Code 对话驱动。

## Structure
- `.claude/skills/write-novel/` — 主编排 Skill
- `.claude/skills/*/` — Superpowers 工程化技能（TDD、调试、代码审查等，已适配为创作工作流）
- `.claude/agents/` — 7 个 Agent 定义：
  - `architect.md` — 架构师：故事结构 + 读者期望规格生成
  - `screenwriter.md` — 编剧：场景剧本
  - `spec-reviewer.md` — 蓝图合规审查（新增，借鉴Superpowers两阶段Review）
  - `stylist.md` — 文体家：正文写作
  - `editor.md` — 编辑：六维度审阅（含蓝图合规+证据驱动验证）
  - `reader.md` — 读者：追读打分 + TDD规格验证
  - `researcher.md` — 研究员：按需调用
- `.claude/commands/` — Superpowers 命令（brainstorm, write-plan, execute-plan）
- `references/` — 模板文件（含新增的 reader-spec-template.md）
- `books/{书名}/` — 每本书的独立工作目录

## How It Works（工程化增强版）
1. 用户通过 `/write-novel` 命令触发 Skill
2. 架构师产出蓝图 + **读者期望规格**（TDD类比：先写测试）
3. 编剧产出剧本 → **蓝图合规审查**（先验证"做的对不对"）
4. 文体家写正文 → 编辑**六维度审阅**（含证据驱动验证）
5. 读者**逐条验证读者期望规格**（TDD类比：运行测试）
6. 低分时触发**根因分析**（借鉴Superpowers系统化调试）
7. 3次迭代失败触发**熔断机制**（强制决策点）
8. 研究员可在任何阶段按需调用

## Superpowers 融合映射
| Superpowers 概念 | 创作系统等价物 |
|---|---|
| TDD | 读者期望规格（先定义成功标准再写正文） |
| Spec Compliance Review | 蓝图合规审查（剧本是否忠实执行蓝图） |
| Verification Before Completion | 证据驱动验证（每个判断都引用正文原文） |
| Systematic Debugging | 根因分析（低分时诊断问题出在哪个环节） |
| Circuit Breaker | 迭代熔断（3次失败后强制选择方向） |

## Conventions
- 所有状态文件使用中文
- Agent 定义文件使用中英混合（指令英文，示例中文）
- 章节文件命名：`chapter-001.md`, `chapter-002.md`, ...
- 草稿命名：`chapter-{N}-{stage}.md`（blueprint/script/draft/review/feedback/reader-spec/spec-review）

## Testing
- 使用 `/write-novel init "测试"` 初始化测试项目
- 运行完整流水线验证各 Agent 产出格式
- 检查状态文件更新是否正确
- 验证读者期望规格生成和验证流程
- 验证蓝图合规审查是否正确捕获偏差
