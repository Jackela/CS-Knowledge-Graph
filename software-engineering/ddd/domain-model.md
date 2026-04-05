# 领域模型 (Domain Model)

## 简介

领域模型（Domain Model）是领域驱动设计（Domain-Driven Design, DDD）的核心概念，它是对业务领域的抽象表示， encapsulates了业务知识、规则和逻辑。领域模型不仅仅是数据结构的集合，更是对业务行为和业务规则的精确描述。

领域模型的主要目标是：
- 建立开发团队与业务专家之间的通用语言（Ubiquitous Language）
- 将复杂的业务逻辑从基础设施代码中分离出来
- 提供对业务领域的精确、可维护的表示
- 支持业务规则的有效实现和演化

一个良好的领域模型应该具备以下特征：
1. **业务驱动**：由业务需求驱动，而非技术实现驱动
2. **语义丰富**：包含业务概念、行为和规则
3. **高内聚低耦合**：相关概念组织在一起，无关概念分离
4. **可测试性**：业务逻辑可以独立于基础设施进行测试
5. **可演化性**：能够适应业务需求的变化

## 核心概念

### 1. 领域（Domain）

领域是指软件系统所要解决的业务问题空间。例如：
- 电子商务系统中的订单、商品、支付等业务
- 银行系统中的账户、转账、贷款等业务
- 物流系统中的配送、仓储、运输等业务

### 2. 子域（Subdomain）

复杂的领域通常划分为多个子域：

- **核心域（Core Domain）**：业务的差异化竞争优势所在，包含最核心的业务逻辑
- **支撑子域（Supporting Subdomain）**：支持核心域的业务功能，但不提供竞争优势
- **通用子域（Generic Subdomain）**：行业通用的功能，如用户认证、通知服务等

### 3. 通用语言（Ubiquitous Language）

通用语言是领域模型的重要组成部分：
- 开发团队与业务专家使用相同的术语
- 术语在代码、文档、对话中保持一致
- 消除技术术语与业务术语之间的鸿沟
- 每个术语都有明确的业务含义

### 4. 领域模型的组成要素

领域模型由以下要素构成：

| 要素 | 英文名称 | 描述 |
|------|----------|------|
| 实体 | [Entity](./entities-value-objects.md) | 具有唯一标识的对象 |
| 值对象 | [Value Object](./entities-value-objects.md) | 通过属性定义的对象 |
| 聚合 | [Aggregate](./aggregates.md) | 一组相关对象的集合 |
| 领域服务 | Domain Service | 不适合放入实体或值对象的业务逻辑 |
| 仓库 | [Repository](./repositories.md) | 聚合的持久化抽象 |
| 工厂 | Factory | 复杂对象的创建逻辑 |

### 5. 分层架构

领域模型通常位于分层架构的领域层（Domain Layer）：

```
┌─────────────────────────────────────────┐
│           用户界面层 (UI Layer)           │
│         - 控制器、视图、DTO              │
├─────────────────────────────────────────┤
│           应用层 (Application Layer)      │
│      - 应用服务、用例协调、事务控制        │
├─────────────────────────────────────────┤
│           领域层 (Domain Layer)           │
│  - 实体、值对象、聚合、领域服务、领域事件   │
├─────────────────────────────────────────┤
│          基础设施层 (Infrastructure Layer) │
│       - 数据库、消息队列、外部服务         │
└─────────────────────────────────────────┘
```

## 实现方式

### 1. 贫血模型 vs 充血模型

**贫血模型（Anemic Domain Model）**：
```python
# 贫血模型 - 只有数据，没有行为
class Order:
    def __init__(self, order_id, customer_id, items, status):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items
        self.status = status

# 业务逻辑在服务中
class OrderService:
    def calculate_total(self, order):
        return sum(item.price * item.quantity for item in order.items)
    
    def can_cancel(self, order):
        return order.status in ['PENDING', 'CONFIRMED']
```

**充血模型（Rich Domain Model）**：
```python
# 充血模型 - 数据与行为封装在一起
class Order:
    def __init__(self, order_id: str, customer_id: str):
        self._order_id = order_id
        self._customer_id = customer_id
        self._items = []
        self._status = OrderStatus.PENDING
        self._created_at = datetime.now()
    
    @property
    def total_amount(self) -> Decimal:
        """计算订单总金额"""
        return sum(
            item.subtotal for item in self._items
        )
    
    def add_item(self, product_id: str, name: str, 
                 price: Decimal, quantity: int) -> None:
        """添加订单项"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self._status != OrderStatus.PENDING:
            raise ValueError("Can only modify pending orders")
        
        item = OrderItem(product_id, name, price, quantity)
        self._items.append(item)
    
    def confirm(self) -> None:
        """确认订单"""
        if not self._items:
            raise ValueError("Cannot confirm empty order")
        if self._status != OrderStatus.PENDING:
            raise ValueError("Can only confirm pending orders")
        
        self._status = OrderStatus.CONFIRMED
        self._confirmed_at = datetime.now()
    
    def cancel(self, reason: str) -> None:
        """取消订单"""
        if self._status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise ValueError(f"Cannot cancel order in {self._status} status")
        
        self._status = OrderStatus.CANCELLED
        self._cancel_reason = reason
        self._cancelled_at = datetime.now()
```

