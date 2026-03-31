# 领域驱动设计 (Domain-Driven Design)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自Eric Evans的《领域驱动设计》及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**领域驱动设计 (Domain-Driven Design, DDD)** 是由Eric Evans提出的一套针对复杂业务领域的软件设计方法论。它强调以领域为核心，通过统一语言(Ubiquitous Language)连接业务专家和技术团队，将业务知识转化为软件模型。

```
┌─────────────────────────────────────────────────────────────────┐
│                    DDD核心思想                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   业务领域 ────────▶ 领域模型 ────────▶ 软件实现                │
│   (Domain)           (Model)            (Code)                  │
│      │                  │                  │                    │
│      │   统一语言        │   战略/战术      │   分层架构         │
│      │   知识提炼        │   设计          │   技术实现         │
│      │                  │                  │                    │
│   领域专家◀───────────▶开发团队                                │
│                                                                 │
│   适用场景：                                                    │
│   ✓ 业务逻辑复杂的系统                                          │
│   ✓ 业务规则频繁变化的系统                                      │
│   ✓ 需要长期演进的大型系统                                      │
│   ✗ 简单的CRUD应用                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 战略设计 vs 战术设计

| 维度 | 战略设计 (Strategic) | 战术设计 (Tactical) |
|------|---------------------|---------------------|
| 关注点 | 宏观架构、业务边界 | 具体实现、代码结构 |
| 核心概念 | 限界上下文、领域划分 | 实体、值对象、聚合 |
| 参与人员 | 架构师、领域专家 | 开发团队 |
| 产出物 | 上下文映射、领域愿景 | 类图、代码实现 |

---

## 战略设计 (Strategic Design)

### 1. 限界上下文 (Bounded Context)

**限界上下文**是DDD的核心概念，它定义了领域模型的边界。在同一个限界上下文内，统一语言是一致的；跨上下文则可能需要翻译。

```
┌─────────────────────────────────────────────────────────────────┐
│                   限界上下文示例 - 电商系统                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│   │  销售上下文    │  │  库存上下文    │  │  物流上下文    │       │
│   │               │  │               │  │               │       │
│   │ Product       │  │ Item          │  │ Package       │       │
│   │ - price       │  │ - quantity    │  │ - weight      │       │
│   │ - description │  │ - location    │  │ - destination │       │
│   │ - promotion   │  │ - status      │  │ - tracking    │       │
│   │               │  │               │  │               │       │
│   │ 产品=销售的商品│  │ 商品=库存单元  │  │ 包裹=运输单元  │       │
│   └───────┬───────┘  └───────┬───────┘  └───────┬───────┘       │
│           │                  │                  │               │
│           └──────────────────┴──────────────────┘               │
│                         通过ID关联                              │
│                                                                 │
│   注意：同一概念"Product"在不同上下文有不同含义                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**识别限界上下文的信号**：
- 相同的术语在不同团队有不同理解
- 业务规则的冲突和矛盾
- 自然存在组织架构边界
- 不同的用户群体和使用场景

### 2. 领域与子域

