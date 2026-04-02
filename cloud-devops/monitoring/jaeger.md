# 分布式追踪 (Jaeger)

## 简介

Jaeger 是 Uber 开源的分布式追踪系统，灵感来自 Google Dapper 和 OpenZipkin，兼容 OpenTelemetry 标准。用于监控和排查微服务架构中的请求流，分析服务依赖关系，识别性能瓶颈。

## 核心概念

### Trace（追踪）
- **定义**: 表示一个完整的请求链路，由多个 Span 组成
- **Trace ID**: 64位或128位唯一标识符，贯穿整个请求链路
- **上下文传播**: 通过 HTTP Header、gRPC Metadata 传递 Trace 信息

### Span（跨度）
- **定义**: 表示一个工作单元，包含操作名称、开始/结束时间
- **Span ID**: 每个 Span 的唯一标识
- **Parent Span ID**: 父子关系引用，构建调用树
- **Span Context**: 传播给下游服务的 Trace 信息
- **Attributes/Tags**: 键值对元数据（HTTP 方法、状态码、用户ID等）
- **Logs**: 时间戳事件（异常、调试信息）

### Service & Operation
- **Service**: 参与请求处理的应用/服务名称
- **Operation**: 具体操作的名称（HTTP 端点、函数名）
- **Service Dependencies**: 服务间的调用关系图

### Sampling（采样）
| 策略 | 说明 | 适用场景 |
|------|------|----------|
| **Const** | 全部或全不采样 | 开发调试 |
| **Probabilistic** | 按概率随机采样 | 生产环境 |
| **Rate Limiting** | 固定速率采样 | 控制存储成本 |
| **Adaptive** | 动态调整采样率 | 异常检测 |

### 架构组件
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Application │────▶│   Client    │────▶│   Agent     │
│  (Instrumented)   │  Libraries  │     │  (Daemon)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                              ┌────────────────┼────────────────┐
                              │                │                │
                     ┌────────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
                     │  Collector    │ │  Collector  │ │  Collector  │
                     │  (Receives)   │ │  (Receives) │ │  (Receives) │
                     └───────┬───────┘ └──────┬──────┘ └──────┬──────┘
                             │                │               │
                             └────────────────┼───────────────┘
                                              │
                              ┌───────────────┼───────────────┐
                              │               │               │
                     ┌────────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
                     │ Elasticsearch │ │    Kafka    │ │   Badger    │
                     │   (Storage)   │ │  (Queue)    │ │   (Local)   │
                     └───────────────┘ └─────────────┘ └─────────────┘
```

## 实现方式

### Docker Compose 部署
```yaml
version: '3.8'
services:
  jaeger-collector:
    image: jaegertracing/jaeger-collector:latest
    ports:
      - "14250:14250"  # gRPC
      - "14268:14268"  # HTTP
      - "14269:14269"  # Admin
    environment:
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
    networks:
      - tracing

  jaeger-query:
    image: jaegertracing/jaeger-query:latest
    ports:
      - "16686:16686"  # UI
      - "16687:16687"  # Admin
    environment:
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
    networks:
      - tracing

  jaeger-agent:
    image: jaegertracing/jaeger-agent:latest
    ports:
      - "6831:6831/udp"   # Compact Thrift
      - "6832:6832/udp"   # Binary Thrift
      - "5778:5778"       # Config
    command: ["--reporter.grpc.host-port=jaeger-collector:14250"]
    networks:
      - tracing

  # 全合一模式（开发测试）
  jaeger-all-in-one:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"   # UI
      - "14250:14250"   # gRPC
      - "6831:6831/udp" # UDP
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - tracing
    profiles:
      - dev

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    volumes:
      - es-data:/usr/share/elasticsearch/data
    networks:
      - tracing

volumes:
  es-data:

networks:
  tracing:
    driver: bridge
```

### OpenTelemetry 自动埋点 (Java)
```java
// Maven 依赖
/*
<dependency>
    <groupId>io.opentelemetry.javaagent</groupId>
    <artifactId>opentelemetry-javaagent</artifactId>
    <version>1.32.0</version>
</dependency>
*/

// 启动参数
// java -javaagent:opentelemetry-javaagent.jar \
//      -Dotel.service.name=order-service \
//      -Dotel.traces.exporter=jaeger \
//      -Dotel.exporter.jaeger.endpoint=http://localhost:14250 \
//      -jar order-service.jar
```

### OpenTelemetry 手动埋点 (Go)
```go
package main

import (
    "context"
    "log"
    "time"
    
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/exporters/jaeger"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.21.0"
    "go.opentelemetry.io/otel/trace"
)

