#!/bin/bash

# 修复Docker网络问题

echo "🔧 修复Docker网络配置..."
echo ""

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"

sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 root@$REMOTE_IP 2>&1 << 'REMOTE'

cd /root/aicommonplatform

echo "1️⃣ 清理现有网络..."
docker-compose -f docker-compose.yml down 2>&1 | tail -5

echo ""
echo "2️⃣ 删除旧网络..."
docker network rm aicommonplatform_ai_net 2>/dev/null || echo "网络不存在（正常）"

echo ""
echo "3️⃣ 重启Docker服务..."
systemctl restart docker

sleep 3

echo "4️⃣ 重建网络并启动容器..."
docker-compose -f docker-compose.yml up -d 2>&1 | tail -10

sleep 5

echo ""
echo "✅ 容器启动状态："
docker ps --filter "name=ai_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📊 所有容器（包括其他应用）："
docker ps --format "table {{.Names}}\t{{.Status}}"

REMOTE
