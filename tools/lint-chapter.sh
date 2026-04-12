#!/bin/bash
# lint-chapter.sh — 章节自动化质量检测（Harness Linting Layer）
#
# 借鉴 OpenAI Harness Engineering 理念：
# "Custom linters enforce rules... remediation instructions are injected
#  into agent context through error messages."
#
# 用法: ./tools/lint-chapter.sh <markdown文件路径>
# 输出: 结构化 lint 报告，可直接注入 agent context
#
# 退出码: 0=全部通过, 1=有警告, 2=有严重问题

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "用法: $0 <章节文件路径>"
    echo "示例: $0 books/英伦崛起/drafts/chapter-2-draft.md"
    exit 1
fi

FILE="$1"
if [ ! -f "$FILE" ]; then
    echo "错误: 文件不存在 — $FILE"
    exit 1
fi

# 读取文件内容
CONTENT=$(cat "$FILE")
CHAR_COUNT=$(echo "$CONTENT" | wc -m)
LINE_COUNT=$(echo "$CONTENT" | wc -l)

# 计数器
ERRORS=0    # 严重问题 (🔴)
WARNINGS=0  # ���告 (🟡)
PASSES=0    # 通过 (🟢)

# 结果收集
REPORT=""

add_error() {
    ERRORS=$((ERRORS + 1))
    REPORT="${REPORT}\n🔴 [严重] $1"
    if [ -n "${2:-}" ]; then
        REPORT="${REPORT}\n   修复建议: $2"
    fi
}

add_warning() {
    WARNINGS=$((WARNINGS + 1))
    REPORT="${REPORT}\n🟡 [警告] $1"
    if [ -n "${2:-}" ]; then
        REPORT="${REPORT}\n   修复建��: $2"
    fi
}

add_pass() {
    PASSES=$((PASSES + 1))
    REPORT="${REPORT}\n🟢 [通过] $1"
}

# ============================================================
# 检测 1: 破折号（——）检测 [严重]
# 规则: 绝对禁止使用��折号
# ============================================================
DASH_COUNT=$(echo "$CONTENT" | grep -oP '——' | wc -l || true)
if [ "$DASH_COUNT" -gt 0 ]; then
    # 找到具体位置
    DASH_LINES=$(echo "$CONTENT" | grep -nP '——' | head -5)
    add_error "检测到 $DASH_COUNT 处破折号（——）— 这是AI写作最典型的坏习惯" \
              "用逗号、句号、冒号或重组句子替代。出现位置:\n$DASH_LINES"
else
    add_pass "无破折号使用"
fi

# ============================================================
# 检�� 2: AI高频词黑名单 [严重/警告]
# ============================================================

# 严格禁用词（出现即标记严重）
BANNED_WORDS="首先|其次|此外|另外|值得注意的是|总而言之|综上所述|但真相是|然而鲜为人知的是|但事情远没有这么简单"
BANNED_COUNT=$(echo "$CONTENT" | grep -oP "$BANNED_WORDS" | wc -l || true)
if [ "$BANNED_COUNT" -gt 0 ]; then
    BANNED_FOUND=$(echo "$CONTENT" | grep -noP "$BANNED_WORDS" | head -8)
    add_error "检测到 $BANNED_COUNT 个禁用过渡词/假冲突短语" \
              "删除或用具体动作/场景自然过渡。出现位置:\n$BANNED_FOUND"
else
    add_pass "无禁用过渡词"
fi

# 限用词（每章不超过2次，超过则警告）
check_limited_word() {
    local word="$1"
    local limit="$2"
    local count=$(echo "$CONTENT" | grep -oP "$word" | wc -l || true)
    if [ "$count" -gt "$limit" ]; then
        add_warning "「${word}」出现 $count 次（上限 $limit 次/章）" \
                    "用具体动作/反应代替，保留最有效的 $limit 处"
    fi
}

check_limited_word "不禁" 2
check_limited_word "竟然" 2
check_limited_word "居然" 2
check_limited_word "毫不犹豫" 1
check_limited_word "不由自主" 1

