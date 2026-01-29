# 🐳 Docker 部署指南 - AI Common Platform 轻量级版

## ✅ 部署状态

系统已成功通过 Docker 方式部署运行！

```
╔════════════════════════════════════════════════════════════════╗
║              🚀 所有服务已启动并运行                            ║
╚════════════════════════════════════════════════════════════════╝

✅ ai_lite_redis            (Redis 缓存)         PORT 6379
✅ ai_lite_web_ui           (Web UI 界面)         PORT 3000
✅ ai_lite_qa_entry         (QA 入口)            PORT 8001
✅ ai_lite_rag_service      (知识库检索)         PORT 8003
✅ ai_lite_prompt_service   (提示词管理)         PORT 8002
✅ ai_lite_agent_service    (企业系统集成)       PORT 8004
✅ ai_lite_integration      (数据集成)           PORT 8005
✅ ai_lite_llm_service      (LLM 接口)           PORT 8006
```

---

## 📖 快速启动

### 1️⃣ 启动所有服务

```bash
cd /Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform

# 启动所有容器（后台运行）
docker-compose -f docker-compose.lite.yml up -d

# 查看服务状态
docker-compose -f docker-compose.lite.yml ps
```

### 2️⃣ 停止所有服务

```bash
docker-compose -f docker-compose.lite.yml down
```

### 3️⃣ 查看实时日志

```bash
# 查看所有日志
docker-compose -f docker-compose.lite.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.lite.yml logs -f qa_entry
docker-compose -f docker-compose.lite.yml logs -f rag_service
docker-compose -f docker-compose.lite.yml logs -f web_ui
```

---

## 🌐 服务访问

### Web UI - 用户界面

```
🌍 http://localhost:3000
```

**功能**:
- LLM 模型管理 (OpenAI / ChatAnywhere)
- 实时问答测试
- 知识库管理
- 系统配置

### QA Entry - 问答接口

```
POST http://localhost:8001/api/qa/ask
```

**示例请求**:

```bash
curl -X POST http://localhost:8001/api/qa/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "2024年Q1的销售业绩如何？",
    "user_id": "test_user"
  }'
```

**预期响应**:

```json
{
  "answer": "根据知识库，2024年Q1销售业绩为...",
  "sources": ["erp_system"],
  "confidence": 0.95
}
```

### RAG Service - 知识库检索

```
POST http://localhost:8003/api/rag/search
GET  http://localhost:8003/api/rag/documents
```

**示例请求**:

```bash
curl -X POST http://localhost:8003/api/rag/search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "销售",
    "top_k": 3
  }'
```

---

## 🔧 配置 LLM 模型

### 方式 1: 通过 Web UI（推荐）

1. 访问 `http://localhost:3000`
2. 菜单 → **LLM 模型管理** → **添加新模型**
3. 填入模型信息：
   - **模型名称**: GPT-3.5 / ChatGPT 等
   - **提供商**: `openai` 或 `chatanywhere`
   - **API Key**: 您的真实 API Key
   - **温度**: 0.7
   - **最大 tokens**: 2048
4. 保存并设置为默认

### 方式 2: 通过 API

```bash
# 创建 ChatAnywhere 模型
curl -X POST http://localhost:3000/api/llm/models \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "ChatGPT-Free",
    "provider": "chatanywhere",
    "api_key": "sk-your-key-here",
    "temperature": 0.7,
    "max_tokens": 2048
  }'

# 获取所有模型
curl http://localhost:3000/api/llm/models/list
```

---

## 💡 获取 API Key

### ChatAnywhere (免费，推荐用于测试)

1. 访问: https://chatanywhere.com.cn/
2. 注册账号
3. 复制 API Key

**优点**:
- 完全免费
- 无需信用卡
- 兼容 OpenAI 接口
- 支持 GPT-3.5, GPT-4 等

### OpenAI (商业用)

1. 访问: https://platform.openai.com/api-keys
2. 创建新 API Key
3. 设置使用额度

**优点**:
- 官方 API
- 支持最新模型
- 可自定义配额

---

## 🧪 测试示例

### 测试 1: 查询销售数据

```bash
curl -X POST http://localhost:8001/api/qa/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "2024年Q1的销售业绩如何？",
    "user_id": "test"
  }'
```

**返回**:
```json
{
  "answer": "2024年Q1销售业绩：总销售额5000万元，同比增长15%...",
  "sources": ["erp_system"],
  "confidence": 0.95
}
```

### 测试 2: 查询员工政策

```bash
curl -X POST http://localhost:8001/api/qa/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "员工年假是多少天？",
    "user_id": "test"
  }'
```

### 测试 3: 搜索知识库

```bash
curl -X POST http://localhost:8003/api/rag/search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "财务预算",
    "top_k": 3,
    "category": "finance"
  }'
```

### 测试 4: 获取健康状态

```bash
# 所有服务都有 /health 端点
curl http://localhost:8001/health
curl http://localhost:8003/health
curl http://localhost:8002/health
curl http://localhost:3000/health
```

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────┐
│          🌐 Web UI (Port 3000)                  │
│      用户界面 + 模型管理 + API 测试             │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ RAG      │ │QA Entry  │ │ Prompt   │
│Service   │ │(8001)    │ │Service   │
│(8003)    │ └────┬─────┘ │(8002)    │
└──────┬───┘      │       └────┬─────┘
       │      ┌───▼───────────┐ │
       │      │ LLM Provider  │◄┘
       │      │ - OpenAI      │
       │      │ - ChatAnywhere│
       │      └───────────────┘
       │
