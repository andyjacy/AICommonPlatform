# 🚀 系统现状快速参考

**最后更新**: 2024年  
**状态**: ✅ 运行中

---

## 📍 当前系统状态

### Docker 容器
```
✅ Web UI (port 3000)           - 正常
✅ Prompt Service (port 8002)   - 正常
✅ LLM Service (port 8006)      - 正常
✅ QA Entry (port 8001)         - 正常
✅ RAG Service (port 8003)      - 正常
✅ Agent Service (port 8004)    - 正常
✅ Integration (port 8005)      - 正常
✅ Redis (port 6379)            - 正常
```

### 最近更改

| 项目 | 类型 | 状态 |
|------|------|------|
| 架构学习模块 | ✅ 删除 | 完成 |
| /admin 路由 | ✅ 添加 | 运行中 |
| QA 追踪功能 | ✅ 保留 | 正常 |

---

## 🔗 快速访问

### Web 应用
- **主页**: http://localhost:3000
- **管理控制台**: http://localhost:3000/admin
- **健康检查**: http://localhost:3000/health

### 主要 API

#### QA 追踪 API
```bash
POST /api/trace/qa/ask
{
  "question": "销售情况如何？",
  "user_id": "test_user"
}
```

#### 服务状态
```bash
GET /api/services/status
```

#### Prompts
```bash
GET /api/prompts
```

#### RAG 搜索
```bash
POST /api/rag/search
{
  "query": "销售",
  "top_k": 5
}
```

#### Agent 工具
```bash
GET /api/agent/tools
```

---

## 🎯 常见操作

### 查看系统日志
```bash
docker logs -f ai_lite_web_ui
```

### 重启服务
```bash
docker-compose -f docker-compose.lite.yml restart web_ui
```

### 完全重建
```bash
docker-compose -f docker-compose.lite.yml up -d --build
```

### 停止所有服务
```bash
docker-compose -f docker-compose.lite.yml down
```

---

## 📚 文档导航

- **系统架构**: `docs/ARCHITECTURE.md`
- **部署指南**: `LOCAL_RUNNING_GUIDE.md`
- **API 文档**: `docs/API.md`
- **删除记录**: `CLEANUP_COMPLETE.md`
- **操作指南**: `QUICKSTART.md`

---

## ❌ 已删除功能

- ❌ 架构学习模块
- ❌ `/api/trace/architecture` API
- ❌ 系统架构可视化
- ❌ 8 阶段流程展示

## ✅ 现有功能

- ✅ QA 问答系统
- ✅ 调用链追踪
- ✅ Prompt 管理
- ✅ 知识库搜索
- ✅ Agent 工具
- ✅ 管理控制台
- ✅ 系统集成

---

## 🔧 故障排除

### 404 错误
- 检查路由是否存在
- 确认容器正在运行
- 查看 Docker 日志

### 容器无法启动
```bash
docker-compose -f docker-compose.lite.yml up -d
docker logs ai_lite_web_ui
```

### 性能问题
- 检查 Docker 资源使用
- 重启相关服务
- 查看系统日志

---

## 📞 需要帮助？

1. 查看 `CLEANUP_COMPLETE.md` - 了解最近的更改
2. 查看 `docs/ARCHITECTURE.md` - 系统架构
3. 查看 `LOCAL_RUNNING_GUIDE.md` - 运行指南
4. 检查 Docker 日志 - 诊断问题

---

**✨ 系统已清理完毕，可以正常使用！**
