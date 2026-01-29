# 🚀 AI 平台部署和配置指南

## 📋 目录

1. [快速开始](#快速开始)
2. [完整部署步骤](#完整部署步骤)
3. [配置说明](#配置说明)
4. [功能验证](#功能验证)
5. [故障排查](#故障排查)
6. [维护和监控](#维护和监控)

---

## 🚀 快速开始

### 1️⃣ 初始化项目

```bash
# 进入项目目录
cd /Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform

# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置
nano .env
```

### 2️⃣ 启动容器

```bash
# 启动 Lite 版本（推荐，资源占用少）
docker-compose -f docker-compose.lite.yml up -d --build

# 或启动完整版
docker-compose -f docker-compose.yml up -d --build

# 查看容器状态
docker-compose -f docker-compose.lite.yml ps
```

### 3️⃣ 访问应用

| 服务 | URL | 说明 |
|------|-----|------|
| Web UI | http://localhost:3000 | 主界面 |
| 管理控制台 | http://localhost:3000/admin | Prompt 和 Agent 配置 |
| Prompt 服务 API | http://localhost:8002/docs | API 文档 |
| LLM 服务 API | http://localhost:8001/docs | LLM 调用 API |

### 4️⃣ 验证部署

```bash
# 检查 Prompt 模板
curl http://localhost:8002/api/prompts

# 检查 Agent 工具
curl http://localhost:8002/api/agent/tools

# 查看完整日志
docker-compose -f docker-compose.lite.yml logs -f web_ui
```

---

## 📑 完整部署步骤

### 步骤 1: 安全配置

#### 1.1 撤销泄露的 API Key ⚠️

```bash
# 这非常重要！
# 1. 访问 https://platform.openai.com/api-keys
# 2. 找到泄露的 Key（查看之前的对话历史）
# 3. 点击 "Delete" 或 "Revoke"
# 4. 生成新的 API Key
```

#### 1.2 创建 .env 文件

```bash
# 复制模板
cp .env.example .env

# 编辑文件（使用你喜欢的编辑器）
code .env
# 或
vim .env
# 或
nano .env
```

#### 1.3 填入必要的配置

```env
# 🔴 必需：OpenAI 配置
OPENAI_API_KEY=sk-proj-your-new-key-here    # 使用新生成的 Key
OPENAI_MODEL=gpt-4

# 🟡 推荐：其他 LLM（备用）
ALIBABA_API_KEY=your-key
BAIDU_API_KEY=your-key

# 🟢 可选：企业系统集成
ERP_API_URL=http://your-erp-server:8000
ERP_API_KEY=your-key

CRM_API_URL=http://your-crm-server:8000
CRM_API_KEY=your-key

# 系统配置
LOG_LEVEL=INFO
USE_MOCK_DATA=false
```

#### 1.4 验证 .gitignore

```bash
# 确保 .env 文件被忽略
cat .gitignore | grep ".env"

# 输出应该包含：
# .env
# .env.local
# .env.*.local

# 如果没有，添加：
echo ".env" >> .gitignore
```

---

### 步骤 2: Docker 容器配置

#### 2.1 查看当前 Docker Compose 配置

```bash
# Lite 版本
cat docker-compose.lite.yml | head -50

# 完整版
cat docker-compose.yml | head -50
```

#### 2.2 确保 Prompt Service 在配置中

```yaml
# docker-compose.lite.yml 应该包含：
services:
  prompt_service:
    build:
      context: ./services/prompt_service
      dockerfile: Dockerfile.lite
    ports:
      - "8002:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=${OPENAI_MODEL}
    volumes:
      - ./services/prompt_service:/app
```

#### 2.3 确保 Web UI 挂载了管理控制台

```yaml
# docker-compose.lite.yml 中的 web_ui 服务应该包含：
services:
  web_ui:
    build:
      context: ./services/web_ui
      dockerfile: Dockerfile.lite
    ports:
      - "3000:5000"
    volumes:
      - ./services/web_ui/static:/app/static
    environment:
      - PROMPT_SERVICE_URL=http://prompt_service:8000
```

---

### 步骤 3: 构建和启动容器

#### 3.1 清理旧容器（可选）

```bash
# 停止所有容器
docker-compose -f docker-compose.lite.yml down

# 移除旧镜像
docker-compose -f docker-compose.lite.yml down --rmi all

# 清理未使用的资源
docker system prune -a
```

#### 3.2 启动新容器

```bash
# 从 .env 文件读取配置，构建并启动容器
docker-compose -f docker-compose.lite.yml up -d --build

# 实时查看日志
docker-compose -f docker-compose.lite.yml logs -f

# 后台启动（不看日志）
docker-compose -f docker-compose.lite.yml up -d --build &
```

#### 3.3 验证容器运行状态

```bash
# 查看所有容器
docker-compose -f docker-compose.lite.yml ps

# 应该看到：
# NAME          STATUS         PORTS
# web_ui        Up 2 seconds   0.0.0.0:3000->5000/tcp
# prompt_service Up 2 seconds   0.0.0.0:8002->8000/tcp
# llm_service   Up 2 seconds   0.0.0.0:8001->8000/tcp
```

---

### 步骤 4: 验证服务可用性

#### 4.1 Prompt Service API

```bash
# 获取所有 Prompt 模板
curl http://localhost:8002/api/prompts

# 获取特定角色的 Prompt
curl http://localhost:8002/api/prompts/sales_advisor

# 获取所有 Agent 工具
curl http://localhost:8002/api/agent/tools

# 查看 API 文档
open http://localhost:8002/docs
```

#### 4.2 Web UI

```bash
# 打开主界面
open http://localhost:3000

# 打开管理控制台
open http://localhost:3000/admin
```

#### 4.3 LLM Service

```bash
# 测试 LLM 调用
curl -X POST http://localhost:8001/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

---

## 🔧 配置说明

### 1. OpenAI 配置

```env
# API Key：从 https://platform.openai.com/api-keys 获取
OPENAI_API_KEY=sk-proj-...

# 选择使用的模型
OPENAI_MODEL=gpt-4              # 功能完整但成本高
# OPENAI_MODEL=gpt-3.5-turbo    # 便宜但功能较少
# OPENAI_MODEL=gpt-4-turbo      # 中等成本和性能
```

### 2. 代替 LLM 配置

如果 OpenAI 不可用，可以配置其他 LLM：

#### 阿里云 (Qwen)

```env
ALIBABA_API_KEY=your-key-here
ALIBABA_MODEL=qwen-max          # 功能最完整
# ALIBABA_MODEL=qwen-plus       # 中等性能
# ALIBABA_MODEL=qwen-turbo      # 快速便宜
```

#### 百度 (ERNIE)

```env
BAIDU_API_KEY=your-key-here
BAIDU_SECRET_KEY=your-secret-here
BAIDU_MODEL=ernie-4.0
```

#### 科大讯飞 (Spark)

```env
XUNFEI_API_KEY=your-key-here
XUNFEI_APP_ID=your-app-id
XUNFEI_MODEL=sparkdesk-v3.1
```

#### 智谱 (GLM)

```env
ZHIPU_API_KEY=your-key-here
ZHIPU_MODEL=glm-4
```

### 3. 企业系统集成

#### ERP 系统

```env
ERP_API_URL=http://your-erp-server:8000
ERP_API_KEY=your-key
ERP_TIMEOUT=30                   # 请求超时（秒）

# Prompt Service 将能查询：
# - 销售数据、库存、订单
# - 财务数据、报表
# - 成本、利润分析
```

#### CRM 系统

```env
CRM_API_URL=http://your-crm-server:8000
CRM_API_KEY=your-key

# Prompt Service 将能查询：
# - 客户信息、联系历史
# - 销售机会、漏斗
# - 合同、续约
```

#### HRM 系统

```env
HRM_API_URL=http://your-hrm-server:8000
HRM_API_KEY=your-key

# Prompt Service 将能查询：
# - 员工信息、组织结构
# - 薪酬、考勤
# - 培训、发展计划
```

### 4. 系统配置

```env
# 日志级别
LOG_LEVEL=DEBUG     # 调试信息最详细
# LOG_LEVEL=INFO    # 普通信息（推荐）
# LOG_LEVEL=WARNING # 只显示警告
# LOG_LEVEL=ERROR   # 只显示错误

# 缓存 TTL（秒）
CACHE_TTL=3600      # 1小时缓存

# 使用模拟数据（开发调试用）
USE_MOCK_DATA=false # 生产环境关闭
# USE_MOCK_DATA=true # 开发环境可开启

# 调试模式
DEBUG=false         # 生产环境关闭
```

---

## ✅ 功能验证

### 1. Prompt 模板管理

打开 http://localhost:3000/admin，选择 **Prompt Management** 标签：

- [ ] 显示 5 个预定义 Prompt：销售顾问、HR 顾问、技术顾问、财务顾问、通用助手
- [ ] 可以搜索和筛选 Prompt
- [ ] 可以查看每个 Prompt 的详细信息
- [ ] 可以创建自定义 Prompt
- [ ] 可以编辑现有 Prompt
- [ ] 可以删除自定义 Prompt

### 2. Agent 工具配置

选择 **Agent Tools** 标签：

- [ ] 显示 9 个预定义工具：Web 搜索、ERP 查询、CRM 查询、HRM 查询、数据分析、报告生成、日程管理、邮件管理、文件管理
- [ ] 可以拖拽重新排序工具
- [ ] 可以启用/禁用工具（切换开关）
- [ ] 可以查看每个工具的参数
- [ ] 可以创建自定义工具
- [ ] 可以编辑工具配置
- [ ] 可以删除自定义工具
- [ ] 拖拽排序后点击 **Save Tool Order** 可以持久化

### 3. 系统设置

选择 **Settings** 标签：

- [ ] 可以设置 OpenAI API Key
- [ ] 可以选择 LLM 模型
- [ ] 可以配置缓存设置
- [ ] 可以启用/禁用日志

### 4. API 端点验证

```bash
# 1. 获取所有 Prompt 模板
curl http://localhost:8002/api/prompts | jq

# 2. 获取特定 Prompt
curl http://localhost:8002/api/prompts/sales_advisor | jq

# 3. 生成完整 Prompt
curl -X POST http://localhost:8002/api/prompts/generate \
  -H "Content-Type: application/json" \
  -d '{"role": "sales_advisor", "context": "New customer inquiry"}' | jq

# 4. 创建自定义 Prompt
curl -X POST http://localhost:8002/api/prompts/custom \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Prompt",
    "role": "custom_role",
    "system_prompt": "You are a helpful assistant...",
    "examples": []
  }' | jq

# 5. 获取所有 Agent 工具
curl http://localhost:8002/api/agent/tools | jq

# 6. 获取特定工具
curl http://localhost:8002/api/agent/tools/web_search | jq

# 7. 创建自定义工具
curl -X POST http://localhost:8002/api/agent/tools/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_tool",
    "description": "My custom tool",
    "parameters": {}
  }' | jq

# 8. 更新工具配置
curl -X POST http://localhost:8002/api/agent/tools/update \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web_search",
    "enabled": true
  }' | jq

# 9. 删除工具
curl -X DELETE http://localhost:8002/api/agent/tools/my_tool

# 10. 保存工具顺序
curl -X POST http://localhost:8002/api/agent/tools/reorder \
  -H "Content-Type: application/json" \
  -d '{
    "order": ["web_search", "erp_query", "crm_query", ...]
  }' | jq
```

---

## 🔍 故障排查

### 问题 1: 容器无法启动

```bash
# 查看错误日志
docker-compose -f docker-compose.lite.yml logs

# 检查特定服务
docker-compose -f docker-compose.lite.yml logs prompt_service

# 检查端口是否被占用
lsof -i :3000
lsof -i :8002

# 杀死占用端口的进程
kill -9 <PID>
```

### 问题 2: API Key 无效

```bash
# 检查 .env 文件
cat .env | grep OPENAI_API_KEY

# 验证 Key 格式
echo $OPENAI_API_KEY

# 测试 API 连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# 如果失败，重新获取 Key：
# 1. 访问 https://platform.openai.com/api-keys
# 2. 创建新 Key
# 3. 更新 .env 文件
# 4. 重启容器
docker-compose -f docker-compose.lite.yml restart
```

### 问题 3: 管理控制台无法加载

```bash
# 检查 web_ui 服务日志
docker-compose -f docker-compose.lite.yml logs web_ui

# 检查静态文件是否存在
ls -la services/web_ui/static/admin_console.html

# 检查 web_ui 是否正确挂载静态文件
docker-compose -f docker-compose.lite.yml exec web_ui \
  ls -la /app/static/
```

### 问题 4: Prompt 模板未显示

```bash
# 检查 Prompt Service 是否运行
curl http://localhost:8002/api/prompts

# 查看 Prompt Service 日志
docker-compose -f docker-compose.lite.yml logs prompt_service

# 检查 Prompt Service 容器内的代码
docker-compose -f docker-compose.lite.yml exec prompt_service \
  python3 -c "from main_enhanced import PROMPT_TEMPLATES; print(list(PROMPT_TEMPLATES.keys()))"
```

### 问题 5: Agent 工具拖拽不工作

```bash
# 检查浏览器控制台错误
# 打开 DevTools (F12) → Console → 查看错误信息

# 清除浏览器缓存
# Cmd+Shift+Delete (Mac) 或 Ctrl+Shift+Delete (Windows)

# 检查 admin_console.html 是否正确加载
curl http://localhost:3000/admin | head -20
```

---

## 🛠️ 维护和监控

### 1. 日志管理

```bash
# 实时查看日志
docker-compose -f docker-compose.lite.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.lite.yml logs -f prompt_service

# 查看最后 100 行日志
docker-compose -f docker-compose.lite.yml logs --tail=100

# 保存日志到文件
docker-compose -f docker-compose.lite.yml logs > app.log 2>&1
```

### 2. 性能监控

```bash
# 监控容器资源使用
docker stats

# 检查磁盘空间
docker system df

# 清理未使用的镜像和容器
docker system prune -a
```

### 3. 备份配置

```bash
# 备份 .env 文件（放在安全的地方）
cp .env .env.backup

# 备份自定义 Prompt（如果使用数据库）
docker-compose -f docker-compose.lite.yml exec prompt_service \
  python3 -c "import json; from main_enhanced import custom_prompts; print(json.dumps(custom_prompts, indent=2))"
```

### 4. 更新服务

```bash
# 更新 Prompt Service 代码
git pull
docker-compose -f docker-compose.lite.yml up -d --build prompt_service

# 更新 Web UI
docker-compose -f docker-compose.lite.yml up -d --build web_ui

# 更新所有服务
docker-compose -f docker-compose.lite.yml up -d --build
```

### 5. 定期维护

| 任务 | 频率 | 命令 |
|------|------|------|
| 轮换 API Key | 3 个月 | `更新 .env，重启容器` |
| 清理日志 | 每月 | `docker system prune` |
| 更新依赖 | 每季度 | `pip install --upgrade` |
| 备份配置 | 每周 | `cp .env .env.backup` |
| 检查安全更新 | 每周 | `docker image pull` |

---

## 📞 获取帮助

### 常见命令速查表

```bash
# 启动
docker-compose -f docker-compose.lite.yml up -d --build

# 停止
docker-compose -f docker-compose.lite.yml down

# 查看状态
docker-compose -f docker-compose.lite.yml ps

# 查看日志
docker-compose -f docker-compose.lite.yml logs -f

# 进入容器
docker-compose -f docker-compose.lite.yml exec prompt_service bash

# 重启服务
docker-compose -f docker-compose.lite.yml restart

# 清理资源
docker system prune -a

# 查看环境变量
docker-compose -f docker-compose.lite.yml config | grep OPENAI
```

### 检查清单

部署前：
- [ ] .env 文件已创建并填入真实的 API Key
- [ ] .gitignore 包含 .env 文件
- [ ] Docker 已安装并运行
- [ ] 端口 3000, 8001, 8002 未被占用

部署后：
- [ ] 所有容器都在运行
- [ ] Web UI 可以访问
- [ ] 管理控制台可以加载
- [ ] API 端点返回 200 状态码
- [ ] Prompt 模板显示正确
- [ ] Agent 工具可以拖拽

---

**更新日期**: 2024-01-15
**版本**: 1.0.0
**维护者**: AI Platform Team
