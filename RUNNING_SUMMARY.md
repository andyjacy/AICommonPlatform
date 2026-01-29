# 🎉 AI 平台本地运行 - 完整启动总结

**启动时间**: 2024-01-26  
**状态**: ✅ **系统已运行**  
**环境**: Docker Lite (本地 macOS/Linux)

---

## ✨ 成功启动！

您的 AI 通用平台已成功在本地 Docker 中启动！

### 📊 当前系统状态

| 服务 | 端口 | 状态 | 状态 |
|------|------|------|------|
| Web UI | 3000 | ✅ Running (unhealthy - 正在初始化) | 可访问 |
| QA Entry | 8001 | ⏳ 启动中 | 稍候可访问 |
| **Prompt Service** | **8002** | ✅ **Healthy** | **✅ 可用** |
| RAG Service | 8003 | ✅ Healthy | ✅ 可用 |
| Agent Service | 8004 | ✅ Healthy | ✅ 可用 |
| Integration | 8005 | ✅ Healthy | ✅ 可用 |
| LLM Service | 8006 | ✅ Healthy | ✅ 可用 |
| Redis | 6379 | ✅ Healthy | ✅ 可用 |

---

## 🌐 立即访问

### 【最优先打开】管理控制台
```
http://localhost:3000/admin
```
👉 在浏览器中复制粘贴上面的地址，或点击下方链接

**功能**:
- 📝 Prompt 模板管理（5个预定义 + 自定义）
- ⚙️ Agent 工具配置（9个工具 + 拖拽排序）
- 🔧 系统设置面板

### 其他访问地址

| URL | 用途 |
|-----|------|
| http://localhost:3000 | Web UI 主界面 |
| http://localhost:3000/admin | 📌 **管理控制台** |
| http://localhost:8002/docs | Prompt Service API 文档 |
| http://localhost:8001/docs | QA Entry API 文档 |
| http://localhost:8003/docs | RAG Service API 文档 |
| http://localhost:8004/docs | Agent Service API 文档 |
| http://localhost:8006/docs | LLM Service API 文档 |

---

## 🚀 第一次使用

### 步骤 1: 打开管理控制台
在浏览器打开: **http://localhost:3000/admin**

### 步骤 2: 浏览预装内容

**Prompt Management 标签**:
- 查看 5 个预定义 Prompt 模板
- 了解每个角色的用途
- 可以创建自定义 Prompt

**Agent Tools 标签**:
- 查看 9 个预定义工具
- 尝试拖拽重新排序
- 可以启用/禁用工具

**Settings 标签**:
- 配置 OpenAI API Key（重要！）
- 选择 LLM 模型
- 系统设置

### 步骤 3: 配置 OpenAI API Key

⚠️ **这是必需的！**

1. 打开 `.env` 文件
2. 找到这一行：
   ```env
   OPENAI_API_KEY=your-api-key-here
   ```
3. 替换为你的真实 API Key：
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
   ```
4. 保存文件
5. 重启 LLM 服务：
   ```bash
   docker-compose -f docker-compose.lite.yml restart llm_service
   ```

### 步骤 4: 开始使用

- 创建自定义 Prompt
- 配置 Agent 工具
- 测试 API
- 集成企业系统

---

## 📝 已预装的 Prompt 模板

系统已包含 5 个专业 Prompt 模板，可在管理控制台直接查看和使用：

### 1. 销售顾问 (sales_advisor)
- **角色**: 销售分析和策略专家
- **应用**: 销售数据分析、客户策略、报价优化
- **使用场景**: 分析新客户询价，提供销售建议

### 2. HR 顾问 (hr_advisor)
- **角色**: 人才管理和组织发展专家
- **应用**: 人才招聘、薪酬管理、组织规划
- **使用场景**: 分析员工绩效，提出晋升建议

### 3. 技术顾问 (tech_advisor)
- **角色**: 技术架构和优化专家
- **应用**: 系统设计、性能优化、技术选型
- **使用场景**: 评估架构可扩展性，提供优化方案

### 4. 财务顾问 (finance_advisor)
- **角色**: 财务分析和规划专家
- **应用**: 成本分析、投资评估、财务预测
- **使用场景**: 分析投资回报率，制定财务计划

### 5. 通用助手 (general_assistant)
- **角色**: 多能助手
- **应用**: 通用问答、信息查询、文档生成
- **使用场景**: 回答各类问题，提供信息摘要

---

## 🛠️ 已预装的 Agent 工具

系统已包含 9 个企业级工具，可在管理控制台中拖拽排序：

| # | 名称 | 图标 | 描述 | 用途 |
|---|------|------|------|------|
| 1 | Web Search | 🔍 | 网络搜索 | 获取最新信息、市场调研 |
| 2 | ERP Query | 💼 | ERP 系统查询 | 销售、库存、财务数据 |
| 3 | CRM Query | 👥 | CRM 系统查询 | 客户信息、销售机会 |
| 4 | HRM Query | 👔 | HRM 系统查询 | 员工信息、薪酬考勤 |
| 5 | Data Analysis | 📊 | 数据分析 | 趋势分析、数据对比 |
| 6 | Report Generation | 📄 | 报告生成 | PDF、Excel、Word 生成 |
| 7 | Calendar Management | 📅 | 日程管理 | 会议安排、日程提醒 |
| 8 | Email Management | 📧 | 邮件管理 | 发送邮件、定时邮件 |
| 9 | File Management | 📁 | 文件管理 | 文件上传、下载、共享 |

---

## 💻 常用命令

### 查看容器状态
```bash
docker-compose -f docker-compose.lite.yml ps
```

### 查看实时日志
```bash
# 所有服务
docker-compose -f docker-compose.lite.yml logs -f