### 2. 领域模型设计原则

**单一职责原则（SRP）**：
```python
# 不好：一个类承担多个职责
class Product:
    def __init__(self):
        self.name = ""
        self.price = 0
        self.inventory = 0
    
    def calculate_discount(self):  # 定价逻辑
        pass
    
    def update_inventory(self):    # 库存逻辑
        pass
    
    def generate_report(self):     # 报表逻辑
        pass

# 好：分离职责
class Product:
    """产品核心信息"""
    def __init__(self, product_id, name, base_price):
        self.product_id = product_id
        self.name = name
        self.base_price = base_price

class PricingService:
    """定价服务"""
    def calculate_price(self, product, customer):
        pass

class InventoryService:
    """库存服务"""
    def check_availability(self, product, quantity):
        pass
```

**领域不变量（Invariants）**：
```python
class BankAccount:
    """银行账户 - 维护余额不为负的不变量"""
    
    def __init__(self, account_id: str, initial_balance: Decimal):
        self._account_id = account_id
        self._balance = initial_balance
        self._transactions = []
        self._version = 0
    
    def withdraw(self, amount: Decimal) -> None:
        """取款 - 确保余额不会为负"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        new_balance = self._balance - amount
        if new_balance < 0:
            raise InsufficientFundsError(
                f"Insufficient funds: balance={self._balance}, requested={amount}"
            )
        
        self._balance = new_balance
        self._transactions.append(
            Transaction(TransactionType.DEBIT, amount, datetime.now())
        )
        self._version += 1
    
    def deposit(self, amount: Decimal) -> None:
        """存款"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        self._balance += amount
        self._transactions.append(
            Transaction(TransactionType.CREDIT, amount, datetime.now())
        )
        self._version += 1
```

### 3. 领域服务（Domain Service）

当业务逻辑不适合放在任何实体或值对象中时，使用领域服务：

```python
class TransferService:
    """转账服务 - 涉及多个账户的业务逻辑"""
    
    def __init__(self, account_repository):
        self._account_repository = account_repository
    
    def transfer(self, from_account_id: str, to_account_id: str, 
                 amount: Decimal, currency: str) -> TransferResult:
        """执行转账操作"""
        # 加载账户
        from_account = self._account_repository.find_by_id(from_account_id)
        to_account = self._account_repository.find_by_id(to_account_id)
        
        if not from_account or not to_account:
            raise AccountNotFoundError("Account not found")
        
        # 执行转账
        from_account.debit(amount, currency)
        to_account.credit(amount, currency)
        
        # 创建转账记录
        transfer = Transfer(
            transfer_id=generate_uuid(),
            from_account=from_account_id,
            to_account=to_account_id,
            amount=amount,
            currency=currency,
            timestamp=datetime.now()
        )
        
        return TransferResult.success(transfer)
```

### 4. 领域事件（Domain Event）

领域事件用于记录领域中的重要业务事件：

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass(frozen=True)
class DomainEvent:
    """领域事件基类"""
    occurred_on: datetime

@dataclass(frozen=True)
class OrderConfirmedEvent(DomainEvent):
    """订单已确认事件"""
    order_id: str
    customer_id: str
    total_amount: Decimal
    confirmed_at: datetime

class Order:
    def __init__(self, order_id: str, customer_id: str):
        self._order_id = order_id
        self._customer_id = customer_id
        self._status = OrderStatus.PENDING
        self._domain_events: List[DomainEvent] = []
    
    def confirm(self) -> None:
        if self._status != OrderStatus.PENDING:
            raise InvalidOrderStateError()
        
        self._status = OrderStatus.CONFIRMED
        
        # 发布领域事件
        event = OrderConfirmedEvent(
            occurred_on=datetime.now(),
            order_id=self._order_id,
            customer_id=self._customer_id,
            total_amount=self.total_amount,
            confirmed_at=datetime.now()
        )
        self._domain_events.append(event)
    
    def pop_events(self) -> List[DomainEvent]:
        """获取并清空领域事件"""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
