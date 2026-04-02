# Kubernetes 网络 (K8s Networking)

## 简介

**Kubernetes 网络** 为容器化应用提供了完整的网络解决方案，包括 Pod 间通信、服务发现、外部访问和网络隔离。Kubernetes 网络模型遵循 "每个 Pod 都有独立 IP" 的扁平网络设计，简化了服务间通信，无需显式创建端口映射。网络功能通过 CNI（Container Network Interface）插件实现，支持多种网络方案。

## 核心概念

| 概念 | 英文 | 说明 |
|------|------|------|
| **Service** | 服务 | 为一组 Pod 提供稳定的网络端点和负载均衡 |
| **ClusterIP** | 集群 IP | 默认 Service 类型，仅在集群内部可访问 |
| **NodePort** | 节点端口 | 在每个节点上开放端口，暴露服务到外部 |
| **LoadBalancer** | 负载均衡器 | 使用云厂商负载均衡器暴露服务 |
| **Ingress** | 入口 | 七层流量路由，提供 HTTP/HTTPS 访问 |
| **NetworkPolicy** | 网络策略 | 定义 Pod 间的网络访问规则，实现隔离 |
| **CNI** | 容器网络接口 | 标准化的网络插件接口 |
| **CoreDNS** | 集群 DNS | 提供服务发现能力的内置 DNS |

## 网络架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Kubernetes 网络架构                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         外部流量入口                              │   │
│  │  ┌────────────┐    ┌────────────┐    ┌────────────────────────┐ │   │
│  │  │   Ingress  │    │ LoadBalancer│   │       NodePort         │ │   │
│  │  │  (L7 HTTP) │    │   (L4 TCP)  │   │   (NodeIP:Port)        │ │   │
│  │  └─────┬──────┘    └─────┬──────┘    └───────────┬────────────┘ │   │
│  └────────┼────────────────┼───────────────────────┼──────────────┘   │
│           └────────────────┴───────────────────────┘                   │
│                              │                                         │
│                              ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        Service 层                                │   │
│  │     ClusterIP: 10.96.0.0/12 (默认)    kube-proxy 负载均衡        │   │
│  └────────────────────────┬────────────────────────────────────────┘   │
│                           │                                            │
│           ┌───────────────┼───────────────┐                            │
│           ▼               ▼               ▼                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        Pod 网络层 (CNI)                          │   │
│  │     Pod IP: 10.244.0.0/16 (默认)    每个 Pod 独立 IP             │   │
│  │                                                                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │  Pod 1   │  │  Pod 2   │  │  Pod 3   │  │  Pod N   │        │   │
│  │  │10.244.1.2│  │10.244.1.3│  │10.244.2.2│  │10.244.2.3│        │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 实现方式

### 1. Service - ClusterIP

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: default
spec:
  type: ClusterIP           # 默认类型
  selector:
    app: backend
    tier: api
  ports:
    - name: http
      port: 80              # Service 暴露的端口
      targetPort: 8080      # 后端 Pod 的端口
      protocol: TCP
    - name: metrics
      port: 9090
      targetPort: 9090
  sessionAffinity: None     # 会话亲和性：None/ClientIP
```

### 2. Service - NodePort

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - name: http
      port: 80
      targetPort: 8080
      nodePort: 30080       # 指定节点端口 (30000-32767)
      protocol: TCP
    - name: https
      port: 443
      targetPort: 8443
      nodePort: 30443
  externalTrafficPolicy: Local  # Local 保留源 IP，Cluster 负载均衡更好
```

### 3. Service - LoadBalancer

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-lb
  namespace: production
  annotations:
    # AWS 特定配置
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
    service.beta.kubernetes.io/aws-load-balancer-healthcheck-protocol: "http"
    # GCP 特定配置
    cloud.google.com/load-balancer-type: "External"
spec:
  type: LoadBalancer
  selector:
    app: api-gateway
  ports:
    - port: 443
      targetPort: 8443
  loadBalancerSourceRanges:    # 限制访问来源
    - 10.0.0.0/8
    - 172.16.0.0/12
  externalTrafficPolicy: Local
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

### 4. Headless Service

```yaml
# 用于有状态应用，直接返回 Pod IP 列表
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
spec:
  clusterIP: None             # 设置为 None，不分配 ClusterIP
  selector:
    app: mysql
  ports:
    - port: 3306
      name: mysql
```

### 5. Ingress（七层路由）

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: default
  annotations:
    # NGINX Ingress Controller 配置
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    
    # 重写配置
    nginx.ingress.kubernetes.io/rewrite-target: /
    
    # 认证配置
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    
    # 限流配置
    nginx.ingress.kubernetes.io/limit-rps: "10"
    nginx.ingress.kubernetes.io/limit-connections: "5"
