# AI Common Platform - 完整功能说明 (v1.1.0)

## 📚 项目概览

**AI Common Platform** 是一个完整的、可学习的企业级 AI 问答系统，包含了现代 AI 应用的所有核心组件。

**最新特性**: 🆕 **调用链追踪系统** - 可视化完整的 AI 处理流程

---

## ✨ 核心特性

### 1️⃣ 完整的 AI 处理流程（8阶段）
```
输入处理 → 意图识别 → 知识检索 → 上下文增强 → Prompt编排 → LLM推理 → 结果处理 → 结果返回
```

### 2️⃣ 检索增强生成 (RAG)
- **向量搜索**: Milvus 向量数据库 (支持百万级规模)
- **全文搜索**: Elasticsearch (中文分词、复杂查询)
- **结果融合**: 多源检索结果的智能合并

### 3️⃣ Agent 工具调用
- 与企业系统的 REST API 集成
- ERP、CRM、HRM、财务系统数据查询
- 权限校验和数据安全

### 4️⃣ Prompt 工程
- 5种预定义角色 (销售顾问、HR顾问、技术顾问、财务顾问、通用助手)
- Chain-of-Thought 推理支持
- Few-shot 学习示例

### 5️⃣ 多LLM模型支持
- OpenAI GPT-4 / GPT-3.5-turbo
- 阿里通义千问 (Qwen)
- 百度文心一言 (Ernie)
- 科大讯飞讯飞星火 (SparkDesk)
- 智谱 GLM-4
- **智能模型选择**: 根据问题复杂度自动选择最合适的模型

### 6️⃣ 调用链追踪（NEW! 🎉）
- **可选追踪**: 一键启用详细的执行流程追踪
- **8层细节**: 每个处理阶段的目的、参数、结果都被记录
- **架构学习**: 通过可视化追踪链理解 AI 系统工作原理
- **调试支持**: 快速定位问题所在的处理阶段

### 7️⃣ 轻量级部署
- **Docker容器化**: 7个微服务 + Web UI
- **优化镜像**: Python 3.11-slim 基础镜像，总体积 < 2GB
- **Redis缓存**: 提高响应速度
- **本地开发**: 可在单台机器上运行全套系统

---

## 📦 系统架构

### 微服务组件

| 服务 | 端口 | 功能 | 技术栈 |
|------|------|------|--------|
| **QA Entry** | 8001 | 问答入口、意图识别 | FastAPI, NLP |
| **RAG Service** | 8003 | 知识检索、向量搜索 | Milvus, Elasticsearch |
| **Prompt Service** | 8002 | Prompt 工程、模板管理 | FastAPI, Jinja2 |
| **LLM Service** | 8006 | LLM 调用、多模型支持 | FastAPI, openai库 |
| **Agent Service** | 8004 | Agent 工具调用、企业集成 | FastAPI, aiohttp |
| **Integration Service** | 8005 | 企业系统集成 (ERP/CRM/HRM) | FastAPI |
| **Web UI** | 3000 | 交互式 Web 界面 | FastAPI, HTML5/CSS3/JS |

### 数据存储

- **Milvus**: 向量存储 (支持百万级相似度搜索)
- **Elasticsearch**: 全文搜索引擎
- **PostgreSQL**: 结构化数据存储
- **Redis**: 缓存和会话管理

---

## 🎯 使用场景

### 场景 1: 企业知识库问答
**用户**: "2024年销售目标是多少?"
**处理流程**:
1. ✅ 输入处理: 清洗问题
2. ✅ 意图识别: 识别为"数据查询"
3. ✅ 知识检索: 从向量库检索相关文档
4. ✅ 上下文增强: 从 ERP 查询实时数据
5. ✅ Prompt编排: 选择销售顾问角色
6. ✅ LLM推理: GPT-4 生成回答
7. ✅ 结果处理: 添加参考文献、置信度
8. ✅ 结果返回: 展示带追踪链的答案

### 场景 2: 流程自动化咨询
**用户**: "如何自动化报销流程?"
**系统特性**:
- Agent 调用多个企业系统的 API
- 整合 HRM、财务、流程系统的信息
- 生成包含成本-效益分析的方案

### 场景 3: 学习 AI 架构
**用户**: 学生、技术爱好者
**收获**:
- 通过可视化追踪链理解 AI 系统
- 看到每一步的具体数据流转
- 学习行业标准的架构模式

