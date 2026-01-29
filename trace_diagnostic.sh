#!/bin/bash
set -e

echo "🧪 AI Common Platform - 调用链追踪诊断工具"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 1: 后端服务
echo "1️⃣ 检查后端服务..."
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Web UI 服务运行正常 (端口 3000)"
else
    echo -e "${RED}❌${NC} Web UI 服务未运行"
    exit 1
fi

# 检查 2: API 追踪数据
echo ""
echo "2️⃣ 测试 API 追踪数据..."
RESPONSE=$(curl -s -X POST http://localhost:3000/api/trace/qa/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"测试","token":null}')

TRACE_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('trace',{}).get('trace_id',''))" 2>/dev/null || echo "")
STEPS=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('trace',{}).get('steps',[])))" 2>/dev/null || echo "0")

if [ -n "$TRACE_ID" ] && [ "$STEPS" -gt 0 ]; then
    echo -e "${GREEN}✅${NC} API 返回追踪数据"
    echo "   - Trace ID: $TRACE_ID"
    echo "   - 步骤数: $STEPS"
else
    echo -e "${RED}❌${NC} API 未返回追踪数据"
fi

# 检查 3: 前端代码
echo ""
echo "3️⃣ 检查前端代码..."
FRONT_PAGE=$(curl -s http://localhost:3000/)

TESTS=(
    "查看调用链|按钮代码"
    "function displayTrace|displayTrace 函数"
    "function viewTrace|viewTrace 函数"
    "window.currentTraceData|全局追踪数据"
)

for i in "${!TESTS[@]}"; do
    PATTERN=$(echo "${TESTS[$i]}" | cut -d'|' -f1)
    DESC=$(echo "${TESTS[$i]}" | cut -d'|' -f2)
    
    if echo "$FRONT_PAGE" | grep -q "$PATTERN"; then
        echo -e "${GREEN}✅${NC} 前端包含 $DESC"
    else
        echo -e "${RED}❌${NC} 前端缺少 $DESC"
    fi
done

# 检查 4: 缓存控制
echo ""
echo "4️⃣ 检查缓存控制..."
HEADERS=$(curl -s -I http://localhost:3000/ | grep -i "cache-control\|pragma\|expires" | head -1)
if [ -n "$HEADERS" ]; then
    echo -e "${GREEN}✅${NC} 缓存控制已启用"
    echo "   $HEADERS"
else
    echo -e "${YELLOW}⚠️${NC} 未检测到缓存控制头"
fi

# 检查 5: Docker 容器
echo ""
echo "5️⃣ 检查 Docker 容器..."
if command -v docker-compose &> /dev/null; then
    RUNNING=$(docker-compose -f docker-compose.lite.yml ps --services --filter "status=running" 2>/dev/null | wc -l)
    if [ "$RUNNING" -gt 0 ]; then
        echo -e "${GREEN}✅${NC} Docker 容器运行中 ($RUNNING 个服务)"
    else
        echo -e "${RED}❌${NC} Docker 容器未运行"
    fi
else
    echo -e "${YELLOW}⚠️${NC} 未找到 docker-compose"
fi

# 总结
echo ""
echo "=========================================="
echo "✅ 诊断完成"
echo ""
echo "📝 建议操作："
echo "  1. 打开浏览器访问 http://localhost:3000/"
echo "  2. 按 Cmd+Shift+Delete (Mac) 或 Ctrl+Shift+Delete (Windows) 清除缓存"
echo "  3. 强制刷新页面: Cmd+Shift+R (Mac) 或 Ctrl+Shift+R (Windows)"
echo "  4. 在问答框输入问题并点击提问"
echo "  5. 等待处理完成后点击'🔍 查看调用链'按钮"
echo "  6. 打开开发者工具 (F12) 查看 Console 日志进行调试"
echo ""
echo "📚 详细调试指南: cat TRACE_DEBUG_GUIDE.md"
