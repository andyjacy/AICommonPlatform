# AI Common Platform - 企业级AI能力层

一个基于Docker的企业级AI能力统一平台，提供问答、知识库、Agent等核心能力。

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway (入口)                     │
│                    Flask + FastAPI                        │
└────────┬────────┬────────┬────────┬─────────────────────┘
         │        │        │        │
    ┌────▼──┐ ┌──▼────┐ ┌─▼────┐ ┌─▼─────┐
    │Question│ │Prompt │ │ RAG  │ │Agent  │
    │入口    │ │模版层 │ │知识库 │ │执行   │
    └───┬────┘ └──┬────┘ └─┬────┘ └──┬────┘
        │         │        │         │
    ┌───▼─────────▼────────▼─────────▼────┐
    │         Redis缓存 & 消息队列          │
    └──────────────────────────────────────┘
        │         │        │         │
    ┌───▼──────────────────────────────────┐
    │    PostgreSQL (知识库 + 元数据)        │
    │    Milvus (向量数据库)                 │
    │    Elastic Search (全文检索)           │
    └────────────────────────────────────────┘
```

## 服务模块

### 1. **QA Entry Service** (问答入口)
- 接收用户自然语言问题
- 问题分类和意图识别
- 路由到不同的处理模块
- 响应管理

### 2. **Prompt Service** (Prompt管理层)
- 角色系统（Role-based）
- 提示词模板库
- 动态Prompt组装
- 版本管理

### 3. **RAG Service** (检索增强生成)
- 企业知识库管理
- 向量化存储和检索
- 全文搜索
- 文档管理（PDF、Word等）

### 4. **Agent Service** (Agent执行层)
- Tool调用能力
- 企业系统接口集成
- 工作流编排
- 执行日志和监控

### 5. **Integration Service** (企业系统集成)
- ERP接口
- CRM接口
- HRM接口
- 模拟数据服务

### 6. **LLM Service** (大模型接口)
- 模型管理
- API调用封装
- Token计费

## 快速开始

### 前置要求
- Docker & Docker Compose
- Python 3.9+
- 至少 4GB 内存

### 启动服务

```bash
# 克隆项目
git clone <repo>
cd AICommonPlatform

# 启动所有容器（轻量级版本，不包含Elasticsearch和Prometheus）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f qa_entry

# 停止服务
docker-compose down

# 完全清理（包括数据卷）
docker-compose down -v
```

### 本地测试配置

轻量级版本包含的核心服务：
- ✅ PostgreSQL - 知识库和元数据存储
- ✅ Redis - 缓存和消息队列
- ✅ Milvus - 向量数据库
- ✅ 6个应用服务
- ✅ Web UI - 交互式界面

移除的服务（生产环境可添加）：
- ❌ Elasticsearch - 全文检索（可用PostgreSQL的全文搜索替代）
- ❌ Prometheus & Grafana - 监控（Web UI已包含基础状态监控）

## API 文档

### 问答入口

```bash
POST /api/qa/ask
Content-Type: application/json

{
  "question": "今年Q1的销售额是多少?",
  "user_id": "user123",
  "context": {}
}
```

响应：
```json
{
  "id": "qa_123",
  "question": "今年Q1的销售额是多少?",
  "answer": "根据我们的数据，Q1总销售额为...",
  "sources": ["rag_doc_1", "system_call_erp"],
  "confidence": 0.95,
  "execution_time": 2.5
}
```

## 项目结构

```
AICommonPlatform/
│
├── 📖 文档 (必读)
│   ├── README.md                      # ← 您在这里
│   ├── QUICKSTART.md                  # 快速参考（最常用）
│   ├── PROJECT_SUMMARY.md             # 项目交付总结
│   ├── OVERVIEW.md                    # 项目亮点概览
│   ├── DELIVERY.md                    # 交付清单
│   └── docs/
│       ├── API.md                     # API详细文档（30+端点）
│       ├── DEVELOPMENT.md             # 开发指南
│       └── ARCHITECTURE.md            # 系统架构设计
│
├── 🐳 Docker容器配置
│   ├── docker-compose.yml             # 容器编排（8个服务）
│   ├── Makefile                       # 便捷命令
│   ├── .env                           # 环境变量
│   ├── .gitignore                     # Git规则
│   └── requirements.txt               # Python全局依赖
│
├── 🔧 脚本工具
│   └── scripts/
│       ├── start.sh                   # 启动脚本
│       ├── verify.sh                  # 验证脚本
│       ├── test_api.py                # API测试脚本
│       └── init_db.sql                # 数据库初始化
│
├── 🎯 核心服务 (6个微服务)
│   └── services/
│       ├── qa_entry/                  # 问答入口服务
│       │   ├── main.py                # FastAPI应用 (350行)
│       │   ├── config.py              # 配置管理
│       │   ├── models.py              # 数据模型
│       │   ├── services.py            # 业务逻辑
│       │   ├── utils.py               # 工具函数
│       │   ├── Dockerfile             # Docker配置
│       │   └── requirements.txt       # 依赖
│       │
│       ├── prompt_service/            # Prompt管理服务
│       │   ├── main.py                # 提示词模板管理
│       │   ├── Dockerfile
│       │   └── requirements.txt
│       │
│       ├── rag_service/               # RAG知识库服务
│       │   ├── main.py                # 知识库检索
│       │   ├── Dockerfile
│       │   └── requirements.txt
│       │
│       ├── agent_service/             # Agent执行服务
│       │   ├── main.py                # Agent和工具调用
│       │   ├── Dockerfile
│       │   └── requirements.txt
│       │
│       ├── integration/               # 企业系统集成
│       │   ├── main.py                # ERP/HRM/CRM/财务集成
│       │   ├── Dockerfile
│       │   └── requirements.txt
│       │
│       ├── llm_service/               # LLM大模型接口
│       │   ├── main.py                # 多LLM支持
│       │   ├── Dockerfile
│       │   └── requirements.txt
│       │
│       └── web_ui/                    # Web UI 交互界面 ✨NEW
│           ├── main.py                # FastAPI 后端
│           ├── static/
│           │   └── index.html         # 现代化前端界面
│           ├── Dockerfile
│           └── requirements.txt
│
└── 📦 基础设施服务 (通过Docker Compose)
    ├── PostgreSQL                     # 关系数据库
    ├── Redis                          # 缓存和消息队列
    └── Milvus                         # 向量数据库
