#!/bin/bash

# SSH诊断和修复脚本
# 在阿里云服务器上（VNC或Web终端）运行此脚本

echo "🔍 SSH连接问题诊断"
echo "=================================================="
echo ""

# 1. 检查SSH服务状态
echo "1️⃣  SSH服务状态:"
systemctl status sshd | grep -E "Active|running"
echo ""

# 2. 检查SSH监听端口
echo "2️⃣  SSH监听端口:"
ss -tlnp | grep ssh || netstat -tlnp | grep ssh || echo "  ❌ 未找到SSH监听"
echo ""

# 3. 检查SSH配置
echo "3️⃣  SSH配置文件:"
if [ -f /etc/ssh/sshd_config ]; then
  echo "  ✓ 配置文件存在"
  echo "  Port: $(grep -v '^#' /etc/ssh/sshd_config | grep Port | head -1)"
  echo "  PermitRootLogin: $(grep -v '^#' /etc/ssh/sshd_config | grep PermitRootLogin | head -1)"
  echo "  PasswordAuthentication: $(grep -v '^#' /etc/ssh/sshd_config | grep PasswordAuthentication | head -1)"
else
  echo "  ❌ 配置文件不存在"
fi
echo ""

# 4. 检查防火墙
echo "4️⃣  防火墙状态:"
systemctl status firewalld 2>/dev/null | grep -E "Active|running" || echo "  firewalld 未启用"
echo ""

# 5. 检查iptables
echo "5️⃣  iptables SSH规则:"
iptables -L -n | grep -E "22|ssh" || echo "  (无特定规则)"
echo ""

# 6. 检查SSH日志
echo "6️⃣  最近的SSH日志错误:"
journalctl -u sshd -n 20 2>/dev/null | tail -10 || tail -10 /var/log/auth.log 2>/dev/null || echo "  (无法读取日志)"
echo ""

# 7. 重启SSH服务
echo "🔧 尝试重启SSH服务..."
systemctl restart sshd
sleep 2
systemctl status sshd | grep -E "Active|running" && echo "  ✓ SSH服务已重启" || echo "  ✗ 重启失败"
echo ""

# 8. 最终检查
echo "✅ 诊断完成"
echo ""
echo "如果SSH仍无法连接，尝试以下命令修复:"
echo ""
echo "# 确保SSH服务启用并启动"
echo "systemctl enable sshd"
echo "systemctl start sshd"
echo ""
echo "# 检查SSH进程"
echo "ps aux | grep sshd"
echo ""
echo "# 检查22端口是否真的在监听"
echo "ss -tlnp | grep :22"
echo ""
echo "# 查看完整的sshd日志"
echo "journalctl -u sshd -n 50 --no-pager"
