# 领域服务 (Domain Services)

## 简介

**领域服务 (Domain Service)** 是领域驱动设计(DDD)战术设计中的核心概念之一，用于封装不属于任何单个实体(Entity)或值对象(Value Object)的业务逻辑。当业务操作涉及多个领域对象，或者某个业务概念本身不适合用实体/值对象表达时，领域服务是最佳选择。

> **核心原则**: 领域服务是无状态的，它只负责协调领域对象完成业务操作，自身不维护业务状态。

```
┌─────────────────────────────────────────────────────────────────┐
│                    领域服务的定位                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│   │   Entity    │    │ Value Object│    │   Domain Service    │ │
│   │   实体       │    │   值对象     │    │    领域服务          │ │
│   ├─────────────┤    ├─────────────┤    ├─────────────────────┤ │
│   │ 有唯一标识   │    │ 无标识      │    │ 无状态              │ │
│   │ 有生命周期   │    │ 不可变      │    │ 跨对象操作          │ │
│   │ 封装自身逻辑 │    │ 属性定义    │    │ 业务规则协调        │ │
│   └─────────────┘    └─────────────┘    └─────────────────────┘ │
│                                                                 │
│   使用场景:                                                     │
│   ✓ 业务逻辑跨越多个聚合                                        │
│   ✓ 业务逻辑不适合放在任何实体中                                │
│   ✓ 需要表达重要的业务概念                                      │
│   ✓ 执行转换或计算操作                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 核心概念

### 1. 领域服务的特征

| 特征 | 说明 |
|------|------|
| **无状态** | 不维护任何业务状态，仅通过参数接收输入 |
| **无副作用** | 不直接修改数据库或调用外部系统(通过领域对象) |
| **表达业务概念** | 命名来源于领域专家使用的业务术语 |
| **协调者角色** | 协调多个领域对象完成复杂业务操作 |

### 2. 领域服务 vs 应用服务

```
┌─────────────────────────────────────────────────────────────────┐
│               领域服务 vs 应用服务                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────────────┐      ┌───────────────────────┐      │
│   │    Application        │      │      Domain           │      │
│   │     Service           │      │     Service           │      │
│   │    应用服务            │      │    领域服务            │      │
│   ├───────────────────────┤      ├───────────────────────┤      │
│   │ • 事务管理            │      │ • 业务规则            │      │
│   │ • 权限检查            │      │ • 领域计算            │      │
│   │ • 日志记录            │      │ • 跨聚合协调          │      │
│   │ • 调用仓储            │      │ • 领域概念表达        │      │
│   │ • 编排用例            │      │ • 纯业务逻辑          │      │
│   │ • 技术关注点          │      │ • 业务关注点          │      │
│   └───────────────────────┘      └───────────────────────┘      │
│                                                                 │
│   层次: 应用层(上一层)            层次: 领域层(核心层)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3. 何时使用领域服务

**应该使用领域服务的情况**:
1. **跨聚合操作**: 需要协调多个聚合完成业务逻辑
2. **复杂计算**: 涉及多个领域对象的复杂业务计算
3. **业务概念本身**: 如"转账"、"结算"本身就是业务概念
4. **不适合归属于实体**: 逻辑不适合放在任何单一实体中

**不应该使用的情况**:
1. 可以放在实体内部的简单逻辑 → 使用充血模型
2. 纯数据查询操作 → 使用仓储或查询服务
3. 技术基础设施操作 → 放在基础设施层
4. 流程编排 → 这是应用服务的职责

## 实现方式

### 基本结构

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


class Money:
    """值对象 - 金额"""
    def __init__(self, amount: Decimal, currency: str = "CNY"):
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        self._amount = amount
        self._currency = currency
    
    @property
    def amount(self) -> Decimal:
        return self._amount
    
    def add(self, other: 'Money') -> 'Money':
        if self._currency != other._currency:
            raise ValueError("Cannot add different currencies")
        return Money(self._amount + other._amount, self._currency)
    
    def multiply(self, factor: float) -> 'Money':
        return Money(self._amount * Decimal(str(factor)), self._currency)


class DiscountRule:
    """值对象 - 折扣规则"""
    def __init__(self, threshold: Money, discount_rate: float):
        self._threshold = threshold
        self._discount_rate = discount_rate
    
    def is_applicable(self, amount: Money) -> bool:
        return amount.amount >= self._threshold.amount
    
    def apply(self, amount: Money) -> Money:
        if not self.is_applicable(amount):
            return amount
        return amount.multiply(1 - self._discount_rate)


# ============================================
# 领域服务实现
# ============================================

