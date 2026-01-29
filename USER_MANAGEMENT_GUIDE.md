# 用户管理和国际化完整实现指南

## 概述

本文档详细说明了如何完全实现用户管理（登录、会话、用户隔离）、国际化（中英文切换）和问答历史追踪功能。

---

## 架构设计

### 1. 用户会话管理架构

```
登录流程：
用户输入用户名/密码
         ↓
POST /api/login → 验证凭证
         ↓
生成 token (UUID + 时间戳)
         ↓
存储到 user_sessions 表
         ↓
返回 token + 用户信息
         ↓
客户端保存 token 到 localStorage
         ↓
后续请求携带 token
         ↓
GET /api/user/verify-token → 验证有效性
         ↓
提取 user_id → 查询用户专属数据
```

### 2. 数据库设计

#### users 表（用户表）
```sql
id                  INTEGER PRIMARY KEY
username            TEXT NOT NULL UNIQUE
password_hash       TEXT NOT NULL
email               TEXT
role                TEXT DEFAULT 'user'
enabled             BOOLEAN DEFAULT 1
language            TEXT DEFAULT 'zh'  -- 新增字段
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

#### user_sessions 表（用户会话表 - 新增）
```sql
id                  INTEGER PRIMARY KEY
user_id             INTEGER NOT NULL (FK → users.id)
token               TEXT NOT NULL UNIQUE
expires_at          TIMESTAMP NOT NULL  -- 7天后过期
created_at          TIMESTAMP
```

#### qa_history 表（问答历史表 - 新增）
```sql
id                  INTEGER PRIMARY KEY
user_id             INTEGER NOT NULL (FK → users.id)
question            TEXT NOT NULL
answer              TEXT NOT NULL
question_type       TEXT
confidence          REAL DEFAULT 0.0
sources             TEXT (JSON 格式)
execution_time      REAL DEFAULT 0.0
trace_id            TEXT
trace_data          TEXT (完整调用链 JSON)
created_at          TIMESTAMP
```

### 3. 会话令牌格式

```
token_{user_id}_{timestamp}_{uuid_hex}

示例：
token_1_1738089600_a3f2c1e5

说明：
- 前缀: "token_"
- user_id: 用户 ID (例：1)
- timestamp: Unix 时间戳
- uuid_hex: UUID 前8位十六进制字符
```

### 4. 会话生命周期

```
创建时间: 登录时
有效期: 7 天
检查间隔: 每 5 分钟（前端）
过期处理: 自动清除 + 重新登录
```

---

## 后端实现（FastAPI）

### 1. 数据库初始化

**文件**: `/services/web_ui/main.py`（第 136-174 行）

```python
# 创建 user_sessions 表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL UNIQUE,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

# 创建 qa_history 表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS qa_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        question_type TEXT,
        confidence REAL DEFAULT 0.0,
        sources TEXT,
        execution_time REAL DEFAULT 0.0,
        trace_id TEXT,
        trace_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

