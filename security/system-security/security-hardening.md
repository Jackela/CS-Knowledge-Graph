# 系统加固 (Security Hardening)

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、安全标准及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**系统加固 (Security Hardening)** 是通过配置安全策略、关闭不必要服务、修补漏洞等手段，降低系统攻击面的安全实践。系统加固涵盖操作系统、网络服务、应用程序和容器等多个层面，遵循"最小权限原则"和"纵深防御"理念。

```
┌─────────────────────────────────────────────────────────────────┐
│                     系统加固层次架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  应用层 (Application)                                    │  │
│   │  • 代码审计、依赖扫描、WAF部署                            │  │
│   ├─────────────────────────────────────────────────────────┤  │
│   │  容器层 (Container)                                      │  │
│   │  • 镜像安全、运行时防护、资源限制                         │  │
│   ├─────────────────────────────────────────────────────────┤  │
│   │  主机层 (Host)                                           │  │
│   │  • OS加固、防火墙、入侵检测                               │  │
│   ├─────────────────────────────────────────────────────────┤  │
│   │  网络层 (Network)                                        │  │
│   │  • 网络分段、流量监控、DDoS防护                           │  │
│   ├─────────────────────────────────────────────────────────┤  │
│   │  物理层 (Physical)                                       │  │
│   │  • 访问控制、监控录像、环境安全                           │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心概念

### 加固原则

```
┌─────────────────────────────────────────────────────────────────┐
│                    系统加固核心原则                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. 最小权限原则 (Principle of Least Privilege)               │
│      └─ 仅授予完成任务所必需的最小权限                          │
│                                                                 │
│   2. 纵深防御 (Defense in Depth)                               │
│      └─ 多层安全控制，单点失效不导致整体失效                     │
│                                                                 │
│   3. 默认拒绝 (Default Deny)                                   │
│      └─ 未明确允许的访问一律拒绝                                │
│                                                                 │
│   4. 安全基线 (Security Baseline)                              │
│      └─ 定义最低安全配置要求                                    │
│                                                                 │
│   5. 持续监控 (Continuous Monitoring)                          │
│      └─ 实时监控安全事件和异常行为                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Linux 系统加固

