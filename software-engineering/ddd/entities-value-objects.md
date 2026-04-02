# 实体与值对象 (Entities and Value Objects)

## 简介

实体（Entity）和值对象（Value Object）是领域驱动设计（Domain-Driven Design, DDD）中描述领域模型的两种基本对象类型。它们区分了领域中"有身份标识的事物"和"仅由属性描述的事物"，是构建丰富领域模型的基础。

理解实体和值对象的区别对于正确建模业务领域至关重要，这直接影响到系统的性能、一致性和可维护性。

## 核心概念

### 实体 (Entity)

**定义**：实体是具有唯一身份标识（Identity）的领域对象，即使其属性发生变化，其身份保持不变。

**核心特征**：
- **身份标识**：拥有唯一的ID，通常在整个生命周期中保持不变
- **可变性**：属性可以随时间变化，但身份不变
- **连续性**：关注对象的生命周期和状态演变
- **相等性判断**：基于身份标识判断相等，而非属性

**常见实体示例**：
- 用户（User）- 用户ID不变，但姓名、邮箱可变更
- 订单（Order）- 订单号固定，但状态、地址可变更
- 商品（Product）- SKU唯一，价格、库存可调整

### 值对象 (Value Object)

**定义**：值对象是通过属性值来定义的领域对象，没有身份标识，不可变，通常用于描述实体的特征。

**核心特征**：
- **无身份标识**：没有唯一ID，完全由属性值定义
- **不可变性**：创建后不可修改，修改即创建新对象
- **可替换性**：属性相同的值对象可以互换使用
- **相等性判断**：基于所有属性值判断相等
- **无副作用**：操作值对象不会影响系统状态

**常见值对象示例**：
- 地址（Address）- 街道、城市、邮编的组合
- 货币金额（Money）- 数值和货币单位的组合
- 日期范围（DateRange）- 开始日期和结束日期
- 颜色（Color）- RGB值或名称

### 实体 vs 值对象对比

| 特性 | 实体 (Entity) | 值对象 (Value Object) |
|------|---------------|----------------------|
| 身份标识 | 有唯一ID | 无ID，由属性定义 |
| 可变性 | 可变 | 不可变（Immutable） |
| 相等性 | 基于ID | 基于所有属性值 |
| 生命周期 | 有完整生命周期 | 无生命周期概念 |
| 存储方式 | 通常独立存储 | 可嵌入实体或序列化存储 |
| 典型用途 | 业务核心对象 | 描述属性、度量、规格 |

## 实现方式

### 实体的实现

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4


class Entity:
    """实体基类"""
    
    def __init__(self, entity_id: Optional[UUID] = None):
        self._id = entity_id or uuid4()
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Entity):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
    
    def _mark_updated(self):
        """标记实体已更新"""
        self._updated_at = datetime.now()


class User(Entity):
    """用户实体"""
    
    def __init__(self, entity_id: Optional[UUID] = None,
                 username: str = "",
                 email: str = "",
                 address: Optional['Address'] = None):
        super().__init__(entity_id)
        self._username = username
        self._email = email
        self._address = address
        self._orders: List['Order'] = []
    
    @property
    def username(self) -> str:
        return self._username
    
    @username.setter
    def username(self, value: str):
        self._username = value
        self._mark_updated()
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, value: str):
        self._email = value
        self._mark_updated()
    
    @property
    def address(self) -> Optional['Address']:
        return self._address
    
    def change_address(self, new_address: 'Address'):
        """更换地址（值对象替换）"""
        self._address = new_address
        self._mark_updated()
    
    def add_order(self, order: 'Order'):
        """添加订单"""
        self._orders.append(order)
        self._mark_updated()


class Order(Entity):
    """订单实体"""
    
    def __init__(self, entity_id: Optional[UUID] = None,
                 user_id: Optional[UUID] = None,
                 items: Optional[List['OrderItem']] = None,
                 shipping_address: Optional['Address'] = None):
        super().__init__(entity_id)
        self._user_id = user_id
        self._items = items or []
        self._shipping_address = shipping_address
        self._status = OrderStatus.PENDING
        self._total_amount = self._calculate_total()
    
    def _calculate_total(self) -> 'Money':
        """计算订单总金额"""
        total = Money(0, "USD")
        for item in self._items:
            total = total.add(item.subtotal)
        return total
    
    def update_status(self, new_status: 'OrderStatus'):
        """更新订单状态"""
        if self._status.can_transition_to(new_status):
            self._status = new_status
            self._mark_updated()


