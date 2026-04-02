# Kubernetes Ingress (K8s 入口控制器)

## 简介

**Kubernetes Ingress** 是管理集群外部访问的 API 对象，提供 HTTP 和 HTTPS 路由规则。Ingress 充当了集群的"智能网关"，基于域名和路径将外部流量路由到集群内部的服务，同时支持 SSL/TLS 终止、负载均衡、虚拟主机等功能。

## 核心概念

- **Ingress 资源**：定义路由规则的 Kubernetes API 对象
- **Ingress Controller**：实际执行路由的组件（如 Nginx、Traefik、HAProxy）
- **Ingress Class**：用于区分和选择不同 Controller 的元数据
- **规则（Rules）**：基于主机名和路径的路由配置
- **后端（Backend）**：路由目标 Service 和端口
- **TLS**：SSL 证书配置，实现 HTTPS 访问
- **注解（Annotations）**：Controller 特定的配置扩展

## Ingress Controller 类型

| Controller | 特点 | 适用场景 |
|------------|------|----------|
| Nginx | 功能丰富、文档完善、社区活跃 | 通用场景，企业首选 |
| Traefik | 云原生、自动服务发现、动态配置 | 微服务、云环境 |
| HAProxy | 高性能、稳定、低延迟 | 高并发、金融级应用 |
| Istio Gateway | 服务网格集成、高级流量管理 | 服务网格架构 |
| AWS ALB | 与 AWS 深度集成 | AWS 云环境 |
| Kong | API 网关功能丰富 | API 管理场景 |

## 实现方式

### 基础 Ingress 配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
  namespace: default
spec:
  ingressClassName: nginx
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-service
                port:
                  number: 80
```

### 多路径路由配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-path-ingress
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: api-tls-secret
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /v1/users
            pathType: Prefix
            backend:
              service:
                name: user-service
                port:
                  number: 8080
          - path: /v1/orders
            pathType: Prefix
            backend:
              service:
                name: order-service
                port:
                  number: 8080
          - path: /v1/products
            pathType: Prefix
            backend:
              service:
                name: product-service
                port:
                  number: 8080
          - path: /static
            pathType: Prefix
            backend:
              service:
                name: static-assets
                port:
                  number: 80
```

### 虚拟主机配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: virtual-host-ingress
  namespace: default
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - www.example.com
        - blog.example.com
        - shop.example.com
      secretName: multi-domain-tls
  rules:
    - host: www.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: website-service
                port:
                  number: 80
    - host: blog.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: blog-service
                port:
                  number: 8080
    - host: shop.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ecommerce-service
                port:
                  number: 3000
```

### 高级 Nginx 配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: advanced-nginx-ingress
  namespace: production
  annotations:
    # 速率限制
    nginx.ingress.kubernetes.io/limit-rps: "10"
    nginx.ingress.kubernetes.io/limit-connections: "5"
    
    # 超时配置
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "30"
    
    # 缓冲区配置
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-buffering: "on"
    nginx.ingress.kubernetes.io/proxy-buffer-size: "8k"
    
    # CORS 配置
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://example.com"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "DNT,X-CustomHeader,Keep-Alive,User-Agent"
    
    # 会话保持
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/session-cookie-name: "route"
    nginx.ingress.kubernetes.io/session-cookie-expires: "172800"
    nginx.ingress.kubernetes.io/session-cookie-max-age: "172800"
    
    # 认证
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: basic-auth-secret
    nginx.ingress.kubernetes.io/auth-realm: "Authentication Required"
    
    # 重写
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    
    # 金丝雀发布
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "20"
    nginx.ingress.kubernetes.io/canary-by-header: "canary"
    nginx.ingress.kubernetes.io/canary-by-header-value: "always"

spec:
  ingressClassName: nginx
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /api(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
          - path: /admin(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: admin-service
                port:
                  number: 3000
```

### IngressClass 配置

```yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: nginx-internal
  annotations:
    ingressclass.kubernetes.io/is-default-class: "false"
spec:
  controller: k8s.io/ingress-nginx
  parameters:
    apiGroup: k8s.io
    kind: IngressParameters
    name: internal-lb-config
    scope: Namespace
---
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: nginx-external
  annotations:
    ingressclass.kubernetes.io/is-default-class: "true"
spec:
  controller: k8s.io/ingress-nginx
```

### Traefik IngressRoute (CRD)

```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: api-ingress
  namespace: default
spec:
  entryPoints:
    - web
    - websecure
  routes:
    - match: Host(`api.example.com`) && PathPrefix(`/v1`)
      kind: Rule
      services:
        - name: api-service
          port: 8080
          healthCheck:
            path: /health
            interval: 10s
      middlewares:
        - name: rate-limit
        - name: jwt-auth
    - match: Host(`api.example.com`) && PathPrefix(`/v2`)
      kind: Rule
      services:
        - name: api-v2-service
          port: 8080
  tls:
    certResolver: letsencrypt
    options:
      name: tls-options
---
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: rate-limit
spec:
  rateLimit:
    average: 100
    burst: 50
```

