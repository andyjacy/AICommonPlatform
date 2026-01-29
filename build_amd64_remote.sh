#!/bin/bash

# 在远程AMD64服务器上构建镜像的脚本

echo "🔨 准备在远程服务器上构建AMD64镜像..."
echo ""

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"

# 上传所有服务的Dockerfile和源代码
echo "📤 步骤1: 上传源代码到远程服务器..."

SERVICES=(
  "web_ui"
  "qa_entry"
  "rag_service"
  "prompt_service"
  "agent_service"
  "integration"
  "llm_service"
)

PROJECT_PATH="/Users/zhao_/Documents/PRC/AI实践/AICommonPlatform/services"

for service in "${SERVICES[@]}"; do
  echo "  ⏳ 上传 $service..."
  sshpass -p "$PASSWORD" scp -r -o ConnectTimeout=10 "$PROJECT_PATH/$service" \
    root@$REMOTE_IP:/root/build/ 2>/dev/null
done

echo "✅ 源代码已上传"
echo ""

# 在远程服务器构建镜像
echo "🔨 步骤2: 在远程服务器构建镜像..."

sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 root@$REMOTE_IP 2>&1 << 'REMOTE'

cd /root/build

# 构建Web UI
echo "  [1/7] 构建 web_ui..."
cd web_ui
docker build -t aicommonplatform-web_ui:latest -f Dockerfile . > /tmp/web_ui_build.log 2>&1
if [ $? -eq 0 ]; then
  echo "  ✅ web_ui 构建成功"
else
  echo "  ❌ web_ui 构建失败"
  tail -20 /tmp/web_ui_build.log
fi

# 构建其他服务
services=(
  "qa_entry:Dockerfile.lite"
  "rag_service:Dockerfile.lite"
  "prompt_service:Dockerfile.lite"
  "agent_service:Dockerfile.lite"
  "integration:Dockerfile.lite"
  "llm_service:Dockerfile.lite"
)

count=2
for service_info in "${services[@]}"; do
  IFS=: read service dockerfile <<< "$service_info"
  echo "  [$count/7] 构建 $service..."
  cd /root/build/$service
  docker build -t aicommonplatform-$service:latest -f $dockerfile . > /tmp/${service}_build.log 2>&1
  if [ $? -eq 0 ]; then
    echo "  ✅ $service 构建成功"
  else
    echo "  ❌ $service 构建失败"
  fi
  ((count++))
done

echo ""
echo "✅ 所有镜像构建完成"

REMOTE

echo ""

# 验证镜像
echo "✅ 步骤3: 验证镜像架构..."

sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 root@$REMOTE_IP << 'VERIFY' 2>&1 | head -20

echo "已构建的镜像:"
docker images | grep aicommonplatform

echo ""
echo "验证架构 (应该显示 amd64):"
docker inspect aicommonplatform-web_ui:latest | grep -A 2 '"Architecture"'

VERIFY

echo ""
echo "🚀 步骤4: 重启容器..."

sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 root@$REMOTE_IP << 'RESTART' 2>&1 | tail -20

cd /root/aicommonplatform

# 停止旧容器
docker-compose -f docker-compose.yml stop 2>/dev/null || true
docker-compose -f docker-compose.yml rm -f 2>/dev/null || true

# 启动新容器
docker-compose -f docker-compose.yml up -d

# 等待启动
sleep 5

# 检查状态
echo ""
echo "容器状态:"
docker ps --filter "name=ai_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

RESTART

echo ""
echo "=========================================="
echo "✅ 构建和部署完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  Web UI: http://47.100.35.44:9000"
echo "  QA API: http://47.100.35.44:8001"
echo ""
