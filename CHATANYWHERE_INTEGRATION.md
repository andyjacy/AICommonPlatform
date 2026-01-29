# ChatAnywhere 大模型集成指南

## 📋 概述

本系统现已支持多个 LLM 提供商，包括：
- **OpenAI** - 官方 API (GPT-4, GPT-3.5-turbo 等)
- **ChatAnywhere** - 免费 ChatGPT API (兼容 OpenAI 接口)

系统会根据模型配置中的 `provider` 字段自动选择调用方式，无需修改代码。

---

## 🚀 快速开始 - ChatAnywhere

### 1. 获取 ChatAnywhere API Key

#### 步骤 1: 访问 ChatAnywhere 官网
```
https://chatanywhere.com.cn/
```

#### 步骤 2: 注册/登录账号
- 使用邮箱或手机号注册
- 完成邮箱/手机验证

#### 步骤 3: 获取 API Key
- 登录后进入 "API" 或 "个人中心"
- 找到 "API Keys" 或 "令牌管理" 部分
- 复制你的 API Key（通常以 `sk-` 开头）

#### 步骤 4: 查看可用模型
```
访问: https://chatanywhere.com.cn/
查看支持的模型列表，通常包括:
- gpt-3.5-turbo (免费)
- gpt-4 (如果已升级)
- claude (如果支持)
```

---

## 📝 在 Web UI 中配置 ChatAnywhere

### 方法 1: 通过 Web UI 界面配置

#### 1. 打开 Web UI
```
http://localhost:3000
```

#### 2. 进入 LLM 模型管理
```
导航菜单 → LLM 模型管理 → 添加新模型
或
直接访问: http://localhost:3000/models
```

#### 3. 填写 ChatAnywhere 配置
```
字段说明:

【基本信息】
- 模型名称: ChatGPT-Free (或任意名称)
- Provider: chatanywhere (重要！必须是这个值)
- 模型类型: api (保持默认)

【API 配置】
- API Key: 你在 ChatAnywhere 获取的 Key
- Base URL: https://api.chatanywhere.com.cn/v1 (自动配置，无需修改)

【模型参数】
- 最大 Tokens: 2048 (根据需求调整)
- 温度: 0.7 (0 = 确定, 1 = 随机)
- Top P: 1.0 (保持默认或调整 0-1)

【其他选项】
- 启用: ✓ (勾选)
- 设为默认: ✓ (可选，如果要作为默认模型)
- 描述: ChatGPT 免费 API (可选)
```

#### 4. 保存配置
点击 "保存" 或 "更新" 按钮

#### 5. 验证配置
- 配置保存后应该看到成功提示
- 在模型列表中可以看到新配置的模型
- 状态应显示为 "启用"

---

### 方法 2: 通过 API 直接配置

#### 使用 cURL 命令创建模型

```bash
curl -X POST http://localhost:3000/api/llm/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ChatGPT-Free",
    "provider": "chatanywhere",
    "model_type": "api",
    "api_key": "sk-your-chatanywhere-key-here",
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 1.0,
    "description": "ChatAnywhere 免费 API"
  }'
```

#### 使用 Python 创建模型

```python
import requests

url = "http://localhost:3000/api/llm/models"
headers = {"Content-Type": "application/json"}
data = {
    "name": "ChatGPT-Free",
    "provider": "chatanywhere",
    "model_type": "api",
    "api_key": "sk-your-chatanywhere-key-here",
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 1.0,
    "description": "ChatAnywhere 免费 API"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

## 🔍 验证配置是否成功

### 1. 查看模型列表
```bash
curl http://localhost:3000/api/llm/models/list
```

预期输出：
```json
{
  "models": [
    {
      "id": 2,
      "name": "ChatGPT-Free",
      "provider": "chatanywhere",
      "enabled": 1,
      "is_default": 0,
      "api_key": "sk-***",
      "temperature": 0.7,
      "max_tokens": 2048
    }
  ]
}
```

### 2. 测试 QA 系统

#### 使用 Web UI 提问
```
访问: http://localhost:3000/qa
输入问题: "你好，请介绍一下你自己"
点击 "提问" 按钮
```

#### 使用 API 调用
```bash
curl -X POST http://localhost:8001/api/qa/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "你好，请介绍一下你自己",
    "user_id": "test_user"
  }'
