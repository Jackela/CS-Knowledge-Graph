# 可视化监控 (Grafana)

## 简介

Grafana 是领先的开源数据可视化和监控平台，支持多种数据源（时序数据库、日志、追踪等），提供丰富的可视化面板、告警系统和仪表板功能。广泛应用于基础设施监控、应用性能监控和业务指标分析。

## 核心概念

### 数据源 (Data Sources)
| 数据源类型 | 用途 | 查询语言 |
|------------|------|----------|
| **Prometheus** | 指标监控 | PromQL |
| **Elasticsearch** | 日志分析 | Lucene/KQL |
| **InfluxDB** | 时序数据 | InfluxQL/Flux |
| **MySQL/PostgreSQL** | SQL 数据 | SQL |
| **CloudWatch** | AWS 监控 | CloudWatch Query |
| **Loki** | 日志聚合 | LogQL |
| **Jaeger/Tempo** | 分布式追踪 | TraceQL |

### 仪表板 (Dashboards)
- **面板 (Panels)**: 基本可视化单元（图表、表格、统计、日志等）
- **变量 (Variables)**: 动态仪表板参数（服务器、环境、时间范围）
- **模板 (Templating)**: 可复用的面板配置
- **注释 (Annotations)**: 标记重要事件（部署、告警）
- **链接 (Links)**: 仪表板间导航和钻取

### 可视化类型
- **Time Series**: 时序图，最常用
- **Stat**: 单值统计，带阈值颜色
- **Gauge**: 仪表盘，适合百分比
- **Bar Chart**: 柱状图，适合分类比较
- **Heatmap**: 热力图，适合分布分析
- **Logs**: 日志查看器
- **Table**: 表格展示
- **Node Graph**: 拓扑图，服务依赖

### 告警系统
- **告警规则**: 基于查询的条件判断
- **通知渠道**: Email、Slack、PagerDuty、Webhook
- **告警状态**: Pending → Firing → Resolved
- **静默 (Silencing)**: 临时禁用告警
- **告警组**: 相关告警聚合

## 实现方式

### 基础部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./provisioning:/etc/grafana/provisioning
      - ./dashboards:/var/lib/grafana/dashboards
    networks:
      - monitoring

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-storage:/prometheus
    networks:
      - monitoring

volumes:
  grafana-storage:
  prometheus-storage:

networks:
  monitoring:
    driver: bridge
```

### 数据源配置 (Provisioning)
```yaml
# provisioning/datasources/prometheus.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: 5s
      httpMethod: POST
      manageAlerts: true
      alertmanagerUid: alertmanager

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    jsonData:
      maxLines: 1000
      derivedFields:
        - name: TraceID
          matcherRegex: '"trace_id":"([^"]+)"'
          url: 'http://jaeger:16686/trace/$${__value.raw}'

  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger:16686
    jsonData:
      tracesToLogs:
        datasourceUid: 'Loki'
        tags: ['pod', 'namespace']
        mappedTags: [{ key: 'service.name', value: 'service' }]
        mapTagNamesEnabled: false
        spanStartTimeShift: '1h'
        spanEndTimeShift: '1h'
        filterByTraceID: false
        filterBySpanID: false
```

### 仪表板配置 (Provisioning)
```yaml
# provisioning/dashboards/dashboard.yml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
```

### 仪表板 JSON 定义
```json
{
  "dashboard": {
    "id": null,
    "title": "Node Exporter Full",
    "tags": ["prometheus", "node"],
    "timezone": "browser",
    "schemaVersion": 36,
    "refresh": "30s",
    "panels": [
      {
        "id": 1,
        "title": "CPU Usage",
        "type": "timeseries",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 70},
                {"color": "red", "value": 85}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Memory Usage",
        "type": "gauge",
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {"color": "green", "value": 0},
                {"color": "yellow", "value": 70},
                {"color": "red", "value": 85}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      }
    ]
  },
  "overwrite": true
}
```

### 告警规则配置
```yaml
# provisioning/alerting/alerts.yml
apiVersion: 1

groups:
  - orgId: 1
    name: infrastructure
    folder: Infrastructure
    interval: 60s
    rules:
      - uid: high-cpu-usage
        title: High CPU Usage
        condition: B
        data:
          - refId: A
            relativeTimeRange:
              from: 300
              to: 0
            datasourceUid: prometheus
            model:
              expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
              refId: A
          - refId: B
            relativeTimeRange:
              from: 0
              to: 0
            datasourceUid: __expr__
            model:
              type: threshold
              expression: A
              conditions:
                - evaluator:
                    type: gt
                    params: [80]
        noDataState: NoData
        execErrState: Error
        for: 5m
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"
        labels:
          severity: warning

  - orgId: 1
    name: notifications
    folder: Notifications
    interval: 60s
    rules:
      - uid: high-memory-usage
        title: High Memory Usage
        condition: B
        for: 10m
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
        labels:
          severity: critical
```

### 通知渠道配置
```yaml
# provisioning/alerting/contact-points.yml
apiVersion: 1

contactPoints:
  - orgId: 1
    name: default
    receivers:
      - uid: slack-alerts
        type: slack
        settings:
          url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
          title: "{{ .CommonAnnotations.summary }}"
          text: "{{ .CommonAnnotations.description }}"
          username: Grafana Alert
          icon_emoji: ":warning:"
          
      - uid: email-alerts
        type: email
        settings:
          addresses: "admin@example.com;oncall@example.com"
          singleEmail: false
          
      - uid: pagerduty-alerts
        type: pagerduty
        settings:
          integrationKey: "YOUR_PAGERDUTY_KEY"
          severity: critical

