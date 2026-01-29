#!/bin/bash

# 在阿里云服务器上运行此脚本
# 下载并导入本地HTTP服务器上的AMD64镜像

HTTP_URL="http://192.168.176.173:8899"
IMAGES_DIR="/root/aicommonplatform/images"

echo "📥 开始从HTTP服务器下载镜像..."
echo "=================================================="
echo ""

mkdir -p "$IMAGES_DIR"
cd "$IMAGES_DIR"

# 要下载的镜像列表
images=(
  "agent_service:amd64:amd64.tar"
  "integration:amd64:amd64.tar"
  "llm_service:amd64:amd64.tar"
  "prompt_service:amd64:amd64.tar"
  "qa_entry:amd64:amd64.tar"
  "rag_service:amd64:amd64.tar"
  "web_ui:amd64:amd64.tar"
)

# 并行下载所有镜像
echo "⏳ 并行下载中..."
for image in "${images[@]}"; do
  wget "$HTTP_URL/$image" -O "$image" > /tmp/wget_$image.log 2>&1 &
done

# 等待所有下载完成
wait
echo "✅ 下载完成"
echo ""

# 列出下载的文件
echo "📋 下载的文件:"
ls -lh *.tar | awk '{printf "  %-40s %8s\n", $9, $5}'
echo ""

# 停止现有容器
echo "⏸️  停止现有容器..."
cd /root/aicommonplatform
docker-compose -f docker-compose.yml down 2>/dev/null || true
sleep 2

# 删除旧镜像
echo "🗑️  清理旧镜像..."
docker rmi $(docker images | grep aicommonplatform | awk '{print $3}' | sort -u) 2>/dev/null || true
echo "✅ 旧镜像已清理"
echo ""

# 导入新镜像
echo "📥 导入AMD64镜像..."
cd "$IMAGES_DIR"
for tar_file in *.tar; do
  echo "  导入 $tar_file..."
  docker load -i "$tar_file" > /dev/null 2>&1 && echo "    ✓" || echo "    ✗ 失败"
done
echo "✅ 镜像导入完成"
echo ""

# 启动容器
echo "🚀 启动容器..."
cd /root/aicommonplatform
docker-compose -f docker-compose.yml up -d 2>&1 | tail -5

sleep 3
echo ""
echo "📊 容器状态:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "ai_|ticket"

echo ""
echo "✅ 部署完成！"
echo ""
echo "🧪 测试Web UI:"
echo "  curl http://localhost:9000"
echo "  或者访问: http://47.100.35.44:9000"