// 初始化 Tracer
func initTracer() (*sdktrace.TracerProvider, error) {
    // 创建 Jaeger Exporter
    exp, err := jaeger.New(jaeger.WithCollectorEndpoint(
        jaeger.WithEndpoint("http://localhost:14268/api/traces"),
    ))
    if err != nil {
        return nil, err
    }
    
    // 配置 Resource
    res, err := resource.Merge(
        resource.Default(),
        resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceNameKey.String("payment-service"),
            semconv.ServiceVersionKey.String("v1.0.0"),
            attribute.String("environment", "production"),
        ),
    )
    if err != nil {
        return nil, err
    }
    
    // 创建 TracerProvider
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exp),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.TraceIDRatioBased(0.1)),
    )
    
    otel.SetTracerProvider(tp)
    return tp, nil
}

func main() {
    tp, err := initTracer()
    if err != nil {
        log.Fatal(err)
    }
    defer tp.Shutdown(context.Background())
    
    tracer := otel.Tracer("payment-service")
    
    // 创建 Root Span
    ctx, span := tracer.Start(context.Background(), "process-payment",
        trace.WithAttributes(
            attribute.String("payment.method", "credit_card"),
            attribute.Float64("payment.amount", 99.99),
        ),
    )
    defer span.End()
    
    // 模拟处理
    validatePayment(ctx, tracer)
    chargeCard(ctx, tracer)
    sendNotification(ctx, tracer)
}

func validatePayment(ctx context.Context, tracer trace.Tracer) {
    _, span := tracer.Start(ctx, "validate-payment")
    defer span.End()
    
    span.SetAttributes(
        attribute.String("validation.rule", "fraud_check"),
        attribute.Bool("validation.passed", true),
    )
    
    time.Sleep(10 * time.Millisecond)
}

func chargeCard(ctx context.Context, tracer trace.Tracer) {
    ctx, span := tracer.Start(ctx, "charge-card")
    defer span.End()
    
    span.SetAttributes(
        attribute.String("gateway", "stripe"),
    )
    
    // 模拟调用外部服务
    time.Sleep(50 * time.Millisecond)
    
    // 记录事件
    span.AddEvent("gateway-response", trace.WithAttributes(
        attribute.String("status", "approved"),
        attribute.String("transaction_id", "txn_123456"),
    ))
}

func sendNotification(ctx context.Context, tracer trace.Tracer) {
    _, span := tracer.Start(ctx, "send-notification",
        trace.WithAttributes(
            attribute.String("channel", "email"),
        ),
    )
    defer span.End()
    
    time.Sleep(5 * time.Millisecond)
}
```

### Python 埋点示例
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# 配置 Tracer
resource = Resource(attributes={
    SERVICE_NAME: "inventory-service"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# Flask 应用自动埋点
from flask import Flask, request
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route('/api/inventory/<product_id>')
def get_inventory(product_id):
    with tracer.start_as_current_span("check_inventory") as span:
        span.set_attribute("product.id", product_id)
        
        # 查询数据库
        with tracer.start_as_current_span("db.query") as db_span:
            db_span.set_attribute("db.system", "mysql")
            db_span.set_attribute("db.statement", "SELECT * FROM inventory WHERE id = ?")
            quantity = query_database(product_id)
            db_span.set_attribute("db.rows_returned", 1)
        
        span.set_attribute("inventory.quantity", quantity)
        
        # 调用下游服务
        response = requests.get(f"http://pricing-service/api/price/{product_id}")
        
        return {"product_id": product_id, "quantity": quantity}

def query_database(product_id):
    # 模拟数据库查询
    return 100

if __name__ == '__main__':
    app.run(port=5000)
```

### 上下文传播 (HTTP)
```go
// 服务端：提取 Trace 上下文
import "go.opentelemetry.io/otel/propagation"

func extractContext(r *http.Request) context.Context {
    propagator := propagation.TraceContext{}
    ctx := propagator.Extract(r.Context(), propagation.HeaderCarrier(r.Header))
    return ctx
}

// 客户端：注入 Trace 上下文
func injectContext(ctx context.Context, req *http.Request) {
    propagator := propagation.TraceContext{}
    propagator.Inject(ctx, propagation.HeaderCarrier(req.Header))
}

// HTTP Header 格式
// traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
// tracestate: vendor=value
```

## 示例

### 微服务追踪架构
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  API Gateway │────▶│  Auth       │────▶│  User       │
│  (Trace Root)│     │  Service    │     │  Service    │
└──────┬──────┘     └─────────────┘     └─────────────┘
       │
       ├────────────────┬────────────────┐
       │                │                │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  Order      │ │  Payment    │ │  Inventory  │
│  Service    │ │  Service    │ │  Service    │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
              ┌────────▼────────┐
              │  Notification   │
              │  Service        │
              └─────────────────┘

Trace Structure:
────────────────────────────────────────────────────────
Trace: abc123 (API Gateway)
├── Span: api-gateway /api/orders [200ms]
│   ├── Span: auth-service /validate [20ms]
│   ├── Span: user-service /get-profile [30ms]
│   ├── Span: order-service /create-order [100ms]
│   │   ├── Span: payment-service /charge [50ms]
│   │   │   └── Span: payment-gateway [40ms]
│   │   ├── Span: inventory-service /reserve [30ms]
│   │   │   └── Span: db-query [10ms]
│   │   └── Span: order-db /insert [20ms]
│   └── Span: notification-service /send [50ms]
└── (Total: 200ms)
```

### 性能分析查询
```javascript
// Jaeger UI 查询语法

