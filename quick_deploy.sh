#!/bin/bash

#########################################################################
# 快速部署脚本：一键部署本地Docker镜像到阿里云服务器
# 用法: ./quick_deploy.sh
# 或者: ./quick_deploy.sh your_password
#########################################################################

set -e

# 配置信息
REMOTE_IP="47.100.35.44"
REMOTE_USER="root"
REMOTE_PORT="22"
REMOTE_PATH="/root/aicommonplatform"
PASSWORD="${1:-65,UaTzA\$9kAsny}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 一键部署到阿里云${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "目标服务器: ${YELLOW}$REMOTE_IP${NC}"
echo -e "用户: ${YELLOW}$REMOTE_USER${NC}"
echo -e "部署路径: ${YELLOW}$REMOTE_PATH${NC}"
echo ""

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

# 检查 sshpass
if ! command -v sshpass &> /dev/null; then
  echo -e "${YELLOW}📦 正在安装 sshpass...${NC}"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install sshpass 2>/dev/null || {
      echo -e "${RED}❌ 无法安装sshpass，请手动安装: brew install sshpass${NC}"
      exit 1
    }
  else
    sudo apt-get install -y sshpass >/dev/null 2>&1 || {
      echo -e "${RED}❌ 无法安装sshpass，请手动安装${NC}"
      exit 1
    }
  fi
  echo -e "${GREEN}✓ sshpass 已安装${NC}"
fi

# 第1步：导出镜像
echo -e "${BLUE}📦 步骤 1/5: 准备镜像文件...${NC}"
TEMP_DIR="/tmp/docker-deploy-$$"
mkdir -p "$TEMP_DIR"

image_count=0
for image in "${IMAGES[@]}"; do
  echo -e "  ${YELLOW}⏳${NC} 导出 $image..."
  tar_name="${image//:/-}.tar"
  docker save "$image" -o "$TEMP_DIR/$tar_name"
  size=$(du -h "$TEMP_DIR/$tar_name" | cut -f1)
  echo -e "    ${GREEN}✓${NC} 大小: $size"
  ((image_count++))
done

echo -e "${GREEN}✅ 已导出 $image_count 个镜像${NC}"
echo ""

# 第2步：初始化远程环境
echo -e "${BLUE}🔗 步骤 2/5: 连接服务器并初始化环境...${NC}"

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $REMOTE_PORT "$REMOTE_USER@$REMOTE_IP" << 'REMOTE_INIT' 2>/dev/null || {
  echo -e "${RED}❌ 无法连接到远程服务器 $REMOTE_IP${NC}"
  echo -e "${RED}   请检查: IP地址、用户名、密码是否正确${NC}"
  exit 1
}
set -e
mkdir -p /root/aicommonplatform/images
mkdir -p /root/aicommonplatform/data/web_ui
mkdir -p /root/aicommonplatform/data/documents
echo "✓ 远程目录初始化完成"
DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+')
echo "✓ Docker版本: $DOCKER_VERSION"
REMOTE_INIT

echo -e "${GREEN}✅ 服务器初始化完成${NC}"
echo ""

# 第3步：上传镜像
echo -e "${BLUE}📤 步骤 3/5: 上传镜像到服务器...${NC}"

total_files=$(ls "$TEMP_DIR"/*.tar | wc -l)
current_file=1

for tar_file in "$TEMP_DIR"/*.tar; do
  filename=$(basename "$tar_file")
  file_size=$(du -h "$tar_file" | cut -f1)
  echo -e "  ${YELLOW}[$current_file/$total_files]${NC} 上传 $filename ($file_size)..."
  
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $REMOTE_PORT "$tar_file" "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/images/" 2>/dev/null || {
    echo -e "${RED}❌ 上传 $filename 失败${NC}"
    exit 1
  }
  
  ((current_file++))
done

echo -e "${GREEN}✅ 所有镜像上传完成${NC}"
echo ""

# 第4步：上传docker-compose文件
echo -e "${BLUE}📁 步骤 4/5: 上传配置文件...${NC}"

PROJECT_PATH="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$PROJECT_PATH/docker-compose.remote.yml" ]; then
  echo -e "  ${YELLOW}⏳${NC} 上传 docker-compose.yml..."
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $REMOTE_PORT "$PROJECT_PATH/docker-compose.remote.yml" "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/docker-compose.yml" 2>/dev/null || {
    echo -e "${RED}❌ 上传compose文件失败${NC}"
    exit 1
  }
  echo -e "  ${GREEN}✓${NC} 配置文件上传完成"
else
  echo -e "${YELLOW}⚠️  找不到 docker-compose.remote.yml${NC}"
fi

echo -e "${GREEN}✅ 配置文件准备完成${NC}"
echo ""

# 第5步：导入镜像并启动服务
echo -e "${BLUE}🐳 步骤 5/5: 导入镜像并启动服务...${NC}"

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $REMOTE_PORT "$REMOTE_USER@$REMOTE_IP" << 'REMOTE_DEPLOY' 2>/dev/null
set -e
cd /root/aicommonplatform/images

echo "  导入Docker镜像..."
count=1
total=$(ls *.tar 2>/dev/null | wc -l)

for tar_file in *.tar; do
  echo "    [$count/$total] $tar_file..."
  docker load -i "$tar_file" > /dev/null 2>&1
  ((count++))
done

echo "  ✓ 所有镜像导入完成"

# 验证镜像
echo ""
echo "  已加载的镜像:"
docker images | grep aicommonplatform | awk '{printf "    • %s:%s (%s)\n", $1, $2, $7}'

# 启动服务
cd /root/aicommonplatform

echo ""
echo "  启动容器服务..."
docker-compose -f docker-compose.yml up -d 2>&1 | tail -20

echo "  等待服务启动..."
sleep 3

# 获取容器状态
echo ""
echo "  容器运行状态:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "  ✓ 服务启动完成"

REMOTE_DEPLOY

# 清理临时文件
echo ""
echo -e "${BLUE}🧹 清理临时文件...${NC}"
rm -rf "$TEMP_DIR"
echo -e "${GREEN}✅ 临时文件已清理${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📋 服务信息:${NC}"
echo -e "  ${YELLOW}Web UI:${NC}        http://$REMOTE_IP:3000"
echo -e "  ${YELLOW}QA Entry:${NC}      http://$REMOTE_IP:8001/docs"
echo -e "  ${YELLOW}RAG Service:${NC}   http://$REMOTE_IP:8003/docs"
echo ""
echo -e "${BLUE}🔍 远程操作:${NC}"
echo -e "  ${YELLOW}SSH 连接:${NC}      ssh root@$REMOTE_IP"
echo -e "  ${YELLOW}查看日志:${NC}      docker logs -f ai_web_ui"
echo -e "  ${YELLOW}容器状态:${NC}      docker ps"
echo -e "  ${YELLOW}查看compose:${NC}   cd /root/aicommonplatform && docker-compose ps"
echo ""
echo -e "${BLUE}🛑 停止服务:${NC}"
echo -e "  ${YELLOW}命令:${NC}          docker-compose -f /root/aicommonplatform/docker-compose.yml down"
echo ""