```

## 示例

### 完整电商订单领域模型

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import List, Optional
from uuid import uuid4

class OrderStatus(Enum):
    PENDING = auto()
    CONFIRMED = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()

@dataclass(frozen=True)
class Address:
    """值对象：地址"""
    province: str
    city: str
    district: str
    street: str
    zip_code: str
    
    def __str__(self) -> str:
        return f"{self.province}{self.city}{self.district}{self.street}"

@dataclass(frozen=True)
class Money:
    """值对象：金额"""
    amount: Decimal
    currency: str
    
    def add(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: int) -> Money:
        return Money(self.amount * factor, self.currency)

@dataclass
class OrderItem:
    """订单项实体"""
    product_id: str
    product_name: str
    unit_price: Money
    quantity: int
    
    @property
    def subtotal(self) -> Money:
        return self.unit_price.multiply(self.quantity)
    
    def validate(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.unit_price.amount < 0:
            raise ValueError("Price cannot be negative")

class Order:
    """订单聚合根"""
    
    def __init__(self, order_id: str, customer_id: str, 
                 shipping_address: Address):
        self._order_id = order_id
        self._customer_id = customer_id
        self._shipping_address = shipping_address
        self._items: List[OrderItem] = []
        self._status = OrderStatus.PENDING
        self._created_at = datetime.now()
        self._events: List[object] = []
    
    @property
    def order_id(self) -> str:
        return self._order_id
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    @property
    def total_amount(self) -> Money:
        """计算订单总金额"""
        if not self._items:
            return Money(Decimal('0'), 'CNY')
        return sum(
            (item.subtotal for item in self._items[1:]),
            self._items[0].subtotal
        )
    
    def add_item(self, product_id: str, product_name: str,
                 unit_price: Money, quantity: int) -> None:
        """添加订单项"""
        self._assert_can_modify()
        
        item = OrderItem(product_id, product_name, unit_price, quantity)
        item.validate()
        self._items.append(item)
    
    def confirm(self) -> None:
        """确认订单"""
        if self._status != OrderStatus.PENDING:
            raise ValueError(f"Cannot confirm order in {self._status} status")
        if not self._items:
            raise ValueError("Cannot confirm empty order")
        
        self._status = OrderStatus.CONFIRMED
        self._confirmed_at = datetime.now()
    
    def ship(self, tracking_number: str) -> None:
        """发货"""
        if self._status != OrderStatus.CONFIRMED:
            raise ValueError(f"Cannot ship order in {self._status} status")
        
        self._status = OrderStatus.SHIPPED
        self._tracking_number = tracking_number
        self._shipped_at = datetime.now()
    
    def cancel(self, reason: str) -> None:
        """取消订单"""
        if self._status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise ValueError(f"Cannot cancel order in {self._status} status")
        
        self._status = OrderStatus.CANCELLED
        self._cancel_reason = reason
        self._cancelled_at = datetime.now()
    
    def _assert_can_modify(self) -> None:
        """断言订单可以修改"""
        if self._status != OrderStatus.PENDING:
            raise ValueError(f"Cannot modify order in {self._status} status")
    
    def get_items(self) -> List[OrderItem]:
        """获取订单项列表（只读副本）"""
        return self._items.copy()


# 使用示例
def create_order_example():
    # 创建订单
    address = Address("广东省", "深圳市", "南山区", "科技园", "518000")
    order = Order(str(uuid4()), "customer_001", address)
    
    # 添加商品
    order.add_item(
        "prod_001", 
        "iPhone 15",
        Money(Decimal("6999.00"), "CNY"),
        1
    )
    order.add_item(
        "prod_002",
        "AirPods Pro",
        Money(Decimal("1999.00"), "CNY"),
        2
    )
    
    # 确认订单
    order.confirm()
    
    print(f"Order total: {order.total_amount.amount}")
    return order
```

## 应用场景

### 1. 复杂业务逻辑系统

领域模型最适合具有复杂业务规则的系统：
- **金融系统**：账户管理、交易处理、风险控制
- **保险系统**：保单管理、理赔处理、精算计算
- **医疗系统**：病历管理、处方处理、预约调度
- **供应链系统**：库存管理、采购计划、物流跟踪

### 2. 业务频繁变化的系统

当业务需求频繁变化时，领域模型提供良好的可维护性：
- 业务规则集中在领域层，修改影响范围可控
- 通用语言确保业务变更能准确映射到代码
- 领域事件支持业务扩展的松耦合

### 3. 需要长期维护的企业级应用

领域模型的投资回报在长期使用中显现：
- 代码结构清晰，新成员易于理解
- 测试覆盖率高，重构风险低
- 业务知识沉淀在代码中，不易丢失

### 4. 不适合使用领域模型的情况

