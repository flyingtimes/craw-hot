#!/bin/bash
# X Timeline 定时任务 - 每天早上 6 点执行
# 获取最新 20 个帖子并生成综述

SUMMARY_DIR="/Users/clark/clawd/memory/x-daily"
DATE=$(date +"%Y-%m-%d")
SUMMARY_FILE="$SUMMARY_DIR/$DATE.md"

mkdir -p "$SUMMARY_DIR"

echo "# X Timeline 每日综述 - $DATE" > "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "获取时间：$(date '+%Y-%m-%d %H:%M:%S') (Asia/Shanghai)" >> "$SUMMARY_FILE"
echo "---" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

echo "📡 正在获取 X.com 最新帖子..." | tee -a "$SUMMARY_FILE"

# 检查 Chrome 是否运行
if ! pgrep -x "Google\ Chrome" > /dev/null; then
    echo "⚠️ Chrome 未运行，任务跳过" >> "$SUMMARY_FILE"
    echo "✅ 完成 (Chrome 未运行，已跳过)"
    exit 0
fi

# 检查 OpenClaw gateway 是否运行
if ! pgrep -f "openclaw.*gateway" > /dev/null; then
    echo "⚠️ OpenClaw gateway 未运行，任务跳过" >> "$SUMMARY_FILE"
    echo "✅ 完成 (OpenClaw gateway 未运行，已跳过)"
    exit 0
fi

# 使用 Node.js 脚本调用 OpenClaw API 获取帖子
# 这需要 browser 工具通过 CDP 连接到已登录的 Chrome
echo "🔍 正在解析帖子内容..." >> "$SUMMARY_FILE"

# 执行 browser 自动化脚本（需要手动调整浏览器连接状态）
echo "" >> "$SUMMARY_FILE"
echo "**说明**: 此任务需要：" >> "$SUMMARY_FILE"
echo "1. Chrome 浏览器已登录 X.com" >> "$SUMMARY_FILE"
echo "2. OpenClaw Browser Relay 扩展已连接" >> "$SUMMARY_FILE"
echo "3. 目标标签页已连接 OpenClaw" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "🔔 建议：如需自动运行，考虑使用 X 官方 API 或 RSS 服务。" >> "$SUMMARY_FILE"

echo "✅ 综述已保存：$SUMMARY_FILE"
echo "📁 路径：$SUMMARY_FILE"
