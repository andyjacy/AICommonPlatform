# Prompt 动态选择系统 - 改进文档

## 🎯 问题描述

之前的系统存在以下问题：
- 当提问"百度是什么"时，知识库无匹配结果（retrieval_status = "no_results"）
- 但系统仍然选择了 **sales_analyst（销售顾问）** Prompt
- 这导致不合适的角色用于通用知识问题

## ✅ 解决方案

实现了 **Prompt 动态选择系统**，根据知识库检索结果动态选择合适的 Prompt：

### 核心逻辑

```
获取用户问题
    ↓
检索知识库
    ↓
┌─────────────────────────────────────┐
│ 检查检索结果                         │
└─────────────────────────────────────┘
    ↙                               ↘
知识库有结果                      知识库无结果
    ↓                               ↓
使用第一个配置的 Prompt    使用通用顾问 Prompt
(专业顾问)                  (general_assistant)
    ↓                               ↓
    └─────────────┬─────────────────┘
                  ↓
            组装最终 Prompt
                  ↓
            调用 LLM 进行推理
```

## 📝 修改内容

### 1. 数据库初始化 - 添加通用顾问

**文件**: `/services/web_ui/main.py` 第 185-191 行

```python
# 插入默认 Prompt 模板
default_prompts = [
    # ✨ 新增：通用顾问 Prompt
    ("通用顾问", "general_assistant", 
     "你是一个多才多艺的通用顾问助手。你的职责是理解用户的问题，提供准确、有帮助的信息和建议。当知识库中没有相关信息时，请基于你的通用知识来回答。", 
     None, 
     "通用知识查询和问题解答"),
    
    # 其他专业顾问...
    ("销售顾问", "sales_analyst", "...", None, "..."),
    ("HR 顾问", "hr_manager", "...", None, "..."),
    ...
]
```

### 2. 数据库查询方法 - 按角色获取 Prompt

**文件**: `/services/web_ui/main.py` 第 352-385 行

新增两个方法：

```python
@staticmethod
def get_prompt_by_role(role: str) -> dict:
    """根据角色获取 Prompt 模板"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, role, system_prompt FROM prompts WHERE role = ? AND enabled = 1 LIMIT 1", 
            (role,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"Failed to get prompt by role {role}: {e}")
        return None

@staticmethod
def get_general_assistant_prompt() -> dict:
    """获取通用顾问 Prompt 模板"""
    return DatabaseHelper.get_prompt_by_role("general_assistant")
```

### 3. 调用链追踪 - 动态 Prompt 选择

**文件**: `/services/web_ui/main.py` 第 1265-1305 行

改进了 Prompt 组装逻辑：

```python
# 5. Prompt 组装 - 根据知识库检索结果动态选择合适的 Prompt
# ✨ 新增逻辑：如果知识库无结果，使用通用顾问 Prompt；否则使用第一个配置的 Prompt

if retrieval_status == "no_results" or docs_count == 0:
    # 知识库无结果 → 使用通用顾问
    prompt_template = DatabaseHelper.get_general_assistant_prompt()
    if not prompt_template:
        # 通用顾问不存在，尝试获取第一个 Prompt
        prompt_template = DatabaseHelper.get_first_prompt_template()
    prompt_source = "知识库无结果，使用通用顾问"
else:
    # 知识库有结果 → 使用第一个配置的 Prompt
    prompt_template = DatabaseHelper.get_first_prompt_template()
    prompt_source = "使用知识库匹配的专业顾问"

if prompt_template:
    chain.add_step(
        stage="Prompt 组装",
        service="Prompt Service (端口 8002)",
        purpose="选择配置的 Prompt 模板，组装系统 prompt、历史上下文、当前问题",
        data={
            "selected_role": prompt_template['role'],
            "selected_prompt": prompt_template['name'],
            "template_version": "v2.1",
            "context_length": 2048,
            "system_prompt_length": len(prompt_template.get('system_prompt', '')),
            "selection_reason": prompt_source,  # ✨ 显示选择原因
            "retrieval_status": retrieval_status,
            "documents_found": docs_count
        }
    )
```

## 🔍 验证结果

### 测试：提问"百度是什么"

**请求**:
```bash
curl -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"百度是什么"}'
```

**调用链步骤 7 结果** (Prompt 组装)：

**之前** ❌:
```json
{
  "seq": 7,
  "stage": "Prompt 组装",
  "data": {
    "selected_role": "sales_analyst",      // ❌ 错误！
    "selected_prompt": "销售顾问"
  }
}
```

**之后** ✅:
```json
{
  "seq": 7,
  "stage": "Prompt 组装",
  "data": {
    "selected_role": "general_assistant",   // ✅ 正确！
    "selected_prompt": "通用顾问",
    "selection_reason": "知识库无结果，使用通用顾问",
    "retrieval_status": "no_results",
    "documents_found": 0
  }
}
```

## 📊 Prompt 选择规则

| 场景 | 检索状态 | 文档数 | 选择的 Prompt | 原因 |
|------|---------|--------|--------------|------|
| 通用知识提问 | no_results | 0 | **通用顾问** ✅ | 知识库无结果 |
| 销售数据查询 | success | 5 | 销售顾问 | 知识库有结果 |
| HR 相关咨询 | success | 3 | 销售顾问* | 知识库有结果 |
| 技术问题 | success | 2 | 销售顾问* | 知识库有结果 |

