# Kubernetes Services (K8s 服务)

## 简介

**Kubernetes Service** 是 Kubernetes 中用于暴露一组 Pod 的网络服务的抽象层。由于 Pod 是动态创建和销毁的，其 IP 地址不固定，Service 提供了稳定的网络端点和负载均衡能力，使客户端能够可靠地访问后端 Pod。

## 核心概念

- **ClusterIP**：默认类型，仅在集群内部暴露服务，分配集群内部 IP
- **NodePort**：在每个节点的 IP 上暴露服务，通过静态端口（30000-32767）访问
- **LoadBalancer**：使用云提供商的负载均衡器暴露服务，适用于公有云环境
- **ExternalName**：将服务映射到外部 DNS 名称，不创建代理
- **Endpoint/EndpointSlice**：Service 后端 Pod 的地址集合，由 kube-proxy 维护
- **Selector**：标签选择器，用于将 Service 与匹配的 Pod 关联

## 架构原理

### Service 工作原理

```
┌─────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster                  │
│  ┌─────────────┐      ┌─────────────┐     ┌──────────┐  │
│  │   Client    │─────▶│   Service   │────▶│  Pod 1   │  │
│  │  (Cluster)  │      │  (ClusterIP)│     └──────────┘  │
│  └─────────────┘      │   10.0.0.1  │────▶┌──────────┐  │
│                       └─────────────┘     │  Pod 2   │  │
│                             │             └──────────┘  │
│                             └──────────▶┌──────────┐    │
│                                         │  Pod 3   │    │
│                                         └──────────┘    │
└─────────────────────────────────────────────────────────┘
```

### kube-proxy 实现模式

- **iptables 模式**（默认）：使用 iptables 规则实现负载均衡，性能高
- **ipvs 模式**：使用 Linux IPVS 实现，支持更多负载均衡算法
- **userspace 模式**（已废弃）：早期实现，性能较差

## 实现方式

### ClusterIP 服务

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: default
  labels:
    app: backend
    tier: api
spec:
  type: ClusterIP
  selector:
    app: backend
    tier: api
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: 9090
      protocol: TCP
  sessionAffinity: None
  publishNotReadyAddresses: false
```

### NodePort 服务

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
  namespace: default
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - name: http
      port: 80
      targetPort: 8080
      nodePort: 30080
      protocol: TCP
    - name: https
      port: 443
      targetPort: 8443
      nodePort: 30443
      protocol: TCP
  externalTrafficPolicy: Local
  healthCheckNodePort: 32000
```

### LoadBalancer 服务

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-loadbalancer
  namespace: production
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-protocol: "http"
spec:
  type: LoadBalancer
  selector:
    app: api-gateway
  ports:
    - name: https
      port: 443
      targetPort: 8443
      protocol: TCP
  loadBalancerSourceRanges:
    - 10.0.0.0/8
    - 172.16.0.0/12
  externalTrafficPolicy: Local
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

### ExternalName 服务

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-database
  namespace: default
spec:
  type: ExternalName
  externalName: prod-db.example.com
```

### Headless 服务

```yaml
apiVersion: v1
kind: Service
metadata:
  name: stateful-app-headless
  namespace: default
spec:
  type: ClusterIP
  clusterIP: None
  selector:
    app: stateful-app
  ports:
    - name: http
      port: 80
      targetPort: 8080
```

### 无选择器服务（手动端点）

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-service
  namespace: default
spec:
  type: ClusterIP
  ports:
    - name: http
      port: 80
      targetPort: 8080
---
apiVersion: v1
kind: Endpoints
metadata:
  name: external-service
  namespace: default
subsets:
  - addresses:
      - ip: 192.168.1.100
      - ip: 192.168.1.101
    ports:
      - name: http
        port: 8080
```

## 服务发现机制

### DNS 发现

Kubernetes 内置 CoreDNS 提供服务发现：

```bash
# 同一命名空间
<service-name>

# 跨命名空间
<service-name>.<namespace>.svc.cluster.local

# 完整 FQDN
<service-name>.<namespace>.svc.cluster.local
```

### 环境变量发现

```bash
# 每个 Pod 自动注入的环境变量
WEB_SERVICE_SERVICE_HOST=10.0.0.1
WEB_SERVICE_SERVICE_PORT=80
WEB_SERVICE_PORT=tcp://10.0.0.1:80
WEB_SERVICE_PORT_80_TCP=tcp://10.0.0.1:80
WEB_SERVICE_PORT_80_TCP_ADDR=10.0.0.1
WEB_SERVICE_PORT_80_TCP_PORT=80
WEB_SERVICE_PORT_80_TCP_PROTO=tcp
```

