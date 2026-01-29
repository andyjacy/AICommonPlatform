# 📚 AI 平台完整功能文档

## 🎯 项目概览

这是一个企业级 AI 平台，提供：

1. **Prompt 模板管理** - 针对不同角色的预定义 Prompt
2. **Agent 工具配置** - 可拖拽的企业集成工具
3. **Web 管理控制台** - 可视化配置界面
4. **LLM 服务** - 统一的 LLM 调用接口
5. **安全配置** - 环境变量管理和最佳实践

---

## 📦 已创建的文件

### 1. **SECURITY_GUIDE.md** (安全指南)
- **目的**: 指导如何安全管理 API Key
- **内容**:
  - ⚠️ API Key 泄露的紧急响应步骤
  - ✅ 正确的配置方法
  - 🔐 安全最佳实践
  - 🛡️ 密钥管理和轮换
  - 📊 环境变量完整列表
  - ⚡ 故障排查指南

**使用场景**: 当你需要了解如何安全处理敏感信息时

### 2. **DEPLOYMENT_GUIDE.md** (部署指南)
- **目的**: 详细的部署和配置步骤
- **内容**:
  - 🚀 快速开始（3 分钟）
  - 📋 完整部署步骤（分 4 个阶段）
  - 🔧 详细的配置说明
  - ✅ 功能验证清单
  - 🔍 故障排查指南
  - 🛠️ 维护和监控

**使用场景**: 当你要部署和配置整个系统时

### 3. **QUICK_REFERENCE.md** (快速参考)
- **目的**: 5 分钟快速入门指南
- **内容**:
  - ⚡ 5 分钟快速开始
  - 📊 系统架构图
  - 📝 Prompt 模板一览表
  - 🛠️ Agent 工具一览表
  - 🎨 管理控制台功能介绍
  - 🔌 API 快速参考
  - 🐳 Docker 常用命令
  - ⚡ 性能优化建议

**使用场景**: 当你需要快速查找信息时

### 4. **setup_and_verify.py** (自动化配置脚本)
- **目的**: 一键配置和验证系统
- **功能**:
  - ✓ 自动检查 Docker 和依赖
  - ✓ 验证 .env 文件配置
  - ✓ 检查 API Key 有效性
  - ✓ 检查端口可用性
  - ✓ 自动启动 Docker 容器
  - ✓ 测试 API 端点
  - ✓ 交互式配置向导

**使用方法**:
```bash
# 运行配置脚本
python3 setup_and_verify.py

# 如果需要交互式配置
# 脚本会自动引导你
```

---

## 🚀 使用流程

### 场景 1: 第一次部署

```bash
# 步骤 1: 进入项目目录
cd /Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform

# 步骤 2: 运行自动化设置脚本
python3 setup_and_verify.py

# 脚本会：
# ✓ 检查 Docker 安装
# ✓ 验证 .env 文件
# ✓ 启动容器
# ✓ 测试 API

# 步骤 3: 打开浏览器
# 管理控制台: http://localhost:3000/admin
```

### 场景 2: 安全问题

```bash
# 如果 API Key 泄露，打开 SECURITY_GUIDE.md
# 按照以下步骤：
# 1. 立即撤销泄露的 Key
# 2. 生成新的 API Key
# 3. 更新 .env 文件
# 4. 重启容器

# 快速命令：
cat SECURITY_GUIDE.md | grep -A 10 "立即撤销"
```

### 场景 3: 部署问题

```bash
# 如果遇到部署问题，打开 DEPLOYMENT_GUIDE.md
# 查看故障排查部分

cat DEPLOYMENT_GUIDE.md | grep -A 20 "问题 1:"
```

### 场景 4: 快速查询

```bash
# 需要快速找到某个命令或 API？
# 打开 QUICK_REFERENCE.md

cat QUICK_REFERENCE.md | grep -i "docker"
# 或查看 API 快速参考部分
```

---

## 🎓 学习路径

### Day 1: 初始部署（2 小时）

