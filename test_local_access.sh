#!/bin/bash

# 检查远程服务器本地访问

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"

sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 root@$REMOTE_IP 2>&1 << 'EOF' | tail -50

cd /root/aicommonplatform

echo "=== 容器状态 ==="
docker ps --filter "name=ai_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=== 本地HTTP测试 (localhost:9000) ==="
response=$(curl -s -m 2 -w "%{http_code}" -o /tmp/curl_test.html http://localhost:9000/ 2>&1)
echo "HTTP状态码: $response"
if [ "$response" = "200" ]; then
  echo "✅ Web UI 可访问"
  head -3 /tmp/curl_test.html
else
  echo "⚠️ Web UI 状态: $response"
fi

echo ""
echo "=== 本地HTTP测试 (localhost:8001) ==="
curl -s -m 2 http://localhost:8001/docs > /dev/null 2>&1 && echo "✅ QA API 可访问" || echo "⚠️ QA API 状态: 无法连接"

echo ""
echo "=== 监听端口检查 ==="
ss -tlnp 2>/dev/null | grep -E "9000|8001|8003|8002|8004|8005|8006" || netstat -tlnp 2>/dev/null | grep -E "9000|8001|8003|8002|8004|8005|8006" || echo "无法获取端口信息"

echo ""
echo "=== Docker网络检查 ==="
docker network ls
docker inspect aicommonplatform_ai_net 2>/dev/null | grep -A 5 "Containers" || echo "网络检查: 可能存在问题"

EOF
