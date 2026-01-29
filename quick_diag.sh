#!/bin/bash

# 快速诊断脚本

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"
LOG_FILE="/tmp/diag-$(date +%s).log"

echo "📋 收集远程诊断信息..."
echo "日志保存到: $LOG_FILE"
echo ""

# 执行远程诊断
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 root@$REMOTE_IP > "$LOG_FILE" 2>&1 << 'SSH_DIAG'
set -e
cd /root/aicommonplatform

echo "========== 容器状态 =========="
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "========== 镜像信息 =========="
docker images | grep aicommonplatform | head -10

echo ""
echo "========== Web UI 容器检查 =========="
docker inspect ai_web_ui 2>/dev/null | grep -E "State|Image|Ports" || echo "容器不存在"

echo ""
echo "========== Web UI 日志 (最后100行) =========="
docker logs --tail 100 ai_web_ui 2>&1 || echo "无法获取日志"

echo ""
echo "========== QA Entry 日志 (最后50行) =========="
docker logs --tail 50 ai_qa_entry 2>&1 || echo "无法获取日志"

echo ""
echo "========== 监听端口 =========="
ss -tlnp 2>/dev/null | grep -E "9000|8001|8003" || echo "无法检查端口"

echo ""
echo "========== docker-compose 配置 =========="
head -30 docker-compose.yml

SSH_DIAG

# 显示日志
echo ""
echo "✅ 完整诊断信息："
echo "=================================================="
cat "$LOG_FILE"
