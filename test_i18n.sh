#!/bin/bash

echo "======================================"
echo "🌍 i18n 多语言支持 功能测试"
echo "======================================"
echo ""

# 测试1: 验证i18n对象
echo "📋 测试1: 验证i18n对象是否加载"
html=$(curl -s http://localhost:3000/)
if echo "$html" | grep -q "const i18n = {"; then
    echo "✅ i18n对象已加载"
else
    echo "❌ i18n对象加载失败"
    exit 1
fi

# 测试2: 验证中文翻译
echo ""
echo "📋 测试2: 验证中文翻译条目"
if echo "$html" | grep -q "'qa.question': '请输入您的问题'"; then
    echo "✅ 中文翻译已加载"
else
    echo "❌ 中文翻译加载失败"
fi

# 测试3: 验证英文翻译
echo ""
echo "📋 测试3: 验证英文翻译条目"
if echo "$html" | grep -q "'qa.question': 'Enter your question'"; then
    echo "✅ 英文翻译已加载"
else
    echo "❌ 英文翻译加载失败"
fi

# 测试4: 验证语言切换函数
echo ""
echo "📋 测试4: 验证语言切换函数"
if echo "$html" | grep -q "function setLanguage"; then
    echo "✅ setLanguage函数已加载"
else
    echo "❌ setLanguage函数加载失败"
fi

# 测试5: 验证语言切换按钮
echo ""
echo "📋 测试5: 验证语言切换按钮HTML"
button_count=$(echo "$html" | grep -c "language-btn")
if [ "$button_count" -ge 2 ]; then
    echo "✅ 找到 $button_count 个语言切换按钮"
else
    echo "❌ 语言切换按钮不足"
fi

# 测试6: 验证翻译数量
echo ""
echo "📋 测试6: 统计翻译条目数量"
zh_count=$(echo "$html" | grep -o "'[a-z.]*':" | wc -l)
echo "✅ 发现 $zh_count 个翻译key"

# 测试7: 验证微服务连接
echo ""
echo "📋 测试7: 验证关键微服务"
services=("QA:8001" "Prompt:8002" "RAG:8003" "Agent:8004" "Integration:8005" "LLM:8006")
for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s http://localhost:$port/health 2>/dev/null | grep -q "healthy"; then
        echo "✅ $name 服务 (端口 $port) - 正常"
    else
        echo "⚠️ $name 服务 (端口 $port) - 状态异常"
    fi
done

echo ""
echo "======================================"
echo "✅ i18n功能测试完成！"
echo "======================================"
echo ""
echo "🌐 访问地址: http://localhost:3000"
echo "📝 测试功能:"
echo "  1. 在右上角找到'中文'和'English'切换按钮"
echo "  2. 点击按钮切换语言"
echo "  3. 页面文本应该实时更新为对应语言"
echo "  4. 刷新页面，语言偏好应该被记住（localStorage）"