---

## 🚀 快速开始

### 前提条件
- Docker & Docker Compose
- 8GB+ RAM (推荐 16GB)
- 本地端口 3000, 6379, 8001-8006 可用

### 安装步骤

```bash
# 1. 进入项目目录
cd /Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform

# 2. 启动所有服务 (轻量级部署)
docker-compose -f docker-compose.lite.yml up -d

# 3. 等待服务就绪 (30-60秒)
docker-compose -f docker-compose.lite.yml ps

# 4. 打开 Web UI
访问: http://localhost:3000
```

### 验证部署

```bash
# 检查所有服务状态
docker-compose -f docker-compose.lite.yml ps

# 测试 API
curl http://localhost:3000/api/services/status
```

---

## 📖 功能指南

### 1. 问答 (QA) 模块

**基本流程**:
1. 在输入框输入问题
2. (可选) 勾选"📊 显示调用链"以启用追踪
3. 点击"提问"按钮
4. 查看答案和追踪链 (如果启用)

**支持的查询类型**:
- 自由文本问答 (最常用)
- 数据查询 (聚合、统计、对比)
- 操作执行 (流程启动、任务分配)
- 推荐建议 (基于数据和历史的智能建议)

### 2. 调用链追踪 (Trace) 模块 🆕

**启用方式**:
1. 进入"问答"模块
2. 勾选"📊 显示调用链"
3. 提出问题
4. 系统自动切换到"调用链追踪"标签页

**查看内容**:
- **追踪 ID**: 唯一标识整个请求
- **处理步骤**: 12 个步骤的详细信息
- **执行时间**: 每步耗时和总耗时
- **数据流转**: 每步的输入输出数据
- **架构说明**: 整个处理流程的详细说明

### 3. 架构学习 (Architecture) 模块 🆕

**打开方式**:
点击侧边栏的"🏗️ 查看 AI 架构"

**包含内容**:
- 8 个核心处理阶段的详细说明
- 每个阶段使用的技术
- 支持的 LLM 模型列表
- 数据源和集成说明
- 关键技术栈

### 4. 知识库搜索 (Knowledge Search) 模块

**功能**:
- 向量搜索: 语义相似性搜索
- 全文搜索: 精确关键词匹配
- 高级搜索: 结合多个搜索条件

**应用场景**:
- 快速定位相关文档
- 探索知识库内容
- 评估 RAG 检索效果

### 5. 系统管理 (System) 模块

**服务状态**:
- 实时查看各微服务的健康状态
- 响应时间和错误率统计

**配置管理**:
- Prompt 模板管理
- LLM 模型选择
- RAG 参数调优

---

## 🎓 学习资源

### 核心文档
1. **[TRACE_GUIDE.md](./TRACE_GUIDE.md)** - 调用链追踪完整指南
2. **[TRACE_DEMO_GUIDE.md](./TRACE_DEMO_GUIDE.md)** - 演示和学习教程
3. **[ENHANCED_UI_GUIDE.md](./ENHANCED_UI_GUIDE.md)** - Web UI 功能说明
4. **[LITE_GUIDE.md](./LITE_GUIDE.md)** - 轻量级部署指南

### 示例问题
推荐的学习问题序列:
```
初级:
1. "什么是 RAG?" → 理解检索增强生成
2. "AI 系统如何理解问题?" → 了解意图识别
3. "如何使用 Prompt 工程?" → 学习 Prompt 的威力

中级:
4. "企业系统集成的意义是什么?" → 理解上下文增强
5. "如何选择合适的 LLM 模型?" → 学习模型选择策略
6. "权限校验在 AI 系统中的作用?" → 理解安全性

高级:
7. "如何优化 RAG 的检索性能?" → 性能优化思路
8. "如何设计自定义的 Agent 工具?" → 扩展系统能力
9. "如何评估生成答案的质量?" → 质量评估方法
```

