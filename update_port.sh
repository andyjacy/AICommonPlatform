#!/bin/bash

echo "🔄 更新Web UI端口到9000..."
echo ""

# 上传新配置
echo "📤 上传配置文件..."
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 22 \
  /Users/zhao_/Documents/PRC/AI实践/AICommonPlatform/docker-compose.remote.yml \
  root@47.100.35.44:/root/aicommonplatform/docker-compose.yml 2>/dev/null

# 重启容器
echo "🔄 重启容器..."
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@47.100.35.44 2>/dev/null << 'SSH_CMD'
cd /root/aicommonplatform
docker-compose down web_ui 2>/dev/null || true
sleep 1
docker-compose up -d web_ui
sleep 2
docker ps --filter "name=ai_web_ui" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
SSH_CMD

echo ""
echo "✅ Web UI 已迁移到端口 9000"
echo "   访问地址: http://47.100.35.44:9000"
