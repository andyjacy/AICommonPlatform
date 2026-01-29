# AI Common Platform - 快速参考

## 🚀 快速启动

### 最简单的启动方式

```bash
cd AICommonPlatform
docker-compose up -d
python3 scripts/test_api.py
```

### 常用命令

```bash
# 启动/停止
make up          # 启动所有服务
make down        # 停止所有服务
make restart     # 重启服务
docker-compose logs -f  # 查看日志

# 测试
make test        # 运行API测试
python3 scripts/test_api.py

# 开发
make dev-qa      # 开发QA服务（本地运行）
make dev-rag     # 开发RAG服务（本地运行）
```

---

## 📋 服务端口表

| 服务 | 地址 | 端口 |
|------|------|------|
| **QA Entry** | http://localhost:8001 | 8001 |
| **Prompt Service** | http://localhost:8002 | 8002 |
| **RAG Service** | http://localhost:8003 | 8003 |
| **Agent Service** | http://localhost:8004 | 8004 |
| **Integration** | http://localhost:8005 | 8005 |
| **LLM Service** | http://localhost:8006 | 8006 |
| **Prometheus** | http://localhost:9090 | 9090 |
| **Grafana** | http://localhost:3000 | 3000 |
| **PostgreSQL** | localhost:5432 | 5432 |
| **Redis** | localhost:6379 | 6379 |
| **Milvus** | localhost:19530 | 19530 |

---

## 🔑 基本凭证

| 服务 | 用户名 | 密码 |
|------|--------|------|
| PostgreSQL | admin | ai_platform_2024 |
| Redis | (无用户名) | ai_redis_2024 |
| Grafana | admin | admin |

---

## 📡 核心API端点

### 问答入口

```bash
# 提问
curl -X POST http://localhost:8001/api/qa/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "今年Q1的销售额是多少?",
    "user_id": "user123"
  }'

# 获取历史记录
curl http://localhost:8001/api/qa/{qa_id}

# 获取统计
curl http://localhost:8001/api/qa/stats
```

### Prompt模板

```bash
# 获取所有模板
curl http://localhost:8002/api/prompts

# 组装Prompt
curl -X POST http://localhost:8002/api/prompts/assemble \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "sales_advisor",
    "variables": {
      "question": "Q1销售额?",
      "sales_data": "5000万元",
      "customer_info": "ABC公司"
    }
  }'
```

### 知识库搜索

```bash
# 搜索文档
curl -X POST http://localhost:8003/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "销售",
    "top_k": 5
  }'

# 上传文档
curl -X POST http://localhost:8003/api/rag/upload \
  -F "file=@document.pdf"
```

### Agent工具

```bash
# 获取工具列表
curl http://localhost:8004/api/agent/tools

# 执行任务
curl -X POST http://localhost:8004/api/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "question": "查询Q1销售数据",
    "tools": ["erp_sales", "hrm_employee"]
  }'
```

### 企业系统集成

```bash
# 查询ERP销售数据
curl http://localhost:8005/api/integration/erp/sales/2024/Q1

# 查询HRM部门
curl http://localhost:8005/api/integration/hrm/departments

# 查询CRM客户
curl http://localhost:8005/api/integration/crm/customers

# 查询财务预算
curl http://localhost:8005/api/integration/finance/budget/2024
```

### LLM服务

```bash
# 获取模型列表
curl http://localhost:8006/api/llm/models

# 文本完成
curl -X POST http://localhost:8006/api/llm/complete \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "今年Q1的销售额",
    "model": "gpt-3.5-turbo"
  }'

# 文本聊天
curl -X POST http://localhost:8006/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "今年Q1的销售额是多少?"}
    ]
  }'
```

---

## 🏗️ 项目结构速查

```
AICommonPlatform/
├── docker-compose.yml          ← Docker编排配置
├── Makefile                    ← 快捷命令
├── .env                        ← 环境变量
├── requirements.txt            ← Python依赖
│
├── services/
│   ├── qa_entry/              ← 问答入口
│   ├── prompt_service/        ← Prompt管理
│   ├── rag_service/           ← 知识库和检索
│   ├── agent_service/         ← Agent执行
│   ├── integration/           ← 企业系统集成
│   └── llm_service/           ← LLM接口
│
├── scripts/
│   ├── start.sh               ← 启动脚本
│   ├── test_api.py            ← API测试
│   └── init_db.sql            ← 数据库初始化
│
└── docs/
    ├── API.md                 ← API文档
    ├── DEVELOPMENT.md         ← 开发指南
    ├── ARCHITECTURE.md        ← 架构文档
    └── QUICKSTART.md          ← 本文件
```

---

## 🐛 常见问题排查

### Q: Docker容器无法启动
```bash
# 查看详细错误信息
docker-compose logs <service_name>

# 重建镜像
docker-compose build --no-cache <service_name>

# 重启服务
docker-compose restart <service_name>
```

### Q: 无法连接到数据库
```bash
# 确保PostgreSQL正在运行
docker-compose ps postgres

# 检查连接参数
docker-compose exec postgres psql -U admin -d ai_platform

# 查看PostgreSQL日志
docker-compose logs postgres
```

### Q: Redis连接失败
```bash
# 测试Redis连接
docker-compose exec redis redis-cli ping

# 检查Redis密码
docker-compose exec redis redis-cli -a ai_redis_2024 ping
```

### Q: API请求超时
```bash
# 增加超时时间
# 修改services配置中的timeout值

# 检查服务健康状态
curl http://localhost:8001/health
curl http://localhost:8002/health
# ...其他服务

# 查看服务日志
docker-compose logs <service_name>
```

### Q: 内存/磁盘不足
```bash
# 清理未使用的Docker资源
docker system prune

# 清理所有数据（谨慎！）
make clean
# 或
docker-compose down -v
```

