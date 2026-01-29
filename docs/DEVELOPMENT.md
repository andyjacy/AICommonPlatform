# AI Common Platform - 开发指南

## 项目结构说明

```
AICommonPlatform/
├── docker-compose.yml          # 容器编排配置
├── Makefile                    # 快捷命令
├── requirements.txt            # Python依赖
├── .env                        # 环境变量配置
├── .gitignore                  # Git忽略文件
│
├── services/                   # 微服务模块
│   ├── qa_entry/              # 问答入口服务
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── utils.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── prompt_service/        # Prompt管理服务
│   ├── rag_service/           # 知识库和检索
│   ├── agent_service/         # Agent执行
│   ├── integration/           # 企业系统集成
│   └── llm_service/           # LLM接口
│
├── shared/                     # 共享代码（可选）
│   ├── models/
│   ├── utils/
│   └── constants/
│
├── scripts/                    # 实用脚本
│   ├── start.sh               # 启动脚本
│   ├── test_api.py            # API测试
│   └── init_db.sql            # 数据库初始化
│
├── docs/                       # 文档
│   ├── API.md                 # API文档
│   └── DEVELOPMENT.md         # 本文件
│
└── config/                     # 配置文件
    └── prometheus.yml         # Prometheus配置
```

---

## 快速开始

### 前置要求
- Docker & Docker Compose
- Python 3.9+
- Git

### 本地开发环境搭建

#### 1. 克隆项目
```bash
git clone <repo_url>
cd AICommonPlatform
```

#### 2. 启动容器
```bash
# 使用docker-compose
docker-compose up -d

# 或使用Makefile
make up

# 或使用启动脚本
bash scripts/start.sh up
```

#### 3. 验证服务
```bash
# 运行API测试
python3 scripts/test_api.py

# 或使用Makefile
make test
```

### 本地直接运行（不用Docker）

如果想在本地直接开发而不使用Docker容器，需要启动以下基础服务：

```bash
# 启动PostgreSQL、Redis等基础服务
docker-compose up -d postgres redis milvus

# 在单独的终端启动各个服务
# 终端1 - QA服务
cd services/qa_entry
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8001

# 终端2 - Prompt服务
cd services/prompt_service
python -m uvicorn main:app --reload --port 8002

# 终端3 - RAG服务
cd services/rag_service
python -m uvicorn main:app --reload --port 8003

# 以此类推...
```

或使用Makefile中的dev命令：
```bash
make dev-qa    # 开发QA服务
make dev-rag   # 开发RAG服务
# 等等
```

---

## 开发指南

### 添加新服务

1. **创建服务目录结构**：
```bash
mkdir -p services/my_service
cd services/my_service
touch main.py config.py models.py utils.py Dockerfile requirements.txt
```

2. **编写服务代码**：
参考现有服务的结构，例如 `services/prompt_service/main.py`。

3. **编写Dockerfile**：
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

4. **更新docker-compose.yml**：
```yaml
my_service:
  build:
    context: ./services/my_service
    dockerfile: Dockerfile
  container_name: ai_platform_my_service
  ports:
    - "8007:8000"  # 使用未使用的端口
  environment:
    SERVICE_NAME: my_service
    REDIS_URL: redis://:ai_redis_2024@redis:6379/6
    DB_URL: postgresql://admin:ai_platform_2024@postgres:5432/ai_platform
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
  networks:
    - ai_platform_net
  restart: unless-stopped
```

### 添加新的Prompt模板

在 `services/prompt_service/main.py` 中的 `PROMPT_TEMPLATES` 字典中添加：

```python
"my_template": PromptTemplate(
    id="my_template",
    name="我的模板",
    role="My Role",
    description="模板描述",
    template_content="""你是一个...
用户问题: {question}
额外信息: {extra_info}

请...""",
    variables=["question", "extra_info"]
)
```

### 添加新的知识库文档

```python
# 通过API
POST /api/rag/documents

{
  "title": "新文档",
  "content": "文档内容...",
  "category": "sales",
  "tags": ["标签1", "标签2"],
  "source": "internal"
}
```

### 添加新的Agent工具

在 `services/agent_service/main.py` 中的 `TOOLS` 字典中添加：

```python
"my_tool": Tool(
    id="my_tool",
    name="我的工具",
    description="工具描述",
    tool_type=ToolType.ERP,  # 选择合适的类型
    parameters={"param1": "type1", "param2": "type2"}
)
```

并在 `execute_tool` 函数中添加实现：

```python
elif tool_id == "my_tool":
    return {
        "tool": tool_id,
        "status": "success",
        "data": {...}
    }
```

### 集成新的企业系统

