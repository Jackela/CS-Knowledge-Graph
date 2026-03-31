# 沙箱技术 (Sandboxing)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、Linux内核文档及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**沙箱 (Sandbox)** 是一种安全机制，用于在受限环境中运行程序，隔离其对系统资源的访问。沙箱技术广泛应用于浏览器、移动应用、容器运行时等场景，是防御恶意代码和漏洞利用的重要防线。

```
┌─────────────────────────────────────────────────────────────────┐
│                   沙箱技术层次                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   应用层沙箱                                                     │
│   ├─ 浏览器沙箱 (Chrome Sandbox, Firefox RLBox)                │
│   ├─ Java SecurityManager                                       │
│   └─ 移动应用沙箱 (iOS App Sandbox, Android SELinux)           │
│                                                                 │
│   容器层沙箱                                                     │
│   ├─ Namespaces + CGroups (Docker, containerd)                 │
│   ├─ gVisor (用户态内核)                                        │
│   └─ Firecracker (MicroVM)                                      │
│                                                                 │
│   系统调用层沙箱                                                 │
│   ├─ Seccomp (系统调用过滤)                                     │
│   ├─ ptrace (进程追踪)                                          │
│   └─ Landlock (非特权沙箱)                                      │
│                                                                 │
│   内核层沙箱                                                     │
│   ├─ chroot (文件系统隔离)                                      │
│   └─ KVM/QEMU (硬件虚拟化)                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## chroot

chroot (Change Root) 是最基础的文件系统隔离机制，改变进程的根目录视图。

```
┌─────────────────────────────────────────────────────────────────┐
│                   chroot 隔离原理                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   正常进程视角:                                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  /                                                       │   │
│   │  ├── bin/                                                │   │
│   │  ├── etc/                                                │   │
│   │  ├── home/                                               │   │
│   │  ├── lib/                                                │   │
│   │  ├── proc/                                               │   │
│   │  ├── tmp/                                                │   │
│   │  └── usr/                                                │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   chroot后进程视角:                                               │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  /home/jail (被设为新的根目录)                           │   │
│   │  ├── bin/  ◀── chroot jail内部                          │   │
│   │  ├── lib/                                                │   │
│   │  ├── usr/                                                │   │
│   │  └── tmp/                                                │   │
│   │                                                          │   │
│   │  [无法访问真实文件系统的其他部分]                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   ⚠️ chroot 的局限:                                              │
│   • 需要root权限创建chroot jail                                  │
│   • 不隔离网络、进程、设备等                                      │
│   • root用户可能通过chroot escape突破                           │
│   • 现代沙箱需要配合其他机制使用                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**chroot 使用示例：**

```bash
# 创建chroot jail
$ sudo mkdir -p /var/chroot/{bin,lib,lib64,etc,tmp,proc}

# 复制必要的程序
$ sudo cp /bin/bash /var/chroot/bin/
$ sudo cp /bin/ls /var/chroot/bin/

# 复制依赖库 (使用ldd查看依赖)
$ ldd /bin/bash
	linux-vdso.so.1 => ...
	libtinfo.so.6 => /lib/x86_64-linux-gnu/libtinfo.so.6
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6
	/lib64/ld-linux-x86-64.so.2 => ...

# 复制依赖库到chroot
$ sudo cp /lib/x86_64-linux-gnu/libtinfo.so.6 /var/chroot/lib/
$ sudo cp /lib/x86_64-linux-gnu/libc.so.6 /var/chroot/lib/
$ sudo cp /lib64/ld-linux-x86-64.so.2 /var/chroot/lib64/

# 创建必要的设备文件
$ sudo mknod -m 666 /var/chroot/dev/null c 1 3
$ sudo mknod -m 666 /var/chroot/dev/random c 1 8
$ sudo mknod -m 666 /var/chroot/dev/urandom c 1 9
$ sudo mknod -m 666 /var/chroot/dev/zero c 1 5

# 执行chroot
$ sudo chroot /var/chroot /bin/bash
# 现在在chroot jail中运行

# 更安全的chroot (使用unshare)
$ sudo unshare --mount --pid --fork --chroot=/var/chroot /bin/bash
```

---

## Linux Namespaces

