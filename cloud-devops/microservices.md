# 微服务架构 (Microservices)

## 简介

微服务架构是一种将单体应用拆分为一组小型、独立部署服务的架构风格。每个服务围绕业务能力构建，拥有自己的技术栈、数据存储和部署生命周期，通过轻量级通信机制（HTTP/gRPC/消息）协作。

## 核心概念

### 服务拆分原则
- **单一职责**: 每个服务只做一件事并做好
- **业务边界**: 按领域（Domain）划分，对应限界上下文
- **数据隔离**: 每个服务拥有自己的数据库
- **独立部署**: 服务可独立构建、测试、部署、扩展

### 分解策略
| 策略 | 描述 | 适用场景 |
|------|------|----------|
| **按业务能力** | 订单服务、用户服务、支付服务 | 业务清晰的系统 |
| **按子域 (DDD)** | 核心域、支撑域、通用域 | 复杂业务系统 |
| **按事务边界** | 保证 ACID 的事务内聚 | 强一致性要求 |
| **按团队边界** | 康威定律，2个披萨团队 | 大型组织 |

### 通信模式
- **同步通信**: 
  - REST/HTTP: 简单通用，适合外部 API
  - gRPC: 高性能，二进制，适合内部服务
  - GraphQL: 客户端驱动查询
- **异步通信**:
  - 消息队列: RabbitMQ, Kafka（解耦、削峰）
  - 事件总线: 事件驱动架构
  - CQRS: 命令查询职责分离

### 服务发现
- **客户端发现**: 客户端直接查询注册中心（Eureka, Consul）
- **服务器端发现**: 通过负载均衡器（Nginx, ALB）
- **服务网格**: Sidecar 代理处理（Istio, Linkerd）
- **Kubernetes**: DNS + Service 抽象

### 数据管理
- **数据库 per Service**: 服务拥有独立数据存储
- **Saga 模式**: 分布式事务的最终一致性
  - 编排式 (Orchestration): 中央协调器
  - 协奏曲式 (Choreography): 事件驱动
- **CQRS**: 读写分离，不同模型优化
- **事件溯源**: 状态变更记录为事件序列

### 可观测性
- **日志聚合**: ELK, Loki
- **指标监控**: Prometheus + Grafana
- **分布式追踪**: Jaeger, Zipkin
- **健康检查**: /health, /ready 端点

### 韧性模式
- **熔断**: 防止级联故障
- **舱壁**: 资源隔离，限制并发
- **重试**: 指数退避重试
- **超时**: 设置合理的超时时间
- **限流**: 保护服务免受过载

## 实现方式

### 基础项目结构
```
order-service/
├── cmd/
│   └── api/
│       └── main.go
├── internal/
│   ├── domain/          # 领域模型
│   │   ├── order.go
│   │   └── order_item.go
│   ├── application/     # 应用服务
│   │   ├── order_service.go
│   │   └── order_handler.go
│   ├── infrastructure/  # 基础设施
│   │   ├── persistence/
│   │   │   └── order_repo.go
│   │   └── messaging/
│   │       └── event_publisher.go
│   └── interfaces/      # 接口适配器
│       ├── http/
│       │   └── order_controller.go
│       └── grpc/
│           └── order_grpc.go
├── pkg/
│   └── utils/
├── api/
│   ├── proto/           # Protocol Buffers
│   └── openapi/         # OpenAPI 规范
├── configs/
├── deployments/
│   ├── docker/
│   └── k8s/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── go.mod
├── go.sum
├── Dockerfile
├── Makefile
└── README.md
```

### 服务定义 (gRPC)
```protobuf
// api/proto/order.proto
syntax = "proto3";

package order;

option go_package = "github.com/example/orderservice/api/proto";

service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (Order);
  rpc GetOrder(GetOrderRequest) returns (Order);
  rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse);
  rpc CancelOrder(CancelOrderRequest) returns (Order);
  
  // 双向流用于实时订单更新
  rpc StreamOrderUpdates(StreamOrderRequest) returns (stream OrderUpdate);
}

message CreateOrderRequest {
  string customer_id = 1;
  repeated OrderItem items = 2;
  Address shipping_address = 3;
}

message OrderItem {
  string product_id = 1;
  int32 quantity = 2;
  double unit_price = 3;
}

message Order {
  string order_id = 1;
  string customer_id = 2;
  OrderStatus status = 3;
  repeated OrderItem items = 4;
  double total_amount = 5;
  string created_at = 6;
  string updated_at = 7;
}

enum OrderStatus {
  PENDING = 0;
  CONFIRMED = 1;
  SHIPPED = 2;
  DELIVERED = 3;
  CANCELLED = 4;
}
```

