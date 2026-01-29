#!/bin/bash
set -e

REMOTE_IP="47.100.35.44"
REMOTE_USER="root"
REMOTE_PORT="22"
REMOTE_PATH="/root/aicommonplatform"
PASSWORD="${1:-65,UaTzA\$9kAsny}"

IMAGES=(
  "aicommonplatform-web_ui:latest"
  "aicommonplatform-qa_entry:latest"
  "aicommonplatform-rag_service:latest"
  "aicommonplatform-llm_service:latest"
  "aicommonplatform-agent_service:latest"
  "aicommonplatform-prompt_service:latest"
  "aicommonplatform-integration:latest"
)

echo "=========================================="
echo "🚀 一键部署到阿里云"
echo "=========================================="
echo "目标: $REMOTE_IP (Docker 26.1.3)"
echo ""

# 检查sshpass
if ! command -v sshpass &> /dev/null; then
  echo "📦 安装sshpass..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install sshpass >/dev/null 2>&1
  fi
fi

# 第1步：导出镜像
echo "📦 步骤1: 准备镜像..."
TEMP_DIR="/tmp/docker-deploy-$$"
mkdir -p "$TEMP_DIR"

for image in "${IMAGES[@]}"; do
  echo "  ⏳ $image"
  tar_name="${image//:/-}.tar"
  docker save "$image" -o "$TEMP_DIR/$tar_name"
done
echo "✅ 镜像已导出"
echo ""

# 第2步：初始化远程环境
echo "🔗 步骤2: 初始化远程环境..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $REMOTE_PORT "$REMOTE_USER@$REMOTE_IP" << 'REMOTE_INIT' 2>/dev/null
mkdir -p /root/aicommonplatform/images
mkdir -p /root/aicommonplatform/data/web_ui
mkdir -p /root/aicommonplatform/data/documents
echo "✅ 远程目录已创建"
REMOTE_INIT

# 第3步：上传镜像
echo "📤 步骤3: 上传镜像..."
for tar_file in "$TEMP_DIR"/*.tar; do
  filename=$(basename "$tar_file")
  echo "  ⏳ $filename"
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $REMOTE_PORT "$tar_file" "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/images/" 2>/dev/null
done
echo "✅ 镜像已上传"
echo ""

# 第4步：上传配置文件
echo "📁 步骤4: 上传配置..."
PROJECT_PATH="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$PROJECT_PATH/docker-compose.remote.yml" ]; then
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $REMOTE_PORT "$PROJECT_PATH/docker-compose.remote.yml" "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/docker-compose.yml" 2>/dev/null
  echo "✅ 配置已上传"
fi
echo ""

# 第5步：导入镜像并启动
echo "🐳 步骤5: 导入镜像并启动..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $REMOTE_PORT "$REMOTE_USER@$REMOTE_IP" 2>/dev/null << 'REMOTE_DEPLOY'
cd /root/aicommonplatform/images
echo "  导入镜像..."
for tar_file in *.tar; do
  docker load -i "$tar_file" > /dev/null 2>&1
done
echo "  ✓ 镜像已导入"

cd /root/aicommonplatform
echo "  启动服务..."
docker-compose -f docker-compose.yml up -d > /dev/null 2>&1
sleep 2

echo "  容器状态:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
REMOTE_DEPLOY

# 清理
rm -rf "$TEMP_DIR"

echo ""
echo "=========================================="
echo "✅ 部署完成"
echo "=========================================="
echo ""
echo "📋 服务信息:"
echo "  Web UI:  http://$REMOTE_IP:3000"
echo "  QA:      http://$REMOTE_IP:8001"
echo "  RAG:     http://$REMOTE_IP:8003"
echo ""
echo "🔍 SSH连接:"
echo "  ssh root@$REMOTE_IP"
echo ""
echo "📊 查看日志:"
echo "  docker logs -f ai_web_ui"
echo ""
