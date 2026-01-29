# 🎉 AI 平台本地运行指南

## ✅ 系统已启动！

所有 Docker 容器已成功启动。以下是访问地址：

---

## 🌐 访问 URLs

### 📱 Web UI
- **主界面**: http://localhost:3000
- **管理控制台**: http://localhost:3000/admin ⭐ 推荐首先打开这个

### 🔌 API 服务
| 服务 | 端口 | 访问地址 | 功能 |
|------|------|---------|------|
| **Web UI** | 3000 | http://localhost:3000 | 主界面和管理控制台 |
| **QA Entry** | 8001 | http://localhost:8001/docs | 问答入口 API |
| **Prompt Service** | 8002 | http://localhost:8002/docs | Prompt 管理和工具 API ⭐ |
| **RAG Service** | 8003 | http://localhost:8003/docs | RAG 服务 API |
| **Agent Service** | 8004 | http://localhost:8004/docs | Agent 服务 API |
| **Integration** | 8005 | http://localhost:8005/docs | 集成服务 API |
| **LLM Service** | 8006 | http://localhost:8006/docs | LLM 调用 API |

---

## 🚀 快速开始

### 1️⃣ 打开管理控制台（最重要）
```bash
# 在浏览器中打开：
open http://localhost:3000/admin
```

### 2️⃣ 探索功能
- 📝 **Prompt Management** - 查看和创建 Prompt 模板
- ⚙️ **Agent Tools** - 配置和拖拽工具
- 🔧 **Settings** - 系统设置

### 3️⃣ 测试 API
```bash
# 获取所有 Prompt 模板
curl http://localhost:8002/api/prompts

# 获取所有 Agent 工具
curl http://localhost:8002/api/agent/tools

# 查看 API 文档
open http://localhost:8002/docs
```

---

## 📚 可用的 Prompt 模板

系统已预装 5 个专业 Prompt 模板：

1. **销售顾问** (sales_advisor)
   - 角色：销售分析和策略专家
   - API：http://localhost:8002/api/prompts/sales_advisor

2. **HR 顾问** (hr_advisor)
   - 角色：人才管理和组织发展专家
   - API：http://localhost:8002/api/prompts/hr_advisor

3. **技术顾问** (tech_advisor)
   - 角色：技术架构和优化专家
   - API：http://localhost:8002/api/prompts/tech_advisor

4. **财务顾问** (finance_advisor)
   - 角色：财务分析和规划专家
   - API：http://localhost:8002/api/prompts/finance_advisor

5. **通用助手** (general_assistant)
   - 角色：多能助手
   - API：http://localhost:8002/api/prompts/general_assistant

---

## 🛠️ 可用的 Agent 工具

系统已预装 9 个企业级工具：

1. **Web 搜索** 🔍 (web_search)
2. **ERP 查询** 💼 (erp_query)
3. **CRM 查询** 👥 (crm_query)
4. **HRM 查询** 👔 (hrm_query)
5. **数据分析** 📊 (data_analysis)
6. **报告生成** 📄 (report_generation)
7. **日程管理** 📅 (calendar_management)
8. **邮件管理** 📧 (email_management)
9. **文件管理** 📁 (file_management)

---

## 💡 常用命令

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
```

### 停止所有容器
```bash
docker-compose -f docker-compose.lite.yml down
```

### 重启特定服务
```bash
docker-compose -f docker-compose.lite.yml restart prompt_service
```

### 进入容器内部
```bash
docker-compose -f docker-compose.lite.yml exec prompt_service bash
```

---

## 🔧 配置 OpenAI API Key

### 现在配置 API Key（重要！）

打开 `.env` 文件，找到这一行：

```env
OPENAI_API_KEY=your-api-key-here
```

替换为你的真实 API Key：

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
```

然后重启 LLM 服务：

```bash
docker-compose -f docker-compose.lite.yml restart llm_service
```

### 获取 API Key

1. 访问 https://platform.openai.com/api-keys
2. 创建或复制你的 API Key
3. 粘贴到 `.env` 文件中
4. 保存并重启容器

---

## 📊 管理控制台功能介绍

### Tab 1: Prompt Management 📝

| 功能 | 说明 |
|------|------|
| **浏览模板** | 查看所有预定义 Prompt 模板 |
| **搜索筛选** | 按名称或角色搜索 |
| **查看详情** | 点击卡片查看完整 Prompt |
| **创建新增** | 创建自定义 Prompt 模板 |
| **编辑修改** | 编辑现有 Prompt |
| **删除操作** | 删除自定义 Prompt |

