# 服务网格 (Service Mesh)

## 简介

服务网格（Service Mesh）是处理服务间通信的基础设施层，通过 Sidecar 代理模式将服务发现、负载均衡、流量管理、安全通信、可观测性等功能从应用代码中剥离，使开发者专注于业务逻辑。

## 核心概念

### Sidecar 模式
- **定义**: 每个服务 Pod 中部署独立的代理容器
- **流量拦截**: 通过 iptables/eBPF 透明拦截进出流量
- **无侵入**: 应用无需感知代理存在
- **独立升级**: 代理可独立于应用更新

### 数据平面 (Data Plane)
- **Envoy Proxy**: 最常用的 Sidecar 代理
  - L3/L4 代理: TCP/UDP 流量转发
  - L7 代理: HTTP/HTTP2/gRPC 路由
  - 负载均衡: 轮询、最小连接、一致性哈希
  - 健康检查: 主动/被动健康检测
  - 熔断: 错误率/延迟阈值触发
- **Proxyless Mesh**: gRPC 直接实现 xDS 协议，无独立代理

### 控制平面 (Control Plane)
| 组件 | Istio | Linkerd | Consul Connect |
|------|-------|---------|----------------|
| **证书管理** | Citadel | 内置 | Consul CA |
| **配置分发** | Galley/Pilot | 控制器 | Consul |
| **数据平面** | Envoy | Linkerd-proxy | Envoy |
| **资源占用** | 较高 | 低 | 中等 |

### 流量管理
- **VirtualService**: 定义路由规则
  - 权重分发: 金丝雀发布、蓝绿部署
  - 条件路由: Header、URI、Query 匹配
  - 重试策略: 次数、超时、退避
  - 故障注入: 延迟、错误模拟（混沌工程）
- **DestinationRule**: 定义目标策略
  - 负载均衡策略
  - 连接池设置
  - 熔断配置
  - mTLS 设置
- **Gateway**: 入站流量管理
  - 边缘代理
  - TLS 终止
  - 虚拟主机配置

### 安全
- **mTLS (双向 TLS)**: 服务间自动加密通信
  - PERMISSIVE: 允许明文和 TLS
  - STRICT: 仅允许 TLS
- **证书自动轮换**: SPIFFE/SPIRE 身份标识
- **授权策略**: 基于身份的访问控制（RBAC）

### 可观测性
- **Metrics**: Envoy 暴露 Prometheus 指标
- **分布式追踪**: Jaeger/Zipkin 集成
- **访问日志**: 详细的请求/响应日志

## 实现方式

### Istio 安装
```bash
# 使用 istioctl 安装
istioctl install --set profile=default -y

# 启用自动 Sidecar 注入
kubectl label namespace default istio-injection=enabled

# 验证安装
kubectl get pods -n istio-system
istioctl verify-install
```

### 基本流量路由
```yaml
# VirtualService: 定义路由规则
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-route
spec:
  hosts:
    - reviews
  http:
    - match:
        - headers:
            end-user:
              exact: jason
      route:
        - destination:
            host: reviews
            subset: v2
    - route:
        - destination:
            host: reviews
            subset: v1
          weight: 75
        - destination:
            host: reviews
            subset: v3
          weight: 25
---
# DestinationRule: 定义服务子集和策略
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews-destination
spec:
  host: reviews
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 10
    loadBalancer:
      simple: LEAST_CONN
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
    - name: v1
      labels:
        version: v1
    - name: v2
      labels:
        version: v2
    - name: v3
      labels:
        version: v3
```

### 熔断配置
```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: productpage-circuit-breaker
spec:
  host: productpage
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        maxRequestsPerConnection: 2
    outlierDetection:
      # 连续 5 个 5xx 错误剔除端点
      consecutive5xxErrors: 5
      # 检测间隔
      interval: 10s
      # 基础剔除时间
      baseEjectionTime: 30s
      # 最大剔除比例
      maxEjectionPercent: 50
```

### 故障注入（混沌工程）
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ratings-fault
spec:
  hosts:
    - ratings
  http:
    - fault:
        delay:
          percentage:
            value: 10.0
          fixedDelay: 5s
        abort:
          percentage:
            value: 5.0
          httpStatus: 503
      route:
        - destination:
            host: ratings
            subset: v1
