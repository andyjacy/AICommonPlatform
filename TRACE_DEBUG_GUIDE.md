# 调用链追踪 - 调试指南

## 问题排查步骤

### 1️⃣ **清除浏览器缓存（最重要！）**

#### Chrome/Edge
- 按 `Ctrl+Shift+Delete` (Windows/Linux) 或 `Cmd+Shift+Delete` (Mac)
- 选择"全部时间"
- 勾选"Cookie和其他网站数据"、"缓存的图片和文件"
- 点击"清除数据"
- 关闭并重新打开浏览器

#### Safari
- 点击菜单 Safari → 偏好设置
- 选择"隐私"选项卡
- 点击"管理网站数据"
- 找到 `localhost:3000` 并删除
- 清空历史记录：历史记录 → 清空历史记录

#### Firefox
- 按 `Ctrl+Shift+Delete` (Windows/Linux) 或 `Cmd+Shift+Delete` (Mac)
- 选择"全部"
- 点击"清除"

### 2️⃣ **完整刷新页面**

使用强制刷新（不只是普通刷新）：
- Windows/Linux: `Ctrl+Shift+R` 或 `Ctrl+F5`
- Mac: `Cmd+Shift+R`

### 3️⃣ **打开开发者工具进行调试**

按 `F12` 打开开发者工具，查看 **Console** 标签页

#### 应该看到的日志：

**提问时：**
```
✅ Trace data saved: {trace_id: "xxxxx", ...}
API Response: {question: "...", answer: "...", trace: {...}}
```

**点击"查看调用链"时：**
```
📍 displayTrace called
📍 window.currentTraceData: {...}
📍 trace object: {...}
✅ Found 11 steps in trace
✅ displayTrace rendering complete
```

#### 如果看到错误：

```
❌ No trace data available
⚠️ No steps in trace data
❌ No trace data in response
```

这表示 API 没有返回追踪数据或前端未正确捕获。

### 4️⃣ **后端诊断**

#### 验证 API 返回追踪数据
```bash
curl -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"测试","token":null}' | python3 -m json.tool | grep -A20 "trace"
```

应该看到完整的 trace 对象包含 `trace_id`、`steps` 等字段。

#### 检查前端代码是否已部署
```bash
curl http://localhost:3000/ | grep -c "displayTrace"
```

应该返回 > 0，表示函数已部署。

### 5️⃣ **前端代码验证**

在浏览器 Console 中执行：

```javascript
// 查看全局变量
console.log('currentTraceData:', window.currentTraceData);
console.log('isAnswering:', window.isAnswering);

// 测试手动调用
displayTrace();

// 查看追踪标签页是否存在
console.log('Tab elements:', document.querySelectorAll('.tab-btn'));
```

---

## 常见问题

### ❓ "查看调用链"按钮没有出现

**原因：** 后端没有返回 `trace` 对象或前端代码未正确解析

**解决：**
1. 检查浏览器 Console 是否有错误
2. 验证后端 API 是否返回追踪数据
3. 清除浏览器缓存并刷新

### ❓ 点击"查看调用链"没有反应

**原因：** 可能是 `window.currentTraceData` 为空或 `displayTrace()` 函数有错误

**解决：**
1. 在 Console 中检查 `window.currentTraceData` 是否有值
2. 在 Console 中手动调用 `displayTrace()` 查看是否有错误
3. 检查浏览器开发者工具的 Console 和 Network 标签

### ❓ 看到错误信息"调用链数据不可用"

**原因：** API 返回了追踪对象，但 `steps` 字段为空

**解决：**
1. 检查后端服务是否全部运行正常
2. 验证 `/api/trace/qa/ask` 端点返回的数据完整性

### ❓ Console 中看到 "📌 提示：需要勾选..."

**原因：** 前端代码还是旧版本（已修复）

**解决：**
1. 完全清除浏览器缓存
2. 关闭并重新打开浏览器
3. 访问 http://localhost:3000/ 并强制刷新

---

## 技术细节

### 前端工作流程

```
用户输入问题
    ↓
点击"提问"按钮
    ↓
askQuestion() 调用 /api/trace/qa/ask
    ↓
后端返回响应，包含 trace 对象
    ↓
前端保存到 window.currentTraceData
    ↓
displayResponse() 检查 trace 数据
    ↓
如果有 trace 数据，显示"查看调用链"按钮
    ↓
用户点击按钮
    ↓
viewTrace() 调用 displayTrace()
    ↓
displayTrace() 从 window.currentTraceData 读取数据
    ↓
渲染追踪信息到 UI
```

### API 响应结构

```json
{
  "question": "用户问题",
  "answer": "AI 回答",
  "confidence": 0.85,
  "execution_time": 2.5,
  "trace": {
    "trace_id": "abc123",
    "question": "用户问题",
    "total_steps": 11,
    "total_time": "2.834s",
    "steps": [
      {
        "seq": 1,
        "stage": "输入处理",
        "service": "QA Entry Service (端口 8001)",
        "purpose": "接收用户问题",
        "status": "success",
        "data": {...}
      },
      // ... 更多步骤
    ]
  }
}
```

---

## 快速测试

### 终端中测试（无需浏览器）

```bash
# 1. 测试 API 是否返回追踪数据
curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"测试","token":null}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
trace = data.get('trace', {})
print(f'✅ Trace ID: {trace.get(\"trace_id\")}')
print(f'✅ Steps: {trace.get(\"total_steps\")}')
print(f'✅ Time: {trace.get(\"total_time\")}')
"

# 2. 检查前端是否包含必要的函数
curl -s http://localhost:3000/ | grep -o "function displayTrace\|function viewTrace\|查看调用链" | sort | uniq -c

# 3. 检查 Docker 容器状态
docker-compose -f docker-compose.lite.yml ps
```

---

## 需要帮助？

如果按照上述步骤操作后仍无法看到调用链，请：

1. 清除所有浏览器缓存
2. 关闭浏览器完全重启
3. 访问 http://localhost:3000/
4. 打开开发者工具（F12）
5. 提交包含以下内容的报告：
   - Console 中的完整错误信息
   - Network 标签中 `/api/trace/qa/ask` 的响应
   - 后端服务日志
