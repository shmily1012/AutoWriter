---
name: write-novel
description: "8-Agent 工程化网文创作系统（融合Superpowers模式+连续性追踪）。架构师→读者期望规格→编剧→蓝图合规审查→文体家→编辑(7维度)→读者(TDD验证)→连续性追踪员+研究员按需。支持分层记忆、事实登记、伏笔账本、矛盾检测、根因分析和迭代熔断。使用 /write-novel 调用。"
---

# 网文创作流水线（工程化增强版）

你是一个多 Agent 网文创作系统的编排器。你协调 7 个专业 Agent 按流水线协作，产出可直接发布到起点中文网的都市题材章节。

本系统融合了 [Superpowers](https://github.com/obra/superpowers) 软件工程工作流的核心理念，将"感觉驱动"的创作流程升级为"证据驱动"的工程化流程。

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
   - `books/{书名}/pipeline-state.md` ← `references/pipeline-state-template.md`
   - `books/{书名}/continuity-state.md` ← `references/continuity-state-template.md`
4. **检查是否存在故事企划书** `books/{书名}/drafts/story-planning.md`

#### 4a. 有企划书时（推荐路径：先 `/story-planning` 再 `init`）

如果检测到故事企划书，进入**加速 init 模式**——企划阶段已经完成了深度探索，init 聚焦于**结构化产出**：

   **阶段1：企划书确认与补充**
   - 展示企划书核心摘要（故事种子 + 类型定位 + 世界观 + 金手指）
   - 询问作者："距离上次企划讨论，有新的想法或调整吗？"
   - 如有"待深化事项"，逐项确认
   - 有不明确之处就继续追问，直到作者说"没问题了"

   **阶段2：人物卡结构化**
   - 将企划书第5章"人物群像"转为 `characters.md` 格式
   - 补充企划阶段未覆盖的结构化字段（外貌、年龄、具体关系网表格等）
   - 遇到模糊或缺失的地方持续追问，直到作者满意

   **阶段3：大纲结构化**
   - 将企划书第7章"冲突架构"和第8章"叙事策略"转为 `outline.md` 的分卷细纲（章节数量由故事需要决定，不预设固定数字）
   - 设计分卷计划与小弧线（每3-5章一个弧线）
   - 对节奏、高潮分布、伏笔规划等不确定之处持续讨论，直到作者确认

   **阶段4：开篇策略确认**
   - 将企划书的开篇策略落实为前3章详细规划
   - 展示前3章蓝图初稿
   - 作者有任何疑虑就继续讨论

   **阶段5：状态文件定稿**
   - 综合所有成果，展示 story-state.md、characters.md、outline.md 最终内容
   - 作者确认后写入状态文件

#### 4b. 无企划书时（传统路径）

调用**架构师 Agent**（读取 `.claude/agents/architect.md`）进行新书启动流程，**必须经过至少5轮深度交互**：

   **阶段1：故事基因探索** — 围绕核心创意展开
   - 基于作者提供的初始信息，动态提问
   - 方向：深入挖掘核心冲突、读者体验目标、独特卖点等
   - 有不明确之处就继续追问，直到作者说"够了"/"继续"

   **阶段2：世界观与金手指设计** — 基于前面讨论成果
   - 提出初步方案，针对薄弱环节和逻辑漏洞持续追问
   - 方向：机制细化、限制设计、成长路线、合理性验证等
   - 直到作者满意为止

   **阶段3：人物肖像深度构建** — 基于已确立的世界观
   - 展示人物设计初稿，持续讨论
   - 方向：性格深度、关系动态、人物弧线、标志性特征等
   - 直到作者确认人物到位

   **阶段4：大纲结构与剧情节奏** — 基于完整设定
   - 展示大纲初稿，持续讨论薄弱环节
   - 方向：高潮分布、伏笔规划、卷间递进、爽点节奏等
   - 直到作者对整体节奏满意

   **阶段5：开篇策略与定稿确认** — 总览全局
   - 展示前3章详细规划，查漏补缺
   - 方向：开篇吸引力、全局一致性、遗漏排查等
   - 作者确认后，将所有成果写入状态文件

   **动态提问原则**：每次只问一个问题。问题必须基于作者上一轮的具体回答动态生成。没有预设的固定问题数量——不明确的地方就继续问，直到作者表示满意。像资深编辑与作者的真实对话——敏锐捕捉亮点和盲区，顺势深挖。

> **提示**：如果你还没有做过深度故事规划，建议先运行 `/story-planning "{书名}"` 进行故事企划，再回来 init。企划阶段探索得越深，init 阶段就越高效。

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

## 流水线执行（增强版：融合Superpowers工程化模式）

### 核心理念

本流水线借鉴 Superpowers 软件工程工作流的5个核心原则：

1. **TDD类比**：先定义"读者期望规格"（=测试用例），再写正文（=实现代码）
2. **规格合规审查**：编剧产出后、文体家动笔前，验证剧本是否忠实执行了蓝图
3. **证据驱动验证**：每个质量判断必须有正文原文作为证据，拒绝模糊评价
4. **根因分析**：低分时先诊断问题出在哪个环节，而非盲目重写
5. **迭代熔断**：连续失败时强制决策点，防止无限循环

### 前置准备（Initializer / Coding Agent 分离）

借鉴 Anthropic "Effective harnesses for long-running agents"：**第一次进入和后续恢复使用不同的 prompt 策略**。

1. 确认 `books/{书名}/` 目录存在，否则提示先 `init`
2. **读取 `pipeline-state.md`**，判断进入哪种模式：

#### 模式 A：首次启动（Initializer Agent）

当 `pipeline-state.md` 无活跃流水线时：

1. 读取全量状态：`story-state.md`、`characters.md`、`outline.md`、`continuity-state.md`
2. 如果有前一章定稿，读取其结尾段
3. **生成「章节工作简报」**（`books/{书名}/drafts/chapter-{N}-brief.md`）：
   - 基于 `references/chapter-brief-template.md` 格式
   - 精炼全量状态为本章所需的最小上下文：故事背景、前情概要、前章结尾、本章任务、活跃人物、活跃伏笔
   - 这份简报是后续所有 session 恢复时的**唯一入口文件**，必须包含足够信息
4. 初始化 `pipeline-state.md` 为第 N 章
5. 进入 Step 1（架构师）

#### 模式 B：断点续写（Coding Agent）

当 `pipeline-state.md` 存在未完成流水线时（session 中断后恢复）：

**Coding Agent 不需要重读全量状态文件**，只需：
1. `pipeline-state.md`（知道流水线在哪）
2. `chapter-{N}-brief.md`（Initializer 已生成的精炼上下文）
3. 已 completed Step 的产出文件（知道上游结果）

这比每次都加载 4 个完整状态文件节省大量 context。

### 断点续写模式（Harness 持久化）

当 `pipeline-state.md` 中存在未完成的章节流水线时（session 中断后恢复的场景）：

1. 读取 `pipeline-state.md`，解析当前进度
2. 向作者报告恢复状态：
   ```
   检测到未完成的流水线：
   - 章节：第 N 章
   - 已完成：[列出 completed 的 Step]
   - 中断位置：[in_progress 的 Step]
   - 迭代状态：第 X 轮
   
   是否从中断位置继续？（输入"继续"恢复 / "重来"从头开始）
   ```
3. 如果作者选择继续：
   - 读取所有 completed Step 的产出文件作为上下文
   - 从 in_progress 的 Step 重新开始（context 已丢失，需重新执行该 Step）
   - 跳过已 completed 的 Step，不重复执行
4. 如果作者选择重来：
   - 重置 `pipeline-state.md`，从 Step 1 开始

### 流水线状态更新规则

**每个 Step 执行前后都必须更新 `pipeline-state.md`**：

- **开始执行 Step X** → 将该 Step 状态改为 `in_progress`，记录当前时间
- **Step X 完成** → 将状态改为 `completed`，填入产出文件名
- **Step X 失败/需回退** → 将状态改为 `failed`，记录原因
- **迭代回退** → 更新迭代状态（轮次、追读分、根因、回退目标），将回退目标 Step 状态改为 `in_progress`
- **定稿完成** → 清空 `pipeline-state.md`（恢复为模板初始状态），表示无活跃流水线

### Step 1：架构师（Architect）— 蓝图 + 读者期望规格

加载 Agent 指令：`.claude/agents/architect.md`

执行：
1. 读取状态文件和前章上下文
2. **5轮Brainstorm交互**（每轮动态生成至少3个问题）：
   - 第1轮：上下文回顾与章节定位
   - 第2轮：核心事件设计
   - 第3轮：场景与人物动线
   - 第4轮：伏笔与钩子设计
   - 第5轮：蓝图定稿确认
3. 作者确认后，产出最终蓝图
4. 写入 `books/{书名}/drafts/chapter-{N}-blueprint.md`
5. **【新增】生成读者期望规格**（TDD类比：先写测试）
   - 基于蓝图，定义本章的可验证读者体验目标
   - 包含：情绪目标、信息目标、悬念目标、爽点目标、伏笔目标
   - 每条目标必须具体到"读完后能明确回答做到了/没做到"
   - 写入 `books/{书名}/drafts/chapter-{N}-reader-spec.md`
   - 展示给作者确认

如果是 auto 模式，跳过 brainstorm，直接产出蓝图和读者期望规格。
如果作者在某轮说"继续"/"OK"，可加速后续轮次，但前2轮不可跳过。

### Step 2：编剧（Screenwriter）

加载 Agent 指令：`.claude/agents/screenwriter.md`

执行：
1. 读取架构师蓝图 + 读者期望规格 + characters.md
2. **5轮Brainstorm交互**（每轮动态生成至少3个问题）：
   - 第1轮：场景拆分方案展示
   - 第2轮：冲突节拍讨论
   - 第3轮：对话方向与信息流
   - 第4轮：节奏与情绪曲线
   - 第5轮：剧本定稿
3. 产出最终场景剧本
4. 写入 `books/{书名}/drafts/chapter-{N}-script.md`

如果作者说"继续"/"OK"，可加速后续轮次，但前2轮不可跳过。

### Step 2.5：蓝图合规审查（Spec Review）— 【新增质量关卡】

加载 Agent 指令：`.claude/agents/spec-reviewer.md`

这是借鉴 Superpowers 两阶段 Review 的关键创新：**先验证"做的是不是对的东西"，再验证"做得好不好"。**

执行：
1. 读取蓝图 `chapter-{N}-blueprint.md` + 剧本 `chapter-{N}-script.md`
2. 逐项检查：核心事件覆盖、场景结构对齐、人物动线一致、伏笔执行、章末钩子
3. 产出合规审查报告
4. 写入 `books/{书名}/drafts/chapter-{N}-spec-review.md`

**判定逻辑**：
- ✅ **通过**：继续进入 Step 3
- ⚠️ **有偏差需确认**：展示偏差给作者
  - 作者说"保留"→ 标记为"创造性偏差"，继续
  - 作者说"修正"→ 回到 Step 2 让编剧修改
- ❌ **严重偏离**：必须回到 Step 2 修正

auto 模式下：✅ 直接通过，⚠️ 自动保留创造性偏差，❌ 自动回 Step 2（最多1次）。

### Step 3：文体家（Stylist）

加载 Agent 指令：`.claude/agents/stylist.md`

执行：
1. 读取场景剧本 + 读者期望规格 + characters.md + style-guide.md + 前章结尾
2. **5轮Brainstorm交互**（每轮动态生成至少3个问题）：
   - 第1轮：正文初稿展示
   - 第2轮：开篇节奏与代入感讨论
   - 第3轮：对话自然度与角色声音
   - 第4轮：描写密度与爽点呈现
   - 第5轮：章末钩子与正文定稿
3. 产出最终正文
4. 写入 `books/{书名}/drafts/chapter-{N}-draft.md`

如果作者说"继续"/"OK"，可加速后续轮次，但前2轮不可跳过。

### Step 3.5：自动化 Lint（Harness Linting Layer）— 【新增质量关卡】

借鉴 OpenAI Harness Engineering："Custom linters enforce rules... remediation instructions are injected into agent context through error messages."

**这不是 Agent 的自觉遵守，而是 Harness 层的强制约束。**

执行：
1. 运行 `./tools/lint-chapter.sh books/{书名}/drafts/chapter-{N}-draft.md`
2. 解析 lint 报告：
   - **🔴 严重问题**（退出码 2）→ **必须回到 Step 3 文体家修复**，把 lint 报告作为修改指令注入
   - **🟡 警告**（退出码 1）→ 将 lint 报告附加到编辑 Agent 的输入中，作为额外审查维度
   - **🟢 全部通过**（退出码 0）→ 直接进入 Step 4

lint 检测项包括：破折号禁用、AI高频词黑名单、万能形容词计数、模板感叹句、连续等长句、段落开头模板化、字数范围、排比三连、纯对话连续、章末钩子套路化。

**关键理念**：把"希望 agent 做对"变成"让 agent 不可能做错"。Lint 报告中的修复建议直接告诉 agent 具体该怎么改。

### Step 4 & 5：编辑 + 读者 — 独立 Evaluator（GAN 启发）

借鉴 Anthropic "Harness design for long-running apps" 的 Generator/Evaluator 分离模式：

> **核心原则：模型无法可靠地自我评估。** Generator 和 Evaluator 必须在隔离的 context 中运行，
> Evaluator 不能接触 Generator 的推理过程，只能看到最终产出。

**编辑和读者必须作为独立 subagent 启动**，实现真正的评估独立性：

#### Step 4：编辑（独立 Evaluator Subagent）

**使用 `Agent` tool 启动独立 subagent**，prompt 中只包含：
- Agent 指令：`.claude/agents/editor.md` 的完整内容
- `books/{书名}/drafts/chapter-{N}-draft.md`（正文）
- `books/{书名}/drafts/chapter-{N}-blueprint.md`（蓝图）
- `books/{书名}/drafts/chapter-{N}-reader-spec.md`（规格）
- `books/{书名}/story-state.md`、`characters.md`、`continuity-state.md`（状态文件）
- Lint 报告（如果 Step 3.5 产生了警告）

**禁止传入的内容**：
- ❌ 文体家的 brainstorm 讨论记录
- ❌ 架构师/编剧的推理过程
- ❌ 编排器的任何内部状态

subagent 产出审阅报告 → 写入 `books/{书名}/drafts/chapter-{N}-review.md`

七维度审阅内容不变：
- 一致性、节奏、平台适配、文字质量（传统四维度）
- **蓝图合规性**：正文是否实现了蓝图中的核心事件？
- **连续性**：对照 continuity-state.md 检查事实/时间线/角色位置/知识边界/伏笔一致性
- **证据驱动验证**：每个评判必须引用正文原文

**铁律**：审阅中每个问题必须引用正文原文。不接受"感觉X有问题"式的模糊评价。

#### Step 5：读者（独立 Evaluator Subagent）

**使用 `Agent` tool 启动独立 subagent**，prompt 中只包含：
- Agent 指令：`.claude/agents/reader.md` 的完整内容
- `books/{书名}/drafts/chapter-{N}-draft.md`（正文）
- `books/{书名}/drafts/chapter-{N}-reader-spec.md`（规格）
- 前章结尾段（用于连续阅读体验）

**禁止传入的内容**：
- ❌ 编辑的审阅报告（读者评价应独立于编辑评价）
- ❌ 任何前序 Agent 的讨论记录
- ❌ 蓝图和剧本（读者不应该知道"设计意图"，只应感受"阅读体验"）

subagent 执行：
1. 正常阅读，记录自然感受
2. **逐条验证读者期望规格**（TDD类比：运行测试）
   - 对每条目标判定：✅ 达成 / ⚠️ 部分达成 / ❌ 未达成
   - 未达成的附上"我实际的感受是什么"
4. 结合自然感受和规格验证，给出追读分数（1-10）
5. 写入 `books/{书名}/drafts/chapter-{N}-feedback.md`

---

## 反馈循环（增强版：根因分析 + 迭代熔断）

读者产出追读分数后，将以下信息一并展示给作者：
- 编辑六维度审阅报告
- 读者反馈 + 追读分数
- **读者期望规格达成度**（X/Y 条通过）

### 追读分 ≥ 8 且规格达成率 ≥ 80%：章节通过

执行**证据驱动的完成确认**（借鉴 Superpowers Verification Before Completion）：

1. **完成验证清单**（每项必须有证据，不接受"应该没问题"）：
   - ☐ 正文中所有蓝图核心事件已实现（列出证据）
   - ☐ 读者期望规格已达成（引用读者验证报告）
   - ☐ 无人物一致性冲突（引用编辑报告相关段落）
   - ☐ 章末钩子有效（引用读者反馈中的追读意愿）
   - ☐ 字数在 2000-4000 范围内
2. 验证通过后，将正文复制到 `chapters/chapter-{NNN}.md`
3. 调用架构师执行**收尾工作**：
   - 更新 `story-state.md`（章节数、总字数）
   - 更新 `characters.md`（新人物、关系变化、能力变化）
   - 更新 `outline.md`（标记定稿、记录偏差和灵感）
4. **【Step 6】调用连续性追踪员**（`.claude/agents/continuity-tracker.md`）：
   - 生成"继承→发展→铺垫"三段式摘要，写入即时记忆
   - 提取事实到事实登记簿
   - 更新时间线
   - 更新角色动态状态（位置、情绪、已知信息等）
   - 更新伏笔账本（新埋/推进/回收/超期警告）
   - 执行矛盾扫描（事实/时间线/角色位置/能力设定/称呼）
   - 产出连续性追踪报告
5. **如果矛盾扫描发现 🔴 严重矛盾**：展示给作者，讨论是否需要修正（可能需要回到 Step 3 微调正文，或在下一章中自然修正）
6. 报告全部更新内容（架构师收尾 + 连续性追踪报告）

### 追读分 ≥ 8 但规格达成率 < 80%：需要作者决定

展示规格差异，由作者选择：
- **接受**："好看就行，规格不是铁律"→ 按通过处理
- **修改**："要补上缺失的目标"→ 回到 Step 3 文体家针对性修改

### 追读分 5-7：根因分析 → 定向修改

**【新增】根因分析阶段**（借鉴 Superpowers Systematic Debugging）：

不再盲目回到文体家重写，而是先诊断问题出在哪里：

**Phase 1：症状收集**
- 从编辑报告提取：哪些维度评分最低？具体问题是什么？
- 从读者反馈提取：哪个维度评分最低？什么时候"差点划走"？
- 从规格验证提取：哪些目标未达成？

**Phase 2：根因定位**
将问题追溯到源头环节：

| 症状 | 可能根因 | 定位到环节 |
|---|---|---|
| 情绪目标未达成 | 场景冲突设计不足 | → 编剧（剧本问题） |
| 信息目标未达成 | 信息流设计有误 | → 编剧（剧本问题） |
| 爽点不够 | 核心事件设计太平 | → 架构师（蓝图问题） |
| 节奏拖沓 | 描写过多/对话冗余 | → 文体家（执行问题） |
| 对话不自然 | 人物声音设定模糊 | → 文体家（执行问题） |
| 一致性问题 | 状态文件过时 | → 架构师（状态管理） |
| 读者困惑 | 信息密度不当 | → 编剧/文体家 |

**Phase 3：定向修复**
根据根因定位，只回到对应环节：
- **文体家问题**（节奏/对话/描写）→ 回 Step 3，带着具体修改指令
- **编剧问题**（场景/冲突/信息流）→ 回 Step 2，带着具体调整方向
- **蓝图问题**（核心事件/爽点设计）→ 回 Step 1，带着具体重审重点

修复后重走下游步骤（编辑→读者），最多迭代 2 次。

### 追读分 < 5：深度根因分析 → 重新设计

**Phase 1-2 同上**（症状收集 + 根因定位），但分析更深：
- 不只问"哪个环节出了问题"，还要问"设计前提是否成立"
- 是这个章节的问题，还是整个弧线的问题？
- 读者期望规格本身是否合理？

**Phase 3：带着诊断结论回到架构师**
- 展示完整诊断报告给作者
- 架构师根据诊断调整蓝图（而非从零开始）
- 重走完整流水线，最多迭代 2 次

### 迭代熔断机制（Circuit Breaker）— 【新增】

借鉴 Superpowers Systematic Debugging 的第4阶段："如果3次修复都失败了，质疑架构本身。"

**同一章累计迭代 3 次仍未通过**时，触发熔断：

```
⚠️ 迭代熔断：第 N 章已累计迭代 3 次，仍未达到通过标准。
这可能意味着问题不在执行层面，而在设计前提。

请选择：

1. 📌 接受当前版本
   保留最佳版本，标记待优化，继续推进后续章节。
   "完美是好的敌人。先有再优。"

2. 🔄 换一个方向
   放弃当前设计，为本章重新构思一个完全不同的核心事件。
   适用于：核心事件本身缺乏戏剧张力。

3. ✂️ 缩小范围
   降低本章野心，聚焦1个核心事件（而非2-3个），简化场景。
   适用于：章节试图做太多事。

4. ⏩ 跳过这个 beat
   重新审视大纲，考虑是否可以合并或跳过这个章节。
   适用于：这个章节的存在本身就有问题。
```

作者选择后，按选项执行。**每次熔断决策记录到 `outline.md` 的偏差记录中**，作为后续参考。

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
