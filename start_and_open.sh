#!/bin/bash

# AI Common Platform 快速启动和测试脚本

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   AI Common Platform - 启动和测试                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 检查 Docker 和 Docker Compose
echo "📋 检查环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 启动服务
echo "🚀 启动所有服务..."
docker-compose up -d

echo "⏳ 等待服务启动... (30秒)"
sleep 30

echo ""
echo "📊 检查服务状态..."
echo ""

# 定义要检查的服务
services=(
    "postgres:5432:PostgreSQL"
    "localhost:6379:Redis"
    "localhost:19530:Milvus"
    "localhost:8001:QA Entry"
    "localhost:8002:Prompt Service"
    "localhost:8003:RAG Service"
    "localhost:8004:Agent Service"
    "localhost:8005:Integration Service"
    "localhost:8006:LLM Service"
    "localhost:3000:Web UI"
)

# 检查每个服务
for service in "${services[@]}"; do
    IFS=':' read -r host port name <<< "$service"
    
    # 特殊处理 postgres
    if [ "$name" = "PostgreSQL" ]; then
        if docker exec ai_platform_postgres pg_isready -U admin &> /dev/null; then
            echo "✅ $name - 正常"
        else
            echo "❌ $name - 离线"
        fi
    else
        if timeout 5 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
            echo "✅ $name - 正常"
        else
            echo "❌ $name - 离线或未响应"
        fi
    fi
done

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 启动完成                                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 访问地址："
echo "   🌐 Web UI:      http://localhost:3000"
echo "   📡 API 文档:    http://localhost:8001/docs"
echo ""
echo "🔧 常用命令："
echo "   docker-compose logs -f          # 查看实时日志"
echo "   docker-compose logs -f web_ui   # 查看 Web UI 日志"
echo "   docker-compose ps               # 查看容器状态"
echo "   docker-compose down             # 停止所有服务"
echo ""
echo "💡 提示："
echo "   在浏览器中打开 http://localhost:3000 开始使用！"
echo ""
