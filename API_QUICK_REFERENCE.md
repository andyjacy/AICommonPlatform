# 快速参考指南 - AI Common Platform v1.1

## 🚀 快速开始

### 启动系统
```bash
cd /Users/zhao_/Documents/保乐力加/AI实践/AICommonPlatform
docker-compose -f docker-compose.lite.yml up -d
```

### 访问页面
- **主页**: http://localhost:3000
- **Admin 控制台**: http://localhost:3000/admin
- **LLM 管理**: http://localhost:3000?page=llm_models

---

## 📚 API 快速参考

### LLM 模型管理

#### 列出所有模型
```bash
curl http://localhost:3000/api/llm/models/list
```

#### 创建新模型
```bash
curl -X POST http://localhost:3000/api/llm/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GPT-4",
    "provider": "OpenAI",
    "endpoint": "https://api.openai.com/v1/chat/completions",
    "api_key": "sk-xxx",
    "max_tokens": 4096,
    "temperature": 0.7,
    "description": "OpenAI GPT-4"
  }'
```

#### 更新模型
```bash
curl -X PUT http://localhost:3000/api/llm/models/1 \
  -H "Content-Type: application/json" \
  -d '{"temperature": 0.5, "is_default": true}'
```

#### 删除模型
```bash
curl -X DELETE http://localhost:3000/api/llm/models/1
```

### Prompt 模板管理

#### 列出所有模板
```bash
curl http://localhost:3000/api/prompts
```

#### 创建新模板
```bash
curl -X POST http://localhost:3000/api/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "市场分析师",
    "role": "market_analyst",
    "system_prompt": "你是一位市场分析专家...",
    "description": "市场趋势分析"
  }'
```

#### 更新模板
```bash
curl -X PUT http://localhost:3000/api/prompts/market_analyst \
  -H "Content-Type: application/json" \
  -d '{"system_prompt": "更新内容", "description": "新描述"}'
```

#### 删除模板
```bash
curl -X DELETE http://localhost:3000/api/prompts/market_analyst
```

### 配置导出
```bash
curl http://localhost:3000/api/data/export > config.json
```

---

## 🗄️ 数据库信息

### 表结构

**llm_models** - LLM 模型配置
- id, name, provider, model_type, endpoint, api_key
- max_tokens, temperature, top_p, enabled, is_default
- description, created_at, updated_at, metadata

**prompts** - Prompt 模板
- id, name, role, system_prompt, variables, description
- enabled, created_at, updated_at, metadata

---

## 🔧 常见问题

### 重置数据库
```bash
docker exec ai_lite_web_ui rm /app/web_ui.db
docker-compose -f docker-compose.lite.yml restart web_ui
```

### 查看日志
```bash
docker logs ai_lite_web_ui -f
```

### 备份数据
```bash
curl http://localhost:3000/api/data/export > backup.json
```

---

## 🎯 核心功能总结

✅ **LLM 模型持久化**: 支持创建、编辑、删除、设置默认
✅ **Prompt 模板持久化**: 完整的 CRUD 功能
✅ **Admin 页面修复**: 无错误加载和操作
✅ **配置导出**: JSON 格式完整备份
✅ **数据持久化**: 容器重启数据保留

---

*版本: 1.1 | 更新: 2026-01-26*
