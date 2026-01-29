# 🚀 AI Common Platform - 轻量级 Docker 运行成功！

**启动时间**: 2026-01-27  
**版本**: 1.2.0  
**模式**: 轻量级 (Lite Mode)  
**状态**: ✅ 所有核心服务已启动

---

## 📊 服务状态

| 服务 | 端口 | 状态 | 说明 |
|------|------|------|------|
| 🌐 Web UI | 3000 | ✅ 运行 | 用户界面和管理后台 |
| ❓ QA Entry | 8001 | ✅ 运行 | 问答入口服务 |
| 📚 RAG Service | 8003 | ✅ 运行 | 知识库检索服务 |
| 🔍 Prompt Service | 8002 | ✅ 运行 | 提示词管理 |
| 🤖 Agent Service | 8004 | ✅ 运行 | 企业系统集成 |
| 🔗 Integration | 8005 | ✅ 运行 | 数据集成服务 |
| 💡 LLM Service | 8006 | ✅ 运行 | 大模型接口 |
| 🗄️ Redis | 6379 | ✅ 运行 | 缓存和消息队列 |

---

## 🎯 快速开始

### 1️⃣ 访问 Web UI
```
http://localhost:3000
```

### 2️⃣ 配置 LLM 模型

在 Web UI 中:
```
菜单 → LLM 模型管理 → 添加新模型
```

**选项 A: ChatAnywhere (推荐👍)**
```
提供商: chatanywhere
API Key: 从 https://chatanywhere.com.cn/ 获取
模型: gpt-3.5-turbo
特点: 免费、快速、无需信用卡
```

**选项 B: OpenAI**
```
提供商: openai
API Key: 从 https://platform.openai.com 获取
模型: gpt-3.5-turbo 或 gpt-4
特点: 更准确，需要 API 配额
```

### 3️⃣ 测试问答功能

在 Web UI 中提问:
```
"2024年Q1的销售业绩如何？"
```

或使用 API:
```bash
curl -X POST http://localhost:8001/api/qa/ask \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "2024年Q1的销售业绩如何？",
    "user_id": "test_user"
  }'
```

---

## 📖 系统架构

```
用户界面 (Web UI)
    ↓
问答入口 (QA Entry) ←→ 知识库 (RAG Service)
    ↓
大模型接口 (OpenAI / ChatAnywhere)
    ↓
生成答案
```

### 数据流程

1. **问题输入** → Web UI → QA Entry
2. **意图分类** → 确定问题类型
3. **知识库检索** → RAG Service (搜索相关文档)
4. **LLM 处理** → 调用 OpenAI 或 ChatAnywhere
5. **答案生成** → 返回结构化答案
6. **呈现给用户** → Web UI

---

## 🔧 常用命令

### 查看日志
```bash
# 查看所有服务日志（持续）
docker-compose -f docker-compose.lite.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.lite.yml logs -f qa_entry

# 查看最后 50 行日志
docker-compose -f docker-compose.lite.yml logs --tail 50
```

### 管理服务
```bash
# 查看所有服务状态
docker-compose -f docker-compose.lite.yml ps

# 重启特定服务
docker-compose -f docker-compose.lite.yml restart qa_entry

# 重启所有服务
docker-compose -f docker-compose.lite.yml restart

# 停止所有服务
docker-compose -f docker-compose.lite.yml down

# 启动所有服务
docker-compose -f docker-compose.lite.yml up -d
```

### 进入容器
```bash
# 进入 qa_entry 容器
docker exec -it ai_lite_qa_entry /bin/bash

# 查看容器中的文件
docker exec ai_lite_qa_entry ls -la /app
```

---

## 🧪 测试场景

### 场景 1: 销售数据查询
**问题**: "2024年Q1的销售业绩如何？"
**期望**: 返回销售数据和分析

### 场景 2: HR 信息查询
**问题**: "员工的年假有多少天？"
**期望**: 返回员工手册中的假期信息

### 场景 3: 技术架构查询
**问题**: "系统采用什么样的架构？"
**期望**: 返回技术架构说明

### 场景 4: 知识库无结果
**问题**: "公司在火星有办公室吗？"
**期望**: 返回友好的无结果提示

---

## 📊 知识库内容

系统包含 10 个预置文档，涵盖多个领域：

| 文档 | 分类 | 内容 |
|------|------|------|
| Q1销售报告 | sales | 销售数据、增长率、地区分布 |
| 员工手册 | hr | 薪资、假期、考勤、福利 |
| 技术架构 | technical | 微服务架构、部署方案 |
| 财务预算 | finance | 预算分配、ROI 预期 |
| 客户案例 | case_study | 实施案例、成果展示 |
| 产品功能 | product | 平台功能清单、特性 |
| Q2销售计划 | sales | 销售目标、策略、行动项 |
| 安全政策 | security | 数据加密、访问控制 |
| 技术栈 | technical | 依赖版本、技术选型 |
| 常见问题 | support | FAQ、故障排除 |

---

## ⚙️ 配置管理