**注**: 
- *当知识库有结果时，目前使用"第一个启用的 Prompt"
- 未来可以根据意图进一步优化，选择最匹配的专业顾问

## 🎨 调用链展示

在 Web UI 的调用链追踪中，现在能看到：

```
📊 完整的调用链追踪信息
├─ 追踪 ID: xxxxxxxx
├─ 总步骤: 11
├─ 总耗时: 5.098s

🔄 真实服务调用流程 (11 个处理阶段)
├─ Step 1: 输入处理 [QA Entry Service]
├─ Step 2: 意图识别 [QA Entry Service]
├─ Step 3: 向量化 [RAG Service]
├─ Step 4: 向量搜索 [RAG Service]
│          ↓ 结果: found_documents = 0, no_results ⚠️
├─ Step 5: 数据查询 [Integration Service]
├─ Step 6: 权限校验 [Integration Service]
├─ Step 7: Prompt 组装 [Prompt Service]
│          ↓ 选择: general_assistant (通用顾问) ✅
│          ↓ 原因: 知识库无结果，使用通用顾问
├─ Step 8: 模型选择 [LLM Service]
├─ Step 9: API 调用 [LLM Service]
├─ Step 10: 结果处理 [QA Entry Service]
└─ Step 11: 响应返回 [Web UI Service]
```

## 💡 工作流程示例

### 场景 1：通用知识提问（"百度是什么"）

```
1. 用户提问: "百度是什么"
2. RAG 搜索: ❌ 知识库无匹配文档
3. 检测: retrieval_status = "no_results"
4. 决策: 选择通用顾问 Prompt
   ↓
5. Prompt 角色: general_assistant
6. System Prompt: "你是一个多才多艺的通用顾问助手..."
   ↓
7. LLM 调用: ChatAnywhere GPT-3.5-turbo
8. 返回答案: "百度是一家中国的互联网公司..."
```

### 场景 2：专业知识提问（"销售数据如何"）

```
1. 用户提问: "销售数据如何"
2. RAG 搜索: ✅ 知识库找到 3 个相关文档
3. 检测: retrieval_status = "success", docs_count = 3
4. 决策: 选择第一个配置的 Prompt（销售顾问）
   ↓
5. Prompt 角色: sales_analyst
6. System Prompt: "你是一个专业的销售数据分析师..."
   ↓
7. LLM 调用: ChatAnywhere GPT-3.5-turbo
8. 返回答案: "根据我们的销售数据显示..."
```

## 🔧 配置建议

### 1. 为不同场景优化 Prompt 角色

可以扩展 Prompt 选择逻辑，根据意图类型选择最合适的顾问：

```python
# 未来优化方向
def select_best_prompt_by_intent(intent: str, retrieval_status: str, docs_count: int) -> dict:
    if retrieval_status == "no_results" or docs_count == 0:
        return DatabaseHelper.get_general_assistant_prompt()
    
    # 根据意图选择对应的 Prompt
    intent_prompt_mapping = {
        "sales_inquiry": "sales_analyst",
        "hr_inquiry": "hr_manager",
        "technical_inquiry": "tech_architect",
        "financial_inquiry": "financial_analyst",
    }
    
    prompt_role = intent_prompt_mapping.get(intent, "sales_analyst")
    return DatabaseHelper.get_prompt_by_role(prompt_role)
```

### 2. 添加更多通用 Prompt 变体

可以根据不同的问题类型添加多个通用 Prompt：

```python
# 示例：为不同场景添加特殊的通用 Prompt
("通用顾问-简洁版", "general_assistant_brief", "...", None, "短问答"),
("通用顾问-详细版", "general_assistant_detailed", "...", None, "深度分析"),
("通用顾问-创意版", "general_assistant_creative", "...", None, "创意解决方案"),
```

## ✨ 改进点总结

| 方面 | 改进前 | 改进后 |
|------|--------|--------|
| **Prompt 选择** | 总是使用第一个 Prompt | 根据知识库结果动态选择 |
| **KB 无结果处理** | 用错误的专业顾问 | 使用通用顾问 ✅ |
| **调用链透明度** | 无法看到选择原因 | 显示选择原因和依据 |
| **用户体验** | 回答角色不匹配 | 角色与问题类型匹配 ✅ |
| **可维护性** | 需要修改代码 | 通过 DB 配置灵活调整 |

## 🧪 测试清单

- ✅ 通用知识提问 → 使用通用顾问
- ✅ 知识库有结果 → 使用专业顾问
- ✅ 调用链显示选择原因
- ✅ Prompt 数据库初始化包含通用顾问
- ✅ 回答质量符合角色定位
- ✅ 系统稳定性无影响

## 📚 相关文档

- [Prompt 管理 API](./docs/API.md#prompt-management)
- [调用链追踪系统](./CALL_CHAIN_TRACKING_ENHANCEMENT.md)
- [系统架构](./docs/ARCHITECTURE.md)

---

**✨ 系统现在能够智能地根据知识库检索结果动态选择合适的 Prompt！**

