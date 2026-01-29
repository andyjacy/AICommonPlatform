# 🎯 AI 平台快速参考

## 🚀 5 分钟快速开始

```bash
# 1️⃣ 创建配置文件
cp .env.example .env

# 2️⃣ 编辑配置（填入你的 OpenAI API Key）
nano .env
# 或 code .env

# 3️⃣ 启动容器
docker-compose -f docker-compose.lite.yml up -d --build

# 4️⃣ 打开浏览器
# Web UI: http://localhost:3000
# 管理控制台: http://localhost:3000/admin
# API 文档: http://localhost:8002/docs
```

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────┐
│             Web UI (Port 3000)                  │
│  ├─ Main Interface (/)                          │
│  ├─ Admin Console (/admin) ← 你在这里配置      │
│  └─ Static Files (HTML, CSS, JS)                │
└──────────────────────┬──────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    ┌────────┐  ┌────────────┐  ┌────────────┐
    │  LLM   │  │  Prompt    │  │   Agent    │
    │Service │  │  Service   │  │  Service   │
    │(8001)  │  │  (8002)    │  │ (inside 8002)
    └────────┘  └────────────┘  └────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼              ▼              ▼
    ┌────────┐  ┌────────────┐  ┌────────────┐
    │ OpenAI │  │ Enterprise │  │  Cache &  │
    │  API   │  │ Systems    │  │Database   │
    │        │  │(ERP/CRM...)│  │           │
    └────────┘  └────────────┘  └────────────┘
```

---

## 📝 Prompt 模板一览

| 模板名 | 角色 | 用途 | API 端点 |
|--------|------|------|---------|
| 销售顾问 | sales_advisor | 销售分析、策略制定 | `/api/prompts/sales_advisor` |
| HR 顾问 | hr_advisor | 人才管理、组织规划 | `/api/prompts/hr_advisor` |
| 技术顾问 | tech_advisor | 技术架构、优化建议 | `/api/prompts/tech_advisor` |
| 财务顾问 | finance_advisor | 财务分析、投资规划 | `/api/prompts/finance_advisor` |
| 通用助手 | general_assistant | 通用问答、信息查询 | `/api/prompts/general_assistant` |

### 使用 Prompt 模板

```bash
# 获取特定 Prompt
curl http://localhost:8002/api/prompts/sales_advisor

# 生成完整 Prompt（包含上下文）
curl -X POST http://localhost:8002/api/prompts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "role": "sales_advisor",
    "context": "客户：Fortune 500 公司，年销售额 10 亿美元"
  }'

# 创建自定义 Prompt
curl -X POST http://localhost:8002/api/prompts/custom \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Custom Prompt",
    "role": "custom_role",
    "system_prompt": "You are...",
    "examples": []
  }'
```

---

## 🛠️ Agent 工具一览

| 工具名 | 图标 | 描述 | 参数 |
|--------|------|------|------|
| Web Search | 🔍 | 网络搜索 | query, max_results |
| ERP Query | 💼 | ERP 系统查询 | data_type, filters |
| CRM Query | 👥 | CRM 系统查询 | customer_id, action |
| HRM Query | 👔 | HRM 系统查询 | employee_id, data_type |
| Data Analysis | 📊 | 数据分析 | data_source, analysis_type |
| Report Generation | 📄 | 报告生成 | report_type, format |
| Calendar Management | 📅 | 日程管理 | action, event_data |
| Email Management | 📧 | 邮件管理 | action, recipient |
| File Management | 📁 | 文件管理 | action, file_path |

### 操作 Agent 工具

```bash
# 获取所有工具
curl http://localhost:8002/api/agent/tools

# 获取工具详情
curl http://localhost:8002/api/agent/tools/web_search

# 启用/禁用工具
curl -X POST http://localhost:8002/api/agent/tools/update \
  -H "Content-Type: application/json" \
  -d '{"name": "web_search", "enabled": true}'

# 创建自定义工具
curl -X POST http://localhost:8002/api/agent/tools/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_tool",
    "description": "My tool description",
    "parameters": {"param1": {"type": "string"}}
  }'

# 删除工具
curl -X DELETE http://localhost:8002/api/agent/tools/my_tool

# 保存工具顺序（拖拽后调用）
curl -X POST http://localhost:8002/api/agent/tools/reorder \
  -H "Content-Type: application/json" \
  -d '{"order": ["web_search", "erp_query", "crm_query", ...]}'
```

---

## 🎨 管理控制台功能

### Tab 1: Prompt Management

**功能**:
- 📋 浏览所有 Prompt 模板
- 🔍 搜索和筛选
- 📄 查看详细信息
- ✏️ 编辑现有 Prompt
- ➕ 创建自定义 Prompt
- 🗑️ 删除 Prompt

**快捷键**:
- `Ctrl+F` 搜索
- `Ctrl+N` 创建新 Prompt

### Tab 2: Agent Tools

**功能**:
- 📋 浏览所有 Agent 工具
- 🎯 拖拽重新排序
- ⚙️ 启用/禁用工具
- 📊 查看工具参数
- ✏️ 编辑工具配置
- ➕ 创建自定义工具
- 🗑️ 删除工具
- 💾 保存排序

**操作步骤**:
1. 打开管理控制台：http://localhost:3000/admin
2. 选择 Agent Tools 标签
3. 拖拽工具卡片重新排序
4. 点击切换开关启用/禁用
5. 点击"Save Tool Order"保存

### Tab 3: Settings

**功能**:
- 🔑 配置 API Key
- 🤖 选择 LLM 模型
- 💾 缓存设置
- 📝 日志配置
- 🔄 同步设置

---

## 🔌 API 快速参考

### Prompt Service (Port 8002)

```bash
# 基础 URL
BASE_URL=http://localhost:8002

