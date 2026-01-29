# AI Common Platform - 架构设计文档

## 系统架构概览

### 高层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端应用                                  │
│                    (Web / Mobile / Desktop)                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    API Gateway
                    (8001-8006)
                           │
        ┌──────────────────┼──────────────────┬──────────────────┐
        │                  │                  │                  │
    ┌───▼────┐       ┌───▼────┐        ┌───▼────┐        ┌───▼────┐
    │   QA    │       │Prompt  │        │  RAG   │        │ Agent  │
    │ Entry   │       │Service │        │Service │        │Service │
    └───┬────┘       └───┬────┘        └───┬────┘        └───┬────┘
        │                │                  │                 │
        └────────────────┼──────────────────┼─────────────────┘
                         │                  │
                    ┌────▼──────────────────▼────┐
                    │   Integration Service      │
                    │   (ERP/CRM/HRM/Finance)   │
                    └────┬──────────────────┬────┘
                         │                  │
            ┌────────────▼────────┐    ┌───▼─────────────┐
            │  LLM Service        │    │  External APIs  │
            │ (OpenAI/Aliyun...)  │    │  (ERP/CRM...)   │
            └────────────────────┘    └─────────────────┘
```

### 数据流

```
用户问题
   │
   ▼
┌─────────────┐
│ QA Entry    │ → 分类和意图识别
│ Service     │
└──────┬──────┘
       │
       ├─────────────────┬────────────────┐
       │                 │                │
       ▼                 ▼                ▼
  ┌────────┐    ┌──────────┐      ┌────────────┐
  │  RAG   │    │  Agent   │      │LLM Service │
  │Service │    │ Service  │      │ (Prompt)   │
  └───┬────┘    └────┬─────┘      └──────┬─────┘
      │              │                   │
      └──────────────┼───────────────────┘
                     │
                     ▼
            ┌──────────────────┐
            │  结果汇总和排序   │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │  返回最终答案     │
            └──────────────────┘