```python
#!/usr/bin/env python3
"""
Linux 系统加固脚本 - 自动化安全基线检查与配置
"""

import os
import subprocess
import stat
import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class Severity(Enum):
    """加固项严重级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CheckStatus(Enum):
    """检查状态"""
    PASS = "PASS"
    FAIL = "FAIL"
    MANUAL = "MANUAL"  # 需要人工确认
    NOT_APPLICABLE = "N/A"


@dataclass
class HardeningCheck:
    """系统加固检查项"""
    id: str
    name: str
    description: str
    severity: Severity
    category: str
    check_command: Optional[str] = None
    expected_result: Optional[str] = None
    remediation: Optional[str] = None


@dataclass
class CheckResult:
    """检查结果"""
    check: HardeningCheck
    status: CheckStatus
    actual_result: str
    details: Optional[str] = None


class LinuxSecurityHardening:
    """Linux 系统安全加固工具"""
    
    # CIS Benchmark 关键检查项
    CIS_CHECKS = [
        HardeningCheck(
            id="CIS-1.1.1",
            name="确保禁止 USB 存储设备",
            description="防止通过 USB 设备的数据泄露和恶意软件传播",
            severity=Severity.HIGH,
            category="物理安全",
            check_command="modprobe -n -v usb-storage",
            expected_result="install /bin/true",
            remediation="echo 'install usb-storage /bin/true' >> /etc/modprobe.d/usb-storage.conf"
        ),
        HardeningCheck(
            id="CIS-1.3.1",
            name="确保 AIDE 已安装",
            description="文件完整性检查工具，检测未授权的文件修改",
            severity=Severity.MEDIUM,
            category="文件完整性",
            check_command="dpkg -s aide 2>/dev/null || rpm -q aide 2>/dev/null",
            expected_result="Status: install ok installed",
            remediation="apt-get install -y aide && aideinit"
        ),
        HardeningCheck(
            id="CIS-2.2.2",
            name="确保 X Window System 未安装",
            description="生产服务器不应安装图形界面，减少攻击面",
            severity=Severity.HIGH,
            category="服务加固",
            check_command="dpkg -l xserver-xorg-core 2>/dev/null || rpm -qa xorg-x11*",
            expected_result="no packages found",
            remediation="apt-get remove --purge xserver-xorg-core*"
        ),
        HardeningCheck(
            id="CIS-3.1.1",
            name="确保 IP 转发已禁用",
            description="防止系统被用作路由器，降低中间人攻击风险",
            severity=Severity.HIGH,
            category="网络加固",
            check_command="sysctl net.ipv4.ip_forward",
            expected_result="net.ipv4.ip_forward = 0",
            remediation="echo 'net.ipv4.ip_forward = 0' >> /etc/sysctl.conf && sysctl -w net.ipv4.ip_forward=0"
        ),
        HardeningCheck(
            id="CIS-3.2.1",
            name="确保数据包重定向已禁用",
            description="防止 ICMP 重定向攻击",
            severity=Severity.MEDIUM,
            category="网络加固",
            check_command="sysctl net.ipv4.conf.all.accept_redirects",
            expected_result="net.ipv4.conf.all.accept_redirects = 0",
            remediation="echo 'net.ipv4.conf.all.accept_redirects = 0' >> /etc/sysctl.conf"
        ),
        HardeningCheck(
            id="CIS-4.2.1.1",
            name="确保 rsyslog 已安装",
            description="集中日志管理，满足审计要求",
            severity=Severity.MEDIUM,
            category="日志审计",
            check_command="dpkg -s rsyslog || rpm -q rsyslog",
            expected_result="installed",
            remediation="apt-get install -y rsyslog"
        ),
        HardeningCheck(
            id="CIS-5.1.1",
            name="确保 SSH 协议版本为 2",
            description="SSH v1 存在已知安全漏洞",
            severity=Severity.CRITICAL,
            category="SSH 加固",
            check_command="grep ^Protocol /etc/ssh/sshd_config",
            expected_result="Protocol 2",
            remediation="sed -i 's/^Protocol.*/Protocol 2/' /etc/ssh/sshd_config"
        ),
        HardeningCheck(
            id="CIS-5.1.2",
            name="确保 SSH 空闲超时时间已设置",
            description="防止空闲会话被劫持",
            severity=Severity.MEDIUM,
            category="SSH 加固",
            check_command="grep ^ClientAliveInterval /etc/ssh/sshd_config",
            expected_result="ClientAliveInterval 300",
            remediation="echo 'ClientAliveInterval 300' >> /etc/ssh/sshd_config"
        ),
        HardeningCheck(
            id="CIS-5.2.1",
            name="确保 sudo 已安装",
            description="特权提升审计和控制",
            severity=Severity.HIGH,
            category="权限管理",
            check_command="dpkg -s sudo || rpm -q sudo",
            expected_result="installed",
            remediation="apt-get install -y sudo"
        ),
        HardeningCheck(
            id="CIS-5.4.1.1",
            name="确保密码最小长度为 14",
            description="增强密码复杂度，防止暴力破解",
            severity=Severity.HIGH,
            category="密码策略",
            check_command="grep minlen /etc/security/pwquality.conf",
            expected_result="minlen = 14",
            remediation="sed -i 's/^#*\\s*minlen.*/minlen = 14/' /etc/security/pwquality.conf"
        ),
    ]
    
    def __init__(self):
        self.results: List[CheckResult] = []
    
    def run_command(self, command: str) -> Tuple[str, int]:
        """执行系统命令并返回输出"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "Command timeout", -1
        except Exception as e:
            return str(e), -1
    
    def execute_check(self, check: HardeningCheck) -> CheckResult:
        """执行单个检查"""
        if not check.check_command:
            return CheckResult(
                check=check,
                status=CheckStatus.MANUAL,
                actual_result="需要人工确认",
                details="此检查项需要手动验证"
            )
        
        output, returncode = self.run_command(check.check_command)
        
        # 判断检查结果
        if check.expected_result:
            if check.expected_result in output or returncode == 0:
                status = CheckStatus.PASS
            else:
                status = CheckStatus.FAIL
        else:
            status = CheckStatus.PASS if returncode == 0 else CheckStatus.FAIL
        
        return CheckResult(
            check=check,
            status=status,
            actual_result=output[:200] if output else "No output",
            details=None
        )
    
    def run_all_checks(self) -> List[CheckResult]:
        """运行所有安全检查"""
        self.results = []
        for check in self.CIS_CHECKS:
            result = self.execute_check(check)
            self.results.append(result)
        return self.results
    
    def generate_report(self) -> Dict:
        """生成加固检查报告"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == CheckStatus.PASS)
        failed = sum(1 for r in self.results if r.status == CheckStatus.FAIL)
        manual = sum(1 for r in self.results if r.status == CheckStatus.MANUAL)
        
        return {
            "summary": {
                "total_checks": total,
                "passed": passed,
                "failed": failed,
                "manual": manual,
                "compliance_rate": f"{(passed/total)*100:.1f}%" if total > 0 else "N/A"
            },
            "failed_checks": [
                {
                    "id": r.check.id,
                    "name": r.check.name,
                    "severity": r.check.severity.value,
                    "remediation": r.check.remediation,
                    "actual": r.actual_result
                }
                for r in self.results if r.status == CheckStatus.FAIL
            ],
            "details": [
                {
                    "id": r.check.id,
                    "name": r.check.name,
                    "status": r.status.value,
                    "severity": r.check.severity.value,
                    "category": r.check.category
                }
                for r in self.results
            ]
        }
    
    def apply_remediation(self, check_id: str, dry_run: bool = True) -> bool:
        """应用修复措施"""
        check = next((c for c in self.CIS_CHECKS if c.id == check_id), None)
        if not check or not check.remediation:
            return False
        
        if dry_run:
            print(f"[DRY RUN] Would execute: {check.remediation}")
            return True
        
        output, returncode = self.run_command(check.remediation)
        return returncode == 0


class SSHHardening:
    """SSH 服务加固配置"""
    
    SECURE_SSH_CONFIG = """
# SSH 安全配置 - 由自动化脚本生成
# 基于 CIS Benchmark 和业界最佳实践

# 协议版本
Protocol 2

# 认证设置
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
MaxAuthTries 3
MaxSessions 2

# 空闲超时
ClientAliveInterval 300
ClientAliveCountMax 2
LoginGraceTime 60

# 安全算法
Ciphers aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512,hmac-sha2-256
KexAlgorithms curve25519-sha256@libssh.org,ecdh-sha2-nistp521,ecdh-sha2-nistp384,ecdh-sha2-nistp256,diffie-hellman-group-exchange-sha256

# 访问控制
AllowUsers deploy@10.0.*.* admin@192.168.*.*
DenyUsers root test guest

# 日志
SyslogFacility AUTH
LogLevel VERBOSE

# 其他安全设置
X11Forwarding no
PermitUserEnvironment no
AllowAgentForwarding no
AllowTcpForwarding no
PermitTunnel no
Banner /etc/ssh/banner
"""
    
    @classmethod
    def apply_config(cls, backup: bool = True) -> bool:
        """应用安全 SSH 配置"""
        ssh_config_path = Path("/etc/ssh/sshd_config")
        
        if not ssh_config_path.exists():
            print(f"Error: {ssh_config_path} not found")
            return False
        
        # 备份原配置
        if backup:
            backup_path = Path("/etc/ssh/sshd_config.bak")
            backup_path.write_text(ssh_config_path.read_text())
            print(f"Backup created: {backup_path}")
        
        # 写入新配置
        ssh_config_path.write_text(cls.SECURE_SSH_CONFIG)
        
        # 验证配置
        result = subprocess.run(
            ["sshd", "-t"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"SSH config validation failed: {result.stderr}")
            return False
        
        # 重启 SSH 服务
        subprocess.run(["systemctl", "restart", "sshd"], check=True)
        print("SSH service restarted with secure configuration")
        return True


class FilePermissionHardening:
    """文件权限加固"""
    
    # 关键文件的推荐权限
    FILE_PERMISSIONS = {
        "/etc/passwd": (0o644, "root", "root"),
        "/etc/shadow": (0o000, "root", "shadow"),
        "/etc/group": (0o644, "root", "root"),
        "/etc/gshadow": (0o000, "root", "shadow"),
        "/etc/ssh/sshd_config": (0o600, "root", "root"),
        "/var/log": (0o755, "root", "root"),
        "/tmp": (0o1777, "root", "root"),  # Sticky bit
        "/etc/crontab": (0o600, "root", "root"),
        "/etc/cron.d": (0o700, "root", "root"),
        "/etc/sudoers": (0o440, "root", "root"),
    }
    
    # SUID/SGID 黑名单 - 高风险程序
    SUID_BLACKLIST = [
        "/usr/bin/chsh",
        "/usr/bin/chfn",
        "/usr/bin/newgrp",
        "/sbin/mount.nfs",
    ]
    
    @classmethod
    def check_file_permissions(cls) -> List[Dict]:
        """检查关键文件权限"""
        issues = []
        
        for path_str, (expected_mode, expected_owner, expected_group) in cls.FILE_PERMISSIONS.items():
            path = Path(path_str)
            if not path.exists():
                continue
            
            stat_info = path.stat()
            actual_mode = stat.S_IMODE(stat_info.st_mode)
            
            # 检查权限
            if actual_mode != expected_mode:
                issues.append({
                    "path": path_str,
                    "issue": "incorrect_permissions",
                    "expected": oct(expected_mode),
                    "actual": oct(actual_mode)
                })
            
            # 检查所有者 (需要 root 权限)
            try:
                import pwd, grp
                actual_owner = pwd.getpwuid(stat_info.st_uid).pw_name
                actual_group = grp.getgrgid(stat_info.st_gid).gr_name
                
                if actual_owner != expected_owner or actual_group != expected_group:
                    issues.append({
                        "path": path_str,
                        "issue": "incorrect_ownership",
                        "expected": f"{expected_owner}:{expected_group}",
                        "actual": f"{actual_owner}:{actual_group}"
                    })
            except (KeyError, ImportError):
                pass
        
        return issues
    
    @classmethod
    def fix_permissions(cls, dry_run: bool = True) -> None:
        """修复文件权限"""
        for path_str, (mode, owner, group) in cls.FILE_PERMISSIONS.items():
            path = Path(path_str)
            if not path.exists():
                continue
            
            if dry_run:
                print(f"[DRY RUN] Would set {path_str} to {oct(mode)} {owner}:{group}")
            else:
                try:
                    path.chmod(mode)
                    shutil.chown(path, owner, group)
                    print(f"[FIXED] {path_str}")
                except PermissionError:
                    print(f"[ERROR] Permission denied: {path_str}")
    
    @classmethod
    def scan_suid_binaries(cls) -> List[Dict]:
        """扫描系统中的 SUID/SGID 程序"""
        result = subprocess.run(
            ["find", "/", "-perm", "-4000", "-o", "-perm", "-2000"],
            capture_output=True,
            text=True
        )
        
        suid_files = []
        for line in result.stdout.strip().split('\n'):
            if line and not line.startswith('/proc'):
                suid_files.append({
                    "path": line,
                    "risk": "high" if line in cls.SUID_BLACKLIST else "medium"
                })
        
        return suid_files


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("Linux 系统安全加固检查工具")
    print("=" * 60)
    
    # 运行 CIS 检查
    hardening = LinuxSecurityHardening()
    results = hardening.run_all_checks()
    
    # 生成报告
    report = hardening.generate_report()
    
    print("\n检查摘要:")
    print(f"  总检查项: {report['summary']['total_checks']}")
    print(f"  通过: {report['summary']['passed']}")
    print(f"  失败: {report['summary']['failed']}")
    print(f"  合规率: {report['summary']['compliance_rate']}")
    
    if report['failed_checks']:
        print("\n失败的检查项:")
        for item in report['failed_checks']:
            print(f"  [{item['severity']}] {item['id']}: {item['name']}")
            print(f"    修复建议: {item['remediation'][:80]}...")
```