**如何创建自定义 Prompt**:
1. 点击 "Create New Prompt" 按钮
2. 填入 Name、Role、System Prompt
3. 添加示例（可选）
4. 点击 "Save"

### Tab 2: Agent Tools ⚙️

| 功能 | 说明 |
|------|------|
| **显示工具** | 列表显示所有工具 |
| **拖拽排序** | 拖动卡片重新排序工具 |
| **启用禁用** | 切换开关启用/禁用工具 |
| **查看参数** | 点击工具查看参数定义 |
| **创建工具** | 创建自定义工具 |
| **编辑配置** | 编辑工具参数 |
| **删除工具** | 删除自定义工具 |
| **保存排序** | 点击按钮保存拖拽的顺序 |

**如何拖拽排序**:
1. 选择要排序的工具卡片
2. 向上或向下拖动
3. 看到顺序改变后释放鼠标
4. 点击 "Save Tool Order" 保存

### Tab 3: Settings 🔧

| 功能 | 说明 |
|------|------|
| **API Key** | 配置 OpenAI API Key |
| **模型选择** | 选择 LLM 模型 (gpt-4, gpt-3.5-turbo) |
| **缓存设置** | 配置缓存参数 |
| **日志配置** | 设置日志级别 |

---

## ⚠️ 常见问题

### Q: 浏览器无法连接？
**A**: 
1. 检查容器状态：`docker-compose ps`
2. 查看日志：`docker-compose logs`
3. 等待 30 秒让容器完全启动
4. 清除浏览器缓存并重试

### Q: API 返回 503 错误？
**A**:
1. 服务可能还在启动，请等待
2. 查看日志：`docker-compose logs web_ui`
3. 重启该服务：`docker-compose restart web_ui`

### Q: 拖拽功能不工作？
**A**:
1. 按 F12 打开浏览器开发者工具
2. 查看 Console 标签是否有错误
3. 尝试清除缓存：Cmd+Shift+Delete (Mac)
4. 重新加载页面：Cmd+R

### Q: 如何停止系统？
**A**:
```bash
docker-compose -f docker-compose.lite.yml down
```

---

## 📈 性能监控

### 监控容器资源使用
```bash
docker stats
```

### 查看容器日志统计
```bash
docker-compose logs | wc -l
```

### 检查磁盘使用
```bash
docker system df
```

---

## 🎓 接下来要做的事

### 短期（今天）
- [ ] 打开管理控制台 (http://localhost:3000/admin)
- [ ] 浏览 Prompt 模板
- [ ] 查看 Agent 工具
- [ ] 尝试拖拽排序工具

### 中期（本周）
- [ ] 创建自定义 Prompt
- [ ] 配置 API Key
- [ ] 测试 API 端点
- [ ] 集成企业系统（ERP/CRM）

### 长期（本月）
- [ ] 优化 Prompt 性能
- [ ] 实现自定义工具
- [ ] 添加监控和告警
- [ ] 准备生产部署

---

## 📞 获取帮助

### 查看完整文档
- `START_HERE.md` - 快速导航
- `QUICK_REFERENCE.md` - 速查表
- `SECURITY_GUIDE.md` - 安全指南
- `DEPLOYMENT_GUIDE.md` - 完整部署指南

### 查看日志
```bash
docker-compose -f docker-compose.lite.yml logs -f
```

### 进入容器调试
```bash
docker-compose -f docker-compose.lite.yml exec prompt_service bash
```

---

## ✅ 系统检查清单

启动后检查：

- [x] Redis 运行正常
- [x] Prompt Service 运行正常 (8002)
- [x] Web UI 运行正常 (3000)
- [x] LLM Service 运行正常 (8006)
- [ ] 配置了 OpenAI API Key
- [ ] 管理控制台可以打开
- [ ] Prompt 模板显示正确
- [ ] Agent 工具可以拖拽

---

## 🎉 祝贺！

**系统已在本地成功运行！** 🚀

### 立即打开管理控制台
```bash
open http://localhost:3000/admin
```

或在浏览器地址栏输入：
```
http://localhost:3000/admin
```

---

**启动时间**: 2024-01-26
**状态**: ✅ 运行中
**环境**: Docker Lite
**版本**: 1.0.0

祝你使用愉快！ 🎯
