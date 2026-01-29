# AI Common Platform - API 文档

## 快速开始

### 1. 启动服务

```bash
# 使用 docker-compose 启动所有服务
docker-compose up -d

# 或使用启动脚本
bash scripts/start.sh up

# 或使用 Makefile
make up
```

### 2. 运行测试

```bash
# 运行API测试
python3 scripts/test_api.py

# 或使用 Makefile
make test
```

---

## API 端点文档

### 1. 问答入口服务 (QA Entry Service)
**地址**: `http://localhost:8001`

#### 健康检查
```
GET /health
```

响应:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-26T10:30:00",
  "service": "qa_entry",
  "version": "1.0.0"
}
```

#### 提问
```
POST /api/qa/ask
Content-Type: application/json

{
  "question": "今年Q1的销售额是多少?",
  "user_id": "user123",
  "session_id": "session_456",
  "context": {
    "department": "sales",
    "role": "manager"
  }
}
```

响应:
```json
{
  "id": "qa_12345",
  "question": "今年Q1的销售额是多少?",
  "answer": "根据我们的数据，Q1总销售额为5000万元，同比增长15%。",
  "sources": ["rag_doc_1", "erp_system"],
  "confidence": 0.95,
  "execution_time": 2.5,
  "question_type": "sales_inquiry",
  "status": "completed",
  "timestamp": "2024-01-26T10:30:00"
}
```

#### 获取历史问答
```
GET /api/qa/{qa_id}
```

#### 批量提问
```
POST /api/qa/batch
Content-Type: application/json

[
  {
    "question": "Q1销售额?",
    "user_id": "user123"
  },
  {
    "question": "员工总数?",
    "user_id": "user124"
  }
]
```

#### 获取统计
```
GET /api/qa/stats
```

---

### 2. Prompt服务 (Prompt Service)
**地址**: `http://localhost:8002`

#### 健康检查
```
GET /health
```

#### 获取所有模板
```
GET /api/prompts
```

响应:
```json
{
  "templates": [
    {
      "id": "sales_advisor",
      "name": "销售顾问",
      "role": "Sales Advisor",
      "description": "专注于销售数据和客户信息的顾问",
      "version": "1.0"
    },
    ...
  ],
  "total": 4
}
```

#### 获取特定模板
```
GET /api/prompts/{template_id}
```

#### 组装Prompt
```
POST /api/prompts/assemble
Content-Type: application/json

{
  "template_id": "sales_advisor",
  "variables": {
    "question": "今年Q1的销售额是多少?",
    "sales_data": "Q1销售额5000万元",
    "customer_info": "主要客户ABC公司"
  },
  "role": "Sales Advisor",
  "context": {
    "department": "sales"
  }
}
```

响应:
```json
{
  "prompt": "你是一名专业的销售顾问...",
  "template_id": "sales_advisor",
  "role": "Sales Advisor",
  "variable_count": 3
}
```

---

### 3. RAG服务 (RAG Service)
**地址**: `http://localhost:8003`

#### 搜索知识库
```
POST /api/rag/search
Content-Type: application/json

{
  "query": "销售",
  "top_k": 5,
  "category": "sales",
  "threshold": 0.5
}
```

响应:
```json
{
  "documents": [
    {
      "id": "doc_001",
      "title": "Q1销售报告",
      "content": "2024年Q1销售业绩：总销售额5000万元，同比增长15%。",
      "category": "sales",
      "tags": ["销售", "报告", "Q1"],
      "source": "erp_system"
    }
  ],
  "total": 1,
  "search_time": 0.05
}
```

#### 获取文档列表
```
GET /api/rag/documents
GET /api/rag/documents?category=sales
```

#### 创建文档
```
POST /api/rag/documents
Content-Type: application/json

{
  "title": "新文档",
  "content": "文档内容...",
  "category": "sales",
  "tags": ["新闻", "市场"],
  "source": "internal"
}
```

#### 上传文档
```
POST /api/rag/upload
Content-Type: multipart/form-data

file=<binary_file_content>
```

---

### 4. Agent服务 (Agent Service)
**地址**: `http://localhost:8004`

#### 获取工具列表
```
GET /api/agent/tools
```

响应:
```json
{
  "tools": [
    {
      "id": "erp_sales",
      "name": "ERP销售查询",
      "description": "从ERP系统查询销售数据",
      "tool_type": "erp",
      "parameters": {
        "time_range": "str",
        "department": "str"
      }
    }
  ],
  "total": 3
}
```

