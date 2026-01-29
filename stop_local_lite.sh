#!/bin/bash

# 停止本地轻量级服务脚本

echo ""
echo "🛑 停止 AI Common Platform 服务..."
echo ""

# 从 PID 文件读取
if [ -f /tmp/ai_lite.pids ]; then
    while IFS= read -r pid; do
        if [ -n "$pid" ]; then
            echo "   终止进程 $pid..."
            kill $pid 2>/dev/null || true
        fi
    done < /tmp/ai_lite.pids
    rm -f /tmp/ai_lite.pids
    echo "✅ 所有进程已终止"
else
    echo "⚠️  未找到 PID 文件，尝试杀死相关进程..."
    # 尝试杀死相关的 Python 进程
    pkill -f "uvicorn main:app --host 0.0.0.0 --port 8003" 2>/dev/null || true
    pkill -f "uvicorn main:app --host 0.0.0.0 --port 8001" 2>/dev/null || true
    pkill -f "uvicorn main:app --host 0.0.0.0 --port 3000" 2>/dev/null || true
    echo "✅ 相关进程已终止"
fi

echo ""
echo "✨ 清理日志文件..."
rm -f /tmp/rag_service.log /tmp/qa_entry.log /tmp/web_ui.log
echo "✅ 完成"
echo ""
