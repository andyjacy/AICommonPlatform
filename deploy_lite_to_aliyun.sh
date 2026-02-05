#!/bin/bash

# ================================================================
# 轻量级AICommonPlatform部署到阿里云
# 本地构建AMD64镜像 + 初始化数据 → 上传 → 远程启动
# ================================================================

set -e

REMOTE_IP="47.100.35.44"
PASSWORD='65,UaTzA$9kAsny'
LOCAL_PATH="/Users/zhao_/Documents/PRC/AI实践/AICommonPlatform"
REMOTE_PATH="/root/aicommonplatform"
TEMP_DIR="/tmp/amd64_lite_deploy_$$"

echo "🚀 AICommonPlatform 轻量级部署到阿里云"
echo "=================================================="
echo "远程服务器: $REMOTE_IP"
echo "本地路径: $LOCAL_PATH"
echo "远程路径: $REMOTE_PATH"
echo "=================================================="
echo ""

# 创建临时目录
mkdir -p "$TEMP_DIR/images"

cd "$LOCAL_PATH"

# ==================== 第1步：构建AMD64镜像 ====================
echo "📦 步骤1: 本地构建AMD64镜像..."
echo ""

# 构建web_ui
echo "  🔧 构建 web_ui..."
docker buildx build \
  --platform linux/amd64 \
  -f services/web_ui/Dockerfile \
  -t aicommonplatform-web_ui:amd64 \
  --load \
  services/web_ui 2>&1 | tail -3
echo "    ✅ web_ui 完成"

# 构建其他服务
for service in qa_entry rag_service llm_service agent_service prompt_service integration; do
  echo "  🔧 构建 $service..."
  if [ -f "services/${service}/Dockerfile.lite" ]; then
    docker buildx build \
      --platform linux/amd64 \
      -f "services/${service}/Dockerfile.lite" \
      -t "aicommonplatform-${service}:amd64" \
      --load \
      "services/${service}" 2>&1 | tail -2
  else
    docker buildx build \
      --platform linux/amd64 \
      -f "services/${service}/Dockerfile" \
      -t "aicommonplatform-${service}:amd64" \
      --load \
      "services/${service}" 2>&1 | tail -2
  fi
  echo "    ✅ $service 完成"
done

echo ""
echo "✅ 所有AMD64镜像构建完成"
echo ""

# ==================== 第2步：导出镜像 ====================
echo "💾 步骤2: 导出镜像为tar文件..."

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
  service_name="${image%:*}"
  service_name="${service_name##*-}"
  tar_file="$TEMP_DIR/images/${service_name}.tar"
  echo "  ⏳ 导出 $image..."
  docker save "$image" -o "$tar_file"
  size=$(du -h "$tar_file" | cut -f1)
  echo "    ✅ $service_name.tar ($size)"
done

echo ""
echo "✅ 镜像导出完成"
echo ""

# ==================== 第3步：准备配置文件和数据 ====================
echo "📝 步骤3: 准备配置文件和初始化数据..."

# 复制docker-compose配置
cp "$LOCAL_PATH/docker-compose.lite.yml" "$TEMP_DIR/docker-compose.yml"

# 修改端口映射：3000 -> 9000 (适配远程服务器)
sed -i '' 's/"3000:3000"/"9000:3000"/g' "$TEMP_DIR/docker-compose.yml"

# 移除profile限制，让所有服务都启动
sed -i '' '/profiles:/d' "$TEMP_DIR/docker-compose.yml"

# 移除static挂载（远程不需要热更新，使用镜像内置的static）
sed -i '' '/services\/web_ui\/static/d' "$TEMP_DIR/docker-compose.yml"

# 从本地.env读取真实的API Key并写入docker-compose.yml
LOCAL_CHATANYWHERE_KEY=$(grep CHATANYWHERE_API_KEY "$LOCAL_PATH/.env" | tail -1 | cut -d'=' -f2)
if [ -n "$LOCAL_CHATANYWHERE_KEY" ]; then
  echo "  ✅ 检测到ChatAnywhere API Key"
  # 替换环境变量引用为真实值
  sed -i '' "s/CHATANYWHERE_API_KEY: \${CHATANYWHERE_API_KEY:-}/CHATANYWHERE_API_KEY: $LOCAL_CHATANYWHERE_KEY/" "$TEMP_DIR/docker-compose.yml"
  sed -i '' 's/LLM_PROVIDER: ${LLM_PROVIDER:-openai}/LLM_PROVIDER: chatanywhere/' "$TEMP_DIR/docker-compose.yml"
fi

# 复制数据目录（包含SQLite数据库和初始化数据）
mkdir -p "$TEMP_DIR/data"
if [ -d "$LOCAL_PATH/data/web_ui" ]; then
  cp -r "$LOCAL_PATH/data/web_ui" "$TEMP_DIR/data/"
  echo "  ✅ 复制 web_ui 数据"
fi
if [ -d "$LOCAL_PATH/data/documents" ]; then
  cp -r "$LOCAL_PATH/data/documents" "$TEMP_DIR/data/"
  echo "  ✅ 复制 documents 数据"
fi

# 创建.env文件
cat > "$TEMP_DIR/.env" << 'EOF'
# LLM配置
LLM_PROVIDER=chatanywhere
CHATANYWHERE_API_KEY=sk-xxx
CHATANYWHERE_API_URL=https://api.chatanywhere.com.cn/v1
LLM_MODEL=gpt-3.5-turbo
EOF
echo "  ✅ 创建 .env 配置"

