#!/bin/bash

# 快速本地轻量级启动脚本
# 在 Python 虚拟环境中运行所有服务

set -e

PROJECT_DIR="/Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform"
VENV_DIR="$PROJECT_DIR/.venv_lite"

cd "$PROJECT_DIR"

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║  🚀 AI Common Platform - 轻量级本地运行   ║"
echo "║     (真实大模型 + ChatAnywhere 支持)       ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# 创建虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 升级 pip
echo "📚 升级 pip..."
pip install --upgrade -q pip

# 安装依赖
echo "📚 安装依赖包..."
pip install -q \
    fastapi \
    uvicorn \
    pydantic \
    pydantic-settings \
    redis \
    python-dotenv \
    aiohttp \
    httpx \
    openai

echo "✅ 所有依赖已安装"
echo ""

# 启动 Redis（可选）
echo "🔷 检查 Redis..."
if command -v docker &> /dev/null; then
    REDIS_CHECK=$(docker ps --filter "name=ai_lite_redis" -q 2>/dev/null || true)
    if [ -z "$REDIS_CHECK" ]; then
        echo "   启动 Redis Docker 容器..."
        docker run -d --name ai_lite_redis -p 6379:6379 redis:7-alpine >/dev/null 2>&1 || {
            echo "   ⚠️  Redis 启动失败，继续..."
        }
        sleep 2
    fi
    echo "✅ Redis 就绪"
else
    echo "⚠️  Docker 未安装，跳过 Redis 启动"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 启动服务..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 启动 RAG 服务（后台）
echo "📚 [1/3] RAG 服务 (http://localhost:8003)"
cd "$PROJECT_DIR/services/rag_service"
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8003 > /tmp/rag_service.log 2>&1 &
RAG_PID=$!
sleep 1
echo "      ✅ PID: $RAG_PID"

# 启动 QA Entry 服务（后台）
echo "❓ [2/3] QA Entry (http://localhost:8001)"
cd "$PROJECT_DIR/services/qa_entry"
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/qa_entry.log 2>&1 &
QA_PID=$!
sleep 2
echo "      ✅ PID: $QA_PID"

# 启动 Web UI（前台）
echo "🌍 [3/3] Web UI (http://localhost:3000)"
cd "$PROJECT_DIR/services/web_ui"
nohup python -m uvicorn main:app --host 0.0.0.0 --port 3000 > /tmp/web_ui.log 2>&1 &
WEB_PID=$!
sleep 1
echo "      ✅ PID: $WEB_PID"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ 所有服务已启动！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "� 服务地址:"
echo ""
echo "   🌍 Web UI:        http://localhost:3000"
echo "   ❓ QA Entry:      http://localhost:8001"
echo "   📚 RAG Service:   http://localhost:8003"
echo "   🔷 Redis:         localhost:6379"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 快速开始:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  打开 Web UI 并配置 LLM 模型:"
echo ""
echo "   🌐 http://localhost:3000"
echo ""
echo "   菜单 → LLM 模型管理 → 添加新模型"
echo ""
echo "   选择提供商:"
echo "   • ChatAnywhere (免费): https://chatanywhere.com.cn/"
echo "   • OpenAI (需要付费): https://platform.openai.com/"
echo ""
echo "2️⃣  测试 QA 功能:"
echo ""
echo "   curl -X POST http://localhost:8001/api/qa/ask \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{"
echo "       \"question\": \"2024年Q1的销售业绩如何？\","
echo "       \"user_id\": \"test_user\""
echo "     }'"
echo ""
echo "3️⃣  查看知识库文档:"
echo ""
echo "   curl http://localhost:8003/api/rag/documents"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 日志文件:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   RAG Service:  /tmp/rag_service.log"
echo "   QA Entry:     /tmp/qa_entry.log"
echo "   Web UI:       /tmp/web_ui.log"
echo ""
echo "   查看实时日志:"
echo "   tail -f /tmp/qa_entry.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 停止服务:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   kill $RAG_PID $QA_PID $WEB_PID"
echo ""
echo "   或执行："
echo "   bash /Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform/stop_local_lite.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 保存 PID 到文件以便后续停止
echo "$RAG_PID" > /tmp/ai_lite.pids
echo "$QA_PID" >> /tmp/ai_lite.pids
echo "$WEB_PID" >> /tmp/ai_lite.pids

echo "💡 提示：服务已在后台运行"
echo "   可以关闭此终端窗口"
echo ""
