# 访问控制 (Access Control)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、NIST标准及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**访问控制 (Access Control)** 是系统安全的核心机制，用于决定"谁可以访问什么资源、执行什么操作"。它是防止未授权访问的第一道防线，涵盖从操作系统到应用程序的各个层面。

```
┌─────────────────────────────────────────────────────────────────┐
│                   访问控制三要素 (AAA)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │ Authentication│  │ Authorization│  │   Accounting │         │
│   │    身份认证    │  │    授权      │  │    审计      │         │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
│          │                   │                   │             │
│          ▼                   ▼                   ▼             │
│      "你是谁？"          "你能做什么？"       "你做了什么？"      │
│                                                                 │
│   访问控制位于 Authorization 阶段，基于身份决定权限             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 访问控制模型

### 1. RBAC (Role-Based Access Control) - 基于角色的访问控制

RBAC 是目前企业应用中最主流的访问控制模型。用户通过被分配角色来获得权限，权限与角色关联而非直接与用户关联。

```
┌─────────────────────────────────────────────────────────────────┐
│                   RBAC 模型架构                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│     User ──────▶ Role ──────▶ Permission ──────▶ Resource      │
│     用户          角色           权限              资源          │
│                                                                 │
│   ┌─────────┐    ┌─────────┐    ┌───────────┐    ┌─────────┐   │
│   │  Alice  │───▶│  Admin  │───▶│  create   │───▶│ /api/*  │   │
│   │  Bob    │───▶│  Editor │───▶│  read     │───▶│ /docs/* │   │
│   │  Carol  │───▶│  Viewer │───▶│  update   │    │ /reports│   │
│   └─────────┘    └─────────┘    │  delete   │    └─────────┘   │
│                                 └───────────┘                  │
│                                                                 │
│   角色层次结构 (Role Hierarchy):                                 │
│                                                                 │
│            Admin (完整权限)                                      │
│              │                                                   │
│        Editor (读写权限)                                         │
│              │                                                   │
│        Viewer (只读权限)                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Linux sudoers RBAC 配置示例：**

```bash
# /etc/sudoers 文件配置

# 用户别名定义
User_Alias ADMINS = alice, bob
User_Alias DEVELOPERS = carol, dave

# 命令别名定义
Cmnd_Alias SOFTWARE_INSTALL = /usr/bin/apt-get install *
Cmnd_Alias SYSTEMCTL = /usr/bin/systemctl *
Cmnd_Alias LOGS = /usr/bin/journalctl *, /var/log/*

# 权限规则
ADMINS      ALL=(ALL:ALL) ALL                              # 管理员全权限
DEVELOPERS  ALL=(ALL) NOPASSWD: SOFTWARE_INSTALL          # 开发者可安装软件
DEVELOPERS  ALL=(ALL) SYSTEMCTL                           # 开发者管理服务
%operators  ALL=(ALL) LOGS                                # operators组查看日志

# 限制规则
Defaults    env_reset                                     # 重置环境变量
Defaults    logfile="/var/log/sudo.log"                   # 记录sudo使用
Defaults    timestamp_timeout=10                          # 密码缓存10分钟
```

### 2. ABAC (Attribute-Based Access Control) - 基于属性的访问控制

ABAC 根据主体、资源、环境的属性动态决策，是最灵活的访问控制模型。

```
┌─────────────────────────────────────────────────────────────────┐
│                   ABAC 决策流程                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   策略规则: IF (条件) THEN (允许/拒绝)                           │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  主体属性 (Subject)                                      │   │
│   │  • user.role = "manager"                                 │   │
│   │  • user.department = "finance"                           │   │
│   │  • user.clearance = "secret"                             │   │
│   │  • user.location = "office"                              │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  资源属性 (Resource)                                     │   │
│   │  • resource.type = "document"                            │   │
│   │  • resource.owner = "alice@company.com"                  │   │
│   │  • resource.department = "finance"                       │   │
│   │  • resource.classification = "confidential"              │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  环境属性 (Environment)                                  │   │
│   │  • time.hour = 14 (工作时间)                             │   │
│   │  • day = "weekday"                                       │   │
│   │  • network = "corporate"                                 │   │
│   │  • threat_level = "low"                                  │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│   决策结果: ALLOW / DENY                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3. ACL (Access Control List) - 访问控制列表

ACL 是最直接的访问控制机制，直接定义每个资源可被哪些主体访问。

```
┌─────────────────────────────────────────────────────────────────┐
│                   ACL 结构对比                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Unix 文件权限 (简化ACL):                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  -rwxr-xr-- 1 alice developers 4096 Mar 30 10:00 file   │   │
│   │   │││││││││                                               │   │
│   │   │││││││└┴─ 其他用户权限 (r--)                           │   │
│   │   │││││└─┴─── 所属组权限 (r-x)                            │   │
│   │   ││└─┴────── 所有者权限 (rwx)                            │   │
│   │   └────────── 文件类型 (- = 普通文件)                     │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   Windows ACL (扩展ACL):                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  File: C:\Documents\report.pdf                           │   │
│   │                                                         │   │
│   │  User: DOMAIN\Alice          Allow  Full Control        │   │
│   │  User: DOMAIN\Bob            Allow  Read, Write         │   │
│   │  Group: DOMAIN\Finance        Allow  Read                │   │
│   │  Group: DOMAIN\Guests         Deny   All                 │   │
│   │                                                         │   │
│   │  特殊权限:                                               │   │
│   │  • 继承控制 (Inheritance)                                │   │
│   │  • 审计设置 (Auditing)                                   │   │
│   │  • 所有者变更 (Take Ownership)                           │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**POSIX ACL 配置示例：**

```bash
# 查看文件ACL
$ getfacl /path/to/file
# file: /path/to/file
# owner: alice
# group: developers
user::rwx
user:bob:r-x          # 特定用户权限
group::r-x
group:finance:r--     # 特定组权限
mask::r-x
other::---

# 设置ACL
$ setfacl -m u:carol:rw /path/to/file      # 给用户carol读写权限
$ setfacl -m g:auditors:r /path/to/file    # 给auditors组只读权限
$ setfacl -x u:bob /path/to/file           # 移除用户bob的ACL

# 默认ACL (新文件继承)
$ setfacl -d -m g:staff:rwx /shared/dir

# 递归设置
$ setfacl -R -m g:web:rx /var/www/html
```

---

## Linux Capabilities

Capabilities 将 root 权限细分为多个独立单元，实现更细粒度的权限控制。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Linux Capabilities 架构                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   传统root权限:                                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  UID 0 = 所有特权 (ALL PRIVILEGES)                       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│   Capabilities 细粒度拆分:                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  CAP_NET_ADMIN    - 网络配置 (ifconfig, iptables)        │   │
│   │  CAP_SYS_ADMIN    - 系统管理 (mount, swapon)             │   │
│   │  CAP_CHOWN        - 修改文件所有者                       │   │
│   │  CAP_KILL         - 发送信号给任意进程                   │   │
│   │  CAP_NET_BIND_SERVICE - 绑定特权端口 (<1024)             │   │
│   │  CAP_SETUID       - 修改进程UID                          │   │
│   │  CAP_SYS_PTRACE   - 调试其他进程                         │   │
│   │  CAP_IPC_LOCK     - 锁定共享内存                         │   │
│   │  ... (共40+个capability)                                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Capabilities 使用示例：**

```bash
# 查看进程的capabilities
$ cat /proc/1/status | grep Cap
CapInh: 0000000000000000
CapPrm: 000001ffffffffff
CapEff: 000001ffffffffff
CapBnd: 000001ffffffffff
CapAmb: 0000000000000000

# 给可执行文件添加capability
$ sudo setcap cap_net_bind_service=+ep /usr/bin/my-server
# =+ep 表示: = (设置), + (添加), e (有效), p (允许)

# 查看文件的capabilities
$ getcap /usr/bin/my-server
/usr/bin/my-server = cap_net_bind_service+eip

# 在Docker中使用capabilities
$ docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myimage

# 移除capability
$ sudo setcap -r /usr/bin/my-server
```

---

## SELinux 与 AppArmor

### SELinux (Security-Enhanced Linux)

SELinux 是 MAC (Mandatory Access Control) 的实现，通过安全策略强制限制进程行为。

```
┌─────────────────────────────────────────────────────────────────┐
│                   SELinux 架构                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   SELinux 模式:                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │   Enforcing │  │  Permissive │  │   Disabled  │            │
│   │   (强制)    │  │  (宽容)     │  │   (禁用)    │            │
│   │             │  │             │  │             │            │
│   │ 拒绝违规操作 │  │ 记录但不阻止│  │ 完全关闭    │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│   安全上下文 (Security Context):                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  user:role:type:level                                    │   │
│   │  system_u:system_r:httpd_t:s0                            │   │
│   │                                                         │   │
│   │  user_u:user_r:user_t:s0                                 │   │
│   │  ↑     ↑      ↑     ↑                                    │   │
│   │  用户  角色   类型  安全级别                              │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   类型强制 (Type Enforcement):                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  httpd_t (Apache进程)  ────────▶  httpd_sys_content_t   │   │
│   │       │                              (Web内容)          │   │
│   │       └───────────────────────▶  httpd_sys_script_t     │   │
│   │                                      (CGI脚本)          │   │
│   │       ╳                                                    │   │
│   │       └───────────────────────▶  shadow_t                │   │
│   │                                      (/etc/shadow)       │   │
│   │                               [拒绝访问 - 违反策略]       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**SELinux 命令示例：**

```bash
# 查看当前SELinux状态
$ sestatus
SELinux status:                 enabled
SELinuxfs mount:                /sys/fs/selinux
SELinux root directory:         /etc/selinux
Loaded policy name:             targeted
Current mode:                   enforcing
Mode from config file:          enforcing

# 查看文件的安全上下文
$ ls -Z /var/www/html/
unconfined_u:object_r:httpd_sys_content_t:s0 index.html

# 查看进程的SELinux上下文
$ ps auxZ | grep httpd
system_u:system_r:httpd_t:s0    root     1234  ...

# 修改文件上下文
$ semanage fcontext -a -t httpd_sys_content_t "/web(/.*)?"
$ restorecon -Rv /web

# 查看SELinux日志
$ ausearch -m avc -ts recent
$ sealert -a /var/log/audit/audit.log

# 临时切换到宽容模式(排查问题时使用)
$ sudo setenforce 0
# 恢复强制模式
$ sudo setenforce 1
```

### AppArmor

AppArmor 是另一种 Linux 安全模块，通过路径名而非 inode 进行控制，配置更简单。

```bash
# AppArmor profile 示例 (/etc/apparmor.d/usr.bin.nginx)
#include <tunables/global>

/usr/sbin/nginx {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  
  capability net_bind_service,
  capability setgid,
  capability setuid,
  
  # 可执行文件
  /usr/sbin/nginx mr,
  
  # 配置文件
  /etc/nginx/** r,
  
  # 日志文件
  /var/log/nginx/** rw,
  
  # Web内容
  /var/www/** r,
  
  # PID文件
  /run/nginx.pid rwk,
  
  # 拒绝访问其他区域
  deny /etc/shadow r,
  deny /root/** r,
}

# AppArmor 管理命令
$ aa-status                    # 查看所有profile状态
$ aa-enforce /usr/sbin/nginx   # 启用强制模式
$ aa-complain /usr/sbin/nginx  # 启用抱怨模式
$ aa-disable /usr/sbin/nginx   # 禁用profile
$ apparmor_parser -r /etc/apparmor.d/usr.bin.nginx  # 重新加载
```

---

## 最佳实践

```
┌─────────────────────────────────────────────────────────────────┐
│                   访问控制最佳实践                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ □ 权限设计原则                                                   │
│   □ 最小权限原则 (Principle of Least Privilege)                │
│   □ 默认拒绝 (Default Deny)                                     │
│   □ 职责分离 (Separation of Duties)                            │
│   □ 需要知道 (Need-to-Know)                                    │
│                                                                 │
│ □ 实施建议                                                       │
│   □ 使用RBAC作为基础模型，复杂场景使用ABAC                      │
│   □ 定期审查和清理无用权限                                       │
│   □ 使用sudo而非直接root登录                                    │
│   □ 利用capabilities替代setuid程序                              │
│   □ 启用SELinux/AppArmor等强制访问控制                          │
│                                                                 │
│ □ 监控与审计                                                     │
│   □ 记录所有权限变更                                             │
│   □ 监控特权命令使用                                             │
│   □ 定期权限审计报告                                             │
│   □ 异常访问模式检测                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

### 常见问题

**Q1: RBAC和ABAC的主要区别是什么？**
> RBAC基于静态角色，用户通过角色获得权限，管理简单但不够灵活；ABAC基于动态属性（主体、资源、环境属性），可实现细粒度、上下文感知的访问控制，但复杂度高。实际中常结合使用：RBAC作为基础，ABAC处理特殊场景。

**Q2: 什么是最小权限原则？如何在Linux系统中实施？**
> 最小权限原则指只授予完成任务所需的最小权限集合。在Linux中实施：1) 使用普通用户而非root；2) 使用sudo精确控制特权命令；3) 使用capabilities替代setuid；4) 启用SELinux/AppArmor限制进程；5) 文件权限遵循umask设置。

**Q3: SELinux和AppArmor的区别？**
> 两者都是Linux安全模块(LSM)。SELinux基于inode和标签，使用Type Enforcement，策略严格但复杂，适合高安全环境；AppArmor基于路径名，配置简单直观，学习曲线平缓，适合一般企业环境。

**Q4: 什么是Capabilities？为什么要用它替代setuid？**
> Capabilities将root权限细分为40+个独立单元。相比setuid(给予程序完整root权限)，capabilities只授予特定权限（如CAP_NET_BIND_SERVICE只给绑定特权端口权限），大幅降低了安全风险。

---

## 相关概念

- [身份认证](../authentication.md) - 访问控制的前置步骤
- [授权](../authorization.md) - 权限分配机制
- [特权提升](./privilege-escalation.md) - 权限滥用攻击
- [审计日志](./audit-logging.md) - 访问控制审计

---

## 参考资料

1. NIST RBAC Standard (ANSI/INCITS 359-2004)
2. SELinux Project Documentation: https://selinuxproject.org/
3. AppArmor Documentation: https://gitlab.com/apparmor/apparmor/-/wikis/home
4. Linux Capabilities Man Page: capabilities(7)
5. "Linux Security" by Michael Boelen