### 查看/修改 LLM 配置
```bash
# 查看所有模型
curl http://localhost:3000/api/llm/models/list

# 获取特定模型详情
curl http://localhost:3000/api/llm/models/1

# 更新模型配置
curl -X PUT http://localhost:3000/api/llm/models/1 \
  -H 'Content-Type: application/json' \
  -d '{
    "temperature": 0.8,
    "max_tokens": 2048
  }'
```

### 管理知识库
```bash
# 查看所有文档
curl http://localhost:8003/api/rag/documents

# 搜索知识库
curl -X POST http://localhost:8003/api/rag/search \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "销售",
    "top_k": 3
  }'
```

---

## 🐛 故障排除

### 问题: 服务无法启动

**症状**: Container 显示 Exited (1)

**排查**:
```bash
# 查看错误日志
docker-compose -f docker-compose.lite.yml logs qa_entry

# 重建镜像（清除缓存）
docker-compose -f docker-compose.lite.yml build --no-cache qa_entry

# 重启服务
docker-compose -f docker-compose.lite.yml restart qa_entry
```

### 问题: 无法连接到 LLM

**症状**: 返回错误 "Failed to call LLM"

**排查**:
1. 检查 API Key 是否配置正确
2. 检查网络连接
3. 检查 API Key 是否有有效期
4. 查看服务日志获取详细错误信息

### 问题: 知识库搜索返回无结果

**症状**: 查询返回 "无相关结果" 提示

**排查**:
1. 尝试使用不同的关键词
2. 检查是否有相关文档
3. 查看 RAG 服务日志
4. 测试其他已知存在的文档

---

## 📚 相关文档

- **[CHATANYWHERE_INTEGRATION.md](./CHATANYWHERE_INTEGRATION.md)** - ChatAnywhere 详细集成指南
- **[IMPROVEMENT_SUMMARY.md](./IMPROVEMENT_SUMMARY.md)** - 系统改进总结
- **[QA_LLM_INTEGRATION.md](./QA_LLM_INTEGRATION.md)** - LLM 集成技术文档

---

## 🎓 学习资源

### 系统架构学习
- 微服务架构设计
- 异步编程（async/await）
- 知识库检索（RAG）

### 大模型集成
- OpenAI API 使用
- ChatAnywhere 免费 API
- Prompt 工程最佳实践

### 数据管理
- SQLite 数据库操作
- Redis 缓存使用
- 向量数据库基础

---

## 💡 性能优化建议

### 1. 缓存优化
```python
# Redis 缓存配置
CACHE_TTL = 3600  # 1小时
CACHE_MAX_SIZE = 1000  # 最多 1000 条记录
```

### 2. 批量处理
```bash
# 批量处理多个问题
# 使用异步 API 提高吞吐量
```

### 3. 日志管理
```bash
# 定期清理日志
# 监控服务内存占用
```

---

## 🔐 安全建议

### API Key 保护
- ✅ 使用环境变量管理敏感信息
- ✅ 不要在代码中硬编码 API Key
- ✅ 定期轮换 API Key
- ✅ 在生产环境使用 HTTPS

### 数据安全
- ✅ 数据库使用加密
- ✅ 实施访问控制
- ✅ 定期备份数据
- ✅ 审计日志记录

---

## 📞 支持和反馈

### 遇到问题？

1. **查看日志**: 
   ```bash
   docker-compose -f docker-compose.lite.yml logs -f
   ```

2. **检查配置**: 
   ```bash
   curl http://localhost:3000/api/llm/models/list
   ```

3. **测试连接**: 
   ```bash
   curl http://localhost:8001/health
   ```

4. **查看文档**: 
   - [CHATANYWHERE_INTEGRATION.md](./CHATANYWHERE_INTEGRATION.md)
   - [IMPROVEMENT_SUMMARY.md](./IMPROVEMENT_SUMMARY.md)

---

## ✅ 验收清单

运行轻量级 Docker 前，请确保：

- [ ] Docker 已安装 (版本 ≥ 20.10)
- [ ] Docker Compose 已安装 (版本 ≥ 2.0)
- [ ] 本地端口 3000, 8001-8006, 6379 未被占用
- [ ] 至少 2GB 可用磁盘空间
- [ ] 互联网连接稳定

运行后，请验证：

- [ ] 所有 10 个容器都在运行
- [ ] Web UI 可以访问 (http://localhost:3000)
- [ ] API 返回 200 状态码
- [ ] 能够成功配置 LLM 模型
- [ ] 能够成功提问并获得答案

---

## 🎉 完成！

您现在已成功启动了 AI Common Platform 的轻量级版本！

### 下一步建议：

1. **体验系统**
   - 访问 Web UI
   - 配置 LLM 模型
   - 尝试提问功能

2. **学习系统**
   - 阅读系统架构文档
   - 理解数据流程
   - 研究代码实现

3. **扩展功能**
   - 添加自己的知识库文档
   - 自定义提示词
   - 集成企业系统

### 需要帮助？

查看以下文档获取详细信息：
- 🌐 [ChatAnywhere 集成指南](./CHATANYWHERE_INTEGRATION.md)
- 🔧 [系统改进总结](./IMPROVEMENT_SUMMARY.md)
- 📖 [LLM 集成技术文档](./QA_LLM_INTEGRATION.md)

---

**祝您使用愉快！** 🚀✨
