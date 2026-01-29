#!/bin/bash

# 使用buildx为AMD64构建并直接保存镜像

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

echo "🔨 构建AMD64镜像并上传"
echo "=================================================="
echo ""

mkdir -p "$TEMP_DIR"

# 第1步：为每个服务构建AMD64镜像
echo "📦 步骤1: 构建AMD64镜像..."
for service in "${SERVICES[@]}"; do
  echo "  🏗️  $service..."
  
  # 使用buildx构建并导出为tar
  docker buildx build \
    --platform linux/amd64 \
    --output "type=oci,dest=$TEMP_DIR/${service}-amd64" \
    -f "./services/${service}/Dockerfile.lite" \
    "./services/${service}" \
    --progress=plain 2>&1 | grep -E "DONE|ERROR" || true
  
  # 将OCI格式转为Docker tar格式
  echo "    转换格式..."
  # 使用skopeo转换（如果可用）或用其他方法
done

echo ""
echo "⚠️  使用docker save方式重新构建..."
echo ""

# 重新用标准docker build方式为AMD64构建
for service in "${SERVICES[@]}"; do
  echo "  🏗️  构建 $service (AMD64)..."
  
  # 判断使用哪个Dockerfile
  if [ "$service" = "web_ui" ]; then
    dockerfile="./services/${service}/Dockerfile"
  else
    dockerfile="./services/${service}/Dockerfile.lite"
  fi
  
  # 使用buildx构建AMD64镜像
  docker buildx build \
    --platform linux/amd64 \
    --load \
    -t "aicommonplatform-${service}:amd64" \
    -f "$dockerfile" \
    "./services/${service}" 2>&1 | tail -5
  
  echo "  💾 导出 $service..."
  docker save "aicommonplatform-${service}:amd64" -o "$TEMP_DIR/${service}-amd64.tar"
  size=$(du -h "$TEMP_DIR/${service}-amd64.tar" | cut -f1)
  echo "    ✓ $size"
done

echo ""
echo "✅ 所有AMD64镜像已构建"
echo ""

