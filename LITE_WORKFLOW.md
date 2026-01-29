# 轻量级版本工作流指南

## 🎯 3 步启动

### Step 1：准备环境
```bash
# 确保安装了 Docker 和 Docker Compose
docker --version
docker-compose --version

# 进入项目目录
cd AICommonPlatform
```

### Step 2：启动轻量版本
```bash
# 自动启动（推荐）
bash start-lite.sh

# 或手动启动
docker-compose -f docker-compose.lite.yml up -d
```

### Step 3：访问界面
```bash
# 打开浏览器访问
open http://localhost:3000

# 或者使用 curl 测试
curl http://localhost:3000
```

---

## 📊 服务架构（轻量版）

```
┌──────────────────────────────────────────────┐
│              Web UI (port 3000)               │
│           交互式问答 + 状态监控               │
└────────────────────┬─────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼────┐  ┌───▼────┐  ┌──▼─────┐
    │ QA/RAG │  │ Prompt │  │ Agent  │
    │ (8001) │  │(8002)  │  │(8004)  │
    └───┬────┘  └───┬────┘  └──┬─────┘
        │            │          │
        └────────────┼──────────┘
                     │
            ┌────────▼────────┐
            │   Redis缓存     │
            │  (port 6379)    │
            └─────────────────┘
```

---

## 🔧 常用操作

### 查看服务状态
```bash
# 列出所有容器
docker-compose -f docker-compose.lite.yml ps

# 输出示例：
# NAME                    STATUS
# ai_lite_web_ui          Up 2 minutes
# ai_lite_qa_entry        Up 2 minutes
# ai_lite_prompt_service  Up 2 minutes
# ai_lite_rag_service     Up 2 minutes
# ai_lite_agent_service   Up 2 minutes
# ai_lite_integration     Up 2 minutes
# ai_lite_llm_service     Up 2 minutes
# ai_lite_redis           Up 2 minutes
```

### 查看日志
```bash
# 所有服务的日志
docker-compose -f docker-compose.lite.yml logs -f

# 特定服务的日志（实时）
docker-compose -f docker-compose.lite.yml logs -f web_ui

# 查看最近 100 行日志
docker-compose -f docker-compose.lite.yml logs --tail=100 qa_entry

# 保存日志到文件
docker-compose -f docker-compose.lite.yml logs > service_logs.txt
```

### 进入容器调试
```bash
# 进入 web_ui 容器
docker-compose -f docker-compose.lite.yml exec web_ui /bin/bash

# 在容器内执行命令
docker-compose -f docker-compose.lite.yml exec qa_entry ls -la /app

# 查看容器环境变量
docker-compose -f docker-compose.lite.yml exec qa_entry env
```

### 重启服务
```bash
# 重启特定服务
docker-compose -f docker-compose.lite.yml restart web_ui

# 重启所有服务
docker-compose -f docker-compose.lite.yml restart

# 重新构建并启动
docker-compose -f docker-compose.lite.yml up -d --build
```

### 停止和清理
```bash
# 停止所有容器（保留）
docker-compose -f docker-compose.lite.yml stop

# 启动已停止的容器
docker-compose -f docker-compose.lite.yml start

# 完全删除容器
docker-compose -f docker-compose.lite.yml down

# 删除容器和数据卷
docker-compose -f docker-compose.lite.yml down -v

# 清理 Docker 缓存
docker system prune -a
```

---

## 📝 常见工作流

### 工作流 1：学习服务架构

1. **启动轻量版本**
   ```bash
   bash start-lite.sh
   ```

2. **打开 Web UI**
   - 访问 http://localhost:3000
   - 查看"服务状态"标签页
   - 了解各个服务的职责

3. **查看服务日志**
   ```bash
   docker-compose -f docker-compose.lite.yml logs -f
   ```

4. **理解调用流程**
   - 在 Web UI 中提交问题
   - 观察日志中的服务调用链

### 工作流 2：调试 API

1. **进入 qa_entry 容器**
   ```bash
   docker-compose -f docker-compose.lite.yml exec qa_entry /bin/bash
   ```

2. **测试 API**
   ```bash
   # 在容器内测试本地 API
   curl http://localhost:8000/health
   
   # 测试其他服务
   curl http://prompt_service:8000/health
   ```

3. **查看代码**
   ```bash
   # 查看当前文件结构
   ls -la /app
   
   # 查看主文件
   cat /app/main.py
   ```

### 工作流 3：修改代码后重新启动

1. **编辑本地代码**
   ```bash
   # 在你的编辑器中修改服务代码
   # 例如：services/qa_entry/main.py
   ```