Namespaces 是Linux内核提供的资源隔离机制，实现进程间资源视图隔离。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Linux Namespaces 类型                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Mount (mnt)     - 文件系统挂载点隔离                    │   │
│   │ UTS             - 主机名/域名隔离                       │   │
│   │ IPC             - 进程间通信隔离 (共享内存、信号量等)   │   │
│   │ PID             - 进程ID空间隔离                        │   │
│   │ Network (net)   - 网络设备、端口、路由表隔离           │   │
│   │ User            - 用户/组ID隔离                         │   │
│   │ Cgroup          - Cgroup根目录隔离                      │   │
│   │ Time            - 系统时间隔离 (Linux 5.6+)            │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   隔离效果对比:                                                   │
│   ┌──────────────┬──────────┬─────────────┬──────────────┐     │
│   │   特性       │  chroot  │  Namespaces │   VM         │     │
│   ├──────────────┼──────────┼─────────────┼──────────────┤     │
│   │ 文件系统     │    ✓     │      ✓      │      ✓       │     │
│   │ 进程隔离     │    ✗     │      ✓      │      ✓       │     │
│   │ 网络隔离     │    ✗     │      ✓      │      ✓       │     │
│   │ 用户隔离     │    ✗     │      ✓      │      ✓       │     │
│   │ 硬件隔离     │    ✗     │      ✗      │      ✓       │     │
│   │ 性能开销     │   极低   │     低      │     中       │     │
│   └──────────────┴──────────┴─────────────┴──────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Namespaces 使用示例：**

```bash
# 查看当前进程的namespace
$ ls -la /proc/self/ns/
total 0
drwx--x--x 2 root root 0 Mar 30 10:00 .
dr-xr-xr-x 9 root root 0 Mar 30 10:00 ..
lrwxrwxrwx 1 root root 0 Mar 30 10:00 cgroup -> 'cgroup:[4026531835]'
lrwxrwxrwx 1 root root 0 Mar 30 10:00 ipc -> 'ipc:[4026531839]'
lrwxrwxrwx 1 root root 0 Mar 30 10:00 mnt -> 'mnt:[4026531840]'
lrwxrwxrwx 1 root root 0 Mar 30 10:00 net -> 'net:[4026532008]'
lrwxrwxrwx 1 root root 0 Mar 30 10:00 pid -> 'pid:[4026531836]'
lrwxrwxrwx 1 root root 0 Mar 30 10:00 user -> 'user:[4026531837]'
lrwxrwxrwx 1 root root 0 Mar 30 10:00 uts -> 'uts:[4026531838]'

# 使用unshare创建新的namespace
# 创建新的PID、网络、挂载namespace
$ sudo unshare --pid --net --mount --fork --mount-proc=/proc /bin/bash

# 在新namespace中
# PID 1是bash本身
$ ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0   7236  3840 pts/0    S    10:00   0:00 /bin/bash
root         2  0.0  0.0   8888  3200 pts/0    R+   10:00   0:00 ps aux

# 网络设备独立
$ ip link
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN mode DEFAULT
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

# 配置网络
$ ip link set lo up
$ ip addr add 10.0.0.1/24 dev lo
```

---

## Seccomp

Seccomp (Secure Computing Mode) 是Linux内核的系统调用过滤机制，限制进程可调用的系统调用。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Seccomp 工作原理                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   进程请求 ────▶ 系统调用 ────▶ Seccomp BPF过滤器              │
│                                    │                           │
│                               ┌────┴────┐                      │
│                               ▼         ▼                      │
│                            允许       拒绝                     │
│                               │         │                      │
│                               ▼         ▼                      │
│                           正常执行   终止进程(SIGSYS)           │
│                                                               │
│   Seccomp 模式:                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Mode 0 (SECCOMP_MODE_DISABLED) - 禁用seccomp           │   │
│   │  Mode 1 (SECCOMP_MODE_STRICT)   - 只允许read/write/exit │   │
│   │  Mode 2 (SECCOMP_MODE_FILTER)   - BPF过滤器规则          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   BPF规则示例逻辑:                                                │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  IF syscall == open THEN ALLOW                          │   │
│   │  IF syscall == read THEN ALLOW                          │   │
│   │  IF syscall == write AND fd == 1 THEN ALLOW             │   │
│   │  IF syscall == execve THEN DENY                         │   │
│   │  IF syscall == fork THEN DENY                           │   │
│   │  DEFAULT: DENY                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Seccomp 配置示例：**