### 技术深度学习
- [向量数据库原理 (Milvus)](https://milvus.io/)
- [Prompt 工程最佳实践](https://platform.openai.com/docs/guides/prompt-engineering)
- [LLM 应用架构](https://github.com/llm-project)
- [微服务架构设计](https://microservices.io/)

---

## 🔧 配置和自定义

### 修改 Prompt 模板
编辑 `services/prompt_service/prompts.py`:
```python
SALES_ADVISOR_PROMPT = """
你是销售顾问。基于以下信息回答客户的问题:
{context}

问题: {question}
"""
```

### 添加新的 LLM 模型
编辑 `services/llm_service/main.py`:
```python
AVAILABLE_MODELS = {
    "gpt-4": "OpenAI GPT-4",
    "claude-3": "Anthropic Claude-3",  # 新增
}
```

### 调整 RAG 参数
编辑 `services/rag_service/main.py`:
```python
RAG_CONFIG = {
    "top_k": 5,           # 检索返回的文档数
    "similarity_threshold": 0.5,  # 相似度阈值
    "use_rerank": True,   # 是否使用重排
}
```

---

## 📊 性能指标

### 基准测试结果 (在 Mac M1 上)

| 场景 | 响应时间 | 备注 |
|------|---------|------|
| 缓存命中 | 10-50ms | Redis 缓存 |
| 简单问答 | 200-400ms | 无企业数据查询 |
| 数据查询 | 400-800ms | 调用 ERP/CRM |
| 复杂问题 | 800ms-2s | 多步骤处理 |
| 完整追踪 | +50-100ms | 追踪记录开销 |

### 优化建议
- ✅ 启用 Redis 缓存常见问题
- ✅ 并行执行向量搜索和全文搜索
- ✅ 使用轻量级 LLM 模型处理简单问题
- ✅ 预编译常用的 SQL 查询

---

## 🐛 常见问题

### Q: 为什么容器启动失败?
**A**: 检查:
- Docker daemon 是否运行
- 端口是否被占用: `lsof -i :3000`
- 磁盘空间是否充足: `df -h`

### Q: 如何调整 Redis 缓存时间?
**A**: 编辑 `docker-compose.lite.yml`, 查找 `CACHE_TTL` 配置

### Q: 如何关闭 Web UI 的演示数据?
**A**: 修改 `services/web_ui/main.py` 中的 `USE_MOCK_DATA` 设置

### Q: 支持的最大问题长度是多少?
**A**: 建议 < 500 字符，最长 2000 字符

### Q: 如何集成自己的数据源?
**A**: 在 `Integration Service` 中添加新的端点，参考 `services/integration/main.py`

---

## 🤝 贡献和扩展

### 添加新的 Prompt 角色
```python
# 在 services/prompt_service/prompts.py 中
NEW_ROLE_PROMPT = """
[你的 prompt 定义]
"""
```

### 添加新的企业系统集成
```python
# 在 services/integration/main.py 中
@app.post("/api/custom-system/query")
async def query_custom_system(request):
    # 你的集成代码
    pass
```

### 自定义追踪链处理
```python
# 在 services/web_ui/main.py 中
# 修改 CallChain 类的 _get_architecture_description() 方法
```

---

## 📈 路线图

### v1.1.0 (当前) ✅
- ✅ 调用链追踪系统
- ✅ 架构学习模块
- ✅ 8 步处理流程可视化
- ✅ 轻量级部署优化

### v1.2.0 (计划)
- 📋 追踪链持久化存储
- 📋 历史问答查询
- 📋 用户反馈和评分系统
- 📋 A/B 测试框架

### v1.3.0 (计划)
- 📋 流式回答 (Streaming)
- 📋 多轮对话支持
- 📋 知识库管理界面
- 📋 模型评估仪表板

### v2.0.0 (远期)
- 📋 分布式部署支持
- 📋 GPU 加速
- 📋 插件系统
- 📋 企业级安全认证

---

## 📞 支持

### 获取帮助
- 📚 阅读文档: [完整指南列表](.)
- 🐛 提交问题: 在项目中提 Issue
- 💬 社区讨论: 检查 Discussions

### 提供反馈
- ⭐ 给项目 Star
- 📝 提供改进建议
- 🤖 分享你的使用案例

---

## 📄 许可证

MIT License

---

## 🙏 致谢

感谢所有为 AI 开源社区做贡献的人！

特别感谢:
- OpenAI (GPT models)
- Milvus (向量数据库)
- Elasticsearch (搜索引擎)
- FastAPI (Web 框架)

---

**最后更新**: 2026年1月26日

**版本**: v1.1.0

**状态**: ✅ 生产就绪

---

**开始你的 AI 学习之旅吧！🚀**

访问 http://localhost:3000 体验完整的 AI 平台
