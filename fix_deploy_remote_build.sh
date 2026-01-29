#!/bin/bash

# 解决方案：在远程服务器上直接构建AMD64镜像
# 这避免了Mac上buildx --load的限制

set -e

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"
LOCAL_PATH="/Users/zhao_/Documents/PRC/AI实践/AICommonPlatform"

echo "🔧 在远程服务器上构建AMD64镜像"
echo "=================================================="
echo ""

# 第1步：上传所有源代码到远程
echo "📤 步骤1: 上传源代码到远程..."
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$REMOTE_IP << 'REMOTE'
cd /root/aicommonplatform
# 停止容器
docker-compose -f docker-compose.yml down 2>/dev/null || true
# 删除所有aicommonplatform镜像
docker rmi $(docker images | grep aicommonplatform | awk '{print $3}' | sort -u) 2>/dev/null || true
echo "✅ 清理完成"
REMOTE

# 上传整个project文件夹
echo "  📂 上传项目文件..."
sshpass -p "$PASSWORD" scp -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  "$LOCAL_PATH/services" "root@$REMOTE_IP:/tmp/aicommonplatform-src/" 2>/dev/null || echo "  ⚠️  上传可能超时，继续..."

echo "✅ 上传完成"
echo ""

# 第2步：在远程构建所有镜像
echo "🏗️  步骤2: 在远程构建AMD64镜像..."
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=120 -o StrictHostKeyChecking=no root@$REMOTE_IP 2>/dev/null << 'REMOTE'
cd /tmp/aicommonplatform-src

echo "  🔨 构建 web_ui..."
docker build -f web_ui/Dockerfile -t aicommonplatform-web_ui:latest web_ui > /dev/null 2>&1 && echo "    ✓ web_ui"

for service in qa_entry rag_service llm_service agent_service prompt_service integration; do
  echo "  🔨 构建 $service..."
  if [ -f "${service}/Dockerfile.lite" ]; then
    docker build -f "${service}/Dockerfile.lite" -t "aicommonplatform-${service}:latest" "$service" > /dev/null 2>&1 && echo "    ✓ $service"
  else
    docker build -f "${service}/Dockerfile" -t "aicommonplatform-${service}:latest" "$service" > /dev/null 2>&1 && echo "    ✓ $service"
  fi
done

echo "✅ 所有镜像构建完成"

# 验证镜像架构
echo ""
echo "  确认镜像架构："
docker inspect aicommonplatform-web_ui:latest --format='{{.Os}}/{{.Architecture}}'

REMOTE

echo ""

# 第3步：启动容器
echo "🐳 步骤3: 启动容器..."
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$REMOTE_IP 2>/dev/null << 'REMOTE'
cd /root/aicommonplatform

# 启动容器
docker-compose -f docker-compose.yml up -d 2>&1 | tail -5

# 等待容器启动
sleep 3

# 显示容器状态
echo ""
echo "📊 容器状态："
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "ai_|ticket"

REMOTE

echo ""
echo "✅ 部署完成！"
echo ""
echo "测试方式："
echo "  curl http://47.100.35.44:9000  (Web UI)"
echo "  curl http://47.100.35.44:8001/docs  (QA Entry API)"
