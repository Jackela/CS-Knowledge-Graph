# 仓库模式 (Repository Pattern)

## 简介

仓库模式（Repository Pattern）是领域驱动设计（DDD）中的一个重要战术模式，它为聚合的持久化提供了抽象接口。仓库充当了领域层与数据映射层之间的中介，使领域模型与数据存储技术解耦。

通过仓库模式，领域层可以使用面向对象的方式操作聚合，而无需关心底层数据存储的具体实现细节（如关系型数据库、NoSQL、内存存储等）。

## 核心概念

### 仓库的职责

仓库主要负责以下操作：
- **保存聚合**：将聚合的当前状态持久化到存储
- **查询聚合**：根据标识符或查询条件检索聚合
- **删除聚合**：从存储中移除聚合
- **管理生命周期**：处理聚合的创建、更新和销毁

### 仓库 vs DAO vs ORM

| 模式 | 抽象层次 | 粒度 | 用途 |
|-----|---------|-----|-----|
| **Repository** | 领域层 | 聚合 | 业务概念操作 |
| **DAO** | 数据层 | 表/记录 | 数据库操作 |
| **ORM** | 映射层 | 对象 | 对象-关系映射 |

### 设计原则

1. **面向聚合**：每个聚合对应一个仓库
2. **领域语义**：方法名使用领域语言而非技术术语
3. **延迟加载**：合理处理聚合内部对象的加载策略
4. **规格模式**：复杂查询使用规格（Specification）模式

## 实现方式

### 基础仓库接口

```python
from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar, Generic

T = TypeVar('T')
ID = TypeVar('ID')

class Repository(ABC, Generic[T, ID]):
    """泛型仓库接口"""
    
    @abstractmethod
    def save(self, entity: T) -> None:
        """保存实体"""
        pass
    
    @abstractmethod
    def find_by_id(self, id: ID) -> Optional[T]:
        """根据ID查找"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[T]:
        """查找所有"""
        pass
    
    @abstractmethod
    def delete(self, id: ID) -> None:
        """删除"""
        pass
    
    @abstractmethod
    def exists(self, id: ID) -> bool:
        """检查是否存在"""
        pass
```

### 具体仓库实现

```python
from typing import Dict

class OrderRepository(Repository[Order, str]):
    """订单仓库抽象接口"""
    
    @abstractmethod
    def find_by_customer(self, customer_id: str) -> List[Order]:
        """查找客户的所有订单"""
        pass
    
    @abstractmethod
    def find_by_status(self, status: OrderStatus) -> List[Order]:
        """按状态查找订单"""
        pass
    
    @abstractmethod
    def find_recent_orders(self, days: int = 30) -> List[Order]:
        """查找最近N天的订单"""
        pass

class InMemoryOrderRepository(OrderRepository):
    """内存实现 - 用于测试"""
    
    def __init__(self):
        self._orders: Dict[str, Order] = {}
    
    def save(self, order: Order) -> None:
        """保存订单聚合"""
        self._orders[order.order_id] = order
    
    def find_by_id(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)
    
    def find_all(self) -> List[Order]:
        return list(self._orders.values())
    
    def delete(self, order_id: str) -> None:
        if order_id in self._orders:
            del self._orders[order_id]
    
    def exists(self, order_id: str) -> bool:
        return order_id in self._orders
    
    def find_by_customer(self, customer_id: str) -> List[Order]:
        return [
            order for order in self._orders.values()
            if order.customer_id == customer_id
        ]
    
    def find_by_status(self, status: OrderStatus) -> List[Order]:
        return [
            order for order in self._orders.values()
            if order.status == status
        ]
    
    def find_recent_orders(self, days: int = 30) -> List[Order]:
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        return [
            order for order in self._orders.values()
            if order.created_at >= cutoff
        ]

class SQLOrderRepository(OrderRepository):
    """SQL实现 - 生产环境使用"""
    
    def __init__(self, db_session):
        self._session = db_session
    
    def save(self, order: Order) -> None:
        """保存订单（包含订单项）"""
        # 使用ORM或原始SQL保存整个聚合
        order_data = {
            'order_id': order.order_id,
            'customer_id': order.customer_id,
            'status': order.status,
            'total_amount': float(order.total_amount),
            'created_at': order.created_at,
            'items': [
                {
                    'product_id': item.product_id,
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price)
                }
                for item in order.items
            ]
        }
        
        # 事务中保存订单和订单项
        with self._session.begin():
            self._session.execute(
                """
                INSERT INTO orders (order_id, customer_id, status, total_amount, created_at)
                VALUES (:order_id, :customer_id, :status, :total_amount, :created_at)
                ON DUPLICATE KEY UPDATE
                status = :status, total_amount = :total_amount
                """,
                order_data
            )
            
            # 删除旧订单项
            self._session.execute(
                "DELETE FROM order_items WHERE order_id = :order_id",
                {'order_id': order.order_id}
            )
            
            # 插入新订单项
            for item in order_data['items']:
                item['order_id'] = order.order_id
                self._session.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price)
                    VALUES (:order_id, :product_id, :product_name, :quantity, :unit_price)
                    """,
                    item
                )
    
    def find_by_id(self, order_id: str) -> Optional[Order]:
        """通过ID加载完整聚合"""
        # 查询订单主表
        order_row = self._session.execute(
            "SELECT * FROM orders WHERE order_id = :order_id",
            {'order_id': order_id}
        ).fetchone()
        
        if not order_row:
            return None
        
        # 查询订单项
        item_rows = self._session.execute(
            "SELECT * FROM order_items WHERE order_id = :order_id",
            {'order_id': order_id}
        ).fetchall()
        
        # 重建聚合
        order = Order(order_row['order_id'], order_row['customer_id'])
        order._status = order_row['status']
        order._total_amount = Decimal(str(order_row['total_amount']))
        order._created_at = order_row['created_at']
        
        for item_row in item_rows:
            order._items.append(OrderItem(
                product_id=item_row['product_id'],
                product_name=item_row['product_name'],
                quantity=item_row['quantity'],
                unit_price=Decimal(str(item_row['unit_price']))
            ))
        
        return order
```

