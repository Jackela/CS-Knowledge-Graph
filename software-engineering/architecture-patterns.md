# 架构模式 (Architecture Patterns)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、经典架构著作及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**架构模式 (Architecture Patterns)** 是在软件架构层面解决常见问题的通用、可复用的解决方案。它们描述了一组组件、它们之间的关系，以及控制它们设计和演化的规则。架构模式决定了系统的整体结构、组织方式和交互方式。

```
┌─────────────────────────────────────────────────────────────────┐
│                   架构模式 vs 设计模式                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   架构模式                          设计模式                    │
│   ├─ 系统级别                       ├─ 类/对象级别              │
│   ├─ 影响整个应用                   ├─ 影响单个组件             │
│   ├─ 决定技术栈选择                 ├─ 与语言无关               │
│   ├─ 难以改变                       ├─ 相对容易重构             │
│   └─ 关注非功能需求                 └─ 关注功能实现             │
│                                                                 │
│   常见架构模式：                                                │
│   • 分层架构 (Layered)                                          │
│   • 微服务架构 (Microservices)                                  │
│   • 事件驱动架构 (Event-Driven)                                 │
│   • 微内核架构 (Microkernel)                                    │
│   • 管道-过滤器 (Pipes and Filters)                             │
│   • 客户端-服务器 (Client-Server)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. 分层架构 (Layered Architecture)

分层架构是最常见的架构模式，将系统划分为若干水平层，每层有明确的职责。

```
┌─────────────────────────────────────────────────────────────────┐
│                   分层架构 - 四层架构示例                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  表现层 (Presentation)                                   │   │
│   │  - Controllers / Views / API Endpoints                  │   │
│   │  - 处理用户输入和输出                                   │   │
│   │  - 数据格式转换 (DTO)                                   │   │
│   └────────────────────┬────────────────────────────────────┘   │
│                        │ 调用应用层                              │
│   ┌────────────────────▼────────────────────────────────────┐   │
│   │  应用层 (Application)                                    │   │
│   │  - Services / Use Cases                                 │   │
│   │  - 编排业务逻辑                                         │   │
│   │  - 事务管理                                             │   │
│   └────────────────────┬────────────────────────────────────┘   │
│                        │ 调用领域层                              │
│   ┌────────────────────▼────────────────────────────────────┐   │
│   │  领域层 (Domain)                                         │   │
│   │  - Entities / Value Objects                             │   │
│   │  - Domain Services                                      │   │
│   │  - 核心业务逻辑 (DDD)                                   │   │
│   └────────────────────┬────────────────────────────────────┘   │
│                        │ 调用基础设施层                          │
│   ┌────────────────────▼────────────────────────────────────┐   │
│   │  基础设施层 (Infrastructure)                             │   │
│   │  - Repositories / Database                              │   │
│   │  - External APIs / Message Queue                        │   │
│   │  - 技术实现细节                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   依赖规则：上层依赖下层，下层不依赖上层                        │
│   跨层调用：只能通过相邻层，不能跨层调用                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 分层架构优缺点

| 优点 | 缺点 |
|------|------|
| 关注点分离，易于理解 | 可能导致性能开销（多层传递） |
| 层内高内聚，层间低耦合 | 小改动可能需要修改多层 |
| 易于测试（可Mock层） | 可能导致贫血领域模型 |
| 团队可分层分工 | 严格分层可能限制灵活性 |

---

## 2. 微服务架构 (Microservices Architecture)

微服务架构将应用拆分为小型、独立部署的服务，每个服务围绕业务能力构建。

```
┌─────────────────────────────────────────────────────────────────┐
│                   微服务架构                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│   │  API    │ │  User   │ │  Order  │ │Payment  │ │Inventory│   │
│   │ Gateway │ │ Service │ │ Service │ │ Service │ │ Service │   │
│   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │
│        │           │           │           │           │        │
│        └───────────┴─────┬─────┴───────────┴───────────┘        │
│                          │                                       │
│                   ┌──────┴──────┐                                │
│                   │ Message Bus │  (异步通信)                    │
│                   └─────────────┘                                │
│                                                                 │
│   服务拆分原则：                                                │
│   • 按业务能力拆分                                              │
│   • 每个服务有独立数据库                                        │
│   • 服务间通过API通信                                           │
│   • 独立部署、独立扩展                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 微服务通信模式

```python
# 1. 同步通信 - REST/HTTP
import requests

