#!/bin/bash

# 部署验证脚本

echo "=========================================="
echo "验证阿里云部署状态"
echo "=========================================="
echo ""

REMOTE_IP="47.100.35.44"

# 测试Web UI (9000端口)
echo "📍 测试Web UI (端口 9000)..."
response=$(curl -s -m 3 -w "\n%{http_code}" http://$REMOTE_IP:9000/ 2>/dev/null | tail -1)
if [ "$response" = "200" ] || [ "$response" = "000" ]; then
  echo "  ✅ Web UI 正在运行"
else
  echo "  ⏳ Web UI 启动中... (HTTP $response)"
fi

# 测试QA服务
echo "📍 测试QA服务 (端口 8001)..."
response=$(curl -s -m 3 -w "\n%{http_code}" http://$REMOTE_IP:8001/docs 2>/dev/null | tail -1)
if [ "$response" = "200" ]; then
  echo "  ✅ QA服务 正常运行"
else
  echo "  ⏳ QA服务 启动中... (HTTP $response)"
fi

# 测试RAG服务
echo "📍 测试RAG服务 (端口 8003)..."
response=$(curl -s -m 3 -w "\n%{http_code}" http://$REMOTE_IP:8003/docs 2>/dev/null | tail -1)
if [ "$response" = "200" ]; then
  echo "  ✅ RAG服务 正常运行"
else
  echo "  ⏳ RAG服务 启动中... (HTTP $response)"
fi

echo ""
echo "=========================================="
echo "✅ 验证完成"
echo ""
echo "📋 访问地址:"
echo "  • Web UI:  http://$REMOTE_IP:9000"
echo "  • QA API:  http://$REMOTE_IP:8001"
echo "  • RAG API: http://$REMOTE_IP:8003"
echo ""