# 添加 language 字段到 users 表
cursor.execute("""ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'zh'""")
```

### 2. 登入接口

**文件**: `/services/web_ui/main.py`（POST /api/login）

```python
@app.post("/api/login")
async def login(request: LoginRequest):
    """用户登陆"""
    try:
        from datetime import timedelta
        import hashlib
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 验证用户
        password_hash = hashlib.sha256(request.password.encode()).hexdigest()
        cursor.execute("""
            SELECT id, username, role, language FROM users 
            WHERE username=? AND password_hash=? AND enabled=1
        """, (request.username, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            user_id = user[0]
            
            # 生成会话令牌
            token = f"token_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            expires_at = (datetime.now() + timedelta(days=7)).isoformat()
            
            # 保存会话
            cursor.execute("""
                INSERT INTO user_sessions (user_id, token, expires_at)
                VALUES (?, ?, ?)
            """, (user_id, token, expires_at))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "token": token,
                "user": {
                    "id": user_id,
                    "username": user[1],
                    "role": user[2],
                    "language": user[3] or 'zh'
                },
                "expires_at": expires_at
            }
        else:
            conn.close()
            return {"status": "error", "message": "用户名或密码错误"}
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return {"status": "error", "message": str(e)}
```

### 3. 令牌验证接口

**文件**: `/services/web_ui/main.py`（GET /api/user/verify-token）

```python
@app.get("/api/user/verify-token")
async def verify_token(token: str = Query(...)):
    """验证会话令牌"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT us.user_id, u.username, u.role, u.language 
            FROM user_sessions us
            JOIN users u ON us.user_id = u.id
            WHERE us.token = ? AND us.expires_at > ?
        """, (token, datetime.now().isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "status": "valid",
                "user_id": row[0],
                "username": row[1],
                "role": row[2],
                "language": row[3]
            }
        else:
            return {"status": "invalid"}
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return {"status": "error", "message": str(e)}
```

### 4. 问答历史保存

**文件**: `/services/web_ui/main.py`（POST /api/trace/qa/ask - 第 1300-1330 行）

```python
# 从 token 提取 user_id
user_id = None
user_token = getattr(request, 'token', None)
if user_token:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM user_sessions WHERE token = ?", (user_token,))
    row = cursor.fetchone()
    if row:
        user_id = row[0]
    conn.close()

# ... 处理问答 ...

# 保存到用户问答历史
if user_id:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO qa_history 
            (user_id, question, answer, question_type, confidence, sources, execution_time, trace_id, trace_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            request.question,
            qa_response.get("answer", ""),
            intent_data,
            qa_response.get("confidence", 0),
            json.dumps(sources),
            qa_response.get("execution_time", 0),
            chain.trace_id,
            json.dumps(chain.get_summary())
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to save QA history: {e}")
```

### 5. 问答历史查询接口

**文件**: `/services/web_ui/main.py`

```python
# 获取用户历史列表
@app.get("/api/qa/history")
async def get_qa_history(token: str = Query(...), limit: int = Query(20)):
    """获取用户的问答历史"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 验证 token 并获取 user_id
        cursor.execute("SELECT user_id FROM user_sessions WHERE token = ?", (token,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"status": "error", "message": "令牌无效"}
        
        user_id = row[0]
        
        # 获取该用户的历史（用户隔离）
        cursor.execute("""
            SELECT id, question, answer, question_type, confidence, sources, 
                   execution_time, created_at
            FROM qa_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        # 返回用户专属的历史数据
        history = [...]
        return {
            "status": "success",
            "user_id": user_id,
            "total": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Failed to get QA history: {e}")
        return {"status": "error", "message": str(e)}

# 获取特定问答详情
@app.get("/api/qa/history/{qa_id}")
async def get_qa_detail(qa_id: int, token: str = Query(...)):
    """获取特定问答的完整详情"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 验证 token
        cursor.execute("SELECT user_id FROM user_sessions WHERE token = ?", (token,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"status": "error", "message": "令牌无效"}
        
        user_id = row[0]
        
        # 查询问答（确保属于当前用户）
        cursor.execute("""
            SELECT id, question, answer, question_type, confidence, sources, 
                   execution_time, trace_id, trace_data, created_at
            FROM qa_history
            WHERE id = ? AND user_id = ?
        """, (qa_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"status": "error", "message": "未找到此问答记录"}
        
        # 返回完整详情
        return {
            "status": "success",
            "qa": {...}
        }
```

### 6. 语言偏好接口

**文件**: `/services/web_ui/main.py`

```python
@app.put("/api/user/language")
async def set_user_language(token: str = Query(...), language: str = Query(...)):
    """设置用户语言偏好"""
    if language not in ['zh', 'en']:
        return {"status": "error", "message": "不支持的语言"}
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 从 token 获取 user_id
        cursor.execute("SELECT user_id FROM user_sessions WHERE token = ?", (token,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"status": "error", "message": "令牌无效"}
        
        user_id = row[0]
        
        # 更新用户语言
        cursor.execute("UPDATE users SET language = ? WHERE id = ?", (language, user_id))
        conn.commit()
        conn.close()
        
        return {"status": "success", "language": language}
```

---

## 前端实现（JavaScript）

### 1. 国际化模块

**文件**: `/services/web_ui/static/js/i18n.js`

```javascript
class I18nManager {
    constructor() {
        this.language = 'zh';
        this.translations = {};
    }

    async init(defaultLang = 'zh') {
        this.language = defaultLang;
        
        // 从 localStorage 获取用户偏好
        const savedLang = localStorage.getItem('user_language');
        if (savedLang && ['zh', 'en'].includes(savedLang)) {
            this.language = savedLang;
        }
        
        // 加载翻译文件
        await this.loadLanguage(this.language);
    }

    async loadLanguage(lang) {
        try {
            const response = await fetch(`/static/i18n/${lang}.json`);
            if (response.ok) {
                this.translations = await response.json();
                this.language = lang;
                localStorage.setItem('user_language', lang);
            }
        } catch (error) {
            console.error(`Error loading language file:`, error);
        }
    }

    t(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations;

        for (const k of keys) {
            value = value?.[k];
            if (!value) return key;
        }

        // 替换参数
        let result = value;
        for (const [param, paramValue] of Object.entries(params)) {
            result = result.replace(`{{${param}}}`, paramValue);
        }

        return result;
    }

    async switchLanguage(lang) {
        if (!['zh', 'en'].includes(lang)) return false;

        await this.loadLanguage(lang);
        
        // 触发语言变化事件
        window.dispatchEvent(new CustomEvent('languageChanged', { 
            detail: { language: lang } 
        }));

        return true;
    }
}

const i18n = new I18nManager();
```

### 2. 会话管理模块

**文件**: `/services/web_ui/static/js/session.js`

```javascript
class SessionManager {
    constructor() {
        this.token = null;
        this.user = null;
        this.isAuthenticated = false;
    }

    async init() {
        const savedToken = localStorage.getItem('auth_token');
        
        if (savedToken) {
            if (await this.verifyToken(savedToken)) {
                this.token = savedToken;
                return true;
            } else {
                localStorage.removeItem('auth_token');
                return false;
            }
        }
        
        return false;
    }

    async login(username, password) {
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.status === 'success' && data.token) {
                this.token = data.token;
                this.user = data.user;
                this.isAuthenticated = true;

                localStorage.setItem('auth_token', this.token);
                localStorage.setItem('user_info', JSON.stringify(this.user));

                this.startSessionCheck();
                return true;
            }
            return false;
        } catch (error) {
            console.error('[Session] Login error:', error);
            return false;
        }
    }

    async logout() {
        try {
            if (this.token) {
                await fetch(`/api/user/logout?token=${this.token}`, {
                    method: 'POST'
                });
            }

            this.token = null;
            this.user = null;
            this.isAuthenticated = false;
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_info');

            this.stopSessionCheck();
            return true;
        } catch (error) {
            console.error('[Session] Logout error:', error);
            return false;
        }
    }

    async verifyToken(token) {
        try {
            const response = await fetch(`/api/user/verify-token?token=${token}`);
            const data = await response.json();

            if (data.status === 'valid') {
                this.user = {
                    id: data.user_id,
                    username: data.username,
                    role: data.role,
                    language: data.language
                };
                this.isAuthenticated = true;
                return true;
            }
            this.isAuthenticated = false;
            return false;
        } catch (error) {
            console.error('[Session] Token verification error:', error);
            return false;
        }
    }

    startSessionCheck() {
        // 每 5 分钟检查一次会话有效性
        this.sessionCheckInterval = setInterval(async () => {
            if (this.token && !await this.verifyToken(this.token)) {
                console.log('[Session] Session expired');
                await this.logout();
                window.dispatchEvent(new CustomEvent('sessionExpired'));
            }
        }, 5 * 60 * 1000);
    }

    stopSessionCheck() {
        if (this.sessionCheckInterval) {
            clearInterval(this.sessionCheckInterval);
        }
    }

    getToken() { return this.token; }
    getUser() { return this.user; }
    isLoggedIn() { return this.isAuthenticated; }
}

const session = new SessionManager();
```

### 3. 登录页面集成

**文件**: `/services/web_ui/static/login.html`

```javascript
<script src="/static/js/i18n.js"></script>
<script src="/static/js/session.js"></script>

<script>
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            // 使用会话管理器登录
            const loginSuccess = await session.login(
                username.value, 
                password.value
            );

            if (loginSuccess) {
                localStorage.setItem('auth_token', session.getToken());
                window.location.href = '/';
            } else {
                showError('用户名或密码错误');
            }
        } catch (error) {
            showError('网络错误: ' + error.message);
        }
    });
</script>
```

### 4. 主页面集成

**文件**: `/services/web_ui/static/index.html`

```javascript
<script src="/static/js/i18n.js"></script>
<script src="/static/js/session.js"></script>

<script>
    window.addEventListener('DOMContentLoaded', async () => {
        // 检查登录状态
        if (!session.isLoggedIn()) {
            window.location.href = '/login';
            return;
        }

        // 更新用户名
        const user = session.getUser();
        document.getElementById('userName').textContent = user.username;

        // 初始化国际化
        await i18n.init(user?.language || 'zh');
    });

    // 语言切换
    async function toggleLanguage() {
        const currentLang = i18n.getCurrentLanguage();
        const newLang = currentLang === 'zh' ? 'en' : 'zh';
        const token = session.getToken();

        await switchUserLanguage(newLang, token);
    }

    // 登出处理
    async function handleLogout(event) {
        event.preventDefault();
        
        if (confirm('确认登出？')) {
            await session.logout();
            window.location.href = '/login';
        }
    }
</script>
```

---

## 测试指南

### 1. 测试用户隔离

```bash
# 用户 1 登录并提问
curl -X POST http://localhost:3000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 返回的 token 示例
{
  "status": "success",
  "token": "token_1_1738089600_a3f2c1e5",
  "user": {"id": 1, "username": "admin", "role": "admin", "language": "zh"}
}

# 用户 1 提问（带 token）
curl -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "销售数据怎样?",
    "token": "token_1_1738089600_a3f2c1e5"
  }'

# 用户 1 查看自己的历史
curl "http://localhost:3000/api/qa/history?token=token_1_1738089600_a3f2c1e5&limit=10"

# 返回的历史应该只包含用户 1 的问答
{
  "status": "success",
  "user_id": 1,
  "total": 1,
  "history": [
    {
      "id": 1,
      "question": "销售数据怎样?",
      "answer": "...",
      "created_at": "2024-01-28T..."
    }
  ]
}
```

### 2. 测试会话过期

```bash
# 生成一个过期的 token（expires_at 设置为过去的时间）
# 尝试使用它
curl "http://localhost:3000/api/user/verify-token?token=expired_token"

# 应该返回
{
  "status": "invalid"
}
```

### 3. 测试语言切换

```bash
# 获取当前语言
curl "http://localhost:3000/api/user/verify-token?token=token_1_..."
# 返回 "language": "zh"

# 切换到英文
curl -X PUT "http://localhost:3000/api/user/language?token=token_1_...&language=en"

# 再次验证
curl "http://localhost:3000/api/user/verify-token?token=token_1_..."
# 返回 "language": "en"
```

### 4. 浏览器测试

1. 打开 http://localhost:3000/login
2. 输入用户名: `admin`, 密码: `admin123`
3. 点击登录 → 应该跳转到主页
4. 确认用户名显示在导航栏右侧
5. 提问并查看问答历史
6. 点击语言按钮切换中英文
7. 刷新页面，确认语言偏好保持

---

## 部署检查清单

- [ ] 数据库表已创建 (user_sessions, qa_history)
- [ ] 后端 API 端点已实现（登录、验证、历史、语言）
- [ ] 前端模块已加载 (i18n.js, session.js)
- [ ] 登录页面已更新
- [ ] 主页面已集成会话管理
- [ ] 导航栏添加了用户菜单和语言切换器
- [ ] 问答接口传递了 token
- [ ] 问答历史已保存到数据库
- [ ] 翻译文件已创建 (zh.json, en.json)
- [ ] CSS 样式已添加

---

## 关键特性验证

### ✅ 用户会话管理
- 登录生成持久化会话
- Token 有 7 天有效期
- 自动过期处理
- 安全登出清除会话

### ✅ 用户数据隔离
- 每个用户只看自己的问答历史
- 数据库查询包含 user_id 过滤
- API 验证 token 对应的用户身份

### ✅ 国际化支持
- 支持中文 (zh) 和英文 (en)
- 用户语言偏好持久化
- 页面实时语言切换
- 语言偏好跨 session 保持

### ✅ 调用链实时数据
- 步骤 10（结果处理）显示真实 KB 匹配数
- 步骤 11（响应返回）显示实际集成数据
- 包含真实置信度和执行时间

---

## 故障排查

### 问题：登录后仍显示登录页面
**解决**: 检查 localStorage 是否正常工作，验证 session.isLoggedIn() 返回值

### 问题：问答历史为空
**解决**: 确认 token 正确传递，检查 user_id 是否正确提取

### 问题：语言切换不生效
**解决**: 确认翻译文件路径正确，检查浏览器控制台错误

### 问题：会话频繁过期
**解决**: 检查服务器时间是否同步，增加 startSessionCheck 间隔

---

## 总结

该实现提供了：
1. **企业级用户管理** - 安全的身份验证和会话管理
2. **数据隔离** - 用户只能访问自己的数据
3. **国际化支持** - 中英文切换和偏好保存
4. **审计追踪** - 完整的 QA 历史记录和追踪数据
5. **真实数据展示** - 调用链显示实际的服务交互结果

