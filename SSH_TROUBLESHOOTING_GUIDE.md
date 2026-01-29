# 如何通过阿里云控制台访问服务器并修复SSH

## 方法 1️⃣：使用VNC远程连接（推荐）

1. **登陆阿里云控制台**
   - 访问 https://www.aliyun.com
   - 进入「轻量应用服务器」> 选择你的实例（IP: 47.100.35.44）

2. **打开VNC连接**
   - 点击实例右侧的「远程连接」
   - 选择「VNC远程连接」
   - 使用密码登陆（密码: 65,UaTzA$9kAsny）

3. **在VNC终端中执行诊断脚本**
   ```bash
   cd /tmp
   # 将诊断脚本内容复制粘贴进去，或用这个快速诊断
   systemctl status sshd
   ss -tlnp | grep :22
   systemctl restart sshd
   ```

---

## 方法 2️⃣：使用Web终端（如果VNC不可用）

1. 在阿里云控制台点击「远程连接」
2. 选择「Web远程连接」（如果可用）
3. 在Web终端中执行相同的诊断命令

---

## 快速诊断脚本（粘贴到终端执行）

```bash
#!/bin/bash
echo "=== SSH诊断 ==="
echo "1. SSH服务状态:"
systemctl is-active sshd

echo ""
echo "2. SSH监听状态:"
ss -tlnp | grep :22 || echo "未监听22端口"

echo ""
echo "3. SSH进程:"
ps aux | grep sshd | grep -v grep

echo ""
echo "4. 重启SSH:"
systemctl restart sshd
sleep 2

echo ""
echo "5. 重启后状态:"
systemctl is-active sshd && echo "✓ SSH已启动" || echo "✗ SSH启动失败"

echo ""
echo "6. 监听端口:"
ss -tlnp | grep :22
```

---

## 常见SSH问题及修复

### 问题1：SSH服务未启动
```bash
systemctl start sshd
systemctl enable sshd
```

### 问题2：SSH配置错误
```bash
# 检查配置
sshd -t  # 验证配置文件语法

# 重新启动
systemctl restart sshd
```

### 问题3：防火墙阻止了22端口
```bash
# 如果使用firewalld
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload

# 或检查iptables
iptables -L -n | grep 22
```

### 问题4：权限问题
```bash
# 修复SSH目录权限
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys

# 修复SSH配置权限
chmod 600 /etc/ssh/sshd_config
```

---

## 在VNC/Web终端中完整的修复步骤

```bash
# 1. 检查SSH状态
systemctl status sshd

# 2. 如果未运行，启动它
systemctl start sshd

# 3. 设置为开机自启
systemctl enable sshd

# 4. 验证配置
sshd -t

# 5. 重启SSH
systemctl restart sshd

# 6. 验证是否监听22端口
ss -tlnp | grep :22

# 7. 查看日志
journalctl -u sshd -n 50 --no-pager
```

---

## 如果上述都不行

尝试重启整个服务器：
```bash
# 在Web终端或VNC中执行
reboot
```

或在阿里云控制台中：
1. 选择实例
2. 点击「管理」> 「重启」

---

## 完成后验证SSH连接

从本地Mac执行：
```bash
sshpass -p '65,UaTzA$9kAsny' ssh -o StrictHostKeyChecking=no root@47.100.35.44 'date'
```

如果显示服务器时间，说明SSH已恢复！

然后可以运行镜像上传脚本：
```bash
bash /Users/zhao_/Documents/PRC/AI实践/AICommonPlatform/upload_amd64_images.sh
```