```

---

## 核心服务设计

### 1. QA Entry Service (问答入口)

**职责：**
- 接收用户自然语言问题
- 问题分类和意图识别
- 路由到不同的处理模块
- 结果汇总和返回

**关键特性：**
- 缓存热点问题
- 会话管理
- 多轮对话支持
- 审计日志记录

**技术栈：**
- FastAPI
- Redis (缓存)
- PostgreSQL (存储)

### 2. Prompt Service (提示词管理)

**职责：**
- 管理Prompt模板库
- 角色系统设计和管理
- 动态Prompt组装
- 版本控制

**Prompt模板类型：**
- 销售顾问: 关注销售数据、客户信息
- HR顾问: 关注员工、薪资、福利
- 技术顾问: 关注架构、技术方案
- 财务顾问: 关注财务、预算

**API：**
```
GET  /api/prompts                      # 获取模板列表
GET  /api/prompts/{id}                 # 获取特定模板
POST /api/prompts/assemble             # 组装Prompt
POST /api/prompts/create               # 创建新模板
```

### 3. RAG Service (检索增强生成)

**职责：**
- 知识库文档管理
- 向量化存储和检索
- 相似度搜索
- 文档分类

**数据结构：**
```python
{
    "id": "doc_001",
    "title": "Q1销售报告",
    "content": "...",
    "category": "sales",
    "tags": ["销售", "Q1"],
    "embedding": [...],  # 向量表示
    "source": "erp_system"
}
```

**检索流程：**
1. 对用户问题进行向量化
2. 在Milvus中进行相似度搜索
3. 过滤和排序结果
4. 返回Top-K文档

### 4. Agent Service (Agent执行)

**职责：**
- Tool定义和管理
- Tool调用编排
- 工作流执行
- 结果验证

**支持的工具类型：**
- ERP工具: 查询销售、库存等
- CRM工具: 查询客户信息
- HRM工具: 查询员工、部门
- 财务工具: 查询预算、报表
- 分析工具: 数据分析

**Tool定义：**
```python
{
    "id": "erp_sales",
    "name": "ERP销售查询",
    "type": "erp",
    "parameters": {
        "time_range": "str",
        "department": "str"
    },
    "endpoint": "http://erp.example.com/sales"
}
```

### 5. Integration Service (企业系统集成)

**职责：**
- 集成企业各类系统
- 数据转换和适配
- 错误处理和重试
- 日志和监控

**集成的系统：**
- ERP系统: 销售、采购、库存、财务
- CRM系统: 客户、订单、合同
- HRM系统: 员工、薪资、考勤、培训
- 财务系统: 预算、报表、成本
- 自定义系统: 支持扩展

**API设计模式：**
```
GET  /api/integration/{system}/{resource}
GET  /api/integration/{system}/{resource}/{id}
POST /api/integration/{system}/{resource}
```

### 6. LLM Service (大模型接口)

**职责：**
- 大模型API调用
- 模型管理和切换
- Token计费
- 缓存优化

**支持的模型提供商：**
- OpenAI: GPT-3.5, GPT-4
- 阿里云: 通义千问
- 百度: 文心一言
- 本地模型: 支持本地部署

**API端点：**
```
GET  /api/llm/models                   # 获取模型列表
POST /api/llm/complete                 # 文本完成
POST /api/llm/chat                     # 聊天
POST /api/llm/embedding                # 获取向量
POST /api/llm/tokens/count             # 计算Token
```

---

## 数据持久化

### PostgreSQL Schema

**主要表：**

1. **qa_records** (问答记录)
   - id, user_id, question, answer
   - question_type, confidence, status
   - created_at, updated_at

2. **documents** (知识库文档)
   - id, title, content, category
   - tags, source, embedding
   - created_at, updated_at

3. **prompt_templates** (Prompt模板)
   - id, name, role, content
   - version, variables, created_at

4. **agent_tasks** (Agent任务)
   - id, question, tools, status
   - results, execution_time, created_at

5. **user_sessions** (用户会话)
   - id, user_id, context, last_activity

6. **llm_usage** (LLM使用记录)
   - id, model, tokens, cost, created_at

7. **audit_logs** (审计日志)
   - id, user_id, action, resource, created_at

### Redis缓存策略

**缓存键设计：**
```
qa_cache:{question_hash}           # 问答结果缓存
user_session:{user_id}             # 用户会话
prompt_template:{template_id}      # Prompt模板缓存
rag_search:{query_hash}            # 搜索结果缓存
```

**过期时间：**
- 问答结果: 24小时
- 用户会话: 30天
- Prompt模板: 30天
- 搜索结果: 7天

### Milvus向量数据库

**集合设计：**
```python
{
    "collection_name": "documents",
    "fields": [
        {"name": "id", "type": "VARCHAR", "params": {"max_length": 100}},
        {"name": "content_vector", "type": "FLOAT_VECTOR", "params": {"dim": 1536}},
        {"name": "document_id", "type": "VARCHAR"},
        {"name": "category", "type": "VARCHAR"}
    ],
    "primary_field": "id",
    "vector_field": "content_vector"
}
```

---

## 通信协议

### 服务间通信

**同步通信：**
- HTTP/REST (主要方式)
- JSON格式数据
- 使用httpx库进行异步请求

**异步通信（可选）：**
- Redis Pub/Sub
- RabbitMQ
- Celery任务队列

### 请求/响应格式

**请求：**
```json
{
  "question": "...",
  "user_id": "...",
  "context": {...}
}
```

**响应：**
```json
{
  "id": "qa_12345",
  "status": "success",
  "data": {...},
  "timestamp": "2024-01-26T10:30:00Z",
  "execution_time": 2.5
}
```

**错误响应：**
```json
{
  "status": "error",
  "error": {
    "code": "SERVICE_ERROR",
    "message": "具体错误信息",
    "details": {...}
  }
}
```

---

## 安全设计

### 认证与授权

```
┌─────────────┐
│   API Key   │
│  (Optional) │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Token Validation   │
│   (JWT/Custom)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Permission Check    │
│  (Role-based)       │
└──────┬──────────────┘
       │
       ▼
  Request Processing
