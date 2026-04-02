# 领域事件 (Domain Events)

## 简介

**领域事件 (Domain Event)** 是领域驱动设计中用于捕获领域中有意义业务发生的重要概念。它表示过去发生的事实，用于在限界上下文(Bounded Context)之间传递信息，实现松耦合的系统集成。

> **核心原则**: 领域事件是已发生的事实，用过去时态命名(如OrderCreated, PaymentConfirmed)，一经发布不可变更。

```
┌─────────────────────────────────────────────────────────────────┐
│                    领域事件的定位                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   Bounded Context A                      │   │
│   │                   订单上下文                              │   │
│   │                                                         │   │
│   │   ┌─────────┐      ┌─────────────┐     ┌───────────┐   │   │
│   │   │ Order   │ ───▶ │ OrderCreated│ ──▶ │  Event    │   │   │
│   │   │ Aggregate│     │ Domain Event│     │ Publisher │   │   │
│   │   └─────────┘      └─────────────┘     └─────┬─────┘   │   │
│   │                                              │         │   │
│   └──────────────────────────────────────────────┼─────────┘   │
│                                                  │             │
│                           异步消息总线            │             │
│                    ┌─────────────────────────────┘             │
│                    │                                           │
│                    ▼                                           │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   Bounded Context B                      │   │
│   │                   库存上下文                              │   │
│   │                                                         │   │
│   │   ┌───────────┐     ┌─────────────┐     ┌─────────┐    │   │
│   │   │  Event    │ ──▶ │ OrderCreated│ ──▶ │ Inventory│   │   │
│   │   │ Subscriber│     │  Handler    │     │ Service  │   │   │
│   │   └───────────┘     └─────────────┘     └─────────┘    │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   优势: 解耦、最终一致性、可扩展、可追溯                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 核心概念

### 1. 领域事件的特征

| 特征 | 说明 | 示例 |
|------|------|------|
| **不可变性** | 事件表示已发生的事实，不能修改 | OrderCreated一旦发布不可变更 |
| **时态命名** | 使用过去时态命名 | OrderPaid, InventoryReserved |
| **包含上下文** | 携带事件发生时的相关信息 | 订单ID、时间戳、变更数据 |
| **最终一致性** | 不要求立即同步，允许延迟 | 库存扣减可以异步处理 |

### 2. 领域事件 vs 应用事件

```
┌─────────────────────────────────────────────────────────────────┐
│                领域事件 vs 应用事件                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────────────────┐  ┌──────────────────────────┐    │
│   │     Domain Event         │  │    Application Event     │    │
│   │       领域事件            │  │       应用事件            │    │
│   ├──────────────────────────┤  ├──────────────────────────┤    │
│   │ • 表示业务发生的事实      │  │ • 表示系统状态变化        │    │
│   │ • 业务专家能理解          │  │ • 技术层面的通知          │    │
│   │ • 跨限界上下文通信        │  │ • 通常上下文内使用        │    │
│   │ • 用于领域模型演进        │  │ • 用于技术集成            │    │
│   │ • 命名来源于业务术语      │  │ • 命名来源于技术术语      │    │
│   ├──────────────────────────┤  ├──────────────────────────┤    │
│   │ OrderCreated             │  │ UserLoggedIn             │    │
│   │ PaymentReceived          │  │ CacheInvalidated         │    │
│   │ InventoryAllocated       │  │ EmailSent                │    │
│   │ ShipmentDispatched       │  │ LogEntryCreated          │    │
│   └──────────────────────────┘  └──────────────────────────┘    │
│                                                                 │
│   注意: 同一件事可能既是领域事件也是应用事件                      │
│   例如: OrderCreated 是领域事件，传播到其他上下文                 │
│        在订单上下文内部也可作为应用事件触发本地处理               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3. 事件溯源 (Event Sourcing)