```
┌─────────────────────────────────────────────────────────────────┐
│                   领域拆分示例                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    电商业务领域                                 │
│                         │                                       │
│        ┌────────────────┼────────────────┐                     │
│        │                │                │                     │
│        ▼                ▼                ▼                     │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐                  │
│   │核心子域 │     │支撑子域 │     │通用子域 │                  │
│   │         │     │         │     │         │                  │
│   │ 订单管理 │     │ 库存管理 │     │ 用户认证 │                  │
│   │ 支付处理 │     │ 商品目录 │     │ 日志记录 │                  │
│   │ 优惠计算 │     │ 搜索推荐 │     │ 消息通知 │                  │
│   │         │     │         │     │         │                  │
│   │ 内建/最优│     │ 外购/外包│     │ 现成方案 │                  │
│   └─────────┘     └─────────┘     └─────────┘                  │
│                                                                 │
│   核心域：决定企业竞争优势的业务                                 │
│   支撑域：支持核心业务，但非差异化                               │
│   通用域：通用功能，通常使用现成方案                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3. 上下文映射 (Context Mapping)

上下文映射描述限界上下文之间的关系和集成方式。

```
┌─────────────────────────────────────────────────────────────────┐
│                   上下文映射模式                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. 合作关系 (Partnership)                                    │
│      ┌───────┐ ←──────→ ┌───────┐                              │
│      │ 上下文A│   紧密协作  │ 上下文B│                              │
│      └───────┘          └───────┘                              │
│      两个团队协作紧密，同步迭代                                  │
│                                                                 │
│   2. 共享内核 (Shared Kernel)                                  │
│      ┌───────┐ ╔═════════╗ ┌───────┐                           │
│      │ 上下文A│ ║ 共享模型 ║ │ 上下文B│                           │
│      └───────┘ ╚═════════╝ └───────┘                           │
│      共享部分领域模型，修改需双方同意                             │
│                                                                 │
│   3. 客户-供应商 (Customer-Supplier)                           │
│      ┌───────┐ ────────▶ ┌───────┐                              │
│      │ 供应商 │   下游依赖  │  客户  │                              │
│      └───────┘           └───────┘                              │
│      上游优先满足下游需求                                        │
│                                                                 │
│   4. 遵奉者 (Conformist)                                       │
│      ┌───────┐ ────────▶ ┌───────┐                              │
│      │ 上游   │         │ 下游   │ ← 完全采用上游模型            │
│      └───────┘           └───────┘                              │
│      下游完全接受上游模型，不尝试转换                             │
│                                                                 │
│   5. 防腐层 (Anti-Corruption Layer)                            │
│      ┌───────┐ ╔═══════╗ ┌───────┐                              │
│      │ 本上下文│ ║ ACL ║ │ 外部上下文│                              │
│      └───────┘ ╚═══════╝ └───────┘                              │
│      通过适配器隔离外部模型，保护内部模型纯净                     │
│                                                                 │
│   6. 开放主机服务 (Open Host Service)                          │
│      ┌───────┐ ◀───────▶ ┌───────┐                              │
│      │ 上游   │  公开API  │ 多个下游│                              │
│      └───────┘           └───────┘                              │
│      上游提供统一API供多个下游使用                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 战术设计 (Tactical Design)

### 1. 实体 (Entity)

**实体**是具有唯一标识的领域对象，其标识在整个生命周期中保持不变，即使属性发生变化。

```python
from dataclasses import dataclass, field
from uuid import uuid4
from datetime import datetime

@dataclass
class OrderId:
    """值对象 - 订单ID"""
    value: str
    
    @classmethod
    def generate(cls):
        return cls(str(uuid4()))

class Order:
    """实体 - 订单"""
    def __init__(self, order_id: OrderId, customer_id: str):
        self._order_id = order_id  # 唯一标识
        self._customer_id = customer_id
        self._items = []
        self._status = OrderStatus.CREATED
        self._created_at = datetime.now()
        self._total_amount = 0.0
    
    @property
    def order_id(self) -> OrderId:
        return self._order_id
    
    @property
    def status(self):
        return self._status
    
    def add_item(self, product_id: str, quantity: int, unit_price: float):
        """添加订单项"""
        item = OrderItem(product_id, quantity, unit_price)
        self._items.append(item)
        self._recalculate_total()
    
    def remove_item(self, product_id: str):
        """移除订单项"""
        self._items = [item for item in self._items 
                      if item.product_id != product_id]
        self._recalculate_total()
    
    def confirm(self):
        """确认订单"""
        if self._status != OrderStatus.CREATED:
            raise DomainError("Only created orders can be confirmed")
        self._status = OrderStatus.CONFIRMED
    
    def ship(self):
        """发货"""
        if self._status != OrderStatus.CONFIRMED:
            raise DomainError("Only confirmed orders can be shipped")
        self._status = OrderStatus.SHIPPED
    
    def _recalculate_total(self):
        """重新计算总金额"""
        self._total_amount = sum(
            item.subtotal for item in self._items
        )
    
    def __eq__(self, other):
        """实体通过ID比较"""
        if not isinstance(other, Order):
            return False
        return self._order_id == other._order_id
    
    def __hash__(self):
        return hash(self._order_id)

@dataclass(frozen=True)
class OrderItem:
    """值对象 - 订单项"""
    product_id: str
    quantity: int
    unit_price: float
    
    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price

from enum import Enum, auto

class OrderStatus(Enum):
    CREATED = auto()
    CONFIRMED = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()

class DomainError(Exception):
    pass
```