class OrderStatus:
    """订单状态值对象"""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    
    VALID_TRANSITIONS = {
        PENDING: [PAID, CANCELLED],
        PAID: [SHIPPED, CANCELLED],
        SHIPPED: [DELIVERED],
        DELIVERED: [],
        CANCELLED: []
    }
    
    def __init__(self, value: str):
        if value not in [self.PENDING, self.PAID, self.SHIPPED, 
                        self.DELIVERED, self.CANCELLED]:
            raise ValueError(f"Invalid order status: {value}")
        self._value = value
    
    def can_transition_to(self, new_status: 'OrderStatus') -> bool:
        return new_status._value in self.VALID_TRANSITIONS.get(self._value, [])
```

### 值对象的实现

```python
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Address:
    """
    地址值对象
    
    使用 frozen=True 确保不可变性
    """
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "CN"
    
    def __post_init__(self):
        """验证地址数据完整性"""
        if not self.street or not self.city:
            raise ValueError("Street and city are required")
    
    def format(self) -> str:
        """格式化地址字符串"""
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"
    
    def with_zip_code(self, new_zip: str) -> 'Address':
        """
        创建具有新邮编的地址（返回新对象，原对象不变）
        """
        return Address(
            street=self.street,
            city=self.city,
            state=self.state,
            zip_code=new_zip,
            country=self.country
        )


@dataclass(frozen=True)
class Money:
    """
    货币金额值对象
    
    避免浮点数精度问题，使用整数存储最小单位
    """
    amount: int  # 最小单位（分）
    currency: str  # ISO 4217 货币代码
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency code must be 3 characters")
    
    @classmethod
    def from_decimal(cls, amount: float, currency: str = "USD") -> 'Money':
        """从浮点数创建金额（转换为分）"""
        cents = int(round(amount * 100))
        return cls(cents, currency)
    
    @property
    def decimal_amount(self) -> float:
        """返回元为单位的金额"""
        return self.amount / 100.0
    
    def add(self, other: 'Money') -> 'Money':
        """金额相加"""
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """金额相减"""
        self._assert_same_currency(other)
        if other.amount > self.amount:
            raise ValueError("Insufficient amount")
        return Money(self.amount - other.amount, self.currency)
    
    def multiply(self, factor: float) -> 'Money':
        """金额乘以系数"""
        new_amount = int(round(self.amount * factor))
        return Money(new_amount, self.currency)
    
    def _assert_same_currency(self, other: 'Money'):
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot operate on different currencies: "
                f"{self.currency} vs {other.currency}"
            )
    
    def __str__(self) -> str:
        return f"{self.currency} {self.decimal_amount:.2f}"


@dataclass(frozen=True)
class DateRange:
    """日期范围值对象"""
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before end date")
    
    @property
    def duration_days(self) -> int:
        """计算天数"""
        return (self.end_date - self.start_date).days
    
    def overlaps(self, other: 'DateRange') -> bool:
        """检查两个日期范围是否重叠"""
        return (
            self.start_date < other.end_date and
            self.end_date > other.start_date
        )
    
    def contains(self, date: datetime) -> bool:
        """检查日期是否在范围内"""
        return self.start_date <= date <= self.end_date


@dataclass(frozen=True)
class Email:
    """邮箱值对象"""
    value: str
    
    def __post_init__(self):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid email format: {self.value}")
    
    @property
    def domain(self) -> str:
        """获取邮箱域名"""
        return self.value.split('@')[1]
    
    @property
    def local_part(self) -> str:
        """获取邮箱本地部分"""
        return self.value.split('@')[0]
```

### 值对象的持久化策略

```python
from typing import Dict, Any
import json