// 1. 查找特定服务的慢请求
service="order-service" 
  AND duration>500ms 
  AND http.status_code=500

// 2. 查找包含特定错误的追踪
tags:error=true 
  AND service="payment-service"

// 3. 查找特定用户的请求
tags:user_id="user123" 
  AND service="api-gateway"
```

### 依赖图分析
```
┌──────────────────────────────────────────────────────┐
│                   Service Dependencies               │
├──────────────────────────────────────────────────────┤
│                                                      │
│    ┌─────────┐         ┌─────────┐                  │
│    │   API   │────────▶│  Auth   │                  │
│    │ Gateway │         │ Service │                  │
│    └────┬────┘         └─────────┘                  │
│         │                                            │
│    ┌────┴────┬─────────┬─────────┐                   │
│    │         │         │         │                   │
│    ▼         ▼         ▼         ▼                   │
│ ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐              │
│ │Order │  │User  │  │Invtry│  │Notif │              │
│ │Svc   │  │Svc   │  │Svc   │  │Svc   │              │
│ └──┬───┘  └──────┘  └──┬───┘  └──────┘              │
│    │                   │                             │
│    └─────────┬─────────┘                             │
│              ▼                                       │
│           ┌──────┐                                   │
│           │Paymt │                                   │
│           │Svc   │                                   │
│           └──┬───┘                                   │
│              │                                       │
│              ▼                                       │
│           ┌──────┐                                   │
│           │Stripe│                                   │
│           │API   │                                   │
│           └──────┘                                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## 应用场景

| 场景 | 使用方法 | 关键指标 |
|------|----------|----------|
| **延迟分析** | Trace 时间线视图 | P50/P95/P99 延迟 |
| **错误定位** | 错误标签过滤 | 错误率、异常堆栈 |
| **依赖分析** | Service Dependency 图 | 调用深度、扇出 |
| **性能优化** | 关键路径分析 | 瓶颈 Span 识别 |
| **容量规划** | 请求量趋势 | QPS、并发数 |
| **合规审计** | 全量采样存储 | 请求完整性验证 |

## 面试要点

Q: Jaeger 和 Zipkin 的主要区别？
A: Jaeger 支持更现代的 OpenTelemetry 标准，存储后端更灵活（支持 Cassandra、Elasticsearch、Kafka），UI 功能更丰富（依赖图、对比视图），采样策略更灵活（自适应采样），性能更高（使用 gRPC 传输）。

Q: 什么是 Trace 上下文传播？
A: 在分布式调用中，Trace ID 和 Span ID 需要跨进程边界传递，通常通过 HTTP Header（W3C Trace Context: traceparent, tracestate）或 gRPC Metadata 传播，确保整个调用链关联。

Q: 采样策略如何选择？
A: 开发环境使用 Const(1) 全量采样；生产环境通常使用 Probabilistic(0.01-0.1) 或 Adaptive 自适应采样；对于重要接口可使用基于规则的头部采样（debug flag）。

Q: 如何处理高基数标签问题？
A: 避免将用户ID、订单ID等高基数信息作为标签，改用 Log 记录或聚合维度标签（如 tenant_id 而非 user_id）。高基数会导致存储爆炸和查询性能下降。

Q: Jaeger 与 APM 工具的区别？
A: Jaeger 专注于分布式追踪，提供调用链可视化；APM（如 Elastic APM、Datadog）通常集成追踪、指标、日志、性能剖析，提供更全面的可观测性。Jaeger 可作为 APM 的追踪组件。

## 相关概念

### 数据结构
- **Span 树**: 父子关系构建的有向无环图
- **跳跃表**: 按时间排序的 Span 索引
- **邻接表**: 服务依赖关系图存储

### 算法
- **关键路径分析**: 识别 Trace 中最长的执行路径
- **自适应采样**: 基于错误率、延迟动态调整采样率
- **因果追踪**: 确定请求间的因果关系

### 复杂度分析
- **存储复杂度**: 每个 Span O(k)，k 为标签数量
- **查询复杂度**: 按 Trace ID 查询 O(1)，按标签查询 O(n)
- **采样开销**: 追踪上下文传播 O(1)，不影响业务逻辑

### 系统实现
- **Thrift/gRPC**: 高效的数据传输协议
- **Badger**: 嵌入式本地存储（适用于 all-in-one）
- **Apache Kafka**: 高吞吐量缓冲队列

### 对比参考
- [Grafana](./grafana.md) - 可视化集成
- [ELK Stack](./elk-stack.md) - 日志与追踪关联
- [Prometheus](./prometheus.md) - 指标与追踪关联
- [微服务架构](../microservices.md) - 追踪背景
- [服务网格](../service-mesh.md) - 自动追踪注入
