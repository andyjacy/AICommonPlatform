#!/bin/bash

# AI Common Platform - 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数定义
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# 处理命令
case "${1:-up}" in
    up)
        print_info "启动所有容器..."
        docker-compose up -d
        print_info "容器启动完成"
        print_info "等待服务就绪..."
        sleep 10
        print_info ""
        print_info "服务地址:"
        print_info "  QA Entry Service: http://localhost:8001"
        print_info "  Prompt Service: http://localhost:8002"
        print_info "  RAG Service: http://localhost:8003"
        print_info "  Agent Service: http://localhost:8004"
        print_info "  Integration Service: http://localhost:8005"
        print_info "  LLM Service: http://localhost:8006"
        print_info "  Prometheus: http://localhost:9090"
        print_info "  Grafana: http://localhost:3000 (admin/admin)"
        print_info ""
        print_info "查看日志: docker-compose logs -f"
        ;;
    
    down)
        print_info "停止所有容器..."
        docker-compose down
        print_info "容器已停止"
        ;;
    
    restart)
        print_info "重启所有容器..."
        docker-compose restart
        print_info "容器已重启"
        ;;
    
    logs)
        print_info "显示日志..."
        docker-compose logs -f ${2:-}
        ;;
    
    clean)
        print_warning "清理所有数据（包括数据库和缓存）..."
        read -p "确认？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            print_info "清理完成"
        else
            print_info "已取消"
        fi
        ;;
    
    test)
        print_info "运行API测试..."
        python3 scripts/test_api.py
        ;;
    
    ps)
        print_info "显示运行中的容器..."
        docker-compose ps
        ;;
    
    *)
        echo "用法: $0 {up|down|restart|logs|clean|test|ps}"
        echo ""
        echo "命令说明:"
        echo "  up       启动所有容器"
        echo "  down     停止所有容器"
        echo "  restart  重启所有容器"
        echo "  logs     显示容器日志"
        echo "  clean    清理所有数据（危险！）"
        echo "  test     运行API测试"
        echo "  ps       显示运行中的容器"
        exit 1
        ;;
esac
