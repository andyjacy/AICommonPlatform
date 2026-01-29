#!/bin/bash

# 测试 PUT 请求，重现 422 错误

echo "🔍 开始测试 LLM 模型更新..."
echo ""

# 测试1：成功的 PUT 请求（已知有效）
echo "✅ 测试1：已知有效的 PUT 请求"
curl -i -X PUT http://localhost:3000/api/llm/models/2 \
  -H "Content-Type: application/json" \
  -d '{"provider":"OpenAI","model_type":"api","temperature":0.8}' 2>/dev/null | head -20
echo ""
echo ""

# 测试2：包含 null 值的请求
echo "⚠️  测试2：包含 null 值的请求"
curl -i -X PUT http://localhost:3000/api/llm/models/2 \
  -H "Content-Type: application/json" \
  -d '{"provider":"OpenAI","model_type":"api","temperature":0.8,"api_key":null}' 2>/dev/null | head -20
echo ""
echo ""

# 测试3：包含额外字段的请求
echo "⚠️  测试3：包含额外字段的请求"
curl -i -X PUT http://localhost:3000/api/llm/models/2 \
  -H "Content-Type: application/json" \
  -d '{"provider":"OpenAI","model_type":"api","temperature":0.8,"invalid_field":"test"}' 2>/dev/null | head -20
echo ""
echo ""

echo "🔍 现在检查 docker logs..."
docker-compose logs web_ui 2>&1 | grep -A 5 -B 5 "\[DEBUG\]\|\[422"