### 规格模式（Specification）

```python
from abc import ABC, abstractmethod

class Specification(ABC):
    """规格抽象基类"""
    
    @abstractmethod
    def is_satisfied_by(self, candidate) -> bool:
        pass
    
    def and_(self, other: 'Specification') -> 'Specification':
        return AndSpecification(self, other)
    
    def or_(self, other: 'Specification') -> 'Specification':
        return OrSpecification(self, other)
    
    def not_(self) -> 'Specification':
        return NotSpecification(self)

class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self._left = left
        self._right = right
    
    def is_satisfied_by(self, candidate) -> bool:
        return (self._left.is_satisfied_by(candidate) and 
                self._right.is_satisfied_by(candidate))

class HighValueOrderSpecification(Specification):
    """高价值订单规格"""
    def __init__(self, threshold: Decimal = Decimal('1000')):
        self._threshold = threshold
    
    def is_satisfied_by(self, order: Order) -> bool:
        return order.total_amount >= self._threshold

class RecentOrderSpecification(Specification):
    """近期订单规格"""
    def __init__(self, days: int = 30):
        self._days = days
    
    def is_satisfied_by(self, order: Order) -> bool:
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=self._days)
        return order.created_at >= cutoff

class OrderRepositoryWithSpec(OrderRepository):
    """支持规格的仓库"""
    
    def find_by_specification(self, spec: Specification) -> List[Order]:
        """根据规格查找订单"""
        return [
            order for order in self.find_all()
            if spec.is_satisfied_by(order)
        ]

# 使用示例
repo = OrderRepositoryWithSpec()
high_value_recent = (
    HighValueOrderSpecification(Decimal('500'))
    .and_(RecentOrderSpecification(7))
)
orders = repo.find_by_specification(high_value_recent)
```

## 示例

### 完整订单仓库实现