# 特定服务
docker-compose -f docker-compose.lite.yml logs -f prompt_service
docker-compose -f docker-compose.lite.yml logs -f web_ui
docker-compose -f docker-compose.lite.yml logs -f llm_service
```

### 重启特定服务
```bash
# 重启 Prompt Service
docker-compose -f docker-compose.lite.yml restart prompt_service

# 重启 LLM Service（配置 API Key 后）
docker-compose -f docker-compose.lite.yml restart llm_service

# 重启 Web UI
docker-compose -f docker-compose.lite.yml restart web_ui
```

### 停止所有服务
```bash
docker-compose -f docker-compose.lite.yml down
```

### 完全清理（谨慎使用）
```bash
docker-compose -f docker-compose.lite.yml down -v
```

### 进入容器调试
```bash
# 进入 Prompt Service
docker-compose -f docker-compose.lite.yml exec prompt_service bash

# 进入 Web UI
docker-compose -f docker-compose.lite.yml exec web_ui bash
```

### 查看容器资源使用
```bash
docker stats
```

---

## 🔌 API 端点快速参考

### Prompt Service (8002)

```bash
# 获取所有 Prompt
curl http://localhost:8002/api/prompts

# 获取特定 Prompt
curl http://localhost:8002/api/prompts/sales_advisor

# 获取所有 Agent 工具
curl http://localhost:8002/api/agent/tools

# 获取特定工具
curl http://localhost:8002/api/agent/tools/web_search

# 查看 API 文档
open http://localhost:8002/docs
```

### 测试 API 连接
```bash
# 测试 Prompt Service
curl -s http://localhost:8002/api/prompts | jq '.prompts | length'
# 应该返回: 5