```
1. 读完 QUICK_REFERENCE.md (5 分钟)
2. 运行 setup_and_verify.py (10 分钟)
3. 打开管理控制台，浏览界面 (15 分钟)
4. 查看 Prompt 模板和 Agent 工具 (20 分钟)
5. 创建第一个自定义 Prompt (20 分钟)
6. 配置一个 Agent 工具 (20 分钟)
7. 阅读 DEPLOYMENT_GUIDE.md (30 分钟)
```

### Day 2-3: 进阶使用（4 小时）

```
1. 深入阅读 SECURITY_GUIDE.md (1 小时)
2. 配置企业系统集成（ERP/CRM）(1 小时)
3. 创建多个自定义 Prompt (1 小时)
4. 实现自定义 Agent 工具 (1 小时)
5. 优化性能和成本 (30 分钟)
```

### Day 4+: 生产部署（持续）

```
1. 设置监控和告警
2. 定期轮换 API Key
3. 备份配置
4. 添加数据库持久化
5. 实现认证和授权
```

---

## 📊 功能对照表

| 功能 | 文档 | 脚本 | 位置 |
|------|------|------|------|
| 快速入门 | QUICK_REFERENCE | 无 | 5分钟阅读 |
| 安全配置 | SECURITY_GUIDE | setup_and_verify.py | 15分钟阅读 + 5分钟运行 |
| 完整部署 | DEPLOYMENT_GUIDE | 无 | 20分钟阅读 + 手动配置 |
| 自动验证 | 无 | setup_and_verify.py | 2分钟运行 |
| Prompt 管理 | QUICK_REFERENCE | 无 | 管理控制台操作 |
| Agent 工具 | QUICK_REFERENCE | 无 | 管理控制台操作 |
| API 测试 | DEPLOYMENT_GUIDE | setup_and_verify.py | curl 命令或自动脚本 |
| Docker 命令 | QUICK_REFERENCE | 无 | 速查表 |
| 故障排查 | DEPLOYMENT_GUIDE | setup_and_verify.py | 查看对应章节 |

---

## 🔑 关键命令速查

### 启动和停止

```bash
# 启动（自动构建）
docker-compose -f docker-compose.lite.yml up -d --build

# 停止
docker-compose -f docker-compose.lite.yml down

# 查看状态
docker-compose -f docker-compose.lite.yml ps

# 查看日志
docker-compose -f docker-compose.lite.yml logs -f
```

### 自动化

```bash
# 一键配置和验证
python3 setup_and_verify.py
```

### API 测试

```bash
# 获取 Prompt 模板
curl http://localhost:8002/api/prompts

# 获取 Agent 工具
curl http://localhost:8002/api/agent/tools

# 查看 API 文档
open http://localhost:8002/docs
```

### 访问应用

```bash
# Web UI
open http://localhost:3000

# 管理控制台（最重要）
open http://localhost:3000/admin

# Prompt Service API
open http://localhost:8002/docs
```

---

## 🎯 每个文档的使用时机

### 📖 SECURITY_GUIDE.md 何时使用

✅ **当你需要**:
- 了解 API Key 安全最佳实践
- 处理泄露的 Key
- 设置密钥轮换策略
- 在生产环境部署
- 了解环境变量管理

❌ **当你不需要**:
- 只是快速测试系统
- 只是开发环境使用

### 📖 DEPLOYMENT_GUIDE.md 何时使用

✅ **当你需要**:
- 详细的部署步骤
- 完整的配置说明
- 故障排查和诊断
- 维护和监控指导
- 系统验证清单

❌ **当你不需要**:
- 只是快速查询某个命令
- 已经部署成功

### 📖 QUICK_REFERENCE.md 何时使用

✅ **当你需要**:
- 快速查询某个命令
- 查看 API 端点
- 理解系统架构
- 查看 Prompt 和工具列表
- 快速参考（速查表）

❌ **当你需要**:
- 详细的故障排查
- 完整的部署指南
- 安全最佳实践

### 🐍 setup_and_verify.py 何时使用

✅ **当你需要**:
- 一键自动配置和验证
- 交互式设置 .env
- 检查系统先决条件
- 启动容器和测试 API
- 新手用户快速开始

❌ **当你需要**:
- 手动控制部署流程
- 自定义高级配置

---

## 🏗️ 系统架构一览