在 `services/integration/main.py` 中添加：

1. **模拟数据**：
```python
MY_SYSTEM_DATA = {
    "field1": "value1",
    "field2": "value2",
}
```

2. **API端点**：
```python
@app.get("/api/integration/my_system/{resource}")
async def query_my_system(resource: str):
    return {
        "status": "success",
        "system": "my_system",
        "data": MY_SYSTEM_DATA
    }
```

---

## 代码规范

### Python代码风格
- 遵循 PEP 8
- 使用4个空格缩进
- 使用有意义的变量名
- 添加docstring和注释

### 命名约定
```python
# 类名使用PascalCase
class QuestionRequest:
    pass

# 函数和变量使用snake_case
def process_question():
    pass

# 常量使用UPPER_CASE
MAX_TOKENS = 2000

# 私有变量/函数使用前置下划线
def _internal_function():
    pass
```

### 注释和文档
```python
def complex_function(param1: str, param2: int) -> dict:
    """
    功能简述
    
    详细说明（可选）
    
    参数：
    - param1: 参数1说明
    - param2: 参数2说明
    
    返回：
    - dict: 返回值说明
    """
    pass
```

---

## 测试

### 运行单个服务的测试

```bash
# 进入服务目录
cd services/qa_entry

# 运行单个服务
python -m unittest discover tests/ -v
```

### 运行集成测试

```bash
# 确保所有服务都在运行
docker-compose ps

# 运行测试脚本
python3 scripts/test_api.py
```

### 手动测试API

```bash
# 使用curl
curl -X POST http://localhost:8001/api/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"今年Q1的销售额是多少?","user_id":"user123"}'

# 或使用httpie
http POST localhost:8001/api/qa/ask question="今年Q1的销售额是多少?" user_id="user123"

# 或使用Python requests
python
>>> import requests
>>> requests.post("http://localhost:8001/api/qa/ask", json={
...   "question": "今年Q1的销售额是多少?",
...   "user_id": "user123"
... }).json()
```

---

## 调试技巧

### 查看容器日志
```bash
# 查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f qa_entry

# 查看最后100行日志
docker-compose logs --tail=100 qa_entry
```

### 进入容器调试
```bash
# 进入容器shell
docker-compose exec qa_entry /bin/bash

# 运行Python交互式环境
docker-compose exec qa_entry python
```

### 监控资源使用
```bash
# 查看容器资源使用情况
docker stats

# 或通过Grafana
# http://localhost:3000
```

---

## 性能优化

### 缓存策略
- 利用Redis缓存热点数据
- 设置合理的过期时间
- 避免缓存雪崩

### 数据库优化
- 使用索引加快查询
- 定期分析和清理日志
- 使用连接池

### API优化
- 使用异步处理长耗时任务
- 实现请求超时控制
- 使用gzip压缩响应

---

## 部署

### 生产环境检查清单
- [ ] 配置生产环境的.env文件
- [ ] 更新所有密钥和令牌
- [ ] 启用HTTPS
- [ ] 配置日志聚合和监控
- [ ] 进行性能测试
- [ ] 进行安全审计
- [ ] 准备灾备方案

### Docker镜像优化
```dockerfile
# 多阶段构建减小镜像大小
FROM python:3.11-slim as builder
# ...构建阶段...

FROM python:3.11-slim
# ...运行阶段...
```

---

## 故障排查

### 常见问题

#### Q: 容器无法连接到数据库
**A:** 检查PostgreSQL容器是否运行，查看日志
```bash
docker-compose logs postgres
docker-compose ps postgres
```

#### Q: Redis连接失败
**A:** 检查Redis URL配置，确保使用service name（在Docker中）或localhost（本地运行）

#### Q: API响应超时
**A:** 增加超时时间，检查服务性能，查看日志

#### Q: 数据库查询缓慢
**A:** 检查索引，使用EXPLAIN分析查询计划，考虑分页

---

## 贡献指南

1. **Fork项目**
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **打开Pull Request**

---

## 常用命令速查

```bash
# 启动/停止/重启
make up
make down
make restart

# 查看状态和日志
make ps
make logs

# 运行测试
make test

# 开发模式运行单个服务
make dev-qa
make dev-rag

# 清理数据（危险！）
make clean
```

---

## 相关资源

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Docker文档](https://docs.docker.com/)
- [PostgreSQL文档](https://www.postgresql.org/docs/)
- [Redis文档](https://redis.io/documentation)
- [Milvus文档](https://milvus.io/docs)

---

## 联系和支持

- 提交Issue：GitHub Issues
- 讨论：GitHub Discussions
- 邮件：[你的邮箱]

---

*最后更新: 2024年1月26日*