policies:
  - orgId: 1
    receiver: default
    group_by: ['alertname', 'severity']
    group_wait: 30s
    group_interval: 5m
    repeat_interval: 4h
    routes:
      - receiver: slack-alerts
        matchers:
          - severity = warning
      - receiver: pagerduty-alerts
        matchers:
          - severity = critical
```

## 示例

### 完整监控架构
```
┌─────────────────────────────────────────────────────────────┐
│                        Grafana UI                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Dashboard  │  │   Alerts    │  │   Explore (Ad-hoc)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
┌───────▼─────┐ ┌───▼────┐ ┌────▼────┐ ┌────▼────┐
│ Prometheus  │ │  Loki  │ │ Jaeger  │ │ InfluxDB│
│  (Metrics)  │ │ (Logs) │ │(Traces) │ │  (IoT)  │
└───────┬─────┘ └───┬────┘ └────┬────┘ └────┬────┘
        │           │           │           │
    ┌───┴───┐   ┌───┴───┐   ┌───┴───┐   ┌───┴───┐
    │Node   │   │Promtail│   │App    │   │Telegraf│
    │Exporter│   │       │   │SDK    │   │        │
    └───────┘   └───────┘   └───────┘   └───────┘
```

### 变量和模板示例
```json
{
  "templating": {
    "list": [
      {
        "name": "datasource",
        "type": "datasource",
        "query": "prometheus",
        "current": {"text": "Prometheus", "value": "prometheus"}
      },
      {
        "name": "namespace",
        "type": "query",
        "datasource": {"type": "prometheus", "uid": "${datasource}"},
        "query": "label_values(kube_namespace_labels, namespace)",
        "multi": true,
        "includeAll": true,
        "allValue": ".*"
      },
      {
        "name": "pod",
        "type": "query",
        "datasource": {"type": "prometheus", "uid": "${datasource}"},
        "query": "label_values(kube_pod_info{namespace=~\"$namespace\"}, pod)",
        "multi": true,
        "includeAll": true
      },
      {
        "name": "interval",
        "type": "interval",
        "query": "1m,5m,10m,30m,1h,6h,12h,1d",
        "current": {"text": "5m", "value": "5m"}
      }
    ]
  }
}
```

### LogQL 查询示例
```
# 基础日志查询
{app="api", level=~"error|warn"}

# 带过滤的日志
{namespace="production"} |= "ERROR" != "DEBUG" |~ "timeout|connection refused"

# 日志统计
sum by (level) (count_over_time({app="api"} [5m]))

# 日志聚合
quantile_over_time(0.95, 
  {app="api"} 
  | json 
  | unwrap duration(response_time) [5m]
) by (method)
```

## 应用场景

| 场景 | 关键功能 | 推荐面板 |
|------|----------|----------|
| **基础设施监控** | Node Exporter + Prometheus | CPU、内存、磁盘、网络 |
| **Kubernetes 监控** | kube-state-metrics + cAdvisor | Pod 状态、资源使用、集群概览 |
| **应用性能监控** | APM 集成 + 日志关联 | 响应时间、错误率、吞吐量 |
| **业务指标分析** | SQL 数据源 + 变量 | 转化率、DAU、收入趋势 |
| **日志分析** | Loki + LogQL | 实时日志流、错误聚合 |
| **分布式追踪** | Jaeger/Tempo + TraceQL | 调用链分析、延迟分解 |

## 面试要点

Q: Grafana 与 Prometheus 的关系？
A: Grafana 是可视化层，Prometheus 是时序数据库和告警引擎。Grafana 可以查询 Prometheus 数据，但 Grafana 8.0+ 也内置了告警系统，可以独立配置告警。

Q: 如何优化大规模仪表板的性能？
A: 1) 限制查询时间范围；2) 使用 Recording Rules 预处理复杂查询；3) 减少面板数量或分页；4) 使用模板变量减少查询数据量；5) 启用查询缓存；6) 使用 Streaming 实时数据。

Q: Grafana 的访问控制机制？
A: 支持组织 (Org) 级别的数据隔离，基于角色的访问控制 (RBAC) 包括 Viewer/Editor/Admin，细粒度权限可控制数据源、仪表板、文件夹级别访问。

Q: 如何实现日志、指标、追踪的关联？
A: 使用统一标签（如 trace_id、span_id），在 Grafana 中配置数据源之间的链接（如从指标跳转到日志、从日志跳转到追踪），使用 Derived Fields 提取和链接 Trace ID。

Q: 告警状态转换流程？
A: Normal → Pending（满足条件但未达持续时间）→ Firing（持续满足条件，发送通知）→ Resolved（条件不再满足）。支持 NoData 和 Error 状态处理。

## 相关概念

### 数据结构
- **时序数据模型**: (timestamp, value) 序列，带标签
- **倒排索引**: 日志标签的快速检索
- **R树/R*树**: 空间/时间范围查询索引

### 算法
- **降采样算法**: 展示大规模数据时的采样策略
- **异常检测**: 基于统计或 ML 的告警规则
- **告警去重**: 分组和抑制算法

### 复杂度分析
- **查询复杂度**: 范围查询 O(log n + k)，聚合查询 O(n)
- **可视化渲染**: 大量数据点时的浏览器性能优化

### 系统实现
- **React 前端**: 现代 UI 框架实现
- **Go 后端**: 高性能查询代理和告警引擎
- **插件架构**: 数据源和面板的可扩展机制

### 对比参考
- [Prometheus](./prometheus.md) - 指标收集和告警
- [ELK Stack](./elk-stack.md) - 日志分析方案对比
- [Jaeger](./jaeger.md) - 分布式追踪集成
- [微服务架构](../microservices.md) - 监控需求背景
- [服务网格](../service-mesh.md) - 可观测性集成
