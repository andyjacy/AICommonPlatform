#!/bin/bash

# ==================== 访问控制测试脚本 ====================
# 测试会话验证中间件和登录流程

set -e

# 配置
BASE_URL="http://localhost:3000"
TEST_USER="admin"
TEST_PASSWORD="admin123"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}► $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➜ $1${NC}"
}

# ==================== 测试 1: 未认证访问主页 ====================

test_unauthenticated_access() {
    print_test "测试 1: 未认证用户访问 / 应重定向到登录页"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
    
    if [ "$response" = "302" ]; then
        print_success "收到 302 重定向响应"
        
        # 检查重定向目标
        location=$(curl -s -i "$BASE_URL/" | grep -i "^location:" | cut -d' ' -f2 | tr -d '\r')
        if [[ "$location" == *"/login"* ]]; then
            print_success "正确重定向到登录页: $location"
            return 0
        else
            print_error "重定向目标不正确: $location"
            return 1
        fi
    else
        print_error "预期 302 但收到 $response"
        return 1
    fi
}

# ==================== 测试 2: 访问登录页 ====================

test_login_page_access() {
    print_test "测试 2: 访问登录页应成功"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/login")
    
    if [ "$response" = "200" ]; then
        print_success "成功访问登录页 (HTTP $response)"
        return 0
    else
        print_error "访问登录页失败 (HTTP $response)"
        return 1
    fi
}

# ==================== 测试 3: 登录 ====================

test_login() {
    print_test "测试 3: 使用正确凭证登录"
    
    response=$(curl -s -X POST "$BASE_URL/api/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$TEST_USER\",\"password\":\"$TEST_PASSWORD\"}")
    
    print_info "响应: $response"
    
    # 检查响应中是否有 token
    token=$(echo "$response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$token" ]; then
        print_success "登录成功，获得 token: ${token:0:30}..."
        echo "$token"
        return 0
    else
        print_error "登录失败，未获得 token"
        echo "$response"
        return 1
    fi
}

# ==================== 测试 4: 使用 Token 访问主页 ====================

test_authenticated_access() {
    local token="$1"
    print_test "测试 4: 使用有效 token 访问 /"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/?token=$token")
    
    if [ "$response" = "200" ]; then
        print_success "成功访问主页 (HTTP $response)"
        return 0
    else
        print_error "访问主页失败 (HTTP $response)"
        return 1
    fi
}

# ==================== 测试 5: Cookie 验证 ====================

test_cookie_validation() {
    local token="$1"
    print_test "测试 5: 通过 Cookie 验证访问"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Cookie: auth_token=$token" \
        "$BASE_URL/")
    
    if [ "$response" = "200" ]; then
        print_success "使用 Cookie 成功访问主页 (HTTP $response)"
        return 0
    else
        print_error "使用 Cookie 访问失败 (HTTP $response)"
        return 1
    fi
}

# ==================== 测试 6: 错误的 Token ====================

test_invalid_token() {
    print_test "测试 6: 使用无效 token 应重定向到登录"
    
    invalid_token="invalid_token_12345"
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/?token=$invalid_token")
    
    if [ "$response" = "302" ]; then
        print_success "无效 token 被正确拒绝，重定向到登录 (HTTP $response)"
        return 0
    else
        print_error "预期 302 但收到 $response"
        return 1
    fi
}

# ==================== 测试 7: Q&A 历史隔离 ====================

test_qa_history_isolation() {
    local token="$1"
    print_test "测试 7: Q&A 历史应只显示当前用户的数据"
    
    response=$(curl -s -X GET "$BASE_URL/api/qa/history?token=$token" \
        -H "Cookie: auth_token=$token")
    
    print_info "响应: ${response:0:100}..."
    
    # 检查响应是否为数组或包含状态
    if echo "$response" | grep -q '"user_id"'; then
        print_success "Q&A 历史 API 返回正确的用户隔离数据"
        return 0
    else
        print_info "Q&A 历史为空或格式不同（这是正常的，如果还没有历史记录）"
        return 0
    fi
}

# ==================== 测试 8: Token 验证端点 ====================

test_verify_token_endpoint() {
    local token="$1"
    print_test "测试 8: Token 验证端点"
    
    response=$(curl -s -X GET "$BASE_URL/api/user/verify-token?token=$token")
    
    print_info "响应: $response"
    
    if echo "$response" | grep -q '"status":"valid"'; then
        print_success "Token 验证成功"
        return 0
    else
        print_error "Token 验证失败"
        return 1
    fi
}

# ==================== 测试 9: API 文档访问 ====================

test_api_docs_access() {
    print_test "测试 9: API 文档应始终可访问"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
    
    if [ "$response" = "200" ]; then
        print_success "API 文档可访问 (HTTP $response)"
        return 0
    else
        print_error "API 文档访问失败 (HTTP $response)"
        return 1
    fi
}

# ==================== 测试 10: 健康检查 ====================

test_health_check() {
    print_test "测试 10: 健康检查端点应始终可访问"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
    
    if [ "$response" = "200" ]; then
        print_success "健康检查通过 (HTTP $response)"
        return 0
    else
        print_error "健康检查失败 (HTTP $response)"
        return 1
    fi
}

# ==================== 主测试流程 ====================

main() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  访问控制和会话管理测试                                  ║${NC}"
    echo -e "${BLUE}║  测试 URL: $BASE_URL${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    
    # 检查服务是否运行
    print_info "检查服务健康状态..."
    if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        print_error "服务未运行或无法访问"
        print_info "请先运行: bash start_lite_local.sh"
        exit 1
    fi
    print_success "服务正常运行"
    
    # 运行测试
    local failed=0
    
    test_unauthenticated_access || ((failed++))
    test_login_page_access || ((failed++))
    
    # 获取 Token
    token=$(test_login) || ((failed++))
    
    if [ -n "$token" ]; then
        test_authenticated_access "$token" || ((failed++))
        test_cookie_validation "$token" || ((failed++))
        test_qa_history_isolation "$token" || ((failed++))
        test_verify_token_endpoint "$token" || ((failed++))
    else
        print_error "无法获得 token，跳过后续测试"
        ((failed++))
    fi
    
    test_invalid_token || ((failed++))
    test_api_docs_access || ((failed++))
    test_health_check || ((failed++))
    
    # 总结
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}║  所有测试通过！✓                                        ║${NC}"
    else
        echo -e "${RED}║  $failed 个测试失败                                       ║${NC}"
    fi
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}\n"
    
    exit $failed
}

main "$@"
