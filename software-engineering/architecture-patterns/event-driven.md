# 事件驱动架构 (Event-Driven Architecture)

## 概念

事件驱动架构（Event-Driven Architecture, EDA）是一种**架构模式**，组件通过事件的产生、检测和消费进行通信。

> **核心思想**: 松耦合、异步、响应式。

---

## 核心组件

### 1. 事件生产者 (Producer)

```python
class OrderService:
    def __init__(self, event_bus):
        self.event_bus = event_bus
    
    def create_order(self, order_data):
        order = self.save_order(order_data)
        # 发布事件
        self.event_bus.publish('order.created', {
            'order_id': order.id,
            'user_id': order.user_id,
            'amount': order.amount
        })
        return order
```

### 2. 事件消费者 (Consumer)

```python
class PaymentService:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.event_bus.subscribe('order.created', self.handle_order_created)
    
    def handle_order_created(self, event):
        order_id = event['order_id']
        amount = event['amount']
        self.process_payment(order_id, amount)
```

### 3. 事件总线 (Event Bus)

```python
from typing import Dict, List, Callable

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def publish(self, event_type: str, event_data: dict):
        handlers = self.subscribers.get(event_type, [])
        for handler in handlers:
            handler(event_data)
```

---

## 事件模式

### 1. 事件通知

```
Producer -> Event -> Consumer (查询获取详情)
```

### 2. 事件携带状态转移 (Event-Carried State Transfer)

```
Producer -> Event(含完整数据) -> Consumer (无需查询)
```

### 3. 事件溯源 (Event Sourcing)

```
Command -> Event -> Event Store -> 重建状态
```

---

## 优缺点

**优点**:
- 松耦合
- 可扩展
- 响应式
- 审计追踪

**缺点**:
- 调试困难
- 事件顺序
- 一致性挑战

---

## 面试要点

1. **vs 消息队列**: EDA 是架构，MQ 是实现
2. **事件顺序**: 时间戳、序列号
3. **幂等性**: 重复事件处理

---

## 相关概念

- [CQRS](./cqrs.md)
- [事件溯源](./event-sourcing.md)
- [消息队列](../../../cloud-devops/messaging.md)