# 万能形容词（超过3次警告）
VAGUE_WORDS="深邃|凌厉|淡淡的|缓缓|微微"
VAGUE_COUNT=$(echo "$CONTENT" | grep -oP "$VAGUE_WORDS" | wc -l || true)
if [ "$VAGUE_COUNT" -gt 3 ]; then
    VAGUE_FOUND=$(echo "$CONTENT" | grep -oP "$VAGUE_WORDS" | sort | uniq -c | sort -rn)
    add_warning "万能形容词出现 $VAGUE_COUNT 次（阈值3次）" \
                "用具体的、不可替换的细节。分布:\n$VAGUE_FOUND"
elif [ "$VAGUE_COUNT" -le 3 ]; then
    add_pass "万能形容词使用节制（${VAGUE_COUNT}次）"
fi

# 模板感叹句
TEMPLATE_PHRASES="这一刻.*他明白了|心中涌起一股|一股无名的"
TEMPLATE_COUNT=$(echo "$CONTENT" | grep -cP "$TEMPLATE_PHRASES" || true)
if [ "$TEMPLATE_COUNT" -gt 0 ]; then
    TEMPLATE_FOUND=$(echo "$CONTENT" | grep -nP "$TEMPLATE_PHRASES" | head -5)
    add_warning "检测�� $TEMPLATE_COUNT 处模板感叹句" \
                "用外在动作表现内心（攥��、咬牙、手指发白）。出现位置:\n$TEMPLATE_FOUND"
else
    add_pass "无模板感叹句"
fi

# ============================================================
# 检测 3: 连续等长句检测 [警告]
# 规则: 不允许连续3个以上句子长度相近（±5字以内）
# ============================================================
# 提取每个句子（以句号、问号、感叹号分割）的字数
SIMILAR_RUNS=0
PREV_LEN=0
PPREV_LEN=0
RUN_COUNT=0

