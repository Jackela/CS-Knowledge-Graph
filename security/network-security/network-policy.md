# 网络策略 (Network Policy)

网络策略（Network Policy）是 Kubernetes 中用于控制 Pod 间网络流量的安全机制，定义了哪些 Pod 可以相互通信。

## 核心概念

### 网络策略模型

```
┌─────────────────────────────────────────────────────────────┐
│                   网络策略模型                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   默认状态（无策略）：                                         │
│   ┌─────┐ ◀───────▶ ┌─────┐ ◀───────▶ ┌─────┐             │
│   │ Pod │           │ Pod │           │ Pod │             │
│   │  A  │ ◀───────▶ │  B  │ ◀───────▶ │  C  │             │
│   └─────┘           └─────┘           └─────┘             │
│                                                             │
│   应用网络策略后：                                           │
│   ┌─────┐          ┌─────┐          ┌─────┐               │
│   │ Pod │◀────────▶│ Pod │◀────────▶│ Pod │               │
│   │  A  │   允许    │  B  │   拒绝    │  C  │               │
│   └─────┘          └─────┘          └─────┘               │
│                                                             │
│   默认拒绝所有流量，只允许白名单中的通信                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 网络策略配置

### 默认拒绝所有入站流量

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}  # 选择所有 Pod
  policyTypes:
  - Ingress        # 仅限制入站
```

### 允许特定 Pod 通信

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow
spec:
  podSelector:
    matchLabels:
      app: api      # 应用于 api Pod
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend  # 只允许 frontend 访问
    ports:
    - protocol: TCP
      port: 8080
```

### 命名空间隔离

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: namespace-isolation
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector: {}  # 允许同一命名空间
    - namespaceSelector:
        matchLabels:
          name: trusted  # 允许特定命名空间
  egress:
  - to:
    - podSelector: {}  # 允许访问同一命名空间
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system  # 允许访问 kube-system
```

## 网络策略规则

### 选择器类型

| 选择器 | 说明 | 示例 |
|--------|------|------|
| podSelector | 选择 Pod | app: frontend |
| namespaceSelector | 选择命名空间 | name: production |
| ipBlock | 选择 IP 段 | 10.0.0.0/8 |

### 策略类型

```yaml
policyTypes:
- Ingress  # 入站规则
- Egress   # 出站规则
```

## 最佳实践

### 1. 默认拒绝

```yaml
# 每个命名空间启用默认拒绝
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### 2. 按层划分

```
┌─────────────┐
│   Ingress   │  入口层（只允许外部访问）
├─────────────┤
│   Frontend  │  前端层（只允许 Ingress 访问）
├─────────────┤
│    API      │  API层（只允许 Frontend 访问）
├─────────────┤
│   Database  │  数据层（只允许 API 访问）
└─────────────┘
```

### 3. 显式允许 DNS

```yaml
egress:
- to:
  - namespaceSelector:
      matchLabels:
        name: kube-system
  ports:
  - protocol: UDP
    port: 53  # DNS
```

## 常见网络插件

| 插件 | 支持 NetworkPolicy | 特点 |
|------|-------------------|------|
| Calico | ✅ | 功能全面，性能优秀 |
| Cilium | ✅ | eBPF 加速，可观测性好 |
| Weave | ✅ | 简单易用 |
| Flannel | ❌ | 简单网络，不支持策略 |

## 面试要点

**Q: NetworkPolicy 和 Service 的区别？**

**A:**
- **Service**: 提供服务发现和负载均衡，控制流量目的地
- **NetworkPolicy**: 控制 Pod 间是否允许通信，是安全策略

**Q: 为什么配置了 NetworkPolicy 但没有生效？**

**A:**
1. 网络插件不支持 NetworkPolicy（如 Flannel）
2. 选择器不匹配任何 Pod
3. 规则顺序问题（NetworkPolicy 是累加的）

## 相关概念

- [Kubernetes 安全](../system-security/kubernetes-security.md) - K8s 安全实践
- [容器安全](../application-security/container-security.md) - 容器网络安全
- [防火墙](./firewalls.md) - 网络层访问控制
- [Service Mesh](../../software-engineering/architecture-patterns/service-mesh.md) - 应用层流量管理

## 参考资料

1. [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
2. Calico Network Policy Guide