---

## 📊 监控和调试

### 查看实时日志
```bash
# 所有服务的日志
docker-compose logs -f

# 特定服务的日志
docker-compose logs -f qa_entry

# 最后100行日志
docker-compose logs --tail=100 qa_entry

# 跟随特定时间范围的日志
docker-compose logs -f --since 2024-01-26T10:00:00Z
```

### 进入容器调试
```bash
# 进入容器的bash
docker-compose exec qa_entry /bin/bash

# 在容器中运行命令
docker-compose exec qa_entry python -c "import os; print(os.environ)"

# 安装额外工具用于调试
docker-compose exec qa_entry apt-get install -y curl
```

### 查看容器资源使用
```bash
# Docker stats
docker stats

# 容器进程
docker top <container_id>

# 容器磁盘占用
docker system df
```

### 访问监控和日志系统
```
Prometheus: http://localhost:9090
  - 查询: http://localhost:9090/graph
  - 告警: http://localhost:9090/alerts

Grafana: http://localhost:3000
  - 用户名: admin
  - 密码: admin
```

---

## 🔧 常用配置修改

### 修改LLM提供商

编辑 `.env` 文件：
```bash
# 使用OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# 或使用阿里云
LLM_PROVIDER=aliyun
ALIYUN_API_KEY=your-key

# 或使用百度
LLM_PROVIDER=baidu
BAIDU_API_KEY=your-key
```

### 修改数据库连接
```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@host:5432/dbname

# 本地PostgreSQL
DATABASE_URL=postgresql://admin:ai_platform_2024@localhost:5432/ai_platform
```

### 修改Redis连接
```bash
# Redis
REDIS_URL=redis://:password@host:6379/0

# 本地Redis
REDIS_URL=redis://:ai_redis_2024@localhost:6379/0
```

修改后重启服务：
```bash
docker-compose up -d
```

---

## 📚 Prompt模板参考

### 销售顾问模板

```
你是一名专业的销售顾问，具备以下特点：
- 专业的销售知识和行业经验
- 关注销售数据、客户信息、市场趋势
- 提供数据驱动的建议

用户问题：{question}
销售数据：{sales_data}
客户信息：{customer_info}

请提供专业的销售建议：
```

### HR顾问模板

```
你是一名专业的人力资源顾问，具备以下特点：
- 人力资源管理的专业知识
- 关注员工信息、薪资福利、考勤记录
- 遵守相关法规和公司政策

用户问题：{question}
员工信息：{employee_info}
福利政策：{benefits_policy}

请提供专业的HR建议：
```

### 技术顾问模板

```
你是一名资深技术架构师，具备以下特点：
- 深厚的技术知识和系统设计经验
- 关注系统架构、技术栈、最佳实践
- 提供可行的技术解决方案

用户问题：{question}
系统架构：{system_architecture}
技术约束：{technical_constraints}

请提供专业的技术建议：
```

---

## 🚢 部署清单

### 本地测试
- [ ] 安装Docker和Docker Compose
- [ ] 克隆项目
- [ ] 运行 `docker-compose up -d`
- [ ] 运行 `python3 scripts/test_api.py`
- [ ] 所有测试通过✓

### 生产部署前
- [ ] 生成所有密钥和Token
- [ ] 配置生产数据库
- [ ] 配置LLM API密钥
- [ ] 启用HTTPS和认证
- [ ] 配置日志聚合
- [ ] 配置备份和恢复
- [ ] 进行安全审计
- [ ] 进行性能测试
- [ ] 准备运维文档
- [ ] 培训运维人员

---

## 📞 获取帮助

### 查看文档
- API文档: `docs/API.md`
- 开发指南: `docs/DEVELOPMENT.md`
- 架构设计: `docs/ARCHITECTURE.md`

### 调试技巧
1. 查看Docker日志: `docker-compose logs -f <service>`
2. 测试服务健康: `curl http://localhost:<port>/health`
3. 检查网络连接: `docker-compose exec <service> ping <other_service>`
4. 查看数据库: `docker-compose exec postgres psql -U admin -d ai_platform`

### 常用工具
- **httpie**: 更好用的curl
- **jq**: JSON处理
- **dbeaver**: 数据库GUI工具
- **insomnia/postman**: API测试工具

---

## ✨ 快速体验示例

### 完整的问答流程

```bash
# 1. 启动所有服务
docker-compose up -d
sleep 10

# 2. 提问一个关于销售的问题
curl -X POST http://localhost:8001/api/qa/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "今年Q1的销售额是多少?",
    "user_id": "user123",
    "context": {"department": "sales"}
  }'

# 3. 获取回复的详细信息
# 记下返回的 qa_id，然后查询历史
curl http://localhost:8001/api/qa/{qa_id}

# 4. 查看Prompt模板
curl http://localhost:8002/api/prompts

# 5. 从知识库搜索相关信息
curl -X POST http://localhost:8003/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "销售", "top_k": 3}'

# 6. 调用Agent工具获取实时数据
curl -X POST http://localhost:8004/api/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "question": "查询Q1销售数据",
    "tools": ["erp_sales"]
  }'

# 7. 查看可用的企业系统
curl http://localhost:8005/api/integration/systems

# 8. 在Grafana中查看指标
# 打开 http://localhost:3000 (admin/admin)
```

---

## 📖 学习路线

1. **入门**: 本文件
2. **API使用**: `docs/API.md`
3. **开发指南**: `docs/DEVELOPMENT.md`
4. **架构深入**: `docs/ARCHITECTURE.md`
5. **源代码**: `services/` 目录

---

**最后更新**: 2024年1月26日

祝您使用愉快！🎉
