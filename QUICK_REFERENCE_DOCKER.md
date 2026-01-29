# 🚀 快速参考指南 - AI Common Platform

## ⚡ 30秒快速开始

```bash
# 1. 启动所有服务
cd /Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform
docker-compose -f docker-compose.lite.yml up -d

# 2. 打开浏览器
open http://localhost:3000

# 3. 配置 API Key
菜单 → LLM 模型管理 → 添加新模型 → 输入 API Key

# 4. 开始提问！
```

---

## 📍 服务地址

| 服务 | 地址 | 功能 |
|------|------|------|
| 🌐 Web UI | http://localhost:3000 | 用户界面 |
| ❓ QA API | http://localhost:8001 | 提问接口 |
| 📚 RAG | http://localhost:8003 | 知识库 |
| ⚙️ Prompt | http://localhost:8002 | 提示词 |
| 🤖 LLM | http://localhost:8006 | LLM 接口 |
| 🔷 Redis | localhost:6379 | 缓存 |

---

## 🔑 获取 API Key

### ChatAnywhere（推荐，免费）
1. https://chatanywhere.com.cn/
2. 注册 → 复制 Key
3. 提供商: `chatanywhere`

### OpenAI（商业，付费）
1. https://platform.openai.com/api-keys
2. 创建 Key → 复制
3. 提供商: `openai`

---

## 💻 常用命令

```bash
# 查看状态
docker-compose -f docker-compose.lite.yml ps

# 查看日志
docker-compose -f docker-compose.lite.yml logs -f qa_entry

# 重启服务
docker-compose -f docker-compose.lite.yml restart qa_entry

# 停止服务
docker-compose -f docker-compose.lite.yml down

# 重新启动
docker-compose -f docker-compose.lite.yml up -d
```

---

## 🧪 API 测试

### 提问

```bash
curl -X POST http://localhost:8001/api/qa/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "2024年Q1的销售业绩如何？",
    "user_id": "test"
  }'
```

### 知识库搜索

```bash
curl -X POST http://localhost:8003/api/rag/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "销售", "top_k": 3}'
```

### 健康检查

```bash
curl http://localhost:8001/health
curl http://localhost:8003/health
```

---

## 🧠 知识库文档

系统预置 10 个文档：

1. Q1销售报告 - 5000万元销售额
2. 员工手册 - HR 政策
3. 技术架构 - 微服务设计
4. 财务预算 - 2000万预算
5. 客户案例 - 零售行业
6. 产品功能 - 7 大功能
7. Q2销售计划 - 6500万目标
8. 安全政策 - ISO27001
9. 技术栈 - FastAPI+Docker
10. 常见问题 - FAQ

---

## ❓ 常见问题

### Q: 如何停止所有服务？
```bash
docker-compose -f docker-compose.lite.yml down
```

### Q: 如何查看实时日志？
```bash
docker-compose -f docker-compose.lite.yml logs -f
```

### Q: 如何重新配置 API Key？
在 Web UI → LLM 模型管理 中修改

### Q: 如何添加新的知识库文档？
在 Web UI 中上传，或通过 API 添加

### Q: 如何清除所有数据重新开始？
```bash
docker-compose -f docker-compose.lite.yml down -v
docker-compose -f docker-compose.lite.yml up -d
```

---

## 📱 支持的提问类型

✅ 销售数据查询
✅ 员工政策咨询
✅ 技术架构问题
✅ 财务信息查询
✅ 产品功能说明
✅ 安全政策查询
✅ 常见问题解答

---

## 🔧 Docker 相关

### 查看所有容器
```bash
docker ps
```

### 查看所有镜像
```bash
docker images | grep aicommonplatform
```

### 重建镜像
```bash
docker-compose -f docker-compose.lite.yml build --no-cache
```

### 进入容器
```bash
docker-compose -f docker-compose.lite.yml exec qa_entry bash
```

---

## 📊 系统要求

- Docker >= 20.10
- Docker Compose >= 2.0
- 磁盘: >= 2GB
- 内存: >= 4GB
- CPU: >= 2核

---

## 🎯 关键特性

✅ 真实大模型集成
✅ 多提供商支持 (OpenAI + ChatAnywhere)
✅ 完整 RAG 流程
✅ 10 个预置文档
✅ 8 个微服务
✅ Docker 容器化
✅ 轻量级部署
✅ Web 用户界面
✅ RESTful API
✅ JSON 日志

---

## 📚 详细文档

- `DOCKER_DEPLOYMENT_GUIDE.md` - 完整部署指南
- `CHATANYWHERE_INTEGRATION.md` - ChatAnywhere 指南
- `FINAL_DEPLOYMENT_SUMMARY.md` - 部署总结
- `QA_LLM_INTEGRATION.md` - 技术细节

---

**准备好了吗？现在就开始！**

```bash
docker-compose -f docker-compose.lite.yml up -d
open http://localhost:3000
```

🎉 祝您使用愉快！