class PricingService:
    """
    定价服务 - 领域服务
    
    封装复杂的定价逻辑，包括：
    - 基础价格计算
    - 会员折扣
    - 促销规则应用
    - 满减/满折计算
    """
    
    def __init__(self, discount_rules: List[DiscountRule]):
        self._discount_rules = discount_rules
    
    def calculate_order_total(
        self,
        items: List['OrderItem'],
        customer: 'Customer',
        coupon: Optional['Coupon'] = None
    ) -> Money:
        """
        计算订单总价
        
        Args:
            items: 订单项列表
            customer: 客户(用于会员折扣)
            coupon: 优惠券
        
        Returns:
            计算后的总金额
        """
        # 1. 计算商品原价总和
        subtotal = sum(
            (item.unit_price.multiply(item.quantity) for item in items),
            start=Money(Decimal('0'))
        )
        
        # 2. 应用折扣规则
        discounted_amount = self._apply_discount_rules(subtotal)
        
        # 3. 应用会员折扣
        final_amount = self._apply_membership_discount(
            discounted_amount, customer
        )
        
        # 4. 应用优惠券
        if coupon and coupon.is_valid():
            final_amount = coupon.apply(final_amount)
        
        return final_amount
    
    def _apply_discount_rules(self, amount: Money) -> Money:
        """应用折扣规则"""
        applicable_rules = [
            rule for rule in self._discount_rules 
            if rule.is_applicable(amount)
        ]
        
        if not applicable_rules:
            return amount
        
        # 选择最优折扣
        best_rule = min(
            applicable_rules,
            key=lambda r: r.apply(amount).amount
        )
        return best_rule.apply(amount)
    
    def _apply_membership_discount(
        self, 
        amount: Money, 
        customer: 'Customer'
    ) -> Money:
        """应用会员折扣"""
        if customer.membership_level == MembershipLevel.GOLD:
            return amount.multiply(0.85)  # 金卡85折
        elif customer.membership_level == MembershipLevel.SILVER:
            return amount.multiply(0.90)  # 银卡9折
        return amount


class TransferService:
    """
    转账服务 - 领域服务
    
    跨聚合的业务操作示例，协调两个账户聚合
    """
    
    def transfer(
        self,
        from_account: 'Account',
        to_account: 'Account',
        amount: Money,
        description: str = ""
    ) -> 'TransferRecord':
        """
        执行转账操作
        
        Args:
            from_account: 转出账户
            to_account: 转入账户
            amount: 转账金额
            description: 转账说明
        
        Returns:
            转账记录
        
        Raises:
            InsufficientBalanceError: 余额不足
            TransferLimitExceededError: 超出转账限额
        """
        # 1. 验证转账规则
        self._validate_transfer(from_account, to_account, amount)
        
        # 2. 执行扣款
        from_account.debit(amount, description)
        
        # 3. 执行入账
        to_account.credit(amount, description)
        
        # 4. 创建转账记录
        return TransferRecord(
            from_account_id=from_account.account_id,
            to_account_id=to_account.account_id,
            amount=amount,
            description=description,
            timestamp=datetime.now()
        )
    
    def _validate_transfer(
        self,
        from_account: 'Account',
        to_account: 'Account', 
        amount: Money
    ) -> None:
        """验证转账规则"""
        # 检查余额
        if from_account.balance.amount < amount.amount:
            raise InsufficientBalanceError(
                f"Insufficient balance: {from_account.balance.amount} < {amount.amount}"
            )
        
        # 检查转账限额
        daily_limit = from_account.daily_transfer_limit
        if amount.amount > daily_limit.amount:
            raise TransferLimitExceededError(
                f"Amount {amount.amount} exceeds daily limit {daily_limit.amount}"
            )
        
        # 检查账户状态
        if not from_account.is_active:
            raise AccountInactiveError("Source account is inactive")
        if not to_account.is_active:
            raise AccountInactiveError("Target account is inactive")