### 2. 值对象 (Value Object)

**值对象**是没有概念标识的对象，通过属性值来定义，通常是不可变的。

```python
from dataclasses import dataclass
from typing import Optional
import re

@dataclass(frozen=True)
class Money:
    """值对象 - 货币金额"""
    amount: float
    currency: str
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if not re.match(r'^[A-Z]{3}$', self.currency):
            raise ValueError("Currency must be 3-letter ISO code")
    
    def add(self, other: 'Money') -> 'Money':
        """货币相加"""
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: float) -> 'Money':
        """金额乘数"""
        return Money(self.amount * factor, self.currency)
    
    def __str__(self):
        return f"{self.currency} {self.amount:.2f}"

@dataclass(frozen=True)
class Address:
    """值对象 - 地址"""
    country: str
    province: str
    city: str
    district: str
    street: str
    zip_code: str
    
    def format(self) -> str:
        """格式化地址"""
        return f"{self.country}, {self.province} {self.city}, " \
               f"{self.district} {self.street}, {self.zip_code}"

@dataclass(frozen=True)
class Email:
    """值对象 - 邮箱地址"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email: {self.value}")
    
    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def domain(self) -> str:
        return self.value.split('@')[1]
```

**实体 vs 值对象**：

| 特性 | 实体 (Entity) | 值对象 (Value Object) |
|------|--------------|----------------------|
| 标识 | 有唯一标识 | 无标识，由属性定义 |
| 相等性 | 基于ID | 基于属性值 |
| 可变性 | 可变 | 不可变（推荐） |
| 生命周期 | 有独立生命周期 | 依附于实体 |
| 示例 | 订单、用户、产品 | 金额、地址、日期范围 |

### 3. 聚合 (Aggregate)

**聚合**是一组相关对象的集合，作为数据修改的单元。每个聚合都有一个聚合根(Aggregate Root)，外部对象只能通过聚合根访问内部对象。

```
┌─────────────────────────────────────────────────────────────────┐
│                     聚合示例 - 订单聚合                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   订单聚合 (Order Aggregate)              │   │
│   │                                                         │   │
│   │   ┌─────────────┐  ← 聚合根                             │   │
│   │   │   Order     │                                       │   │
│   │   │   (实体)     │                                       │   │
│   │   ├─────────────┤                                       │   │
│   │   │ order_id    │◀── 全局唯一标识                        │   │
│   │   │ customer_id │                                       │   │
│   │   │ status      │                                       │   │
│   │   │ total       │                                       │   │
│   │   └──────┬──────┘                                       │   │
│   │          │                                              │   │
│   │          │ 包含 (通过引用或内嵌)                         │   │
│   │          ▼                                              │   │
│   │   ┌─────────────────┐  ┌─────────────────┐             │   │
│   │   │   OrderItem     │  │   ShippingInfo  │             │   │
│   │   │   (实体)         │  │   (值对象)       │             │   │
│   │   ├─────────────────┤  ├─────────────────┤             │   │
│   │   │ item_id (局部)  │  │ address         │             │   │
│   │   │ product_id      │  │ method          │             │   │
│   │   │ quantity        │  │ tracking_number │             │   │
│   │   │ price           │  └─────────────────┘             │   │
│   │   └─────────────────┘                                   │   │
│   │                                                         │   │
│   │   事务边界：订单及其项作为一个单元被加载和保存           │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   规则：                                                        │
│   • 外部对象只能通过Order访问OrderItem                          │
│   • OrderItem没有全局ID，只有聚合内局部ID                       │
│   • 删除Order会级联删除所有OrderItem                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

```python
class OrderRepository:
    """仓储 - 聚合的持久化"""
    
    def save(self, order: Order):
        """保存整个聚合"""
        # 保存订单
        self._db.orders.insert({
            'order_id': str(order.order_id),
            'customer_id': order._customer_id,
            'status': order.status.name,
            'total': order._total_amount,
            'created_at': order._created_at
        })
        
        # 保存订单项
        for item in order._items:
            self._db.order_items.insert({
                'order_id': str(order.order_id),
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_price': item.unit_price
            })
    
    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        """加载整个聚合"""
        order_data = self._db.orders.find_one(
            {'order_id': str(order_id)}
        )
        if not order_data:
            return None
        
        # 重建聚合根
        order = Order(order_id, order_data['customer_id'])
        
        # 加载订单项
        items_data = self._db.order_items.find(
            {'order_id': str(order_id)}
        )
        for item_data in items_data:
            order.add_item(
                item_data['product_id'],
                item_data['quantity'],
                item_data['unit_price']
            )
        
        return order