2. **重新构建并启动**
   ```bash
   # 方式 1：重新构建单个服务
   docker-compose -f docker-compose.lite.yml up -d --build qa_entry
   
   # 方式 2：重新构建所有服务
   docker-compose -f docker-compose.lite.yml up -d --build
   ```

3. **验证更改**
   ```bash
   # 查看日志确认启动成功
   docker-compose -f docker-compose.lite.yml logs -f qa_entry
   
   # 测试 API
   curl http://localhost:8001/health
   ```

### 工作流 4：添加新的知识库文档

1. **创建或修改文档**
   ```bash
   # 文档放在 data/documents/ 目录
   mkdir -p data/documents
   echo "问题: 如何使用AI Platform?
   答案: AI Platform 是一个企业级AI能力层..." > data/documents/faq.txt
   ```

2. **RAG 服务会自动检索**
   - 在 Web UI 中搜索相关内容
   - RAG 服务会从本地文档中检索

### 工作流 5：整合真实的 LLM API

1. **设置 API Key**
   ```bash
   # 编辑 docker-compose.lite.yml，添加 API Key
   # 在 llm_service 的 environment 中添加
   OPENAI_API_KEY: sk-your-key-here
   ```

2. **重启 LLM 服务**
   ```bash
   docker-compose -f docker-compose.lite.yml up -d --build llm_service
   ```

3. **在 Web UI 中测试**
   - 提交问题
   - 应用将调用真实 LLM 生成回答

---

## 🧪 快速测试

### 测试 API 连通性

```bash
# 测试所有服务健康状态
for port in 8001 8002 8003 8004 8005 8006 3000; do
    echo "Testing port $port..."
    curl -s http://localhost:$port/health || echo "Failed"
done
```

### 测试 QA 流程

```bash
# 1. 提交问题
curl -X POST http://localhost:8001/api/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是AI?", "user_id": "test_user"}'

# 2. 查看 Prompt 模板
curl http://localhost:8002/api/prompts

# 3. 搜索知识库
curl -X POST http://localhost:8003/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "AI", "top_k": 5}'
```

### 测试 Web UI

```bash
# 确保 Web UI 正常运行
curl -s http://localhost:3000 | head -20

# 获取服务状态
curl http://localhost:3000/api/services/status
```

---

## 💡 调试技巧

### 1. 查看容器详细信息
```bash
# 查看容器的挂载点
docker-compose -f docker-compose.lite.yml exec web_ui mount | grep /app

# 查看容器的 IP 地址
docker-compose -f docker-compose.lite.yml exec web_ui hostname -I

# 查看网络连接
docker-compose -f docker-compose.lite.yml exec web_ui netstat -tlnp
```

### 2. 检查网络通信
```bash
# 测试容器间通信
docker-compose -f docker-compose.lite.yml exec web_ui ping prompt_service

# 测试 DNS 解析
docker-compose -f docker-compose.lite.yml exec web_ui nslookup qa_entry

# 查看网络信息
docker network ls
docker network inspect aicommonplatform_ai_lite_net
```

### 3. 查看容器日志的更多细节
```bash
# 查看具体时间范围的日志
docker-compose -f docker-compose.lite.yml logs --since 10m

# 查看具体时间的日志
docker-compose -f docker-compose.lite.yml logs --until 5m

# 按关键词过滤日志
docker-compose -f docker-compose.lite.yml logs | grep ERROR
docker-compose -f docker-compose.lite.yml logs | grep "qa_entry"
```

---

## 🔄 版本切换

### 从轻量版切换到标准版

```bash
# 1. 停止轻量版本
docker-compose -f docker-compose.lite.yml down

# 2. 启动标准版本（会自动拉取额外镜像）
docker-compose up -d

# 3. 等待 PostgreSQL 和 Milvus 启动（3-5 分钟）
docker-compose ps

# 4. 验证
curl http://localhost:3000
```

### 从标准版切换回轻量版

```bash
# 1. 停止标准版本
docker-compose down

# 2. 启动轻量版本
docker-compose -f docker-compose.lite.yml up -d

# 3. 立即访问（1-2 分钟后）
open http://localhost:3000
```

---

## 📖 推荐学习顺序

### Day 1-2: 架构理解
- [ ] 启动轻量版本
- [ ] 浏览 Web UI
- [ ] 查看各服务日志
- [ ] 理解服务间调用关系

### Day 3-5: API 学习
- [ ] 使用 curl 测试各个 API
- [ ] 理解请求/响应格式
- [ ] 修改 Prompt 模板
- [ ] 添加知识库文档

### Day 6-7: 实践扩展
- [ ] 修改源代码
- [ ] 重新构建服务
- [ ] 集成自己的业务逻辑
- [ ] 测试完整流程

---

**祝你学习愉快！有问题随时查看日志和文档 📚**
