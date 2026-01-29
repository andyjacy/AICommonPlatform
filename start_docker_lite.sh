#!/bin/bash

# ============================================================================
# AI Common Platform - 轻量级 Docker 启动脚本 (Lite Mode)
# 最小化依赖，快速启动，支持 ChatAnywhere + OpenAI
# ============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 函数定义
print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  ${CYAN}$1${BLUE}                    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
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

print_step() {
    echo -e "${CYAN}→ $1${NC}"
}

# 主程序开始
print_header "AI Common Platform - 轻量级启动"

# ============ 第一步：环境检查 ============
print_header "第一步: 环境检查"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker 未安装"
    exit 1
fi
print_success "Docker: $(docker --version)"

# 检查 docker-compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose 未安装"
    exit 1
fi
print_success "Docker Compose: $(docker-compose --version)"

# ============ 第二步：清理旧容器（可选）============
print_header "第二步: 环境准备"

# 查询是否有运行的容器
running_containers=$(docker-compose -f docker-compose.lite.yml ps -q 2>/dev/null || echo "")

if [ ! -z "$running_containers" ]; then
    print_info "检测到旧容器，正在清理..."
    docker-compose -f docker-compose.lite.yml down -v 2>/dev/null || true
    sleep 2
    print_success "环境已清理"
else
    print_success "环境干净"
fi

# ============ 第三步：启动服务 ============
print_header "第三步: 启动 Docker 服务"

print_info "使用轻量级配置启动服务 (docker-compose.lite.yml)..."
print_step "这可能需要 30-60 秒，请耐心等待..."

cd "$(dirname "$0")"

# 启动服务 - 轻量级模式
if docker-compose -f docker-compose.lite.yml up -d; then
    print_success "Docker 服务启动命令已发送"
else
    print_error "Docker 服务启动失败"
    exit 1
fi

# ============ 第四步：等待服务就绪 ============
print_header "第四步: 等待服务就绪"

# 定义检查函数
check_service() {
    local name=$1
    local url=$2
    local max_attempts=30
    local attempt=0
    
    print_step "检查 $name..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_success "$name 已就绪"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done
    
    print_error "$name 启动超时 (${max_attempts}s)"
    return 1
}

# 等待关键服务
check_service "Web UI" "http://localhost:3000" || true
sleep 2
check_service "QA Entry" "http://localhost:8001/health" || true
sleep 2
check_service "RAG Service" "http://localhost:8003/health" || true

# ============ 第五步：验证服务状态 ============
print_header "第五步: 验证服务状态"

echo ""
echo -e "${CYAN}服务状态检查:${NC}"
docker-compose -f docker-compose.lite.yml ps

# ============ 第六步：显示访问信息 ============
print_header "🎉 启动完成！"

echo ""
echo -e "${GREEN}📱 Web UI 地址:${NC}"
echo "  ${BLUE}http://localhost:3000${NC}"
echo ""

echo -e "${GREEN}🔗 API 地址:${NC}"
echo "  • QA 服务:       ${BLUE}http://localhost:8001${NC}"
echo "  • RAG 服务:      ${BLUE}http://localhost:8003${NC}"
echo "  • Prompt 服务:   ${BLUE}http://localhost:8002${NC}"
echo "  • Agent 服务:    ${BLUE}http://localhost:8004${NC}"
echo ""

echo -e "${GREEN}📝 常用命令:${NC}"
echo "  • 查看日志:          ${BLUE}docker-compose -f docker-compose.lite.yml logs -f${NC}"
echo "  • 查看特定服务日志:  ${BLUE}docker-compose -f docker-compose.lite.yml logs -f qa_entry${NC}"
echo "  • 停止服务:          ${BLUE}docker-compose -f docker-compose.lite.yml down${NC}"
echo "  • 重启服务:          ${BLUE}docker-compose -f docker-compose.lite.yml restart${NC}"
echo "  • 查看服务状态:      ${BLUE}docker-compose -f docker-compose.lite.yml ps${NC}"
echo ""

echo -e "${GREEN}🚀 快速测试:${NC}"
echo ""
echo "1️⃣  首次访问 Web UI:"
echo "   访问 http://localhost:3000"
echo ""

echo "2️⃣  配置 LLM 模型 (选择一个):"
echo ""
echo "   【选项 A: OpenAI】"
echo "     • 获取 API Key: https://platform.openai.com/account/api-keys"
echo "     • Provider: openai"
echo "     • Model: gpt-3.5-turbo 或 gpt-4"
echo ""

echo "   【选项 B: ChatAnywhere (推荐快速测试)】"
echo "     • 获取 API Key: https://chatanywhere.com.cn/"
echo "     • Provider: chatanywhere"
echo "     • Model: gpt-3.5-turbo"
echo "     • 特点: 免费、快速、无需信用卡"
echo ""

echo "3️⃣  在 Web UI 中:"
echo "   菜单 → LLM 模型管理 → 添加新模型 → 输入 API Key → 保存"
echo ""

echo "4️⃣  开始提问测试:"
echo "   Web UI 中输入问题: '2024年Q1的销售业绩如何？'"
echo ""

echo -e "${GREEN}📊 测试 API:${NC}"
echo ""
echo "示例: 提问关于销售的问题"
echo ""
echo -e "${CYAN}curl -X POST http://localhost:8001/api/qa/ask \\${NC}"
echo -e "${CYAN}  -H 'Content-Type: application/json' \\${NC}"
echo -e "${CYAN}  -d '{\"question\":\"2024年Q1的销售业绩如何？\",\"user_id\":\"test\"}'${NC}"
echo ""

echo -e "${YELLOW}⚠️  重要提示:${NC}"
echo "  • 首次运行需要配置 LLM API Key"
echo "  • ChatAnywhere 更快速（推荐新手）"
echo "  • OpenAI 更准确（需要 API 配额）"
echo "  • 所有数据存储在本地 SQLite"
echo ""

echo -e "${CYAN}📚 更多文档:${NC}"
echo "  • ChatAnywhere 集成: ${BLUE}CHATANYWHERE_INTEGRATION.md${NC}"
echo "  • 系统改进总结:      ${BLUE}IMPROVEMENT_SUMMARY.md${NC}"
echo "  • LLM 集成指南:      ${BLUE}QA_LLM_INTEGRATION.md${NC}"
echo ""

print_header "✨ 祝您使用愉快！"
