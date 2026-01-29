#!/bin/bash

# 在本地构建AMD64镜像并上传到远程

set -e

SERVICES=(
  "web_ui"
  "qa_entry"
  "rag_service"
  "llm_service"
  "agent_service"
  "prompt_service"
  "integration"
)

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"
TEMP_DIR="/tmp/amd64-images-$$"

echo "🔨 构建AMD64镜像"
echo "=================================================="
echo ""

# 第1步：构建所有AMD64镜像
echo "📦 步骤1: 本地构建AMD64镜像..."
mkdir -p "$TEMP_DIR"

for service in "${SERVICES[@]}"; do
  echo "  🏗️  构建 $service..."
  docker buildx build \
    --platform linux/amd64 \
    --output type=docker \
    -t "aicommonplatform-${service}:amd64" \
    -f "./services/${service}/Dockerfile.lite" \
    "./services/${service}" 2>&1 | grep -E "Building|loaded|Digest" || true
done

echo "✅ 所有AMD64镜像已构建"
echo ""

# 第2步：导出镜像
echo "💾 步骤2: 导出镜像..."
for service in "${SERVICES[@]}"; do
  tar_name="${service}-amd64.tar"
  echo "  ⏳ 导出 $tar_name..."
  docker save "aicommonplatform-${service}:amd64" -o "$TEMP_DIR/$tar_name"
  size=$(du -h "$TEMP_DIR/$tar_name" | cut -f1)
  echo "    ✓ $size"
done

echo "✅ 镜像导出完成"
echo ""

# 第3步：上传镜像
echo "📤 步骤3: 上传到远程服务器..."
echo "  连接到 $REMOTE_IP..."

for tar_file in "$TEMP_DIR"/*.tar; do
  filename=$(basename "$tar_file")
  echo "  ⏳ 上传 $filename..."
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 22 \
    "$tar_file" "root@$REMOTE_IP:/root/aicommonplatform/images/" 2>/dev/null
done

echo "✅ 镜像上传完成"
echo ""

# 第4步：远程导入并启动
echo "🐳 步骤4: 远程导入镜像并启动..."
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$REMOTE_IP 2>/dev/null << 'REMOTE'
cd /root/aicommonplatform/images

echo "  导入AMD64镜像..."
for tar_file in *-amd64.tar; do
  echo "    ⏳ $tar_file"
  docker load -i "$tar_file" > /dev/null 2>&1
done

echo "  ✓ 镜像导入完成"
echo ""

# 停止旧容器
cd /root/aicommonplatform
docker-compose -f docker-compose.yml stop 2>/dev/null || true
docker-compose -f docker-compose.yml rm -f 2>/dev/null || true

# 修改docker-compose.yml使用amd64镜像
echo "  修改配置文件..."
sed -i 's/aicommonplatform-\([^:]*\):latest/aicommonplatform-\1:amd64/g' docker-compose.yml

# 启动容器
echo "  启动容器..."
docker-compose -f docker-compose.yml up -d 2>&1 | grep -E "Creating|Starting"

sleep 5

echo ""
echo "  容器状态:"
docker ps --filter "name=ai_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

REMOTE

echo ""
echo "✅ 部署完成！"
echo ""

# 清理
rm -rf "$TEMP_DIR"

echo "🌐 访问地址:"
echo "   Web UI: http://$REMOTE_IP:9000"
echo "   QA API: http://$REMOTE_IP:8001"