```python
class OrderRepositoryImpl(OrderRepository):
    """完整的订单仓库实现"""
    
    def __init__(self, db_session, event_bus):
        self._session = db_session
        self._event_bus = event_bus
    
    def save(self, order: Order) -> None:
        """保存订单并发布领域事件"""
        is_new = not self.exists(order.order_id)
        
        # 持久化到数据库
        self._persist_order(order)
        
        # 发布领域事件
        events = order.get_domain_events()
        for event in events:
            self._event_bus.publish(event)
        order.clear_domain_events()
    
    def find_by_id(self, order_id: str) -> Optional[Order]:
        """通过ID查找订单"""
        return self._load_order(order_id)
    
    def find_by_customer(self, customer_id: str, 
                          limit: int = 100) -> List[Order]:
        """查找客户的订单历史"""
        rows = self._session.execute(
            """
            SELECT order_id FROM orders 
            WHERE customer_id = :customer_id
            ORDER BY created_at DESC
            LIMIT :limit
            """,
            {'customer_id': customer_id, 'limit': limit}
        ).fetchall()
        
        return [self._load_order(row['order_id']) for row in rows]
    
    def find_pending_orders(self) -> List[Order]:
        """查找待处理订单（用于批量作业）"""
        rows = self._session.execute(
            """
            SELECT order_id FROM orders 
            WHERE status IN ('submitted', 'paid')
            ORDER BY created_at ASC
            """
        ).fetchall()
        
        return [self._load_order(row['order_id']) for row in rows]
    
    def delete(self, order_id: str) -> None:
        """删除订单"""
        with self._session.begin():
            # 先删除订单项（外键约束）
            self._session.execute(
                "DELETE FROM order_items WHERE order_id = :order_id",
                {'order_id': order_id}
            )
            # 再删除订单
            self._session.execute(
                "DELETE FROM orders WHERE order_id = :order_id",
                {'order_id': order_id}
            )
    
    def _persist_order(self, order: Order) -> None:
        """持久化订单内部方法"""
        # 具体实现...
        pass
    
    def _load_order(self, order_id: str) -> Optional[Order]:
        """加载订单内部方法"""
        # 具体实现...
        pass

# 应用服务使用仓库
class OrderApplicationService:
    def __init__(self, order_repo: OrderRepository):
        self._order_repo = order_repo
    
    def get_order_details(self, order_id: str) -> OrderDTO:
        """获取订单详情"""
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundException(f"Order {order_id} not found")
        
        return OrderDTO.from_order(order)
    
    def cancel_order(self, order_id: str, reason: str) -> None:
        """取消订单"""
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise OrderNotFoundException(f"Order {order_id} not found")
        
        order.cancel(reason)
        self._order_repo.save(order)
```

## 应用场景

### 何时使用仓库模式

1. **聚合持久化**：需要将聚合保存到数据存储
2. **测试支持**：需要内存实现进行单元测试
3. **存储切换**：可能需要更换底层存储技术
4. **查询抽象**：复杂查询逻辑需要封装

### 仓库 vs 直接数据库访问

| 场景 | 推荐方式 | 原因 |
|-----|---------|-----|
| 简单CRUD | 仓库 | 保持一致性 |
| 复杂报表 | 直接SQL | 性能优化 |
| 领域操作 | 仓库 | 维护业务完整性 |
| 批量处理 | 专用服务 | 避免加载整个聚合 |

## 面试要点

**Q: 仓库模式和DAO模式有什么区别？**
A: 主要区别在于：
- **抽象层次**：仓库面向领域模型（聚合），DAO面向数据库表
- **方法语义**：仓库使用方法名表达业务意图（findPendingOrders），DAO使用技术操作（selectByStatus）
- **事务边界**：仓库通常管理聚合的事务边界，DAO只管理单表操作

**Q: 一个聚合是否可以有多个仓库？**
A: 不，一个聚合应该只有一个仓库。聚合是持久化的基本单元，多个仓库会导致职责不清和数据一致性问题。

**Q: 如何处理跨聚合的查询？**
A: 推荐做法：
- 使用领域服务协调多个仓库
- 对于复杂查询，可以使用专门的查询服务（CQRS）
- 避免直接跨聚合引用，通过ID关联

**Q: 仓库应该返回实体还是DTO？**
A: 仓库返回完整的聚合实体，因为领域逻辑需要操作实体。DTO转换应在应用服务层完成。

## 相关概念

### 数据结构
- [哈希表](../computer-science/data-structures/hash-table.md) - 仓库的索引实现

### 算法
- [二分查找](../computer-science/algorithms/binary-search.md) - 有序数据查询优化

### 复杂度分析
- [空间复杂度](../computer-science/algorithms/space-complexity.md) - 仓库缓存策略

### 系统实现
- [聚合](./aggregates.md) - 仓库管理的基本单元
- [领域服务](./domain-services.md) - 跨聚合操作协调
- [CQRS](../architecture-patterns/cqrs.md) - 读写分离架构
- [事务管理](../system-design/transaction-management.md) - 聚合持久化的事务策略
