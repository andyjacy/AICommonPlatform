# 大模型配置指南

## 功能概述

AI Common Platform 现已支持多个大模型提供商的配置和管理，包括：

- **OpenAI** - GPT-3.5-turbo（默认）
- **ChatAnywhere** - GPT-3.5-turbo（国内备选方案）

## 如何访问大模型配置页面

### 方式一：通过主页面导航
1. 打开 Web UI：`http://localhost:3000`
2. 点击导航栏中的 **"🧠 大模型"** 菜单项
3. 在大模型管理页面点击 **"🚀 完整配置页面"** 按钮

### 方式二：直接访问
直接访问：`http://localhost:3000/llm_models.html`

## 大模型配置页面功能

### 1. 模型卡片展示

页面默认显示两个 LLM 模型卡片：

#### OpenAI GPT-3.5-turbo
- 🔵 提供商：OpenAI
- 端点：https://api.openai.com/v1
- 状态：启用/禁用
- 操作：
  - **🔑 配置 API Key**：更新 OpenAI API Key
  - **★ 设为默认**：将此模型设置为系统默认

#### ChatAnywhere GPT-3.5-turbo  
- 🔴 提供商：ChatAnywhere
- 端点：https://api.chatanywhere.com.cn/v1
- 状态：启用/禁用
- 操作：
  - **🔑 配置 API Key**：更新 ChatAnywhere API Key
  - **★ 设为默认**：将此模型设置为系统默认

### 2. 切换大模型提供商

#### 步骤 1：启用模型
点击模型卡片右上角的 **启用/禁用按钮** 来启用或禁用特定模型。

#### 步骤 2：设置为默认
对于已启用的模型，点击 **"★ 设为默认"** 按钮来设置其为系统默认模型。

#### 步骤 3：配置 API Key
1. 点击 **"🔑 配置 API Key"** 按钮
2. 在弹出的对话框中输入您的 API Key
3. （可选）勾选 **"显示 API Key"** 来查看输入内容
4. 点击 **"💾 保存"** 按钮

### 3. 系统设置面板

#### 选择默认提供商
在系统设置中的下拉菜单中选择默认的 LLM 提供商：
- OpenAI
- ChatAnywhere

#### 查看当前默认模型
显示当前系统设置的默认大模型和相关信息。

## 工作流程

### 场景 1：从 OpenAI 切换到 ChatAnywhere

```
1. 打开大模型配置页面
2. 找到 "ChatAnywhere GPT-3.5-turbo" 卡片
3. 点击切换按钮启用它
4. 点击 "★ 设为默认"
5. 在系统设置中确认默认提供商已更新为 "chatanywhere"
6. ✅ 系统现在将使用 ChatAnywhere API
```

### 场景 2：更新 API Key

```
1. 打开大模型配置页面
2. 找到需要更新的模型卡片
3. 点击 "🔑 配置 API Key"
4. 输入新的 API Key
5. 点击 "💾 保存"
6. ✅ API Key 已更新
```

### 场景 3：禁用某个模型

```
1. 打开大模型配置页面
2. 找到要禁用的模型卡片
3. 点击卡片右上角的启用/禁用按钮
4. 模型将变成灰色，表示已禁用
5. ✅ 系统不会使用此模型
```

## 核心特性

### ✨ 多提供商支持
- 支持同时配置多个 LLM 提供商
- 可以动态切换默认提供商
- 每个提供商独立配置

### 🔄 实时切换
- 无需重启服务
- 更改默认提供商后立即生效
- 支持在不同提供商间快速切换

### 🔐 安全性
- API Key 存储在本地数据库中
- 可以隐藏/显示 API Key 输入框
- 支持更新 API Key 而不暴露原始值

### 📊 可视化管理
- 清晰的卡片式界面
- 彩色状态指示（蓝色 OpenAI，红色 ChatAnywhere）
- 实时反映模型启用/禁用状态
- 显示模型默认状态