while IFS= read -r sentence; do
    LEN=$(echo "$sentence" | wc -m)
    # 忽略太短的句子（对话标签等）
    if [ "$LEN" -lt 5 ]; then
        RUN_COUNT=0
        continue
    fi
    if [ "$PREV_LEN" -gt 0 ]; then
        DIFF=$((LEN - PREV_LEN))
        DIFF=${DIFF#-}  # 绝对值
        if [ "$DIFF" -le 5 ]; then
            RUN_COUNT=$((RUN_COUNT + 1))
            if [ "$RUN_COUNT" -ge 3 ]; then
                SIMILAR_RUNS=$((SIMILAR_RUNS + 1))
                RUN_COUNT=0
            fi
        else
            RUN_COUNT=1
        fi
    else
        RUN_COUNT=1
    fi
    PPREV_LEN=$PREV_LEN
    PREV_LEN=$LEN
done <<< "$(echo "$CONTENT" | grep -oP '[^。！？\n]+[。！？]')"

if [ "$SIMILAR_RUNS" -gt 0 ]; then
    add_warning "检测到 $SIMILAR_RUNS 组连续等长句（3+句长度相近）" \
                "刻意穿插极短句（3-5字）打破均匀��奏"
else
    add_pass "句式长度有变化"
fi

# ============================================================
# 检测 4: 段落开头模板化检测 [警告]
# 规则: 不允许连续两段以相同句式结构开头
# ============================================================
SAME_START=0
PREV_START=""

while IFS= read -r line; do
    # 提取段落前两个字（判断句式模式：他+动词、她+动词等）
    START=$(echo "$line" | grep -oP '^.{1,2}' || true)
    if [ -n "$START" ] && [ "$START" = "$PREV_START" ]; then
        SAME_START=$((SAME_START + 1))
    fi
    PREV_START="$START"
done <<< "$(echo "$CONTENT" | grep -P '^\S' | grep -vP '^[#\-\|>]')"

if [ "$SAME_START" -gt 2 ]; then
    add_warning "连续同句式开头段落 $SAME_START 处" \
                "变换段落开头：用对话/环境/动作/时间词等不同方式起头"
else
    add_pass "段落开头多样化"
fi

# ============================================================
# 检测 5: 字数范围 [严重/警告]
# 规则: 2000-4000字
# ============================================================
if [ "$CHAR_COUNT" -lt 1500 ]; then
    add_error "字数严重不足: ${CHAR_COUNT}字（最低2000字���" \
              "补充场景细节、对话或情节推进"
elif [ "$CHAR_COUNT" -lt 2000 ]; then
    add_warning "字数偏少: ${CHAR_COUNT}���（推荐2000-4000字）" \
                "考虑补充一个过渡场景或深化现有场景"
elif [ "$CHAR_COUNT" -gt 4500 ]; then
    add_error "字数严重超出: ${CHAR_COUNT}字（上限4000字）" \
              "考虑拆分为两章，或精简描写和对话"
elif [ "$CHAR_COUNT" -gt 4000 ]; then
    add_warning "字数偏多: ${CHAR_COUNT}字（推荐2000-4000字）" \
                "精简冗余描写或拆分场景"
else
    add_pass "字数合规: ${CHAR_COUNT}字"
fi

# ============================================================
# 检��� 6: 排比三连检测 [警告]
# 规则: AI特别喜欢"他看到了X，看到了Y，看到了Z"式排比
# ============================================================
PARALLEL_COUNT=$(echo "$CONTENT" | grep -cP '(.{2,6})了.{2,15}，\1了.{2,15}，\1了' || true)
if [ "$PARALLEL_COUNT" -gt 0 ]; then
    add_warning "检��到 $PARALLEL_COUNT 处排比三连句式" \
                "打散排比，用不同句式结构表达"
else
    add_pass "无排比三连"
fi

# ============================================================
# 检测 7: 纯对话连续检测 [警告]
# 规则: 连续纯对话不超过4句须穿插动��
# ============================================================
DIALOGUE_RUN=0
MAX_DIALOGUE_RUN=0

while IFS= read -r line; do
    if echo "$line" | grep -qP '^[「"''""]|^——|^"' ; then
        DIALOGUE_RUN=$((DIALOGUE_RUN + 1))
    elif [ -n "$line" ]; then
        if [ "$DIALOGUE_RUN" -gt "$MAX_DIALOGUE_RUN" ]; then
            MAX_DIALOGUE_RUN=$DIALOGUE_RUN
        fi
        DIALOGUE_RUN=0
    fi
done <<< "$CONTENT"

if [ "$MAX_DIALOGUE_RUN" -gt 4 ]; then
    add_warning "最长连续纯对话 ${MAX_DIALOGUE_RUN} 句（��限4句）" \
                "在对话间穿插动作描写（搅咖啡、看手机、抖腿）"
else
    add_pass "对话间穿插得当"
fi

# ============================================================
# 检测 8: 章末钩子检测 [警告]
# 检查是否以转折句套路结尾
# ============================================================
LAST_LINES=$(echo "$CONTENT" | tail -3)
if echo "$LAST_LINES" | grep -qP '然而他不知道|然而.*不知道的是|殊不知|却不知'; then
    add_warning "章末使用了套路化转折钩子（'然而他不知道...'类型）" \
                "尝试其他钩子形式：悬念、新信息、情绪高点、突然中断"
else
    add_pass "章末钩子非模板化"
fi

# ============================================================
# 输出报告
# ============================================================
echo "═══════════════════════════════════════════"
echo "  章节 Lint 报告"
echo "  文件: $FILE"
echo "  字数: $CHAR_COUNT | 行数: $LINE_COUNT"
echo "═══════════════════════════════���═══════════"
echo ""
echo -e "$REPORT"
echo ""
echo "───────────────────────────────────────────"
echo "  汇总: 🔴 严重 $ERRORS | 🟡 警告 $WARNINGS | 🟢 通过 $PASSES"
echo "───���───────────────────────────────────────"

# 退出码
if [ "$ERRORS" -gt 0 ]; then
    echo ""
    echo "❌ Lint 未通过 — 存在 $ERRORS 个严重问题需修复后再提交审阅"
    exit 2
elif [ "$WARNINGS" -gt 0 ]; then
    echo ""
    echo "��️ Lint 有警告 — $WARNINGS 个问题建议修复"
    exit 1
else
    echo ""
    echo "✅ Lint 全部通过"
    exit 0
fi
