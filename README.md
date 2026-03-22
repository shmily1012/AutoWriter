# AutoWriter — AI 多 Agent 网文创作系统

基于 Claude Code Skill 的 6-Agent 流水线协作长篇小说创作系统。

## 架构

6 个专业 Agent 按流水线协作，每步支持作者 brainstorm 参与：

```
[研究员按需] → 架构师 ⇄ 作者 → 编剧 ⇄ 作者 → 文体家 ⇄ 作者 → 编辑 → 读者 → 定稿
```

| Agent | 职责 | 交付物 |
|-------|------|--------|
| 架构师 | 故事结构、情节弧线、长线布局 | 章节蓝图 |
| 编剧 | 场景设计、冲突节拍、对话框架 | 场景剧本 |
| 文体家 | 语言风格、叙事节奏、正文写作 | 完整章节（2000-4000字） |
| 编辑 | 质量把控、一致性检查 | 审阅报告 + ABCD 评分 |
| 读者 | 情绪验证、代入感评估 | 追读分数（1-10） |
| 研究员 | 网络查询真实信息 | 研究备忘录 |

## 使用

在 Claude Code 中：

```
/write-novel init "我的小说"     # 初始化新书
/write-novel chapter "我的小说" 1 # 写第1章（交互模式）
/write-novel auto "我的小说" 2   # 自动写第2章
/write-novel status "我的小说"   # 查看进度
/write-novel list               # 列出所有书
/write-novel research "话题"    # 查询真实信息
```

## 目录结构

```
.claude/skills/write-novel/    # 主 Skill 定义
.claude/agents/                # 6 个 Agent 定义
references/                    # 模板文件
books/{书名}/                  # 每本书独立目录
  ├── story-state.md           # 故事状态
  ├── characters.md            # 人物图谱
  ├── outline.md               # 大纲
  ├── chapters/                # 定稿章节
  └── drafts/                  # 流水线中间产物
```

## 反馈循环

- 追读分 ≥ 8：章节通过，进入定稿
- 追读分 5-7：返回文体家修改
- 追读分 < 5：返回架构师重新设计
- 每次循环最多迭代 2 次
