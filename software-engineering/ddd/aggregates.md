# 聚合 (Aggregates)

## 简介

聚合（Aggregate）是领域驱动设计（DDD）中的一个核心战术模式，它定义了一组相关对象的集合，这些对象被视为一个单一的单元。聚合通过定义清晰的边界来维护领域模型的一致性，并确保业务规则在对象组级别得到遵守。

聚合根（Aggregate Root）是聚合的入口点，外部对象只能通过聚合根来访问聚合内部的实体。这种设计模式有效地封装了业务逻辑的复杂性，并提供了事务一致性的边界。

## 核心概念

### 聚合的结构

一个聚合通常包含以下元素：
- **聚合根（Aggregate Root）**：聚合的唯一外部访问点，具有全局唯一标识符
- **实体（Entities）**：具有唯一标识的对象，生命周期由聚合根管理
- **值对象（Value Objects）**：通过属性值定义的对象，无独立标识
- **领域事件（Domain Events）**：聚合状态变更时触发的事件

### 聚合的设计原则

1. **事务边界**：一个聚合对应一个事务边界，保证ACID特性
2. **最小化设计**：聚合应尽可能小，只包含真正需要一致性的对象
3. **通过根访问**：外部只能通过聚合根访问聚合内部对象
4. **不变量保护**：聚合负责维护其内部的不变量（业务规则）

### 聚合 vs 其他概念

| 概念 | 关系 | 区别 |
|-----|------|------|
| 实体 | 包含 | 实体是聚合的组成部分 |
| 值对象 | 包含 | 值对象可以属于聚合 |
| 限界上下文 | 边界 | 聚合是限界上下文内的逻辑分组 |

## 实现方式

### 基本聚合实现

```python
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class OrderItem:
    """订单项 - 值对象"""
    def __init__(self, product_id: str, product_name: str, 
                 quantity: int, unit_price: Decimal):
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price
    
    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity

class Order:
    """订单 - 聚合根"""
    def __init__(self, order_id: str, customer_id: str):
        self._order_id = order_id
        self._customer_id = customer_id
        self._items: List[OrderItem] = []
        self._status = OrderStatus.CREATED
        self._created_at = datetime.now()
        self._total_amount = Decimal('0')
        self._domain_events: List[DomainEvent] = []
    
    @property
    def order_id(self) -> str:
        return self._order_id
    
    @property
    def total_amount(self) -> Decimal:
        return self._total_amount
    
    @property
    def status(self) -> OrderStatus:
        return self._status
    
    def add_item(self, product_id: str, product_name: str,
                 quantity: int, unit_price: Decimal):
        """添加订单项 - 聚合根的公共方法"""
        # 业务规则验证
        if self._status != OrderStatus.CREATED:
            raise InvalidOrderOperation("Cannot modify submitted order")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # 创建值对象
        item = OrderItem(product_id, product_name, quantity, unit_price)
        self._items.append(item)
        
        # 更新聚合状态
        self._recalculate_total()
    
    def remove_item(self, product_id: str):
        """移除订单项"""
        if self._status != OrderStatus.CREATED:
            raise InvalidOrderOperation("Cannot modify submitted order")
        
        self._items = [item for item in self._items 
                       if item.product_id != product_id]
        self._recalculate_total()
    
    def submit(self):
        """提交订单"""
        if not self._items:
            raise InvalidOrderOperation("Cannot submit empty order")
        
        self._status = OrderStatus.SUBMITTED
        
        # 发布领域事件
        self._domain_events.append(OrderSubmittedEvent(
            order_id=self._order_id,
            customer_id=self._customer_id,
            total_amount=self._total_amount
        ))
    
    def _recalculate_total(self):
        """重新计算订单总额 - 内部方法"""
        self._total_amount = sum(
            item.subtotal for item in self._items
        )
    
    def get_domain_events(self) -> List[DomainEvent]:
        """获取待处理的领域事件"""
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """清除已处理的领域事件"""
        self._domain_events.clear()

class OrderStatus:
    CREATED = "created"
    SUBMITTED = "submitted"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DomainEvent:
    pass

class OrderSubmittedEvent(DomainEvent):
    def __init__(self, order_id: str, customer_id: str, 
                 total_amount: Decimal):
        self.order_id = order_id
        self.customer_id = customer_id
        self.total_amount = total_amount

class InvalidOrderOperation(Exception):
    pass
```

### 仓储模式配合

```python
from abc import ABC, abstractmethod
from typing import Optional

class OrderRepository(ABC):
    """订单仓储接口"""
    
    @abstractmethod
    def save(self, order: Order) -> None:
        """保存聚合"""
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        """通过ID查找聚合"""
        pass
    
    @abstractmethod
    def find_by_customer(self, customer_id: str) -> List[Order]:
        """查找客户的所有订单"""
        pass

class InMemoryOrderRepository(OrderRepository):
    """内存实现 - 用于测试"""
    def __init__(self):
        self._orders: Dict[str, Order] = {}
    
    def save(self, order: Order) -> None:
        """保存整个聚合"""
        self._orders[order.order_id] = order
    
    def find_by_id(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)
    
    def find_by_customer(self, customer_id: str) -> List[Order]:
        return [o for o in self._orders.values() 
                if o._customer_id == customer_id]

# 应用服务
class OrderApplicationService:
    """订单应用服务"""
    def __init__(self, order_repo: OrderRepository, 
                 event_bus: EventBus):
        self.order_repo = order_repo
        self.event_bus = event_bus
    
    def create_order(self, customer_id: str, 
                     items: List[dict]) -> str:
        """创建订单"""
        order_id = generate_order_id()
        order = Order(order_id, customer_id)
        
        for item in items:
            order.add_item(
                item['product_id'],
                item['product_name'],
                item['quantity'],
                Decimal(item['unit_price'])
            )
        
        order.submit()
        self.order_repo.save(order)
        
        # 发布领域事件
        for event in order.get_domain_events():
            self.event_bus.publish(event)
        order.clear_domain_events()
        
        return order_id
```

