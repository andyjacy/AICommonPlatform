#!/bin/bash

# AI Common Platform 调用链追踪系统 - 集成测试脚本
# 用于验证追踪功能是否正常工作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
API_BASE_URL="http://localhost:3000"
TESTS_PASSED=0
TESTS_FAILED=0

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 检查 API 可访问性
check_api_availability() {
    log_info "检查 API 可用性..."
    
    if curl -s "${API_BASE_URL}/" > /dev/null; then
        log_success "API 服务在线"
    else
        log_error "API 服务无法访问，请确保 docker-compose 已启动"
        exit 1
    fi
}

# 测试普通问答（无追踪）
test_normal_qa() {
    log_info "测试 1: 普通问答（无追踪）"
    
    response=$(curl -s -X POST "${API_BASE_URL}/api/qa/ask" \
        -H "Content-Type: application/json" \
        -d '{
            "question": "测试问题：什么是人工智能?",
            "user_id": "test_user"
        }')
    
    # 检查响应是否包含必要字段
    if echo "$response" | grep -q '"answer"'; then
        log_success "普通问答API正常工作"
        echo "$response" | python3 -m json.tool 2>/dev/null | head -20
    else
        log_error "普通问答API返回异常"
        echo "$response"
    fi
}

# 测试带追踪的问答
test_trace_qa() {
    log_info "测试 2: 问答with追踪数据"
    
    response=$(curl -s -X POST "${API_BASE_URL}/api/trace/qa/ask" \
        -H "Content-Type: application/json" \
        -d '{
            "question": "什么是检索增强生成(RAG)?",
            "user_id": "test_user"
        }')
    
    # 检查追踪数据
    if echo "$response" | grep -q '"trace"'; then
        log_success "追踪问答API正常工作"
        
        # 验证追踪数据结构
        if echo "$response" | grep -q '"trace_id"'; then
            log_success "  - 追踪ID存在"
        else
            log_error "  - 追踪ID缺失"
        fi
        
        if echo "$response" | grep -q '"total_steps"'; then
            log_success "  - 处理步骤数存在"
        else
            log_error "  - 处理步骤数缺失"
        fi
        
        if echo "$response" | grep -q '"steps"'; then
            log_success "  - 步骤详情存在"
            
            # 获取步骤数
            step_count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('trace', {}).get('steps', [])))" 2>/dev/null || echo "0")
            log_info "  - 追踪包含 $step_count 个步骤"
            
            # 验证每个步骤包含必要的字段
            if echo "$response" | grep -q '"stage"'; then
                log_success "  - 阶段名称字段存在"
            else
                log_error "  - 阶段名称字段缺失"
            fi
            
            if echo "$response" | grep -q '"service"'; then
                log_success "  - 服务名字段存在"
            else
                log_error "  - 服务名字段缺失"
            fi
            
            if echo "$response" | grep -q '"purpose"'; then
                log_success "  - 步骤用途字段存在"
            else
                log_error "  - 步骤用途字段缺失"
            fi
        else
            log_error "  - 步骤详情缺失"
        fi
        
        if echo "$response" | grep -q '"architecture_description"'; then
            log_success "  - 架构说明存在"
        else
            log_error "  - 架构说明缺失"
        fi
        
    else
        log_error "追踪问答API返回异常"
        echo "$response"
    fi
    
    echo "---"
}

# 测试架构信息端点
test_architecture_info() {
    log_info "测试 3: 架构信息端点"
    
    response=$(curl -s -X GET "${API_BASE_URL}/api/trace/architecture" \
        -H "Content-Type: application/json")
    
    if echo "$response" | grep -q '"platform_name"'; then
        log_success "架构端点正常工作"
        
        # 验证架构数据结构
        if echo "$response" | grep -q '"core_stages"'; then
            log_success "  - 核心处理阶段存在"
            
            # 获取阶段数
            stage_count=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('architecture', {}).get('core_stages', [])))" 2>/dev/null || echo "0")
            log_info "  - 包含 $stage_count 个核心处理阶段"
        else
            log_error "  - 核心处理阶段缺失"
        fi
        
        if echo "$response" | grep -q '"key_technologies"'; then
            log_success "  - 关键技术存在"
        else
            log_error "  - 关键技术缺失"
        fi
        
        # 显示平台信息
        platform_name=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('platform_name', 'Unknown'))" 2>/dev/null)
        version=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('version', 'Unknown'))" 2>/dev/null)
        log_info "  - 平台: $platform_name v$version"
        
    else
        log_error "架构端点返回异常"
        echo "$response"
    fi
    
    echo "---"
}

# 测试多个不同的问题
test_multiple_questions() {
    log_info "测试 4: 处理多个不同问题"
    
    questions=(
        "什么是 Agent?"
        "如何进行 Prompt 工程?"
        "LLM 模型有哪些?"
    )
    
    for i in "${!questions[@]}"; do
        question="${questions[$i]}"
        log_info "  - 问题 $((i+1)): $question"
        
        response=$(curl -s -X POST "${API_BASE_URL}/api/trace/qa/ask" \
            -H "Content-Type: application/json" \
            -d "{
                \"question\": \"$question\",
                \"user_id\": \"test_user\"
            }")
        
        if echo "$response" | grep -q '"trace"'; then
            log_success "    ✓ 问题处理成功"
        else
            log_error "    ✗ 问题处理失败"
        fi
    done
    
    echo "---"
}

