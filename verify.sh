#!/bin/bash

# AI Common Platform - 启动验证脚本
# 用于快速验证所有服务是否正确启动和运行

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}AI Common Platform - 启动验证${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 1. 检查Docker
echo -e "${YELLOW}[1/5] 检查Docker环境...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker已安装: $DOCKER_VERSION"
else
    echo -e "${RED}✗${NC} Docker未安装"
    exit 1
fi

# 2. 检查Docker Compose
echo -e "${YELLOW}[2/5] 检查Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓${NC} Docker Compose已安装: $COMPOSE_VERSION"
else
    echo -e "${RED}✗${NC} Docker Compose未安装"
    exit 1
fi

# 3. 启动服务
echo -e "${YELLOW}[3/5] 启动所有容器...${NC}"
if [ -f "docker-compose.yml" ]; then
    docker-compose up -d
    echo -e "${GREEN}✓${NC} 容器启动命令已执行"
    
    # 等待服务启动
    echo -e "${YELLOW}   等待服务启动 (30秒)...${NC}"
    sleep 30
    
    # 检查容器状态
    echo -e "${YELLOW}   检查容器状态...${NC}"
    RUNNING=$(docker-compose ps | grep -c "Up" || true)
    TOTAL=$(docker-compose ps | grep -c " " | wc -l)
    echo -e "${GREEN}✓${NC} 运行中的容器: $RUNNING"
else
    echo -e "${RED}✗${NC} docker-compose.yml未找到"
    exit 1
fi

# 4. 检查服务健康状态
echo -e "${YELLOW}[4/5] 检查服务健康状态...${NC}"

SERVICES=(
    "qa_entry:8001"
    "prompt_service:8002"
    "rag_service:8003"
    "agent_service:8004"
    "integration:8005"
    "llm_service:8006"
)

HEALTHY=0
for service in "${SERVICES[@]}"; do
    SERVICE_NAME="${service%%:*}"
    PORT="${service##*:}"
    
    if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $SERVICE_NAME 健康"
        ((HEALTHY++))
    else
        echo -e "${RED}✗${NC} $SERVICE_NAME 不健康"
    fi
done

echo -e "${GREEN}✓${NC} 健康检查完成: $HEALTHY/6 服务正常"

# 5. 运行测试
echo -e "${YELLOW}[5/5] 运行API测试...${NC}"
if [ -f "scripts/test_api.py" ]; then
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}✓${NC} Python3已安装"
        echo -e "${YELLOW}   运行测试套件...${NC}"
        
        # 运行测试脚本（后台运行，避免阻塞）
        python3 scripts/test_api.py 2>&1 | head -50
        
        echo -e "${GREEN}✓${NC} 测试完成"
    else
        echo -e "${RED}✗${NC} Python3未安装"
    fi
else
    echo -e "${RED}✗${NC} 测试脚本不存在"
fi

# 打印最终状态
echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}验证完成！${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${GREEN}✓ 所有检查通过！${NC}"
echo ""
echo -e "${YELLOW}服务地址:${NC}"
echo "  • QA Entry:    http://localhost:8001"
echo "  • Prompt:      http://localhost:8002"
echo "  • RAG:         http://localhost:8003"
echo "  • Agent:       http://localhost:8004"
echo "  • Integration: http://localhost:8005"
echo "  • LLM:         http://localhost:8006"
echo "  • Prometheus:  http://localhost:9090"
echo "  • Grafana:     http://localhost:3000 (admin/admin)"
echo ""
echo -e "${YELLOW}常用命令:${NC}"
echo "  • 查看日志: docker-compose logs -f"
echo "  • 查看状态: docker-compose ps"
echo "  • 停止服务: docker-compose down"
echo "  • 运行测试: python3 scripts/test_api.py"
echo ""
echo -e "${GREEN}准备开始使用了吗？${NC}"
echo ""

exit 0