### 容器安全加固

```python
#!/usr/bin/env python3
"""
容器安全加固 - Docker/Kubernetes 安全基线
基于 CIS Docker Benchmark 和 Kubernetes CIS Benchmark
"""

import json
import subprocess
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class ContainerRuntime(Enum):
    """容器运行时类型"""
    DOCKER = "docker"
    CONTAINERD = "containerd"
    CRIO = "cri-o"


@dataclass
class ContainerSecurityPolicy:
    """容器安全策略配置"""
    # 资源限制
    cpu_limit: str = "1.0"           # CPU 限制
    memory_limit: str = "512m"       # 内存限制
    pids_limit: int = 100            # 进程数限制
    
    # 安全选项
    read_only_rootfs: bool = True    # 只读根文件系统
    no_new_privileges: bool = True   # 禁止提升权限
    drop_all_capabilities: bool = True  # 丢弃所有 capability
    add_capabilities: List[str] = None  # 显式添加的 capability
    
    # 命名空间隔离
    disable_host_network: bool = True
    disable_host_pid: bool = True
    disable_host_ipc: bool = True
    
    # 用户配置
    run_as_non_root: bool = True
    run_as_user: int = 1000
    
    def __post_init__(self):
        if self.add_capabilities is None:
            self.add_capabilities = []


class DockerSecurityHardening:
    """Docker 安全加固"""
    
    # CIS Docker Benchmark 关键检查
    DOCKER_CHECKS = [
        {
            "id": "2.1",
            "description": "确保 network Traffic 被限制在容器之间",
            "check": "docker network ls --filter driver=bridge --quiet | xargs docker network inspect --format '{{.Name}}: {{.Options.com.docker.network.bridge.enable_icc}}'",
            "expected": "false"
        },
        {
            "id": "2.2",
            "description": "确保日志级别设置为 info",
            "check": "docker info --format '{{.LoggingDriver}}'",
            "expected": "json-file"
        },
        {
            "id": "2.3",
            "description": "确保 Docker 允许特定用户控制 Docker 守护进程",
            "check": "grep docker /etc/group",
            "expected": "docker:x"
        },
        {
            "id": "2.4",
            "description": "确保 cgroup 使用已启用",
            "check": "docker info --format '{{.CgroupDriver}}'",
            "expected": "cgroupfs"
        },
        {
            "id": "2.5",
            "description": "确保不启用 insecure registries",
            "check": "docker info --format '{{.RegistryConfig.InsecureRegistryCIDRs}}'",
            "expected": "[]"
        },
        {
            "id": "2.6",
            "description": "确保 aufs 存储驱动不被使用",
            "check": "docker info --format '{{.Driver}}'",
            "expected_not": "aufs"
        },
        {
            "id": "2.7",
            "description": "确保 TLS 认证用于 Docker 守护进程",
            "check": "ps aux | grep dockerd",
            "expected": "tlsverify"
        },
        {
            "id": "4.1",
            "description": "确保 container 以非 root 用户运行",
            "check": "docker ps --quiet | xargs docker inspect --format '{{.Id}}: User={{.Config.User}}'",
            "expected_not": "User=0"
        },
        {
            "id": "4.2",
            "description": "确保容器使用可信的基础镜像",
            "manual": True,
            "note": "需要人工审核 Dockerfile 中的 FROM 指令"
        },
        {
            "id": "4.3",
            "description": "确保在 Dockerfile 中不使用 ADD，使用 COPY 替代",
            "manual": True,
            "note": "检查 Dockerfile 中是否使用 ADD 指令"
        },
        {
            "id": "4.4",
            "description": "确保镜像中不包含敏感信息",
            "manual": True,
            "note": "使用 docker history 检查镜像层，确保无 secrets"
        },
        {
            "id": "4.5",
            "description": "确保开启 CONTENT_TRUST",
            "check": "echo $DOCKER_CONTENT_TRUST",
            "expected": "1"
        },
        {
            "id": "4.6",
            "description": "确保更新 HEALTHCHECK 指令",
            "manual": True,
            "note": "检查 Dockerfile 是否包含 HEALTHCHECK"
        },
        {
            "id": "4.7",
            "description": "确保不使用特权容器",
            "check": "docker ps --quiet --all | xargs docker inspect --format '{{.Id}}: Privileged={{.HostConfig.Privileged}}'",
            "expected_not": "Privileged=true"
        },
        {
            "id": "4.8",
            "description": "确保敏感主机系统目录不以读写模式挂载",
            "manual": True,
            "note": "检查容器是否挂载了 /etc, /usr, /bin 等系统目录"
        },
        {
            "id": "4.9",
            "description": "确保禁用 sshd",
            "check": "docker ps --quiet | xargs docker exec 2>/dev/null which sshd",
            "expected": ""
        },
    ]
    
    @staticmethod
    def generate_secure_dockerfile(base_image: str = "python:3.11-slim") -> str:
        """生成安全的 Dockerfile 模板"""
        return f'''# 安全 Dockerfile 模板
FROM {base_image}

# 创建非 root 用户
RUN groupadd -r appgroup && useradd -r -g appgroup -s /bin/false appuser

# 设置工作目录
WORKDIR /app

# 仅复制必要的文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY --chown=appuser:appgroup . .

# 切换到非 root 用户
USER appuser

# 只读根文件系统需要在运行时指定，这里标记
# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["python", "app.py"]
'''
    
    @staticmethod
    def generate_docker_run_command(
        image: str,
        name: str,
        policy: Optional[ContainerSecurityPolicy] = None
    ) -> str:
        """生成安全的 docker run 命令"""
        if policy is None:
            policy = ContainerSecurityPolicy()
        
        cmd_parts = ["docker run -d"]
        
        # 资源限制
        cmd_parts.append(f"--cpus='{policy.cpu_limit}'")
        cmd_parts.append(f"--memory='{policy.memory_limit}'")
        cmd_parts.append(f"--pids-limit={policy.pids_limit}")
        
        # 安全选项
        if policy.read_only_rootfs:
            cmd_parts.append("--read-only")
        
        if policy.no_new_privileges:
            cmd_parts.append("--security-opt=no-new-privileges:true")
        
        # Capability 管理
        if policy.drop_all_capabilities:
            cmd_parts.append("--cap-drop=ALL")
        for cap in policy.add_capabilities:
            cmd_parts.append(f"--cap-add={cap}")
        
        # 命名空间隔离
        if policy.disable_host_network:
            cmd_parts.append("--network=bridge")
        if policy.disable_host_pid:
            cmd_parts.append("--pid=host")
        if policy.disable_host_ipc:
            cmd_parts.append("--ipc=private")
        
        # 用户配置
        if policy.run_as_non_root:
            cmd_parts.append(f"--user={policy.run_as_user}")
        
        # 其他安全选项
        cmd_parts.append("--security-opt=seccomp=default.json")
        cmd_parts.append("--tmpfs /tmp:noexec,nosuid,size=100m")
        
        # 名称和镜像
        cmd_parts.append(f"--name {name}")
        cmd_parts.append(image)
        
        return " \\\n    ".join(cmd_parts)
    
    @classmethod
    def get_secure_daemon_config(cls) -> Dict:
        """获取安全的 Docker daemon 配置"""
        return {
            "userns-remap": "default",  # 启用用户命名空间重映射
            "log-driver": "json-file",
            "log-opts": {
                "max-size": "10m",
                "max-file": "3"
            },
            "live-restore": True,  # 守护进程重启时保持容器运行
            "no-new-privileges": True,
            "seccomp-profile": "/etc/docker/seccomp-default.json",
            "default-ulimits": {
                "nofile": {
                    "Name": "nofile",
                    "Hard": 64000,
                    "Soft": 64000
                }
            },
            "icc": False,  # 禁用容器间通信
            "iptables": True,
            "ip-forward": False,
            "tls": True,
            "tlscacert": "/etc/docker/ca.pem",
            "tlscert": "/etc/docker/server-cert.pem",
            "tlskey": "/etc/docker/server-key.pem",
            "tlsverify": True,
            "storage-driver": "overlay2",
            "selinux-enabled": True,
            "apparmor-default": "docker-default"
        }


class KubernetesSecurityHardening:
    """Kubernetes 安全加固"""
    
    @staticmethod
    def generate_secure_pod_spec(name: str, image: str) -> Dict:
        """生成安全的 Pod 配置"""
        return {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": name,
                "labels": {
                    "app": name,
                    "security.istio.io/tlsMode": "istio"
                },
                "annotations": {
                    "seccomp.security.alpha.kubernetes.io/pod": "runtime/default"
                }
            },
            "spec": {
                "securityContext": {
                    "runAsNonRoot": True,
                    "runAsUser": 1000,
                    "runAsGroup": 1000,
                    "fsGroup": 1000,
                    "seccompProfile": {
                        "type": "RuntimeDefault"
                    }
                },
                "containers": [{
                    "name": name,
                    "image": image,
                    "imagePullPolicy": "Always",
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                        "readOnlyRootFilesystem": True,
                        "privileged": False,
                        "capabilities": {
                            "drop": ["ALL"],
                            "add": ["NET_BIND_SERVICE"]
                        },
                        "runAsNonRoot": True,
                        "runAsUser": 1000,
                        "seccompProfile": {
                            "type": "RuntimeDefault"
                        }
                    },
                    "resources": {
                        "limits": {
                            "cpu": "500m",
                            "memory": "512Mi"
                        },
                        "requests": {
                            "cpu": "100m",
                            "memory": "128Mi"
                        }
                    },
                    "volumeMounts": [
                        {
                            "name": "tmp",
                            "mountPath": "/tmp"
                        },
                        {
                            "name": "cache",
                            "mountPath": "/cache"
                        }
                    ],
                    "livenessProbe": {
                        "httpGet": {
                            "path": "/health",
                            "port": 8080
                        },
                        "initialDelaySeconds": 30,
                        "periodSeconds": 10
                    },
                    "readinessProbe": {
                        "httpGet": {
                            "path": "/ready",
                            "port": 8080
                        },
                        "initialDelaySeconds": 5,
                        "periodSeconds": 5
                    }
                }],
                "volumes": [
                    {
                        "name": "tmp",
                        "emptyDir": {}
                    },
                    {
                        "name": "cache",
                        "emptyDir": {
                            "sizeLimit": "1Gi"
                        }
                    }
                ],
                "automountServiceAccountToken": False,  # 不自动挂载 ServiceAccount Token
                "securityContext": {
                    "sysctls": [
                        {"name": "net.ipv4.ip_unprivileged_port_start", "value": "80"}
                    ]
                }
            }
        }
    
    @staticmethod
    def generate_network_policy(app_label: str) -> Dict:
        """生成默认拒绝的网络策略"""
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{app_label}-default-deny"
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "app": app_label
                    }
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [],  # 默认拒绝所有入站
                "egress": [
                    {
                        "to": [
                            {"namespaceSelector": {}, "podSelector": {}}
                        ],
                        "ports": [
                            {"protocol": "UDP", "port": 53},  # DNS
                            {"protocol": "TCP", "port": 443}   # HTTPS
                        ]
                    }
                ]
            }
        }
    
    @staticmethod
    def generate_rbac_least_privilege(service_account: str, namespace: str) -> Dict:
        """生成最小权限 RBAC 配置"""
        return {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": f"{service_account}-role",
                "namespace": namespace
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods"],
                    "verbs": ["get", "list"],
                    "resourceNames": [f"{service_account}*"]  # 仅特定资源
                },
                {
                    "apiGroups": [""],
                    "resources": ["configmaps"],
                    "verbs": ["get"],
                    "resourceNames": [f"{service_account}-config"]
                }
            ]
        }


# Seccomp 默认配置文件
SECCOMP_DEFAULT_PROFILE = {
    "defaultAction": "SCMP_ACT_ERRNO",
    "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_X86", "SCMP_ARCH_AARCH64"],
    "syscalls": [
        {
            "names": [
                "accept", "accept4", "access", "adjtimex", "alarm", "bind",
                "brk", "capget", "capset", "chdir", "chmod", "chown", "chown32",
                "clock_adjtime", "clock_getres", "clock_gettime", "clock_nanosleep",
                "clone", "close", "connect", "copy_file_range", "creat",
                "dup", "dup2", "dup3", "epoll_create", "epoll_create1",
                "epoll_ctl", "epoll_ctl_old", "epoll_pwait", "epoll_wait",
                "epoll_wait_old", "eventfd", "eventfd2", "execve", "execveat",
                "exit", "exit_group", "faccessat", "fadvise64", "fadvise64_64",
                "fallocate", "fanotify_mark", "fchdir", "fchmod", "fchmodat",
                "fchown", "fchown32", "fchownat", "fcntl", "fcntl64", "fdatasync",
                "fgetxattr", "flistxattr", "flock", "fork", "fremovexattr",
                "fsetxattr", "fstat", "fstat64", "fstatat64", "fstatfs",
                "fstatfs64", "fsync", "ftruncate", "ftruncate64", "futex",
                "getcpu", "getcwd", "getdents", "getdents64", "getegid",
                "getegid32", "geteuid", "geteuid32", "getgid", "getgid32",
                "getgroups", "getgroups32", "getitimer", "getpeername",
                "getpgid", "getpgrp", "getpid", "getppid", "getpriority",
                "getrandom", "getresgid", "getresgid32", "getresuid",
                "getresuid32", "getrlimit", "get_robust_list", "getrusage",
                "getsid", "getsockname", "getsockopt", "get_thread_area",
                "gettid", "gettimeofday", "getuid", "getuid32", "getxattr",
                "inotify_add_watch", "inotify_init", "inotify_init1",
                "inotify_rm_watch", "io_cancel", "ioctl", "io_destroy",
                "io_getevents", "io_pgetevents", "ioprio_get", "ioprio_set",
                "io_setup", "io_submit", "io_uring_enter", "io_uring_register",
                "io_uring_setup", "kill", "lchown", "lchown32", "lgetxattr",
                "link", "linkat", "listen", "listxattr", "llistxattr",
                "lremovexattr", "lseek", "lsetxattr", "lstat", "lstat64",
                "madvise", "memfd_create", "mincore", "mkdir", "mkdirat",
                "mknod", "mknodat", "mlock", "mlock2", "mlockall", "mmap",
                "mmap2", "mprotect", "mq_getsetattr", "mq_notify", "mq_open",
                "mq_timedreceive", "mq_timedsend", "mq_unlink", "mremap",
                "msgctl", "msgget", "msgrcv", "msgsnd", "msync", "munlock",
                "munlockall", "munmap", "nanosleep", "newfstatat", "open",
                "openat", "pause", "pipe", "pipe2", "poll", "ppoll",
                "prctl", "pread64", "preadv", "preadv2", "prlimit64",
                "pselect6", "pwrite64", "pwritev", "pwritev2", "read",
                "readahead", "readdir", "readlink", "readlinkat", "readv",
                "recv", "recvfrom", "recvmmsg", "recvmsg", "remap_file_pages",
                "removexattr", "rename", "renameat", "renameat2", "restart_syscall",
                "rmdir", "rseq", "rt_sigaction", "rt_sigpending", "rt_sigprocmask",
                "rt_sigqueueinfo", "rt_sigreturn", "rt_sigsuspend", "rt_sigtimedwait",
                "rt_tgsigqueueinfo", "sched_getaffinity", "sched_getattr",
                "sched_getparam", "sched_get_priority_max", "sched_get_priority_min",
                "sched_getscheduler", "sched_rr_get_interval", "sched_setaffinity",
                "sched_setattr", "sched_setparam", "sched_setscheduler",
                "sched_yield", "seccomp", "select", "semctl", "semget",
                "semop", "semtimedop", "send", "sendfile", "sendfile64",
                "sendmmsg", "sendmsg", "sendto", "setfsgid", "setfsgid32",
                "setfsuid", "setfsuid32", "setgid", "setgid32", "setgroups",
                "setgroups32", "setitimer", "setpgid", "setpriority",
                "setregid", "setregid32", "setresgid", "setresgid32",
                "setresuid", "setresuid32", "setreuid", "setreuid32",
                "setrlimit", "set_robust_list", "setsid", "setsockopt",
                "set_thread_area", "set_tid_address", "setuid", "setuid32",
                "setxattr", "shmat", "shmctl", "shmdt", "shmget", "shutdown",
                "sigaltstack", "signalfd", "signalfd4", "sigpending",
                "sigprocmask", "sigreturn", "socket", "socketcall",
                "socketpair", "splice", "stat", "stat64", "statfs",
                "statfs64", "statx", "symlink", "symlinkat", "sync",
                "sync_file_range", "syncfs", "sysinfo", "tee", "tgkill",
                "time", "timer_create", "timer_delete", "timer_getoverrun",
                "timer_gettime", "timer_settime", "timerfd_create",
                "timerfd_gettime", "timerfd_settime", "times", "tkill",
                "truncate", "truncate64", "ugetrlimit", "umask", "uname",
                "unlink", "unlinkat", "utime", "utimensat", "utimes",
                "vfork", "wait4", "waitid", "waitpid", "write", "writev"
            ],
            "action": "SCMP_ACT_ALLOW"
        }
    ]
}


# 使用示例
if __name__ == "__main__":
    print("容器安全加固工具")
    print("=" * 50)
    
    # 生成安全 Dockerfile
    print("\n1. 安全 Dockerfile 模板:")
    print(DockerSecurityHardening.generate_secure_dockerfile())
    
    # 生成安全 docker run 命令
    print("\n2. 安全容器运行命令:")
    policy = ContainerSecurityPolicy(
        cpu_limit="0.5",
        memory_limit="256m",
        add_capabilities=["NET_BIND_SERVICE"]
    )
    cmd = DockerSecurityHardening.generate_docker_run_command(
        "myapp:latest",
        "secure-app",
        policy
    )
    print(cmd)
    
    # 生成 Pod spec
    print("\n3. 安全 Kubernetes Pod 配置:")
    pod_spec = KubernetesSecurityHardening.generate_secure_pod_spec("web", "nginx:alpine")
    print(json.dumps(pod_spec, indent=2))
```

