#!/bin/bash

# ========================================
# SSH快速修复脚本
# 在阿里云VNC/Web终端中直接复制粘贴执行
# ========================================

echo "🔧 SSH快速诊断和修复"
echo "========================================="
echo ""

# 1. 基本诊断
echo "📋 当前状态:"
echo "  SSH服务: $(systemctl is-active sshd 2>/dev/null || echo '未知')"
echo "  SSH进程: $(pgrep sshd > /dev/null && echo '运行中' || echo '已停止')"
echo "  监听22: $(ss -tlnp 2>/dev/null | grep -q :22 && echo '是' || echo '否')"
echo ""

# 2. 尝试启动SSH
echo "🚀 启动SSH服务..."
systemctl start sshd 2>/dev/null || service sshd start 2>/dev/null || /usr/sbin/sshd

# 3. 启用自启动
echo "✓ 启用自启动..."
systemctl enable sshd 2>/dev/null || true

# 4. 重启SSH
echo "✓ 重启SSH..."
systemctl restart sshd 2>/dev/null || service sshd restart 2>/dev/null

sleep 2

# 5. 验证
echo ""
echo "✅ 修复完成，当前状态:"
echo "  SSH服务: $(systemctl is-active sshd 2>/dev/null || echo '未知')"
echo "  监听22: $(ss -tlnp 2>/dev/null | grep -q :22 && echo '✓' || echo '✗')"
echo ""

# 6. 显示监听信息
echo "📊 详细信息:"
ss -tlnp 2>/dev/null | grep -E "^|:22" || netstat -tlnp 2>/dev/null | grep :22 || echo "  (无法获取监听信息)"

echo ""
echo "测试: 在本地Mac执行以下命令检查连接"
echo "  sshpass -p '65,UaTzA\$9kAsny' ssh -o StrictHostKeyChecking=no root@47.100.35.44 'date'"
