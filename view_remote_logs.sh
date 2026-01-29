#!/bin/bash

# 查看远程服务器日志脚本

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"

echo "🔍 查看远程服务器日志"
echo "=================================================="
echo ""

# 查看容器状态和日志
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$REMOTE_IP 2>/dev/null << 'EOF'
echo "📦 === 容器运行状态 ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📋 === Web UI 日志 (最后30行) ==="
docker logs --tail 30 ai_web_ui 2>&1 || echo "容器不存在或错误"

echo ""
echo "📋 === QA Entry 日志 (最后30行) ==="
docker logs --tail 30 ai_qa_entry 2>&1 || echo "容器不存在或错误"

echo ""
echo "📋 === RAG Service 日志 (最后30行) ==="
docker logs --tail 30 ai_rag_service 2>&1 || echo "容器不存在或错误"

echo ""
echo "💾 === 系统资源使用 ==="
echo "磁盘使用:"
df -h | grep -E "^/dev|^Filesystem"

echo ""
echo "内存使用:"
free -h | head -2

echo ""
echo "📊 === Docker 容器资源使用 ==="
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.CPUPerc}}" 2>/dev/null || echo "无法获取stats"

echo ""
echo "🔌 === 监听端口 ==="
netstat -tlnp 2>/dev/null | grep -E "9000|8001|8003|8002|8004|8005|8006" || ss -tlnp 2>/dev/null | grep -E "9000|8001|8003|8002|8004|8005|8006" || echo "无法检查端口"

EOF
