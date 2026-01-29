#!/bin/bash

# ============================================================================
# AI Common Platform - 完整 Docker 启动脚本
# 支持多 LLM 提供商集成 (OpenAI + ChatAnywhere)
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数定义
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# 主程序开始
print_header "AI Common Platform - Docker 完整启动"

# ============ 第一步：检查环境 ============
print_header "第一步: 检查环境"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker 未安装或不在 PATH 中"
    exit 1
fi
print_success "Docker 已安装: $(docker --version)"

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose 未安装或不在 PATH 中"
    exit 1
fi
print_success "Docker Compose 已安装: $(docker-compose --version)"

# 检查项目文件
if [ ! -f "docker-compose.yml" ]; then
    print_error "找不到 docker-compose.yml 文件"
    exit 1
fi
print_success "docker-compose.yml 文件存在"

# ============ 第二步：清理旧容器（可选） ============
print_header "第二步: 清理环境"

read -p "是否清理旧的容器和镜像？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "停止并删除旧容器..."
    docker-compose down -v --remove-orphans 2>/dev/null || true
    print_success "清理完成"
else
    print_info "跳过清理"
fi

# ============ 第三步：构建镜像 ============
print_header "第三步: 构建 Docker 镜像"

print_info "这可能需要 5-10 分钟，请耐心等待..."

# 构建关键服务 - 带重试机制
services=(
    "web_ui"
    "qa_entry"
    "rag_service"
    "prompt_service"
    "agent_service"
    "integration"
    "llm_service"
)

for service in "${services[@]}"; do
    print_info "构建 $service..."
    
    # 重试最多 3 次
    retry_count=0
    max_retries=3
    
    while [ $retry_count -lt $max_retries ]; do
        if docker-compose build --no-cache "$service"; then
            print_success "$service 构建成功"
            break
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $max_retries ]; then
                print_error "$service 构建失败，等待 10 秒后重试 ($retry_count/$max_retries)..."
                sleep 10
            else
                print_error "$service 构建失败 ($max_retries 次重试后)，跳过此服务"
            fi
        fi
    done
done

print_success "所有镜像构建完成"

# ============ 第四步：启动服务 ============
print_header "第四步: 启动 Docker 服务"

print_info "启动所有服务..."
docker-compose up -d

print_success "Docker 服务已启动"

# ============ 第五步：等待服务就绪 ============
print_header "第五步: 等待服务就绪"

# 等待 PostgreSQL
print_info "等待 PostgreSQL 就绪..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec ai_platform_postgres pg_isready -U admin &> /dev/null; then
        print_success "PostgreSQL 已就绪"
        break
    fi
    attempt=$((attempt + 1))
    echo -n "."
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    print_error "PostgreSQL 启动超时"
fi

# 等待 Redis
print_info "等待 Redis 就绪..."
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker exec ai_platform_redis redis-cli -a ai_redis_2024 ping &> /dev/null; then
        print_success "Redis 已就绪"
        break
    fi
    attempt=$((attempt + 1))
    echo -n "."
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    print_error "Redis 启动超时"
fi

# 等待 Web UI
print_info "等待 Web UI 就绪..."
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:3000 > /dev/null; then
        print_success "Web UI 已就绪"
        break
    fi
    attempt=$((attempt + 1))
    echo -n "."
    sleep 1
done

# 等待 QA Entry
print_info "等待 QA Entry 服务就绪..."
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8001/health > /dev/null; then
        print_success "QA Entry 已就绪"
        break
    fi
    attempt=$((attempt + 1))
    echo -n "."
    sleep 1
done

# 等待 RAG Service
print_info "等待 RAG 服务就绪..."
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8003/health > /dev/null; then
        print_success "RAG 服务已就绪"
        break
    fi
    attempt=$((attempt + 1))
    echo -n "."
    sleep 1
done

# ============ 第六步：验证服务 ============
print_header "第六步: 验证服务健康状态"

services_to_check=(
    "Web UI:http://localhost:3000"
    "QA Entry:http://localhost:8001/health"
    "RAG Service:http://localhost:8003/health"
    "Prompt Service:http://localhost:8002/health"
    "Agent Service:http://localhost:8004/health"
    "Integration:http://localhost:8005/health"
    "LLM Service:http://localhost:8006/health"
)

all_healthy=true
for service_info in "${services_to_check[@]}"; do
    IFS=':' read -r name url <<< "$service_info"
    if curl -s "$url" > /dev/null 2>&1; then
        print_success "$name 健康"
    else
        print_error "$name 不可用"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    print_success "所有服务健康"
else
    print_error "某些服务不健康，请检查日志"
    echo ""
    echo "查看日志命令:"
    echo "  docker-compose logs -f"
fi

# ============ 第七步：显示访问信息 ============
print_header "🎉 启动完成！"

echo ""
echo -e "${GREEN}访问地址:${NC}"
echo "  • Web UI:        ${BLUE}http://localhost:3000${NC}"
echo "  • QA 服务:       ${BLUE}http://localhost:8001${NC}"
echo "  • RAG 服务:      ${BLUE}http://localhost:8003${NC}"
echo "  • Prompt 服务:   ${BLUE}http://localhost:8002${NC}"
echo "  • Agent 服务:    ${BLUE}http://localhost:8004${NC}"
echo "  • Integration:   ${BLUE}http://localhost:8005${NC}"
echo "  • LLM 服务:      ${BLUE}http://localhost:8006${NC}"

echo ""
echo -e "${GREEN}数据库连接:${NC}"
echo "  • PostgreSQL:    postgresql://admin:ai_platform_2024@localhost:5432/ai_platform"
echo "  • Redis:         redis://:ai_redis_2024@localhost:6379"
echo "  • Milvus:        localhost:19530"

echo ""
echo -e "${GREEN}常用命令:${NC}"
echo "  • 查看所有日志:  ${BLUE}docker-compose logs -f${NC}"
echo "  • 查看特定服务日志: ${BLUE}docker-compose logs -f qa_entry${NC}"
echo "  • 停止所有服务:  ${BLUE}docker-compose down${NC}"
echo "  • 重启服务:      ${BLUE}docker-compose restart${NC}"
echo "  • 查看服务状态:  ${BLUE}docker-compose ps${NC}"

echo ""
echo -e "${GREEN}后续步骤:${NC}"
echo "  1. 访问 Web UI: http://localhost:3000"
echo "  2. 进入 LLM 模型管理，配置 API Key"
echo "  3. 选择 OpenAI 或 ChatAnywhere"
echo "  4. 开始提问测试"

echo ""
echo -e "${YELLOW}首次使用注意:${NC}"
echo "  • 需要在 Web UI 中配置 LLM API Key"
echo "  • OpenAI: 从 https://platform.openai.com 获取"
echo "  • ChatAnywhere: 从 https://chatanywhere.com.cn/ 获取"

echo ""
print_header "✨ 所有服务已启动！祝您使用愉快！"
