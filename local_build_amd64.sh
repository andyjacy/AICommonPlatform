#!/bin/bash

# 只在本地构建和导出AMD64镜像，等待服务器恢复后再上传

LOCAL_PATH="/Users/zhao_/Documents/PRC/AI实践/AICommonPlatform"
EXPORT_DIR="/tmp/amd64_images"

echo "🏗️  步骤1: 本地构建AMD64镜像..."
cd "$LOCAL_PATH"

# 清理旧的导出目录
rm -rf "$EXPORT_DIR"
mkdir -p "$EXPORT_DIR"

# 构建web_ui
echo "  构建 web_ui..."
docker buildx build \
  --platform linux/amd64 \
  -f services/web_ui/Dockerfile \
  -t aicommonplatform-web_ui:amd64 \
  --load \
  services/web_ui 2>&1 | tail -3

# 构建其他服务
for service in qa_entry rag_service llm_service agent_service prompt_service integration; do
  echo "  构建 $service..."
  if [ -f "services/${service}/Dockerfile.lite" ]; then
    docker buildx build \
      --platform linux/amd64 \
      -f "services/${service}/Dockerfile.lite" \
      -t "aicommonplatform-${service}:amd64" \
      --load \
      "services/${service}" 2>&1 | tail -3
  fi
done

echo ""
echo "✅ 本地镜像构建完成"

# 验证镜像
echo ""
echo "📊 验证构建的镜像:"
docker images | grep amd64

# 导出镜像
echo ""
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
  tar_file="$EXPORT_DIR/${image%%:*##*-}.tar"
  echo "  导出 $image..."
  docker save "$image" -o "$tar_file" && echo "    ✓ $tar_file" || echo "    ✗ 导出失败"
done

echo ""
echo "✅ 所有镜像已导出到: $EXPORT_DIR"
echo ""
echo "📋 导出文件列表:"
ls -lh "$EXPORT_DIR"/*.tar 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "⏳ 等服务器恢复后，运行此命令上传:"
echo "  bash upload_amd64_images.sh"