```

### mTLS 安全配置
```yaml
# PeerAuthentication: 启用严格 mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
---
# AuthorizationPolicy: 访问控制
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: productpage-policy
  namespace: default
spec:
  selector:
    matchLabels:
      app: productpage
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/default/sa/frontend"]
      to:
        - operation:
            methods: ["GET"]
            paths: ["/productpage"]
---
# RequestAuthentication: JWT 验证
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: default
spec:
  selector:
    matchLabels:
      app: productpage
  jwtRules:
    - issuer: "https://accounts.google.com"
      jwksUri: "https://www.googleapis.com/oauth2/v3/certs"
      audiences: ["productpage-api"]
```

### 入口网关
```yaml
# Gateway: 定义入站监听
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: bookinfo-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
    - port:
        number: 443
        name: https
        protocol: HTTPS
      tls:
        mode: SIMPLE
        credentialName: bookinfo-credential
      hosts:
        - "bookinfo.example.com"
    - port:
        number: 80
        name: http
        protocol: HTTP
      hosts:
        - "bookinfo.example.com"
      tls:
        httpsRedirect: true
---
# VirtualService 绑定 Gateway
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: bookinfo
spec:
  hosts:
    - "bookinfo.example.com"
  gateways:
    - bookinfo-gateway
  http:
    - match:
        - uri:
            exact: /productpage
        - uri:
            prefix: /static
        - uri:
            exact: /login
        - uri:
            exact: /logout
        - uri:
            prefix: /api/v1/products
      route:
        - destination:
            host: productpage
            port:
              number: 9080
```

### EnvoyFilter 扩展
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: lua-filter
  namespace: istio-system
spec:
  configPatches:
    - applyTo: HTTP_FILTER
      match:
        context: SIDECAR_INBOUND
        listener:
          filterChain:
            filter:
              name: envoy.filters.network.http_connection_manager
      patch:
        operation: INSERT_BEFORE
        value:
          name: envoy.lua
          typed_config:
            "@type": type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua
            inlineCode: |
              function envoy_on_request(request_handle)
                request_handle:headers():add("x-custom-header", "istio-lua")
                local path = request_handle:headers():get(":path")
                request_handle:logInfo("Request path: " .. path)
              end
              
              function envoy_on_response(response_handle)
                response_handle:headers():add("x-response-time", "processed")
              end
```

## 示例

### 金丝雀发布流程
```yaml
# 步骤1: 部署新版本，0% 流量
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-canary
spec:
  hosts:
    - reviews
  http:
    - route:
        - destination:
            host: reviews
            subset: stable
          weight: 100
        - destination:
            host: reviews
            subset: canary
          weight: 0
---
# 步骤2: 5% 流量切换到金丝雀
# weight: stable=95, canary=5

# 步骤3: 监控指标，逐步增加 canary 权重
# weight: stable=50, canary=50

# 步骤4: 完全切换
# weight: stable=0, canary=100
```

### 多集群服务网格
```
┌─────────────────────────────────────────────────────────────┐
│                     Multi-Cluster Mesh                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────┐    ┌───────────────────────┐    │
│  │     Cluster East      │    │     Cluster West      │    │
│  │   (Primary - Control) │◄──►│     (Remote)          │    │
│  │                       │    │                       │    │
│  │  ┌─────────────────┐  │    │  ┌─────────────────┐  │    │
│  │  │  Istiod         │  │    │  │  Istiod (lite)  │  │    │
│  │  │  (Control Plane)│◄─┼────┼──►│  (Sync only)    │  │    │
│  │  └─────────────────┘  │    │  └─────────────────┘  │    │
│  │         │             │    │         │             │    │
│  │    ┌────┴────┐        │    │    ┌────┴────┐        │    │
│  │    ▼         ▼        │    │    ▼         ▼        │    │
│  │ ┌──────┐  ┌──────┐    │    │ ┌──────┐  ┌──────┐    │    │
│  │ │Svc A │  │Svc B │    │    │ │Svc C │  │Svc D │    │    │
│  │ │+Envoy│  │+Envoy│    │    │ │+Envoy│  │+Envoy│    │    │
│  │ └──────┘  └──────┘    │    │ └──────┘  └──────┘    │    │
│  └───────────────────────┘    └───────────────────────┘    │
│                                                             │
│  Service Discovery: Istiod syncs endpoints across clusters  │
│  mTLS: Cross-cluster identity verification via SPIFFE       │
└─────────────────────────────────────────────────────────────┘
```