## 示例

### 复杂聚合：购物车

```python
class ShoppingCart:
    """购物车聚合"""
    MAX_ITEMS = 50
    MAX_QUANTITY_PER_ITEM = 20
    
    def __init__(self, cart_id: str, customer_id: str):
        self._cart_id = cart_id
        self._customer_id = customer_id
        self._items: Dict[str, CartItem] = {}
        self._created_at = datetime.now()
        self._last_modified = datetime.now()
        self._version = 0  # 乐观锁版本号
    
    def add_product(self, product_id: str, product_name: str,
                    quantity: int, unit_price: Decimal):
        """添加商品到购物车"""
        # 验证购物车容量
        if len(self._items) >= self.MAX_ITEMS:
            raise CartFullException("Shopping cart is full")
        
        # 验证单品数量
        current_qty = self._items[product_id].quantity \
            if product_id in self._items else 0
        if current_qty + quantity > self.MAX_QUANTITY_PER_ITEM:
            raise QuantityLimitExceeded(
                f"Cannot add more than {self.MAX_QUANTITY_PER_ITEM} "
                f"of the same product"
            )
        
        if product_id in self._items:
            # 更新现有项
            self._items[product_id].increase_quantity(quantity)
        else:
            # 添加新项
            self._items[product_id] = CartItem(
                product_id, product_name, quantity, unit_price
            )
        
        self._update_modified()
    
    def remove_product(self, product_id: str):
        """从购物车移除商品"""
        if product_id in self._items:
            del self._items[product_id]
            self._update_modified()
    
    def change_quantity(self, product_id: str, new_quantity: int):
        """修改商品数量"""
        if product_id not in self._items:
            raise ProductNotInCart("Product not in cart")
        
        if new_quantity <= 0:
            self.remove_product(product_id)
        elif new_quantity > self.MAX_QUANTITY_PER_ITEM:
            raise QuantityLimitExceeded("Quantity exceeds limit")
        else:
            self._items[product_id].set_quantity(new_quantity)
            self._update_modified()
    
    def clear(self):
        """清空购物车"""
        self._items.clear()
        self._update_modified()
    
    def calculate_total(self) -> Decimal:
        """计算购物车总价"""
        return sum(
            item.subtotal for item in self._items.values()
        )
    
    def to_order_items(self) -> List[OrderItem]:
        """转换为订单项"""
        return [
            OrderItem(
                item.product_id,
                item.product_name,
                item.quantity,
                item.unit_price
            )
            for item in self._items.values()
        ]
    
    def _update_modified(self):
        """更新修改时间"""
        self._last_modified = datetime.now()
        self._version += 1

class CartItem:
    """购物车项 - 值对象"""
    def __init__(self, product_id: str, product_name: str,
                 quantity: int, unit_price: Decimal):
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.unit_price = unit_price
    
    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity
    
    def increase_quantity(self, amount: int):
        self.quantity += amount
    
    def set_quantity(self, new_quantity: int):
        self.quantity = new_quantity
```

## 应用场景

### 适合使用聚合的场景

1. **强一致性要求**：一组对象必须同时满足某些业务规则
2. **事务边界**：需要原子性更新的对象组
3. **复杂业务规则**：涉及多个对象的复杂验证逻辑
4. **领域事件触发**：状态变更需要触发领域事件

### 聚合设计误区

| 误区 | 正确做法 |
|-----|---------|
| 聚合过大 | 按事务边界拆分，避免大聚合 |
| 绕过根访问 | 所有访问必须通过聚合根 |
| 忽视性能 | 考虑加载整个聚合的成本 |
| 跨聚合引用 | 使用ID引用其他聚合，而非对象引用 |

## 面试要点

**Q: 为什么需要通过聚合根访问聚合内部对象？**
A: 聚合根作为唯一的访问入口，确保：
- 业务不变量得到保护
- 封装性不被破坏
- 事务边界清晰
- 领域规则集中管理

**Q: 如何判断两个实体是否属于同一个聚合？**
A: 关键判断标准：
- 它们是否需要在同一个事务中更新
- 一个实体的删除是否要求另一个实体同时删除
- 它们是否共享某些业务不变量

**Q: 聚合和微服务的关系是什么？**
A: 通常一个微服务包含一个或多个聚合，但一个聚合不应跨越多个微服务。聚合是微服务内部的组织单元，微服务是部署边界。

**Q: 如何处理聚合间的引用？**
A: 推荐做法：
- 使用ID而非对象引用
- 通过领域事件实现最终一致性
- 必要时使用领域服务协调多个聚合

## 相关概念

### 数据结构
- [树](../computer-science/data-structures/tree.md) - 聚合的层次结构

### 算法
- [深度优先搜索](../computer-science/algorithms/dfs.md) - 遍历聚合结构

### 复杂度分析
- [事务复杂度](../system-design/transaction-complexity.md) - 聚合事务边界分析

### 系统实现
- [实体与值对象](./entities-value-objects.md) - 聚合的组成部分
- [仓储模式](./repositories.md) - 聚合的持久化
- [领域事件](./domain-events.md) - 聚合状态变更通知
- [领域服务](./domain-services.md) - 跨聚合业务逻辑
