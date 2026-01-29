#!/bin/bash

# ==================== 轻量化本地启动脚本 ====================
# 支持快速本地测试，仅启动 Web UI 服务
# 
# 用法：
#   bash start_lite_local.sh          # 启动 Web UI 单机版（推荐）
#   bash start_lite_local.sh all      # 启动 Web UI + 所有微服务
#   bash start_lite_local.sh stop     # 停止所有服务
#   bash start_lite_local.sh logs     # 查看实时日志

set -e

# ==================== 配置 ====================

PROJECT_NAME="ai_platform_lite"
COMPOSE_FILE="docker-compose.lite.yml"
WEB_UI_PORT=3000
WEB_UI_URL="http://localhost:${WEB_UI_PORT}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==================== 辅助函数 ====================

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}➜${NC} $1"
}

# ==================== 检查依赖 ====================

check_requirements() {
    print_header "检查依赖"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装或未在 PATH 中"
        exit 1
    fi
    print_success "Docker 已安装"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装或未在 PATH 中"
        exit 1
    fi
    print_success "Docker Compose 已安装"
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "$COMPOSE_FILE 文件不存在"
        exit 1
    fi
    print_success "$COMPOSE_FILE 文件已找到"
}

# ==================== 启动服务 ====================

start_services() {
    local mode="${1:-web_ui}"
    
    if [ "$mode" = "all" ]; then
        print_header "启动 Web UI + 所有微服务（完整模式）"
        print_info "这将启动：Web UI + QA Entry + Prompt + RAG + Agent + Integration + LLM"
        print_info "所有服务大约需要 30-60 秒启动"
        
        docker-compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" \
            --profile all up --build -d
            
    else
        print_header "启动 Web UI 单机版（轻量模式）"
        print_info "仅启动 Web UI 服务，快速轻量化部署"
        
        docker-compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" \
            up --build -d web_ui
    fi
    
    # 等待服务启动
    print_info "等待服务启动..."
    sleep 5
    
    # 检查 Web UI 健康状态
    print_info "检查 Web UI 健康状态..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$WEB_UI_URL/health" > /dev/null 2>&1; then
            print_success "Web UI 健康检查通过"
            break
        fi
        attempt=$((attempt + 1))
        if [ $attempt -eq $max_attempts ]; then
            print_error "Web UI 启动超时，请检查日志"
            docker-compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" logs web_ui
            exit 1
        fi
        sleep 1
    done
}

# ==================== 显示信息 ====================

show_info() {
    local mode="${1:-web_ui}"
    
    echo ""
    print_header "启动完成！"
    echo ""
    
    echo -e "${GREEN}Web UI 访问地址:${NC}"
    echo -e "  ${BLUE}$WEB_UI_URL${NC}"
    echo ""
    
    echo -e "${GREEN}默认账号:${NC}"
    echo -e "  用户名: ${YELLOW}admin${NC}"
    echo -e "  密码: ${YELLOW}admin123${NC}"
    echo ""
    
    echo -e "${GREEN}快速链接:${NC}"
    echo -e "  登录页面: ${BLUE}$WEB_UI_URL/login${NC}"
    echo -e "  主页: ${BLUE}$WEB_UI_URL/${NC}"
    echo -e "  API 文档: ${BLUE}$WEB_UI_URL/docs${NC}"
    echo ""
    
    if [ "$mode" = "all" ]; then
        echo -e "${GREEN}微服务地址:${NC}"
        echo -e "  QA Entry: ${BLUE}http://localhost:8001${NC}"
        echo -e "  Prompt Service: ${BLUE}http://localhost:8002${NC}"
        echo -e "  RAG Service: ${BLUE}http://localhost:8003${NC}"
        echo -e "  Agent Service: ${BLUE}http://localhost:8004${NC}"
        echo -e "  Integration: ${BLUE}http://localhost:8005${NC}"
        echo -e "  LLM Service: ${BLUE}http://localhost:8006${NC}"
        echo ""
    fi
    
    echo -e "${GREEN}常用命令:${NC}"
    echo -e "  查看日志: ${YELLOW}bash start_lite_local.sh logs${NC}"
    echo -e "  停止服务: ${YELLOW}bash start_lite_local.sh stop${NC}"
    echo -e "  重启服务: ${YELLOW}bash start_lite_local.sh restart${NC}"
    echo ""
    
    echo -e "${GREEN}测试流程:${NC}"
    echo -e "  1. 访问 $WEB_UI_URL"
    echo -e "  2. 系统应自动重定向到 $WEB_UI_URL/login"
    echo -e "  3. 使用 admin/admin123 登录"
    echo -e "  4. 登录后访问主页查看 Q&A 功能"
    echo -e "  5. 尝试提问并查看调用链结果"
    echo ""
}

# ==================== 显示日志 ====================

show_logs() {
    local service="${1:-web_ui}"
    print_header "显示 $service 日志（按 Ctrl+C 退出）"
    docker-compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" logs -f "$service"
}

# ==================== 停止服务 ====================

stop_services() {
    print_header "停止所有服务"
    docker-compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" down
    print_success "所有服务已停止"
}

# ==================== 重启服务 ====================

restart_services() {
    print_header "重启服务"
    stop_services
    sleep 2
    start_services "$1"
    show_info "$1"
}

# ==================== 主程序 ====================

main() {
    local command="${1:-start}"
    
    case "$command" in
        "start")
            check_requirements
            start_services "web_ui"
            show_info "web_ui"
            ;;
        "all")
            check_requirements
            start_services "all"
            show_info "all"
            ;;
        "logs")
            show_logs "${2:-web_ui}"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services "${2:-web_ui}"
            ;;
        *)
            print_header "使用帮助"
            echo ""
            echo "用法: bash start_lite_local.sh [命令]"
            echo ""
            echo "命令:"
            echo "  start                  启动 Web UI 单机版（默认）"
            echo "  all                    启动 Web UI + 所有微服务"
            echo "  logs [service]         查看实时日志"
            echo "  stop                   停止所有服务"
            echo "  restart [mode]         重启服务"
            echo ""
            echo "示例:"
            echo "  bash start_lite_local.sh             # 启动单机版"
            echo "  bash start_lite_local.sh all         # 启动完整版"
            echo "  bash start_lite_local.sh logs        # 查看 Web UI 日志"
            echo "  bash start_lite_local.sh logs qa_entry  # 查看 QA Entry 日志"
            echo "  bash start_lite_local.sh stop        # 停止所有服务"
            echo ""
            ;;
    esac
}

# ==================== 运行 ====================

main "$@"
