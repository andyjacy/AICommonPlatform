#!/bin/bash

# 上传已导出的AMD64镜像到远程服务器

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA\$9kAsny"
EXPORT_DIR="/tmp/amd64_images"

echo "📤 上传AMD64镜像到远程..."
echo "=================================================="

# 检查导出文件是否存在
if [ ! -d "$EXPORT_DIR" ] || [ -z "$(ls $EXPORT_DIR/*.tar 2>/dev/null)" ]; then
  echo "❌ 错误: 找不到导出的镜像文件"
  echo "请先运行: bash local_build_amd64.sh"
  exit 1
fi

# 测试连接
echo "🔍 测试远程连接..."
sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$REMOTE_IP 'echo "✓ 连接成功"' || {
  echo "❌ 无法连接到 $REMOTE_IP"
  exit 1
}

echo ""
echo "📤 开始上传..."
# 确保远程目录存在
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$REMOTE_IP 'mkdir -p /root/aicommonplatform/images' 2>/dev/null

# 上传所有tar文件
total=$(ls $EXPORT_DIR/*.tar 2>/dev/null | wc -l)
current=0
for tar_file in "$EXPORT_DIR"/*.tar; do
  current=$((current + 1))
  filename=$(basename "$tar_file")
  filesize=$(du -h "$tar_file" | cut -f1)
  echo "  [$current/$total] $filename ($filesize)..."
  sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "$tar_file" "root@$REMOTE_IP:/root/aicommonplatform/images/" 2>/dev/null && echo "    ✓ 上传成功" || echo "    ✗ 上传失败"
done

echo ""
echo "✅ 上传完成"
echo ""
echo "🐳 开始远程导入和启动容器..."
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no root@$REMOTE_IP << 'REMOTE'
cd /root/aicommonplatform

# 停止现有容器
echo "  停止现有容器..."
docker-compose -f docker-compose.yml down 2>/dev/null || true
sleep 1

# 删除旧镜像
echo "  清理旧镜像..."
docker rmi $(docker images | grep aicommonplatform | awk '{print $3}' | sort -u) 2>/dev/null || true

# 导入新镜像
echo "  导入AMD64镜像..."
cd /root/aicommonplatform/images
for tar_file in *.tar; do
  echo "    导入 $tar_file..."
  docker load -i "$tar_file" > /dev/null 2>&1 && echo "      ✓" || echo "      ✗ 失败"
done

cd /root/aicommonplatform

# 启动容器
echo "  启动容器..."
docker-compose -f docker-compose.yml up -d 2>&1 | tail -5

sleep 3
echo ""
echo "📊 容器状态:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "ai_|ticket"

REMOTE

echo ""
echo "✅ 完成！"
echo ""
echo "🧪 测试Web UI:"
echo "  curl http://47.100.35.44:9000"
