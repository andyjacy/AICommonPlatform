# 🔐 AI 平台安全配置指南

## ⚠️ 重要安全警告

**您的 OpenAI API Key 已经公开暴露！**

请立即执行以下步骤：

### 1️⃣ 立即撤销泄露的 Key

```
访问: https://platform.openai.com/api-keys
操作: 找到并删除暴露的 Key
创建: 生成新的 API Key
```

### 2️⃣ 正确管理 API Key

永远不要：
- ❌ 在代码中硬编码 API Key
- ❌ 提交包含 API Key 的代码到 Git
- ❌ 在消息、邮件中分享 API Key
- ❌ 在公开的代码库中存储 API Key

应该这样做：
- ✅ 使用 `.env` 文件存储敏感信息
- ✅ 将 `.env` 添加到 `.gitignore`
- ✅ 使用环境变量读取配置
- ✅ 定期轮换 API Key
- ✅ 使用密钥管理服务 (如 AWS Secrets Manager)

---

## 📋 正确的配置步骤

### 第 1 步: 创建 .env 文件

```bash
# 在项目根目录创建 .env 文件（不要提交到 Git）
cp .env.example .env
```

### 第 2 步: 编辑 .env 文件

```bash
# 使用编辑器打开 .env
nano .env
# 或
vim .env
# 或使用 VS Code
code .env
```

### 第 3 步: 填入您的 API Key

```env
# OpenAI 配置 (必需)
OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_MODEL=gpt-4

# 其他 LLM 配置 (可选)
ALIBABA_API_KEY=your-alibaba-key
BAIDU_API_KEY=your-baidu-key
```

### 第 4 步: 确保 .gitignore 包含 .env

```bash
# 检查 .gitignore
cat .gitignore | grep "\.env"

# 如果没有，添加到 .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.*.local" >> .gitignore
```

### 第 5 步: 验证配置

```bash
# 测试 OpenAI 连接
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "test"}]}'
```

---

## 🔄 Docker 中使用环境变量

### 方法 1: 使用 .env 文件

```bash
# docker-compose.yml 会自动读取 .env 文件
docker-compose -f docker-compose.lite.yml up -d
```

### 方法 2: 在 docker-compose.yml 中指定

```yaml
services:
  web_ui:
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_MODEL: ${OPENAI_MODEL}
```

### 方法 3: 运行时传递环境变量

```bash
docker run -e OPENAI_API_KEY=sk-proj-xxx ... image-name
```

---

## 💡 使用配置的 Python 代码示例

### 简单例子

```python
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 读取 API Key
openai_key = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

# 验证配置
if not openai_key:
    raise ValueError("OPENAI_API_KEY 环境变量未设置")

print(f"使用模型: {openai_model}")
```

### FastAPI 中使用

```python
from fastapi import FastAPI
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    class Config:
        env_file = '.env'

settings = Settings()

app = FastAPI()

@app.get("/config")
async def get_config():
    return {
        "model": settings.openai_model,
        "key_prefix": settings.openai_api_key[:20] + "..."
    }
```

---

## 🛡️ 最佳实践

### 1. 密钥轮换

```bash
# 定期更改 API Key（建议每 3 个月）
# 1. 在 OpenAI 控制面板生成新 Key
# 2. 更新 .env 文件
# 3. 重新启动应用
# 4. 删除旧 Key
```

### 2. 权限控制

```bash
# 限制 .env 文件的读取权限
chmod 600 .env

# 验证权限
ls -la .env
# 应该显示: -rw------- (只有所有者可读写)
```

### 3. 密钥监控

```bash
# GitHub 安全警告
# 如果你不小心提交了 Key，GitHub 会自动检测并警告

# 恢复泄露的 Key
git log --all --full-history -- .env
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all
git push origin --force --all
```

### 4. 使用密钥管理服务

```python
# AWS Secrets Manager 例子
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# 使用
secrets = get_secret('ai-platform/openai')
openai_key = secrets['api_key']
```

---

## 📱 环境变量完整列表

### OpenAI

```env
# 必需
OPENAI_API_KEY=sk-proj-...
# 可选
OPENAI_MODEL=gpt-4
OPENAI_ORG_ID=org-...
OPENAI_TIMEOUT=60
```

### 阿里云

```env
ALIBABA_API_KEY=...
ALIBABA_API_SECRET=...
ALIBABA_MODEL=qwen-plus
ALIBABA_REGION=us-west-1
```

### 百度

```env
BAIDU_API_KEY=...
BAIDU_SECRET_KEY=...
BAIDU_MODEL=ernie-4.0
BAIDU_ENDPOINT=https://...
```

### 科大讯飞

```env
XUNFEI_API_KEY=...
XUNFEI_APP_ID=...
XUNFEI_MODEL=sparkdesk-v3.1
```

### 智谱

```env
ZHIPU_API_KEY=...
ZHIPU_MODEL=glm-4
```

### 企业系统

```env
ERP_API_URL=http://erp-system:8000
ERP_API_KEY=...
ERP_TIMEOUT=30

CRM_API_URL=http://crm-system:8000
CRM_API_KEY=...

HRM_API_URL=http://hrm-system:8000
HRM_API_KEY=...
```

### 系统配置

```env
LOG_LEVEL=INFO
CACHE_TTL=3600
USE_MOCK_DATA=false
DEBUG=false
```

---

## ✅ 检查清单

在生产环境部署前，确保：

- [ ] API Key 从代码中移除
- [ ] `.env` 文件添加到 `.gitignore`
- [ ] 环境变量在 docker-compose.yml 中正确配置
- [ ] `.env` 文件权限设置为 600
- [ ] 所有敏感信息使用环境变量
- [ ] 定期轮换 API Key
- [ ] 监控 API 使用情况和成本
- [ ] 为不同环境使用不同的 Key
- [ ] 建立密钥审计日志
- [ ] 文档中不包含任何真实 Key

---

## 🆘 遇到问题？

### 环境变量未被读取

```bash
# 检查 .env 文件是否存在和有效
cat .env

# 检查 Docker 环境变量
docker exec container-name env | grep OPENAI

# 查看容器日志
docker logs web_ui
```

### API Key 无效

```bash
# 验证 Key 格式
echo $OPENAI_API_KEY

# 测试 API 连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

### 权限被拒绝

```bash
# 检查 .env 文件权限
ls -la .env

# 如果权限错误，修复它
chmod 600 .env
```

---

## 📚 相关资源

- [OpenAI API 文档](https://platform.openai.com/docs)
- [Python python-dotenv](https://github.com/theskumar/python-dotenv)
- [Docker 环境变量](https://docs.docker.com/compose/environment-variables/)
- [12 Factor App - 配置](https://12factor.net/config)

---

**记住**: 安全是首要责任。永远小心处理敏感信息！ 🔒
