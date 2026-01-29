#!/bin/bash

# 部署验证脚本
REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"

echo "🚀 验证阿里云部署"
echo "=========================================="
echo ""

# 检查Web UI
echo "📍 检查Web UI (端口 3000)..."
if curl -s -m 3 http://$REMOTE_IP:3000/ | grep -q "<!DOCTYPE"; then
  echo "  ✅ Web UI 正常运行"
else
  echo "  ❌ Web UI 无法访问"
fi

# 检查QA服务
echo "📍 检查QA服务 (端口 8001)..."
if curl -s -m 3 http://$REMOTE_IP:8001/docs > /dev/null 2>&1; then
  echo "  ✅ QA服务 正常运行"
else
  echo "  ❌ QA服务 无法访问"
fi

# 检查RAG服务
echo "📍 检查RAG服务 (端口 8003)..."
if curl -s -m 3 http://$REMOTE_IP:8003/docs > /dev/null 2>&1; then
  echo "  ✅ RAG服务 正常运行"
else
  echo "  ❌ RAG服务 无法访问"
fi

echo ""
echo "📊 远程容器状态:"
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@$REMOTE_IP "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'" 2>/dev/null || echo "  (无法连接SSH)"

echo ""
echo "=========================================="
echo "✅ 验证完成"
echo ""