```

## 🚀 快速开始

### 最简单的方式 - 轻量级版本（推荐本地开发）

> ⚡ **轻量级专为本地 PC 优化**：仅需 1-2GB 内存，1-2 分钟启动

```bash
cd AICommonPlatform

# 方式 1：运行启动脚本（最简单）
bash start-lite.sh

# 方式 2：手动启动
docker-compose -f docker-compose.lite.yml up -d

# 然后访问
open http://localhost:3000
```

**轻量级 vs 标准版对比**：

| 项目 | 轻量级 | 标准版 |
|------|--------|--------|
| 启动时间 | 1-2 分钟 ⚡ | 3-5 分钟 |
| 内存占用 | 1-2GB 💚 | 4GB+ |
| 磁盘占用 | 500MB | 3GB+ |
| 包含服务 | 7 个 + Web UI | 8 个 + 监控 |
| 适合场景 | **本地学习开发** | 生产环境 |

**推荐使用轻量级版本理解 AI Platform 架构和设计！**

### 验证启动
```bash
# 查看容器状态
docker-compose -f docker-compose.lite.yml ps

# 查看日志（可选）
docker-compose -f docker-compose.lite.yml logs -f web_ui
```

### 标准版本启动（可选）
```bash
# 如需完整功能（PostgreSQL、Milvus、监控等）
docker-compose up -d

# 关于标准版本的详细信息，见下文
```

### 访问服务

**🌐 Web UI (推荐)**: http://localhost:3000
- 交互式问答界面
- 实时服务状态监控
- 知识库搜索
- 系统配置查看

**API 服务**（轻量级版本）:
- QA Entry:      http://localhost:8001
- Prompt:        http://localhost:8002
- RAG:           http://localhost:8003
- Agent:         http://localhost:8004
- Integration:   http://localhost:8005
- LLM:           http://localhost:8006

## 📚 文档导航

| 文档 | 用途 | 适合场景 |
|------|------|---------|
| **README.md** | 项目概览和快速开始 | 5 分钟了解 |
| **LITE_GUIDE.md** ⭐ | 轻量级版本完整指南 | **本地学习** |
| **docs/WEB_UI.md** | Web UI 使用指南 | UI 交互 |
| **QUICKSTART.md** | 常见命令和 API 速查 | 快速参考 |
| **docs/API.md** | 30+个 API 的完整文档 | API 集成 |
| **docs/DEVELOPMENT.md** | 如何开发和扩展 | 定制开发 |
| **docs/ARCHITECTURE.md** | 系统架构深度设计 | 深度理解 |

## 💡 推荐阅读顺序
1. 本文件 (README.md) - 了解项目
2. docs/WEB_UI.md - 学习使用界面
3. QUICKSTART.md - 快速参考
4. docs/API.md - 学习API
5. docs/DEVELOPMENT.md - 开发扩展
6. docs/ARCHITECTURE.md - 深度理解

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| API框架 | FastAPI | 高性能Web框架 |
| Web UI | HTML5 + JavaScript | 现代化交互界面 |
| LLM | OpenAI/通义千问/文心一言 | 多模型支持 |
| 向量DB | Milvus | 向量存储和搜索 |
| 缓存 | Redis | 缓存和消息队列 |
| 数据库 | PostgreSQL | 关系数据存储 |
| 容器化 | Docker | 统一部署 |

## 功能示例

### 问答流程
1. 用户提问 → QA Entry Service
2. 意图识别和关键词提取
3. RAG检索相关知识库文档
4. Agent调用企业系统接口获取实时数据
5. Prompt组装（角色+上下文+指令）
6. LLM生成回答
7. 结果返回和日志记录

### Prompt模板示例
- **销售顾问模板**：关注销售数据、客户信息
- **HR顾问模板**：关注员工信息、薪资福利
- **技术顾问模板**：关注系统架构、技术方案
- **财务顾问模板**：关注财务数据、预算报告

## 监控和日志

- **Web UI**: 实时服务状态监控
- **Docker Logs**: 查看容器输出日志
- **PostgreSQL**: 数据库查询和日志

## 安全考虑

- API密钥管理
- 数据加密传输
- 用户权限控制
- 审计日志记录

## 贡献指南

欢迎提交Issue和PR！

## License

MIT
