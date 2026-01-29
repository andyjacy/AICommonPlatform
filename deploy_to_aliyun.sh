#!/bin/bash

#########################################################################
# 部署脚本：将本地Docker镜像部署到阿里云轻量级服务器
# 目标服务器: 47.100.35.44 (Docker 26.1.3, AMD64)
#########################################################################

set -e

# 配置信息
REMOTE_IP="47.100.35.44"
REMOTE_USER="root"
REMOTE_PORT="22"
REMOTE_PATH="/root/aicommonplatform"

# 镜像列表
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
echo "🚀 阿里云部署脚本"
echo "=========================================="
echo "目标服务器: $REMOTE_IP"
echo "用户: $REMOTE_USER"
echo "部署路径: $REMOTE_PATH"
echo ""

# 第1步：创建临时目录保存镜像
echo "📦 步骤 1/5: 准备镜像文件..."
TEMP_DIR="/tmp/docker-images-$$"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# 导出所有镜像
for image in "${IMAGES[@]}"; do
  echo "  ⏳ 导出 $image..."
  docker save "$image" -o "${image//:/-}.tar"
done

echo "✅ 所有镜像已导出"
echo ""

# 第2步：复制到远程服务器
echo "📤 步骤 2/5: 上传镜像到远程服务器..."
echo "  连接到 $REMOTE_IP..."

# 首先创建远程目录
ssh -p $REMOTE_PORT "$REMOTE_USER@$REMOTE_IP" "mkdir -p $REMOTE_PATH/images && mkdir -p $REMOTE_PATH/compose" 2>/dev/null || {
  echo "❌ SSH连接失败"
  exit 1
}

# 上传镜像文件
scp -P $REMOTE_PORT -r "$TEMP_DIR"/*.tar "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/images/" 2>/dev/null || {
  echo "❌ SCP上传失败"
  exit 1
}

echo "✅ 镜像上传完成"
echo ""

# 第3步：在远程服务器上导入镜像
echo "🐳 步骤 3/5: 在远程服务器导入Docker镜像..."

ssh -p $REMOTE_PORT "$REMOTE_USER@$REMOTE_IP" << 'REMOTE_SCRIPT'
cd /root/aicommonplatform/images

# 获取镜像文件数量
total=$(ls *.tar 2>/dev/null | wc -l)
current=1

echo "  开始导入 $total 个镜像..."

for tar_file in *.tar; do
  echo "  [$current/$total] 导入 $tar_file..."
  docker load -i "$tar_file"
  ((current++))
done

echo "  ✅ 所有镜像导入完成"

# 验证导入
echo ""
echo "  已导入的镜像列表:"
docker images | grep aicommonplatform | awk '{print "    - " $1 ":" $2 " (" $7 ")"}'

REMOTE_SCRIPT

echo "✅ 远程镜像导入完成"
echo ""

# 第4步：上传docker-compose和配置文件
echo "📁 步骤 4/5: 上传docker-compose配置..."

cd /Users/zhao_/Documents/PRC/AI实践/AICommonPlatform

# 上传docker-compose.lite.yml
scp -P $REMOTE_PORT docker-compose.lite.yml "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/compose/docker-compose.yml" 2>/dev/null

# 上传requirements.txt（如果需要）
if [ -f "requirements.txt" ]; then
  scp -P $REMOTE_PORT requirements.txt "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/" 2>/dev/null
fi

echo "✅ 配置文件上传完成"
echo ""

# 第5步：启动服务
echo "🚀 步骤 5/5: 启动Docker服务..."

ssh -p $REMOTE_PORT "$REMOTE_USER@$REMOTE_IP" << 'REMOTE_SCRIPT'
cd /root/aicommonplatform/compose

# 替换compose文件中的镜像名称（如果需要）
# 启动服务
echo "  启动容器..."
docker-compose -f docker-compose.yml up -d

# 等待服务启动
echo "  等待服务初始化..."
sleep 5

# 获取容器状态
echo ""
echo "  容器运行状态:"
docker ps -a --filter "label=com.docker.compose.project" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

REMOTE_SCRIPT

echo "✅ 服务启动完成"
echo ""

# 清理临时文件
echo "🧹 清理临时文件..."
rm -rf "$TEMP_DIR"

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📋 服务器信息："
echo "  地址: $REMOTE_IP"
echo "  Web UI: http://$REMOTE_IP:3000"
echo ""
echo "🔍 查看日志:"
echo "  ssh root@$REMOTE_IP"
echo "  cd /root/aicommonplatform/compose"
echo "  docker-compose logs -f"
echo ""
echo "🛑 停止服务:"
echo "  docker-compose -f /root/aicommonplatform/compose/docker-compose.yml down"
echo ""
