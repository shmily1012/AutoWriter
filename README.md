# AutoWriter — AI 多 Agent 网文创作系统

基于 Claude Code Skill 的 7-Agent 工程化流水线协作长篇小说创作系统，融合 [Superpowers](https://github.com/obra/superpowers) 软件工程工作流核心理念。

## 架构

7 个专业 Agent 按流水线协作，每步支持作者 brainstorm 参与：

```
[研究员按需] → 架构师 ⇄ 作者 → 读者期望规格 → 编剧 ⇄ 作者 → 蓝图合规审查 → 文体家 ⇄ 作者 → 编辑(6维度) → 读者(TDD验证) → 定稿
```

| Agent | 职责 | 交付物 |
|-------|------|--------|
| 架构师 | 故事结构、情节弧线、长线布局 | 章节蓝图 + 读者期望规格 |
| 编剧 | 场景设计、冲突节拍、对话框架 | 场景剧本 |
| 蓝图合规审查 | 验证剧本是否忠实执行蓝图 | 合规报告 |
| 文体家 | 语言风格、叙事节奏、正文写作 | 完整章节（2000-4000字） |
| 编辑 | 六维度审阅（含蓝图合规+证据驱动验证） | 审阅报告 + ABCD 评分 |
| 读者 | 情绪验证、代入感评估、TDD规格验证 | 追读分数（1-10）+ 规格通过率 |
| 研究员 | 网络查询真实信息 | 研究备忘录 |

## Superpowers 融合

| Superpowers 概念 | 创作系统等价物 |
|---|---|
| TDD | 读者期望规格（先定义成功标准再写正文） |
| Spec Compliance Review | 蓝图合规审查（剧本是否忠实执行蓝图） |
| Verification Before Completion | 证据驱动验证（每个判断都引用正文原文） |
| Systematic Debugging | 根因分析（低分时诊断问题出在哪个环节） |
| Circuit Breaker | 迭代熔断（3次失败后强制选择方向） |

## 使用

在 Claude Code 中：

```
/write-novel init "我的小说"     # 初始化新书
/write-novel chapter "我的小说" 1 # 写第1章（交互模式）
/write-novel auto "我的小说" 2   # 自动写第2章
/write-novel status "我的小说"   # 查看进度
/write-novel list               # 列出所有书
/write-novel review "我的小说" 1 # 审阅第1章
/write-novel research "话题"    # 查询真实信息
```

## 目录结构

```
.claude/skills/write-novel/    # 主 Skill 定义
.claude/agents/                # 7 个 Agent 定义
references/                    # 模板文件（含 reader-spec-template.md）
books/{书名}/                  # 每本书独立目录
  ├── story-state.md           # 故事状态
  ├── characters.md            # 人物图谱
  ├── outline.md               # 大纲
  ├── pipeline-state.md        # 流水线断点状态（跨session持久化）
  ├── chapters/                # 定稿章节
  └── drafts/                  # 流水线中间产物
```

## 反馈循环

- 追读分 ≥ 8 且规格通过率 ≥ 80%：章节通过，进入定稿
- 追读分 5-7：触发根因分析，定位问题环节后针对性修改
- 追读分 < 5：返回架构师重新设计
- 3次迭代失败触发熔断机制，强制决策点
