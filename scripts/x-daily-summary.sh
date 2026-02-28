#!/bin/bash
# X.com 每日综述脚本
# 每天早上 6 点执行

SCRIPT_DIR="/Users/clark/clawd/scripts"
LOG_FILE="$HOME/code/x-summary.log"
SUMMARY_FILE="$SCRIPT_DIR/x-summary-today.md"

mkdir -p "$(dirname "$LOG_FILE")"

{
    echo ""
    echo "=================================================="
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
    echo "=== X.com 每日综述任务 ==="
    echo "=================================================="
    echo "开始执行..."
    
    # 激活虚拟环境并运行 Python 脚本
    cd "$SCRIPT_DIR"
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        
        # 运行 Python 脚本
        python3 "$SCRIPT_DIR/x-daily-summary-browser.py"
        RESULT=$?
        
        echo "Python 脚本执行完成 (返回码: $RESULT)"
    else
        echo "❌ 虚拟环境不存在"
        echo "请先运行: cd $SCRIPT_DIR && python3 -m venv venv && source venv/bin/activate && pip install playwright && python -m playwright install chromium"
        RESULT=1
    fi
    
    # 显示结果
    if [ -f "$SUMMARY_FILE" ]; then
        echo ""
        echo "✅ 综述文件已生成：$SUMMARY_FILE"
        echo ""
        echo "--- 前20条内容 ---"
        head -100 "$SUMMARY_FILE"
    else
        echo ""
        echo "❌ 未生成综述文件"
    fi
    
    echo ""
    echo "=================================================="
    echo "任务执行完成"
    echo "=================================================="
    
} >> "$LOG_FILE" 2>&1

# 更新状态
echo "$(date '+%Y-%m-%d %H:%M:%S') - 执行完成" >> "$SCRIPT_DIR/last-run-status.txt"