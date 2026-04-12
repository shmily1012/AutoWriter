# Repository Guidelines

## Project Overview
AutoWriter 是一个基于 Claude Code Skill 的工程化多 Agent 网文创作系统，融合了 [Superpowers](https://github.com/obra/superpowers) 软件工程工作流核心理念和 [Harness Engineering](https://mitchellh.com/writing/my-ai-adoption-journey) 方法论。无传统后端/前端，完全通过 Claude Code 对话驱动。

## Harness Engineering 架构

本项目引入了 5 个来自 harness engineering 社区的核心模式：

1. **Pipeline State 持久化** — 跨 session 断点续写（`pipeline-state.md`）
2. **自动化 Linting** — 约束 > 约定，lint 结果注入 agent context（`tools/lint-chapter.sh`）
3. **Generator/Evaluator 分离** — GAN 启发，编辑和读者作为独立 subagent 运行
4. **Initializer/Coding Agent 分离** — 首次启动生成精炼简报，后续 session 消费简报
5. **稳定接口/适配层分离** — Agent 定义拆为不随模型变的"合同"和模型特定的 workaround

详见各 Agent 定义中的"稳定接口"和"模型适配层"段落，以及 `references/model-adaptations.md`。

## Structure
- `.claude/skills/write-novel/` — 主编排 Skill
- `.claude/skills/*/` — Superpowers 工程化技能（TDD、调试、代码审查等，已适配为创作工作流）
- `.claude/agents/` — 8 个 Agent 定义（每个包含稳定接口 + 模型适配层）：
  - `architect.md` — 架构师：故事结构 + 读者期望规格生成
  - `screenwriter.md` — 编剧：场景剧本
  - `spec-reviewer.md` — 蓝图合规审查（新增，借鉴Superpowers两阶段Review）
  - `stylist.md` — 文体家：正文写作
  - `editor.md` — 编辑：六维度审阅（含蓝图合规+证据驱动验证）
  - `reader.md` — 读者：追读打分 + TDD规格验证
  - `researcher.md` — 研究员：按需调用
- `.claude/commands/` — Superpowers 命令（brainstorm, write-plan, execute-plan）
- `references/` — 模板文件（含新增的 reader-spec-template.md）
- `references/model-adaptations.md` — 模型适配层集中管理（模型升级时审查此文件）
- `tools/lint-chapter.sh` — 自动化章节 lint 脚本（Harness Linting Layer）
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