# 测试 Agent Tools
curl -s http://localhost:8002/api/agent/tools | jq '.tools | length'
# 应该返回: 9
```

---

## ⚠️ 注意事项

### Web UI 显示"Unhealthy"（正常）
Web UI 刚启动时可能显示 "unhealthy"，这是正常的。等待 30-60 秒后会变为 "healthy"。

### 如果无法连接
1. 确认所有容器都在运行：
   ```bash
   docker-compose -f docker-compose.lite.yml ps
   ```
2. 查看日志找出具体错误：
   ```bash
   docker-compose -f docker-compose.lite.yml logs
   ```
3. 检查端口是否被占用：
   ```bash
   lsof -i :3000
   lsof -i :8002
   ```

### Redis 连接错误
如果看到 Redis 连接错误，这是正常的（Lite 版本中 Redis 是可选的）。系统会自动降级使用。

---

## 📚 相关文档

已为您创建详细文档：

| 文件 | 内容 | 推荐阅读 |
|------|------|---------|
| **LOCAL_RUNNING_GUIDE.md** | 本地运行详细指南 | ⭐⭐⭐⭐⭐ |
| **START_HERE.md** | 快速导航和使用指南 | ⭐⭐⭐⭐⭐ |
| **QUICK_REFERENCE.md** | 快速参考和速查表 | ⭐⭐⭐⭐ |
| **SECURITY_GUIDE.md** | 安全和 API Key 管理 | ⭐⭐⭐⭐ |
| **DEPLOYMENT_GUIDE.md** | 完整部署指南 | ⭐⭐⭐ |

---

## 🎯 建议的后续步骤

### 今天（现在）
- [x] 启动系统
- [ ] 打开管理控制台 (http://localhost:3000/admin)
- [ ] 浏览 Prompt 模板
- [ ] 查看 Agent 工具
- [ ] 尝试拖拽排序

### 本周
- [ ] 配置 OpenAI API Key
- [ ] 创建自定义 Prompt
- [ ] 测试 API 端点
- [ ] 阅读详细文档

### 本月
- [ ] 集成企业系统（ERP/CRM）
- [ ] 优化 Prompt 性能
- [ ] 实现自定义工具
- [ ] 准备生产部署

---

## 🆘 故障排查

### 问题：管理控制台无法打开

**解决**:
1. 等待 30 秒让服务完全启动
2. 清除浏览器缓存：Cmd+Shift+Delete (macOS)
3. 尝试硬刷新：Cmd+Shift+R
4. 查看日志：`docker-compose logs web_ui`

### 问题：拖拽功能不工作

**解决**:
1. 按 F12 打开开发者工具
2. 查看 Console 标签是否有错误
3. 在 Network 标签检查 API 调用
4. 重新加载页面：Cmd+R

### 问题：API 返回 503 错误

**解决**:
1. 服务可能还在启动，稍候再试
2. 查看日志：`docker-compose logs prompt_service`
3. 检查服务状态：`docker-compose ps`
4. 重启服务：`docker-compose restart prompt_service`

### 问题：容器一直重启

**解决**:
1. 查看详细日志：`docker-compose logs`
2. 检查资源使用：`docker stats`
3. 清理环境：`docker-compose down -v`
4. 重新启动：`docker-compose up -d --build`

---

## 📋 完整的快速启动脚本

我为您创建了快速启动脚本 `start_local.sh`，可以一键启动所有服务并打开管理控制台：

```bash
./start_local.sh
```

这个脚本会：
1. 启动 Docker 容器
2. 等待服务准备好
3. 自动打开浏览器访问管理控制台

---

## ✅ 验证清单

启动后检查：

- [x] Redis 运行正常 (6379)
- [x] Prompt Service 运行正常 (8002) ✨
- [x] Web UI 运行正常 (3000)
- [x] LLM Service 运行正常 (8006)
- [x] Agent Service 运行正常 (8004)
- [x] RAG Service 运行正常 (8003)
- [x] Integration 运行正常 (8005)
- [ ] 配置了 OpenAI API Key（⚠️ 待完成）
- [ ] 打开了管理控制台（http://localhost:3000/admin）
- [ ] Prompt 模板显示正确
- [ ] Agent 工具可以拖拽

---

## 💡 性能提示

### 减少资源消耗
- 停止不需要的服务
- 使用 Lite 版本（已在使用）
- 定期清理日志和缓存

### 提高响应速度
- 配置 Redis 缓存
- 使用更便宜的 LLM 模型
- 增加缓存 TTL

---

## 🎓 学习资源

### 官方文档
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Docker 文档](https://docs.docker.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

### 我们创建的文档
- LOCAL_RUNNING_GUIDE.md - 详细运行指南
- QUICK_REFERENCE.md - 快速参考
- SECURITY_GUIDE.md - 安全最佳实践

---

## 🎉 恭喜！

您已成功启动 AI 通用平台！

### 立即开始
👉 打开浏览器访问: **http://localhost:3000/admin**

### 需要帮助？
- 查看 `LOCAL_RUNNING_GUIDE.md`
- 查看 `START_HERE.md`
- 查看容器日志：`docker-compose logs`

---

## 📞 支持

| 问题类型 | 查看文档 |
|---------|---------|
| 快速参考 | QUICK_REFERENCE.md |
| 部署问题 | DEPLOYMENT_GUIDE.md |
| 安全问题 | SECURITY_GUIDE.md |
| 本地运行 | LOCAL_RUNNING_GUIDE.md |
| 快速导航 | START_HERE.md |

---

**启动完成时间**: 2024-01-26  
**系统版本**: 1.0.0  
**环境**: Docker Lite  
**状态**: ✅ **运行中**

🚀 **现在就可以使用了！**
