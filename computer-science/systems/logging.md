# 日志 (Logging)

日志是记录系统运行状态、事件和错误的机制，是系统可观测性的三大支柱之一。良好的日志实践对于故障排查、安全审计和业务分析至关重要。

## 核心概念

### 日志的作用

```
┌─────────────────────────────────────────────────────────────┐
│                     日志的作用                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  可观测性 (Observability)                                    │
│  ├── 故障排查 - 快速定位问题根因                            │
│  ├── 性能监控 - 识别性能瓶颈                                │
│  └── 依赖追踪 - 理解系统间调用关系                          │
│                                                             │
│  安全与合规 (Security & Compliance)                          │
│  ├── 安全审计 - 记录访问和操作行为                          │
│  ├── 入侵检测 - 识别异常活动                                │
│  └── 合规证明 - 满足法规要求                                │
│                                                             │
│  业务分析 (Business Analytics)                               │
│  ├── 用户行为 - 理解用户使用模式                            │
│  ├── 业务指标 - 监控系统健康度                              │
│  └── A/B 测试 - 实验数据分析                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 日志级别

| 级别 | 数值 | 用途 | 示例 |
|------|------|------|------|
| **FATAL** | 60 | 系统无法继续运行 | 数据库连接失败，核心服务崩溃 |
| **ERROR** | 50 | 功能受损但未崩溃 | API 调用失败，文件写入错误 |
| **WARN** | 40 | 潜在问题，需要关注 | 配置项缺失，资源接近阈值 |
| **INFO** | 30 | 常规运行信息 | 服务启动，请求处理完成 |
| **DEBUG** | 20 | 详细调试信息 | 变量值，函数调用轨迹 |
| **TRACE** | 10 | 最详细的跟踪信息 | 进入/离开每个方法 |

```python
# 日志级别使用示例
import logging

# 生产环境
logging.basicConfig(level=logging.INFO)

# 开发环境
# logging.basicConfig(level=logging.DEBUG)

logging.debug("调试信息，仅开发时可见")
logging.info("用户登录成功: user_id=12345")
logging.warning("磁盘空间不足: 剩余 10%")
logging.error("数据库查询失败: connection timeout")
logging.critical("系统无法启动: 核心配置缺失")
```

## 日志格式

### 结构化日志

```python
# ❌ 非结构化（难以解析）
log.info("User john logged in from 192.168.1.1 at 2024-01-15 10:30:00")

# ✅ 结构化（易于分析和查询）
log.info("User login successful", extra={
    "event": "user_login",
    "user_id": "john",
    "ip": "192.168.1.1",
    "timestamp": "2024-01-15T10:30:00Z"
})

# JSON 格式（推荐用于生产）
{
    "timestamp": "2024-01-15T10:30:00.123Z",
    "level": "INFO",
    "logger": "auth.service",
    "message": "User login successful",
    "event": "user_login",
    "user_id": "john",
    "ip": "192.168.1.1",
    "trace_id": "abc123",
    "span_id": "xyz789"
}
```

### 字段规范

```python
# 标准日志字段
{
    # 基础字段
    "timestamp": "2024-01-15T10:30:00.123Z",  # ISO8601 格式
    "level": "INFO",
    "message": "操作描述",
    
    # 上下文字段
    "service": "user-service",
    "hostname": "prod-web-01",
    "environment": "production",
    
    # 追踪字段
    "trace_id": "4f6d9e8c7a5b3c2d",
    "span_id": "1a2b3c4d5e6f7g8h",
    "parent_span_id": "9h8g7f6e5d4c3b2a",
    
    # 业务字段
    "user_id": "user_12345",
    "request_id": "req_67890",
    "duration_ms": 45.2
}
```

## 日志架构

### 集中式日志架构

```
┌─────────────────────────────────────────────────────────────┐
│                   集中式日志架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐                   │
│  │ App A   │   │ App B   │   │ App C   │   应用层           │
│  │ (Logs)  │   │ (Logs)  │   │ (Logs)  │                   │
│  └────┬────┘   └────┬────┘   └────┬────┘                   │
│       │             │             │                         │
│       └─────────────┼─────────────┘                         │
│                     ▼                                       │
│            ┌─────────────────┐                              │
│            │  Log Shipper    │    (Filebeat/Fluent Bit)    │
│            │  日志收集器      │                              │
│            └────────┬────────┘                              │
│                     │                                       │
│                     ▼                                       │
│            ┌─────────────────┐                              │
│            │  Message Queue  │    (Kafka/Redis)            │
│            │  消息队列        │    缓冲与削峰                │
│            └────────┬────────┘                              │
│                     │                                       │
│                     ▼                                       │
│            ┌─────────────────┐                              │
│            │  Log Processor  │    (Logstash/Fluentd)       │
│            │  日志处理        │    解析、过滤、增强          │
│            └────────┬────────┘                              │
│                     │                                       │
│                     ▼                                       │
│            ┌─────────────────┐                              │
│            │  Log Storage    │    (Elasticsearch/Loki)     │
│            │  日志存储        │                              │
│            └────────┬────────┘                              │
│                     │                                       │
│                     ▼                                       │
│            ┌─────────────────┐                              │
│            │  Visualization  │    (Grafana/Kibana)         │
│            │  可视化分析      │                              │
│            └─────────────────┘                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 日志轮转