```

### 4. 领域事件 (Domain Event)

**领域事件**表示领域中发生的有意义的业务事件，用于在限界上下文间传递信息。

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import uuid4

@dataclass(frozen=True)
class DomainEvent:
    """领域事件基类"""
    event_id: str
    occurred_on: datetime
    aggregate_id: str

@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    """订单已创建事件"""
    customer_id: str
    total_amount: float

@dataclass(frozen=True)
class OrderConfirmed(DomainEvent):
    """订单已确认事件"""
    confirmed_at: datetime

@dataclass(frozen=True)
class OrderShipped(DomainEvent):
    """订单已发货事件"""
    tracking_number: str
    shipped_at: datetime

class EventPublisher:
    """事件发布器"""
    def __init__(self):
        self._subscribers: List[callable] = []
    
    def subscribe(self, handler: callable):
        self._subscribers.append(handler)
    
    def publish(self, event: DomainEvent):
        for handler in self._subscribers:
            handler(event)

class Order:
    """支持领域事件的订单实体"""
    def __init__(self, order_id: OrderId, customer_id: str):
        self._order_id = order_id
        self._customer_id = customer_id
        self._status = OrderStatus.CREATED
        self._events: List[DomainEvent] = []
        
        # 记录领域事件
        self._add_event(OrderCreated(
            event_id=str(uuid4()),
            occurred_on=datetime.now(),
            aggregate_id=str(order_id),
            customer_id=customer_id,
            total_amount=0.0
        ))
    
    def _add_event(self, event: DomainEvent):
        self._events.append(event)
    
    def clear_events(self):
        """清空已发布的事件"""
        self._events.clear()
    
    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._events.copy()
```

### 5. 仓储 (Repository)

**仓储**是聚合的持久化抽象，隔离领域模型与数据访问细节。

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class OrderRepository(ABC):
    """仓储接口"""
    
    @abstractmethod
    def save(self, order: Order) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        pass
    
    @abstractmethod
    def find_by_customer(self, customer_id: str) -> List[Order]:
        pass
    
    @abstractmethod
    def delete(self, order_id: OrderId) -> None:
        pass

class InMemoryOrderRepository(OrderRepository):
    """内存仓储 - 测试用"""
    def __init__(self):
        self._orders: dict = {}
    
    def save(self, order: Order) -> None:
        self._orders[order.order_id] = order
    
    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        return self._orders.get(order_id)
    
    def find_by_customer(self, customer_id: str) -> List[Order]:
        return [o for o in self._orders.values() 
                if o._customer_id == customer_id]
    
    def delete(self, order_id: OrderId) -> None:
        del self._orders[order_id]
```

### 6. 领域服务 (Domain Service)

**领域服务**封装跨实体或值对象的业务逻辑，当逻辑不属于任何一个实体时，使用领域服务。

```python
class PricingService:
    """定价服务 - 领域服务"""
    
    def calculate_order_total(
        self, 
        items: List[OrderItem],
        customer: Customer,
        promotion: Optional[Promotion] = None
    ) -> Money:
        """计算订单总价（包含折扣逻辑）"""
        subtotal = sum(
            Money(item.subtotal, "CNY") 
            for item in items
        )
        
        # 会员折扣
        if customer.is_vip:
            subtotal = subtotal.multiply(0.95)
        
        # 促销折扣
        if promotion and promotion.is_valid():
            subtotal = promotion.apply(subtotal)
        
        return subtotal

