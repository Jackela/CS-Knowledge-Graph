# 容器安全 (Container Security)

容器安全是保护容器化应用及其运行时环境免受威胁和漏洞影响的安全实践。它覆盖容器生命周期的各个阶段：构建、分发和运行。

## 核心概念

### 容器安全层次

```
┌─────────────────────────────────────────────────────────────┐
│                   容器安全层次                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  镜像安全 (Image Security)                                   │
│  ├── 基础镜像选择                                            │
│  ├── 漏洞扫描                                                │
│  └── 镜像签名验证                                            │
│                                                             │
│  运行时安全 (Runtime Security)                               │
│  ├── 容器隔离                                                │
│  ├── 资源限制                                                │
│  └── 行为监控                                                │
│                                                             │
│  编排安全 (Orchestration Security)                           │
│  ├── Pod 安全策略                                            │
│  ├── 网络策略                                                │
│  └── RBAC 权限控制                                           │
│                                                             │
│  主机安全 (Host Security)                                    │
│  ├── 主机加固                                                │
│  ├── 容器运行时选择                                          │
│  └── 审计与监控                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 镜像安全

### 镜像漏洞扫描

```
扫描流程：

镜像构建 ──▶ 推送到仓库 ──▶ 自动扫描 ──▶ 漏洞报告
                                 │
                                 ▼
                    高风险漏洞？──是──▶ 阻断部署
                        │
                        否
                        ▼
                    允许部署
```

### 常用扫描工具

| 工具 | 特点 | 集成方式 |
|------|------|----------|
| Trivy | 快速、全面 | CLI、CI/CD、K8s Operator |
| Clair | 静态分析 | Harbor、Quay 集成 |
| Snyk | 商业支持 | 多平台集成 |
| Grype | Anchore 出品 | CLI、CI/CD |

### 镜像安全最佳实践

```dockerfile
# ❌ 不安全：使用 latest 标签
FROM ubuntu:latest

# ✅ 安全：使用特定版本和最小基础镜像
FROM alpine:3.18.4

# ❌ 不安全：以 root 运行
USER root

# ✅ 安全：创建非特权用户
RUN addgroup -g 1000 appgroup && \
    adduser -u 1000 -G appgroup -s /bin/sh -D appuser
USER appuser

# ❌ 不安全：包含敏感信息
ENV PASSWORD=secret123

# ✅ 安全：使用多阶段构建减少攻击面
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o main

FROM scratch
COPY --from=builder /app/main /main
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
ENTRYPOINT ["/main"]
```

## 运行时安全

### 容器隔离机制

```
容器隔离技术：

1. Namespace 隔离
   ├── PID Namespace - 进程隔离
   ├── Network Namespace - 网络隔离
   ├── Mount Namespace - 文件系统隔离
   ├── IPC Namespace - 进程间通信隔离
   └── UTS Namespace - 主机名隔离

2. Cgroups 资源限制
   ├── CPU 限制
   ├── 内存限制
   ├── IO 限制
   └── 网络带宽限制

3. Capabilities
   ├── 细粒度权限控制
   └── 默认丢弃 root 能力

4. Seccomp
   └── 系统调用过滤
```

### 安全上下文配置

```yaml
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true        # 禁止 root 运行
    runAsUser: 1000           # 指定用户 ID
    runAsGroup: 1000          # 指定组 ID
    fsGroup: 1000             # 卷挂载的组权限
    seccompProfile:
      type: RuntimeDefault    # 使用默认 Seccomp 配置
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false   # 禁止特权提升
      readOnlyRootFilesystem: true      # 只读根文件系统
      capabilities:
        drop:
        - ALL                          # 丢弃所有能力
        add:
        - NET_BIND_SERVICE             # 仅添加必要能力
    resources:
      limits:
        cpu: "500m"
        memory: "512Mi"
```

## 编排安全

### Pod 安全标准

```yaml
# Pod Security Standards 三个级别

# 1. privileged - 无限制
# 2. baseline - 最小限制（推荐默认）
# 3. restricted - 严格限制

apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 网络策略

```yaml
# 限制 Pod 间通信
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
# 仅允许特定流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

## 容器运行时安全

### 运行时安全工具

| 工具 | 功能 | 特点 |
|------|------|------|
| Falco | 运行时威胁检测 | CNCF 项目，基于规则 |
| Sysdig | 监控与安全 | 商业支持，功能全面 |
| Tracee | 运行时安全 | Aqua Security 出品 |

### Falco 规则示例

```yaml
- rule: Unauthorized container modification
  desc: Detect write to container filesystem
  condition: >
    spawned_process and
    container and
    (proc.name in ("bash", "sh", "python")) and
    user.name != "_apt"
  output: >
    Unexpected process in container
    user=%user.name command=%proc.cmdline container=%container.name
  priority: WARNING
```

## 供应链安全

### 镜像签名与验证

```
镜像签名流程：

构建镜像 ──▶ 签名镜像 ──▶ 推送仓库
                 ↑
            Cosign/Notation
                 
部署时验证签名：

准入控制器 ──▶ 验证签名 ──▶ 允许/拒绝部署
```

### Cosign 使用示例

```bash
# 生成密钥对
cosign generate-key-pair

# 签名镜像
cosign sign --key cosign.key myregistry.io/myimage:1.0

# 验证镜像
cosign verify --key cosign.pub myregistry.io/myimage:1.0

# Kubernetes 策略验证（Kyverno）
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  validationFailureAction: enforce
  rules:
  - name: check-image-signature
    match:
      resources:
        kinds:
        - Pod
    verifyImages:
    - imageReferences:
      - "myregistry.io/*"
      attestors:
      - entries:
        - keys:
            publicKeys: |
              -----BEGIN PUBLIC KEY-----
              ...
              -----END PUBLIC KEY-----
```

## 安全扫描与合规

### CIS Docker Benchmark

```
安全检查清单：

1. 主机配置
   □ 创建专用的容器用户
   □ 加固 Docker 守护进程
   
2. Docker 守护进程配置
   □ 启用用户命名空间
   □ 限制默认能力集
   
3. Docker 守护进程文件
   □ 正确的文件权限
   □ 审计日志配置
   
4. 容器镜像和构建
   □ 使用官方镜像
   □ 定期扫描漏洞
   
5. 容器运行时
   □ 启用 AppArmor/SELinux
   □ 设置资源限制
```

## 相关概念 (Related Concepts)

### DevOps 与安全
- [Web 安全](../web-security.md) - Web 应用安全实践
- [DevSecOps](./devsecops.md) - 安全左移实践
- [CI/CD 安全](./cicd-security.md) - 流水线安全

### Kubernetes
- [Kubernetes](../../cloud-devops/kubernetes.md) - 容器编排平台
- [Kubernetes 安全](../system-security/kubernetes-security.md) - K8s 安全实践
- [Pod 安全策略](./pod-security-policy.md) - Pod 安全配置
- [RBAC](../system-security/rbac.md) - 基于角色的访问控制

### 应用安全
- [API 安全](./api-security.md) - API 安全最佳实践

## 参考资料

1. NIST SP 800-190 - Application Container Security Guide
2. CIS Docker Benchmark v1.5.0
3. CNCF Cloud Native Security Whitepaper
4. Aqua Security - Container Security Guide
5. Snyk Container Security Report