```python
# Python 日志轮转配置
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# 按文件大小轮转
file_handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5            # 保留5个备份
)

# 按时间轮转（每天）
time_handler = TimedRotatingFileHandler(
    'app.log',
    when='midnight',
    interval=1,
    backupCount=30           # 保留30天
)
```

## 最佳实践

### 日志规范

```python
# ✅ 好的日志实践

# 1. 使用合适的日志级别
logger.info("Processing order", extra={"order_id": order_id})
logger.warning("Cache miss", extra={"key": cache_key})
logger.error("Payment failed", extra={
    "order_id": order_id,
    "error": str(e),
    "retry_count": retry_count
})

# 2. 包含上下文信息
logger.info("Request completed", extra={
    "method": request.method,
    "path": request.path,
    "status_code": response.status_code,
    "duration_ms": duration * 1000,
    "user_agent": request.headers.get('User-Agent')
})

# 3. 避免记录敏感信息
# ❌ 不要这样
logger.info(f"User login: {username}, password: {password}")

# ✅ 应该这样
logger.info("User login attempt", extra={
    "username": username,
    "success": success,
    "ip": client_ip
})

# 4. 使用结构化格式
import structlog

logger = structlog.get_logger()
logger.info("event_processed", 
    event_type="order_created",
    order_id="ORD-12345",
    amount=99.99,
    currency="USD"
)
```

### 分布式追踪

```python
# 在微服务中传递追踪 ID
import uuid

# 请求入口生成追踪 ID
trace_id = str(uuid.uuid4())

# 在日志中记录
correlation_id = trace_id

# 通过 HTTP Header 传递
headers = {
    'X-Trace-ID': trace_id,
    'X-Span-ID': span_id
}

# 下游服务提取并使用
@app.middleware("http")
async def add_trace_id(request, call_next):
    trace_id = request.headers.get('X-Trace-ID', str(uuid.uuid4()))
    # 将 trace_id 添加到日志上下文
    with logger.contextualize(trace_id=trace_id):
        response = await call_next(request)
        response.headers['X-Trace-ID'] = trace_id
        return response
```

## 日志分析

### 常用查询

```sql
-- Elasticsearch DSL 查询示例

-- 查找最近1小时的错误
{
    "query": {
        "bool": {
            "must": [
                {"term": {"level": "ERROR"}},
                {"range": {"@timestamp": {"gte": "now-1h"}}}
            ]
        }
    }
}

-- 统计各服务的错误率
{
    "aggs": {
        "errors_by_service": {
            "terms": {"field": "service"},
            "aggs": {
                "error_count": {
                    "filter": {"term": {"level": "ERROR"}}
                }
            }
        }
    }
}
```

### 日志告警

```yaml
# 告警规则示例
alerts:
  - name: high_error_rate
    condition: |
      rate(log_entries{level="ERROR"}[5m]) > 0.1
    severity: critical
    
  - name: slow_requests
    condition: |
      histogram_quantile(0.99, 
        rate(request_duration_seconds_bucket[5m])
      ) > 2
    severity: warning
```

## 相关概念 (Related Concepts)

### 可观测性三大支柱
- [HTTP 协议](../networks/http.md) - 系统间通信

### 系统运维
- [调度](./scheduling.md) - 系统任务调度

### 安全与合规
- [安全审计](../../security/system-security/audit-logging.md) - 安全事件日志

## 参考资料

1. "The 12-Factor App" - 日志章节
2. OpenTelemetry Logging 规范
3. Google SRE Book - 监控与日志
4. Splunk - Logging Best Practices
5. ELK Stack 官方文档