```json
// Docker seccomp profile 示例
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_X86"],
  "syscalls": [
    {
      "names": [
        "accept",
        "accept4",
        "bind",
        "clone",
        "close",
        "connect",
        "epoll_create",
        "epoll_create1",
        "epoll_ctl",
        "epoll_pwait",
        "epoll_wait",
        "exit",
        "exit_group",
        "fcntl",
        "fstat",
        "fsync",
        "futex",
        "getcwd",
        "getpid",
        "getrandom",
        "ioctl",
        "listen",
        "mmap",
        "mprotect",
        "munmap",
        "nanosleep",
        "open",
        "openat",
        "poll",
        "read",
        "readv",
        "recvfrom",
        "recvmsg",
        "rt_sigaction",
        "rt_sigprocmask",
        "rt_sigreturn",
        "select",
        "sendmsg",
        "sendto",
        "sigaltstack",
        "socket",
        "socketpair",
        "write",
        "writev"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "names": ["execve", "execveat", "fork", "vfork"],
      "action": "SCMP_ACT_KILL"
    }
  ]
}
```

```python
# Python使用seccomp示例
import seccomp

# 创建过滤器
f = seccomp.SyscallFilter(seccomp.ALLOW)

# 添加拒绝规则
f.add_rule(seccomp.KILL, "execve")
f.add_rule(seccomp.KILL, "execveat")
f.add_rule(seccomp.KILL, "fork")
f.add_rule(seccomp.KILL, "vfork")
f.add_rule(seccomp.KILL, "ptrace")
f.add_rule(seccomp.KILL, "mount")
f.add_rule(seccomp.KILL, "umount2")
f.add_rule(seccomp.KILL, "chroot")

# 加载过滤器
f.load()

# 此后进程被限制，禁止执行上述系统调用
# 尝试执行会收到SIGSYS信号
import os
try:
    os.system("ls")  # 这将触发execve，被阻止
except Exception as e:
    print(f"Blocked: {e}")
```

---

## 容器安全 (Docker Security)

Docker 使用多层安全机制构建容器沙箱。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Docker 安全架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  容器镜像安全                                             │   │
│   │  • 使用官方/可信镜像                                      │   │
│   │  • 镜像签名验证 (Docker Content Trust)                   │   │
│   │  • 最小化镜像 (Alpine, distroless)                      │   │
│   │  • 定期扫描漏洞                                           │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  容器运行时安全                                           │   │
│   │  • Namespaces (PID, Network, Mount, IPC, UTS)          │   │
│   │  • CGroups (资源限制)                                    │   │
│   │  • Capabilities (能力降权)                               │   │
│   │  • Seccomp (系统调用过滤)                                │   │
│   │  • AppArmor/SELinux (强制访问控制)                       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  主机安全                                                 │   │
│   │  • User Namespaces (UID/GID映射)                        │   │
│   │  • Rootless Docker (无root运行)                         │   │
│   │  • 只读文件系统 (read-only rootfs)                      │   │
│   │  • 限制挂载 (--volume严格限制)                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Docker 安全配置示例：**

```bash
# 安全运行容器的最佳实践
$ docker run -d \
  --name secure-app \
  --read-only \\\n                      # 只读根文件系统
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \\  # 临时可写目录
  --tmpfs /var/tmp:rw,noexec,nosuid,size=100m \\
  --security-opt no-new-privileges:true \\    # 禁止提升特权
  --security-opt seccomp=/path/to/seccomp.json \\  # seccomp规则
  --cap-drop=ALL \\                           # 移除所有能力
  --cap-add=NET_BIND_SERVICE \\              # 只添加必要能力
  --user 1000:1000 \\                        # 非root用户运行
  --memory=512m \\                           # 内存限制
  --cpus=1.0 \\                              # CPU限制
  --pids-limit=100 \\                        # 进程数限制
  --network=none \\                          # 无网络(如不需要)
  --device-cgroup-rule='c 1:3 rm' \\         # 限制设备访问
  -v /host/data:/app/data:ro \\             # 只读挂载
  myapp:latest

# 使用gVisor运行容器 (更强的隔离)
$ docker run --runtime=runsc -d myapp:latest
```

---