def get_user_info(user_id):
    response = requests.get(f"http://user-service/users/{user_id}")
    return response.json()

# 2. 异步通信 - 消息队列
import pika

def publish_order_created(order):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='orders')
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=json.dumps(order)
    )

# 3. gRPC - 高性能RPC
def create_user_grpc(user_request):
    channel = grpc.insecure_channel('user-service:50051')
    stub = user_pb2_grpc.UserServiceStub(channel)
    response = stub.CreateUser(user_request)
    return response
```

### 微服务数据管理

```
┌─────────────────────────────────────────────────────────────────┐
│                   微服务数据管理 - Database per Service          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐                │
│   │  User   │      │  Order  │      │ Payment │                │
│   │ Service │      │ Service │      │ Service │                │
│   └────┬────┘      └────┬────┘      └────┬────┘                │
│        │                │                │                      │
│   ┌────┴────┐      ┌────┴────┐      ┌────┴────┐                │
│   │ User DB │      │ Order DB│      │PaymentDB│                │
│   │ (MySQL) │      │ (Mongo) │      │ (Postgre│                │
│   └─────────┘      └─────────┘      └─────────┘                │
│                                                                 │
│   跨服务数据查询方案：                                          │
│   1. API Composition - 调用多个服务组装数据                    │
│   2. CQRS - 分离读写，使用物化视图                             │
│   3. Saga - 分布式事务                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 事件驱动架构 (Event-Driven Architecture)

系统组件通过事件的生产、检测和消费进行通信，实现松耦合和可扩展性。

```
┌─────────────────────────────────────────────────────────────────┐
│                   事件驱动架构                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐    Event      ┌─────────┐    Event      ┌──────┐ │
│   │Producer │──────────────▶│  Event  │──────────────▶│Consumer│ │
│   │(Publisher)              │  Bus    │               │        │ │
│   └─────────┘               │(Broker) │               └────────┘ │
│                             └────┬────┘                          │
│                                  │                              │
│                                  ▼                              │
│   ┌─────────┐               ┌─────────┐               ┌────────┐│
│   │Producer │──────────────▶│  Event  │──────────────▶│Consumer││
│   └─────────┘               │  Store  │               └────────┘│
│                             └─────────┘                         │
│                                                                 │
│   模式：                                                        │
│   • 发布-订阅 (Pub/Sub) - 一对多广播                            │
│   • 事件溯源 (Event Sourcing) - 状态=所有事件的聚合             │
│   • CQRS - 命令查询职责分离                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 事件溯源示例

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class DomainEvent:
    event_id: str
    aggregate_id: str
    event_type: str
    timestamp: datetime
    payload: dict

class BankAccount:
    """事件溯源账户"""
    
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.balance = 0
        self.version = 0
        self.events: List[DomainEvent] = []
    
    def apply_event(self, event: DomainEvent):
        """应用事件到状态"""
        if event.event_type == 'DEPOSITED':
            self.balance += event.payload['amount']
        elif event.event_type == 'WITHDRAWN':
            self.balance -= event.payload['amount']
        self.version += 1
    
    def deposit(self, amount: float):
        event = DomainEvent(
            event_id=str(uuid4()),
            aggregate_id=self.account_id,
            event_type='DEPOSITED',
            timestamp=datetime.now(),
            payload={'amount': amount}
        )
        self.events.append(event)
        self.apply_event(event)
    
    @classmethod
    def replay_events(cls, account_id: str, events: List[DomainEvent]):
        """重放事件重建状态"""
        account = cls(account_id)
        for event in sorted(events, key=lambda e: e.timestamp):
            account.apply_event(event)
        return account
```

---

## 4. 微内核架构 (Microkernel / Plugin Architecture)

核心系统提供最小功能，通过插件扩展功能。

```
┌─────────────────────────────────────────────────────────────────┐
│                   微内核架构                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  Core System (微内核)                    │   │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │
│   │  │ Plugin  │  │ Plugin  │  │ Plugin  │  │ Plugin  │     │   │
│   │  │Manager  │  │Registry │  │Lifecycle│  │  API    │     │   │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │   │
│   └──────────────────────────┬──────────────────────────────┘   │
│                              │ Plugin Interface                 │
│   ┌──────────┬──────────┬────┴────┬──────────┬──────────┐      │
│   ▼          ▼          ▼          ▼          ▼          ▼      │
│ ┌────┐   ┌────┐   ┌────┐   ┌────┐   ┌────┐   ┌────┐            │
│ │P-1 │   │P-2 │   │P-3 │   │P-4 │   │P-5 │   │P-6 │  插件      │
│ └────┘   └────┘   └────┘   └────┘   └────┘   └────┘            │
│                                                                 │
│   示例：Eclipse IDE、VS Code、Chrome扩展                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. 管道-过滤器架构 (Pipes and Filters)

数据流经过一系列处理步骤（过滤器），通过管道连接。

```
┌─────────────────────────────────────────────────────────────────┐
│                   管道-过滤器架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Source ──▶ Filter1 ──▶ Filter2 ──▶ Filter3 ──▶ Sink          │
│            (提取)      (转换)      (格式化)                      │
│                                                                 │
│   示例：Unix Shell命令                                          │
│   cat file.txt | grep "error" | sort | uniq -c                 │
│                                                                 │
│   示例：编译器                                                   │
│   Source ──▶ Lexer ──▶ Parser ──▶ Optimizer ──▶ CodeGen        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 架构模式对比

| 架构模式 | 优点 | 缺点 | 适用场景 |
|----------|------|------|----------|
| 分层架构 | 简单、易理解 | 性能开销 | 传统企业应用 |
| 微服务 | 独立扩展、技术多样 | 分布式复杂性 | 大型复杂系统 |
| 事件驱动 | 松耦合、可扩展 | 调试困难 | 实时处理、IoT |
| 微内核 | 可扩展、热插拔 | 插件管理复杂 | IDE、浏览器 |
| 管道-过滤器 | 可组合、可重用 | 不适合交互式 | 数据处理、编译器 |

---

## 架构演进

```
单体 ──────▶ 模块化 ──────▶ 微服务

阶段1: 单体应用
┌─────────────────┐
│   Monolith      │
└─────────────────┘

阶段2: 模块化单体
┌─────────────────────────┐
│ ┌─────┐┌─────┐┌─────┐  │
│ │Mod-1││Mod-2││Mod-3│  │
│ └─────┘└─────┘└─────┘  │
└─────────────────────────┘

阶段3: 微服务
┌─────┐┌─────┐┌─────┐
│ Svc-1││Svc-2││Svc-3│
└─────┘└─────┘└─────┘
```

---

## 面试要点

**Q1: 微服务和单体架构如何选择？**> 微服务适合：团队大、业务复杂、需要独立扩展、多技术栈。单体适合：团队小、业务简单、快速启动、低运维成本。可以从单体开始，业务增长后再拆分。

**Q2: 事件驱动架构的挑战？**> 1) 最终一致性 - 数据同步有延迟；2) 调试困难 - 异步流程难追踪；3) 事件顺序 - 保证处理顺序复杂；4) 错误处理 - 需要死信队列等机制。