### 领域层实现 (Go)
```go
// internal/domain/order.go
package domain

import (
    "errors"
    "time"
    
    "github.com/google/uuid"
)

var (
    ErrInvalidQuantity = errors.New("quantity must be positive")
    ErrOrderCancelled  = errors.New("order is already cancelled")
    ErrEmptyOrder      = errors.New("order must have at least one item")
)

type Order struct {
    OrderID         string
    CustomerID      string
    Status          OrderStatus
    Items           []OrderItem
    TotalAmount     float64
    ShippingAddress Address
    CreatedAt       time.Time
    UpdatedAt       time.Time
    Events          []DomainEvent
}

type OrderItem struct {
    ProductID string
    Quantity  int
    UnitPrice float64
}

func (i OrderItem) Amount() float64 {
    return float64(i.Quantity) * i.UnitPrice
}

type OrderStatus string

const (
    OrderStatusPending    OrderStatus = "PENDING"
    OrderStatusConfirmed  OrderStatus = "CONFIRMED"
    OrderStatusShipped    OrderStatus = "SHIPPED"
    OrderStatusDelivered  OrderStatus = "DELIVERED"
    OrderStatusCancelled  OrderStatus = "CANCELLED"
)

// 领域工厂方法
func NewOrder(customerID string, items []OrderItem, addr Address) (*Order, error) {
    if len(items) == 0 {
        return nil, ErrEmptyOrder
    }
    
    for _, item := range items {
        if item.Quantity <= 0 {
            return nil, ErrInvalidQuantity
        }
    }
    
    order := &Order{
        OrderID:         uuid.New().String(),
        CustomerID:      customerID,
        Status:          OrderStatusPending,
        Items:           items,
        ShippingAddress: addr,
        CreatedAt:       time.Now(),
        UpdatedAt:       time.Now(),
        Events:          make([]DomainEvent, 0),
    }
    
    order.calculateTotal()
    order.raiseEvent(OrderCreatedEvent{
        OrderID:    order.OrderID,
        CustomerID: order.CustomerID,
        TotalAmount: order.TotalAmount,
    })
    
    return order, nil
}

func (o *Order) calculateTotal() {
    var total float64
    for _, item := range o.Items {
        total += item.Amount()
    }
    o.TotalAmount = total
}

func (o *Order) Cancel() error {
    if o.Status == OrderStatusCancelled {
        return ErrOrderCancelled
    }
    if o.Status == OrderStatusShipped || o.Status == OrderStatusDelivered {
        return errors.New("cannot cancel shipped or delivered order")
    }
    
    o.Status = OrderStatusCancelled
    o.UpdatedAt = time.Now()
    o.raiseEvent(OrderCancelledEvent{
        OrderID: o.OrderID,
        Reason:  "customer_request",
    })
    
    return nil
}

func (o *Order) Confirm() error {
    if o.Status != OrderStatusPending {
        return errors.New("only pending orders can be confirmed")
    }
    o.Status = OrderStatusConfirmed
    o.UpdatedAt = time.Now()
    return nil
}

func (o *Order) raiseEvent(event DomainEvent) {
    o.Events = append(o.Events, event)
}

// 领域事件
type DomainEvent interface {
    EventName() string
    OccurredAt() time.Time
}

type OrderCreatedEvent struct {
    OrderID     string
    CustomerID  string
    TotalAmount float64
    occurredAt  time.Time
}

func (e OrderCreatedEvent) EventName() string    { return "order.created" }
func (e OrderCreatedEvent) OccurredAt() time.Time { return e.occurredAt }

type OrderCancelledEvent struct {
    OrderID string
    Reason  string
    occurredAt time.Time
}

func (e OrderCancelledEvent) EventName() string    { return "order.cancelled" }
func (e OrderCancelledEvent) OccurredAt() time.Time { return e.occurredAt }
```