## gVisor 与 Firecracker

### gVisor

gVisor 是 Google 开发的用户态内核，为容器提供更强的隔离。

```
┌─────────────────────────────────────────────────────────────────┐
│                   gVisor 架构                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   传统容器:                                                       │
│   ┌─────────┐     ┌─────────────────────────────────────────┐   │
│   │ 应用    │────▶│ 主机内核 (共享)                          │   │
│   └─────────┘     └─────────────────────────────────────────┘   │
│                                                                 │
│   gVisor容器:                                                     │
│   ┌─────────┐     ┌─────────┐     ┌─────────────────────────┐   │
│   │ 应用    │────▶│ Sentry  │────▶│ 主机内核 (最小syscall)  │   │
│   │         │     │ (用户态 │     │                         │   │
│   │         │     │  内核)  │     │  仅使用: open/read/     │   │
│   │         │     │         │     │         write/close/    │   │
│   │         │     │ • 实现  │     │         mmap/select/    │   │
│   │         │     │   大部分│     │         epoll等         │   │
│   │         │     │   系统  │     │                         │   │
│   │         │     │   调用  │     │                         │   │
│   └─────────┘     └─────────┘     └─────────────────────────┘   │
│                                                                 │
│   Gofer进程 (独立): 处理文件系统访问                             │
│   ┌─────────┐                                                   │
│   │  Sentry │────▶ Gofer ────▶ 主机文件系统                     │
│   └─────────┘                                                   │
│                                                                 │
│   优势: 攻击面极小，即使容器突破也只能访问Sentry                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**gVisor 使用：**

```bash
# 安装gVisor
$ curl -fsSL https://gvisor.dev/install.sh | bash

# 配置Docker使用gVisor
$ sudo runsc install
$ sudo systemctl reload docker

# 使用gVisor运行容器
$ docker run --runtime=runsc -it ubuntu bash

# 调试gVisor
$ runsc --debug --debug-log=/tmp/runsc/ run mycontainer
```

### Firecracker

Firecracker 是 AWS 开发的 MicroVM 运行时，专为无服务器和容器优化。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Firecracker MicroVM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Host OS                                                │   │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│   │  │  MicroVM 1   │  │  MicroVM 2   │  │  MicroVM N   │  │   │
│   │  │  ┌────────┐  │  │  ┌────────┐  │  │  ┌────────┐  │  │   │
│   │  │  │Guest OS│  │  │  │Guest OS│  │  │  │Guest OS│  │  │   │
│   │  │  │┌──────┐│  │  │  │┌──────┐│  │  │  │┌──────┐│  │  │   │
│   │  │  ││ App  ││  │  │  ││ App  ││  │  │  ││ App  ││  │  │   │
│   │  │  │└──────┘│  │  │  │└──────┘│  │  │  │└──────┘│  │  │   │
│   │  │  └────────┘  │  │  └────────┘  │  │  └────────┘  │  │   │
│   │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│   │                                                         │   │
│   │  Firecracker VMM (虚拟化管理器)                         │   │
│   │  • 基于KVM                                              │   │
│   │  • 启动时间 < 125ms                                     │   │
│   │  • 内存开销 < 5MB                                       │   │
│   │  • 每个Host可运行数千MicroVM                            │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   使用场景: AWS Lambda, AWS Fargate                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 浏览器沙箱

现代浏览器使用多层沙箱保护用户系统。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Chrome 沙箱架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   浏览器进程 (Browser Process) - 可信                           │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  • UI管理                                                │   │
│   │  • 网络请求                                              │   │
│   │  • 标签页管理                                            │   │
│   │  • 扩展管理                                              │   │
│   └─────────────────────────────────────────────────────────┘   │
│          │                                                      │
│    ┌─────┼─────┬─────────┬─────────┐                           │
│    ▼     ▼     ▼         ▼         ▼                           │
│ ┌────┐┌────┐┌────┐  ┌────┐   ┌────┐                           │
│ │GPU ││Net ││GPU │  │Tab1│   │Tab2│  ... 渲染进程 (Renderer)   │
│ │Proc││Proc││Proc│  │Proc│   │Proc│      不可信，严格沙箱      │
│ └────┘└────┘└────┘  └────┘   └────┘                           │
│                      │    │                                    │
│                      ▼    ▼                                    │
│                ┌─────────────────┐                             │
│                │ 沙箱机制:        │                             │
│                │ • Namespaces    │                             │
│                │ • Seccomp-BPF   │                             │
│                │ • Chroot        │                             │
│                │ • UID隔离       │                             │
│                └─────────────────┘                             │
│                                                                 │
│   渲染进程只能访问:                                               │
│   • 通过IPC与浏览器进程通信                                       │
│   • 有限的系统调用                                                │
│   • 无法直接访问文件系统、网络、设备                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 最佳实践

```
┌─────────────────────────────────────────────────────────────────┐
│                   沙箱技术最佳实践                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ □ 多层防御                                                       │
│   □ 不依赖单一沙箱机制                                          │
│   □ 组合使用 namespaces + seccomp + capabilities               │
│   □ 对高危应用使用 gVisor/Firecracker                           │
│                                                                 │
│ □ 最小权限                                                       │
│   □ 默认deny所有系统调用，白名单允许                              │
│   □ 移除所有capabilities，按需添加                                │
│   □ 只读文件系统 + 必要的tmpfs                                   │
│                                                                 │
│ □ 资源限制                                                       │
│   □ CPU、内存、磁盘配额                                          │
│   □ 进程数限制                                                   │
│   □ 网络带宽限制                                                 │
│                                                                 │
│ □ 监控与审计                                                     │
│   □ 记录沙箱逃逸尝试                                             │
│   □ 监控资源使用                                                 │
│   □ 异常行为检测                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