---

## 应用场景

### 场景一：生产服务器加固流程

```
┌─────────────────────────────────────────────────────────────────┐
│                  生产服务器加固标准流程                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  阶段 1: 基线扫描 (1 天)                                        │
│  ├── 运行 CIS Benchmark 自动化检查                              │
│  ├── 识别高/严重风险项                                          │
│  └── 生成合规性报告                                             │
│                                                                 │
│  阶段 2: 系统加固 (2-3 天)                                      │
│  ├── SSH 安全配置 (禁用 root 登录、密钥认证)                     │
│  ├── 文件权限修复 (shadow、ssh 配置)                            │
│  ├── 网络参数调优 (禁用 IP 转发、ICMP 重定向)                   │
│  ├── 不必要服务关闭 (X11、telnet)                               │
│  └── 防火墙规则配置 (默认拒绝、仅开放必要端口)                   │
│                                                                 │
│  阶段 3: 应用加固 (1-2 天)                                      │
│  ├── Web 服务器安全头配置                                       │
│  ├── 数据库访问控制                                             │
│  └── 日志审计配置                                               │
│                                                                 │
│  阶段 4: 验证测试 (1 天)                                        │
│  ├── 重新运行基线扫描                                           │
│  ├── 漏洞扫描 (OpenVAS/Nessus)                                  │
│  └── 渗透测试                                                   │
│                                                                 │
│  阶段 5: 持续监控 (持续)                                        │
│  ├── 部署 HIDS (OSSEC/Wazuh)                                    │
│  ├── 配置日志集中收集                                           │
│  └── 设置安全告警规则                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 场景二：容器化环境安全加固

```
┌─────────────────────────────────────────────────────────────────┐
│                   容器环境安全加固策略                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  镜像安全                                                       │
│  ├── 使用最小基础镜像 (Alpine/Distroless)                       │
│  ├── 镜像漏洞扫描 (Trivy/Clair)                                 │
│  ├── 镜像签名验证 (Notary/Cosign)                               │
│  └── 禁止 root 用户运行                                         │
│                                                                 │
│  运行时安全                                                     │
│  ├── Seccomp 配置文件                                           │
│  ├── AppArmor/SELinux 策略                                      │
│  ├── Capability 最小化                                          │
│  └── 资源限制 (CPU/内存/PID)                                    │
│                                                                 │
│  编排安全 (Kubernetes)                                          │
│  ├── Pod Security Standards                                     │
│  ├── Network Policies (默认拒绝)                                │
│  ├── RBAC 最小权限                                              │
│  └── Admission Controllers                                      │
│                                                                 │
│  供应链安全                                                     │
│  ├── 镜像仓库访问控制                                           │
│  ├── CI/CD 流水线安全检查                                       │
│  └── 依赖漏洞扫描                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试 Q&A