### Saga 模式实现
```go
// internal/application/saga/order_saga.go
package saga

import (
    "context"
    "fmt"
)

// 编排式 Saga - 订单处理流程
type OrderSaga struct {
    inventoryClient InventoryClient
    paymentClient   PaymentClient
    shippingClient  ShippingClient
    eventBus        EventBus
}

func (s *OrderSaga) ProcessOrder(ctx context.Context, order *domain.Order) error {
    // Step 1: 预留库存
    reservationID, err := s.inventoryClient.ReserveStock(ctx, ReserveStockRequest{
        OrderID: order.OrderID,
        Items:   convertItems(order.Items),
    })
    if err != nil {
        return fmt.Errorf("failed to reserve stock: %w", err)
    }
    
    // Step 2: 处理支付
    paymentID, err := s.paymentClient.Charge(ctx, ChargeRequest{
        OrderID: order.OrderID,
        Amount:  order.TotalAmount,
    })
    if err != nil {
        // 补偿: 释放库存
        _ = s.inventoryClient.ReleaseStock(ctx, reservationID)
        return fmt.Errorf("failed to process payment: %w", err)
    }
    
    // Step 3: 创建配送
    shipmentID, err := s.shippingClient.CreateShipment(ctx, CreateShipmentRequest{
        OrderID: order.OrderID,
        Address: order.ShippingAddress,
    })
    if err != nil {
        // 补偿: 退款 + 释放库存
        _ = s.paymentClient.Refund(ctx, paymentID)
        _ = s.inventoryClient.ReleaseStock(ctx, reservationID)
        return fmt.Errorf("failed to create shipment: %w", err)
    }
    
    // 发送订单完成事件
    s.eventBus.Publish(ctx, OrderCompletedEvent{
        OrderID:     order.OrderID,
        PaymentID:   paymentID,
        ShipmentID:  shipmentID,
    })
    
    return nil
}

// 协奏曲式 Saga - 事件驱动
type OrderEventHandler struct {
    orderRepo      OrderRepository
    inventoryClient InventoryClient
}

func (h *OrderEventHandler) OnPaymentCompleted(ctx context.Context, event PaymentCompletedEvent) error {
    order, err := h.orderRepo.Get(ctx, event.OrderID)
    if err != nil {
        return err
    }
    
    if err := order.Confirm(); err != nil {
        return err
    }
    
    // 触发库存扣减
    if err := h.inventoryClient.ConfirmReservation(ctx, event.OrderID); err != nil {
        // 发送补偿事件
        return h.eventBus.Publish(ctx, InventoryConfirmationFailedEvent{
            OrderID: event.OrderID,
        })
    }
    
    return h.orderRepo.Save(ctx, order)
}

func (h *OrderEventHandler) OnInventoryConfirmationFailed(ctx context.Context, event InventoryConfirmationFailedEvent) error {
    // 补偿: 取消订单，触发退款
    order, err := h.orderRepo.Get(ctx, event.OrderID)
    if err != nil {
        return err
    }
    
    if err := order.Cancel(); err != nil {
        return err
    }
    
    // 发布订单取消事件，PaymentService 监听并退款
    return h.eventBus.Publish(ctx, OrderCancelledEvent{
        OrderID: order.OrderID,
        Reason:  "inventory_confirmation_failed",
    })
}
```

### API Gateway 模式
```go
// api-gateway/main.go
package main

import (
    "github.com/gin-gonic/gin"
    "github.com/go-resty/resty/v2"
)

type APIGateway struct {
    orderClient   *resty.Client
    userClient    *resty.Client
    productClient *resty.Client
}

func (g *APIGateway) SetupRoutes(r *gin.Engine) {
    // 订单聚合 API
    r.GET("/api/v1/orders/:id/details", g.getOrderDetails)
    
    // 统一认证
    r.Use(authMiddleware())
    
    // 服务路由
    r.POST("/api/v1/orders", g.createOrder)
    r.GET("/api/v1/users/:id", g.getUser)
    r.GET("/api/v1/products/:id", g.getProduct)
}

// 聚合查询 - BFF 模式
func (g *APIGateway) getOrderDetails(c *gin.Context) {
    orderID := c.Param("id")
    
    // 并行查询多个服务
    var order OrderResponse
    var user UserResponse
    var products []ProductResponse
    
    err := parallel.Execute(
        func() error {
            resp, err := g.orderClient.R().SetResult(&order).Get("/orders/" + orderID)
            return checkError(resp, err)
        },
        func() error {
            // 在获取 order 后才知 userID，这里简化
            return nil
        },
    )
    
    if err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }
    
    // 聚合响应
    c.JSON(200, OrderDetailsResponse{
        Order:    order,
        Customer: user,
        Items:    products,
    })
}
```

## 示例

### 电商微服务架构
```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Web App   │  │ Mobile App  │  │  Admin Panel│              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
┌─────────▼────────────────▼────────────────▼─────────────────────┐
│                        API Gateway                               │
│  - 路由 │ 认证 │ 限流 │ 缓存 │ 日志 │ 聚合                           │
└─────────┬─────────────────────────────────────────────────────────┘
          │
    ┌─────┴─────┬───────────┬───────────┬───────────┬───────────┐
    │           │           │           │           │           │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│ User  │  │ Order │  │Payment│  │Product│  │Invent │  │Shippng│
│Service│  │Service│  │Service│  │Service│  │Service│  │Service│
│       │  │       │  │       │  │       │  │       │  │       │
│ User  │  │ Order │  │Payment│  │Product│  │Stock  │  │Shipmnt│
│ DB    │  │ DB    │  │ DB    │  │ DB    │  │ DB    │  │ DB    │
└───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘
    │          │          │          │          │          │
    └──────────┴──────────┼──────────┴──────────┴──────────┘
                          │
              ┌───────────▼───────────┐
              │      Message Bus      │
              │      (Kafka/NATS)     │
              └───────────────────────┘
```

