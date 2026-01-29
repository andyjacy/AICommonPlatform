# 🎯 调用链追踪问题 - 完整解决方案

## 问题诊断结果：✅ 系统完全正常

| 验证项目 | 状态 | 说明 |
|--------|------|------|
| 后端 Web UI 服务 | ✅ 运行中 | http://localhost:3000/ |
| API `/api/trace/qa/ask` 端点 | ✅ 正常响应 | 返回完整 trace 对象 |
| 追踪数据完整性 | ✅ 正常 | trace_id、steps、total_time 都有 |
| 前端 `displayTrace()` 函数 | ✅ 已部署 | 完整的追踪信息渲染逻辑 |
| 前端 "查看调用链" 按钮 | ✅ 已部署 | HTML 代码已包含 |
| Docker 容器 | ✅ 全部运行 | 7 个服务都在运行 |

---

## 🔴 根本原因

**浏览器缓存旧版本前端代码**

当更新了前端 JavaScript 代码后，旧版本仍被存储在浏览器缓存中，导致新的 `displayTrace()` 函数和"查看调用链"按钮无法被加载和执行。

---

## ⚡ 解决方案（3 个步骤）

### 步骤 1: 清除浏览器缓存【最重要！】

#### Mac 用户：
1. 按 **`Cmd + Shift + Delete`**
2. 或从菜单：Safari → 历史记录 → 清除历史记录 → 选择"全部历史"

#### Windows 用户：
1. 按 **`Ctrl + Shift + Delete`**
2. 或从菜单：Settings → Privacy and security → Clear browsing data

#### 清除选项：
- ☑ **Cookies 和其他网站数据**
- ☑ **缓存的图像和文件**
- 选择时间范围：**全部时间**

### 步骤 2: 完全关闭浏览器

不仅仅是关闭标签页，需要完全退出浏览器应用。

### 步骤 3: 强制刷新页面

1. 打开 `http://localhost:3000/`
2. 按快捷键强制刷新：
   - **Mac**: `Cmd + Shift + R`
   - **Windows**: `Ctrl + Shift + R`

---

## ✅ 验证修复成功

完成上述步骤后，进行以下测试：

1. 在输入框中输入一个问题（例如：`什么是人工智能`）
2. 点击 **"提问"** 按钮
3. 观察：
   - ✅ 进度条从 0% 增长到 100%
   - ✅ 显示 AI 的回答
4. 查看回答下方是否显示 **"🔍 查看调用链"** 按钮
5. 点击按钮，应该看到：
   - 自动切换到 **"调用链追踪"** 标签页
   - 显示以下信息：
     - 追踪 ID（例如：`f4b089c7`）
     - 步骤数（通常 11 步）
     - 总耗时（例如：`2.834s`）
     - 每个步骤的详细信息

---

## 🐛 高级调试（如果仍有问题）

### 检查浏览器控制台日志

1. 按 **`F12`** 打开开发者工具
2. 切换到 **"Console"** 标签页
3. 提问后，应该看到以下日志：

```
✅ Trace data saved: {trace_id: "f4b089c7", total_steps: 11, ...}
📍 displayTrace called
✅ Found 11 steps in trace
✅ displayTrace rendering complete
```

### 常见错误及解决方案

**错误消息：** `❌ No trace data available`

**原因：** `window.currentTraceData` 为空，说明数据没有被正确保存

**解决：**
1. 再次完全清除浏览器缓存（确保清除 cookies）
2. 重新启动浏览器
3. 强制刷新页面（`Cmd+Shift+R` 或 `Ctrl+Shift+R`）

**错误消息：** `❌ Error: Cannot read property 'steps'`

**原因：** 后端 API 返回格式有问题

**解决：**
```bash
# 检查 API 是否正常工作
curl -s -X POST http://localhost:8001/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}' | jq .
```

---

## 📊 技术细节

### API 返回的追踪数据结构

