#!/bin/bash

# 简单启动脚本 - 后台运行

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"

# 后台执行，避免终端卡顿
nohup sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 root@$REMOTE_IP << 'REMOTE' > /tmp/startup.log 2>&1 &

cd /root/aicommonplatform

# 停止旧容器
docker-compose -f docker-compose.yml stop 2>/dev/null || true

# 等待
sleep 2

# 启动新容器
docker-compose -f docker-compose.yml up -d

# 等待启动
sleep 8

# 记录状态
echo "=== 启动完成 ===" >> /tmp/startup.log
docker ps --filter "name=ai_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" >> /tmp/startup.log 2>&1

REMOTE

echo "✅ 后台启动任务已提交"
echo "日志保存在: /tmp/startup.log"
sleep 2
echo ""
echo "启动日志:"
cat /tmp/startup.log 2>/dev/null | tail -20 || echo "任务执行中..."