┌──────▼──────────────────────────────┐
│  Knowledge Base (10 Documents)       │
│  - Q1销售报告  - 员工手册           │
│  - 技术架构    - 财务预算           │
│  - 客户案例    - 产品功能           │
│  - Q2销售计划  - 安全政策           │
│  - 技术栈      - 常见问题           │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│    基础设施 (Docker Lite)             │
│  - Redis (缓存)                      │
│  - SQLite (轻量数据库)               │
│  - Docker Compose (编排)             │
└──────────────────────────────────────┘
```

---

## 🔍 常见问题

### Q1: 如何检查容器是否运行？

```bash
docker-compose -f docker-compose.lite.yml ps
```

### Q2: 如何查看容器日志？

```bash
# 最后 50 行日志
docker-compose -f docker-compose.lite.yml logs --tail 50 qa_entry

# 实时日志
docker-compose -f docker-compose.lite.yml logs -f qa_entry

# 所有服务日志
docker-compose -f docker-compose.lite.yml logs -f
```

### Q3: 如何重新启动特定服务？

```bash
docker-compose -f docker-compose.lite.yml restart qa_entry
```

### Q4: 如何完全清除所有数据重新开始？

```bash
# 停止并删除所有容器和卷
docker-compose -f docker-compose.lite.yml down -v

# 重新启动
docker-compose -f docker-compose.lite.yml up -d
```

### Q5: 如何在容器中执行命令？

```bash
docker-compose -f docker-compose.lite.yml exec qa_entry bash
docker-compose -f docker-compose.lite.yml exec redis redis-cli
```

---

## 📈 系统要求

| 要求项 | 推荐值 | 最小值 |
|--------|--------|--------|
| 磁盘空间 | 5GB | 2GB |
| 内存 | 8GB | 4GB |
| CPU | 4核+ | 2核 |
| Docker | v20.10+ | v20.0+ |
| Docker Compose | v2.0+ | v1.29+ |

---

## 🚀 性能优化

### 1. 调整资源限制

编辑 `docker-compose.lite.yml` 中的 `services.X.deploy.resources`:

```yaml
services:
  qa_entry:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 2. 启用容器日志驱动

```yaml
services:
  qa_entry:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 3. 使用卷来持久化数据

```bash
# 创建卷
docker volume create qa_data

# 在 compose 文件中引用
volumes:
  - qa_data:/app/data
```

---

## 🔐 安全建议

### 1. 生产环境配置

- 使用强密码和环境变量
- 启用 HTTPS
- 限制网络访问
- 定期更新镜像

### 2. 敏感信息管理

```bash
# 使用 .env 文件存储敏感信息
export OPENAI_API_KEY="sk-proj-xxx"
export CHATANYWHERE_API_KEY="sk-xxx"

# 在 docker-compose 中使用
docker-compose --env-file .env -f docker-compose.lite.yml up -d
```

### 3. 监控和日志

```bash
# 监控资源使用
docker stats

# 查看容器事件
docker events

# 定期检查日志
docker-compose -f docker-compose.lite.yml logs --since 1h
```

---

## 📝 文件结构

```
AICommonPlatform/
├── docker-compose.lite.yml          # Docker Compose 配置
├── services/
│   ├── qa_entry/
│   │   ├── main.py                  # QA 入口服务
│   │   ├── services.py              # 业务逻辑
│   │   ├── Dockerfile.lite          # 轻量级 Dockerfile
│   │   └── requirements-lite.txt    # Python 依赖
│   ├── rag_service/
│   │   ├── main.py                  # RAG 服务
│   │   ├── Dockerfile.lite
│   │   └── requirements-lite.txt
│   ├── web_ui/
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── ... (其他服务)
└── README.md
```

---

## 🎓 学习资源

### Docker
- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 指南](https://docs.docker.com/compose/)
- [最佳实践](https://docs.docker.com/develop/dev-best-practices/)

### FastAPI
- [FastAPI 教程](https://fastapi.tiangolo.com/)
- [Pydantic 验证](https://docs.pydantic.dev/)

### AI/LLM
- [OpenAI API 文档](https://platform.openai.com/docs)
- [RAG 原理](https://docs.langchain.com/docs/modules/indexes/)
- [提示词工程](https://platform.openai.com/docs/guides/prompt-engineering)

---

## 📞 故障排除

### 问题: 容器无法连接到其他容器

**原因**: 网络配置问题

**解决**:
```bash
# 检查网络
docker network ls
docker network inspect ai_lite_net

# 重新创建网络
docker-compose -f docker-compose.lite.yml down
docker-compose -f docker-compose.lite.yml up -d
```

### 问题: 端口被占用

**解决**:
```bash
# 查看占用的进程
lsof -i :8001

# 杀死进程或修改 docker-compose.yml 中的端口
```

### 问题: 容器内 Python 模块缺失

**解决**:
```bash
# 更新 requirements-lite.txt
# 重新构建镜像
docker-compose -f docker-compose.lite.yml build --no-cache qa_entry
# 重启容器
docker-compose -f docker-compose.lite.yml restart qa_entry
```

---

## 🎉 完成!

现在您已拥有一个完整的、支持多个大模型的 AI 问答平台！

### 后续步骤:

1. ✅ 访问 Web UI (http://localhost:3000)
2. ✅ 配置您的 LLM API Key
3. ✅ 进行测试提问
4. ✅ 上传自定义知识库文档
5. ✅ 集成到您的业务系统

### 技术亮点:

- ✅ 真实大模型调用 (OpenAI + ChatAnywhere)
- ✅ 完整的 RAG 流程 (知识库检索 + LLM 生成)
- ✅ 轻量级 Docker 部署 (SQLite + Redis)
- ✅ 8 个微服务协同
- ✅ 10 个预置知识库文档
- ✅ 完整的错误处理和日志

---

**版本**: v1.2.0  
**最后更新**: 2026-01-27  
**状态**: ✅ 已验证并运行正常