**Q: 什么是 CIS Benchmark？为什么它被广泛用作安全基线？**

A: CIS Benchmark 是由互联网安全中心 (Center for Internet Security) 制定的安全配置标准，特点包括：
- **社区驱动**: 由安全专家、厂商和用户共同维护
- **覆盖广泛**: 支持主流操作系统、数据库、云平台、容器等
- **可操作**: 每个检查项都有具体的检测命令和修复建议
- **分级评估**: 分为 Level 1 (基础) 和 Level 2 (高安全) 两个级别
- **持续更新**: 跟随软件版本更新定期发布新版
- **合规基础**: 满足 PCI-DSS、HIPAA、GDPR 等法规的基线要求

---

**Q: 解释 Linux Capabilities 以及为什么在容器安全中重要？**

A: Linux Capabilities 将传统 root 用户的特权细分为多个独立的权限单元：
- **原理**: 传统 UNIX 只有 root/普通用户两种权限级别，Capabilities 允许更细粒度的权限控制
- **容器应用**: 默认情况下容器以 root 运行但有所有 capability，应使用 `--cap-drop=ALL` 然后按需添加
- **常见 capability**: 
  - `NET_BIND_SERVICE`: 绑定低端口 (<1024)
  - `SETUID/SETGID`: 修改进程权限
  - `SYS_ADMIN`: 系统管理操作 (高风险，应避免)
  - `SYS_PTRACE`: 进程调试 (可被利用逃逸)