class InventoryAllocationService:
    """
    库存分配服务 - 领域服务
    
    处理复杂的库存分配逻辑，涉及多个仓库和商品
    """
    
    def allocate(
        self,
        order_items: List['OrderItem'],
        warehouses: List['Warehouse']
    ) -> List['AllocationResult']:
        """
        为订单分配库存
        
        策略：
        1. 优先从最近的仓库分配
        2. 单仓库无法满足时，多仓库拆分
        3. 标记缺货商品
        
        Args:
            order_items: 订单商品列表
            warehouses: 可用仓库列表
        
        Returns:
            分配结果列表
        """
        results = []
        
        for item in order_items:
            allocation = self._allocate_single_item(item, warehouses)
            results.extend(allocation)
        
        return results
    
    def _allocate_single_item(
        self,
        item: 'OrderItem',
        warehouses: List['Warehouse']
    ) -> List['AllocationResult']:
        """为单个商品分配库存"""
        remaining_quantity = item.quantity
        allocations = []
        
        # 按距离排序仓库
        sorted_warehouses = sorted(
            warehouses,
            key=lambda w: w.distance_to_destination
        )
        
        for warehouse in sorted_warehouses:
            if remaining_quantity <= 0:
                break
            
            available = warehouse.get_available_stock(item.product_id)
            if available <= 0:
                continue
            
            allocate_qty = min(remaining_quantity, available)
            warehouse.allocate(item.product_id, allocate_qty)
            
            allocations.append(AllocationResult(
                product_id=item.product_id,
                warehouse_id=warehouse.warehouse_id,
                allocated_quantity=allocate_qty,
                unit_price=item.unit_price
            ))
            
            remaining_quantity -= allocate_qty
        
        # 标记缺货
        if remaining_quantity > 0:
            allocations.append(AllocationResult(
                product_id=item.product_id,
                warehouse_id=None,
                allocated_quantity=0,
                shortage_quantity=remaining_quantity,
                unit_price=item.unit_price
            ))
        
        return allocations


# ============================================
# 相关领域对象定义
# ============================================

class OrderItem:
    """订单项"""
    def __init__(self, product_id: str, quantity: int, unit_price: Money):
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price


class Customer:
    """客户实体"""
    def __init__(self, customer_id: str, membership_level: 'MembershipLevel'):
        self.customer_id = customer_id
        self.membership_level = membership_level


class MembershipLevel:
    """会员等级"""
    REGULAR = "regular"
    SILVER = "silver"
    GOLD = "gold"


class Coupon:
    """优惠券"""
    def __init__(self, code: str, discount_amount: Money, expiry_date: datetime):
        self.code = code
        self.discount_amount = discount_amount
        self.expiry_date = expiry_date
    
    def is_valid(self) -> bool:
        return datetime.now() < self.expiry_date
    
    def apply(self, amount: Money) -> Money:
        result = Money(amount.amount - self.discount_amount.amount)
        return result if result.amount > 0 else Money(Decimal('0'))


class Account:
    """账户实体"""
    def __init__(self, account_id: str, balance: Money, daily_limit: Money):
        self.account_id = account_id
        self._balance = balance
        self._daily_transfer_limit = daily_limit
        self._is_active = True
        self._daily_transferred = Money(Decimal('0'))
    
    @property
    def balance(self) -> Money:
        return self._balance
    
    @property
    def daily_transfer_limit(self) -> Money:
        return self._daily_transfer_limit
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def debit(self, amount: Money, description: str = "") -> None:
        """扣款"""
        if self._balance.amount < amount.amount:
            raise InsufficientBalanceError("Insufficient balance")
        self._balance = Money(self._balance.amount - amount.amount)
    
    def credit(self, amount: Money, description: str = "") -> None:
        """入账"""
        self._balance = self._balance.add(amount)


@dataclass
class TransferRecord:
    """转账记录"""
    from_account_id: str
    to_account_id: str
    amount: Money
    description: str
    timestamp: datetime


class Warehouse:
    """仓库实体"""
    def __init__(self, warehouse_id: str, distance: float):
        self.warehouse_id = warehouse_id
        self.distance_to_destination = distance
        self._inventory = {}
    
    def get_available_stock(self, product_id: str) -> int:
        return self._inventory.get(product_id, 0)
    
    def allocate(self, product_id: str, quantity: int) -> None:
        if self._inventory.get(product_id, 0) < quantity:
            raise ValueError("Insufficient stock")
        self._inventory[product_id] -= quantity


@dataclass
class AllocationResult:
    """分配结果"""
    product_id: str
    warehouse_id: Optional[str]
    allocated_quantity: int
    unit_price: Money
    shortage_quantity: int = 0


# ============================================
# 异常定义
# ============================================

class DomainError(Exception):
    """领域异常基类"""
    pass


class InsufficientBalanceError(DomainError):
    """余额不足"""
    pass


class TransferLimitExceededError(DomainError):
    """超出转账限额"""
    pass


class AccountInactiveError(DomainError):
    """账户未激活"""
    pass


# ============================================
# 领域服务接口(依赖倒置)
# ============================================

class IPricingService(ABC):
    """定价服务接口"""
    
    @abstractmethod
    def calculate_order_total(
        self,
        items: List[OrderItem],
        customer: Customer,
        coupon: Optional[Coupon] = None
    ) -> Money:
        pass


class ITransferService(ABC):
    """转账服务接口"""
    
    @abstractmethod
    def transfer(
        self,
        from_account: Account,
        to_account: Account,
        amount: Money,
        description: str = ""
    ) -> TransferRecord:
        pass
