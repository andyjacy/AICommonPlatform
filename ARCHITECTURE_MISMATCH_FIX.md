# ⚠️ 架构不匹配问题 - 解决方案

## 问题诊断

**错误**: `exec /usr/local/bin/python: exec format error`

**原因**: 
- 本地Mac构建的镜像: **ARM64** 架构
- 远程服务器: **AMD64** 架构
- 架构不兼容导致容器无法执行

## 🔧 解决方案

### 方案1：使用buildx构建多架构镜像（推荐）

```bash
# 1. 启用buildx
docker buildx create --use

# 2. 构建AMD64镜像（在项目目录执行）
cd /Users/zhao_/Documents/PRC/AI实践/AICommonPlatform/services/web_ui

docker buildx build \
  --platform linux/amd64 \
  -t aicommonplatform-web_ui:amd64 \
  -f Dockerfile \
  --load \
  .

# 3. 为其他服务做同样的事情
cd ../qa_entry
docker buildx build --platform linux/amd64 -t aicommonplatform-qa_entry:amd64 -f Dockerfile.lite --load .

cd ../rag_service
docker buildx build --platform linux/amd64 -t aicommonplatform-rag_service:amd64 -f Dockerfile.lite --load .

# 4. 查看构建的镜像
docker images | grep amd64
```

### 方案2：直接在远程AMD64服务器构建

```bash
# 1. 上传源代码到服务器
scp -r /Users/zhao_/Documents/PRC/AI实践/AICommonPlatform/services root@47.100.35.44:/root/aicommonplatform/

# 2. 在远程服务器构建
ssh root@47.100.35.44

cd /root/aicommonplatform/services/web_ui
docker build -t aicommonplatform-web_ui:latest -f Dockerfile .

cd ../qa_entry
docker build -t aicommonplatform-qa_entry:latest -f Dockerfile.lite .

# 3. 查看镜像
docker images | grep aicommonplatform
```

### 方案3：使用docker-buildx推送跨架构镜像

```bash
# 需要Docker Hub账户或私有registry

# 构建并推送到registry（同时支持多架构）
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t your-registry/aicommonplatform-web_ui:latest \
  --push \
  -f Dockerfile \
  ./services/web_ui
```

---

## 🚀 快速修复步骤

### 如果选择方案2（最简单）

1. **在远程服务器上构建镜像**

```bash
# SSH连接
ssh root@47.100.35.44

# 创建源代码目录
mkdir -p /root/build

# 上传Dockerfile和源代码（本地执行）
scp -r /Users/zhao_/Documents/PRC/AI实践/AICommonPlatform/services/web_ui root@47.100.35.44:/root/build/

# 在服务器上构建
cd /root/build/web_ui
docker build -t aicommonplatform-web_ui:latest -f Dockerfile .

# 对其他服务重复...
```

2. **启动容器**

```bash
cd /root/aicommonplatform
docker-compose -f docker-compose.yml down

# 重新启动
docker-compose -f docker-compose.yml up -d

# 检查状态
docker ps --filter "name=ai_"
```

---

## 📋 快速参考

| 项目 | 值 |
|------|-----|
| 本地架构 | ARM64 (Mac M1/M2/M3) |
| 远程架构 | AMD64 (x86_64) |
| 问题 | 镜像不兼容 |
| 解决 | 构建AMD64镜像 |

---

## ✅ 验证修复

构建完成后验证：

```bash
# 检查镜像架构
docker image inspect aicommonplatform-web_ui | grep -i architecture

# 应该显示: "Architecture": "amd64"
```

---

## 📞 需要帮助？

如果不确定如何进行，建议使用方案2（在远程服务器构建），最简单快速。

需要我提供详细的脚本吗？