- **最佳实践**: 始终遵循最小权限原则，使用非 root 用户，仅添加必要的 capability

---

**Q: 如何防止容器逃逸 (Container Escape)？**

A: 容器逃逸防护措施包括多层防御：
- **用户隔离**: 容器内使用非 root 用户 (`--user`)
- **Capability 限制**: `--cap-drop=ALL` 仅保留必要权限
- **Seccomp**: 限制可用的系统调用
- **AppArmor/SELinux**: 强制访问控制策略
- **只读根文件系统**: `--read-only` 防止运行时修改
- **禁止特权模式**: `--privileged=false` (默认)
- **资源限制**: CPU/内存/PID 限制防止 DoS
- **内核补丁**: 及时更新内核修复漏洞 (如 runc CVE-2019-5736)
- **监控告警**: 检测异常系统调用和文件访问模式

---

**Q: SSH 加固的关键配置有哪些？**

A: SSH 服务加固的关键配置项：
- **Protocol 2**: 仅使用 SSH 协议版本 2
- **禁用 root 登录**: `PermitRootLogin no`
- **密钥认证**: `PasswordAuthentication no`, `PubkeyAuthentication yes`
- **限制算法**: 禁用弱算法 (MD5, SHA1, DSA, 3DES)
- **空闲超时**: `ClientAliveInterval 300`, `ClientAliveCountMax 2`
- **访问控制**: `AllowUsers`, `AllowGroups`, `DenyUsers`
- **禁止转发**: `X11Forwarding no`, `AllowTcpForwarding no`
- **限制尝试**: `MaxAuthTries 3`, `MaxSessions 2`
- **端口修改**: 考虑使用非标准端口 (22 → 2222) 减少扫描
- **Fail2ban**: 部署防暴力破解工具

