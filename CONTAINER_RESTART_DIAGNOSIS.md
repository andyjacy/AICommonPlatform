# 🔍 远程服务器容器诊断报告

## 📊 发现的问题

### 容器启动状态
```
ai_web_ui          → Restarting (1) 24 seconds ago  ⚠️
ai_qa_entry        → Restarting (1) 24 seconds ago  ⚠️
ai_agent_service   → Restarting (1) 26 seconds ago  ⚠️
ai_llm_service     → Restarting (1) 26 seconds ago  ⚠️
ai_rag_service     → Restarting (1) 25 seconds ago  ⚠️
ai_prompt_service  → Restarting (1) 24 seconds ago  ⚠️
ai_integration     → Restarting (1) 26 seconds ago  ⚠️
```

**问题**: 所有容器都处于持续重启状态，说明容器启动后立即崩溃

---

## 🔧 解决方案

### 第1步：连接远程服务器查看错误日志

```bash
ssh root@47.100.35.44

# 查看Web UI错误日志
docker logs ai_web_ui

# 查看QA服务错误日志
docker logs ai_qa_entry

# 查看完整日志（包括多次重启）
docker logs --tail 100 ai_web_ui
```

### 第2步：查看具体错误信息

可能的原因包括：
- 📦 依赖包缺失
- 🔐 环境变量配置错误
- 💾 数据卷挂载问题
- 🌐 网络连接问题
- 📂 文件权限问题

### 第3步：重建容器

```bash
cd /root/aicommonplatform

# 停止所有容器
docker-compose -f docker-compose.yml stop

# 删除容器
docker-compose -f docker-compose.yml rm -f

# 重新创建并启动（查看实时日志）
docker-compose -f docker-compose.yml up
```

### 第4步：检查镜像完整性

```bash
# 查看镜像列表
docker images | grep aicommonplatform

# 查看镜像详情
docker inspect aicommonplatform-web_ui:latest

# 尝试手动运行容器查看详细错误
docker run -it --rm aicommonplatform-web_ui:latest /bin/bash
```

---

## 📋 快速诊断脚本

在远程服务器执行以下命令集中诊断：

```bash
#!/bin/bash

echo "=== 系统信息 ==="
uname -a
docker --version
docker-compose --version

echo ""
echo "=== 容器镜像 ==="
docker images | grep aicommonplatform

echo ""
echo "=== 容器状态 ==="
docker ps -a | grep ai_

echo ""
echo "=== Web UI 错误日志 ==="
docker logs --tail 50 ai_web_ui

echo ""
echo "=== 容器环境变量 ==="
docker inspect ai_web_ui | grep -A 20 '"Env"'

echo ""
echo "=== 容器挂载卷 ==="
docker inspect ai_web_ui | grep -A 10 '"Mounts"'

echo ""
echo "=== 磁盘空间 ==="
df -h

echo ""
echo "=== 内存使用 ==="
free -h
```

---

## 🆘 常见错误及解决方案

### 错误1: Python模块缺失

**症状**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
# 重建镜像（本地）
docker-compose -f docker-compose.lite.yml build aicommonplatform-web_ui

# 重新上传并部署
./deploy.sh
```

### 错误2: 端口被占用

**症状**: `Address already in use`

**解决**:
```bash
# 检查占用端口的进程
netstat -tlnp | grep 9000

# 杀死占用端口的进程
kill -9 <PID>

# 或改用其他端口
# 修改docker-compose.yml中的端口配置
```

### 错误3: 环境变量错误

**症状**: `KeyError: 'SERVICE_NAME'`

**解决**:
```bash
# 检查环境变量
docker-compose config | grep environment

# 更新docker-compose.yml中的环境变量
# 或创建.env文件
```

### 错误4: 数据卷权限

**症状**: `Permission denied` 或 `Cannot write to directory`

**解决**:
```bash
# 检查数据卷权限
ls -la /root/aicommonplatform/data/

# 修改权限
chmod -R 777 /root/aicommonplatform/data/

# 重启容器
docker-compose -f docker-compose.yml restart
```

---

## 🔗 容器间通信测试

如果某些容器运行但网络不通，尝试：

```bash
# 测试容器间通信
docker exec ai_web_ui ping ai_qa_entry

# 测试服务端口
docker exec ai_web_ui curl http://ai_qa_entry:8000/docs

# 查看网络配置
docker network inspect aicommonplatform_ai_net
```

---

## 📞 获取完整日志

如果以上步骤未能解决问题，请收集以下信息：

```bash
# 导出完整日志到文件
mkdir -p /root/logs

docker logs ai_web_ui > /root/logs/web_ui.log 2>&1
docker logs ai_qa_entry > /root/logs/qa_entry.log 2>&1
docker logs ai_rag_service > /root/logs/rag_service.log 2>&1

# 导出系统信息
docker system info > /root/logs/docker_info.log
docker inspect $(docker ps -aq) > /root/logs/containers_info.log

# 导出compose配置
docker-compose -f /root/aicommonplatform/docker-compose.yml config > /root/logs/compose_config.yml

# 打包所有日志
tar -czf /root/logs.tar.gz /root/logs/
```

---

## ✅ 下一步操作

1. **SSH连接到服务器**
   ```bash
   ssh root@47.100.35.44
   ```

2. **查看容器日志**
   ```bash
   docker logs ai_web_ui | head -50
   ```

3. **确定具体错误原因**

4. **根据错误修复**
   - 如果是依赖问题：重新构建镜像并上传
   - 如果是配置问题：更新docker-compose.yml
   - 如果是权限问题：修改文件权限

5. **重启容器测试**
   ```bash
   docker-compose -f docker-compose.yml restart
   ```

---

**诊断时间**: 2026年1月29日  
**状态**: 容器处于重启循环中 ⚠️  
**下一步**: 查看容器日志确定具体错误原因
