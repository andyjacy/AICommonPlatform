#!/bin/bash

# 方案：在本地启动HTTP服务器，远程服务器通过wget下载镜像
# 前提：本地网络与阿里云服务器在同一内网或服务器能访问本地IP

EXPORT_DIR="/tmp/amd64_images"
LOCAL_PORT=8899
REMOTE_IP="47.100.35.44"

echo "📦 准备HTTP传输..."
echo "=================================================="
echo ""

# 检查镜像是否存在
if [ ! -d "$EXPORT_DIR" ] || [ -z "$(ls $EXPORT_DIR/*.tar 2>/dev/null)" ]; then
  echo "❌ 找不到镜像文件"
  exit 1
fi

# 进入镜像目录
cd "$EXPORT_DIR"

echo "📂 镜像文件列表:"
ls -lh *.tar | awk '{print "  " $9 " (" $5 ")"}'
echo ""

# 启动HTTP服务器
echo "🚀 启动本地HTTP服务器（端口 $LOCAL_PORT）..."
python3 -m http.server $LOCAL_PORT > /tmp/http_server.log 2>&1 &
HTTP_PID=$!
echo "  PID: $HTTP_PID"

sleep 1

# 获取本地IP（假设在Mac上）
LOCAL_IP=$(ifconfig | grep -E "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}')
echo "  IP: $LOCAL_IP"
echo ""

# 如果本地IP获取失败，手动指定
if [ -z "$LOCAL_IP" ]; then
  echo "⚠️  无法自动获取本地IP，请手动输入:"
  read -p "请输入你的本地IP或Mac的局域网IP: " LOCAL_IP
fi

echo "🔗 HTTP URL: http://$LOCAL_IP:$LOCAL_PORT"
echo ""

echo "⏳ 准备远程下载（需要SSH或其他方式连接远程服务器）..."
echo ""
echo "在远程服务器上执行以下命令:"
echo ""
echo "  cd /root/aicommonplatform/images"
echo ""
for file in *.tar; do
  echo "  wget http://$LOCAL_IP:$LOCAL_PORT/$file &"
done
echo "  wait"
echo ""
echo "然后继续导入和启动:"
echo ""
echo "  cd /root/aicommonplatform"
echo "  docker-compose down 2>/dev/null || true"
echo "  docker rmi \$(docker images | grep aicommonplatform | awk '{print \$3}' | sort -u) 2>/dev/null || true"
echo "  cd images && for f in *.tar; do docker load -i \"\$f\" > /dev/null 2>&1; done"
echo "  cd .."
echo "  docker-compose up -d"
echo ""

echo "📡 HTTP服务器运行中（PID: $HTTP_PID）..."
echo "❌ 按 Ctrl+C 停止服务器"
echo ""

# 保持HTTP服务器运行
wait $HTTP_PID
