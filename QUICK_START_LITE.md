# 🚀 轻量级部署快速启动指南

## 📌 5分钟快速开始

### 1️⃣ 启动所有服务
```bash
cd /Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform
docker-compose -f docker-compose.lite.yml up -d
```

### 2️⃣ 验证服务状态
```bash
docker-compose -f docker-compose.lite.yml ps
```
✅ 所有 7 个服务应显示 "Up" 和 "healthy"

### 3️⃣ 初始化知识库（8 个样本文档）
```bash
curl -X POST http://localhost:8003/api/rag/init
```

### 4️⃣ 测试 Q&A 功能
```bash
curl -X POST http://localhost:8001/api/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","question":"销售报告"}'
```

### 5️⃣ 打开 Web UI
```
http://localhost:3000
```

---

## 🎯 核心功能

### 查询知识库
```bash
curl -X POST http://localhost:8003/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query_text":"销售","top_k":3}'
```

### 配置 LLM 提供商

#### 切换到 ChatAnywhere
```bash
curl -X POST http://localhost:8006/api/llm/config \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "chatanywhere",
    "api_key": "sk-your-key",
    "model": "gpt-3.5-turbo"
  }'
```

#### 查看当前配置
```bash
curl http://localhost:8006/api/llm/config
```

---

## 📊 服务端口一览

| 服务 | 端口 | 功能 |
|------|------|------|
| Web UI | 3000 | 前端界面 |
| QA Entry | 8001 | 问答入口 |
| Prompt Service | 8002 | Prompt 管理 |
| RAG Service | 8003 | 向量数据库 |
| Agent Service | 8004 | Agent 执行 |
| Integration | 8005 | 系统集成 |
| LLM Service | 8006 | LLM 接口 |

---

## ⚠️ 常见问题

### Q: 出现 "Connection refused" 错误？
```bash
# 检查服务是否全部启动
docker-compose -f docker-compose.lite.yml ps

# 等待 5-10 秒后重试
sleep 10
```

### Q: 如何查看服务日志？
```bash
# 查看特定服务
docker-compose -f docker-compose.lite.yml logs qa_entry -f

# 查看所有服务
docker-compose -f docker-compose.lite.yml logs -f
```

### Q: 如何停止所有服务？
```bash
docker-compose -f docker-compose.lite.yml down
```

### Q: 知识库数据存在哪里？
```
/Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform/data/documents/vector_store.db
```

---

## ✅ 部署完成标志

- ✅ 所有 7 个服务都是 "healthy"
- ✅ 不再需要 Redis（已移除）
- ✅ LLM 支持 OpenAI 和 ChatAnywhere
- ✅ 向量库预加载 8 个样本文档
- ✅ Q&A 功能正常工作

---

## 🎉 现在可以使用的功能

1. **实时问答** - 通过 Web UI 或 API 提问
2. **知识库查询** - 搜索已存储的文档
3. **LLM 提供商切换** - 在 OpenAI/ChatAnywhere 之间切换
4. **多语言支持** - 中英文问答
5. **性能统计** - 查看执行时间和置信度

---

**🚀 一切就绪，开始使用吧！**