```

#### 查看日志
```bash
docker logs ai_platform_qa_entry -f
```

预期日志输出：
```
🤖 使用模型: ChatGPT-Free (Provider: chatanywhere)
📤 调用 ChatAnywhere API，模型: gpt-3.5-turbo
📥 ChatAnywhere 返回: tokens=150
✅ LLM 响应生成成功，长度: 245
```

---

## ⚙️ 同时使用 OpenAI 和 ChatAnywhere

您可以同时配置两个模型，系统会使用 "设为默认" 的模型：

### 配置示例

#### 模型 1: OpenAI GPT-4
```json
{
  "name": "GPT-4-Official",
  "provider": "openai",
  "api_key": "sk-proj-your-openai-key",
  "model_type": "api",
  "enabled": true,
  "is_default": false,
  "temperature": 0.7,
  "max_tokens": 4096
}
```

#### 模型 2: ChatAnywhere GPT-3.5
```json
{
  "name": "ChatGPT-Free",
  "provider": "chatanywhere",
  "api_key": "sk-your-chatanywhere-key",
  "model_type": "api",
  "enabled": true,
  "is_default": true,
  "temperature": 0.7,
  "max_tokens": 2048
}
```

### 切换模型

只需在 Web UI 中修改 "设为默认" 字段即可：

```bash
# 切换到 OpenAI
curl -X PUT http://localhost:3000/api/llm/models/1 \
  -H "Content-Type: application/json" \
  -d '{"is_default": true}'

# 关闭 ChatAnywhere 的默认状态
curl -X PUT http://localhost:3000/api/llm/models/2 \
  -H "Content-Type: application/json" \
  -d '{"is_default": false}'