### eBPF 加速（Cilium）
```yaml
# Cilium Service Mesh 配置
apiVersion: cilium.io/v2alpha1
kind: CiliumClusterwideEnvoyConfig
metadata:
  name: envoy-lb-config
spec:
  services:
    - name: backend-service
      namespace: default
  resources:
    - "@type": type.googleapis.com/envoy.config.listener.v3.Listener
      name: envoy-lb-listener
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: envoy-lb
                rds:
                  route_config_name: local_route
                http_filters:
                  - name: envoy.filters.http.router
```

## 应用场景

| 场景 | 解决方案 | 配置要点 |
|------|----------|----------|
| **金丝雀发布** | VirtualService 权重 | 逐步切换，监控错误率 |
| **蓝绿部署** | DestinationRule 子集 | 快速切换，快速回滚 |
| **A/B 测试** | Header 匹配路由 | 用户分组，特征路由 |
| **熔断降级** | OutlierDetection | 错误阈值，驱逐恢复 |
| **超时重试** | HTTPRetry | 退避策略，超时设置 |
| **零信任安全** | STRICT mTLS | 自动证书，身份验证 |
| **多租户隔离** | 命名空间 + 授权策略 | 边界防护，最小权限 |

## 面试要点

Q: Sidecar 模式的优缺点？
A: 优点：无侵入、独立升级、语言无关；缺点：资源开销（每个 Pod 额外容器）、延迟增加（每个请求两次网络跳）、配置复杂。Proxyless Mesh 是优化方向。

Q: Istio 与 Linkerd 的选择？
A: Istio 功能最全（安全、流量管理、可观测性），但资源占用高；Linkerd 轻量简单，专注服务网格核心功能，适合资源受限环境。Consul Connect 适合与 Consul 服务发现集成。

Q: mTLS 如何工作？
A: Istio Citadel 为每个服务颁发 SPIFFE 身份证书，Sidecar 自动进行 TLS 握手和证书验证。支持 PERMISSIVE（过渡模式）和 STRICT（强制模式）。

Q: 如何处理服务网格的性能问题？
A: 1) 使用 eBPF 减少 iptables 开销；2) 调优 Envoy 连接池；3) 启用 HTTP/2 多路复用；4) 合理设置资源限制；5) 使用地域感知路由减少跨区调用。

Q: 控制平面和数据平面的区别？
A: 控制平面（Istiod）负责配置管理、证书颁发、服务发现；数据平面（Envoy Sidecar）负责实际流量处理、负载均衡、安全通信。两者分离保证可用性。

## 相关概念

### 数据结构
- **一致性哈希**: Envoy 的负载均衡算法
- **路由表**: 前缀/精确匹配的 Trie 结构
- **证书链**: X.509 证书信任链验证

### 算法
- **熔断算法**: 错误率/并发数窗口统计
- **加权轮询**: 流量分配算法
- **证书轮换**: 零停机证书更新

### 复杂度分析
- **Sidecar 延迟**: 增加 1-3ms（L7 处理）
- **内存开销**: 每个 Sidecar 50-100MB
- **配置分发**: 最终一致性，传播延迟 < 1s

### 系统实现
- **Envoy**: C++ 高性能代理，事件驱动架构
- **xDS 协议**: 动态服务发现配置协议
- **SPIFFE**: 服务身份标识标准

### 对比参考
- [微服务架构](./microservices.md) - 服务通信模式
- [Kubernetes](../kubernetes/services.md) - 原生服务发现
- [分布式追踪](./jaeger.md) - 网格可观测性
- [负载均衡](../../distributed-systems/load-balancing.md) - 负载均衡原理
- [安全通信](../../distributed-systems/security.md) - mTLS 基础
