#!/bin/bash

# AI Common Platform - 轻量级版本启动脚本
# 专为本地学习和开发优化，资源占用最小

echo "🚀 启动 AI Platform 轻量级版本..."
echo ""
echo "📊 资源配置:"
echo "  • 基础设施: Redis (仅缓存)"
echo "  • 存储: 内存 + 本地文件"
echo "  • 服务数: 7 个微服务 + Web UI"
echo "  • 推荐: 2GB RAM, 1GB 磁盘"
echo ""

# 检查 docker 和 docker-compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

cd "$(dirname "$0")" || exit 1

# 清理旧容器（可选）
echo "🧹 清理旧容器..."
docker-compose -f docker-compose.lite.yml down 2>/dev/null || true

echo ""
echo "⏳ 启动容器（这需要 2-3 分钟）..."
echo ""

# 启动容器
docker-compose -f docker-compose.lite.yml up -d

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📋 服务状态检查:"
docker-compose -f docker-compose.lite.yml ps

echo ""
echo "✅ 启动完成！"
echo ""
echo "📍 访问地址:"
echo "  🌐 Web UI:          http://localhost:3000"
echo "  📝 QA 入口:         http://localhost:8001"
echo "  📚 Prompt 服务:     http://localhost:8002"
echo "  🔍 RAG 知识库:      http://localhost:8003"
echo "  🤖 Agent 执行:      http://localhost:8004"
echo "  🔗 Integration:     http://localhost:8005"
echo "  🧠 LLM 服务:        http://localhost:8006"
echo ""
echo "🛑 停止服务: docker-compose -f docker-compose.lite.yml down"
echo "📖 查看日志: docker-compose -f docker-compose.lite.yml logs -f"
echo ""
