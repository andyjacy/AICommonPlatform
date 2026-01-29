#!/bin/bash

# 部署诊断脚本

echo "🔍 阿里云部署诊断"
echo "=================================================="
echo ""

REMOTE_IP="47.100.35.44"

echo "📊 诊断结果:"
echo ""

# 1. 检查网络连通性
echo "1. 网络连通性测试"
if timeout 3 ping -c 1 $REMOTE_IP >/dev/null 2>&1; then
  echo "   ✅ 服务器IP可ping通"
else
  echo "   ❌ 无法ping通服务器 ($REMOTE_IP)"
  echo "   💡 可能原因："
  echo "      - 防火墙阻止ICMP"
  echo "      - 网络连接问题"
  echo "      - 云服务器配置"
fi

echo ""

# 2. 检查SSH连接
echo "2. SSH连接测试 (端口22)"
if timeout 3 sshpass -p '65,UaTzA$9kAsny' ssh -o ConnectTimeout=2 -o StrictHostKeyChecking=no root@$REMOTE_IP "echo OK" 2>/dev/null | grep -q OK; then
  echo "   ✅ SSH连接正常"
else
  echo "   ⚠️  SSH连接可能有问题"
  echo "   💡 尝试方法："
  echo "      ssh -o ConnectTimeout=10 root@$REMOTE_IP"
fi

echo ""

# 3. 检查HTTP端口9000
echo "3. Web UI端口测试 (端口9000)"
response=$(curl -s -m 2 -w "%{http_code}" -o /dev/null http://$REMOTE_IP:9000 2>/dev/null)
if [ "$response" = "200" ] || [ "$response" = "302" ] || [ "$response" = "000" ]; then
  echo "   ✅ Web UI端口可访问 (HTTP $response)"
else
  echo "   ⚠️  Web UI端口 ($response)"
  echo "   💡 检查防火墙是否开放9000端口"
fi

echo ""

# 4. 检查QA服务端口8001
echo "4. QA服务端口测试 (端口8001)"
response=$(curl -s -m 2 -w "%{http_code}" -o /dev/null http://$REMOTE_IP:8001/docs 2>/dev/null)
if [ "$response" = "200" ]; then
  echo "   ✅ QA服务正常 (HTTP $response)"
else
  echo "   ⏳ QA服务可能还在启动 (HTTP $response)"
fi

echo ""

echo "=================================================="
echo ""
echo "💡 快速修复建议："
echo ""
echo "1️⃣ 如果SSH连接超时:"
echo "   • 增加连接超时时间"
echo "   • 检查云服务器安全组设置"
echo "   • 确保密码正确: 65,UaTzA\$9kAsny"
echo ""
echo "2️⃣ 如果HTTP端口无法访问:"
echo "   • 远程SSH连接后执行: docker-compose ps"
echo "   • 检查容器是否运行"
echo "   • 查看日志: docker logs ai_web_ui"
echo ""
echo "3️⃣ 远程SSH快速连接:"
echo "   ssh -o ConnectTimeout=10 root@47.100.35.44"
echo ""
echo "4️⃣ 或使用sshpass (需要已安装):"
echo "   sshpass -p '65,UaTzA\$9kAsny' ssh root@47.100.35.44"
echo ""
