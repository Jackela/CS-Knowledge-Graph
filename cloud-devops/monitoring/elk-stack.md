# ELK Stack (日志分析)

## 简介

ELK Stack 是业界最流行的开源日志分析平台，由 Elasticsearch（搜索引擎）、Logstash（数据收集处理）、Kibana（可视化）三大核心组件组成，加上轻量级数据收集器 Beats，形成完整的日志采集、存储、分析和可视化解决方案。

## 核心概念

### Elasticsearch
- **分布式搜索**: 基于 Apache Lucene 的倒排索引
- **文档存储**: JSON 格式的文档，无 Schema 灵活存储
- **分片和副本**: 数据水平拆分和冗余保障
- **近实时搜索**: 文档索引后1秒内可搜索
- **聚合分析**: Bucket、Metric、Pipeline 聚合

### Logstash
- **管道处理**: Input → Filter → Output 三阶段
- **插件生态**: 丰富的输入、过滤、输出插件
- ** grok 解析**: 正则匹配非结构化日志
- **条件处理**: 基于字段的条件路由
- **持久化队列**: 磁盘缓冲保证数据不丢失

### Kibana
- **数据探索**: Discover 模式搜索和过滤日志
- **可视化**: 各种图表和仪表板
- **Canvas**: 像素级精确的展示
- **Maps**: 地理空间数据可视化
- **Alerting**: 基于查询的告警（需商业许可或开源替代）

### Beats
| Beat | 用途 |
|------|------|
| **Filebeat** | 日志文件收集 |
| **Metricbeat** | 系统和服务指标 |
| **Packetbeat** | 网络流量分析 |
| **Heartbeat** | 可用性监控（Uptime） |
| **Auditbeat** | 安全审计数据 |
| **Functionbeat** | Serverless 数据收集 |

## 实现方式

### Docker Compose 部署
```yaml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - cluster.routing.allocation.disk.threshold_enabled=false
    volumes:
      - es-data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - elk

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: logstash
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
      - ./logstash/config:/usr/share/logstash/config
    ports:
      - "5044:5044"
      - "5000:5000/tcp"
      - "5000:5000/udp"
      - "9600:9600"
    environment:
      - "LS_JAVA_OPTS=-Xms256m -Xmx256m"
    networks:
      - elk
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    networks:
      - elk
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    container_name: filebeat
    volumes:
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - elk
    depends_on:
      - logstash

volumes:
  es-data:

networks:
  elk:
    driver: bridge
```

### Logstash 管道配置
```ruby
# logstash/pipeline/logstash.conf
input {
  beats {
    port => 5044
  }
  
  tcp {
    port => 5000
    codec => json
  }
  
  syslog {
    port => 5514
    type => "syslog"
  }
}

filter {
  if [type] == "syslog" {
    grok {
      match => { 
        "message" => "%{SYSLOGTIMESTAMP:syslog_timestamp} %{SYSLOGHOST:syslog_hostname} %{DATA:syslog_program}(?:\[%{POSINT:syslog_pid}\])?: %{GREEDYDATA:syslog_message}" 
      }
      add_field => [ "received_at", "%{@timestamp}" ]
      add_field => [ "received_from", "%{host}" ]
    }
    
    date {
      match => [ "syslog_timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
    }
  }
  
  if [fields][log_type] == "nginx" {
    grok {
      match => {
        "message" => "%{COMBINEDAPACHELOG}"
      }
    }
    
    mutate {
      convert => {
        "response" => "integer"
        "bytes" => "integer"
      }
    }
    
    geoip {
      source => "clientip"
      target => "geoip"
    }
    
    useragent {
      source => "agent"
      target => "user_agent"
    }
  }
  
  if [fields][log_type] == "application" {
    json {
      source => "message"
      skip_on_invalid_json => true
    }
    
    if [timestamp] {
      date {
        match => [ "timestamp", "ISO8601" ]
        target => "@timestamp"
      }
    }
  }
  
  # 删除不必要的字段
  mutate {
    remove_field => [ "@version", "beat", "input", "offset", "prospector" ]
  }
}

output {
  if [fields][log_type] == "nginx" {
    elasticsearch {
      hosts => ["elasticsearch:9200"]
      index => "nginx-%{+YYYY.MM.dd}"
      template_name => "nginx"
    }
  } else if [fields][log_type] == "application" {
    elasticsearch {
      hosts => ["elasticsearch:9200"]
      index => "app-%{+YYYY.MM.dd}"
    }
  } else {
    elasticsearch {
      hosts => ["elasticsearch:9200"]
      index => "logstash-%{+YYYY.MM.dd}"
    }
  }
  
  # 调试输出
  # stdout { codec => rubydebug }
}
```

