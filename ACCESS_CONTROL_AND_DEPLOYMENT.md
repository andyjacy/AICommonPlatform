# 访问控制与本地部署指南

## 📋 目录

1. [功能概述](#功能概述)
2. [本地轻量化部署](#本地轻量化部署)
3. [访问控制实现](#访问控制实现)
4. [测试流程](#测试流程)
5. [常见问题](#常见问题)

---

## 功能概述

本次更新实现了两个核心功能：

### 1. 全局访问控制中间件 ✅

- **功能**: 验证所有 GET 请求的登录状态
- **行为**: 未认证用户自动重定向到登录页
- **保护路径**: `/`、`/index`、`/api/*`（除了开放端点）
- **允许路径**: `/login`、`/static/`、`/health`、`/docs`、`/api/login`

### 2. 轻量化本地 Docker 部署 ✅

- **模式支持**:
  - 单机模式：仅 Web UI（推荐用于本地开发）
  - 完整模式：Web UI + 所有微服务（用于系统集成测试）
- **快速启动**: 单机模式 < 10 秒
- **数据持久化**: SQLite 嵌入式数据库

---

## 本地轻量化部署

### 快速开始（推荐）

```bash
# 1. 启动 Web UI 单机版（仅需 Docker，不需其他微服务）
bash start_lite_local.sh

# 2. 浏览器访问
open http://localhost:3000

# 3. 自动重定向到登录页
# 输入账号: admin
# 输入密码: admin123

# 4. 登录后进入主页
```

### 完整启动（包含所有微服务）

```bash
# 启动 Web UI + 所有微服务
bash start_lite_local.sh all

# 这样可以测试完整的系统集成
```

### 常用命令

```bash
# 查看实时日志
bash start_lite_local.sh logs

# 查看特定服务的日志
bash start_lite_local.sh logs qa_entry

# 停止所有服务
bash start_lite_local.sh stop

# 重启服务
bash start_lite_local.sh restart

# 获取帮助
bash start_lite_local.sh help
```

---

## 访问控制实现

### 中间件流程图

```
HTTP 请求 (GET)
    ↓
├─ 检查 allowed_paths
│  ├─ /login → 允许
│  ├─ /static/* → 允许
│  ├─ /api/login → 允许
│  ├─ /health → 允许
│  └─ 其他 → 继续验证
│
├─ 获取 Token
│  ├─ 从 Cookie (auth_token) 获取
│  ├─ 从 Query 参数 (token) 获取
│  └─ 都没有 → ❌ 重定向到 /login (302)
│
├─ 验证 Token
│  ├─ 查询 user_sessions 表
│  ├─ 检查 token 存在 + 未过期
│  ├─ 有效 → ✅ 继续
│  └─ 无效/过期 → ❌ 重定向到 /login (302)
│
└─ 响应请求
```

### 数据库表结构

**users 表**（用户管理）
```sql
id           INTEGER PRIMARY KEY
username     TEXT UNIQUE
password_hash TEXT
role         TEXT
language     TEXT DEFAULT 'zh'
enabled      INTEGER DEFAULT 1
created_at   TIMESTAMP
```

**user_sessions 表**（会话管理）
```sql
id           INTEGER PRIMARY KEY
user_id      INTEGER FOREIGN KEY
token        TEXT UNIQUE
expires_at   TIMESTAMP
created_at   TIMESTAMP
```

**qa_history 表**（Q&A 隔离）
```sql
id           INTEGER PRIMARY KEY
user_id      INTEGER FOREIGN KEY (确保数据隔离)
question     TEXT
answer       TEXT
trace_data   JSON
created_at   TIMESTAMP
```

### Token 格式与生命周期

**Token 格式** (示例)
```
token_1_1738089600_a3f2c1e5

格式: token_{user_id}_{timestamp}_{uuid_hex}
```

**生命周期**
```
登录时创建 → 存储到 user_sessions → 7 天后自动过期
过期后：用户重定向到登录页 → 需要重新登录
```

### Cookie 设置

**前端登录后**
```javascript
const expiryDate = new Date();
expiryDate.setTime(expiryDate.getTime() + (7 * 24 * 60 * 60 * 1000));
document.cookie = `auth_token=${token}; path=/; expires=${expiryDate.toUTCString()}; SameSite=Lax`;
```

**中间件验证**
```python
auth_token = request.cookies.get("auth_token") or request.query_params.get("token")
# 查询 user_sessions 表验证 token 有效性
```

---

## 测试流程

### 自动化测试

```bash
# 运行完整的访问控制测试
bash test_access_control.sh
```

测试项目：
1. ✅ 未认证访问 / → 重定向到 /login (302)
2. ✅ 访问登录页 → 成功 (200)
3. ✅ 登录 → 获得 token
4. ✅ 使用 token 访问 / → 成功 (200)
5. ✅ 通过 Cookie 验证 → 成功 (200)
6. ✅ 使用无效 token → 重定向到 /login (302)
7. ✅ Q&A 历史隔离 → 只显示当前用户数据
8. ✅ Token 验证端点 → 成功返回用户信息
9. ✅ API 文档访问 → 始终可访问 (200)
10. ✅ 健康检查 → 始终可访问 (200)

### 手动测试

#### 测试 1: 验证未认证重定向

```bash
# 应该被重定向到 /login
curl -i http://localhost:3000/
```

预期响应：
```
HTTP/1.1 302 Found
Location: /login
```

#### 测试 2: 登录并获取 Token

```bash
curl -X POST http://localhost:3000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

预期响应：
```json
{
  "status": "success",
  "token": "token_1_1738089600_a3f2c1e5",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "language": "zh"
  },
  "expires_at": "2025-03-01T12:34:56"
}
```

#### 测试 3: 使用 Token 访问受保护资源

```bash
# 方法 1: 通过查询参数
curl -i "http://localhost:3000/?token=token_1_1738089600_a3f2c1e5"

# 方法 2: 通过 Cookie
curl -i -H "Cookie: auth_token=token_1_1738089600_a3f2c1e5" \
  http://localhost:3000/
```

预期响应：HTTP 200 with HTML content

#### 测试 4: 验证用户数据隔离

```bash
# 用户 1 登录并获取 Q&A 历史
token1=$(curl -s -X POST http://localhost:3000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.token')

# 获取用户 1 的 Q&A 历史
curl "http://localhost:3000/api/qa/history?token=$token1"
# 结果只包含该用户的 Q&A 数据
```

---

## 常见问题

### Q1: 启动时收到 "docker: command not found"

**解决方案**:
1. 安装 Docker Desktop (https://www.docker.com/products/docker-desktop)
2. 重启终端
3. 验证: `docker --version`

### Q2: 端口 3000 已被占用

**解决方案**:
```bash
# 查看占用端口 3000 的进程
lsof -i :3000

# 杀死进程
kill -9 <PID>

# 或更改端口 - 编辑 docker-compose.lite.yml
# 将 "3000:3000" 改为 "3001:3000"
```

### Q3: 登录后仍然被重定向到登录页

**可能原因**:
1. Cookie 未被正确设置 - 检查浏览器开发者工具的 Storage → Cookies
2. 浏览器隐私模式 - 尝试使用普通模式
3. 服务未完全启动 - 等待 10 秒后重试

**解决方案**:
```bash
# 查看日志
bash start_lite_local.sh logs

# 检查中间件是否正确加载
# 应该看到类似的日志：
# [Session] User logged in: admin
# [Session] Session validation error: None (not found in table)
```

### Q4: 如何修改登录账号？

**添加新用户**:
```bash
# 进入数据库
sqlite3 ./data/web_ui/web_ui.db

# 创建用户（需要 SHA256 密码哈希）
INSERT INTO users (username, password_hash, role, language, enabled)
VALUES ('newuser', '<SHA256_HASH>', 'user', 'zh', 1);

# 获取 SHA256 哈希（macOS/Linux）
echo -n "password123" | shasum -a 256
```

### Q5: 如何查看数据库？

```bash
# 使用 SQLite CLI
sqlite3 ./data/web_ui/web_ui.db

# 查看所有表
.tables

# 查看用户表
SELECT * FROM users;

# 查看会话表
SELECT * FROM user_sessions;

# 查看 Q&A 历史
SELECT * FROM qa_history;

# 退出
.quit
```

### Q6: Token 过期如何处理？

**当 token 过期**:
1. 前端 session.js 定期检查（每 5 分钟）
2. 发现过期后自动清除本地数据
3. 触发 `sessionExpired` 事件
4. 用户下次访问时自动重定向到登录页

**恢复**:
- 重新登录获取新 token

### Q7: 如何在生产环境中部署？

**推荐方案**:
```bash
# 1. 使用环保存的环境变量
export CHATANYWHERE_API_KEY=your_api_key
export LLM_PROVIDER=chatanywhere

# 2. 启动完整版本（包含所有微服务）
bash start_lite_local.sh all

# 3. 配置反向代理（nginx）
# 将外部请求转发到 localhost:3000

# 4. 启用 HTTPS
# 配置 Let's Encrypt 或自签名证书
```

---

## 架构总结

### 完整的访问控制流程

```
┌─────────────────────────────────────────────────┐
│             用户浏览器                           │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│        HTTP 请求 (GET /index)                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│   FastAPI 中间件                                 │
│   ├─ 检查允许列表                               │
│   ├─ 获取 Token (Cookie/Query)                 │
│   ├─ 查询 user_sessions 表                     │
│   └─ 验证过期时间                               │
└────────────────┬────────────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
    ✅ 有效          ❌ 无效/未找到
         │               │
         ▼               ▼
    ┌───────────┐   ┌──────────────┐
    │ 继续处理  │   │ 302 重定向   │
    │ 路由      │   │ /login       │
    └───────────┘   └──────────────┘
         │               │
         ▼               ▼
    返回资源          显示登录页
```

### 用户数据隔离

```
SQL 查询示例:

SELECT * FROM qa_history 
WHERE user_id = ? 

确保：
- 用户 A 只能看到自己的 Q&A
- 用户 B 只能看到自己的 Q&A
- 无法跨越访问其他用户数据
```

---

## 部署检查清单

- [ ] Docker 已安装
- [ ] Docker Compose 已安装
- [ ] 端口 3000 未被占用
- [ ] 数据目录存在或可创建 (`./data/web_ui/`)
- [ ] Web UI 源代码最新
- [ ] 环境变量已配置（如需要）

## 快速验证

启动后立即验证：

```bash
# 1. 访问健康检查
curl http://localhost:3000/health

# 2. 访问主页（应重定向）
curl -i http://localhost:3000/

# 3. 访问登录页（应成功）
curl http://localhost:3000/login

# 4. 运行测试
bash test_access_control.sh
```

---

## 相关文件

- `docker-compose.lite.yml` - 轻量化 Docker 配置
- `services/web_ui/main.py` - 后端中间件实现
- `services/web_ui/static/js/session.js` - 前端会话管理
- `services/web_ui/static/login.html` - 登录页面
- `start_lite_local.sh` - 启动脚本
- `test_access_control.sh` - 测试脚本

---

## 技术指标

| 指标 | 单机模式 | 完整模式 |
|------|--------|--------|
| 启动时间 | < 10s | 30-60s |
| 内存占用 | 200-300 MB | 800+ MB |
| 磁盘空间 | 500 MB | 2+ GB |
| 运行服务数 | 1 | 7 |
| 推荐用途 | 本地开发 | 系统集成测试 |

---

*最后更新: 2025-02-25*

