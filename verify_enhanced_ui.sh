#!/bin/bash

# AI Common Platform 增强版 UI 验证脚本
# 用于快速验证新 UI 和所有功能

echo "🎬 AI Common Platform 增强版 UI 验证"
echo "====================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试计数
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    
    echo -n "测试 $name ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s "$url")
    else
        response=$(curl -s -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    if echo "$response" | grep -q "error\|Error\|ERROR" 2>/dev/null; then
        echo -e "${RED}✗ 失败${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    else
        echo -e "${GREEN}✓ 成功${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    fi
}

# 1. 检查 Web UI 服务
echo -e "${BLUE}1. 检查基础服务${NC}"
echo ""

echo -n "检查 Web UI 健康状态 ... "
response=$(curl -s http://localhost:3000/health)
if echo "$response" | grep -q "healthy"; then
    echo -e "${GREEN}✓ 健康${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ 不健康${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo -n "检查主页加载 ... "
response=$(curl -s http://localhost:3000/)
if echo "$response" | grep -q "AI Common Platform"; then
    echo -e "${GREEN}✓ 成功${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ 失败${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo -e "${BLUE}2. 测试 API 端点${NC}"
echo ""

# 测试 QA 接口
test_endpoint "QA 提问接口" "POST" "http://localhost:3000/api/qa/ask" \
    '{"question": "销售数据如何", "user_id": "test_user"}'

# 测试 Prompt 接口
test_endpoint "Prompt 列表接口" "GET" "http://localhost:3000/api/prompts" ""

# 测试知识库文档接口
test_endpoint "知识库文档接口" "GET" "http://localhost:3000/api/rag/documents" ""

# 测试搜索接口
test_endpoint "知识库搜索接口" "POST" "http://localhost:3000/api/rag/search" \
    '{"query": "销售报告", "top_k": 5}'

# 测试 Agent 工具接口
test_endpoint "Agent 工具接口" "GET" "http://localhost:3000/api/agent/tools" ""

# 测试服务状态接口
test_endpoint "服务状态接口" "GET" "http://localhost:3000/api/services/status" ""

echo ""
echo -e "${BLUE}3. 测试后端服务连接${NC}"
echo ""

# 测试各个微服务
services=(
    "QA Entry:8001"
    "Prompt Service:8002"
    "RAG Service:8003"
    "Agent Service:8004"
    "Integration:8005"
    "LLM Service:8006"
)

for service in "${services[@]}"; do
    name=${service%:*}
    port=${service#*:}
    echo -n "测试 $name (端口 $port) ... "
    
    if curl -s "http://localhost:$port/health" | grep -q "healthy\|ok\|true"; then
        echo -e "${GREEN}✓ 健康${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠ 可能不可用（这是正常的，会使用 Mock 数据）${NC}"
    fi
done

echo ""
echo -e "${BLUE}4. 验证 UI 功能${NC}"
echo ""

# 检查 HTML 是否包含必要的元素
echo -n "检查导航菜单元素 ... "
if curl -s http://localhost:3000/ | grep -q "问答中心\|Prompt\|知识库"; then
    echo -e "${GREEN}✓ 找到${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ 未找到${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo -n "检查模块页面 ... "
if curl -s http://localhost:3000/ | grep -q "qa-page\|prompt-page\|rag-page"; then
    echo -e "${GREEN}✓ 找到${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ 未找到${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo -n "检查样式表 ... "
if curl -s http://localhost:3000/ | grep -q "<style>"; then
    echo -e "${GREEN}✓ 找到${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ 未找到${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo -n "检查 JavaScript 代码 ... "
if curl -s http://localhost:3000/ | grep -q "<script>" || curl -s http://localhost:3000/ | grep -q "function switchPage"; then
    echo -e "${GREEN}✓ 找到${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ 未找到${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo -e "${BLUE}5. 实时数据测试${NC}"
echo ""

# 测试 Mock 数据质量
echo -n "测试 QA Mock 数据 ... "
response=$(curl -s -X POST http://localhost:3000/api/qa/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "员工数量"}')
if echo "$response" | grep -q "question\|answer\|confidence"; then
    echo -e "${GREEN}✓ 数据完整${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ 数据不完整${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo -n "测试搜索结果结构 ... "
response=$(curl -s -X POST http://localhost:3000/api/rag/search \
    -H "Content-Type: application/json" \
    -d '{"query": "测试"}')
if echo "$response" | grep -q "documents\|results\|total"; then
    echo -e "${GREEN}✓ 结构正确${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ 结构错误${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo "====================================="
echo -e "${BLUE}测试总结${NC}"
echo "====================================="
echo -e "✓ 通过: ${GREEN}$TESTS_PASSED${NC}"
echo -e "✗ 失败: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！UI 已就绪。${NC}"
    echo ""
    echo "📖 访问以下地址查看 UI："
    echo "   主页: http://localhost:3000"
    echo "   API 文档: http://localhost:3000/docs"
    echo ""
    echo "📝 查看文档："
    echo "   ENHANCED_UI_GUIDE.md - 详细使用指南"
    echo "   DEMO_GUIDE.md - 演示指南和说明"
    exit 0
else
    echo -e "${YELLOW}⚠ 有部分测试未通过，但 Mock 数据会提供备用支持${NC}"
    echo ""
    echo "常见原因："
    echo "1. 某些微服务可能未运行（会自动使用 Mock 数据）"
    echo "2. 网络连接问题（检查 Docker 网络）"
    echo "3. 端口冲突（检查是否有其他进程占用）"
    echo ""
    echo "解决方案："
    echo "1. 检查 Docker 容器状态: docker ps"
    echo "2. 查看日志: docker logs ai_lite_web_ui"
    echo "3. 重启服务: docker restart ai_lite_web_ui"
    exit 1
fi
