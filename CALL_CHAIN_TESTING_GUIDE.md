# 调用链追踪系统 - 快速测试指南

## 🚀 快速开始

### 测试 1: 通过 API 查看完整的调用链数据

```bash
# 提交问题并获取完整的调用链信息
curl -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","question":"什么是人工智能?"}'
```

**预期结果:**
```json
{
  "question": "什么是人工智能?",
  "answer": "...",
  "trace": {
    "trace_id": "xxxxxxxx",
    "total_steps": 11,
    "total_time": "~5.0s",
    "steps": [
      { "seq": 1, "stage": "输入处理", "service": "QA Entry Service (端口 8001)", ... },
      { "seq": 2, "stage": "意图识别", "service": "QA Entry Service (端口 8001)", ... },
      { "seq": 3, "stage": "知识检索-向量化", "service": "RAG Service (端口 8003)", ... },
      { "seq": 4, "stage": "知识检索-向量搜索", "service": "RAG Service (端口 8003)", ... },
      { "seq": 5, "stage": "上下文增强-数据查询", "service": "Integration Service (端口 8005)", ... },
      { "seq": 6, "stage": "上下文增强-权限校验", "service": "Integration Service (端口 8005)", ... },
      { "seq": 7, "stage": "Prompt 组装", "service": "Prompt Service (端口 8002)", ... },
      { "seq": 8, "stage": "LLM 推理-模型选择", "service": "LLM Service (端口 8006)", ... },
      { "seq": 9, "stage": "LLM 推理-API 调用", "service": "LLM Service (端口 8006)", ... },
      { "seq": 10, "stage": "结果处理-格式化", "service": "QA Entry Service (端口 8001)", ... },
      { "seq": 11, "stage": "响应返回", "service": "Web UI Service (端口 3000)", ... }
    ]
  }
}
```

---

### 测试 2: 使用 jq 提取关键信息

```bash
# 查看追踪摘要信息
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"百度是什么"}' | \
  jq '.trace | {trace_id, total_steps, total_time, steps_count: (.steps | length)}'

# 输出:
# {
#   "trace_id": "6b7a3060",
#   "total_steps": 11,
#   "total_time": "5.098s",
#   "steps_count": 11
# }
```

---

### 测试 3: 查看特定步骤的详细数据

```bash
# 查看第 4 步（向量搜索）的真实结果
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"百度是什么"}' | \
  jq '.trace.steps[3]'

# 输出:
# {
#   "seq": 4,
#   "stage": "知识检索-向量搜索",
#   "service": "RAG Service (端口 8003) - FAISS轻量级向量库",
#   "data": {
#     "found_documents": 0,              ← 真实的检索结果
#     "retrieval_status": "no_results",
#     "search_query": "百度是什么"
#   }
# }
```

---

### 测试 4: 查看 LLM 模型选择

```bash
# 查看第 8 步（LLM 模型选择）
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"什么是云计算?"}' | \
  jq '.trace.steps[7]'

# 输出:
# {
#   "seq": 8,
#   "stage": "LLM 推理-模型选择",
#   "service": "LLM Service (端口 8006)",
#   "data": {
#     "selected_model": "ChatAnywhere GPT-3.5-turbo",    ← 真实的模型
#     "provider": "chatanywhere",
#     "api_url": "https://api.chatanywhere.com.cn/v1/chat/completions",
#     "temperature": 0.7,
#     "max_tokens": 2048,
#     "reason": "使用用户配置的默认模型"
#   }
# }
```

---

### 测试 5: 查看 Prompt 配置

```bash
# 查看第 7 步（Prompt 组装）
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"销售数据如何"}' | \
  jq '.trace.steps[6]'

# 输出:
# {
#   "seq": 7,
#   "stage": "Prompt 组装",
#   "service": "Prompt Service (端口 8002)",
#   "data": {
#     "selected_role": "sales_analyst",           ← 真实的 Prompt 角色
#     "selected_prompt": "销售顾问",
#     "template_version": "v2.1",
#     "system_prompt_length": 39
#   }
# }
```

---

### 测试 6: 统计调用链状态

```bash
# 统计成功、警告、错误的步骤数
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"test"}' | \
  jq '.trace.steps | group_by(.status) | map({status: .[0].status, count: length})'

# 输出:
# [
#   {"status": "success", "count": 10},
#   {"status": "warning", "count": 1}
# ]
```

---

### 测试 7: 使用 Web UI 查看调用链

1. **打开浏览器** → http://localhost:3000

2. **提交问题:**
   - 在输入框输入问题，例如："什么是区块链?"
   - 勾选"显示调用链"复选框
   - 点击"提问"按钮

3. **查看调用链展示:**
   - 📊 顶部：追踪 ID、总步骤、总耗时
   - 🔄 中部：完整的 11 步服务调用表格
   - 📈 底部：统计信息（成功/警告/错误/服务数）

