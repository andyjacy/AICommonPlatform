#!/bin/bash

# 在本地构建轻量化AMD64镜像，然后上传到远程部署

set -e

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"
TEMP_DIR="/tmp/amd64-lite-$$"

echo "🚀 构建轻量化AMD64镜像并部署到远程"
echo "=================================================="
echo ""

mkdir -p "$TEMP_DIR"

# 第1步：本地构建轻量化AMD64镜像
echo "📦 步骤1: 构建轻量化AMD64镜像..."
cd /Users/zhao_/Documents/PRC/AI实践/AICommonPlatform

# 用buildx构建所有镜像为AMD64
docker buildx build \
  --platform linux/amd64 \
  -f services/web_ui/Dockerfile \
  -t aicommonplatform-web_ui:amd64 \
  --load \
  services/web_ui 2>&1 | grep -E "DONE|error" || echo "✓"

for service in qa_entry rag_service llm_service agent_service prompt_service integration; do
  echo "  🏗️  构建 $service..."
  docker buildx build \
    --platform linux/amd64 \
    -f "services/${service}/Dockerfile.lite" \
    -t "aicommonplatform-${service}:amd64" \
    --load \
    "services/${service}" 2>&1 | grep -E "DONE|error" || echo "✓"
done

echo "✅ 所有AMD64镜像构建完成"
echo ""

# 第2步：导出镜像
echo "💾 步骤2: 导出镜像为tar..."
images=(
  "aicommonplatform-web_ui:amd64"
  "aicommonplatform-qa_entry:amd64"
  "aicommonplatform-rag_service:amd64"
  "aicommonplatform-llm_service:amd64"
  "aicommonplatform-agent_service:amd64"
  "aicommonplatform-prompt_service:amd64"
  "aicommonplatform-integration:amd64"
)

for image in "${images[@]}"; do
  echo "  ⏳ $image..."
  docker save "$image" -o "$TEMP_DIR/${image##*-}.tar"
done

echo "✅ 镜像导出完成"
echo ""

# 第3步：上传到远程
echo "📤 步骤3: 上传到远程服务器..."
for tar_file in "$TEMP_DIR"/*.tar; do
  filename=$(basename "$tar_file")
  size=$(du -h "$tar_file" | cut -f1)
  echo "  ⏳ $filename ($size)..."
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 22 \
    "$tar_file" "root@$REMOTE_IP:/root/aicommonplatform/images/" 2>/dev/null
done

echo "✅ 上传完成"
echo ""

# 第4步：远程导入并启动
echo "🐳 步骤4: 远程导入镜像并启动..."
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$REMOTE_IP 2>/dev/null << 'REMOTE'
cd /root/aicommonplatform

# 停止现有容器
echo "  停止现有容器..."
docker-compose -f docker-compose.yml down 2>/dev/null || true

# 删除旧镜像
echo "  清理旧镜像..."
docker rmi $(docker images | grep aicommonplatform | grep -v amd64 | awk '{print $3}') 2>/dev/null || true

# 导入新镜像
echo "  导入AMD64镜像..."
cd images
for tar_file in *.tar; do
  docker load -i "$tar_file" > /dev/null 2>&1
done

# 返回目录
cd /root/aicommonplatform

# 启动容器
echo "  启动容器..."
docker-compose -f docker-compose.yml up -d 2>&1 | grep -E "Creating|Starting|Created"

sleep 5

echo ""
echo "✅ 容器状态:"
docker ps --filter "name=ai_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

REMOTE

# 清理本地临时文件
rm -rf "$TEMP_DIR"

echo ""
echo "=================================================="
echo "✅ 部署完成！"
echo "=================================================="
echo ""
echo "🌐 访问地址:"
echo "   Web UI:     http://$REMOTE_IP:9000"
echo "   QA API:     http://$REMOTE_IP:8001"
echo "   QA文档:     http://$REMOTE_IP:8001/docs"
echo "   RAG Service: http://$REMOTE_IP:8003"
echo ""
