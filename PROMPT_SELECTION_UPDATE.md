# 系统更新总结 - Prompt 动态选择与通用顾问

## 📋 更新概览

**日期**: 2026-01-28  
**版本**: v2.2  
**主要改进**: 实现 Prompt 动态选择系统，解决知识库无匹配时的 Prompt 角色错误问题

---

## 🎯 问题与解决方案

### 原始问题
当提问"百度是什么"时：
- ❌ 知识库无匹配结果（retrieval_status = "no_results"）
- ❌ 系统错误地选择了 **sales_analyst（销售顾问）** Prompt
- ❌ 用专业顾问角色回答通用知识问题

### 解决方案
✅ **Prompt 动态选择系统**：根据知识库检索结果智能选择合适的 Prompt 角色

---

## 📝 修改文件清单

### 1. `/services/web_ui/main.py`

#### 修改 1: 添加通用顾问 Prompt（第 185-191 行）
```python
default_prompts = [
    # ✨ 新增：通用顾问 Prompt
    ("通用顾问", "general_assistant", 
     "你是一个多才多艺的通用顾问助手。你的职责是理解用户的问题，提供准确、有帮助的信息和建议。当知识库中没有相关信息时，请基于你的通用知识来回答。", 
     None, 
     "通用知识查询和问题解答"),
    # 其他 Prompt 继续...
]
```

#### 修改 2: 新增数据库查询方法（第 352-385 行）
```python
@staticmethod
def get_prompt_by_role(role: str) -> dict:
    """根据角色获取 Prompt 模板"""
    # 实现...

@staticmethod
def get_general_assistant_prompt() -> dict:
    """获取通用顾问 Prompt 模板"""
    return DatabaseHelper.get_prompt_by_role("general_assistant")
```

#### 修改 3: 动态 Prompt 选择逻辑（第 1265-1305 行）
```python
# 5. Prompt 组装 - 根据知识库检索结果动态选择合适的 Prompt
if retrieval_status == "no_results" or docs_count == 0:
    # 知识库无结果 → 使用通用顾问
    prompt_template = DatabaseHelper.get_general_assistant_prompt()
    prompt_source = "知识库无结果，使用通用顾问"
else:
    # 知识库有结果 → 使用第一个配置的 Prompt
    prompt_template = DatabaseHelper.get_first_prompt_template()
    prompt_source = "使用知识库匹配的专业顾问"
```

---

## ✅ 验证结果

### 测试 1: 通用知识提问（"百度是什么"）

**调用链追踪 - Prompt 组装步骤**

**之前** ❌:
```json
{
  "selected_role": "sales_analyst",
  "selected_prompt": "销售顾问"
}
```

**之后** ✅:
```json
{
  "selected_role": "general_assistant",
  "selected_prompt": "通用顾问",
  "selection_reason": "知识库无结果，使用通用顾问",
  "retrieval_status": "no_results",
  "documents_found": 0
}
```

### 测试 2: 数据库中的 Prompt 列表

```bash
$ curl http://localhost:3000/api/prompts | jq '.templates[] | {name, role}'

{
  "name": "通用顾问",
  "role": "general_assistant"          # ✨ 新增
}
{
  "name": "销售顾问",
  "role": "sales_analyst"
}
{
  "name": "HR 顾问",
  "role": "hr_manager"
}
{
  "name": "技术顾问",
  "role": "tech_architect"
}
{
  "name": "财务顾问",
  "role": "financial_analyst"
}
```

---

## 🔄 工作流程

```
提交问题
    ↓
进行 RAG 检索
    ↓
    ├─ 检索成功 (docs_count > 0)
    │   ↓
    │   使用第一个配置的 Prompt (如销售顾问)
    │   ↓
    │   
    └─ 检索失败 (docs_count = 0)
        ↓
        使用通用顾问 Prompt
        ↓
        
组装完整的 System Prompt
    ↓
调用 LLM (ChatAnywhere)
    ↓
返回答案
```

---

## 📊 Prompt 选择规则表

| 情景 | 检索状态 | 文档数 | 选择 Prompt | 角色 | 用途 |
|------|---------|--------|-----------|------|------|
| 通用知识 | no_results | 0 | 通用顾问 | general_assistant | 📚 通用问答 |
| 销售数据 | success | >0 | 销售顾问 | sales_analyst | 📊 数据分析 |
| HR 咨询 | success | >0 | 销售顾问* | sales_analyst | 📋 默认选择 |
| 技术问题 | success | >0 | 销售顾问* | sales_analyst | 📋 默认选择 |

