# 登陆问题排查指南

## 问题：Chrome 提示"使用的密码遭遇泄漏"

### 现象
- Chrome 浏览器在登陆页面显示密码泄漏警告
- 页面可能无法完成跳转

### 原因分析
1. **演示账号使用频繁**：`admin/admin123` 是演示账号，经常被用于公开示例和文档
2. **Chrome 安全功能**：Chrome 的密码管理器会检查账号是否在已知数据泄露中被发现
3. **浏览器自动填充行为**：当预填充密码后，Chrome 会标记为风险

### 解决方案

#### 方案 1：使用不同的演示账号（推荐）
修改 `services/web_ui/static/login.html` 中的演示账号注释：
```html
<div class="demo-hint">
    <strong>演示账号：</strong><br>
    用户名: <code>demo</code><br>
    密码: <code>demo@2024</code>
</div>
```

然后在 `services/web_ui/main.py` 中创建新的演示用户。

#### 方案 2：手动输入账号（当前推荐）
当前版本已改进：
- ✅ 不再强制预填充密码
- ✅ 仅在浏览器未保存过账号时才预填充
- ✅ 消除了 Chrome 密码泄漏警告

**使用步骤：**
1. 访问 `http://localhost:3000/login`
2. 手动输入用户名：`admin`
3. 手动输入密码：`admin123`
4. 点击"登陆"按钮
5. 页面会立即跳转到主页

#### 方案 3：禁用自动填充（备选）
如果需要完全禁用演示账号预填，修改 `login.html`：
```javascript
// 注释掉这段代码以禁用预填充
// if (!username.value && !password.value) {
//     username.value = 'admin';
//     password.value = 'admin123';
// }
```

### 改进措施

已在最新版本中实施：

1. **智能预填充**
   - 仅当浏览器未自动填充时才预填充
   - 避免触发 Chrome 密码泄漏警告

2. **改进的错误处理**
   - 添加详细的控制台日志输出
   - 提供更清晰的错误消息
   - 支持通过 token 参数直接跳转

3. **即时跳转**
   - 登陆成功后立即跳转（不再延迟 1000ms）
   - 通过 token 参数在 URL 中传递，确保认证信息不丢失

### 浏览器控制台调试

如果登陆仍然失败，打开浏览器开发者工具查看控制台：

```javascript
// 查看是否有错误信息
[Login] Starting login for user: admin
[Login] Login result: true
[Login] Token set in cookie: token_1_1769581687_85a38b6b
[Login] Redirecting to home page
```

### 常见错误及解决

| 错误信息 | 原因 | 解决方案 |
|---------|------|--------|
| "session is not defined" | session.js 未加载完成 | 检查 `/static/js/session.js` 是否可访问 |
| "用户名或密码错误" | 凭证不正确或服务器无响应 | 确认服务器运行，检查用户名密码 |
| "网络错误" | 网络连接问题 | 检查网络，确保服务器可达 |
| 页面不跳转 | Cookie 未正确设置 | 检查浏览器 Cookie 设置，尝试清除缓存 |

### 测试步骤

```bash
# 1. 确认服务运行
curl -s http://localhost:3000/login | head -1

# 2. 测试登陆 API
curl -X POST http://localhost:3000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 3. 使用 token 访问主页
TOKEN="token_1_1769581687_85a38b6b"
curl -s "http://localhost:3000/?token=$TOKEN" | grep "<title>"
```

### 联系支持

如果问题仍未解决，请检查：
1. Docker 容器是否正常运行：`docker ps`
2. 服务日志：`docker logs ai_lite_web_ui`
3. 静态文件是否可访问：`curl -s http://localhost:3000/static/js/session.js`
4. 浏览器控制台是否有 JavaScript 错误