**Q3: CQRS是什么？**> Command Query Responsibility Segregation，将读操作和写操作分离。写模型使用领域模型，读模型使用物化视图优化查询。适合读多写少、查询模式多样的场景。

---

## 相关概念

- [设计模式](./design-patterns.md) - 代码级别的设计模式
- [领域驱动设计](./ddd.md) - 复杂系统的领域建模
- [分布式系统](../computer-science/distributed-systems/sharding.md) - 微服务的技术基础
- [微服务架构](./architecture-patterns/microservices.md) - 细粒度的服务拆分模式
- [事件驱动架构](./architecture-patterns/event-driven.md) - 异步消息通信模式
- [SOLID原则](./solid-principles.md) - 面向对象设计原则
- [CAP定理](../computer-science/distributed-systems/cap-theorem.md) - 分布式系统核心理论
- [负载均衡](../computer-science/distributed-systems/load-balancing.md) - 流量分发技术
- [分片](../computer-science/distributed-systems/sharding.md) - 数据水平拆分策略
#### AI与数据系统
- [LLM架构](../ai-data-systems/llm.md) - AI原生架构设计
---

## 参考资料

1. "Software Architecture Patterns" by Mark Richards
2. "Building Microservices" by Sam Newman
3. "Patterns of Enterprise Application Architecture" by Martin Fowler
4. The Twelve-Factor App: https://12factor.net/
5. Microservices.io: https://microservices.io/