spec:
  ingressClassName: nginx     # 指定 Ingress Controller
  tls:
    - hosts:
        - api.example.com
        - www.example.com
      secretName: tls-secret
  rules:
    # API 路由
    - host: api.example.com
      http:
        paths:
          - path: /v1
            pathType: Prefix
            backend:
              service:
                name: api-v1
                port:
                  number: 80
          - path: /v2
            pathType: Prefix
            backend:
              service:
                name: api-v2
                port:
                  number: 80
    
    # Web 路由
    - host: www.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-frontend
                port:
                  number: 80
          - path: /static
            pathType: Prefix
            backend:
              service:
                name: static-cdn
                port:
                  number: 80
    
    # 默认路由（无 Host）
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: default-backend
                port:
                  number: 80
```

### 6. NetworkPolicy（网络隔离）

```yaml
# 默认拒绝所有入站流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}             # 应用到所有 Pod
  policyTypes:
    - Ingress
---
# 允许特定流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # 允许来自 frontend 的流量
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
    # 允许来自特定命名空间的流量
    - from:
        - namespaceSelector:
            matchLabels:
              env: monitoring
        - podSelector:
            matchLabels:
              app: prometheus
      ports:
        - protocol: TCP
          port: 9090
    # 允许来自特定 IP 段的流量
    - from:
        - ipBlock:
            cidr: 10.0.0.0/8
            except:
              - 10.0.1.0/24
  egress:
    # 允许访问数据库
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    # 允许访问 DNS
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
    # 允许访问外部 API
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
      ports:
        - protocol: TCP
          port: 443
---
# 数据库严格访问控制
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: postgres-strict
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              tier: backend
      ports:
        - protocol: TCP
          port: 5432
```

### 7. ExternalName Service

```yaml
# 将外部服务映射到集群内部 DNS
apiVersion: v1
kind: Service
metadata:
  name: external-database
  namespace: default
spec:
  type: ExternalName
  externalName: prod-db.example.com
---
# 应用可以通过 http://external-database 访问外部服务
```

### 8. 无选择器 Service（手动端点）

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-api
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 8080
---
apiVersion: v1
kind: Endpoints
metadata:
  name: external-api
subsets:
  - addresses:
      - ip: 192.168.1.100
      - ip: 192.168.1.101
    ports:
      - port: 8080
```

## CNI 网络插件对比

| CNI 插件 | 特点 | 适用场景 |
|----------|------|----------|
| **Flannel** | 简单、易部署，基于 VXLAN/UDP | 小型集群，快速上手 |
| **Calico** | 支持网络策略、BGP 路由、性能高 | 生产环境，需要网络隔离 |
| **Cilium** | 基于 eBPF，支持 L3-L7 策略、可观测性强 | 云原生，需要细粒度控制 |
| **Weave** | 自动发现、加密通信 | 多主机、安全要求高 |
| **Antrea** | VMware 开源，基于 OVS | 与 NSX-T 集成 |
| **Kube-OVN** | 基于 OVN，企业级特性 | 大规模集群 |

## 服务发现

### DNS 发现

```bash
# 同一命名空间
<service-name>

# 跨命名空间
<service-name>.<namespace>.svc.cluster.local

# 完整 FQDN
<service-name>.<namespace>.svc.cluster.local
```

```yaml
# Pod 中使用 DNS
apiVersion: v1
kind: Pod
metadata:
  name: client-pod
spec:
  containers:
    - name: client
      image: busybox
      command: ["sh", "-c", "while true; do wget -qO- http://backend-service:8080/health; sleep 5; done"]
      env:
        - name: DATABASE_HOST
          value: "postgres.database.svc.cluster.local"
        - name: CACHE_HOST
          value: "redis.default.svc.cluster.local"
```

### 环境变量发现

```bash
# 每个 Pod 自动注入的环境变量
SERVICE_NAME_SERVICE_HOST=10.0.0.1
SERVICE_NAME_SERVICE_PORT=80
SERVICE_NAME_PORT=tcp://10.0.0.1:80
SERVICE_NAME_PORT_80_TCP=tcp://10.0.0.1:80
SERVICE_NAME_PORT_80_TCP_ADDR=10.0.0.1
SERVICE_NAME_PORT_80_TCP_PORT=80
```

## Ingress Controller 部署

```yaml
# NGINX Ingress Controller 部署示例
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-ingress-controller
  namespace: ingress-nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-ingress
  template:
    metadata:
      labels:
        app: nginx-ingress
    spec:
      serviceAccountName: nginx-ingress-serviceaccount
      containers:
        - name: nginx-ingress-controller
          image: k8s.gcr.io/ingress-nginx/controller:v1.8.1
          args:
            - /nginx-ingress-controller
            - --ingress-class=nginx
            - --configmap=$(POD_NAMESPACE)/ingress-nginx-controller
            - --tcp-services-configmap=$(POD_NAMESPACE)/tcp-services
            - --udp-services-configmap=$(POD_NAMESPACE)/udp-services
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsNonRoot: true
          ports:
            - name: http
              containerPort: 80
            - name: https
              containerPort: 443
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
---
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx
  namespace: ingress-nginx
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
spec:
  type: LoadBalancer
  selector:
    app: nginx-ingress
  ports:
    - name: http
      port: 80
      targetPort: 80
    - name: https
      port: 443
      targetPort: 443
```

