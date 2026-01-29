#!/bin/bash
# 🚀 快速启动 QA 系统（带真实 LLM 集成）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎯 启动 QA 系统集成测试环境..."
echo "=================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查 Docker
echo -e "${YELLOW}📦 检查 Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker 就绪${NC}"

# 2. 检查 Docker Compose
echo -e "${YELLOW}📦 检查 Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose 就绪${NC}"

# 3. 启动必要的服务
echo -e "${YELLOW}\n🚀 启动服务...${NC}"

# 启动 Web UI（包含 LLM 配置）
echo -e "${YELLOW}  • Web UI (3000)...${NC}"
docker-compose up -d web_ui
sleep 2

# 启动 RAG 服务
echo -e "${YELLOW}  • RAG Service (8002)...${NC}"
docker-compose up -d rag_service
sleep 2

# 启动 QA Entry 服务
echo -e "${YELLOW}  • QA Entry (8001)...${NC}"
docker-compose up -d qa_entry
sleep 3

# 4. 检查服务健康状态
echo -e "${YELLOW}\n🏥 检查服务状态...${NC}"

check_service() {
    local url=$1
    local name=$2
    local max_attempts=5
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ $name 就绪${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    echo -e "${RED}❌ $name 未就绪${NC}"
    return 1
}

check_service "http://localhost:3000" "Web UI"
check_service "http://localhost:8002" "RAG Service"
check_service "http://localhost:8001" "QA Entry"

# 5. 验证 LLM 配置
echo -e "${YELLOW}\n🤖 验证 LLM 配置...${NC}"

LLM_RESPONSE=$(curl -s http://localhost:3000/api/llm/models/list)
MODEL_COUNT=$(echo "$LLM_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('models', [])))" 2>/dev/null || echo "0")

if [ "$MODEL_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ 找到 $MODEL_COUNT 个配置的模型${NC}"
else
    echo -e "${YELLOW}⚠️  未找到已配置的模型${NC}"
    echo -e "   请访问 http://localhost:3000 配置 LLM 模型"
fi

# 6. 显示访问信息
echo -e "${GREEN}\n✅ 系统启动成功！${NC}"
echo ""
echo "=================================="
echo "📱 访问地址:"
echo "=================================="
echo -e "  Web UI:       ${GREEN}http://localhost:3000${NC}"
echo -e "  QA Entry:     ${GREEN}http://localhost:8001${NC}"
echo -e "  RAG Service:  ${GREEN}http://localhost:8002${NC}"
echo ""
echo "=================================="
echo "🧪 运行测试:"
echo "=================================="
echo -e "  ${YELLOW}python test_qa_with_llm.py${NC}"
echo ""
echo "=================================="
echo "📊 查看日志:"
echo "=================================="
echo -e "  ${YELLOW}docker-compose logs -f qa_entry${NC}"
echo -e "  ${YELLOW}docker-compose logs -f rag_service${NC}"
echo ""
echo "=================================="
echo "💡 快速测试:"
echo "=================================="
echo ""
echo "1️⃣  测试 RAG 搜索:"
echo -e "  ${YELLOW}curl -X POST http://localhost:8002/api/rag/search \\${NC}"
echo -e "    ${YELLOW}-H 'Content-Type: application/json' \\${NC}"
echo -e "    ${YELLOW}-d '{\"query\":\"销售\",\"top_k\":3}'${NC}"
echo ""
echo "2️⃣  测试 QA 问题:"
echo -e "  ${YELLOW}curl -X POST http://localhost:8001/api/qa/ask \\${NC}"
echo -e "    ${YELLOW}-H 'Content-Type: application/json' \\${NC}"
echo -e "    ${YELLOW}-d '{\"question\":\"2024年Q1的销售业绩如何？\",\"user_id\":\"test_user\"}'${NC}"
echo ""
echo "📖 详细文档: QA_LLM_INTEGRATION.md"
echo ""
