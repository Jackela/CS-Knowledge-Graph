# API 网关 (API Gateway)

## 概念

API网关（API Gateway）是一种**架构模式**，作为系统的单一入口点，负责处理所有客户端请求并将它们路由到相应的后端服务。

> **核心思想**: 统一入口、协议转换、横切关注点集中处理。

## 核心功能

### 1. 路由与负载均衡
- 请求路由到对应服务
- 负载均衡分发
- 服务发现集成

### 2. 协议转换
- HTTP ↔ gRPC 转换
- REST ↔ GraphQL 转换
- WebSocket 支持

### 3. 安全控制
- 身份认证（JWT/OAuth）
- 权限校验
- 速率限制（Rate Limiting）
- DDoS 防护

### 4. 流量管理
- 熔断（Circuit Breaker）
- 降级（Degradation）
- 重试机制
- 超时控制

## 常见实现

| 方案 | 特点 |
|------|------|
| **Kong** | 开源、插件丰富、基于Nginx |
| **Zuul** | Netflix开源、Java生态 |
| **Spring Cloud Gateway** | Spring生态、响应式 |
| **Nginx** | 高性能、反向代理 |
| **Envoy** | 云原生、服务网格集成 |

## 相关概念

- [微服务架构](./microservices.md) - API网关是微服务架构的核心组件
- [负载均衡](../../computer-science/distributed-systems/load-balancing.md) - 流量分发策略
- [认证授权](../../security/authentication.md) - 安全验证机制
- 熔断降级 - 容错设计
- [Web安全](../../security/web-security.md) - API网关的安全防护

## 参考资料

- [Microservices Patterns](https://microservices.io/patterns/apigateway.html)
