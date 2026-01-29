# 🎯 AI 平台使用导航

## ⚡ 30 秒快速入门

```bash
# 1. 一键启动
python3 setup_and_verify.py

# 2. 打开浏览器
# 管理控制台: http://localhost:3000/admin
```

---

## 📚 文档地图

### 🟢 我是新手，想快速开始
👉 **阅读**: `QUICK_REFERENCE.md` (5 分钟)  
👉 **然后**: 运行 `python3 setup_and_verify.py`

### 🟡 我需要详细的部署步骤
👉 **阅读**: `DEPLOYMENT_GUIDE.md` (20 分钟)  
👉 **包含**: 完整配置、故障排查、维护

### 🔴 我关心安全和 API Key
👉 **阅读**: `SECURITY_GUIDE.md` (15 分钟)  
👉 **包含**: 最佳实践、密钥轮换、应急响应

### 🔵 我想知道所有可用的文档
👉 **阅读**: `DOCUMENTATION_INDEX.md` (10 分钟)  
👉 **包含**: 学习路径、使用时机、决策树

### 📋 我想看项目完成报告
👉 **阅读**: `COMPLETION_REPORT_2024.md` (10 分钟)  
👉 **包含**: 功能、架构、验证清单

---

## 🎯 按场景选择

### 场景 1️⃣: 第一次部署系统
```
QUICK_REFERENCE.md (第一部分)
↓
运行 setup_and_verify.py
↓
打开管理控制台
✓ 完成
```

### 场景 2️⃣: 生产环境部署
```
SECURITY_GUIDE.md (全部阅读)
↓
DEPLOYMENT_GUIDE.md (全部按步骤执行)
↓
运行 setup_and_verify.py
↓
备份和监控配置
✓ 完成
```

### 场景 3️⃣: API Key 泄露应急
```
SECURITY_GUIDE.md 第一部分
↓
按照 3 步操作：
  1. 撤销泄露的 Key
  2. 生成新 Key
  3. 更新 .env 并重启
✓ 完成
```

### 场景 4️⃣: 需要快速查询
```
QUICK_REFERENCE.md
↓
查找相应的速查表（Prompt/API/Docker 命令）
✓ 找到答案
```

### 场景 5️⃣: 遇到部署问题
```
QUICK_REFERENCE.md (快速故障排查)
↓
DEPLOYMENT_GUIDE.md (详细故障排查)
↓
查看日志: docker-compose logs -f
✓ 问题解决
```

---

## 🚀 核心功能速查

### 启动系统
```bash
# 自动化（推荐）
python3 setup_and_verify.py

# 或手动
docker-compose -f docker-compose.lite.yml up -d --build
```

### 访问系统
| 组件 | URL |
|------|-----|
| 主界面 | http://localhost:3000 |
| **管理控制台** | http://localhost:3000/admin ← 最重要 |
| API 文档 | http://localhost:8002/docs |

### Prompt 模板速查
| 名称 | 角色 | API |
|------|------|-----|
| 销售顾问 | sales_advisor | `/api/prompts/sales_advisor` |
| HR 顾问 | hr_advisor | `/api/prompts/hr_advisor` |
| 技术顾问 | tech_advisor | `/api/prompts/tech_advisor` |
| 财务顾问 | finance_advisor | `/api/prompts/finance_advisor` |
| 通用助手 | general_assistant | `/api/prompts/general_assistant` |

### Agent 工具速查
| 名称 | 图标 | API |
|------|------|-----|
| Web 搜索 | 🔍 | web_search |
| ERP 查询 | 💼 | erp_query |
| CRM 查询 | 👥 | crm_query |
| HRM 查询 | 👔 | hrm_query |
| 数据分析 | 📊 | data_analysis |
| 报告生成 | 📄 | report_generation |
| 日程管理 | 📅 | calendar_management |
| 邮件管理 | 📧 | email_management |
| 文件管理 | 📁 | file_management |

---

## 📝 常见问题快速导航

### Q: 系统无法启动？
**A**: 
1. 查看: `DEPLOYMENT_GUIDE.md` → 问题 1
2. 运行: `docker-compose logs`
3. 检查: Docker 是否运行

### Q: API Key 提示无效？
**A**:
1. 查看: `SECURITY_GUIDE.md` → API Key 无效
2. 生成新 Key: https://platform.openai.com/api-keys
3. 更新: `.env` 文件

### Q: 拖拽功能不工作？
**A**:
1. 清除浏览器缓存 (Cmd+Shift+Delete)
2. 重新加载页面 (Cmd+R)
3. 查看: 浏览器控制台是否有错误 (F12)

### Q: 怎么创建自定义 Prompt？
**A**:
1. 打开: http://localhost:3000/admin
2. 点击: Prompt Management → Create New Prompt
3. 填入信息并保存

### Q: 怎么配置企业系统（ERP/CRM）？
**A**:
1. 编辑: `.env` 文件
2. 填入: ERP_API_URL, CRM_API_URL, HRM_API_URL
3. 重启: 容器

---

## 🎓 学习路径

### Day 1: 快速上手 (2 小时)
```
1. 读 QUICK_REFERENCE.md (5 min)
2. 运行 setup_and_verify.py (10 min)
3. 打开管理控制台 (5 min)
4. 浏览 Prompt 和工具 (20 min)
5. 创建第一个自定义 Prompt (30 min)
6. 尝试拖拽排序工具 (20 min)
7. 查看 API 文档 (30 min)
```

