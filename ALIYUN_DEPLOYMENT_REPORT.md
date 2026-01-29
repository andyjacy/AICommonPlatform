# 🚀 阿里云部署完成报告

## 部署信息

| 项目 | 详情 |
|------|------|
| **云服务器** | 阿里云轻量级服务器 |
| **IP地址** | 47.100.35.44 |
| **Docker版本** | 26.1.3 (AMD64) |
| **操作系统** | Linux (CentOS/Aliyun) |
| **用户名** | root |
| **部署路径** | /root/aicommonplatform |

---

## 部署过程

### ✅ 已完成的步骤

1. **本地构建镜像**
   - ✅ 构建7个轻量级Docker镜像
   - Web UI: 144MB
   - QA Entry: 61MB  
   - RAG Service: 146MB
   - LLM Service: 59MB
   - Agent Service: 57MB
   - Prompt Service: 57MB
   - Integration: 57MB
   - **总大小: 638MB**

2. **导出镜像文件**
   - ✅ 导出所有7个镜像为tar格式
   - 临时目录: /tmp/docker-deploy-*

3. **上传到远程服务器**
   - ✅ 所有镜像文件成功上传到 `/root/aicommonplatform/images/`
   - ✅ docker-compose.yml 配置文件上传

4. **远程导入镜像**
   - ✅ 所有7个镜像成功导入到Docker
   - 验证: `docker images | grep aicommonplatform`

5. **启动容器服务**
   - ✅ 所有服务启动成功
   - 使用 docker-compose 编排管理

6. **端口配置**
   - ✅ Web UI 端口修改从 3000 → **9000**（原3000端口被占用）
   - QA Entry: 8001
   - Prompt Service: 8002
   - RAG Service: 8003
   - Agent Service: 8004
   - Integration: 8005
   - LLM Service: 8006

---

## 🌐 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **Web UI** | http://47.100.35.44:9000 | 主应用界面 |
| **QA Entry API** | http://47.100.35.44:8001 | 问答入口服务 |
| **QA Entry Docs** | http://47.100.35.44:8001/docs | Swagger文档 |
| **RAG Service** | http://47.100.35.44:8003 | 知识库服务 |
| **RAG Docs** | http://47.100.35.44:8003/docs | Swagger文档 |

---

## 📦 容器运行状态

```bash
# SSH连接
ssh root@47.100.35.44

# 查看容器状态
docker ps --filter "label=com.docker.compose.project"

# 查看所有容器
docker-compose -f /root/aicommonplatform/docker-compose.yml ps

# 查看日志
docker logs -f ai_web_ui
docker logs -f ai_qa_entry
```

---

## 🔧 常用命令

### 查看容器状态
```bash
ssh root@47.100.35.44 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
```

### 查看服务日志
```bash
ssh root@47.100.35.44 "docker logs -f ai_web_ui"
ssh root@47.100.35.44 "docker logs -f ai_qa_entry"
```

### 停止服务
```bash
ssh root@47.100.35.44 "cd /root/aicommonplatform && docker-compose down"
```

### 重启服务
```bash
ssh root@47.100.35.44 "cd /root/aicommonplatform && docker-compose restart"
```

### 启动特定服务
```bash
ssh root@47.100.35.44 "cd /root/aicommonplatform && docker-compose up -d web_ui"
```

---

## 📊 数据持久化

所有数据存储在远程服务器以下目录：

```
/root/aicommonplatform/
├── images/              # Docker镜像备份
├── data/
│   ├── web_ui/         # Web UI 数据库
│   └── documents/      # 知识库文档
├── docker-compose.yml   # 容器编排配置
└── logs/               # 日志文件（如配置）
```

---

## 🔐 远程服务器访问

### SSH连接信息
```
地址:     47.100.35.44
用户:     root
密码:     65,UaTzA$9kAsny
端口:     22
```

### SSH命令示例
```bash
# 基本连接
ssh root@47.100.35.44

# 一次性执行命令
ssh root@47.100.35.44 "docker ps"

# 查看系统资源
ssh root@47.100.35.44 "free -h && df -h"
```

---

## 🐛 故障排查

### 如果Web UI无法访问 (9000端口)

1. **检查容器状态**
   ```bash
   ssh root@47.100.35.44 "docker ps | grep ai_web_ui"
   ```

2. **查看容器日志**
   ```bash
   ssh root@47.100.35.44 "docker logs ai_web_ui"
   ```

3. **检查端口占用**
   ```bash
   ssh root@47.100.35.44 "netstat -tlnp | grep 9000"
   ```

4. **重启容器**
   ```bash
   ssh root@47.100.35.44 "docker-compose -f /root/aicommonplatform/docker-compose.yml restart web_ui"
   ```

### 如果API服务无法访问

1. **检查特定服务**
   ```bash
   ssh root@47.100.35.44 "docker logs ai_qa_entry"
   ```

2. **检查依赖服务**
   所有服务依赖关系已在 docker-compose.yml 中定义

3. **查看容器网络**
   ```bash
   ssh root@47.100.35.44 "docker network ls && docker network inspect aicommonplatform_ai_net"
   ```

---

## 📈 性能指标

### 部署统计
- **总镜像大小**: 638MB
- **容器数量**: 7个
- **网络模式**: Bridge (ai_net)
- **重启策略**: unless-stopped (容器自动重启)

### 资源配置
- 默认无资源限制
- 可根据需要在 docker-compose.yml 中添加限制

---

## 🔄 更新/重新部署流程

### 如果需要重新部署新版本镜像：

```bash
# 1. 本地构建新镜像
docker-compose -f docker-compose.lite.yml build

# 2. 执行部署脚本
bash deploy.sh

# 或手动操作：
# 3. 导出镜像
docker save aicommonplatform-web_ui:latest -o /tmp/web_ui.tar

# 4. 上传到服务器
scp /tmp/web_ui.tar root@47.100.35.44:/root/aicommonplatform/images/

# 5. 远程导入并重启
ssh root@47.100.35.44 << 'CMD'
cd /root/aicommonplatform/images
docker load -i web_ui.tar
docker-compose -f ../docker-compose.yml up -d web_ui
CMD
```

---

## 📝 部署脚本位置

```bash
# 快速部署脚本
./deploy.sh                    # 自动上传镜像并部署
./update_port.sh              # 更新端口配置
./verify_deployment.sh        # 验证部署状态
```

---

## ✅ 验证清单

- [x] 所有7个微服务镜像已构建
- [x] 镜像文件已上传到服务器
- [x] 容器已启动并运行
- [x] Web UI 可通过端口 9000 访问
- [x] 所有API服务端口已开放
- [x] Docker容器自动重启策略已启用
- [x] 数据卷持久化已配置

---

## 📞 技术支持

遇到问题时的排查步骤：

1. 检查容器运行状态：`docker ps`
2. 查看容器日志：`docker logs <container_name>`
3. 测试网络连通性：`curl -I http://localhost:port`
4. 检查系统资源：`free -h && df -h && docker stats`

---

**部署完成于**: 2026年1月29日
**部署状态**: ✅ 成功
**最后更新**: 2026年1月29日
