# 快速启动指南 - 无硬编码版本

## 🚀 一键启动

```bash
# 进入项目目录
cd /Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform

# 启动所有 Lite 服务（8 个服务）
docker-compose -f docker-compose.lite.yml up -d

# 查看启动状态
docker-compose -f docker-compose.lite.yml ps
```

**预期结果**：
```
✅ ai_lite_agent_service      - Healthy
✅ ai_lite_integration        - Healthy
✅ ai_lite_llm_service        - Healthy
✅ ai_lite_prompt_service     - Healthy
✅ ai_lite_qa_entry           - Healthy
✅ ai_lite_rag_service        - Healthy
✅ ai_lite_redis              - Healthy
✅ ai_lite_web_ui             - Up
```

---

## 🌐 访问 Web UI

打开浏览器访问：
```
http://localhost:3000
```

---

## ✅ 验证配置动态加载

### 1. 测试调用链追踪（查看数据库配置）

```bash
curl -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"销售数据分析"}'
```

**查看返回的 JSON 中**：
- Step 8: `Prompt 组装` → `selected_prompt`: "销售顾问" ✅ **从数据库读取**
- Step 9: `LLM 推理-模型选择` → `selected_model`: "OpenAI GPT-4" ✅ **从数据库读取**

### 2. 测试系统健康检查

```bash
curl http://localhost:3000/api/system/health
```

**返回**：
- 所有 6 个微服务的健康状态
- 无 Mock 数据，全部实时监测

### 3. 测试 QA 接口（调用真实服务）

```bash
curl -X POST http://localhost:3000/api/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"怎样导出销售报告？"}'
```

**返回**：来自真实 QA Entry Service 的回答，不再是 Mock

---

## 🔧 后台管理配置

### 访问 Prompt 配置
```
http://localhost:3000/admin
→ LLM 配置 → Prompt 模板管理
```

可以在此：
- ✅ 添加新的 Prompt 模板
- ✅ 切换默认 Prompt
- ✅ 编辑系统提示词
- ✅ 实时生效（无需重启）

### 访问 LLM 模型配置
```
http://localhost:3000/admin
→ LLM 配置 → 大模型管理
```

可以在此：
- ✅ 添加新的 LLM 模型
- ✅ 设置默认模型
- ✅ 配置 API Key 和端点
- ✅ 实时生效

---

## 🎯 核心改进点

| 功能 | 之前 | 现在 |
|------|------|------|
| Prompt 选择 | ❌ 硬编码"销售顾问" | ✅ 从数据库动态读取 |
| LLM 模型 | ❌ 硬编码"GPT-4" | ✅ 从数据库动态读取 |
| QA 回答 | ❌ Mock 虚拟数据 | ✅ 调用真实服务 |
| 知识库文档 | ❌ Mock 10 个虚拟文档 | ✅ 调用真实 RAG 服务 |
| 工具列表 | ❌ Mock 6 个虚拟工具 | ✅ 调用真实 Agent 服务 |
| 系统监控 | ❌ 硬编码虚拟数据 | ✅ 实时系统资源 |
| 调用链追踪 | ❌ 硬编码配置显示 | ✅ 显示实际使用的配置 |

---

## 📊 性能指标

- **启动时间**: ~15 秒
- **内存占用**: ~2 GB （8 个 lite 服务）
- **CPU 占用**: ~5-15%
- **数据库查询**: <10ms（SQLite）

---

## 🛠️ 常见命令

### 查看日志
```bash
# Web UI 日志
docker-compose -f docker-compose.lite.yml logs -f web_ui

# 所有服务日志
docker-compose -f docker-compose.lite.yml logs -f

# 特定服务日志
docker-compose -f docker-compose.lite.yml logs -f qa_entry
```

### 停止服务
```bash
docker-compose -f docker-compose.lite.yml down
```

### 重启服务
```bash
docker-compose -f docker-compose.lite.yml restart web_ui
```

### 清理并重新启动
```bash
docker-compose -f docker-compose.lite.yml down
docker-compose -f docker-compose.lite.yml build --no-cache
docker-compose -f docker-compose.lite.yml up -d
```

---

## 🔍 调试技巧

### 1. 检查 Prompt 模板是否已配置
```bash
docker-compose -f docker-compose.lite.yml exec -T web_ui \
  python3 -c "
import sqlite3
conn = sqlite3.connect('web_ui.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('SELECT name, role FROM prompts WHERE enabled=1')
for row in cursor.fetchall():
    print(f'Prompt: {row[\"name\"]} -> Role: {row[\"role\"]}')
"
```

### 2. 检查 LLM 模型是否已配置
```bash
docker-compose -f docker-compose.lite.yml exec -T web_ui \
  python3 -c "
import sqlite3
conn = sqlite3.connect('web_ui.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('SELECT name, provider, is_default FROM llm_models WHERE enabled=1')
for row in cursor.fetchall():
    mark = '✓ 默认' if row[2] else ''
    print(f'Model: {row[\"name\"]} -> {row[\"provider\"]} {mark}')
"
```

---

## ⚠️ 故障排除

### 问题：Web UI 无法启动
```bash
# 查看日志
docker-compose -f docker-compose.lite.yml logs web_ui

# 尝试重建
docker-compose -f docker-compose.lite.yml build --no-cache web_ui
docker-compose -f docker-compose.lite.yml up -d web_ui
```

### 问题：数据库配置未生效
1. 检查数据库是否有数据：
   ```bash
   docker-compose -f docker-compose.lite.yml exec -T web_ui \
     python3 -c "
   import sqlite3
   conn = sqlite3.connect('web_ui.db')
   cursor = conn.cursor()
   cursor.execute('SELECT COUNT(*) FROM prompts')
   print(f'Prompt 数量: {cursor.fetchone()[0]}')
   cursor.execute('SELECT COUNT(*) FROM llm_models')
   print(f'LLM 模型数: {cursor.fetchone()[0]}')
   "
   ```

2. 如果数据为 0，删除并重建数据库：
   ```bash
   docker-compose -f docker-compose.lite.yml down -v
   docker-compose -f docker-compose.lite.yml up -d
   ```

### 问题：服务间调用失败
1. 检查服务是否都在运行
2. 查看具体错误日志
3. 验证服务 URL 配置（默认本地 localhost）

---

## 📚 相关文档

- `HARDCODE_REMOVAL_COMPLETE.md` - 完整的硬编码移除说明
- `/services/web_ui/main.py` - Web UI 源代码
- `docker-compose.lite.yml` - Docker 编排配置

---

## ✨ 新增特性

### 1. DatabaseHelper 辅助类
自动从数据库读取配置，提供统一接口

### 2. 实时配置更新
无需重启应用，后台修改立即生效

### 3. 完整的调用链追踪
显示实际使用的 Prompt 和 LLM 模型

### 4. 真实服务集成
所有接口都调用真实的微服务，不再依赖 Mock

---

**状态**: ✅ 已准备就绪  
**版本**: v2.1 - 无硬编码版本  
**日期**: 2026-01-27