### 事件驱动 Saga 流程
```
OrderService                  InventoryService              PaymentService
     │                              │                              │
     │  1. Create Order             │                              │
     │─────────────────────────────►│                              │
     │                              │  2. Reserve Stock            │
     │                              │  (async command)             │
     │                              │──────────────────────────────│
     │                              │                              │
     │                              │  3. StockReserved Event      │
     │◄─────────────────────────────│                              │
     │                              │                              │
     │  4. Request Payment          │                              │
     │─────────────────────────────────────────────────────────────►
     │                              │                              │
     │                              │                              │  5. Process
     │                              │                              │     Payment
     │                              │                              │
     │  6. PaymentCompleted         │                              │
     │◄─────────────────────────────────────────────────────────────
     │                              │                              │
     │  7. Confirm Stock            │                              │
     │─────────────────────────────►│                              │
     │                              │  8. Deduct Stock             │
     │                              │                              │
     │  9. OrderConfirmed           │                              │
     │◄─────────────────────────────│                              │
```

## 应用场景

| 场景 | 策略 | 工具/技术 |
|------|------|-----------|
| **单体拆分** | 绞杀者模式（Strangler Fig） | API Gateway, 特性开关 |
| **数据迁移** | 双写模式 | 同步双写，逐步切换读 |
| **事务处理** | Saga 模式 | 事件驱动，补偿事务 |
| **配置管理** | 集中配置中心 | Consul, etcd, Spring Cloud Config |
| **熔断降级** | 断路器模式 | Hystrix, Resilience4j |
| **限流防护** | 令牌桶/漏桶 | Rate Limiter, Envoy |

## 面试要点

Q: 微服务与单体架构的选择标准？
A: 微服务适合：团队规模大（>50人）、业务复杂多变、需要独立扩展、多技术栈需求；单体适合：初创团队、简单业务、快速迭代、低运维成本。

Q: 分布式事务如何处理？
A: 首选 Saga 模式实现最终一致性，避免 2PC/XA 的性能问题；编排式适合复杂流程，协奏曲式适合简单事件链；通过补偿事务处理失败回滚。

Q: 服务间通信的最佳实践？
A: 同步调用（REST/gRPC）适合实时查询，异步消息（Kafka）适合事件通知；设置超时和重试，使用熔断防止级联故障；服务网格可统一处理通信。

Q: 如何避免微服务"分布式单体"？
A: 1) 正确的服务边界（DDD）；2) 避免共享数据库；3) 减少同步调用链深度；4) 独立部署流水线；5) 团队对齐服务边界（康威定律）。

Q: 数据一致性如何保证？
A: 服务内使用 ACID 事务；跨服务使用 Saga 最终一致性；需要强一致性时重新考虑服务边界或接受短暂不一致；使用事件溯源实现审计和回放。

## 相关概念

### 数据结构
- **事件存储**: 不可变事件日志
- **物化视图**: 查询优化的数据副本
- **CRDT**: 无冲突复制数据类型

### 算法
- **一致性哈希**: 数据分片路由
- **向量时钟**: 事件顺序和因果检测
- **Gossip 协议**: 服务发现和状态传播

### 复杂度分析
- **服务调用**: 同步调用增加网络延迟 RTT
- **数据一致性**: 最终一致性收敛时间 O(log n)
- **部署复杂度**: 服务数量 n，运维复杂度 O(n²)

### 系统实现
- **容器化**: Docker 标准化部署
- **编排**: Kubernetes 服务调度
- **服务网格**: Istio/Linkerd 通信治理
- **CI/CD**: 独立流水线，GitOps

### 对比参考
- [服务网格](./service-mesh.md) - 微服务通信治理
- [Kubernetes Deployment](../kubernetes/deployment.md) - 部署策略
- [Kubernetes Services](../kubernetes/services.md) - 服务发现
- [API 网关模式](../../software-engineering/design-patterns/api-gateway.md) - 统一入口
- [Saga 模式](../../software-engineering/design-patterns/saga.md) - 分布式事务
- [熔断器模式](../../software-engineering/design-patterns/circuit-breaker.md) - 故障隔离
- [分布式系统](../../distributed-systems/README.md) - 理论基础