```
┌─────────────────────────────────────────────────┐
│         Frontend Layer (Port 3000)              │
├─────────────────────────────────────────────────┤
│  ├─ Web UI (/) - Main interface                │
│  ├─ Admin Console (/admin) - Configuration     │
│  └─ Static Files - HTML, CSS, JS               │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┬──────────────┬──────────────┐
│ LLM Service  │ Prompt Svc   │ Agent Svc    │
│ (Port 8001)  │ (Port 8002)  │ (included)   │
└──────────────┴──────────────┴──────────────┘
        │            │            │
        └────────────┼────────────┘
                     │
        ┌────────────┴────────────┐
        ▼            ▼            ▼
    OpenAI API  ERP/CRM/HRM   Cache &
                               Database
```

---

## 💡 实用提示

### 提示 1: 快速切换模型

```env
# 如果 GPT-4 太贵，改用 GPT-3.5-turbo
OPENAI_MODEL=gpt-3.5-turbo

# 重启容器生效
docker-compose -f docker-compose.lite.yml restart
```

### 提示 2: 性能调优

```env
# 增加缓存时间（减少 API 调用）
CACHE_TTL=7200  # 从 3600 改为 7200（2 小时）

# 启用日志以诊断问题
LOG_LEVEL=DEBUG
```

### 提示 3: 开发时使用模拟数据

```env
# 不消耗 API 配额，用于开发测试
USE_MOCK_DATA=true

# 生产环境必须改为 false
USE_MOCK_DATA=false
```

### 提示 4: 监控 API 使用情况

```bash
# 查看 Prompt Service 的请求
docker-compose -f docker-compose.lite.yml logs prompt_service | grep "GET\|POST"

# 监控资源使用
watch 'docker stats --no-stream'
```

---

## ✅ 验证清单

在开始使用之前，确保：

- [ ] 已读 QUICK_REFERENCE.md
- [ ] 已运行 setup_and_verify.py
- [ ] .env 文件已创建并配置
- [ ] Docker 容器正在运行
- [ ] 管理控制台可以访问
- [ ] API 返回 200 状态码
- [ ] Prompt 模板显示正确
- [ ] Agent 工具可以拖拽

---

## 📞 故障排查决策树

```
遇到问题？
├─ 关于安全的问题？
│  └─ 查看 SECURITY_GUIDE.md
├─ 需要快速查询？
│  └─ 查看 QUICK_REFERENCE.md
├─ 关于部署的问题？
│  ├─ 需要详细步骤？
│  │  └─ 查看 DEPLOYMENT_GUIDE.md
│  └─ 需要自动化？
│     └─ 运行 setup_and_verify.py
└─ 其他问题？
   ├─ 查看容器日志
   │  └─ docker-compose logs -f
   └─ 检查管理控制台
      └─ http://localhost:3000/admin
```

---

## 📚 相关资源

### 官方文档
- [OpenAI API 文档](https://platform.openai.com/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Docker 文档](https://docs.docker.com/)

### 工具
- [Postman](https://www.postman.com/) - API 测试
- [VS Code](https://code.visualstudio.com/) - 代码编辑
- [Docker Desktop](https://www.docker.com/products/docker-desktop) - 容器管理

### 最佳实践
- [12 Factor App](https://12factor.net/)
- [OWASP 安全指南](https://owasp.org/)

---

## 🎉 开始使用

### 第一步：快速开始（推荐）

```bash
python3 setup_and_verify.py
```

### 第二步：打开管理控制台

```bash
open http://localhost:3000/admin
```

### 第三步：创建你的第一个自定义 Prompt

1. 点击 "Prompt Management" 标签
2. 点击 "Create New Prompt" 按钮
3. 填入信息
4. 点击 "Save"

### 第四步：配置 Agent 工具

1. 点击 "Agent Tools" 标签
2. 拖拽重新排序工具
3. 启用/禁用需要的工具
4. 点击 "Save Tool Order"

---

**文档版本**: 1.0.0  
**更新日期**: 2024-01-15  
**维护者**: AI Platform Team  
**语言**: 简体中文 🇨🇳

🎯 **下一步**: 选择上面的一个文档，开始阅读吧！