class ValueObjectMapper:
    """值对象与数据库映射器"""
    
    @staticmethod
    def address_to_columns(address: Address) -> Dict[str, str]:
        """
        将地址值对象映射为数据库列
        
        展开存储模式（Flattening）
        """
        return {
            'street': address.street,
            'city': address.city,
            'state': address.state,
            'zip_code': address.zip_code,
            'country': address.country
        }
    
    @staticmethod
    def address_from_columns(data: Dict[str, str]) -> Address:
        """从数据库列重建地址值对象"""
        return Address(
            street=data['street'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip_code'],
            country=data.get('country', 'CN')
        )
    
    @staticmethod
    def money_to_json(money: Money) -> str:
        """
        将金额值对象序列化为 JSON
        
        JSON 序列化存储模式
        """
        return json.dumps({
            'amount': money.amount,
            'currency': money.currency
        })
    
    @staticmethod
    def money_from_json(json_str: str) -> Money:
        """从 JSON 反序列化金额值对象"""
        data = json.loads(json_str)
        return Money(data['amount'], data['currency'])


# SQLAlchemy 集成示例
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import composite
from sqlalchemy.ext.hybrid import hybrid_property

class UserORM(Base):
    """用户 ORM 模型"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True)
    username = Column(String(50), nullable=False)
    
    # 地址值对象展开存储
    street = Column(String(200))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(2), default='CN')
    
    @hybrid_property
    def address(self) -> Address:
        if not self.street:
            return None
        return Address(
            street=self.street,
            city=self.city,
            state=self.state,
            zip_code=self.zip_code,
            country=self.country
        )
    
    @address.setter
    def address(self, addr: Address):
        self.street = addr.street
        self.city = addr.city
        self.state = addr.state
        self.zip_code = addr.zip_code
        self.country = addr.country
```

## 示例

### 电商系统中的实体与值对象

```python
from typing import List
from decimal import Decimal


class Product(Entity):
    """商品实体"""
    
    def __init__(self, product_id: str, name: str, 
                 price: Money, weight: 'Weight'):
        super().__init__(product_id)
        self._name = name
        self._price = price
        self._weight = weight
        self._variants: List['ProductVariant'] = []
    
    def update_price(self, new_price: Money):
        """更新价格（业务规则验证）"""
        if new_price.amount <= 0:
            raise ValueError("Price must be positive")
        self._price = new_price


class Weight:
    """重量值对象"""
    
    def __init__(self, value: float, unit: str = "kg"):
        self._value = value
        self._unit = unit
    
    def to_kg(self) -> float:
        if self._unit == "g":
            return self._value / 1000
        return self._value
    
    def add(self, other: 'Weight') -> 'Weight':
        total = self.to_kg() + other.to_kg()
        return Weight(total, "kg")


class ShoppingCart:
    """购物车（值对象集合）"""
    
    def __init__(self):
        self._items: List['CartItem'] = []
    
    def add_item(self, product: Product, quantity: int):
        """添加商品"""
        item = CartItem(product.id, product.price, quantity)
        self._items.append(item)
    
    def calculate_total(self) -> Money:
        """计算购物车总价"""
        total = Money(0, "USD")
        for item in self._items:
            total = total.add(item.subtotal)
        return total


class CartItem:
    """购物车项（值对象）"""
    
    def __init__(self, product_id: str, unit_price: Money, 
                 quantity: int):
        self._product_id = product_id
        self._unit_price = unit_price
        self._quantity = quantity
    
    @property
    def subtotal(self) -> Money:
        return self._unit_price.multiply(self._quantity)


# 使用示例
def example_usage():
    # 创建值对象
    home_address = Address(
        street="123 Main St",
        city="Beijing",
        state="Beijing",
        zip_code="100000"
    )
    
    # 创建实体
    user = User(
        username="john_doe",
        email="john@example.com",
        address=home_address
    )
    
    # 修改实体（值对象替换，非修改）
    new_address = home_address.with_zip_code("100001")
    user.change_address(new_address)
    
    # 创建订单
    order = Order(
        user_id=user.id,
        items=[
            OrderItem(product_id="P001", quantity=2, 
                     unit_price=Money.from_decimal(99.99, "USD"))
        ],
        shipping_address=new_address
    )
    
    return user, order
```

## 应用场景

### 1. 何时使用实体？

**使用实体的场景**：
- 对象需要独立追踪其生命周期
- 业务上需要区分不同实例，即使属性相同
- 需要维护状态历史和变更轨迹
- 需要在多个聚合之间建立关联

**典型实体**：
- 用户账户、客户、供应商
- 订单、发票、合同
- 商品、库存项
- 车辆、设备、资产

### 2. 何时使用值对象？

**使用值对象的场景**：
- 对象仅由其属性值定义，无需身份标识
- 需要确保数据一致性和不变性
- 需要在多个实体间共享相同值
- 需要丰富的领域行为（验证、计算等）

**典型值对象**：
- 地址、坐标、范围
- 金额、度量、数量
- 日期范围、时间段
- 配置、规格、参数
- 颜色、尺寸、重量

### 3. 建模决策指南

```
建模决策流程：

开始
  ↓
对象是否需要身份标识？
  ├── 是 → 追踪生命周期？
  │           ├── 是 → 实体
  │           └── 否 → 重新审视设计
  └── 否 → 属性是否可能变化？
              ├── 是 → 是否关注变化历史？
              │           ├── 是 → 实体
              │           └── 否 → 值对象（注意：修改即替换）
              └── 否 → 值对象（完全不可变）
```

## 面试要点

**Q: 实体和值对象的核心区别是什么？**

A: 核心区别在于**身份标识**和**相等性定义**：
- **实体**：通过唯一ID标识，相等性基于ID判断，关注生命周期和状态变化
- **值对象**：无ID，通过属性值定义，相等性基于所有属性，不可变且可替换

**Q: 为什么值对象应该设计为不可变？**

A: 不可变性带来多个好处：
1. **线程安全**：多线程环境下无需同步
2. **可共享**：相同值的实例可以安全共享
3. **无副作用**：使用值对象不会意外修改系统状态
4. **简化推理**：更容易理解和测试
5. **哈希可用**：可作为字典键或集合元素

**Q: 实体和值对象的相等性实现有何不同？**

A: 相等性实现对比：
```python
# 实体 - 基于ID
class Entity:
    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id  # 仅比较ID
    
    def __hash__(self):
        return hash(self.id)

# 值对象 - 基于所有属性
@dataclass(frozen=True)  # 自动实现基于所有字段的__eq__和__hash__
class ValueObject:
    field1: str
    field2: int
```

**Q: 值对象如何持久化到数据库？**

A: 常见持久化策略：
1. **展开存储**（Flattening）：将值对象属性映射到实体的表列
2. **JSON序列化**：将值对象序列化为JSON字符串存储
3. **单独表**：仅在值对象需要独立查询时创建单独表
4. **嵌入式文档**：使用文档数据库（MongoDB等）直接嵌入

**Q: 实体和值对象如何在聚合中协作？**

A: 在聚合中：
- **聚合根**：必须是实体，作为聚合的入口和一致性边界
- **聚合内实体**：可以包含其他实体，通过引用关联
- **值对象**：用于描述实体属性，可嵌入实体内部
- **规则**：值对象不能跨聚合引用实体，实体可引用聚合根

**Q: 如何处理值对象的集合？**

A: 值对象集合的处理：
```python
# 使用 frozenset 存储不可变集合
@dataclass(frozen=True)
class ProductSpecification:
    attributes: frozenset  # 值对象集合
    
    def has_attribute(self, attr: 'Attribute') -> bool:
        return attr in self.attributes

# 或使用元组（tuple）
class Order:
    def __init__(self):
        self._line_items: tuple = ()  # 不可变列表
    
    def add_item(self, item: 'LineItem') -> 'Order':
        # 返回新订单对象而非修改
        new_items = self._line_items + (item,)
        return Order(new_items)
```

**Q: 实体可以包含值对象，值对象可以包含实体吗？**

A: 
- **实体包含值对象**：✅ 常见且推荐，如User包含Address
- **值对象包含实体**：❌ 不推荐，会破坏值对象的语义
  - 值对象应完全由属性定义，包含实体会引入身份标识概念
  - 如果"值对象"需要引用实体，它可能应该设计为实体

## 相关概念

### 数据结构
- [领域模型](./domain-model.md) - 实体和值对象是领域模型的基本构建块
- [聚合](./aggregates.md) - 聚合内包含实体和值对象的层次结构
- [仓库](./repositories.md) - 实体的持久化机制

### 算法
- 相等性比较算法 - 实体基于ID，值对象基于属性值
- 哈希算法 - 实现值对象的哈希一致性
- 对象映射 - ORM中值对象与数据库列的映射

### 复杂度分析
- 时间复杂度：值对象操作通常是O(1)的基础操作
- 空间复杂度：值对象的不可变性可能增加内存使用（创建新对象而非修改）
- 性能权衡：值对象的验证和创建开销 vs 实体状态管理的复杂性

### 系统实现
- Python `dataclasses` 模块实现值对象
- 不可变性模式：frozen dataclasses、namedtuple
- ORM集成：SQLAlchemy hybrid properties、Django model methods
- 序列化：JSON、MessagePack等格式的值对象序列化
- 领域事件：实体状态变化时发布领域事件
