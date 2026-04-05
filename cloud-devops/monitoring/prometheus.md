# Prometheus 监控

## 概念

Prometheus 是一个开源的**监控和告警系统**，专为云原生环境设计，采用拉取（Pull）模式采集指标。

> **核心特点**: 多维数据模型、灵活查询语言、高效存储。

---

## 架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Target     │<────│  Prometheus │<────│  Alertmanager│
│ (Exporter)  │     │   Server    │     │              │
└─────────────┘     └──────┬──────┘     └──────┬───────┘
                           │                     │
                           ▼                     ▼
                    ┌─────────────┐      ┌─────────────┐
                    │   Storage   │      │  Notification│
                    │  (TSDB)     │      │  (Email/Slack)│
                    └─────────────┘      └─────────────┘
```

---

## 核心组件

### 1. Prometheus Server

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 2. Exporters

```python
# Python Flask 应用暴露指标
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('app_requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### 3. Alertmanager

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alert@example.com'

route:
  receiver: 'email-notifications'

receivers:
  - name: 'email-notifications'
    email_configs:
      - to: 'admin@example.com'
```

---

## PromQL 查询

```promql
# CPU 使用率
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance) * 100)

# 内存使用率
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100

# HTTP 请求速率
rate(http_requests_total[5m])

# 95 分位数延迟
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

---

## 告警规则

```yaml
# alert_rules.yml
groups:
  - name: example
    rules:
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal - node_memory_MemAvailable) / node_memory_MemTotal > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
```

---

## 面试要点

1. **Pull vs Push**: Prometheus 是 Pull，InfluxDB 是 Push
2. **数据模型**: 多维度标签 (label)
3. **存储**: 本地 TSDB，默认 15 天

---

## 相关概念

### 监控与告警

### 系统原理
- [进程](../../computer-science/systems/process.md) - 进程指标采集
- [内存管理](../../computer-science/systems/memory-management.md) - 内存监控
- [调度](../../computer-science/systems/scheduling.md) - 任务调度监控

### 数据结构
- [时间序列数据库](../../computer-science/databases/indexing.md) - TSDB存储
- [哈希表](../../computer-science/data-structures/hash-table.md) - 标签索引

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 查询性能优化

