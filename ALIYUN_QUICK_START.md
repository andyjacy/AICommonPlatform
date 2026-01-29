# 🚀 阿里云部署快速指南

## ✅ 部署完成！

您的AI Common Platform已成功部署到阿里云轻量级服务器。

---

## 📍 访问地址

### 主应用
- **Web UI**: http://47.100.35.44:9000
- **用户界面**: 可以提问、查看回答、追踪调用链

### API服务（用于开发）
- **QA Entry**: http://47.100.35.44:8001
- **API文档**: http://47.100.35.44:8001/docs
- **RAG Service**: http://47.100.35.44:8003
- **API文档**: http://47.100.35.44:8003/docs

---

## 🔐 远程服务器信息

```
IP地址:   47.100.35.44
用户名:   root
密码:     65,UaTzA$9kAsny
端口:     22
```

### SSH快速连接
```bash
ssh root@47.100.35.44
```

---

## 📦 运行中的服务

| 容器名 | 服务 | 端口 | 状态 |
|--------|------|------|------|
| ai_web_ui | Web界面 | 9000 | ✅ 运行中 |
| ai_qa_entry | 问答入口 | 8001 | ✅ 运行中 |
| ai_prompt_service | Prompt管理 | 8002 | ✅ 运行中 |
| ai_rag_service | 知识库 | 8003 | ✅ 运行中 |
| ai_agent_service | Agent执行 | 8004 | ✅ 运行中 |
| ai_integration | 系统集成 | 8005 | ✅ 运行中 |
| ai_llm_service | 大模型接口 | 8006 | ✅ 运行中 |

---

## 🔧 常用命令

### 查看所有容器状态
```bash
ssh root@47.100.35.44 "docker ps"
```

### 查看特定容器日志
```bash
# Web UI 日志
ssh root@47.100.35.44 "docker logs -f ai_web_ui"

# QA服务日志
ssh root@47.100.35.44 "docker logs -f ai_qa_entry"
```

### 重启服务
```bash
# 重启所有服务
ssh root@47.100.35.44 "cd /root/aicommonplatform && docker-compose restart"

# 重启特定服务
ssh root@47.100.35.44 "cd /root/aicommonplatform && docker-compose restart ai_web_ui"
```

### 停止/启动服务
```bash
# 停止所有服务
ssh root@47.100.35.44 "cd /root/aicommonplatform && docker-compose down"

# 启动所有服务
ssh root@47.100.35.44 "cd /root/aicommonplatform && docker-compose up -d"
```

---

## 📊 系统资源

### 查看系统资源使用
```bash
ssh root@47.100.35.44 "free -h && df -h"
```

### 查看Docker资源使用
```bash
ssh root@47.100.35.44 "docker stats"
```

---

## 🧪 测试API

### 测试QA服务
```bash
curl -X POST http://47.100.35.44:8001/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是Docker"}'
```

### 查看API文档
直接访问: http://47.100.35.44:8001/docs

---

## 🐛 故障排查

### Web UI 无法访问？
```bash
# 1. 检查容器是否运行
ssh root@47.100.35.44 "docker ps | grep ai_web_ui"

# 2. 查看容器日志
ssh root@47.100.35.44 "docker logs ai_web_ui"

# 3. 检查9000端口
ssh root@47.100.35.44 "netstat -tlnp | grep 9000"

# 4. 重启容器
ssh root@47.100.35.44 "docker-compose -f /root/aicommonplatform/docker-compose.yml restart ai_web_ui"
```

### API 服务无法访问？
```bash
# 1. 检查QA服务
ssh root@47.100.35.44 "docker logs ai_qa_entry | tail -20"

# 2. 检查8001端口
ssh root@47.100.35.44 "netstat -tlnp | grep 8001"

# 3. 尝试本地测试（在服务器上）
ssh root@47.100.35.44 "curl -s http://localhost:8001/docs | head"
```

---

## 💾 数据备份

所有重要数据存储在:
```
/root/aicommonplatform/data/
├── web_ui/      # Web UI SQLite数据库
└── documents/   # 知识库文档
```

### 备份数据
```bash
ssh root@47.100.35.44 "tar -czf /root/aicommonplatform-backup-$(date +%Y%m%d).tar.gz /root/aicommonplatform/data/"
```

---

## 🔄 更新部署

### 如果需要重新部署新版本：

1. **本地构建新镜像**
   ```bash
   docker-compose -f docker-compose.lite.yml build
   ```

2. **执行部署脚本**
   ```bash
   bash deploy.sh
   ```

3. **或手动上传和部署**
   ```bash
   # 导出新镜像
   docker save aicommonplatform-web_ui:latest | gzip > /tmp/web_ui.tar.gz
   
   # 上传到服务器
   scp /tmp/web_ui.tar.gz root@47.100.35.44:/root/aicommonplatform/images/
   
   # 远程导入和重启
   ssh root@47.100.35.44 << 'CMD'
   cd /root/aicommonplatform/images
   tar -xzf web_ui.tar.gz
   docker load -i web_ui.tar
   docker-compose -f ../docker-compose.yml up -d ai_web_ui
   CMD
   ```

---

## 📞 本地部署脚本

项目目录中有以下实用脚本：

```bash
# 一键部署脚本
./deploy.sh

# 验证部署状态
./check_deployment.sh

# 更新端口配置
./update_port.sh

# 验证部署完整性
./verify_deployment.sh
```

---

## 📝 配置文件

远程服务器上的配置文件位置：
```
/root/aicommonplatform/
├── docker-compose.yml    # 容器编排配置
├── images/               # Docker镜像备份
└── data/                 # 数据持久化目录
```

---

## ✨ 功能特性

✅ **完整的微服务架构**
- 问答入口服务
- Prompt管理
- RAG知识库
- Agent执行
- LLM大模型
- 企业系统集成

✅ **调用链追踪**
- 实时显示每个请求的处理流程
- 包含11个处理步骤
- 详细的耗时统计

✅ **Web UI**
- 响应式设计
- 进度条显示
- 调用链可视化

✅ **高可用**
- 容器自动重启
- 数据持久化
- 日志记录

---

## 🎯 下一步

1. **访问Web UI**: http://47.100.35.44:9000
2. **提问测试**: 在输入框中输入问题
3. **查看调用链**: 点击"查看调用链"按钮
4. **查看API文档**: http://47.100.35.44:8001/docs

---

## 📞 技术支持

遇到问题时：
1. 查看容器日志：`docker logs <container_name>`
2. 检查网络连接：`curl -I http://localhost:port`
3. 查看系统资源：`docker stats`
4. 阅读详细报告：`ALIYUN_DEPLOYMENT_REPORT.md`

---

**部署时间**: 2026年1月29日  
**部署状态**: ✅ 完成  
**预期可用性**: 99%+ (带容器自动重启)