# 1. 列出所有 Prompt
GET   $BASE_URL/api/prompts

# 2. 获取特定 Prompt
GET   $BASE_URL/api/prompts/{role}

# 3. 生成完整 Prompt
POST  $BASE_URL/api/prompts/generate
Body: {"role": "sales_advisor", "context": "..."}

# 4. 创建自定义 Prompt
POST  $BASE_URL/api/prompts/custom
Body: {"name": "...", "role": "...", "system_prompt": "...", "examples": []}

# 5. 列出所有 Agent 工具
GET   $BASE_URL/api/agent/tools

# 6. 获取工具详情
GET   $BASE_URL/api/agent/tools/{tool_name}

# 7. 创建自定义工具
POST  $BASE_URL/api/agent/tools/create
Body: {"name": "...", "description": "...", "parameters": {...}}

# 8. 更新工具
POST  $BASE_URL/api/agent/tools/update
Body: {"name": "...", "enabled": true, ...}

# 9. 删除工具
DELETE $BASE_URL/api/agent/tools/{tool_name}

# 10. 保存工具顺序
POST  $BASE_URL/api/agent/tools/reorder
Body: {"order": ["tool1", "tool2", ...]}

# API 文档
GET   $BASE_URL/docs
```

### LLM Service (Port 8001)

```bash
# 基础 URL
BASE_URL=http://localhost:8001

# 调用 LLM
POST  $BASE_URL/api/llm/chat
Body: {
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"}
  ],
  "model": "gpt-4",
  "temperature": 0.7
}

# 流式调用
POST  $BASE_URL/api/llm/chat/stream
Body: {...同上...}
```

---

## 🐳 Docker 常用命令

```bash
# 启动
docker-compose -f docker-compose.lite.yml up -d --build

# 停止
docker-compose -f docker-compose.lite.yml down

# 重启
docker-compose -f docker-compose.lite.yml restart

# 查看状态
docker-compose -f docker-compose.lite.yml ps

# 查看日志
docker-compose -f docker-compose.lite.yml logs -f

# 进入容器
docker-compose -f docker-compose.lite.yml exec prompt_service bash

# 查看环境变量
docker-compose -f docker-compose.lite.yml config | grep -E "OPENAI|ALIBABA"

# 删除所有容器
docker-compose -f docker-compose.lite.yml down -v

# 清理所有资源
docker system prune -a
```

---

## 🔐 安全检查清单

启动前：
- [ ] .env 文件已创建 ✓
- [ ] OPENAI_API_KEY 已更新为新 Key ✓
- [ ] .gitignore 包含 .env ✓
- [ ] 旧 Key 已在 OpenAI 控制面板中撤销 ✓

启动后：
- [ ] 容器正常运行 ✓
- [ ] 管理控制台可访问 ✓
- [ ] API 返回正确数据 ✓
- [ ] 日志中没有错误 ✓

---

## ⚡ 性能优化

### 降低 API 成本

```env
# 使用更便宜的模型
OPENAI_MODEL=gpt-3.5-turbo          # 便宜 90%
# vs
# OPENAI_MODEL=gpt-4                # 功能完整但昂贵

# 或使用本地 LLM（实验性）
# ALIBABA_MODEL=qwen-turbo           # 最便宜
```

### 提高响应速度

```env
# 增加缓存 TTL
CACHE_TTL=7200                       # 2 小时
# 之前: CACHE_TTL=3600              # 1 小时

# 启用模拟数据（开发）
USE_MOCK_DATA=true
```

### 减少资源占用

```bash
# 使用 Lite 版本
docker-compose -f docker-compose.lite.yml ...

# vs Full 版本
# docker-compose -f docker-compose.yml ...
```

---

## 🆘 故障排查

### 问题 1: 容器无法启动
```bash
# 查看详细错误
docker-compose -f docker-compose.lite.yml logs
```

### 问题 2: API Key 无效
```bash
# 检查 Key
cat .env | grep OPENAI_API_KEY

# 获取新 Key: https://platform.openai.com/api-keys
```

### 问题 3: 管理控制台无法加载
```bash
# 清除浏览器缓存（Cmd+Shift+Delete）
# 检查 DevTools (F12) 中的错误
```

### 问题 4: 拖拽不工作
```bash
# 查看浏览器控制台错误
# 尝试刷新页面或用不同浏览器
```

---

## 📚 文档导航

| 文档 | 内容 | 阅读时间 |
|------|------|---------|
| **DEPLOYMENT_GUIDE.md** | 完整部署步骤 | 20分钟 |
| **SECURITY_GUIDE.md** | 安全最佳实践 | 15分钟 |
| **QUICK_REFERENCE.md** | 本文档 | 5分钟 |
| **README.md** | 项目概述 | 10分钟 |

---

## 🎓 学习路径

### 初级 (第 1 天)
1. 阅读本快速参考
2. 配置 .env 文件
3. 启动容器
4. 打开管理控制台

### 中级 (第 2-3 天)
1. 创建自定义 Prompt
2. 配置 Agent 工具
3. 测试 API 端点
4. 集成企业系统（ERP/CRM）

### 高级 (第 4-5 天)
1. 优化 Prompt 性能
2. 实现自定义工具
3. 添加数据库支持
4. 部署到生产环境

---

## 📞 快速联系

遇到问题？

1. 检查本文档的故障排查部分
2. 查看 DEPLOYMENT_GUIDE.md 的完整指南
3. 查看 SECURITY_GUIDE.md 了解安全问题
4. 查看容器日志：`docker-compose logs`

---

**最后更新**: 2024-01-15  
**版本**: 1.0.0  
**语言**: 简体中文 🇨🇳