## 应用场景

- **微服务内部通信**：通过 ClusterIP 实现服务间调用
- **外部流量入口**：NodePort 或 LoadBalancer 暴露服务到外部
- **有状态应用**：Headless Service 配合 StatefulSet 实现 Pod 直接访问
- **外部服务代理**：ExternalName 将外部服务纳入 Kubernetes 服务发现
- **数据库集群**：Headless Service 实现数据库节点发现和直连

## 流量策略

### externalTrafficPolicy

```yaml
spec:
  externalTrafficPolicy: Local  # 或 Cluster
```

- **Cluster**（默认）：流量可路由到任意节点，再转发到目标 Pod，可能经过额外跳数
- **Local**：流量只路由到运行目标 Pod 的节点，保留客户端源 IP，但负载可能不均衡

### sessionAffinity

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3小时
```

- **None**（默认）：无会话保持，请求随机分发
- **ClientIP**：基于客户端 IP 的会话保持

## 健康检查与就绪探测

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
    - port: 80
  publishNotReadyAddresses: false  # 不将未就绪 Pod 加入端点
```

配合 Pod 就绪探针：

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: app
      readinessProbe:
        httpGet:
          path: /ready
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 10
```

## 面试要点

1. **Q: Kubernetes Service 的底层实现原理是什么？**
   A: Service 通过 kube-proxy 组件实现，默认使用 iptables 模式创建 DNAT 规则，将访问 Service ClusterIP 的流量转发到后端 Pod。现代版本推荐使用 IPVS 模式，支持更多负载均衡算法和更好的性能。

2. **Q: ClusterIP、NodePort、LoadBalancer 的区别和适用场景？**
   A: ClusterIP 仅在集群内部访问，适合服务间通信；NodePort 在每个节点开放端口（30000-32767），适合开发测试或没有负载均衡器的环境；LoadBalancer 使用云厂商 LB，适合生产环境直接暴露服务。

3. **Q: 什么是 Headless Service？有什么用途？**
   A: Headless Service 设置 clusterIP: None，不分配虚拟 IP，直接返回后端 Pod 的 IP 列表。用于有状态应用（如数据库集群）需要直接访问特定 Pod 的场景，配合 StatefulSet 使用。

4. **Q: externalTrafficPolicy: Local 和 Cluster 的区别？**
   A: Local 模式下流量只路由到运行目标 Pod 的节点，保留客户端真实 IP，但可能导致节点间负载不均；Cluster 模式允许流量先到达任意节点再转发，负载更均衡但会丢失源 IP（看到的是节点 IP）。

5. **Q: 如何实现会话保持（Session Affinity）？**
   A: 设置 spec.sessionAffinity: ClientIP，基于客户端 IP 进行会话保持。可通过 sessionAffinityConfig.clientIP.timeoutSeconds 配置超时时间（默认 10800 秒）。注意这仅在客户端 IP 不变时有效，不适用于经过 NAT 的场景。

6. **Q: Service 如何选择后端 Pod？**
   A: 通过 spec.selector 标签选择器匹配 Pod。只有同时满足所有 selector 条件的 Pod 才会被纳入端点列表。Pod 必须处于 Running 状态且通过 readinessProbe 才会接收流量。

7. **Q: Endpoint 和 EndpointSlice 的区别？**
   A: Endpoint 早期用于存储 Service 后端地址，但在大规模集群中性能较差；EndpointSlice 是 v1.21+ 的替代方案，将端点分片存储，支持更大规模的端点数量，是现在的推荐方式。

## 相关概念

### Cloud & DevOps
- [Kubernetes](./kubernetes.md) - 容器编排平台概览
- [Pods](./pods.md) - Service 的后端工作负载
- [Ingress](./ingress.md) - 七层流量入口
- [Deployments](./deployments.md) - 应用部署管理
- [Helm](./helm.md) - Kubernetes 包管理

### 系统实现
- [负载均衡](../computer-science/distributed-systems/load-balancing.md) - 流量分发原理
- [DNS 原理](../computer-science/systems/network-security.md) - 服务发现机制
- [网络协议](../computer-science/systems/network-security.md) - TCP/IP 通信基础
- [进程管理](../computer-science/systems/process.md) - 容器进程管理
