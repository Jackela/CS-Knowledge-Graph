# Kubernetes 安全 (Kubernetes Security)

Kubernetes 安全涵盖 K8s 集群的各个方面，包括容器安全、网络安全、访问控制和运行时安全。

## 安全层次

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes 安全层次                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  集群安全 (Cluster Security)                                 │
│  ├── API Server 安全配置                                      │
│  ├── etcd 加密                                               │
│  └── Controller Manager 安全                                 │
│                                                             │
│  节点安全 (Node Security)                                    │
│  ├── 主机加固                                                │
│  ├── Kubelet 安全                                            │
│  └── 容器运行时安全                                          │
│                                                             │
│  网络安全 (Network Security)                                 │
│  ├── 网络策略                                                │
│  ├── Service Mesh                                            │
│  └── 入口/出口控制                                           │
│                                                             │
│  应用安全 (Application Security)                             │
│  ├── Pod 安全标准                                            │
│  ├── 镜像安全                                                │
│  └── 密钥管理                                                │
│                                                             │
│  数据安全 (Data Security)                                    │
│  ├── 存储加密                                                │
│  ├── 备份安全                                                │
│  └── 持久卷安全                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## API Server 安全

### 访问控制
```yaml
# API Server 安全配置
apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority: /etc/kubernetes/pki/ca.crt
    server: https://127.0.0.1:6443
  name: kubernetes
current-context: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: admin
  name: kubernetes
users:
- name: admin
  user:
    client-certificate: /etc/kubernetes/pki/admin.crt
    client-key: /etc/kubernetes/pki/admin.key
```

### 审计日志
```yaml
# 审计策略
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# 记录所有请求
- level: Metadata
  # 排除健康检查
  omitStages:
  - RequestReceived
  
# 记录敏感资源的详细日志
- level: RequestResponse
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
  namespaces: ["kube-system", "production"]
```

## 网络安全

### 网络策略
```yaml
# 默认拒绝所有流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---

# 允许特定流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  - from:  # 允许监控
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090
```

## 密钥管理

### Secrets 加密
```yaml
# 使用 KMS 加密 Secrets
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    - configmaps
    providers:
    - kms:
        apiVersion: v2
        name: myKMSPlugin
        endpoint: unix:///var/run/k8s-kms-plugin/socket.sock
        cachesize: 1000
        timeout: 3s
    - aescbc:
        keys:
        - name: key1
          secret: <base64-encoded-32-byte-key>
    - identity: {}
```

## 运行时安全

### Falco 规则
```yaml
# 检测异常行为
- rule: Unauthorized K8s API Access
  desc: Detect unauthorized access to K8s API
  condition: >
    spawned_process and
    (proc.name in ("kubectl", "helm")) and
    not user.name in ("admin", "devops")
  output: >
    Unauthorized K8s access
    user=%user.name command=%proc.cmdline
  priority: WARNING

- rule: Privileged Container Started
  desc: Detect privileged container creation
  condition: >
    spawned_process and
    container and
    container.privileged=true
  output: >
    Privileged container started
    user=%user.name container=%container.name
  priority: CRITICAL
```

## 安全扫描清单

| 检查项 | 工具 | 优先级 |
|--------|------|--------|
| CIS Benchmark | kube-bench | 高 |
| 镜像漏洞扫描 | Trivy | 高 |
| RBAC 审计 | kubectl auth can-i | 高 |
| 网络策略检查 | network-policy-checker | 中 |
| 密钥扫描 | detect-secrets | 高 |

## 相关概念

### 容器安全
- [容器安全](../application-security/container-security.md) - 容器化应用安全
- [Pod 安全策略](../application-security/pod-security-policy.md) - Pod 安全配置
- [Secrets 管理](../application-security/secrets-management.md) - K8s Secrets 管理

### 访问控制

### 访问控制
- [RBAC](../rbac.md) - 基于角色的访问控制
- [网络策略](../network-security/network-policy.md) - 网络隔离

### DevOps
- [DevSecOps](../application-security/devsecops.md) - 安全左移实践
- [Kubernetes](../../cloud-devops/kubernetes.md) - K8s 平台基础