```
┌─────────────────────────────────────────────────────────────────┐
│                    事件溯源架构                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   传统方式: 存储最终状态                                          │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐                   │
│   │ State   │ ──▶ │  State  │ ──▶ │  State  │                   │
│   │   v1    │     │   v2    │     │   v3    │                   │
│   └─────────┘     └─────────┘     └─────────┘                   │
│                                                                 │
│   事件溯源: 存储事件序列，状态通过重放事件得到                      │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐   │
│   │ Event 1 │ ──▶ │ Event 2 │ ──▶ │ Event 3 │ ──▶ │ Current │   │
│   │Created  │     │ Updated │     │ Paid    │     │  State  │   │
│   └─────────┘     └─────────┘     └─────────┘     └─────────┘   │
│        │               │               │                        │
│        └───────────────┴───────────────┘                        │
│                    Event Store                                  │
│                                                                 │
│   优势:                                                         │
│   • 完整的审计追踪                                              │
│   • 可回溯到任意时间点的状态                                    │
│   • 便于调试和问题排查                                          │
│   • 天然支持CQRS                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 实现方式

### 基础事件框架

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from uuid import uuid4, UUID
import json
from enum import Enum, auto


# ============================================
# 基础事件定义
# ============================================

@dataclass(frozen=True)
class DomainEvent:
    """
    领域事件基类
    
    属性:
        event_id: 事件唯一标识
        aggregate_id: 关联的聚合根ID
        occurred_on: 事件发生时间
        version: 事件版本(用于并发控制)
        metadata: 额外元数据
    """
    event_id: UUID = field(default_factory=uuid4)
    aggregate_id: str = field(default="")
    occurred_on: datetime = field(default_factory=datetime.utcnow)
    version: int = field(default=1)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def event_type(self) -> str:
        """事件类型，默认使用类名"""
        return self.__class__.__name__
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于序列化"""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "metadata": self.metadata,
            **self._get_event_data()
        }
    
    def _get_event_data(self) -> Dict[str, Any]:
        """子类重写此方法提供事件特定数据"""
        return {}
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), default=str)


# ============================================
# 具体领域事件定义
# ============================================

@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    """订单已创建事件"""
    customer_id: str = ""
    items: List[Dict[str, Any]] = field(default_factory=list)
    total_amount: float = 0.0
    shipping_address: Dict[str, str] = field(default_factory=dict)
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "items": self.items,
            "total_amount": self.total_amount,
            "shipping_address": self.shipping_address
        }


@dataclass(frozen=True)
class OrderConfirmed(DomainEvent):
    """订单已确认事件"""
    confirmed_by: str = ""
    confirmed_at: datetime = field(default_factory=datetime.utcnow)
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "confirmed_by": self.confirmed_by,
            "confirmed_at": self.confirmed_at.isoformat()
        }


@dataclass(frozen=True)
class OrderPaid(DomainEvent):
    """订单已支付事件"""
    payment_id: str = ""
    payment_method: str = ""
    paid_amount: float = 0.0
    transaction_id: str = ""
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "payment_id": self.payment_id,
            "payment_method": self.payment_method,
            "paid_amount": self.paid_amount,
            "transaction_id": self.transaction_id
        }


@dataclass(frozen=True)
class OrderShipped(DomainEvent):
    """订单已发货事件"""
    shipment_id: str = ""
    carrier: str = ""
    tracking_number: str = ""
    shipped_at: datetime = field(default_factory=datetime.utcnow)
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "shipment_id": self.shipment_id,
            "carrier": self.carrier,
            "tracking_number": self.tracking_number,
            "shipped_at": self.shipped_at.isoformat()
        }


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    """订单已取消事件"""
    reason: str = ""
    cancelled_by: str = ""
    cancellation_fee: float = 0.0
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            "reason": self.reason,
            "cancelled_by": self.cancelled_by,
            "cancellation_fee": self.cancellation_fee
        }


@dataclass(frozen=True)
class InventoryReserved(DomainEvent):
    """库存已预留事件"""
    product_id: str = ""
    quantity: int = 0
    warehouse_id: str = ""
    reservation_id: str = ""


@dataclass(frozen=True)
class InventoryReleased(DomainEvent):
    """库存已释放事件"""
    product_id: str = ""
    quantity: int = 0
    reservation_id: str = ""
    reason: str = ""


# ============================================
# 事件发布与订阅
# ============================================

class EventPublisher:
    """
    事件发布器
    
    职责:
    - 管理事件处理器注册
    - 分发事件到对应的处理器
    - 支持同步和异步发布
    """
    
    def __init__(self):
        # 事件类型 -> 处理器列表 的映射
        self._handlers: Dict[str, List[Callable[[DomainEvent], None]]] = {}
        self._async_handlers: Dict[str, List[Callable[[DomainEvent], None]]] = {}
    
    def subscribe(
        self,
        event_type: str,
        handler: Callable[[DomainEvent], None],
        async_mode: bool = False
    ) -> None:
        """
        订阅事件
        
        Args:
            event_type: 事件类型名称
            handler: 事件处理器函数
            async_mode: 是否异步处理
        """
        if async_mode:
            self._async_handlers.setdefault(event_type, []).append(handler)
        else:
            self._handlers.setdefault(event_type, []).append(handler)
    
    def unsubscribe(
        self,
        event_type: str,
        handler: Callable[[DomainEvent], None]
    ) -> None:
        """取消订阅"""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ]
    
    def publish(self, event: DomainEvent) -> None:
        """
        发布事件
        
        先执行同步处理器，再调度异步处理器
        """
        event_type = event.event_type
        
        # 1. 执行同步处理器
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # 记录错误但不阻止其他处理器
                    self._log_handler_error(event, handler, e)
        
        # 2. 调度异步处理器
        if event_type in self._async_handlers:
            for handler in self._async_handlers[event_type]:
                # 实际项目中这里会提交到线程池或消息队列
                self._dispatch_async(handler, event)
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        """批量发布事件"""
        for event in events:
            self.publish(event)
    
    def _dispatch_async(self, handler: Callable, event: DomainEvent) -> None:
        """异步分发事件(简化实现)"""
        # 实际项目使用线程池、Celery、RQ等
        import threading
        thread = threading.Thread(target=handler, args=(event,))
        thread.start()
    
    def _log_handler_error(
        self,
        event: DomainEvent,
        handler: Callable,
        error: Exception
    ) -> None:
        """记录处理器错误"""
        print(f"Error handling event {event.event_type}: {error}")


class DomainEventCollector:
    """
    领域事件收集器
    
    用于在聚合内部收集待发布的事件，
    通常在事务提交前统一发布
    """
    
    def __init__(self):
        self._events: List[DomainEvent] = []
    
    def record(self, event: DomainEvent) -> None:
        """记录事件"""
        self._events.append(event)
    
    def collect(self) -> List[DomainEvent]:
        """收集所有事件并清空"""
        events = self._events.copy()
        self._events.clear()
        return events
    
    def has_events(self) -> bool:
        """是否有待发布事件"""
        return len(self._events) > 0


# ============================================
# 聚合根集成领域事件
# ============================================

class AggregateRoot:
    """
    支持领域事件的聚合根基类
    """
    
    def __init__(self):
        self._domain_events: List[DomainEvent] = []
        self._version: int = 0
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        """获取已记录的领域事件"""
        return self._events.copy()
    
    @property
    def version(self) -> int:
        """聚合版本，用于并发控制"""
        return self._version
    
    def _add_domain_event(self, event: DomainEvent) -> None:
        """添加领域事件"""
        # 设置版本信息
        event_with_version = DomainEvent(
            event_id=event.event_id,
            aggregate_id=event.aggregate_id,
            occurred_on=event.occurred_on,
            version=self._version + 1,
            metadata=event.metadata
        )
        # 这里简化处理，实际应该创建新的具体事件实例
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """清空已处理的事件"""
        self._domain_events.clear()
    
    def apply_event(self, event: DomainEvent) -> None:
        """
        应用事件(事件溯源时使用)
        
        子类应该重写此方法根据事件重建状态
        """
        self._version = event.version


class Order(AggregateRoot):
    """
    订单聚合根 - 集成领域事件
    """
    
    def __init__(self, order_id: str, customer_id: str):
        super().__init__()
        self._order_id = order_id
        self._customer_id = customer_id
        self._status = OrderStatus.CREATED
        self._items: List[Dict] = []
        self._total_amount = 0.0
        self._created_at = datetime.utcnow()
    
    @property
    def order_id(self) -> str:
        return self._order_id
    
    @property
    def status(self) -> 'OrderStatus':
        return self._status
    
    @classmethod
    def create(
        cls,
        order_id: str,
        customer_id: str,
        items: List[Dict],
        total_amount: float,
        shipping_address: Dict
    ) -> 'Order':
        """工厂方法: 创建订单"""
        order = cls(order_id, customer_id)
        order._items = items
        order._total_amount = total_amount
        
        # 记录领域事件
        order._add_domain_event(OrderCreated(
            aggregate_id=order_id,
            customer_id=customer_id,
            items=items,
            total_amount=total_amount,
            shipping_address=shipping_address
        ))
        
        return order
    
    def confirm(self, confirmed_by: str) -> None:
        """确认订单"""
        if self._status != OrderStatus.CREATED:
            raise InvalidOrderStateError("Only created orders can be confirmed")
        
        self._status = OrderStatus.CONFIRMED
        
        # 记录领域事件
        self._add_domain_event(OrderConfirmed(
            aggregate_id=self._order_id,
            confirmed_by=confirmed_by
        ))
    
    def pay(
        self,
        payment_id: str,
        payment_method: str,
        paid_amount: float,
        transaction_id: str
    ) -> None:
        """支付订单"""
        if self._status != OrderStatus.CONFIRMED:
            raise InvalidOrderStateError("Order must be confirmed before payment")
        
        if abs(paid_amount - self._total_amount) > 0.01:
            raise PaymentAmountMismatchError("Payment amount mismatch")
        
        self._status = OrderStatus.PAID
        
        # 记录领域事件
        self._add_domain_event(OrderPaid(
            aggregate_id=self._order_id,
            payment_id=payment_id,
            payment_method=payment_method,
            paid_amount=paid_amount,
            transaction_id=transaction_id
        ))
    
    def ship(
        self,
        shipment_id: str,
        carrier: str,
        tracking_number: str
    ) -> None:
        """发货"""
        if self._status != OrderStatus.PAID:
            raise InvalidOrderStateError("Order must be paid before shipping")
        
        self._status = OrderStatus.SHIPPED
        
        # 记录领域事件
        self._add_domain_event(OrderShipped(
            aggregate_id=self._order_id,
            shipment_id=shipment_id,
            carrier=carrier,
            tracking_number=tracking_number
        ))
    
    def cancel(self, reason: str, cancelled_by: str) -> None:
        """取消订单"""
        if self._status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise InvalidOrderStateError("Cannot cancel shipped or delivered orders")
        
        previous_status = self._status
        self._status = OrderStatus.CANCELLED
        
        # 计算取消费用
        cancellation_fee = self._calculate_cancellation_fee(previous_status)
        
        # 记录领域事件
        self._add_domain_event(OrderCancelled(
            aggregate_id=self._order_id,
            reason=reason,
            cancelled_by=cancelled_by,
            cancellation_fee=cancellation_fee
        ))
    
    def _calculate_cancellation_fee(self, previous_status: 'OrderStatus') -> float:
        """计算取消费用"""
        if previous_status == OrderStatus.PAID:
            return self._total_amount * 0.05  # 5%取消费
        return 0.0
    
    def apply_event(self, event: DomainEvent) -> None:
        """应用事件重建状态(事件溯源)"""
        super().apply_event(event)
        
        if isinstance(event, OrderCreated):
            self._customer_id = event.customer_id
            self._items = event.items
            self._total_amount = event.total_amount
            self._status = OrderStatus.CREATED
        elif isinstance(event, OrderConfirmed):
            self._status = OrderStatus.CONFIRMED
        elif isinstance(event, OrderPaid):
            self._status = OrderStatus.PAID
        elif isinstance(event, OrderShipped):
            self._status = OrderStatus.SHIPPED
        elif isinstance(event, OrderCancelled):
            self._status = OrderStatus.CANCELLED


# ============================================
# 事件处理器
# ============================================

class OrderCreatedHandler:
    """订单创建事件处理器 - 库存上下文"""
    
    def __init__(self, inventory_service: 'InventoryService'):
        self._inventory_service = inventory_service
    
    def handle(self, event: OrderCreated) -> None:
        """处理订单创建事件"""
        for item in event.items:
            self._inventory_service.reserve(
                product_id=item['product_id'],
                quantity=item['quantity'],
                reservation_ref=event.aggregate_id
            )


class OrderPaidHandler:
    """订单支付事件处理器 - 物流上下文"""
    
    def __init__(self, shipment_service: 'ShipmentService'):
        self._shipment_service = shipment_service
    
    def handle(self, event: OrderPaid) -> None:
        """处理订单支付事件"""
        # 创建发货单
        self._shipment_service.create_shipment(
            order_id=event.aggregate_id,
            payment_confirmation=event.payment_id
        )


class OrderCancelledHandler:
    """订单取消事件处理器 - 多上下文处理"""
    
    def __init__(
        self,
        inventory_service: 'InventoryService',
        payment_service: 'PaymentService',
        notification_service: 'NotificationService'
    ):
        self._inventory_service = inventory_service
        self._payment_service = payment_service
        self._notification_service = notification_service
    
    def handle(self, event: OrderCancelled) -> None:
        """处理订单取消事件"""
        # 1. 释放库存
        self._inventory_service.release_by_order(event.aggregate_id)
        
        # 2. 处理退款(如果已支付)
        self._payment_service.process_refund(
            order_id=event.aggregate_id,
            reason=event.reason
        )
        
        # 3. 发送通知
        self._notification_service.send_order_cancelled_notification(
            order_id=event.aggregate_id,
            reason=event.reason
        )


# ============================================
# 事件存储(事件溯源)
# ============================================

class EventStore:
    """
    事件存储
    
    用于持久化领域事件，支持事件溯源
    """
    
    def __init__(self):
        # 简化实现，实际使用数据库
        self._events: Dict[str, List[Dict]] = {}
    
    def append(self, aggregate_id: str, event: DomainEvent) -> None:
        """追加事件"""
        if aggregate_id not in self._events:
            self._events[aggregate_id] = []
        
        self._events[aggregate_id].append({
            "event_type": event.event_type,
            "event_data": event.to_dict(),
            "version": event.version,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_events(
        self,
        aggregate_id: str,
        after_version: int = 0
    ) -> List[DomainEvent]:
        """获取聚合的事件序列"""
        events = self._events.get(aggregate_id, [])
        return [
            self._deserialize(e) for e in events
            if e["version"] > after_version
        ]
    
    def get_all_events(
        self,
        event_types: Optional[List[str]] = None,
        after_position: int = 0,
        limit: int = 100
    ) -> List[DomainEvent]:
        """获取所有事件(用于投影重建)"""
        all_events = []
        for agg_events in self._events.values():
            all_events.extend(agg_events)
        
        # 按时间排序
        all_events.sort(key=lambda e: e["timestamp"])
        
        if event_types:
            all_events = [
                e for e in all_events
                if e["event_type"] in event_types
            ]
        
        return [self._deserialize(e) for e in all_events[after_position:after_position + limit]]
    
    def _deserialize(self, event_record: Dict) -> DomainEvent:
        """反序列化事件"""
        # 简化实现，实际需要根据event_type创建对应的事件类
        event_data = event_record["event_data"]
        return DomainEvent(
            event_id=UUID(event_data["event_id"]),
            aggregate_id=event_data["aggregate_id"],
            occurred_on=datetime.fromisoformat(event_data["occurred_on"]),
            version=event_data["version"],
            metadata=event_data.get("metadata", {})
        )


# ============================================
# 辅助定义
# ============================================

class OrderStatus(Enum):
    CREATED = auto()
    CONFIRMED = auto()
    PAID = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()


class DomainError(Exception):
    """领域异常基类"""
    pass


class InvalidOrderStateError(DomainError):
    """无效订单状态"""
    pass


class PaymentAmountMismatchError(DomainError):
    """支付金额不匹配"""
    pass


# ============================================
# 使用示例
# ============================================

def demo_event_flow():
    """演示事件流"""
    # 1. 创建事件发布器
    publisher = EventPublisher()
    
    # 2. 注册事件处理器
    inventory_handler = OrderCreatedHandler(None)  # 注入实际服务
    publisher.subscribe("OrderCreated", inventory_handler.handle, async_mode=True)
    
    # 3. 创建订单(自动产生领域事件)
    order = Order.create(
        order_id="ORD-2024-001",
        customer_id="CUST-001",
        items=[
            {"product_id": "PROD-001", "quantity": 2, "price": 100.0},
            {"product_id": "PROD-002", "quantity": 1, "price": 200.0}
        ],
        total_amount=400.0,
        shipping_address={"province": "北京", "city": "北京市"}
    )
    
    # 4. 发布事件
    for event in order.domain_events:
        publisher.publish(event)
    
    # 5. 清空已发布事件
    order.clear_domain_events()
