#!/bin/bash

# 启动aicommonplatform容器（不影响其他应用）

echo "🚀 启动 aicommonplatform 容器"
echo "=================================================="
echo ""

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"

# 远程执行
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$REMOTE_IP 2>&1 << 'REMOTE_SCRIPT'
set -e

cd /root/aicommonplatform

echo "✅ 进入 aicommonplatform 目录"
echo ""

echo "📦 检查 aicommonplatform 镜像..."
docker images | grep aicommonplatform | wc -l
echo "个镜像已加载"

echo ""
echo "🔍 当前运行中的容器："
docker ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "🐳 启动 aicommonplatform 容器..."
docker-compose -f docker-compose.yml up -d 2>&1 | grep -E "Creating|Starting|Running"

echo ""
echo "⏳ 等待容器启动 (5秒)..."
sleep 5

echo ""
echo "📊 aicommonplatform 容器状态："
docker ps --filter "name=ai_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ 启动完成！"
REMOTE_SCRIPT
