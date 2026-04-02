# Pod 安全策略 (Pod Security Policy)

Pod 安全策略是 Kubernetes 中用于控制 Pod 安全上下文的准入控制器，定义了 Pod 必须满足的安全条件才能被创建。

## Pod 安全标准

Kubernetes 定义了三个安全级别：

### 1. Privileged (特权)
```yaml
# 无限制，允许所有配置
# 适用于：系统级基础设施组件
namespace:
  labels:
    pod-security.kubernetes.io/enforce: privileged
```

### 2. Baseline (基线)
```yaml
# 最小限制，防止已知特权升级
# 适用于：默认应用部署
namespace:
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/warn: baseline

# 主要限制：
# - 禁止共享主机命名空间
# - 禁止特权容器
# - 限制卷类型
# - 禁止 hostPath 卷
```

### 3. Restricted (受限)
```yaml
# 最严格，遵循 Pod 强化最佳实践
# 适用于：安全敏感应用
namespace:
  labels:
    pod-security.kubernetes.io/enforce: restricted

# 主要限制：
# - 必须以非 root 运行
# - 禁止特权提升
# - 只读根文件系统
# - 丢弃所有 capabilities
```

## 安全配置示例

### Restricted 级别 Pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true        # 禁止 root 用户
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault    # 使用默认 seccomp 配置
      
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false   # 禁止特权提升
      readOnlyRootFilesystem: true      # 只读根文件系统
      capabilities:
        drop:
        - ALL                          # 丢弃所有 capabilities
    resources:
      limits:
        cpu: "500m"
        memory: "512Mi"
      requests:
        cpu: "100m"
        memory: "128Mi"
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: cache
      mountPath: /cache
      
  volumes:
  - name: tmp
    emptyDir: {}              # 临时目录
  - name: cache
    emptyDir:
      sizeLimit: 100Mi
```

## 迁移路径

```
Pod Security Policy (已弃用) ──▶ Pod Security Standards

旧版 PSP 配置：
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  runAsUser:
    rule: MustRunAsNonRoot

新版 PSS 配置：
namespace 标签：
  pod-security.kubernetes.io/enforce: restricted
```

## 相关概念

### Kubernetes 安全
- [Kubernetes 安全](../system-security/kubernetes-security.md) - K8s 安全概述
- [容器安全](./container-security.md) - 容器运行时安全
- [网络策略](../network-security/network-policy.md) - Pod 间网络隔离

### 访问控制
- [RBAC](../rbac.md) - 基于角色的访问控制
- [访问控制](../access-control.md) - 访问控制概述
