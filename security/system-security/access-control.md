# 访问控制 (Access Control)

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、NIST标准及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**访问控制 (Access Control)** 是系统安全的核心机制，用于决定"谁可以访问什么资源、执行什么操作"。系统级访问控制涵盖操作系统层面的权限管理，包括用户账户管理、文件权限控制、能力机制（Capabilities）、SELinux/AppArmor 等强制访问控制（MAC）机制，以及容器和云环境中的访问控制策略。

```
┌─────────────────────────────────────────────────────────────────┐
│                   访问控制模型层次                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  物理层访问控制                                          │  │
│   │  • 门禁系统、生物识别、监控                               │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  网络层访问控制                                          │  │
│   │  • 防火墙、ACL、VPN、网络分段                             │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  操作系统层访问控制                                      │  │
│   │  • DAC (自主访问控制): Unix 权限、Windows ACL            │  │
│   │  • MAC (强制访问控制): SELinux、AppArmor                 │  │
│   │  • RBAC (基于角色的访问控制)                             │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  应用层访问控制                                          │  │
│   │  • 认证授权、API 网关、服务网格                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  数据层访问控制                                          │  │
│   │  • 数据库权限、加密、数据脱敏                            │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心概念

### 访问控制模型

```
┌─────────────────────────────────────────────────────────────────┐
│                   访问控制模型对比                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   DAC (Discretionary Access Control) 自主访问控制               │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ • 资源所有者决定访问权限                                 │  │
│   │ • Unix 文件权限 (rwx)                                    │  │
│   │ • Windows ACL                                            │  │
│   │ • 灵活性高，但难以集中管理                               │  │
│   │                                                          │  │
│   │ 所有者: alice    组: developers    其他                  │  │
│   │   rwx              r-x               r--                 │  │
│   │   7                 5                 4   = 754          │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   MAC (Mandatory Access Control) 强制访问控制                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ • 系统强制实施访问策略，用户无法绕过                     │  │
│   │ • SELinux、AppArmor、Trusted Solaris                     │  │
│   │ • 安全性高，但配置复杂                                   │  │
│   │                                                          │  │
│   │ SELinux 标签示例:                                        │  │
│   │   用户: system_u  角色: system_r  类型: httpd_t          │  │
│   │   级别: s0:c0.c1023                                      │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   RBAC (Role-Based Access Control) 基于角色的访问控制         │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ • 权限与角色关联，用户分配角色                           │  │
│   │ • Kubernetes RBAC、AWS IAM                               │  │
│   │ • 简化管理，适合组织架构                                 │  │
│   │                                                          │  │
│   │ User ──▶ Role ──▶ Permission ──▶ Resource               │  │
│   │ alice ──▶ Admin ──▶ [read,write,delete] ──▶ /data/*     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   ABAC (Attribute-Based Access Control) 基于属性的访问控制    │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ • 基于主体、客体、环境属性动态决策                       │  │
│   │ • 细粒度、上下文感知                                     │  │
│   │ • AWS IAM Policy、XACML                                  │  │
│   │                                                          │  │
│   │ IF user.department == resource.department               │  │
│   │    AND time.hour BETWEEN 9 AND 18                       │  │
│   │ THEN ALLOW                                              │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 实现方式

### 1. Linux 文件权限与 ACL

```python
import os
import stat
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class Permission(Enum):
    """Unix 权限"""
    READ = 4
    WRITE = 2
    EXECUTE = 1
    NONE = 0

@dataclass
class FilePermissions:
    """文件权限结构"""
    owner_read: bool = False
    owner_write: bool = False
    owner_execute: bool = False
    group_read: bool = False
    group_write: bool = False
    group_execute: bool = False
    other_read: bool = False
    other_write: bool = False
    other_execute: bool = False
    
    def to_numeric(self) -> int:
        """转换为数字模式（如 755）"""
        owner = (self.owner_read * 4 + 
                self.owner_write * 2 + 
                self.owner_execute * 1)
        group = (self.group_read * 4 + 
                self.group_write * 2 + 
                self.group_execute * 1)
        other = (self.other_read * 4 + 
                self.other_write * 2 + 
                self.other_execute * 1)
        return owner * 100 + group * 10 + other
    
    @classmethod
    def from_numeric(cls, mode: int) -> 'FilePermissions':
        """从数字模式创建"""
        owner = (mode // 100) % 10
        group = (mode // 10) % 10
        other = mode % 10
        
        return cls(
            owner_read=bool(owner & 4),
            owner_write=bool(owner & 2),
            owner_execute=bool(owner & 1),
            group_read=bool(group & 4),
            group_write=bool(group & 2),
            group_execute=bool(group & 1),
            other_read=bool(other & 4),
            other_write=bool(other & 2),
            other_execute=bool(other & 1),
        )
    
    def to_symbolic(self) -> str:
        """转换为符号模式（如 rwxr-xr-x）"""
        return (
            ('r' if self.owner_read else '-') +
            ('w' if self.owner_write else '-') +
            ('x' if self.owner_execute else '-') +
            ('r' if self.group_read else '-') +
            ('w' if self.group_write else '-') +
            ('x' if self.group_execute else '-') +
            ('r' if self.other_read else '-') +
            ('w' if self.other_write else '-') +
            ('x' if self.other_execute else '-')
        )


class SecureFileManager:
    """安全文件管理器"""
    
    # 安全 umask：新文件默认权限
    SECURE_FILE_UMASK = 0o077  # 仅所有者可读写
    SECURE_DIR_UMASK = 0o077
    
    @staticmethod
    def set_secure_umask():
        """设置安全 umask"""
        os.umask(SecureFileManager.SECURE_FILE_UMASK)
    
    @staticmethod
    def create_secure_file(filepath: str, content: bytes,
                          owner_only: bool = True) -> None:
        """
        安全创建文件
        - 使用原子写入
        - 设置最小权限
        """
        # 先设置 umask
        old_umask = os.umask(0o077 if owner_only else 0o022)
        
        try:
            # 创建临时文件
            fd, temp_path = tempfile.mkstemp(
                dir=os.path.dirname(filepath) or '.'
            )
            try:
                os.write(fd, content)
                os.close(fd)
                
                # 原子移动
                os.replace(temp_path, filepath)
                
                # 显式设置权限
                if owner_only:
                    os.chmod(filepath, 0o600)  # -rw-------
                else:
                    os.chmod(filepath, 0o644)  # -rw-r--r--
                    
            except Exception:
                os.close(fd)
                os.unlink(temp_path)
                raise
        finally:
            os.umask(old_umask)
    
    @staticmethod
    def secure_directory_traversal(base_path: str, 
                                    target_path: str) -> Optional[str]:
        """
        安全的目录遍历检查
        防止路径遍历攻击
        """
        try:
            base = Path(base_path).resolve()
            target = (base / target_path).resolve()
            
            # 确保目标路径在基目录内
            if not str(target).startswith(str(base)):
                return None
            
            return str(target)
        except (ValueError, RuntimeError):
            return None
    
    @staticmethod
    def set_acl(filepath: str, user_perms: dict, group_perms: dict) -> bool:
        """
        设置文件 ACL (Access Control List)
        需要系统支持 setfacl/getfacl
        """
        try:
            # 设置用户 ACL
            for user, perm in user_perms.items():
                subprocess.run(
                    ['setfacl', '-m', f'u:{user}:{perm}', filepath],
                    check=True,
                    capture_output=True
                )
            
            # 设置组 ACL
            for group, perm in group_perms.items():
                subprocess.run(
                    ['setfacl', '-m', f'g:{group}:{perm}', filepath],
                    check=True,
                    capture_output=True
                )
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def check_file_ownership(filepath: str, 
                            expected_uid: int = None) -> Tuple[bool, dict]:
        """检查文件所有权和权限"""
        try:
            stat_info = os.stat(filepath)
            
            result = {
                'exists': True,
                'uid': stat_info.st_uid,
                'gid': stat_info.st_gid,
                'mode': stat.S_IMODE(stat_info.st_mode),
                'permissions': FilePermissions.from_numeric(
                    stat.S_IMODE(stat_info.st_mode)
                ),
                'is_writable_by_others': bool(stat_info.st_mode & stat.S_IWOTH),
                'is_readable_by_others': bool(stat_info.st_mode & stat.S_IROTH),
            }
            
            # 安全检查
            is_secure = (
                not result['is_writable_by_others'] and
                not (expected_uid is not None and result['uid'] != expected_uid)
            )
            
            return is_secure, result
            
        except FileNotFoundError:
            return False, {'exists': False}


# 最小权限配置示例
MINIMAL_PERMISSIONS = {
    'config_files': 0o600,      # -rw-------
    'log_files': 0o640,         # -rw-r-----
    'data_files': 0o600,        # -rw-------
    'executable_scripts': 0o700, # -rwx------
    'directories': 0o750,       # drwxr-x---
    'public_directories': 0o755, # drwxr-xr-x
}
```

### 2. Linux Capabilities

```python
"""
Linux Capabilities 管理
Capabilities 将 root 权限细分为多个独立的能力
"""

import ctypes
import ctypes.util
import os
from enum import IntEnum

class Capability(IntEnum):
    """Linux Capabilities"""
    CAP_CHOWN = 0              # 修改文件所有者
    CAP_DAC_OVERRIDE = 1       # 绕过文件权限检查
    CAP_DAC_READ_SEARCH = 2    # 绕过文件读/搜索权限
    CAP_FOWNER = 3             # 绕过文件所有权检查
    CAP_FSETID = 4             # 不清除 setuid/setgid 位
    CAP_KILL = 5               # 发送信号给任意进程
    CAP_SETGID = 6             # 修改进程组 ID
    CAP_SETUID = 7             # 修改进程用户 ID
    CAP_SETPCAP = 8            # 转移/删除能力
    CAP_LINUX_IMMUTABLE = 9    # 设置不可变属性
    CAP_NET_BIND_SERVICE = 10  # 绑定到特权端口 (<1024)
    CAP_NET_BROADCAST = 11     # 网络广播
    CAP_NET_ADMIN = 12         # 网络管理
    CAP_NET_RAW = 13           # 原始套接字
    CAP_IPC_LOCK = 14          # 锁定共享内存
    CAP_IPC_OWNER = 15         # IPC 所有权
    CAP_SYS_MODULE = 16        # 加载/卸载内核模块
    CAP_SYS_RAWIO = 17         # 原始 I/O 访问
    CAP_SYS_CHROOT = 18        # chroot
    CAP_SYS_PTRACE = 19        # ptrace
    CAP_SYS_PACCT = 20         # 进程审计
    CAP_SYS_ADMIN = 21         # 系统管理（保留）
    CAP_SYS_BOOT = 22          # 重启
    CAP_SYS_NICE = 23          # 修改 nice 值
    CAP_SYS_RESOURCE = 24      # 资源限制
    CAP_SYS_TIME = 25          # 修改系统时间
    CAP_SYS_TTY_CONFIG = 26    # TTY 配置
    CAP_MKNOD = 27             # 创建设备节点
    CAP_LEASE = 28             # 文件租约
    CAP_AUDIT_WRITE = 29       # 写入审计日志
    CAP_AUDIT_CONTROL = 30     # 控制审计子系统
    CAP_SETFCAP = 31           # 设置文件能力
    CAP_MAC_OVERRIDE = 32      # 覆盖 MAC (SELinux)
    CAP_MAC_ADMIN = 33         # MAC 管理


class CapabilityManager:
    """Linux 能力管理"""
    
    @staticmethod
    def drop_all_capabilities_except(allowed_caps: list):
        """
        丢弃所有能力，仅保留指定的能力
        用于最小权限运行服务
        """
        # 这需要调用 capset 系统调用
        # 简化示例，实际需要使用 ctypes 或 capng 库
        
        # 获取当前能力
        # 清除所有能力
        # 设置允许的能力
        pass
    
    @staticmethod
    def print_current_capabilities():
        """打印当前进程的能力"""
        # 读取 /proc/self/status 中的 Cap 行
        try:
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('Cap'):
                        print(line.strip())
        except FileNotFoundError:
            print("Capabilities not available")
    
    @staticmethod
    def has_capability(cap: Capability) -> bool:
        """检查当前进程是否有指定能力"""
        # 使用 capget 系统调用
        # 简化实现
        if os.geteuid() == 0:
            return True
        return False


# Docker 容器能力配置示例
DOCKER_CAP_CONFIG = {
    # 完全丢弃的能力（提升安全性）
    'drop': [
        'ALL',  # 先丢弃所有
    ],
    # 添加最小必需的能力
    'add': [
        'CHOWN',
        'SETGID',
        'SETUID',
        'NET_BIND_SERVICE',  # 如需绑定低端口
    ],
    # 或使用安全配置文件
    'security_opt': [
        'no-new-privileges:true',  # 禁止提升权限
    ]
}

# docker run 示例
# docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE myapp
```

### 3. SELinux 和 AppArmor

```python
"""
SELinux 和 AppArmor 配置管理
强制访问控制（MAC）系统
"""

import subprocess
import re
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum

class SELinuxMode(Enum):
    """SELinux 运行模式"""
    ENFORCING = "enforcing"
    PERMISSIVE = "permissive"
    DISABLED = "disabled"

@dataclass
class SELinuxContext:
    """SELinux 安全上下文"""
    user: str
    role: str
    type_: str
    level: str
    
    def __str__(self) -> str:
        return f"{self.user}:{self.role}:{self.type_}:{self.level}"
    
    @classmethod
    def from_string(cls, context: str) -> 'SELinuxContext':
        """从字符串解析 SELinux 上下文"""
        parts = context.split(':')
        if len(parts) >= 3:
            return cls(
                user=parts[0],
                role=parts[1],
                type_=parts[2],
                level=parts[3] if len(parts) > 3 else 's0'
            )
        raise ValueError(f"Invalid SELinux context: {context}")


class SELinuxManager:
    """SELinux 管理工具"""
    
    @staticmethod
    def get_mode() -> SELinuxMode:
        """获取 SELinux 运行模式"""
        try:
            result = subprocess.run(
                ['getenforce'],
                capture_output=True,
                text=True,
                check=True
            )
            return SELinuxMode(result.stdout.strip().lower())
        except (subprocess.CalledProcessError, FileNotFoundError):
            return SELinuxMode.DISABLED
    
    @staticmethod
    def get_file_context(filepath: str) -> Optional[SELinuxContext]:
        """获取文件的 SELinux 上下文"""
        try:
            result = subprocess.run(
                ['ls', '-Z', filepath],
                capture_output=True,
                text=True,
                check=True
            )
            # 解析输出: unconfined_u:object_r:user_home_t:s0 file.txt
            match = re.search(r'(\S+:\S+:\S+:\S+)', result.stdout)
            if match:
                return SELinuxContext.from_string(match.group(1))
        except subprocess.CalledProcessError:
            pass
        return None
    
    @staticmethod
    def set_file_context(filepath: str, context: SELinuxContext) -> bool:
        """设置文件的 SELinux 上下文"""
        try:
            subprocess.run(
                ['chcon', str(context), filepath],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def restore_file_context(filepath: str) -> bool:
        """恢复文件的默认 SELinux 上下文"""
        try:
            subprocess.run(
                ['restorecon', filepath],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False


# AppArmor 配置
APPARMOR_PROFILE_TEMPLATE = '''
#include <tunables/global>

/usr/bin/myapp {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  
  # 网络访问
  network inet stream,
  network inet6 stream,
  
  # 可执行文件
  /usr/bin/myapp mr,
  
  # 配置文件 - 只读
  /etc/myapp/** r,
  
  # 数据目录 - 读写
  /var/lib/myapp/** rwk,
  
  # 日志目录 - 追加写入
  /var/log/myapp/** rw,
  
  # 临时文件
  /tmp/myapp-*/** rw,
  
  # 拒绝访问敏感区域
  deny /etc/shadow r,
  deny /root/** r,
  deny /proc/sys/** w,
  deny /sys/** w,
}
'''


# Kubernetes Pod Security Policy
KUBERNETES_PSP = {
    'apiVersion': 'policy/v1beta1',
    'kind': 'PodSecurityPolicy',
    'metadata': {
        'name': 'restricted'
    },
    'spec': {
        'privileged': False,
        'allowPrivilegeEscalation': False,
        'requiredDropCapabilities': ['ALL'],
        'volumes': ['configMap', 'emptyDir', 'persistentVolumeClaim'],
        'runAsUser': {
            'rule': 'MustRunAsNonRoot'
        },
        'seLinux': {
            'rule': 'RunAsAny'
        },
        'fsGroup': {
            'rule': 'RunAsAny'
        }
    }
}
```

---

## 应用场景

### 场景 1: Web 服务器安全配置

```bash
#!/bin/bash
# Web 服务器安全加固脚本

# 1. 创建专用用户
groupadd -r webapp
useradd -r -g webapp -s /sbin/nologin -M webapp

# 2. 创建目录结构
mkdir -p /var/www/myapp/{public,logs,tmp}

# 3. 设置权限
chown -R root:root /var/www/myapp
chown -R webapp:webapp /var/www/myapp/logs /var/www/myapp/tmp

# 代码目录: root 只读，防止篡改
chmod 755 /var/www/myapp
chmod 755 /var/www/myapp/public

# 日志目录: 服务用户可写
chmod 750 /var/www/myapp/logs

# 临时目录: 严格限制
chmod 700 /var/www/myapp/tmp

# 4. 设置文件能力（如需绑定低端口）
setcap 'cap_net_bind_service=+ep' /usr/bin/myapp

# 5. SELinux 上下文
chcon -R -t httpd_sys_content_t /var/www/myapp/public
chcon -R -t httpd_log_t /var/www/myapp/logs

# 6. 启动服务（最小权限）
sudo -u webapp /usr/bin/myapp
```

### 场景 2: 容器安全访问控制

```dockerfile
# Dockerfile - 安全容器构建
FROM python:3.11-slim

# 创建非 root 用户
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# 设置工作目录
WORKDIR /app

# 复制依赖并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY --chown=appuser:appgroup . .

# 设置文件权限
RUN chmod -R 755 /app && \
    chmod -R 700 /app/secrets && \
    chown -R appuser:appgroup /app/logs

# 切换到非 root 用户
USER appuser

# 暴露端口（非特权端口）
EXPOSE 8080

CMD ["python", "app.py"]
```

```yaml
# docker-compose.yml - 安全配置
version: '3.8'
services:
  webapp:
    build: .
    user: "1000:1000"  # 指定 UID:GID
    read_only: true     # 只读根文件系统
    cap_drop:
      - ALL           # 丢弃所有能力
    cap_add:
      - NET_BIND_SERVICE  # 如需绑定低端口
    security_opt:
      - no-new-privileges:true
      - seccomp:./seccomp-profile.json
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
      - /var/log:size=100m
    volumes:
      - ./data:/app/data:rw
    networks:
      - backend
```

---

## 面试要点

### Q1: DAC 和 MAC 的区别？

**A:**

| 特性 | DAC (自主访问控制) | MAC (强制访问控制) |
|------|-------------------|-------------------|
| 控制权 | 资源所有者决定 | 系统策略强制实施 |
| 灵活性 | 高 | 较低 |
| 安全性 | 依赖用户行为 | 系统保证 |
| 绕过可能 | 可以 | 不可能 |
| 例子 | Unix 权限、ACL | SELinux、AppArmor |

**适用场景:**
- DAC: 通用服务器、开发环境
- MAC: 高安全环境、政府、金融、军事

### Q2: 什么是 Linux Capabilities？为什么要用它？

**A:**

Capabilities 将 root 权限细分为多个独立的能力，允许程序只获得必需的权限。

**为什么使用:**
1. **最小权限**: 不需要完整 root，只需要特定能力
2. **减少攻击面**: 即使程序被攻破，危害有限
3. **合规要求**: 安全审计要求

**示例:**
```bash
# 传统方式：需要 root 绑定 80 端口
sudo ./myserver

# Capabilities 方式：只需要 CAP_NET_BIND_SERVICE
setcap cap_net_bind_service=+ep ./myserver
./myserver  # 以普通用户运行，但能绑定 80 端口
```

### Q3: 如何防止容器逃逸？

**A:**

```yaml
# Kubernetes Pod Security
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true        # 禁止 root
    runAsUser: 1000
    readOnlyRootFilesystem: true  # 只读根文件系统
    allowPrivilegeEscalation: false  # 禁止权限提升
    capabilities:
      drop:
        - ALL               # 丢弃所有能力
  containers:
    - name: app
      image: myapp:latest
      securityContext:
        capabilities:
          add:
            - NET_BIND_SERVICE  # 仅添加必需能力
```

---

## 相关概念

### 数据结构
- [访问控制列表](../computer-science/data-structures/array.md)：权限存储
- [权限位图](../computer-science/algorithms/bit-manipulation.md)：高效权限表示

### 算法
- [权限检查算法](../computer-science/algorithms/sorting.md)：权限排序和查找

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)：权限检查性能

### 系统实现
- [身份认证](../application-security/authentication.md)：访问控制的前提
- [授权](../application-security/authorization.md)：应用层访问控制
- [系统加固](./security-hardening.md)：访问控制配置

### 安全领域
- [RBAC 详细实现](./rbac.md)：角色访问控制
- [审计日志](./audit-logging.md)：访问审计
- [特权提升防护](./privilege-escalation.md)：权限攻击防护

---

## 参考资料

1. [Linux Capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
2. [SELinux User Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/using_selinux/index)
3. [AppArmor Documentation](https://gitlab.com/apparmor/apparmor/-/wikis/Documentation)
4. [NIST SP 800-178](https://csrc.nist.gov/publications/detail/sp/800-178/final)