### ⚡ 快速操作
- 一键启用/禁用模型
- 一键设置为默认
- 一键配置 API Key
- 快速查看当前默认模型

## 技术实现

### 数据存储
- 模型配置存储在 SQLite 数据库中：`web_ui.db`
- 表名：`llm_models`
- 包含字段：name, provider, api_key, base_url, enabled, is_default 等

### API 端点
- `GET /api/llm/models/list` - 获取所有模型列表
- `GET /api/llm/models/{model_id}` - 获取单个模型详情
- `PUT /api/llm/models/{model_id}` - 更新模型配置
- `GET /api/llm/models/default/current` - 获取默认模型

### 环境配置
系统从以下环境变量读取 API Key：
```
LLM_PROVIDER=openai  # 默认提供商
OPENAI_API_KEY=sk-...  # OpenAI API Key
CHATANYWHERE_API_KEY=sk-...  # ChatAnywhere API Key
```

## 故障排除

### 问题 1：模型显示为禁用状态
**解决方案**：
1. 点击启用按钮重新启用模型
2. 确保 API Key 已正确配置

### 问题 2：无法设置为默认
**解决方案**：
1. 确保模型已启用
2. 刷新页面并重试
3. 检查浏览器控制台是否有错误信息

### 问题 3：API Key 保存失败
**解决方案**：
1. 检查 API Key 格式是否正确
2. 确保网络连接正常
3. 查看浏览器开发者工具中的网络请求和响应

### 问题 4：切换后仍使用旧提供商
**解决方案**：
1. 确保已点击 "★ 设为默认"
2. 检查系统设置中的默认提供商是否更新
3. 对于 QA Entry 服务，可能需要重启服务使新配置生效
4. 清除浏览器缓存重新加载页面

## 最佳实践

### 1. 定期检查 API Key 状态
建议每月检查一次 API Key 是否仍然有效。

### 2. 配置备选方案
同时配置 OpenAI 和 ChatAnywhere，以便在一个服务不可用时快速切换。

### 3. 监控成本
使用 OpenAI 前，确保账户有充足的余额或有效的支付方法。

### 4. 测试切换
在生产环境中切换提供商前，先进行小范围测试。

## API Key 获取指南

### OpenAI API Key
1. 访问 https://platform.openai.com/api-keys
2. 登录或注册 OpenAI 账户
3. 创建新的 API Key
4. 复制 Key（格式：`sk-...`）
5. 在大模型配置页面粘贴并保存

### ChatAnywhere API Key
1. 访问 https://chatanywhere.com/api
2. 注册账户或登录
3. 生成新的 API Key
4. 复制 Key（格式：`sk-...`）
5. 在大模型配置页面粘贴并保存

## 系统集成

### QA Entry 服务
QA Entry 服务会根据 Web UI 数据库中的配置自动使用正确的 LLM 提供商。

### LLM Service
LLM Service 从 LLM_PROVIDER 环境变量读取当前提供商配置。

### 自动切换流程
```
用户在 Web UI 更改默认提供商
    ↓
数据库中的 is_default 字段更新
    ↓
QA Entry 服务查询数据库获取默认配置
    ↓
LLM Service 根据配置使用对应的 API Key 和端点
    ↓
新的大模型提供商开始处理请求
```

## 更新日志

### v1.0.0 (2024-01-28)
- ✨ 新增完整的大模型配置管理界面
- ✨ 支持 OpenAI 和 ChatAnywhere 提供商
- ✨ 一键启用/禁用模型
- ✨ 一键设置为默认模型
- ✨ 在线配置和更新 API Key
- ✨ 实时显示模型状态和当前默认模型
- 📚 完整的使用文档和故障排除指南

## 联系支持

如遇到问题或有功能建议，请提交 Issue 或联系开发团队。

---

**提示**：大模型配置更改后，系统会立即生效。无需重启任何服务。