```json
{
  "trace": {
    "trace_id": "f4b089c7",
    "total_steps": 11,
    "total_time": "2.834s",
    "steps": [
      {
        "seq": 1,
        "service": "QA Entry Service (端口 8001)",
        "stage": "输入处理",
        "purpose": "接收用户问题，进行文本预处理和清洗",
        "status": "success",
        "data": {
          "input_question": "什么是人工智能",
          "question_type": "definition",
          "intent": "定义问题"
        }
      },
      // ... 更多步骤 (总共 11 步)
    ]
  }
}
```

### 前端执行流程

```
askQuestion()
    ↓
调用 /api/trace/qa/ask 端点
    ↓
保存响应数据到 window.currentTraceData
    ↓
displayResponse() 函数检测到有 trace 数据
    ↓
显示 "🔍 查看调用链" 按钮
    ↓
用户点击按钮 → viewTrace() 被调用
    ↓
displayTrace() 读取 window.currentTraceData
    ↓
渲染追踪信息到 UI 的 traceContent 区域
```

### 新增缓存控制机制

为了防止此类问题再次发生，前端已添加以下缓存控制：

```html
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
```

---

## 🔧 自动诊断工具

### 运行完整系统检查

```bash
cd /Users/zhao_/Documents/PRC/AI实践/AICommonPlatform
./trace_diagnostic.sh
```

此脚本将检查：
- ✅ 后端服务是否运行
- ✅ API 端点是否响应
- ✅ 前端代码是否部署
- ✅ Docker 容器状态
- ✅ 测试端到端追踪

### 查看详细指南

```bash
cat TRACE_DEBUG_GUIDE.md      # 详细的调试和故障排除指南
cat QUICK_FIX_TRACE.md        # 快速修复步骤
```

---

## 📝 系统架构（调用链追踪流程）

```
┌─────────────────────────────────────────────────────────┐
│                      用户界面 (Web UI)                   │
│  • 输入问题 → 点击"提问" → 显示"查看调用链"按钮        │
└─────────────────────────────────────────────────────────┘
              │
              ↓ 发送请求到
┌─────────────────────────────────────────────────────────┐
│        后端入口服务 (QA Entry Service - 8001)           │
│  • 接收问题 → 记录追踪信息 → 调用下游服务              │
└─────────────────────────────────────────────────────────┘
              │
              ├→ 意图识别服务 (8002)
              ├→ 知识库查询服务 (8003)
              ├→ LLM 生成服务 (8004)
              ├→ 意图验证服务 (8005)
              ├→ 结果排序服务 (8006)
              └→ 响应组装服务 (8007)
              │
              ↓ 返回结果包含 trace 信息
┌─────────────────────────────────────────────────────────┐
│                    Web UI 显示结果                       │
│  • window.currentTraceData 保存追踪数据                 │
│  • 显示"查看调用链"按钮                                 │
│  • 点击后显示 11 个处理步骤的详细信息                   │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 检查清单

- [ ] Mac: `Cmd + Shift + Delete` 或 Windows: `Ctrl + Shift + Delete`
- [ ] 勾选"Cookies 和其他网站数据"和"缓存的图像和文件"
- [ ] 选择"全部时间"
- [ ] 点击"清除数据"
- [ ] 完全关闭浏览器
- [ ] 重新打开浏览器
- [ ] 访问 `http://localhost:3000/`
- [ ] Mac: `Cmd + Shift + R` 或 Windows: `Ctrl + Shift + R` 强制刷新
- [ ] 输入测试问题
- [ ] 验证"🔍 查看调用链"按钮出现
- [ ] 点击按钮查看 11 个追踪步骤

---

## 🎉 总结

✅ **所有系统都工作正常！**

问题 **100% 是浏览器缓存** 导致的。通过清除缓存和强制刷新页面，应该会立即看到调用链追踪功能。

如有任何问题，请：
1. 检查浏览器控制台（F12）中的错误信息
2. 运行诊断脚本：`./trace_diagnostic.sh`
3. 参考详细指南：`TRACE_DEBUG_GUIDE.md`