### Filebeat 配置
```yaml
# filebeat/filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/syslog
    - /var/log/auth.log
  fields:
    log_type: syslog
  fields_under_root: true
  multiline.pattern: '^\['
  multiline.negate: true
  multiline.match: after

- type: log
  enabled: true
  paths:
    - /var/log/nginx/*.log
  fields:
    log_type: nginx
  fields_under_root: true

- type: container
  enabled: true
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
    - add_docker_metadata:
        host: "unix:///var/run/docker.sock"
  fields:
    log_type: container
  fields_under_root: true

filebeat.modules:
  - module: system
    syslog:
      enabled: true
    auth:
      enabled: true

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_cloud_metadata: ~
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~

output.logstash:
  hosts: ["logstash:5044"]
  bulk_max_size: 1024
  worker: 2

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
```

### Elasticsearch 索引模板
```json
{
  "index_patterns": ["app-*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "index.refresh_interval": "5s"
  },
  "mappings": {
    "properties": {
      "@timestamp": {
        "type": "date"
      },
      "level": {
        "type": "keyword"
      },
      "message": {
        "type": "text",
        "analyzer": "standard"
      },
      "service": {
        "type": "keyword"
      },
      "trace_id": {
        "type": "keyword"
      },
      "span_id": {
        "type": "keyword"
      },
      "user_id": {
        "type": "keyword"
      },
      "response_time_ms": {
        "type": "integer"
      },
      "status_code": {
        "type": "integer"
      }
    }
  },
  "aliases": {
    "app-logs": {}
  }
}
```

### Kibana 索引模式设置
```json
{
  "attributes": {
    "title": "app-*",
    "timeFieldName": "@timestamp",
    "fields": "[...]",
    "sourceFilters": "[]"
  }
}
```

## 示例

### 完整日志架构
```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐ │
│  │ App Logs│  │ Nginx   │  │ System  │  │ Audit   │  │  APM   │ │
│  │ (JSON)  │  │ (Text)  │  │ (Syslog)│  │ (Linux) │  │ (Traces)│ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └───┬────┘ │
└───────┼────────────┼────────────┼────────────┼────────────┼──────┘
        │            │            │            │            │
┌───────▼────────────▼────────────▼────────────▼────────────▼──────┐
│                         Beats Collection                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Filebeat │  │Filebeat  │  │Filebeat  │  │Auditbeat │  ...      │
│  │(App/Nginx│  │ (System) │  │(Syslog)  │  │          │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
└───────┼─────────────┼─────────────┼─────────────┼─────────────────┘
        │             │             │             │
        └─────────────┴──────┬──────┴─────────────┘
                             │
                    ┌────────▼────────┐
                    │    Logstash     │
                    │  (Parsing/ENR)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Elasticsearch   │
                    │  (Index/Search) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     Kibana      │
                    │(Visualize/Alert)│
                    └─────────────────┘
```

### Grok 模式示例
```ruby
# Apache/Nginx Combined Log
%{COMBINEDAPACHELOG} = %{IPORHOST:clientip} %{HTTPDUSER:ident} %{USER:auth} \[%{HTTPDATE:timestamp}\] "(?:%{WORD:verb} %{NOTSPACE:request}(?: HTTP/%{NUMBER:httpversion})?|%{DATA:rawrequest})" %{NUMBER:response} (?:%{NUMBER:bytes}|-) %{QS:referrer} %{QS:agent}

# 自定义应用日志
%{TIMESTAMP_ISO8601:log_timestamp} %{LOGLEVEL:level} \[%{DATA:service}\] %{DATA:trace_id} - %{GREEDYDATA:message}

# Java 异常堆栈
%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{JAVAFILE:file}:%{NUMBER:line} - %{GREEDYDATA:message}(\n%{SPACE}at %{JAVASTACKTRACEPART:stacktrace})*
```