- **简单CRUD应用**：业务逻辑简单，直接使用数据模型即可
- **技术验证原型（POC）**：需要快速验证技术可行性
- **短期一次性项目**：项目生命周期短，DDD的前期投入难以回收

## 面试要点

Q: 什么是领域模型？它与数据模型有什么区别？
A: 领域模型是对业务领域的抽象表示，包含业务概念、行为和规则。它与数据模型的主要区别在于：
   - 领域模型关注业务行为，数据模型关注数据存储
   - 领域模型是充血模型，包含业务方法；数据模型通常是贫血模型，只有数据字段
   - 领域模型使用通用语言，面向业务人员；数据模型面向数据库
   - 领域模型可以包含复杂业务逻辑，数据模型通常只表示关系

Q: 贫血模型和充血模型各有什么优缺点？
A: 贫血模型将业务逻辑放在服务层，优点：
   - 简单直观，易于理解
   - 与数据库表结构对应，ORM映射简单
   缺点：
   - 业务逻辑分散，难以维护
   - 违反面向对象封装原则
   - 容易形成事务脚本模式
   充血模型将数据和行为封装在一起，优点：
   - 高内聚，业务逻辑集中在领域对象
   - 更好的封装性
   - 更易于测试
   缺点：
   - 设计复杂度较高
   - 需要正确处理持久化
   - 团队需要DDD经验

Q: 什么是通用语言（Ubiquitous Language）？为什么重要？
A: 通用语言是DDD中要求开发团队与业务专家使用的统一术语系统。重要性在于：
   - 消除沟通歧义，减少需求理解偏差
   - 代码中的类名、方法名直接反映业务概念
   - 降低知识传递成本
   - 使代码成为文档，新成员可以通过代码理解业务
   - 防止"语言腐败"导致的设计偏离

Q: 领域服务（Domain Service）与应用服务（Application Service）的区别是什么？
A: 领域服务：
   - 包含不适合放在实体/值对象中的业务逻辑
   - 通常是无状态的
   - 操作多个聚合或执行领域级别的计算
   - 属于领域层
   应用服务：
   - 协调用例的执行流程
   - 处理事务、安全、日志等横切关注点
   - 调用领域层完成业务逻辑
   - 属于应用层
   - 通常与用例一一对应

Q: 如何判断一个业务概念应该是实体还是值对象？
A: 判断标准：
   - 实体：有唯一标识，生命周期内标识不变，关注身份而非属性。例如：订单、用户、账户
   - 值对象：无唯一标识，通过属性定义，不可变或替换。例如：地址、金额、日期范围
   如果两个对象属性完全相同但需要区分彼此，是实体；如果属性相同就认为是同一个对象，是值对象。

Q: 领域事件的作用是什么？如何使用？
A: 领域事件用于：
   - 记录领域中的重要业务发生
   - 实现聚合间的松耦合通信
   - 支持事件溯源和CQRS模式
   - 触发跨聚合或跨限界上下文的业务处理
   使用方法：
   - 在领域操作中创建事件对象
   - 存储在聚合内的事件列表
   - 事务提交后发布到事件总线
   - 订阅者异步处理事件

Q: 领域模型的分层架构中各层的职责是什么？
A: 分层架构：
   - 用户界面层：处理用户输入和展示，包含控制器、视图
   - 应用层：编排用例，协调领域对象，控制事务边界
   - 领域层：核心业务逻辑，包含实体、值对象、领域服务
   - 基础设施层：技术实现，数据持久化、消息队列、外部API
   依赖规则：上层依赖下层，领域层不依赖其他层。

## 相关概念

### 数据结构
- [实体与值对象](./entities-value-objects.md) - 领域模型的基本构建块
- [聚合](./aggregates.md) - 对象一致性边界
- [仓库模式](./repositories.md) - 聚合的持久化抽象

### 算法
- 事务管理算法 - 确保领域操作的原子性
- 事件驱动编程模式 - 领域事件的发布与订阅
- 乐观锁机制 - 处理并发更新冲突

### 复杂度分析
- 领域模型的复杂度主要来自业务规则的组合
- 时间复杂度：O(1) 的属性访问，O(n) 的集合操作
- 空间复杂度：取决于领域对象的嵌套深度和集合大小
- 设计复杂度：需要平衡模型的完整性与实现的简洁性

### 系统实现
- [限界上下文](./bounded-context.md) - 领域模型的大型结构
- 领域事件总线 - 实现松耦合的事件通信
- 工作单元模式（Unit of Work）- 维护业务操作的原子性
- CQRS模式 - 分离读写模型以适应不同需求
- 事件溯源（Event Sourcing）- 以事件序列存储领域状态
