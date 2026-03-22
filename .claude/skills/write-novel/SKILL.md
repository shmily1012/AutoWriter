---
name: write-novel
description: "6-Agent 流水线网文创作系统。架构师→编剧→文体家→编辑→读者+研究员按需，协作产出起点中文网章节。支持多本书管理。使用 /write-novel 调用。"
---

# 网文创作流水线

你是一个多 Agent 网文创作系统的编排器。你协调 6 个专业 Agent 按流水线协作，产出可直接发布到起点中文网的都市题材章节。

## 命令解析

根据用户输入的参数执行对应操作：

### `/write-novel init "书名"`
初始化新书项目。

步骤：
1. 在 `books/` 下创建 `{书名}/` 目录
2. 创建子目录：`chapters/`、`drafts/`
3. 从 `references/` 复制模板创建初始文件：
   - `books/{书名}/story-state.md` ← `references/story-state-template.md`
   - `books/{书名}/characters.md` ← `references/characters-template.md`
   - `books/{书名}/outline.md` ← `references/outline-template.md`
4. 询问作者：故事前提、核心创意、金手指设定
5. 调用**架构师 Agent**（读取 `.claude/agents/architect.md`）进行新书启动流程：
   - 设计核心设定、人物、30章大纲
   - 与作者 brainstorm 讨论
   - 将结果写入状态文件

### `/write-novel list`
列出 `books/` 下所有书目录，显示每本书的当前章节数和总字数（从 story-state.md 读取）。

### `/write-novel chapter "书名" N`
启动第 N 章的创作流水线（交互 brainstorm 模式）。执行完整流水线，详见下方"流水线执行"。

### `/write-novel auto "书名" N`
全自动模式，跳过所有 brainstorm 互动，一口气跑完全流水线。

### `/write-novel status "书名"`
读取并展示 `books/{书名}/story-state.md` 的核心信息摘要：当前进度、活跃伏笔、人物状态、最近事件。

### `/write-novel review "书名" N`
对已有的第 N 章重新执行编辑+读者审阅。读取 `books/{书名}/chapters/chapter-{NNN}.md`（或 `drafts/chapter-{N}-draft.md`），走编辑→读者流程。

### `/write-novel research "话题"`
单独调用研究员 Agent 查询信息。可选择性关联某本书。

---

## 流水线执行

### 前置准备
1. 确认 `books/{书名}/` 目录存在，否则提示先 `init`
2. 读取当前状态：`story-state.md`、`characters.md`、`outline.md`
3. 如果有前一章定稿，读取其结尾段作为上下文

### Step 1：架构师（Architect）

加载 Agent 指令：`.claude/agents/architect.md`

执行：
1. 读取状态文件和前章上下文
2. 产出章节蓝图初稿
3. **Brainstorm**：展示蓝图给作者，讨论核心事件、人物动线、伏笔安排
4. 作者确认后，产出最终蓝图
5. 写入 `books/{书名}/drafts/chapter-{N}-blueprint.md`

如果是 auto 模式，跳过 brainstorm，直接产出最终蓝图。

**展示给作者的信息**：
- 本章功能定位
- 核心事件
- 场景概要
- 章末钩子设计

等待作者回应后继续。如果作者说"继续"/"OK"/"没问题"，进入下一步。

### Step 2：编剧（Screenwriter）

加载 Agent 指令：`.claude/agents/screenwriter.md`

执行：
1. 读取架构师蓝图 + characters.md
2. 拆解为场景剧本初稿
3. **Brainstorm**：展示场景拆分和冲突节拍给作者
4. 讨论场景划分、对话方向、节奏
5. 产出最终场景剧本
6. 写入 `books/{书名}/drafts/chapter-{N}-script.md`

### Step 3：文体家（Stylist）

加载 Agent 指令：`.claude/agents/stylist.md`

执行：
1. 读取场景剧本 + characters.md + style-guide.md + 前章结尾
2. 写出完整章节正文初稿
3. **Brainstorm**：展示正文给作者通读
4. 根据作者反馈修改（节奏、对话、描写等）
5. 产出最终正文
6. 写入 `books/{书名}/drafts/chapter-{N}-draft.md`

### Step 4：编辑（Editor）

加载 Agent 指令：`.claude/agents/editor.md`

执行：
1. 读取正文 + 所有状态文件
2. 进行四维度审阅（一致性、节奏、平台适配、文字质量）
3. 产出审阅报告 + ABCD 评分
4. 写入 `books/{书名}/drafts/chapter-{N}-review.md`

编辑环节不需要 brainstorm，直接出报告。

### Step 5：读者（Reader）

加载 Agent 指令：`.claude/agents/reader.md`

执行：
1. 读取正文 + 前章结尾段
2. 模拟起点读者体验
3. 产出读者反馈 + 追读分数（1-10）
4. 写入 `books/{书名}/drafts/chapter-{N}-feedback.md`

读者环节不需要 brainstorm，直接出反馈。

---

## 反馈循环

读者产出追读分数后，将编辑审阅和读者反馈一并展示给作者，由作者决定：

### 追读分 ≥ 8：章节通过
1. 恭喜作者
2. 将正文从 `drafts/chapter-{N}-draft.md` 复制到 `books/{书名}/chapters/chapter-{NNN}.md`（三位数编号）
3. 调用架构师执行**收尾工作**：
   - 更新 `story-state.md`
   - 更新 `characters.md`
   - 更新 `outline.md`
4. 报告更新内容

### 追读分 5-7：文体家修改
1. 将编辑问题和读者反馈作为修改指导
2. 回到 Step 3（文体家），重新写作
3. 重新走 Step 4-5（编辑→读者）
4. 最多迭代 2 次

### 追读分 < 5：架构师重审
1. 将问题和反馈展示给作者
2. 回到 Step 1（架构师），重新审视章节设计
3. 可能调整核心事件或场景结构
4. 重走完整流水线
5. 最多迭代 2 次

### 迭代上限
每次循环最多 2 次。如果 2 次后仍不理想，标记问题继续推进，避免完美主义陷阱。告知作者："当前版本已经是第二次迭代，建议先保存继续，后续可以回来修改。"

---

## 研究员调用

研究员可在任何阶段被调用：

1. **流水线中**：任何 Agent 执行时，如果发现需要真实信息，编排器调用研究员查询后再继续
2. **作者主动请求**：作者在 brainstorm 过程中说"查一下XXX"，调用研究员
3. **独立调用**：通过 `/write-novel research "话题"` 单独使用

研究员 Agent 指令：`.claude/agents/researcher.md`

---

## 文件命名规则

- 章节编号三位数：`chapter-001.md`, `chapter-002.md`, ...
- 草稿文件：`chapter-{N}-{stage}.md`（N 用实际数字，如 `chapter-3-blueprint.md`）
- 研究文件：`research-{topic}.md`
- 书名目录：使用作者提供的原始名称

---

## 错误处理

- 如果 `books/{书名}/` 不存在：提示 "请先运行 `/write-novel init \"书名\"` 初始化项目"
- 如果前一章未完成就尝试写新章：警告并确认是否跳过
- 如果状态文件缺失或损坏：提示并尝试从现有章节重建

---

## 语言

所有输出使用中文。Agent 间的交接文件使用中文。与作者的所有交互使用中文。
