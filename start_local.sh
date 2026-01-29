#!/bin/bash

# AI 平台本地运行启动脚本
# 快速启动 Docker 并打开管理控制台

echo "🚀 启动 AI 平台..."

# 进入项目目录
cd "$(dirname "$0")" || exit

# 启动容器
echo "📦 启动 Docker 容器..."
docker-compose -f docker-compose.lite.yml up -d --build

# 等待容器启动
echo "⏳ 等待服务启动（30秒）..."
sleep 30

# 检查状态
echo "✅ 检查服务状态..."
docker-compose -f docker-compose.lite.yml ps

# 打开管理控制台
echo "🌐 打开管理控制台..."
sleep 2

# 根据操作系统选择打开浏览器的命令
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:3000/admin"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "http://localhost:3000/admin" || echo "请手动打开 http://localhost:3000/admin"
else
    # Windows or other
    echo "请手动打开 http://localhost:3000/admin"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✨ AI 平台已启动！"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 访问地址："
echo "   管理控制台: http://localhost:3000/admin"
echo "   主界面: http://localhost:3000"
echo "   API文档: http://localhost:8002/docs"
echo ""
echo "📋 功能："
echo "   • 5 个 Prompt 模板"
echo "   • 9 个 Agent 工具"
echo "   • 拖拽配置界面"
echo "   • 完整的 REST API"
echo ""
echo "⚠️  重要："
echo "   请编辑 .env 文件，配置 OpenAI API Key："
echo "   OPENAI_API_KEY=sk-proj-your-key-here"
echo ""
echo "💡 常用命令："
echo "   停止: docker-compose -f docker-compose.lite.yml down"
echo "   日志: docker-compose -f docker-compose.lite.yml logs -f"
echo "   状态: docker-compose -f docker-compose.lite.yml ps"
echo ""
echo "════════════════════════════════════════════════════════════════"