4. **查看详细参数:**
   - 每步下方显示该步骤的所有参数
   - 彩色编码显示参数类型
   - 支持长文本自动截断

---

## 📊 关键验证点

### ✅ 验证真实数据流

#### 1. RAG 检索结果验证

```bash
# 检查文档检索是否返回真实数据
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"公司财务报表"}' | \
  jq '.trace.steps[3].data'

# 应该显示:
# {
#   "found_documents": N,  # 真实的文档数量
#   "retrieval_status": "success" | "no_results",
#   "documents": [...]      # 真实的文档列表
# }
```

#### 2. LLM 模型验证

```bash
# 确认使用的是 ChatAnywhere
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"test"}' | \
  jq '.trace.steps[7:9]' | \
  grep -E '"provider"|"api_url"|"selected_model"'

# 应该显示:
# "selected_model": "ChatAnywhere GPT-3.5-turbo"
# "provider": "chatanywhere"
# "api_url": "https://api.chatanywhere.com.cn/v1/chat/completions"
```

#### 3. Prompt 配置验证

```bash
# 检查是否读取了数据库中的 Prompt 配置
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"test"}' | \
  jq '.trace.steps[6].data'

# 应该显示数据库中配置的 Prompt（不是硬编码值）
```

---

## 🎯 调用链完整性检查清单

运行以下命令进行完整检查：

```bash
#!/bin/bash

echo "🔍 调用链完整性检查"
echo "=================="

RESPONSE=$(curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"测试问题"}')

echo "✅ 步骤 1: 检查追踪 ID"
echo $RESPONSE | jq '.trace.trace_id'

echo "✅ 步骤 2: 检查总步骤数 (应该是 11)"
echo $RESPONSE | jq '.trace.total_steps'

echo "✅ 步骤 3: 检查服务数量 (应该是 6 个)"
SERVICES=$(echo $RESPONSE | jq '[.trace.steps[].service | split("(")[0]] | unique | length')
echo "服务数: $SERVICES"

echo "✅ 步骤 4: 检查 RAG 搜索结果 (真实的文档数)"
echo $RESPONSE | jq '.trace.steps[3].data.found_documents'

echo "✅ 步骤 5: 检查 LLM 模型 (应该是 ChatAnywhere)"
echo $RESPONSE | jq '.trace.steps[7].data.selected_model'

echo "✅ 步骤 6: 检查 Prompt 配置 (应该是数据库值)"
echo $RESPONSE | jq '.trace.steps[6].data.selected_role'

echo "✅ 步骤 7: 检查执行时间"
echo $RESPONSE | jq '.trace.total_time'

echo "✅ 完整性检查完成！"
```

---

## 🐛 故障排查

### 问题 1: 调用链数据为空

```bash
# 原因: 可能是 Web UI 服务未正确启动
# 解决: 
docker-compose -f docker-compose.lite.yml logs web_ui
```

### 问题 2: LLM 模型显示为"默认模型"

```bash
# 原因: 数据库中没有配置 LLM 模型
# 解决:
# 检查数据库初始化是否包含 ChatAnywhere 模型
curl http://localhost:3000/api/llm/models/list
```

### 问题 3: RAG 显示"connection_error"

```bash
# 原因: RAG Service 未运行或无法连接
# 解决:
docker-compose -f docker-compose.lite.yml logs rag_service
curl http://localhost:8003/health
```

### 问题 4: Prompt 显示为"默认模板"

```bash
# 原因: 数据库中没有配置 Prompt
# 解决:
# 检查 Prompts 表是否有数据
curl http://localhost:3000/api/prompts
```

---

## 📈 性能基准

```
平均响应时间: ~5.0 秒
  - QA Entry 处理: ~0.1s
  - RAG 搜索: ~0.2s
  - Integration 查询: ~0.1s
  - Prompt 处理: ~0.1s
  - LLM 推理: ~4.0s ← 主要耗时
  - 结果格式化: ~0.2s

调用链数据大小: ~2-3KB
前端渲染时间: <100ms
服务调用总数: 6 个
```

---

## 📚 相关文档

- [完整的调用链追踪升级文档](./CALL_CHAIN_TRACKING_ENHANCEMENT.md)
- [系统架构文档](./docs/ARCHITECTURE.md)
- [API 参考](./docs/API.md)

---

## 💡 提示

### 快速查看调用链摘要

```bash
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"your question"}' | \
  jq '{
    trace_id: .trace.trace_id,
    total_steps: .trace.total_steps,
    total_time: .trace.total_time,
    success: ([.trace.steps[] | select(.status=="success")] | length),
    warnings: ([.trace.steps[] | select(.status=="warning")] | length),
    errors: ([.trace.steps[] | select(.status=="error")] | length)
  }'
```

### 导出调用链为 JSON 文件

```bash
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"your question"}' | \
  jq '.trace' > call_chain_$(date +%s).json
```

---

**测试完成！系统现在提供完整的调用链可观测性！** 🎉