### 常见问题

**Q1: chroot和容器的主要区别是什么？**
> chroot只隔离文件系统视图，不隔离进程、网络、用户等资源；容器使用namespaces隔离PID、网络、挂载点、IPC、UTS等资源，使用cgroups限制资源使用，使用capabilities和seccomp限制权限。chroot是基础机制，容器是完整解决方案。

**Q2: seccomp如何增强容器安全？**
> seccomp通过BPF过滤器限制进程可调用的系统调用。即使攻击者获取容器内shell，也无法执行危险的系统调用（如mount、ptrace、open_by_handle_at等），大幅减小攻击面。Docker默认启用seccomp，只允许约44个系统调用。

**Q3: gVisor和KVM虚拟机的区别？**
> gVisor是在用户空间实现大部分Linux系统调用的沙箱，拦截应用syscall并由Sentry处理，只有必要调用才转发给主机内核；KVM是硬件虚拟化，需要完整的Guest OS。gVisor启动更快、资源占用更少，但兼容性和性能略低于KVM。

**Q4: 如何防范容器逃逸？**
> 1) 使用User Namespaces映射root到非特权用户；2) 启用seccomp和AppArmor/SELinux；3) 移除 unnecessary capabilities；4) 使用read-only rootfs；5) 限制挂载敏感目录；6) 及时更新内核修复漏洞；7) 考虑使用gVisor/Firecracker。

---

## 相关概念

- [访问控制](./access-control.md) - 沙箱内的权限管理
- [内存安全](./memory-safety.md) - 内存隔离机制
- [特权提升](./privilege-escalation.md) - 沙箱逃逸技术
- [安全启动](./secure-boot.md) - 可信启动链与沙箱完整性
- [审计日志](./audit-logging.md) - 沙箱行为监控与审计
- [进程](../../computer-science/systems/process.md) - 进程隔离机制
- [虚拟内存](../../computer-science/systems/virtual-memory.md) - 内存隔离与地址空间
- [认证](../../authentication.md) - 沙箱环境中的身份验证
- [授权](../../authorization.md) - 沙箱权限模型
- [Docker Security](https://docs.docker.com/engine/security/)
- [内存安全](./memory-safety.md) - 内存隔离机制
- [特权提升](./privilege-escalation.md) - 沙箱逃逸技术
- [Docker Security](https://docs.docker.com/engine/security/)

---

## 参考资料

1. Linux Namespaces Man Page: namespaces(7)
2. Seccomp Documentation: https://www.kernel.org/doc/Documentation/prctl/seccomp_filter.txt
3. gVisor Documentation: https://gvisor.dev/docs/
4. Firecracker Documentation: https://firecracker-microvm.github.io/
5. Docker Security Documentation
6. "The Art of Software Security Assessment" by Mark Dowd