# 第2步：上传到远程
echo "📤 步骤2: 上传镜像到远程服务器..."
for tar_file in "$TEMP_DIR"/*.tar; do
  filename=$(basename "$tar_file")
  size=$(du -h "$tar_file" | cut -f1)
  echo "  ⏳ $filename ($size)..."
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 22 \
    "$tar_file" "root@$REMOTE_IP:/root/aicommonplatform/images/" 2>/dev/null
done

echo "✅ 上传完成"
echo ""

# 第3步：远程导入并启动
echo "🐳 步骤3: 远程导入并启动..."
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$REMOTE_IP 2>/dev/null << 'REMOTE'
cd /root/aicommonplatform

# 停止现有容器
docker-compose -f docker-compose.yml down 2>/dev/null || true

# 删除旧镜像
docker rmi $(docker images | grep "aicommonplatform" | grep -v "amd64" | awk '{print $3}') 2>/dev/null || true

# 导入新镜像
cd images
echo "导入AMD64镜像..."
for tar_file in *-amd64.tar; do
  echo "  ⏳ $tar_file"
  docker load -i "$tar_file" > /dev/null 2>&1
done

cd /root/aicommonplatform

# 更新docker-compose.yml配置使用amd64镜像
echo "更新配置..."
cat > docker-compose.yml << 'COMPOSE'
version: '3.8'

services:
  web_ui:
    image: aicommonplatform-web_ui:amd64
    container_name: ai_web_ui
    ports:
      - "9000:3000"
    environment:
      SERVICE_NAME: web_ui
      QA_SERVICE_URL: http://qa_entry:8000
      PROMPT_SERVICE_URL: http://prompt_service:8000
      RAG_SERVICE_URL: http://rag_service:8000
      AGENT_SERVICE_URL: http://agent_service:8000
      INTEGRATION_SERVICE_URL: http://integration:8000
      LLM_SERVICE_URL: http://llm_service:8000
      LOG_LEVEL: INFO
      DB_PATH: /app/data/web_ui.db
    volumes:
      - ./data/web_ui:/app/data
    networks:
      - ai_net
    restart: unless-stopped
    depends_on:
      - qa_entry

  qa_entry:
    image: aicommonplatform-qa_entry:amd64
    container_name: ai_qa_entry
    ports:
      - "8001:8000"
    environment:
      SERVICE_NAME: qa_entry
      LITE_MODE: "true"
      PROMPT_SERVICE_URL: http://prompt_service:8000
      RAG_SERVICE_URL: http://rag_service:8000
      AGENT_SERVICE_URL: http://agent_service:8000
      LLM_SERVICE_URL: http://llm_service:8000
      LOG_LEVEL: INFO
    networks:
      - ai_net
    restart: unless-stopped
    depends_on:
      - prompt_service
      - rag_service
      - llm_service

  prompt_service:
    image: aicommonplatform-prompt_service:amd64
    container_name: ai_prompt_service
    ports:
      - "8002:8000"
    environment:
      SERVICE_NAME: prompt_service
      LITE_MODE: "true"
      LOG_LEVEL: INFO
    networks:
      - ai_net
    restart: unless-stopped

  rag_service:
    image: aicommonplatform-rag_service:amd64
    container_name: ai_rag_service
    ports:
      - "8003:8000"
    environment:
      SERVICE_NAME: rag_service
      LITE_MODE: "true"
      LOG_LEVEL: INFO
    volumes:
      - ./data/documents:/app/data
    networks:
      - ai_net
    restart: unless-stopped

  agent_service:
    image: aicommonplatform-agent_service:amd64
    container_name: ai_agent_service
    ports:
      - "8004:8000"
    environment:
      SERVICE_NAME: agent_service
      LITE_MODE: "true"
      LOG_LEVEL: INFO
    networks:
      - ai_net
    restart: unless-stopped

  integration:
    image: aicommonplatform-integration:amd64
    container_name: ai_integration
    ports:
      - "8005:8000"
    environment:
      SERVICE_NAME: integration
      LITE_MODE: "true"
      LOG_LEVEL: INFO
    networks:
      - ai_net
    restart: unless-stopped

  llm_service:
    image: aicommonplatform-llm_service:amd64
    container_name: ai_llm_service
    ports:
      - "8006:8000"
    environment:
      SERVICE_NAME: llm_service
      LITE_MODE: "true"
      LOG_LEVEL: INFO
      LLM_PROVIDER: ${LLM_PROVIDER:-openai}
      OPENAI_API_KEY: ${OPENAI_API_KEY:-}
      OPENAI_API_URL: ${OPENAI_API_URL:-https://api.openai.com/v1}
      CHATANYWHERE_API_KEY: ${CHATANYWHERE_API_KEY:-}
      CHATANYWHERE_API_URL: ${CHATANYWHERE_API_URL:-https://api.chatanywhere.com.cn/v1}
      LLM_MODEL: ${LLM_MODEL:-gpt-3.5-turbo}
    networks:
      - ai_net
    restart: unless-stopped

networks:
  ai_net:
    driver: bridge
COMPOSE

# 启动容器
echo "启动容器..."
docker-compose -f docker-compose.yml up -d 2>&1 | tail -10

sleep 5

echo ""
echo "✅ 容器运行状态:"
docker ps --filter "name=ai_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

REMOTE

echo ""
echo "清理本地临时文件..."
rm -rf "$TEMP_DIR"

echo ""
echo "=================================================="
echo "✅ 部署完成！"
echo "=================================================="
echo ""
echo "🌐 访问地址:"
echo "   Web UI: http://$REMOTE_IP:9000"
echo "   QA API: http://$REMOTE_IP:8001/docs"
echo "   RAG Service: http://$REMOTE_IP:8003/docs"
echo ""