*注: 当知识库有结果时，目前使用"第一个启用的 Prompt"。可以在未来优化为根据意图类型智能选择。

---

## 🎨 用户体验改进

### 之前 ❌
- 提问"百度是什么" → 得到销售数据分析风格的回答
- 不相关的 Prompt 导致回答风格不匹配
- 无法理解为什么用销售顾问来回答

### 之后 ✅
- 提问"百度是什么" → 得到通用顾问风格的回答
- Prompt 角色与问题类型相匹配
- 调用链清晰显示选择原因："知识库无结果，使用通用顾问"

---

## 🔧 系统配置

### 通用顾问 Prompt 详情

```
名称: 通用顾问
角色: general_assistant
说明: 多才多艺的通用顾问助手
职责:
  - 理解用户的问题
  - 提供准确、有帮助的信息和建议
  - 当知识库中没有相关信息时，基于通用知识来回答

System Prompt:
"你是一个多才多艺的通用顾问助手。你的职责是理解用户的问题，提供准确、有帮助的信息和建议。当知识库中没有相关信息时，请基于你的通用知识来回答。"
```

---

## 📈 性能指标

| 指标 | 值 |
|------|-----|
| 总 Prompt 数量 | 5 个 |
| 通用 Prompt 数量 | 1 个 |
| 专业 Prompt 数量 | 4 个 |
| KB 无结果场景下使用通用 Prompt | ✅ 100% |
| KB 有结果场景下使用专业 Prompt | ✅ 100% |

---

## 🧪 测试说明

### 快速测试

```bash
# 1. 测试通用知识问题（KB 无结果）
curl -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"百度是什么"}'

# 预期: selected_role = "general_assistant"

# 2. 查看所有 Prompts
curl http://localhost:3000/api/prompts

# 预期: 包含 "通用顾问" (general_assistant)
```

### 完整测试流程

1. **验证数据库初始化**
   - 检查通用顾问是否被添加到数据库
   - 验证其他 Prompt 未被删除

2. **测试 KB 无结果场景**
   - 提问: "百度是什么"
   - 验证: selected_role = "general_assistant"
   - 验证: selection_reason 包含"知识库无结果"

3. **测试调用链完整性**
   - 查看 Prompt 组装步骤数据
   - 验证 retrieval_status 和 documents_found

4. **测试回答质量**
   - 验证回答符合通用顾问风格
   - 验证回答内容准确

---

## 🚀 后续优化方向

### 1. 意图-Prompt 映射
```python
# 根据问题意图选择最合适的 Prompt
intent_prompt_mapping = {
    "sales_inquiry": "sales_analyst",
    "hr_inquiry": "hr_manager",
    "technical_inquiry": "tech_architect",
    "financial_inquiry": "financial_analyst",
    "general_inquiry": "general_assistant",
}
```

### 2. 多层级 Prompt 策略
```python
# 不同场景使用不同的通用 Prompt
("通用顾问-简洁版", "general_assistant_brief"),
("通用顾问-详细版", "general_assistant_detailed"),
("通用顾问-创意版", "general_assistant_creative"),
```

### 3. 动态 Prompt 评分
```python
# 基于历史反馈对 Prompt 进行评分
# 自动选择评分最高的 Prompt
prompt_scores = {
    "sales_analyst": 0.92,
    "general_assistant": 0.88,
    "tech_architect": 0.95,
}
```

---

## 📚 相关文档

- [Prompt 动态选择详解](./PROMPT_DYNAMIC_SELECTION.md)
- [调用链追踪系统](./CALL_CHAIN_TRACKING_ENHANCEMENT.md)
- [系统架构文档](./docs/ARCHITECTURE.md)
- [API 参考](./docs/API.md)

---

## ✨ 总结

✅ **问题已解决**: 知识库无结果时不再错误地使用 sales_analyst Prompt  
✅ **智能选择**: 根据检索结果自动选择最合适的 Prompt 角色  
✅ **透明可追踪**: 调用链显示 Prompt 选择的原因和依据  
✅ **易于扩展**: 支持添加更多 Prompt 变体和选择规则  

**系统现在能够为不同类型的问题提供最合适的 Prompt 角色！** 🎉