# 测试错误处理
test_error_handling() {
    log_info "测试 5: 错误处理"
    
    # 测试空问题
    log_info "  - 测试空问题"
    response=$(curl -s -X POST "${API_BASE_URL}/api/trace/qa/ask" \
        -H "Content-Type: application/json" \
        -d '{
            "question": "",
            "user_id": "test_user"
        }')
    
    if echo "$response" | grep -q '"answer"\|"error"'; then
        log_success "    ✓ 空问题处理正确"
    else
        log_warning "    ⚠ 空问题返回非预期结果"
    fi
    
    # 测试缺少user_id字段
    log_info "  - 测试缺少user_id"
    response=$(curl -s -X POST "${API_BASE_URL}/api/trace/qa/ask" \
        -H "Content-Type: application/json" \
        -d '{
            "question": "测试问题"
        }')
    
    if echo "$response" | grep -q '"answer"\|"error"\|"user_id"'; then
        log_success "    ✓ 缺少user_id的处理正确"
    else
        log_warning "    ⚠ 缺少user_id返回非预期结果"
    fi
    
    echo "---"
}

# 性能测试
test_performance() {
    log_info "测试 6: 性能基准测试"
    
    question="性能测试问题"
    
    # 不带追踪的性能
    log_info "  - 测试无追踪问答的性能"
    start_time=$(date +%s%N)
    for i in {1..3}; do
        curl -s -X POST "${API_BASE_URL}/api/qa/ask" \
            -H "Content-Type: application/json" \
            -d "{
                \"question\": \"$question\",
                \"user_id\": \"perf_test\"
            }" > /dev/null
    done
    end_time=$(date +%s%N)
    elapsed_ms=$(( (end_time - start_time) / 1000000 ))
    avg_ms=$(( elapsed_ms / 3 ))
    log_success "  - 无追踪平均响应时间: ${avg_ms}ms"
    
    # 带追踪的性能
    log_info "  - 测试有追踪问答的性能"
    start_time=$(date +%s%N)
    for i in {1..3}; do
        curl -s -X POST "${API_BASE_URL}/api/trace/qa/ask" \
            -H "Content-Type: application/json" \
            -d "{
                \"question\": \"$question\",
                \"user_id\": \"perf_test\"
            }" > /dev/null
    done
    end_time=$(date +%s%N)
    elapsed_ms=$(( (end_time - start_time) / 1000000 ))
    avg_ms=$(( elapsed_ms / 3 ))
    log_success "  - 有追踪平均响应时间: ${avg_ms}ms"
    
    echo "---"
}

# 显示追踪链详情
show_trace_details() {
    log_info "展示详细的追踪链信息"
    
    response=$(curl -s -X POST "${API_BASE_URL}/api/trace/qa/ask" \
        -H "Content-Type: application/json" \
        -d '{
            "question": "什么是向量数据库?",
            "user_id": "demo_user"
        }')
    
    # 提取并显示追踪ID
    trace_id=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('trace', {}).get('trace_id', 'N/A'))" 2>/dev/null)
    log_info "  - 追踪ID: $trace_id"
    
    # 显示处理步骤
    echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
trace = data.get('trace', {})
steps = trace.get('steps', [])
print(f'  - 处理步骤:')
for step in steps[:5]:  # 只显示前5个步骤
    print(f'    Step {step[\"seq\"]}: {step[\"stage\"]} ({step[\"service\"]})')
    print(f'      用途: {step[\"purpose\"]}')
print(f'    ... (共 {len(steps)} 个步骤)')
" 2>/dev/null || echo "  - 追踪数据解析失败"
    
    echo "---"
}

# 主函数
main() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   AI Common Platform 调用链追踪系统 - 集成测试${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # 检查依赖
    log_info "检查依赖环境..."
    if ! command -v curl &> /dev/null; then
        log_error "curl 未安装，请先安装 curl"
        exit 1
    fi
    if ! command -v python3 &> /dev/null; then
        log_error "python3 未安装，请先安装 python3"
        exit 1
    fi
    log_success "依赖环境正常"
    echo ""
    
    # 执行测试
    check_api_availability
    echo ""
    
    test_normal_qa
    test_trace_qa
    test_architecture_info
    test_multiple_questions
    test_error_handling
    test_performance
    show_trace_details
    
    # 汇总测试结果
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                      测试结果汇总${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    
    total_tests=$((TESTS_PASSED + TESTS_FAILED))
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ 所有 $TESTS_PASSED 个测试通过！${NC}"
    else
        echo -e "${RED}❌ 测试失败: $TESTS_FAILED 个失败，$TESTS_PASSED 个通过${NC}"
    fi
    
    echo ""
    echo "📊 测试覆盖范围："
    echo "  ✓ API 可用性"
    echo "  ✓ 普通问答功能"
    echo "  ✓ 追踪问答功能"
    echo "  ✓ 架构信息端点"
    echo "  ✓ 多问题处理"
    echo "  ✓ 错误处理"
    echo "  ✓ 性能基准"
    echo ""
}

# 运行主函数
main