```

### 数据安全

- 敏感数据加密存储
- 日志不记录密码和令牌
- HTTPS传输
- SQL注入防护
- XSS防护

### 审计和合规

- 所有操作记录到audit_logs
- 用户行为追踪
- 数据访问控制
- 定期安全审计

---

## 扩展性设计

### 水平扩展

```
┌─────────────┐
│  Load       │
│  Balancer   │
│  (Nginx)    │
└────┬────┬───┘
     │    │
  ┌──▼─┐┌─▼──┐
  │ QA │ QA  │  (多个实例)
  └────┴─────┘
```

### 服务发现

- Docker Compose DNS (开发环境)
- Kubernetes Service (生产环境)
- Consul / Eureka (可选)

### 数据库扩展

- 读写分离
- 分库分表
- 主从复制
- 缓存层

---

## 监控和日志

### Prometheus指标

```
ai_platform_request_total{service="qa_entry", method="POST", endpoint="/api/qa/ask", status="200"}
ai_platform_request_duration_seconds{service="qa_entry", method="POST", endpoint="/api/qa/ask"}
ai_platform_qa_processing_time_seconds
ai_platform_llm_tokens_used{model="gpt-3.5-turbo"}
ai_platform_database_query_duration_seconds
```

### 日志策略

**日志级别：**
- ERROR: 错误和异常
- WARNING: 警告信息
- INFO: 重要业务事件
- DEBUG: 调试信息

**日志格式：**
```json
{
  "timestamp": "2024-01-26T10:30:00Z",
  "level": "INFO",
  "service": "qa_entry",
  "request_id": "req_12345",
  "user_id": "user123",
  "action": "ask_question",
  "message": "问题处理完成",
  "duration": 2.5
}
```

---

## 性能指标

### 目标SLA

| 指标 | 目标 | 说明 |
|------|------|------|
| 可用性 | 99.9% | 月度可用时间 |
| 响应时间 | <3s | P95响应时间 |
| 吞吐量 | >100 QPS | 每秒查询数 |
| 错误率 | <0.1% | 请求错误比例 |

### 性能优化策略

1. **缓存优化**
   - Redis多级缓存
   - 智能缓存失效
   - 缓存预热

2. **数据库优化**
   - 索引优化
   - 查询优化
   - 连接池管理

3. **网络优化**
   - 请求压缩
   - 批量处理
   - 异步处理

---

## 部署架构

### 开发环境

```
Local Machine
├── Docker Compose
├── 6个应用服务
├── PostgreSQL
├── Redis
└── Milvus
```

### 生产环境

```
Kubernetes Cluster
├── Ingress (API Gateway)
├── Service Mesh (Istio)
├── Pods (应用服务)
├── ConfigMap (配置)
├── Secrets (敏感信息)
├── PVC (持久化)
├── RDS (PostgreSQL)
├── Redis Cache
├── Elasticsearch (日志)
└── Prometheus/Grafana (监控)
```

---

## 故障恢复

### 健康检查

```
每30秒检查一次服务健康状态
├── HTTP /health endpoint
├── 数据库连接
├── Redis连接
└── 外部依赖
```

### 自动恢复

- 服务容器自动重启
- 数据库连接池自动恢复
- Redis连接自动重连
- 外部API调用自动重试

### 数据备份

- 数据库: 每天完整备份 + 每小时增量备份
- Redis: AOF持久化
- 文档: 对象存储备份

---

## 术语表

| 术语 | 说明 |
|------|------|
| RAG | 检索增强生成 (Retrieval-Augmented Generation) |
| LLM | 大语言模型 (Large Language Model) |
| Token | LLM的基本处理单位 |
| Embedding | 文本向量表示 |
| Agent | 可以调用工具的智能体 |
| Prompt | 给LLM的输入指令 |
| QA | 问答 (Question & Answer) |
| ERP | 企业资源规划 (Enterprise Resource Planning) |
| CRM | 客户关系管理 (Customer Relationship Management) |
| HRM | 人力资源管理 (Human Resource Management) |

---

*架构文档更新于: 2024年1月26日*