## 常用命令

```bash
# ========== Service 操作 ==========
# 查看 Services
kubectl get svc
kubectl get svc -n <namespace>
kubectl get svc -o wide
kubectl describe svc <service-name>

# 创建临时 Service 暴露 Pod
kubectl expose pod <pod-name> --port=8080 --target-port=80

# 端口转发（本地调试）
kubectl port-forward svc/<service-name> 8080:80
kubectl port-forward pod/<pod-name> 8080:80

# ========== Ingress 操作 ==========
kubectl get ingress
kubectl get ingress -n <namespace>
kubectl describe ingress <ingress-name>
kubectl delete ingress <ingress-name>

# 查看 Ingress Controller 日志
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# ========== NetworkPolicy 操作 ==========
kubectl get networkpolicy
kubectl get netpol
kubectl describe networkpolicy <policy-name>
kubectl delete networkpolicy <policy-name>

# ========== 网络诊断 ==========
# 进入 Pod 执行网络测试
kubectl exec -it <pod-name> -- /bin/sh

# 测试 Service 连通性
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- curl http://service-name:port

# 查看 Endpoints
kubectl get endpoints
kubectl get endpoints <service-name>

# 查看 DNS 解析
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default
```

## 面试要点

**Q: Kubernetes 网络模型有什么特点？**
A: (1) 每个 Pod 有独立的 IP 地址，Pod 内容器共享网络命名空间；(2) Pod 间可以直接通信，无需 NAT；(3) 节点上的 Agent（kubelet）可以与 Pod 通信；(4) 扁平网络设计，Pod 可以跨节点直接通信。

**Q: Service 的底层实现原理是什么？**
A: Service 通过 kube-proxy 实现，默认使用 iptables 模式创建 DNAT 规则，将访问 ClusterIP 的流量转发到后端 Pod。现代版本推荐使用 IPVS 模式，支持更多负载均衡算法。从 v1.21 开始，EndpointSlice 替代 Endpoint 存储后端地址。

**Q: ClusterIP、NodePort、LoadBalancer 的区别？**
A: ClusterIP 仅在集群内部访问，适合服务间通信；NodePort 在每个节点开放端口（30000-32767），适合开发测试；LoadBalancer 使用云厂商负载均衡器，适合生产环境直接暴露服务。三者是层层递进的关系。

**Q: Ingress 和 Service 有什么区别？**
A: Service 工作在四层（TCP/UDP），提供负载均衡和简单的流量转发；Ingress 工作在七层（HTTP/HTTPS），提供基于 Host 和 Path 的路由、SSL 终止、限流等高级功能。Ingress 需要配合 Ingress Controller 使用。

**Q: 什么是 Headless Service？**
A: 设置 `clusterIP: None` 的 Service，不分配虚拟 IP，DNS 查询直接返回后端 Pod 的 IP 列表。用于有状态应用（如数据库集群）需要直接访问特定 Pod 的场景，配合 StatefulSet 使用。

**Q: NetworkPolicy 是如何工作的？**
A: NetworkPolicy 定义 Pod 的入站（Ingress）和出站（Egress）规则，实现网络隔离。需要 CNI 插件支持（如 Calico、Cilium）。默认情况下，如果没有 NetworkPolicy，所有 Pod 都可以互相通信。

**Q: externalTrafficPolicy: Local 和 Cluster 的区别？**
A: Local 模式下流量只路由到运行目标 Pod 的节点，保留客户端真实 IP，但可能导致节点间负载不均；Cluster 模式允许流量先到达任意节点再转发，负载更均衡但会丢失源 IP（看到的是节点 IP）。

**Q: 如何排查 Kubernetes 网络问题？**
A: (1) 检查 Pod 状态和资源配额；(2) 查看 Service Endpoints 是否正确；(3) 使用 `kubectl exec` 进入 Pod 测试连通性；(4) 检查 DNS 解析（CoreDNS 日志）；(5) 查看 CNI 插件和网络策略；(6) 使用工具如 netshoot、tcpdump 抓包分析。

## 相关概念

### Cloud & DevOps
- [Kubernetes](../kubernetes.md) - 容器编排平台
- [Pods](./pods.md) - 网络通信的基本单元
- [Deployments](./deployments.md) - 应用部署
- [Services](./services.md) - 服务暴露和发现
- [Ingress](./ingress.md) - 七层流量入口
- [Storage](./storage.md) - 持久化存储

### 计算机科学
- [网络协议](../../computer-science/networks/transport-layer.md) - TCP/IP 协议栈
- [负载均衡](../../computer-science/distributed-systems/load-balancing.md) - 流量分发原理
- [DNS 原理](../../computer-science/networks/network-layer.md) - 域名解析机制
- [网络安全](../../computer-science/systems/network-security.md) - 网络隔离和防护