---

**Q: 解释纵深防御 (Defense in Depth) 在安全加固中的应用？**

A: 纵深防御是多层安全控制策略：
- **核心思想**: 单点失效不会导致整体安全崩溃
- **网络层**: 防火墙、WAF、DDoS 防护、网络分段
- **主机层**: OS 加固、HIDS、文件完整性检查、EDR
- **应用层**: 输入验证、身份认证、访问控制、WAF
- **数据层**: 加密、备份、访问审计
- **物理层**: 门禁、监控、环境控制
- **人员层**: 安全培训、背景调查、最小权限
- **持续监控**: 日志分析、SIEM、威胁情报

---

## 相关概念

- [访问控制](./access-control.md) - 系统资源访问控制机制
- [漏洞管理](./vulnerability-management.md) - 安全漏洞识别与修复
- [审计日志](./audit-logging.md) - 安全事件记录与分析
- [身份认证](../application-security/authentication.md) - 用户身份验证机制
- [授权](../application-security/authorization.md) - 权限控制模型

## 相关标准

- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) - 安全配置标准
- [STIG (Security Technical Implementation Guides)](https://public.cyber.mil/stigs/) - DoD 安全配置指南
- [NIST SP 800-123](https://csrc.nist.gov/publications/detail/sp/800-123/final) - 系统加固指南
- [PCI DSS](https://www.pcisecuritystandards.org/) - 支付卡行业数据安全标准
- [ISO/IEC 27001](https://www.iso.org/isoiec-27001-information-security.html) - 信息安全管理体系
