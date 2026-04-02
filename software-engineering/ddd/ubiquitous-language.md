# 通用语言 (Ubiquitous Language)

## 简介

通用语言（Ubiquitous Language）是领域驱动设计（DDD）的核心概念之一，它是在领域专家和开发团队之间建立的共享语言。这种语言基于领域模型，贯穿于代码、文档、需求和日常交流中。

通用语言的目标是消除领域专家和技术人员之间的沟通鸿沟，确保业务概念在各个环节得到一致的理解和表达。

## 核心概念

### 为什么需要通用语言

1. **消除歧义**：同一个业务概念在不同角色中有不同理解
2. **减少翻译成本**：避免业务语言和技术语言之间的反复转换
3. **提高代码可读性**：代码反映业务概念，而非技术实现
4. **促进协作**：建立团队共享的词汇表和理解

### 通用语言的特征

1. **基于领域模型**：术语直接映射到领域模型中的概念
2. **无处不在**：存在于代码、测试、文档、会议中
3. **持续演进**：随业务理解深入而不断精炼
4. **团队共享**：开发人员和领域专家共同维护

### 通用语言的层次

```
业务概念层 (Business Concepts)
    ↓ 映射
领域模型层 (Domain Model)
    ↓ 映射
代码实现层 (Code Implementation)
```

## 实现方式

### 建立通用语言的实践

1. **事件风暴（Event Storming）**：通过工作坊识别领域概念
2. **词汇表维护**：建立术语表，定义每个术语的精确含义
3. **代码评审**：确保代码中的命名符合通用语言
4. **文档同步**：保持文档与代码和模型的一致性

### 代码中的通用语言

```python
# 坏示例：技术术语主导
class OrderProcessor:
    def process(self, dto):
        if dto.status == 1:  # 魔法数字
            self.db.execute("UPDATE orders SET s = 2 WHERE id = ?", dto.id)

# 好示例：业务术语主导
class OrderFulfillmentService:
    def fulfill_order(self, order: Order) -> FulfillmentResult:
        """履行订单"""
        if order.status == OrderStatus.PENDING_PAYMENT:
            order.mark_as_paid()
            self.order_repository.save(order)
            
            # 触发库存预留
            self.inventory_service.reserve_stock_for_order(order)
            
            return FulfillmentResult.success(order.order_id)
```

### 领域术语定义示例

```python
# 核心领域术语（通用语言）

class Order:
    """
    订单 - 客户提交的购买请求
    
    业务规则：
    - 订单必须包含至少一个订单项
    - 已支付的订单不可修改
    - 订单总金额 = 所有订单项小计之和
    """
    
    def submit(self) -> None:
        """提交订单 - 客户确认购买意向"""
        pass
    
    def cancel(self, reason: CancellationReason) -> None:
        """取消订单 - 客户或系统取消订单"""
        pass
    
    def fulfill(self) -> None:
        """履行订单 - 仓库开始配货发货"""
        pass

class OrderItem:
    """
    订单项 - 订单中的一个商品条目
    
    包含：商品信息、数量、单价
    """
    
    @property
    def subtotal(self) -> Money:
        """小计 - 该订单项的金额合计"""
        return self.unit_price * self.quantity

class Payment:
    """
    支付 - 客户为订单进行的付款
    
    状态流转：待支付 -> 处理中 -> 已支付/支付失败
    """
    
    def authorize(self) -> Authorization:
        """授权 - 冻结客户账户资金"""
        pass
    
    def capture(self) -> Capture:
        """扣款 - 实际从客户账户扣取资金"""
        pass

# 枚举值也使用业务术语
class OrderStatus(Enum):
    DRAFT = "draft"                    # 草稿 - 购物车状态
    PENDING_PAYMENT = "pending"        # 待支付 - 等待客户付款
    PAID = "paid"                      # 已支付 - 付款成功
    FULFILLING = "fulfilling"          # 履行中 - 仓库配货中
    SHIPPED = "shipped"                # 已发货 - 商品已发出
    DELIVERED = "delivered"            # 已送达 - 客户已签收
    CANCELLED = "cancelled"            # 已取消 - 订单被取消
```

## 示例