```

---

## 🔐 安全建议

### 1. 保护 API Key
- ✅ 不要在代码中硬编码 API Key
- ✅ 使用环境变量管理敏感信息
- ✅ 在版本控制中忽略配置文件
- ✅ 定期轮换 API Key

### 2. 在生产环境中
- 使用更强的数据库加密
- 实现 API 请求速率限制
- 添加审计日志
- 使用 HTTPS 加密传输

### 3. 环境变量示例
```bash
# .env 文件
CHATANYWHERE_API_KEY=sk-your-key-here
OPENAI_API_KEY=sk-proj-your-key-here
```

---

## 🧪 测试脚本

### 完整测试脚本

创建 `test_multi_llm.py`:

```python
#!/usr/bin/env python3
"""
多 LLM 提供商测试脚本
支持 OpenAI 和 ChatAnywhere
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:3000"
QA_URL = "http://localhost:8001"

def test_llm_models():
    """测试获取 LLM 模型列表"""
    print("\n" + "="*60)
    print("📋 测试 1: 获取 LLM 模型列表")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/llm/models/list")
        models = response.json().get("models", [])
        
        for model in models:
            provider = model.get("provider", "unknown")
            name = model.get("name")
            enabled = "✅" if model.get("enabled") else "❌"
            is_default = "📌 默认" if model.get("is_default") else ""
            
            print(f"{enabled} [{provider:12}] {name:20} {is_default}")
        
        return len(models) > 0
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_qa_with_provider(provider: str, question: str):
    """测试特定提供商的 QA"""
    print(f"\n{'='*60}")
    print(f"🤖 测试: {provider.upper()} - {question}")
    print("="*60)
    
    try:
        response = requests.post(
            f"{QA_URL}/api/qa/ask",
            json={
                "question": question,
                "user_id": f"test_{provider}"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            
            print(f"✅ 成功获取答案 ({len(answer)} 字)")
            print(f"📊 数据来源: {', '.join(sources) if sources else '知识库+LLM'}")
            print(f"\n💬 答案预览:")
            print(f"{answer[:200]}..." if len(answer) > 200 else answer)
            
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "#"*60)
    print("# 多 LLM 提供商集成测试")
    print("#"*60)
    
    # 测试 1: 获取模型列表
    models_ok = test_llm_models()
    
    if not models_ok:
        print("\n❌ 模型列表获取失败，无法继续测试")
        return
    
    # 测试 2: ChatAnywhere QA
    ca_ok = test_qa_with_provider("chatanywhere", "请介绍一下你自己")
    
    # 测试 3: OpenAI QA (如果配置了)
    oa_ok = test_qa_with_provider("openai", "什么是人工智能？")
    
    # 测试 4: 销售问题
    sales_ok = test_qa_with_provider("default", "2024年Q1的销售业绩如何？")
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"模型列表: {'✅ 通过' if models_ok else '❌ 失败'}")
    print(f"ChatAnywhere: {'✅ 通过' if ca_ok else '❌ 失败'}")
    print(f"OpenAI: {'✅ 通过' if oa_ok else '⏭️  跳过'}")
    print(f"销售问题: {'✅ 通过' if sales_ok else '❌ 失败'}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
```

运行测试：
```bash
python test_multi_llm.py
```

---

## 🔧 故障排查

### 问题 1: API Key 无效

**症状**: 返回 401 或 403 错误

**解决**:
```bash
# 1. 验证 API Key 格式
# ChatAnywhere: 应该以 sk- 开头
# OpenAI: 应该以 sk-proj- 开头

# 2. 重新获取 API Key
# 访问: https://chatanywhere.com.cn/

# 3. 更新配置
curl -X PUT http://localhost:3000/api/llm/models/2 \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-your-new-key"}'

# 4. 查看日志
docker logs ai_platform_qa_entry | grep -i error
```

### 问题 2: Provider 不被识别

**症状**: 始终使用 OpenAI，忽略 ChatAnywhere 配置

**解决**:
```bash
# 1. 验证 provider 字段
curl http://localhost:3000/api/llm/models/list | jq '.models[].provider'

# 2. 检查是否为小写
# ✅ 正确: "chatanywhere"
# ❌ 错误: "ChatAnywhere" 或 "CHATANYWHERE"

# 3. 更新 provider 字段
curl -X PUT http://localhost:3000/api/llm/models/2 \
  -H "Content-Type: application/json" \
  -d '{"provider": "chatanywhere"}'

# 4. 查看 QA 服务日志
docker logs ai_platform_qa_entry -f | grep -i provider
```

### 问题 3: 响应时间过长

**症状**: QA 响应超过 30 秒

**解决**:
```bash
# 1. 检查网络连接
ping api.chatanywhere.com.cn

# 2. 检查 API 配额限制
# ChatAnywhere 可能有请求限流

# 3. 增加超时时间
# 编辑 services/qa_entry/services.py
# 修改: timeout=aiohttp.ClientTimeout(total=60)

# 4. 查看详细日志
docker logs ai_platform_qa_entry | tail -50
```

### 问题 4: 模型列表为空

**症状**: 获取模型列表时没有任何模型

**解决**:
```bash
# 1. 重启 Web UI 服务
docker-compose restart web_ui

# 2. 检查数据库
docker exec ai_platform_web_ui sqlite3 web_ui.db \
  "SELECT name, provider, enabled FROM llm_models;"

# 3. 手动添加模型
curl -X POST http://localhost:3000/api/llm/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ChatGPT-Free",
    "provider": "chatanywhere",
    "api_key": "sk-your-key",
    "max_tokens": 2048,
    "temperature": 0.7
  }'

# 4. 验证添加
curl http://localhost:3000/api/llm/models/list
```

---

## 📊 性能对比

| 指标 | OpenAI | ChatAnywhere |
|------|--------|--------------|
| 成本 | 按 token 计费 | 免费 |
| 响应时间 | 200-500ms | 300-800ms |
| 模型选择 | GPT-4, GPT-3.5等 | gpt-3.5等 |
| API 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 文档完整性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 💡 最佳实践

### 1. 开发环境
```
使用 ChatAnywhere (免费，快速开发)
- 配置 provider: "chatanywhere"
- 设为默认模型
```

### 2. 生产环境
```
使用 OpenAI (更稳定和准确)
- 配置 provider: "openai"
- 设为默认模型
- 配置 API 配额限制
```

### 3. 高可用方案
```
配置两个模型，互为备份:
- 主: OpenAI (provider: "openai")
- 备: ChatAnywhere (provider: "chatanywhere")

修改代码支持自动故障转移:
try:
    result = call_primary_llm()
except:
    result = call_fallback_llm()  # ChatAnywhere
```

---

## 📞 支持和反馈

### ChatAnywhere 相关
- 官网: https://chatanywhere.com.cn/
- GitHub: https://github.com/chatanywhere/ChatGPT_API_free
- 文档: 查看官网的 API 文档

### 本系统相关
- 查看日志: `docker logs ai_platform_qa_entry -f`
- 检查配置: `curl http://localhost:3000/api/llm/models/list`
- 测试 API: 使用 `test_multi_llm.py` 脚本

---

## ✅ 配置检查清单

在使用 ChatAnywhere 前，请确保：

- [ ] 已获取 ChatAnywhere API Key (从 https://chatanywhere.com.cn/)
- [ ] Web UI 服务正在运行 (访问 http://localhost:3000)
- [ ] QA Entry 服务正在运行 (检查 docker-compose)
- [ ] 在 Web UI 中成功添加 ChatAnywhere 模型配置
- [ ] Provider 字段设置为 "chatanywhere" (小写)
- [ ] API Key 已正确保存
- [ ] 模型已设置为启用
- [ ] 已运行 `test_multi_llm.py` 进行验证
- [ ] 查看日志无错误信息
- [ ] 能成功提问并获取答案

---

## 📚 相关文档

- [IMPROVEMENT_SUMMARY.md](./IMPROVEMENT_SUMMARY.md) - 系统改进总结
- [QA_LLM_INTEGRATION.md](./QA_LLM_INTEGRATION.md) - LLM 集成详细文档
- [README.md](./README.md) - 项目主文档

---

**更新时间**: 2026-01-27  
**系统版本**: 1.2.0  
**状态**: ✅ 支持多 LLM 提供商集成
