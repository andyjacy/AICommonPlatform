#!/bin/bash

# 用户管理和国际化功能快速启动脚本

echo "=================================="
echo "🚀 AI 平台 - 用户管理和国际化启动"
echo "=================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

echo "📋 启动步骤："
echo "1. 启动 Web UI 服务（包含用户管理和问答历史）"
echo "2. 初始化数据库和用户表"
echo ""

# 启动 docker-compose
echo "🐳 启动 Docker Compose..."
docker-compose -f docker-compose.lite.yml up -d web_ui

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 3

# 验证服务健康
echo "✅ 检查服务状态..."
if curl -s http://localhost:3000/api/system/health > /dev/null; then
    echo "✅ Web UI 服务已启动（端口 3000）"
else
    echo "❌ Web UI 服务启动失败"
    exit 1
fi

echo ""
echo "=================================="
echo "🎉 启动完成！"
echo "=================================="
echo ""
echo "📝 关键功能："
echo "  ✅ 用户会话管理 - 登录生成持久化 token"
echo "  ✅ 用户数据隔离 - 每个用户只看自己的问答"
echo "  ✅ 国际化支持 - 中英文切换"
echo "  ✅ 问答追踪 - 完整的调用链和历史"
echo ""
echo "🔗 访问方式："
echo "  • 登录页面: http://localhost:3000/login"
echo "  • 主页面: http://localhost:3000/"
echo ""
echo "👤 默认账号："
echo "  • 用户名: admin"
echo "  • 密码: admin123"
echo ""
echo "📚 API 端点："
echo "  • POST /api/login - 用户登录"
echo "  • GET /api/user/verify-token - 验证会话"
echo "  • POST /api/user/logout - 用户登出"
echo "  • PUT /api/user/language - 设置语言"
echo "  • GET /api/qa/history - 获取问答历史"
echo "  • GET /api/qa/history/{id} - 获取问答详情"
echo ""
echo "🧪 快速测试："
echo ""
echo "1️⃣ 登录获取 token："
echo "  curl -X POST http://localhost:3000/api/login \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\":\"admin\",\"password\":\"admin123\"}'"
echo ""
echo "2️⃣ 验证会话："
echo "  curl 'http://localhost:3000/api/user/verify-token?token=YOUR_TOKEN'"
echo ""
echo "3️⃣ 获取问答历史："
echo "  curl 'http://localhost:3000/api/qa/history?token=YOUR_TOKEN&limit=10'"
echo ""
echo "4️⃣ 切换语言："
echo "  curl -X PUT 'http://localhost:3000/api/user/language?token=YOUR_TOKEN&language=en'"
echo ""
echo "📖 完整文档："
echo "  • 详见 USER_MANAGEMENT_GUIDE.md"
echo ""
echo "=================================="
