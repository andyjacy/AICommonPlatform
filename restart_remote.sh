#!/bin/bash

# 启动远程容器脚本

echo "🚀 启动远程Docker容器"
echo "=================================================="
echo ""

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"

# 创建临时脚本在远程执行
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$REMOTE_IP 2>&1 << 'REMOTE_SCRIPT'
cd /root/aicommonplatform

echo "📦 检查Docker镜像..."
docker images | grep aicommonplatform | wc -l
echo "个镜像已加载"

echo ""
echo "🐳 启动容器..."
docker-compose -f docker-compose.yml down 2>/dev/null || true
sleep 2
docker-compose -f docker-compose.yml up -d 2>&1

echo ""
echo "⏳ 等待容器启动..."
sleep 5

echo ""
echo "📊 容器状态："
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ 启动完成"
REMOTE_SCRIPT
