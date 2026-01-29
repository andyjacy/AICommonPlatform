# ⚡ 快速启动指南 - 2025年1月26日

## 🎯 当前系统状态

✅ **所有系统已部署并运行**
- 8 个 Docker 微服务：全部健康
- LLM 集成：已完成（OpenAI + ChatAnywhere）
- 前端修复：已完成（JavaScript 事件处理）
- 知识库：10 个测试文档已加载

---

## 🚀 立即开始

### 1. 启动系统（如果已停止）
```bash
cd /Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform
docker-compose -f docker-compose.lite.yml up -d
```

### 2. 打开 Web UI
```
http://localhost:3000
```

### 3. 配置 LLM 模型
进入"🧠 大模型"页面：
- 点击"➕ 添加模型"
- 选择提供商（OpenAI 或 ChatAnywhere）
- 输入 API Key
- 保存

### 4. 测试 QA 功能
进入"💬 问答中心"：
- 输入问题：`2024年Q1的销售业绩如何？`
- 点击"提问"或按 Enter
- 查看 LLM 回答

---

## 📋 核心服务地址

| 服务 | 地址 | 用途 |
|------|------|------|
| Web UI | http://localhost:3000 | 用户界面 |
| QA Entry | http://localhost:8001 | 问答入口 |
| LLM Service | http://localhost:8006 | LLM 路由 |
| RAG Service | http://localhost:8003 | 知识库搜索 |

---

## 🔧 故障排除

### 如果出现 JavaScript 错误
1. 清除浏览器缓存（Cmd+Shift+Delete）
2. 强制刷新（Cmd+Shift+R）
3. 重启 Web UI：`docker-compose restart web_ui`

### 如果 LLM 不返回回答
1. 检查模型配置是否正确
2. 验证 API Key 有效
3. 查看日志：`docker-compose logs llm_service`

### 查看完整日志
```bash
docker-compose logs web_ui       # Web UI 日志
docker-compose logs qa_entry     # QA 服务日志
docker-compose logs llm_service  # LLM 服务日志
```

---

## 📁 关键文件

- **部署配置**：`docker-compose.lite.yml`
- **前端代码**：`services/web_ui/static/index.html`
- **LLM 逻辑**：`services/qa_entry/services.py`
- **测试说明**：`TESTING_INSTRUCTIONS.md`
- **完整清单**：`DEPLOYMENT_VERIFICATION.md`

---

## ✨ 功能检查清单

- [ ] 打开 Web UI，无空白屏幕
- [ ] 点击左侧导航菜单，页面正确切换
- [ ] 添加 LLM 模型，成功保存
- [ ] 提交 QA 问题，收到回答
- [ ] 知识库搜索，返回结果
- [ ] 浏览器控制台无 JavaScript 错误

---

## 🎓 系统架构

```
用户界面 (Web UI, 3000)
    ↓
QA 入口 (qa_entry, 8001)
    ├→ LLM Service (llm_service, 8006)
    │    ├→ OpenAI API
    │    └→ ChatAnywhere API
    ├→ RAG Service (rag_service, 8003)
    │    └→ 知识库 (10 个文档)
    └→ Redis Cache (6379)
```

---

## 📞 获取帮助

查看完整文档：
- `TESTING_INSTRUCTIONS.md` - 详细测试步骤
- `DEPLOYMENT_VERIFICATION.md` - 完整验证清单
- `DOCKER_DEPLOYMENT_GUIDE.md` - 部署指南
- `API_QUICK_REFERENCE.md` - API 参考

---

## 🎉 已完成的关键工作

1. ✅ Docker 轻量化部署（8 个服务）
2. ✅ LLM 多提供商集成（OpenAI + ChatAnywhere）
3. ✅ 前端 JavaScript 修复（事件处理）
4. ✅ 依赖问题解决（python-json-logger）
5. ✅ 知识库初始化（10 个文档）

---

**系统就绪！现在您可以开始使用 AI 平台了。** 🚀
