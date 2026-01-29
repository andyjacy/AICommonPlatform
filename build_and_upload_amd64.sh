#!/bin/bash

# 本地构建AMD64镜像并上传远程

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"
LOCAL_PATH="/Users/zhao_/Documents/PRC/AI实践/AICommonPlatform"
EXPORT_DIR="/tmp/amd64_images"

echo "🔄 本地构建AMD64镜像 → 上传 → 远程启动"
echo "=================================================="
echo ""

# 清理旧的导出目录
rm -rf "$EXPORT_DIR"
mkdir -p "$EXPORT_DIR"

# 第1步：本地构建AMD64镜像
echo "🏗️  步骤1: 本地构建AMD64镜像..."
cd "$LOCAL_PATH"

# 构建web_ui
echo "  📦 构建 web_ui..."
docker buildx build \
  --platform linux/amd64 \
  -f services/web_ui/Dockerfile \
  -t aicommonplatform-web_ui:amd64 \
  --output type=docker \
  services/web_ui > /dev/null 2>&1 && echo "    ✓ 完成" || echo "    ✗ 失败"

# 构建其他服务
for service in qa_entry rag_service llm_service agent_service prompt_service integration; do
  echo "  📦 构建 $service..."
  if [ -f "services/${service}/Dockerfile.lite" ]; then
    docker buildx build \
      --platform linux/amd64 \
      -f "services/${service}/Dockerfile.lite" \
      -t "aicommonplatform-${service}:amd64" \
      --output type=docker \
      "services/${service}" > /dev/null 2>&1 && echo "    ✓ 完成" || echo "    ✗ 失败"
  else
    docker buildx build \
      --platform linux/amd64 \
      -f "services/${service}/Dockerfile" \
      -t "aicommonplatform-${service}:amd64" \
      --output type=docker \
      "services/${service}" > /dev/null 2>&1 && echo "    ✓ 完成" || echo "    ✗ 失败"
  fi
done

echo "✅ 本地镜像构建完成"
echo ""

# 第2步：导出镜像为tar
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
  filename="${image##*-}"  # 提取service名
  tar_file="$EXPORT_DIR/${filename}:amd64.tar"
  size=$(docker images --format "{{.Size}}" --filter "reference=$image" 2>/dev/null || echo "N/A")
  echo "  ⏳ $image ($size)..."
  docker save "$image" -o "$tar_file" 2>/dev/null && echo "    ✓ 导出成功" || echo "    ✗ 导出失败"
done

echo "✅ 镜像导出完成"
echo ""

# 第3步：上传到远程
echo "📤 步骤3: 上传到远程服务器..."
# 先确保远程目录存在
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$REMOTE_IP 'mkdir -p /root/aicommonplatform/images' 2>/dev/null

total_files=$(ls "$EXPORT_DIR"/*.tar 2>/dev/null | wc -l)
current=0
for tar_file in "$EXPORT_DIR"/*.tar; do
  current=$((current + 1))
  filename=$(basename "$tar_file")
  filesize=$(du -h "$tar_file" | cut -f1)
  echo "  ⏳ [$current/$total_files] $filename ($filesize)..."
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "$tar_file" "root@$REMOTE_IP:/root/aicommonplatform/images/" 2>/dev/null && echo "    ✓ 上传成功" || echo "    ✗ 上传失败"
done

echo "✅ 上传完成"
echo ""

# 第4步：远程导入镜像并启动
echo "🐳 步骤4: 远程导入镜像并启动..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$REMOTE_IP << 'REMOTE'
cd /root/aicommonplatform

# 停止现有容器
echo "  ⏸️  停止现有容器..."
docker-compose -f docker-compose.yml down 2>/dev/null || true
sleep 1

# 删除旧镜像（保留ticket-grab-app的依赖）
echo "  🗑️  清理旧镜像..."
docker rmi $(docker images | grep aicommonplatform | awk '{print $3}' | sort -u) 2>/dev/null || true

# 导入新镜像
echo "  📥 导入AMD64镜像..."
cd /root/aicommonplatform/images
for tar_file in *.tar; do
  echo "    ⏳ $tar_file..."
  docker load -i "$tar_file" > /dev/null 2>&1 && echo "      ✓" || echo "      ✗"
done

# 返回工作目录
cd /root/aicommonplatform

# 修改docker-compose，使用amd64标签
echo "  🔧 准备启动配置..."
# 备份原文件
cp docker-compose.yml docker-compose.yml.bak

# 替换镜像标签为amd64
sed 's/:latest/:amd64/g' docker-compose.yml.bak > docker-compose.yml.tmp && mv docker-compose.yml.tmp docker-compose.yml

# 启动容器
echo "  🚀 启动容器..."
docker-compose -f docker-compose.yml up -d 2>&1 | grep -E "Creating|Starting|Created|done" || echo "    启动命令已执行"

# 等待容器启动
sleep 3

# 显示状态
echo ""
echo "📊 容器状态:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "ai_|ticket"

REMOTE

echo ""
echo "✅ 部署完成！"
echo ""
echo "🧪 测试命令:"
echo "  curl http://47.100.35.44:9000      # Web UI"
echo "  curl http://47.100.35.44:8001/docs # QA Entry API"