echo ""
echo "✅ 配置文件准备完成"
echo ""

# ==================== 第4步：上传到远程服务器 ====================
echo "📤 步骤4: 上传到远程服务器..."

# 创建远程目录
echo "  📁 创建远程目录..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$REMOTE_IP << REMOTE_CMD
mkdir -p $REMOTE_PATH/images
mkdir -p $REMOTE_PATH/data/web_ui
mkdir -p $REMOTE_PATH/data/documents
REMOTE_CMD

# 上传镜像
echo "  📤 上传镜像文件..."
total=$(ls "$TEMP_DIR/images/"*.tar 2>/dev/null | wc -l)
current=0
for tar_file in "$TEMP_DIR/images/"*.tar; do
  current=$((current + 1))
  filename=$(basename "$tar_file")
  size=$(du -h "$tar_file" | cut -f1)
  echo "    [$current/$total] $filename ($size)..."
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no \
    "$tar_file" "root@$REMOTE_IP:$REMOTE_PATH/images/"
done

# 上传配置文件
echo "  📤 上传配置文件..."
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no \
  "$TEMP_DIR/docker-compose.yml" "root@$REMOTE_IP:$REMOTE_PATH/"
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no \
  "$TEMP_DIR/.env" "root@$REMOTE_IP:$REMOTE_PATH/"

# 上传数据文件
if [ -d "$TEMP_DIR/data/web_ui" ]; then
  echo "  📤 上传初始化数据..."
  sshpass -p "$PASSWORD" scp -r -o StrictHostKeyChecking=no \
    "$TEMP_DIR/data/web_ui/"* "root@$REMOTE_IP:$REMOTE_PATH/data/web_ui/" 2>/dev/null || true
fi
if [ -d "$TEMP_DIR/data/documents" ]; then
  sshpass -p "$PASSWORD" scp -r -o StrictHostKeyChecking=no \
    "$TEMP_DIR/data/documents/"* "root@$REMOTE_IP:$REMOTE_PATH/data/documents/" 2>/dev/null || true
fi

echo ""
echo "✅ 上传完成"
echo ""

# ==================== 第5步：远程导入镜像并启动 ====================
echo "🐳 步骤5: 远程导入镜像并启动服务..."

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$REMOTE_IP << 'REMOTE_SCRIPT'
cd /root/aicommonplatform

echo "  🛑 停止现有容器..."
docker-compose down 2>/dev/null || true

echo "  🗑️  清理旧镜像..."
docker rmi $(docker images | grep aicommonplatform | awk '{print $3}') 2>/dev/null || true

echo "  📥 导入AMD64镜像..."
cd images
for tar_file in *.tar; do
  echo "    导入 $tar_file..."
  docker load -i "$tar_file"
done
cd ..

echo "  🔄 重命名镜像标签..."
# 将amd64标签重命名为latest
docker tag aicommonplatform-web_ui:amd64 aicommonplatform-web_ui:latest 2>/dev/null || true
docker tag aicommonplatform-qa_entry:amd64 aicommonplatform-qa_entry:latest 2>/dev/null || true
docker tag aicommonplatform-rag_service:amd64 aicommonplatform-rag_service:latest 2>/dev/null || true
docker tag aicommonplatform-llm_service:amd64 aicommonplatform-llm_service:latest 2>/dev/null || true
docker tag aicommonplatform-agent_service:amd64 aicommonplatform-agent_service:latest 2>/dev/null || true
docker tag aicommonplatform-prompt_service:amd64 aicommonplatform-prompt_service:latest 2>/dev/null || true
docker tag aicommonplatform-integration:amd64 aicommonplatform-integration:latest 2>/dev/null || true

echo "  🚀 启动容器..."
docker-compose up -d

echo ""
echo "  ⏳ 等待服务启动..."
sleep 8

echo ""
echo "📊 容器状态:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "ai_lite|NAMES"

echo ""
echo "🔍 健康检查:"
curl -s http://localhost:9000/ > /dev/null && echo "  ✅ Web UI (9000): OK" || echo "  ❌ Web UI (9000): Failed"
curl -s http://localhost:8001/health > /dev/null && echo "  ✅ QA Entry (8001): OK" || echo "  ⚠️ QA Entry (8001): Starting..."
curl -s http://localhost:8003/health > /dev/null && echo "  ✅ RAG Service (8003): OK" || echo "  ⚠️ RAG Service (8003): Starting..."
curl -s http://localhost:8006/health > /dev/null && echo "  ✅ LLM Service (8006): OK" || echo "  ⚠️ LLM Service (8006): Starting..."

REMOTE_SCRIPT

# 清理本地临时文件
rm -rf "$TEMP_DIR"

echo ""
echo "=================================================="
echo "✅ 部署完成！"
echo "=================================================="
echo ""
echo "🌐 访问地址:"
echo "   Web UI:      http://$REMOTE_IP:9000"
echo "   QA API:      http://$REMOTE_IP:8001/docs"
echo "   RAG Service: http://$REMOTE_IP:8003/docs"
echo "   LLM Service: http://$REMOTE_IP:8006/docs"
echo ""
echo "🔧 远程管理:"
echo "   SSH登录:     ssh root@$REMOTE_IP"
echo "   查看日志:    docker-compose -f /root/aicommonplatform/docker-compose.yml logs -f"
echo "   重启服务:    docker-compose -f /root/aicommonplatform/docker-compose.yml restart"
echo ""
