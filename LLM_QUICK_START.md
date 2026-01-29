# 大模型配置快速启动指南

## 🚀 5分钟快速开始

### 1. 打开大模型配置页面

访问：**http://localhost:3000/llm_models.html**

或点击主页面菜单中的 **"🧠 大模型"** → **"🚀 完整配置页面"**

### 2. 配置 API Key（可选）

如果卡片显示 API Key 为 "sk-"，说明需要配置：

1. 点击卡片上的 **"🔑 配置 API Key"** 按钮
2. 输入您的 API Key
3. 点击 **"💾 保存"**

### 3. 切换默认大模型

#### 启用 ChatAnywhere
1. 找到 **"ChatAnywhere GPT-3.5-turbo"** 卡片
2. 点击右上角的**启用按钮**（切换为绿色）
3. 点击 **"★ 设为默认"** 按钮
4. 系统设置中的下拉菜单会自动更新

#### 启用 OpenAI
1. 找到 **"OpenAI GPT-3.5-turbo"** 卡片
2. 点击右上角的**启用按钮**（切换为绿色）
3. 点击 **"★ 设为默认"** 按钮
4. 系统设置中的下拉菜单会自动更新

### 4. 验证配置生效

立即测试问答功能，系统会使用新配置的大模型：

```bash
curl -X POST http://localhost:8001/api/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"你好"}'
```

## 📊 系统状态检查

### 检查当前默认模型
```bash
curl http://localhost:3000/api/llm/models/default/current | jq '.model | {name, provider}'
```

### 检查所有模型
```bash
curl http://localhost:3000/api/llm/models/list | jq '.models | .[] | {name, provider, enabled, is_default}'
```

### 检查 LLM Service 配置
```bash
curl http://localhost:8006/api/llm/config | jq '.'
```

## 🎯 常见场景

### 场景 1：从 OpenAI 切换到 ChatAnywhere

```
1. 打开 http://localhost:3000/llm_models.html
2. 在 ChatAnywhere 卡片上点击启用按钮
3. 点击 "★ 设为默认"
4. ✅ 完成！系统现在使用 ChatAnywhere
```

**验证**：
```bash
curl http://localhost:8006/api/llm/config | jq '.provider'
# 输出: "chatanywhere"
```

### 场景 2：更新 API Key

```
1. 点击 "🔑 配置 API Key" 按钮
2. 输入新的 API Key
3. 勾选 "显示 API Key" 来验证输入
4. 点击 "💾 保存"
5. ✅ 新 API Key 已生效
```

### 场景 3：禁用某个模型

```
1. 找到要禁用的模型卡片
2. 点击启用/禁用按钮（卡片变灰）
3. ✅ 该模型已禁用
```

## 🔧 配置文件说明

### `.env` 文件中的 LLM 配置

```properties
# 默认 LLM 提供商
LLM_PROVIDER=chatanywhere

# OpenAI 配置
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1

# ChatAnywhere 配置
CHATANYWHERE_API_KEY=sk-...
CHATANYWHERE_API_URL=https://api.chatanywhere.com.cn/v1
```

## 📱 Web UI 集成

### 主页面中的大模型管理

访问 **http://localhost:3000** 主页面：

1. 点击顶部导航栏的 **"🧠 大模型"** 菜单
2. 页面显示简化的模型列表
3. 点击 **"🚀 完整配置页面"** 进入完整管理界面

## 🔐 API Key 获取

### OpenAI
1. 登录 https://platform.openai.com/api-keys
2. 点击 "Create new secret key"
3. 复制 Key（格式：sk-...）
4. 在配置页面粘贴保存

### ChatAnywhere
1. 登录 https://chatanywhere.com/api
2. 生成或复制现有 API Key
3. 在配置页面粘贴保存

## ✅ 完整检查清单

- [ ] Web UI 已启动（http://localhost:3000）
- [ ] 可以访问大模型配置页面
- [ ] OpenAI 和 ChatAnywhere 卡片都显示
- [ ] 可以切换启用/禁用状态
- [ ] 可以更新 API Key
- [ ] 可以设置为默认模型
- [ ] Q&A 功能正常工作
- [ ] 默认模型状态正确显示

## 🆘 快速故障排除

| 问题 | 解决方案 |
|------|--------|
| 无法访问配置页面 | 确保 Web UI 容器在运行：`docker-compose ps \| grep web_ui` |
| 卡片无法加载 | 刷新页面或清除浏览器缓存 |
| 设置为默认失败 | 确保模型已启用，查看浏览器控制台错误 |
| API Key 保存失败 | 检查 API Key 格式，确保网络连接正常 |
| Q&A 仍使用旧模型 | 刷新 QA Entry 容器：`docker-compose restart qa_entry` |

## 📞 需要帮助？

1. 检查日志：`docker logs ai_lite_web_ui`
2. 查看完整指南：`LLM_MODELS_GUIDE.md`
3. 验证服务状态：`docker-compose ps`

---

**提示**：所有配置更改立即生效，无需重启服务！