### 电商领域的通用语言词汇表

| 通用语言术语 | 定义 | 避免使用的术语 |
|-------------|------|--------------|
| 客户 (Customer) | 在系统中注册的个人或组织 | User, Account |
| 商品 (Product) | 可供销售的物品 | Item, SKU, Goods |
| 购物车 (Shopping Cart) | 客户暂存待购商品的容器 | Basket, CartDTO |
| 订单 (Order) | 客户提交的购买请求 | Transaction, Record |
| 订单项 (Order Line) | 订单中的单个商品条目 | OrderItem, LineItem |
| 价格 (Price) | 商品的单价 | Amount, Value |
| 库存 (Inventory) | 仓库中可售商品的数量 | Stock, Qty |
| 优惠券 (Coupon) | 提供折扣的凭证 | Voucher, DiscountCode |
| 配送 (Delivery) | 将商品送达客户的过程 | Shipping, Logistics |

### 代码中的通用语言实践

```python
class CustomerOnboardingService:
    """客户入职服务 - 处理新客户的注册流程"""
    
    def register_new_customer(
        self,
        registration: CustomerRegistration
    ) -> Customer:
        """
        注册新客户
        
        业务流程：
        1. 验证客户信息
        2. 检查邮箱是否已注册
        3. 创建客户账户
        4. 发送欢迎邮件
        5. 分配客户经理
        """
        # 验证
        self._validate_registration(registration)
        
        # 检查重复
        if self._customer_repository.exists_by_email(
            registration.email
        ):
            raise DuplicateEmailException(
                f"Email {registration.email} already registered"
            )
        
        # 创建客户
        customer = Customer.create(
            email=registration.email,
            name=registration.full_name,
            phone=registration.contact_number
        )
        
        # 保存
        self._customer_repository.save(customer)
        
        # 发送欢迎邮件
        self._notification_service.send_welcome_email(customer)
        
        # 分配客户经理
        account_manager = self._account_manager_assignment_service.assign(
            customer
        )
        customer.assign_account_manager(account_manager)
        
        return customer
```

## 应用场景

### 建立通用语言的时机

1. **项目启动**：在领域建模初期建立基础术语
2. **业务变化**：业务概念演进时更新通用语言
3. **新人加入**：帮助新成员快速理解业务
4. **系统重构**：确保重构不破坏业务语义

### 通用语言维护挑战

| 挑战 | 解决方案 |
|-----|---------|
| 术语冲突 | 工作坊讨论，达成共识 |
| 概念演化 | 版本化术语表，渐进更新 |
| 跨团队不一致 | 共享词汇表，定期同步 |
| 文档不同步 | 代码即文档，注释即约定 |

## 面试要点

**Q: 通用语言和领域模型的关系是什么？**
A: 通用语言是领域模型在语言层面的表达，领域模型是通用语言在代码层面的体现。两者互为表里，共同构成领域驱动设计的核心。

**Q: 如何处理不同限界上下文中的术语差异？**
A: 不同上下文中同一术语可能有不同含义，这是正常的。关键在于：
- 在每个上下文中明确定义术语
- 上下文间通过防腐层进行概念转换
- 避免全局强制统一，允许语境化差异

**Q: 通用语言和数据库表命名有什么关系？**
A: 理想情况下，数据库表名也应该反映通用语言。但在遗留系统中可能需要妥协，此时可以在仓库层进行概念映射。

**Q: 如何向团队推广通用语言？**
A: 推广策略：
- 从核心领域概念开始
- 在代码评审中强化
- 建立术语检查清单
- 定期开展领域知识分享

## 相关概念

### 数据结构
- [字典/哈希表](../computer-science/data-structures/hash-table.md) - 术语映射存储

### 算法
- [自然语言处理](../ai-data-systems/nlp.md) - 术语提取和分析

### 复杂度分析
- [沟通复杂度](../system-design/communication-complexity.md) - 团队协作复杂度

### 系统实现
- [限界上下文](./bounded-context.md) - 通用语言的有效范围
- [领域模型](./domain-model.md) - 通用语言的代码体现
- [事件风暴](../ddd/event-storming.md) - 发现通用语言的方法