## 路径类型（PathType）

```yaml
paths:
  - path: /api
    pathType: Prefix      # 匹配 /api, /api/v1, /api/v1/users
    
  - path: /exact
    pathType: Exact       # 只匹配 /exact，不匹配 /exact/ 或 /exact/more
    
  - path: /impl
    pathType: ImplementationSpecific  # 具体行为取决于 Ingress Controller
```

## TLS 证书管理

### 使用 cert-manager 自动签发

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    acme.cert-manager.io/http01-edit-in-place: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - secure.example.com
      secretName: secure-tls
  rules:
    - host: secure.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: secure-app
                port:
                  number: 443
```

## 应用场景

- **多租户路由**：基于域名将不同租户流量路由到对应服务
- **API 版本管理**：通过路径前缀区分 API 版本（/v1/, /v2/）
- **微服务网关**：统一入口，将请求分发到多个微服务
- **金丝雀发布**：按比例或 Header 将流量路由到新版本
- **蓝绿部署**：快速切换流量到不同版本
- **SSL 终止**：在 Ingress 层处理 HTTPS，后端使用 HTTP
- **静态资源缓存**：为静态资源配置缓存策略

## 常用命令

```bash
# 查看 Ingress
kubectl get ingress
kubectl get ingress -n production

# 查看 Ingress 详情
kubectl describe ingress my-ingress

# 测试 Ingress 路由
curl -H "Host: example.com" http://ingress-ip/api/users

# 查看 Ingress Controller 日志
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# 检查证书状态
kubectl get certificate -n production
kubectl describe certificate my-tls
```

## 面试要点

1. **Q: Ingress 和 Service 的区别是什么？**
   A: Service 是四层（TCP/UDP）负载均衡，通过 IP 和端口暴露服务；Ingress 是七层（HTTP/HTTPS）路由，基于域名和路径进行流量分发。Ingress 通常位于 Service 之前，提供更丰富的 HTTP 层功能。

2. **Q: Ingress Controller 的工作原理？**
   A: Ingress Controller 监听 Kubernetes API 中的 Ingress 资源变化，根据规则动态更新反向代理配置（如 Nginx 配置文件），将外部请求按照域名、路径等规则路由到对应的 Service。

3. **Q: pathType 的三种类型有什么区别？**
   A: Exact 精确匹配完整路径；Prefix 匹配路径前缀，区分大小写，按路径元素匹配；ImplementationSpecific 的具体行为取决于 Ingress Controller 实现。

4. **Q: 如何实现蓝绿部署或金丝雀发布？**
   A: 通过 Nginx Ingress 的 canary 注解实现：设置 nginx.ingress.kubernetes.io/canary: "true"，配合 canary-weight 控制流量比例，或使用 canary-by-header 基于请求头路由。

5. **Q: Ingress 如何处理 HTTPS 和证书？**
   A: 在 spec.tls 中配置证书 Secret，或使用 cert-manager 自动签发 Let's Encrypt 证书。Ingress Controller 负责 SSL/TLS 终止，将解密后的 HTTP 流量转发给后端服务。

6. **Q: 什么是 IngressClass？为什么需要它？**
   A: IngressClass 用于区分不同的 Ingress Controller，一个集群可以部署多个 Controller（如 Nginx 和 Traefik），通过 ingressClassName 字段指定使用哪个 Controller 处理该 Ingress。

7. **Q: 如何排查 Ingress 路由不生效的问题？**
   A: (1) 检查 Ingress Controller 是否运行；(2) 验证 Service 和 Pod 是否正常；(3) 确认 ingressClassName 配置正确；(4) 查看 Controller 日志；(5) 使用 kubectl describe ingress 查看事件；(6) 检查 DNS 解析是否正确。

## 相关概念

### Cloud & DevOps
- [Kubernetes](./kubernetes.md) - 容器编排平台
- [Services](./services.md) - Ingress 后端目标
- [Pods](./pods.md) - 应用运行单元
- [ConfigMaps & Secrets](./configmaps-secrets.md) - TLS 证书存储
- [Helm](./helm.md) - Ingress Controller 部署

### 系统实现
- [负载均衡](../computer-science/distributed-systems/load-balancing.md) - 流量分发算法
- [网络协议](../computer-science/systems/network-security.md) - HTTP/HTTPS 协议
- [TLS/SSL](../computer-science/systems/network-security.md) - 加密通信原理
- [反向代理](../computer-science/systems/network-security.md) - 代理服务器原理