#### 执行Agent任务
```
POST /api/agent/execute
Content-Type: application/json

{
  "question": "查询Q1销售数据和员工信息",
  "tools": ["erp_sales", "hrm_employee"],
  "context": {
    "year": "2024",
    "quarter": "Q1"
  }
}
```

响应:
```json
{
  "task_id": "task_12345",
  "status": "success",
  "results": {
    "erp_sales": {
      "tool": "erp_sales",
      "status": "success",
      "data": {...}
    }
  },
  "executed_tools": ["erp_sales"],
  "execution_time": 1.5
}
```

---

### 5. 企业系统集成服务 (Integration Service)
**地址**: `http://localhost:8005`

#### 查询集成系统列表
```
GET /api/integration/systems
```

#### ERP - 查询销售数据
```
GET /api/integration/erp/sales/{year}/{quarter}

# 示例
GET /api/integration/erp/sales/2024/Q1
```

响应:
```json
{
  "status": "success",
  "system": "erp",
  "data": {
    "amount": 5000,
    "growth": 0.15,
    "top_products": ["产品A", "产品B"],
    "currency": "万元"
  }
}
```

#### ERP - 查询库存
```
GET /api/integration/erp/inventory
GET /api/integration/erp/inventory?product_name=产品A
```

#### HRM - 查询部门
```
GET /api/integration/hrm/departments
```

#### HRM - 查询员工
```
GET /api/integration/hrm/employees
GET /api/integration/hrm/employees?department=sales
GET /api/integration/hrm/employees/{employee_id}
```

#### CRM - 查询客户
```
GET /api/integration/crm/customers
GET /api/integration/crm/customers/{customer_id}
```

#### 财务 - 查询预算
```
GET /api/integration/finance/budget/{year}

# 示例
GET /api/integration/finance/budget/2024
```

---

### 6. LLM服务 (LLM Service)
**地址**: `http://localhost:8006`

#### 获取可用模型
```
GET /api/llm/models
```

响应:
```json
{
  "models": ["gpt-3.5-turbo", "gpt-4", "qwen-max", "ernie-3.5"],
  "details": {
    "gpt-3.5-turbo": {
      "provider": "openai",
      "max_tokens": 4096,
      "cost_per_1k_input": 0.001
    }
  },
  "total": 4
}
```

#### 文本完成
```
POST /api/llm/complete
Content-Type: application/json

{
  "prompt": "今年Q1的销售额",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 2000,
  "system_prompt": "你是一名专业的商业分析师"
}
```

#### 聊天
```
POST /api/llm/chat
Content-Type: application/json

{
  "messages": [
    {
      "role": "system",
      "content": "你是一名专业的商业分析师"
    },
    {
      "role": "user",
      "content": "今年Q1的销售额是多少?"
    }
  ],
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

#### 获取嵌入向量
```
POST /api/llm/embedding
Content-Type: application/json

{
  "text": "今年Q1的销售额是多少?",
  "model": "text-embedding-3-small"
}
```

#### 计算Token数量
```
POST /api/llm/tokens/count
Content-Type: application/json

{
  "text": "今年Q1的销售额是多少?",
  "model": "gpt-3.5-turbo"
}
```

---

## 常见问答

### Q: 如何添加自己的Prompt模板？
A: POST到 `/api/prompts/create` 端点，提供模板信息即可。

### Q: 如何上传企业自己的知识库文档？
A: 使用RAG服务的 `/api/rag/upload` 或 `/api/rag/documents` 端点上传。

### Q: 如何集成新的企业系统？
A: 在Integration Service中添加新的接口实现，参考现有的ERP、HRM、CRM实现。

### Q: 如何替换LLM提供商？
A: 修改 `.env` 中的 `LLM_PROVIDER` 和相关配置，然后重启服务。

### Q: 如何查看监控和日志？
A: 
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Docker日志: `docker-compose logs -f`

---

## 故障排查

### 容器无法启动
```bash
# 查看日志
docker-compose logs <service_name>

# 检查资源占用
docker-compose ps

# 重启服务
docker-compose restart
```

### 服务无法通信
```bash
# 测试网络连接
docker-compose exec <service> ping <other_service>

# 查看网络
docker network ls
```

### 数据库连接失败
```bash
# 检查PostgreSQL状态
docker-compose ps postgres

# 查看PostgreSQL日志
docker-compose logs postgres
```

---

## 更多信息

- **项目主页**: README.md
- **源代码**: services/ 目录
- **脚本工具**: scripts/ 目录
- **配置文件**: docker-compose.yml, .env
