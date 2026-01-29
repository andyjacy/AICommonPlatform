#!/bin/bash

echo "======================================"
echo "🌍 导航栏翻译功能测试"
echo "======================================"
echo ""

html=$(curl -s http://localhost:3000/)

# 测试1: 验证导航栏HTML结构
echo "📋 测试1: 验证导航栏HTML结构"
if echo "$html" | grep -q 'data-i18n="navbar.qa"'; then
    echo "✅ 导航栏已添加i18n属性"
else
    echo "❌ 导航栏缺少i18n属性"
fi

# 测试2: 验证所有导航项的中文翻译
echo ""
echo "📋 测试2: 验证所有导航项的中文翻译"
nav_items=("qa" "prompt" "rag" "agent" "integration" "llm" "monitor")
for item in "${nav_items[@]}"; do
    if echo "$html" | grep -q "'navbar.$item': '"; then
        echo "✅ navbar.$item 翻译已加载"
    else
        echo "❌ navbar.$item 翻译缺失"
    fi
done

# 测试3: 验证英文翻译
echo ""
echo "📋 测试3: 验证导航栏英文翻译存在"
en_count=$(echo "$html" | grep -o "'navbar\.[a-z]*':" | wc -l)
if [ "$en_count" -gt 10 ]; then
    echo "✅ 发现 $en_count 个导航栏翻译key"
else
    echo "❌ 导航栏翻译key不足"
fi

# 测试4: 验证updatePageLanguage函数
echo ""
echo "📋 测试4: 验证updatePageLanguage函数支持导航栏"
if echo "$html" | grep -q "el.classList.contains('nav-item')"; then
    echo "✅ updatePageLanguage函数支持导航栏"
else
    echo "❌ updatePageLanguage函数不支持导航栏"
fi

# 测试5: 验证setLanguage函数
echo ""
echo "📋 测试5: 验证setLanguage函数"
if echo "$html" | grep -q "function setLanguage(lang)"; then
    echo "✅ setLanguage函数已定义"
else
    echo "❌ setLanguage函数缺失"
fi

echo ""
echo "======================================"
echo "✅ 导航栏翻译测试完成！"
echo "======================================"
echo ""
echo "🌐 访问 http://localhost:3000"
echo "📝 测试步骤:"
echo "  1. 打开浏览器访问应用"
echo "  2. 在右上角点击 'English' 按钮"
echo "  3. 验证导航栏标签是否变为英文:"
echo "     - '问答中心' → 'Q&A Center'"
echo "     - 'Prompt 管理' → 'Prompt Management'"
echo "     - '知识库' → 'Knowledge Base'"
echo "     - 'Agent 工具' → 'Agent Tools'"
echo "     - '系统集成' → 'System Integration'"
echo "     - '大模型' → 'LLM Models'"
echo "     - '监控面板' → 'Monitor Panel'"
echo ""
echo "  4. 再次点击 '中文' 按钮验证切换回中文"
echo "  5. 刷新页面验证语言偏好是否被记住"