### Day 2: 深入学习 (4 小时)
```
1. 读 SECURITY_GUIDE.md (1 hour)
2. 读 DEPLOYMENT_GUIDE.md (1 hour)
3. 配置企业系统集成 (1 hour)
4. 创建多个自定义工具 (1 hour)
```

### Day 3+: 生产部署 (持续)
```
1. 完整的安全审计
2. 性能优化
3. 监控和告警
4. 数据库持久化
5. 用户认证
```

---

## 🔧 常用命令

### Docker 操作
```bash
# 启动
docker-compose -f docker-compose.lite.yml up -d --build

# 停止
docker-compose -f docker-compose.lite.yml down

# 查看状态
docker-compose -f docker-compose.lite.yml ps

# 查看日志
docker-compose -f docker-compose.lite.yml logs -f

# 重启
docker-compose -f docker-compose.lite.yml restart
```

### API 测试
```bash
# 获取 Prompts
curl http://localhost:8002/api/prompts | jq

# 获取工具
curl http://localhost:8002/api/agent/tools | jq

# 查看 API 文档
open http://localhost:8002/docs
```

### 配置管理
```bash
# 创建 .env（从模板）
cp .env.example .env

# 编辑 .env
nano .env

# 验证配置
cat .env | grep OPENAI
```

---

## ✅ 检查清单

启动前：
- [ ] Docker 已安装
- [ ] .env 文件已创建
- [ ] OpenAI API Key 已配置
- [ ] 端口 3000, 8001, 8002 可用

启动后：
- [ ] 所有容器在运行
- [ ] Web UI 可访问
- [ ] 管理控制台加载成功
- [ ] Prompt 模板显示正确
- [ ] Agent 工具可拖拽

---

## 💡 专业建议

### 技巧 1: 节省成本
```env
# 改用更便宜的模型
OPENAI_MODEL=gpt-3.5-turbo  # 便宜 90%
```

### 技巧 2: 加快速度
```env
# 增加缓存时间
CACHE_TTL=7200  # 提高到 2 小时
```

### 技巧 3: 开发调试
```env
# 使用模拟数据，不消耗 API 配额
USE_MOCK_DATA=true
LOG_LEVEL=DEBUG
```

### 技巧 4: 监控系统
```bash
# 实时监控资源
watch 'docker stats --no-stream'

# 监控 API 请求
docker-compose -f docker-compose.lite.yml logs -f prompt_service | grep "api"
```

---

## 📞 获取帮助

### 问题解决步骤

```
遇到问题？
  ↓
1. 查看本文档的"常见问题"部分
  ↓
2. 如果不在这里，查看对应的详细文档：
   - QUICK_REFERENCE.md (快速查询)
   - DEPLOYMENT_GUIDE.md (详细步骤和故障排查)
   - SECURITY_GUIDE.md (安全问题)
  ↓
3. 查看容器日志
   docker-compose -f docker-compose.lite.yml logs -f
  ↓
4. 检查浏览器控制台 (F12)
  ↓
5. 查看网络请求 (DevTools → Network)
```

### 文档导航热键（在 VS Code 中）

```
Cmd+P (macOS) 或 Ctrl+P (Windows/Linux)
输入文件名快速打开：
- "QUICK" → QUICK_REFERENCE.md
- "SECURITY" → SECURITY_GUIDE.md
- "DEPLOYMENT" → DEPLOYMENT_GUIDE.md
- "DOCUMENTATION" → DOCUMENTATION_INDEX.md
- "COMPLETION" → COMPLETION_REPORT_2024.md
```

---

## 🎯 下一步行动

### ✅ 立即做（< 5 分钟）
```bash
python3 setup_and_verify.py
```

### ✅ 然后做（< 10 分钟）
```
打开: http://localhost:3000/admin
浏览 Prompt 和工具
```

### ✅ 再做（< 30 分钟）
```
创建自定义 Prompt
配置 Agent 工具
拖拽排序工具
```

### ✅ 最后做（< 1 小时）
```
读完 QUICK_REFERENCE.md 全部内容
准备生产部署
```

---

## 📋 文件一览

| 文件 | 大小 | 读时 | 用途 |
|------|------|------|------|
| QUICK_REFERENCE.md | 500 行 | 5 min | 快速查询 ⭐⭐⭐⭐⭐ |
| SECURITY_GUIDE.md | 1500 行 | 15 min | 安全建议 ⭐⭐⭐⭐ |
| DEPLOYMENT_GUIDE.md | 2000 行 | 20 min | 完整部署 ⭐⭐⭐⭐⭐ |
| DOCUMENTATION_INDEX.md | 1000 行 | 10 min | 文档导航 ⭐⭐⭐ |
| COMPLETION_REPORT_2024.md | 800 行 | 10 min | 项目总结 ⭐⭐⭐ |
| setup_and_verify.py | 600 行 | 2 min (运行) | 自动配置 ⭐⭐⭐⭐⭐ |

**⭐ 推荐度**: 5 = 必读，3 = 参考

---

## 🎉 祝贺！

你现在已经掌握了 AI 平台的使用方法！

**下一步**: 
1. 运行 `setup_and_verify.py`
2. 打开管理控制台
3. 开始配置你的 Prompt 和工具！

---

**最后更新**: 2024-01-15  
**版本**: 1.0.0  
**语言**: 简体中文 🇨🇳  

🚀 **让我们开始吧！**