class TransferService:
    """转账服务 - 领域服务"""
    
    def transfer(
        self,
        from_account: Account,
        to_account: Account,
        amount: Money
    ) -> None:
        """跨聚合的业务操作"""
        if from_account.balance < amount:
            raise DomainError("Insufficient balance")
        
        from_account.debit(amount)
        to_account.credit(amount)
```

---

## 分层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    DDD分层架构                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                 用户界面层 (UI Layer)                    │   │
│   │              Controllers / Views / API                  │   │
│   │                   ↓ 调用应用层                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                 应用层 (Application Layer)               │   │
│   │     Services / DTOs / Use Cases / Event Handlers        │   │
│   │     • 编排用例，协调领域对象                              │   │
│   │     • 事务管理                                          │   │
│   │     • 发布领域事件                                      │   │
│   │                   ↓ 调用领域层                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  领域层 (Domain Layer)                   │   │
│   │     Entities / Value Objects / Aggregates / Services    │   │
│   │     • 核心业务逻辑                                      │   │
│   │     • 不依赖其他层                                      │   │
│   │     • 最纯净、最重要的层                                │   │
│   │                   ↓ 通过仓储接口                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              基础设施层 (Infrastructure Layer)           │   │
│   │   Repository Impl / Message Queue / DB / External API   │   │
│   │   • 实现领域层定义的接口                                │   │
│   │   • 具体技术实现                                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   依赖方向：上层 → 下层（依赖倒置：领域层定义接口，基础设施实现）│   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## DDD实施步骤

```
1. 事件风暴 (Event Storming)
   └─ 识别领域事件、命令、聚合

2. 划分限界上下文
   └─ 确定边界、关系映射

3. 建立统一语言
   └─ 术语表、业务规则文档

4. 战术设计
   └─ 识别实体、值对象、聚合

5. 架构实现
   └─ 分层架构、依赖注入

6. 持续演进
   └─ 模型精炼、上下文调整
```

---

## 面试要点

**Q1: DDD和传统MVC/三层架构的区别？**> DDD的核心是领域模型，以业务为中心；MVC以数据为中心。DDD强调统一语言和领域专家协作，使用战术设计模式（实体、值对象、聚合等）表达业务概念。DDD适合复杂业务，简单CRUD用传统架构即可。

**Q2: 聚合的设计原则是什么？**> 聚合是事务边界，设计原则：1) 聚合根是外部访问的唯一入口；2) 聚合内保持强一致性，聚合间最终一致；3) 小聚合优先，避免大事务；4) 通过ID引用其他聚合，不直接持有引用。

**Q3: 贫血模型和充血模型的区别？**> 贫血模型只有getter/setter，业务逻辑在服务层；充血模型将业务逻辑封装在领域对象内。DDD推荐充血模型，更符合面向对象设计，业务意图更清晰。

**Q4: 什么时候使用领域服务？**> 当业务逻辑：1) 跨越多个实体；2) 不属于任何一个实体；3) 涉及外部系统交互（防腐层）。领域服务是无状态的，协调领域对象完成业务操作。

---

## 相关概念

- [面向对象设计](./oop-design.md) - DDD的面向对象基础
- [设计模式](./design-patterns.md) - DDD中使用的具体模式
- [架构模式](./architecture-patterns.md) - DDD与系统架构
- [约定](../computer-science/data-structures/convention.md) - 领域内的约定与规范
- [设计模式](./design-patterns.md) - DDD中使用的具体模式
- [架构模式](./architecture-patterns.md) - DDD与系统架构

---

## 参考资料

1. "Domain-Driven Design: Tackling Complexity in the Heart of Software" by Eric Evans
2. "Implementing Domain-Driven Design" by Vaughn Vernon
3. DDD China: https://ddd-china.com/
4. Martin Fowler's DDD articles: https://martinfowler.com/tags/domain%20driven%20design.html