### 聚合查询 DSL
```json
{
  "size": 0,
  "query": {
    "bool": {
      "filter": [
        {"range": {"@timestamp": {"gte": "now-1h"}}},
        {"term": {"service": "api-gateway"}}
      ]
    }
  },
  "aggs": {
    "errors_over_time": {
      "date_histogram": {
        "field": "@timestamp",
        "fixed_interval": "5m"
      },
      "aggs": {
        "error_count": {
          "filter": {"term": {"level": "ERROR"}}
        },
        "avg_response_time": {
          "avg": {"field": "response_time_ms"}
        },
        "percentiles_response_time": {
          "percentiles": {
            "field": "response_time_ms",
            "percents": [50, 95, 99]
          }
        }
      }
    },
    "top_errors": {
      "terms": {
        "field": "message.keyword",
        "size": 10
      }
    }
  }
}
```

## 应用场景

| 场景 | 关键特性 | 配置要点 |
|------|----------|----------|
| **集中式日志管理** | Filebeat + Logstash + ES | 多行合并，字段提取 |
| **安全分析 (SIEM)** | Auditbeat + Alerting | 异常检测，规则引擎 |
| **应用性能分析** | APM Server + Trace 关联 | 分布式追踪，慢查询 |
| **业务智能分析** | 聚合查询 + 可视化 | 自定义 Dashboard |
| **合规审计** | 索引生命周期 + 归档 | 数据保留策略 |
| **实时告警** | Watcher/Alerting | 阈值告警，通知渠道 |

## 面试要点

Q: ELK 与 Loki 的主要区别？
A: ELK 是完整的索引方案，所有日志字段都索引，查询快但存储成本高；Loki 只索引标签，日志内容压缩存储，成本低但全文搜索需要扫描，适合云原生大规模日志。

Q: 如何优化 Elasticsearch 写入性能？
A: 1) 批量写入（Bulk API）；2) 调整刷新间隔（index.refresh_interval）；3) 禁用副本（初始导入时）；4) 使用自动生成 ID；5) 调整合并策略；6) 合理设置分片数。

Q: Logstash 的过滤器执行顺序？
A: 按配置文件中的顺序执行，条件判断（if/else）支持动态路由。常用优化：先做 cheap 的过滤（如 mutate remove_field），再做 expensive 的（如 geoip）。

Q: 如何设计日志索引策略？
A: 按时间分索引（如 app-YYYY.MM.dd），便于生命周期管理；使用索引模板预定义 Mapping；设置合理的分片数（避免过多过小）；配置 ILM（Index Lifecycle Management）自动归档和删除。

Q: Elasticsearch 脑裂问题及解决？
A: 脑裂是多个节点认为自己是 Master。解决：设置 discovery.seed_hosts 和 cluster.initial_master_nodes，配置 minimum_master_nodes（7.x 后自动处理），使用专用 Master 节点。

## 相关概念

### 数据结构
- **倒排索引**: 词项到文档的映射，支持快速全文搜索
- **BKD树**: 数值和地理数据的索引结构
- **FST (有限状态转换器)**: 词条字典压缩存储

### 算法
- **TF-IDF/BM25**: 相关性评分算法
- **布隆过滤器**: 快速判断文档是否存在
- **分词算法**: IK、jieba 等中文分词

### 复杂度分析
- **搜索复杂度**: 倒排索引查找 O(1)，聚合 O(n)
- **写入复杂度**: 索引构建 O(n log n)，取决于分词
- **存储空间**: 原始日志的 1.1x-1.5x（含索引）

### 系统实现
- **Lucene**: 底层搜索库，段（Segment）的不可变设计
- **Zen Discovery**: 节点发现和集群协调
- **Translog**: 写前日志，保证持久化

### 对比参考
- [Grafana](./grafana.md) - 可视化平台对比
- [Prometheus](./prometheus.md) - 时序数据方案
- [分布式追踪](./jaeger.md) - Trace 集成
- [分布式系统日志](../../distributed-systems/distributed-log.md) - 日志原理
