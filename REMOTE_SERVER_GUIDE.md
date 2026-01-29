# 阿里云部署状态诊断与修复指南

## 📊 当前状态

- **部署状态**: 镜像已上传并成功加载 ✅
- **容器状态**: 容器网络已创建，但需要启动确认 ⏳
- **现有应用**: ticket-grab-app 正在运行（不影响）✅

---

## 🔧 手动启动容器（远程执行）

如果容器没有自动启动，请在远程服务器执行以下命令：

### 方案1：使用Docker Compose（推荐）

```bash
# SSH连接到服务器
ssh root@47.100.35.44

# 进入aicommonplatform目录
cd /root/aicommonplatform

# 启动容器（不影响其他应用）
docker-compose -f docker-compose.yml up -d

# 查看启动状态
docker-compose -f docker-compose.yml ps

# 查看日志
docker logs -f ai_web_ui
```

### 方案2：逐个启动服务

```bash
# 启动Web UI
docker-compose -f docker-compose.yml up -d ai_web_ui

# 启动QA服务
docker-compose -f docker-compose.yml up -d ai_qa_entry

# 启动所有服务
docker-compose -f docker-compose.yml up -d
```

### 方案3：直接使用Docker命令

```bash
# 启动Web UI容器
docker run -d -p 9000:3000 \
  --name ai_web_ui \
  --network aicommonplatform_ai_net \
  aicommonplatform-web_ui:latest

# 启动QA Entry容器
docker run -d -p 8001:8000 \
  --name ai_qa_entry \
  --network aicommonplatform_ai_net \
  aicommonplatform-qa_entry:latest
```

---

## ✅ 验证服务启动

### 检查容器运行状态

```bash
# 查看所有容器（不影响ticket-grab-app）
docker ps --filter "name=ai_"

# 查看容器日志
docker logs ai_web_ui
docker logs ai_qa_entry

# 查看网络
docker network ls
docker network inspect aicommonplatform_ai_net
```

### 测试服务可访问性

```bash
# 本地测试（在服务器上）
curl -s http://localhost:9000/ | head -5
curl -s http://localhost:8001/docs | head -5

# 查看监听端口
netstat -tlnp | grep -E "9000|8001|8003"
# 或
ss -tlnp | grep -E "9000|8001|8003"
```

---

## 🚨 常见问题处理

### 问题1：容器无法启动

**症状**: `docker-compose up -d` 后容器状态为 `Exit` 或 `Error`

**解决方案**:

```bash
# 查看错误日志
docker logs ai_web_ui

# 删除旧容器重新启动
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d

# 如果需要，清理所有aicommonplatform相关容器
docker ps -a | grep ai_ | awk '{print $1}' | xargs docker rm -f 2>/dev/null || true
```

### 问题2：端口被占用

**症状**: `Error: Port 9000 is already allocated`

**解决方案**:

```bash
# 检查占用端口的进程
netstat -tlnp | grep 9000

# 改用其他端口（修改docker-compose.yml）
# 将 "9000:3000" 改为 "9001:3000"

# 或停止占用端口的容器
docker stop <container_id>
```

### 问题3：网络连接问题

**症状**: 容器启动后无法通过HTTP访问

**解决方案**:

```bash
# 检查容器是否在正确的网络中
docker inspect ai_web_ui | grep Networks -A 10

# 检查防火墙规则
iptables -L -n | grep 9000
firewall-cmd --list-ports

# 重建网络
docker network rm aicommonplatform_ai_net
docker-compose -f docker-compose.yml up -d
```

---

## 📋 启动脚本（本地运行）

### 快速启动脚本

保存为 `start_remote_containers.sh`：

```bash
#!/bin/bash

REMOTE_IP="47.100.35.44"
PASSWORD="65,UaTzA$9kAsny"

sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 root@$REMOTE_IP << 'EOF'
cd /root/aicommonplatform
docker-compose -f docker-compose.yml down 2>/dev/null || true
sleep 2
docker-compose -f docker-compose.yml up -d
sleep 5
echo "✅ 容器启动完成"
docker ps --filter "name=ai_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
EOF
```

运行:
```bash
bash start_remote_containers.sh
```

---

## 🔍 调试步骤

### 第1步：连接服务器并检查镜像

```bash
ssh root@47.100.35.44
docker images | grep aicommonplatform
```

预期输出：7个镜像

### 第2步：查看docker-compose配置

```bash
cat /root/aicommonplatform/docker-compose.yml | head -50
```

### 第3步：手动启动一个容器测试

```bash
docker run -it --rm aicommonplatform-web_ui:latest /bin/bash
# 或
docker run -d -p 9000:3000 aicommonplatform-web_ui:latest
```

### 第4步：查看容器日志

```bash
docker logs -f <container_id>
docker logs --tail 100 ai_web_ui
```

---

## 📊 监控容器状态

### 实时监控

```bash
# 监控所有aicommonplatform容器
watch -n 1 'docker ps --filter "name=ai_"'

# 或使用docker stats
docker stats --filter "name=ai_"
```

### 查看历史日志

```bash
# 查看最后500行日志
docker logs --tail 500 ai_web_ui

# 查看最后1小时的日志
docker logs --since 1h ai_web_ui

# 实时跟踪日志
docker logs -f ai_web_ui
```

---

## 🛑 停止/重启服务

### 停止所有aicommonplatform容器（不影响其他应用）

```bash
cd /root/aicommonplatform
docker-compose -f docker-compose.yml stop

# 或只停止特定容器
docker-compose -f docker-compose.yml stop ai_web_ui
```

### 重启容器

```bash
docker-compose -f docker-compose.yml restart

# 或重启特定容器
docker-compose -f docker-compose.yml restart ai_web_ui
```

### 完全移除容器（保留镜像）

```bash
docker-compose -f docker-compose.yml down

# 重新启动
docker-compose -f docker-compose.yml up -d
```

---

## 📞 获取帮助

如果容器仍无法启动，请收集以下信息：

1. **docker-compose输出**:
   ```bash
   docker-compose -f docker-compose.yml up 2>&1 | tee /tmp/compose.log
   ```

2. **容器日志**:
   ```bash
   docker logs ai_web_ui 2>&1 | tee /tmp/web_ui.log
   docker logs ai_qa_entry 2>&1 | tee /tmp/qa_entry.log
   ```

3. **系统信息**:
   ```bash
   df -h
   free -h
   docker version
   docker-compose version
   ```

4. **网络信息**:
   ```bash
   docker network ls
   netstat -tlnp | grep -E "9000|8001|8003"
   ```

---

**最后更新**: 2026年1月29日  
**状态**: aicommonplatform已部署，需手动启动容器  
**注意**: 所有操作仅涉及aicommonplatform，不会影响ticket-grab-app
