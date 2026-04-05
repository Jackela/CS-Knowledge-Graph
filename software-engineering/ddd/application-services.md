# 应用服务 (Application Services)

## 简介

**应用服务 (Application Service)** 是DDD分层架构中应用层的核心组件，负责编排领域对象来完成具体的业务用例。它作为领域层与外部世界的协调者，处理事务管理、安全验证、日志记录等技术横切关注点，但不包含任何业务规则。

> **核心原则**: 应用服务协调领域对象完成用例，领域服务封装业务规则。应用服务薄，领域服务厚。

```
┌─────────────────────────────────────────────────────────────────┐
│                    应用服务的定位                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌─────────────────┐                          │
│                    │   UI/Controller │                          │
│                    │   用户界面层     │                          │
│                    └────────┬────────┘                          │
│                             │ 调用                              │
│                             ▼                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  Application Layer                       │   │
│   │                    应用层                                 │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│   │  │ App Service │  │ App Service │  │  App Service    │  │   │
│   │  │  订单应用服务 │  │  支付应用服务 │  │  库存应用服务    │  │   │
│   │  ├─────────────┤  ├─────────────┤  ├─────────────────┤  │   │
│   │  │• 事务管理    │  │• 事务管理    │  │• 事务管理        │  │   │
│   │  │• 权限检查    │  │• 安全验证    │  │• 权限检查        │  │   │
│   │  │• 调用仓储    │  │• 调用领域服务│  │• 协调领域对象    │  │   │
│   │  │• 发布事件    │  │• 日志记录    │  │• 事件发布        │  │   │
│   │  │• 用例编排    │  │• 用例编排    │  │• 用例编排        │  │   │
│   │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │   │
│   └─────────┼────────────────┼──────────────────┼───────────┘   │
│             │                │                  │               │
│             ▼                ▼                  ▼               │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  Domain Layer                          │   │
│   │                   领域层(领域对象、领域服务)             │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 核心概念

### 1. 应用服务的职责

| 职责 | 说明 | 示例 |
|------|------|------|
| **用例编排** | 协调领域对象完成特定业务用例 | 下单流程:验证→创建订单→扣库存→支付 |
| **事务管理** | 控制事务边界，确保数据一致性 | `@transactional`装饰器 |
| **安全验证** | 权限检查、身份认证 | 检查用户是否有下单权限 |
| **输入验证** | 验证DTO的完整性和格式 | 验证必填字段、数据格式 |
| **日志记录** | 记录操作日志、审计信息 | 记录谁做了什么操作 |
| **事件发布** | 发布领域事件到消息总线 | 订单创建后发布事件 |

### 2. 应用服务不应该做的事情

```
┌─────────────────────────────────────────────────────────────────┐
│                应用服务职责边界                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ❌ 不应该包含业务规则                                          │
│      • 价格计算 → 应该使用 PricingService(领域服务)             │
│      • 折扣逻辑 → 应该封装在 DiscountPolicy(值对象)            │
│      • 库存检查规则 → 应该在 Inventory 实体中                   │
│                                                                 │
│   ❌ 不应该直接操作数据库                                         │
│      • SQL查询 → 应该通过 Repository 接口                       │
│      • 直接更新表 → 应该通过聚合根方法                          │
│                                                                 │
│   ❌ 不应该依赖具体技术实现                                       │
│      • 直接发送HTTP请求 → 通过防腐层抽象                        │
│      • 直接读写文件 → 通过仓储或基础设施服务                    │
│                                                                 │
│   ✅ 应该专注于                                                   │
│      • 协调领域对象完成用例                                      │
│      • 处理技术横切关注点                                        │
│      • 作为领域层的门面对外提供服务                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3. 应用服务 vs 领域服务对比

| 维度 | 应用服务 (Application Service) | 领域服务 (Domain Service) |
|------|-------------------------------|---------------------------|
| **层次** | 应用层 | 领域层 |
| **关注点** | 技术、流程、协调 | 业务规则、领域概念 |
| **状态** | 无状态 | 无状态 |
| **依赖** | 领域层、基础设施层 | 仅领域层 |
| **事务** | 控制事务边界 | 不参与事务控制 |
| **命名** | `OrderApplicationService` | `PricingService` |
| **测试** | 集成测试为主 | 单元测试为主 |

## 实现方式

### 典型应用服务结构

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager
import logging

# ============================================
# DTO定义 (数据传输对象)
# ============================================

@dataclass
class CreateOrderRequest:
    """创建订单请求DTO"""
    customer_id: str
    items: List['OrderItemDTO']
    shipping_address: 'AddressDTO'
    coupon_code: Optional[str] = None


@dataclass
class OrderItemDTO:
    """订单项DTO"""
    product_id: str
    quantity: int
    unit_price: float


@dataclass
class AddressDTO:
    """地址DTO"""
    province: str
    city: str
    district: str
    street: str
    zip_code: str


@dataclass
class OrderResponse:
    """订单响应DTO"""
    order_id: str
    status: str
    total_amount: float
    created_at: datetime


# ============================================
# 应用服务实现
# ============================================

class OrderApplicationService:
    """
    订单应用服务
    
    职责:
    - 编排下单业务流程
    - 管理事务边界
    - 权限验证
    - 发布领域事件
    """
    
    def __init__(
        self,
        order_repository: 'IOrderRepository',
        product_repository: 'IProductRepository',
        inventory_service: 'IInventoryApplicationService',
        pricing_service: 'IPricingService',
        payment_service: 'IPaymentApplicationService',
        event_publisher: 'IEventPublisher',
        permission_checker: 'IPermissionChecker',
        logger: logging.Logger = None
    ):
        self._order_repository = order_repository
        self._product_repository = product_repository
        self._inventory_service = inventory_service
        self._pricing_service = pricing_service
        self._payment_service = payment_service
        self._event_publisher = event_publisher
        self._permission_checker = permission_checker
        self._logger = logger or logging.getLogger(__name__)
    
    def create_order(
        self,
        request: CreateOrderRequest,
        current_user: 'CurrentUser'
    ) -> OrderResponse:
        """
        创建订单用例
        
        Args:
            request: 创建订单请求
            current_user: 当前用户上下文
        
        Returns:
            订单响应
        
        Raises:
            PermissionDeniedError: 权限不足
            ProductNotFoundError: 商品不存在
            InsufficientInventoryError: 库存不足
            PricingError: 价格计算错误
        """
        # 1. 权限检查
        self._check_permission(current_user, "order:create")
        
        # 2. 参数验证
        self._validate_request(request)
        
        # 3. 开启事务
        with self._transaction_scope():
            # 4. 验证商品并获取价格
            order_items = self._build_order_items(request.items)
            
            # 5. 检查库存
            self._check_inventory(order_items)
            
            # 6. 预留库存
            self._reserve_inventory(order_items)
            
            # 7. 计算价格
            customer = self._get_customer(request.customer_id)
            coupon = self._get_coupon(request.coupon_code)
            total_amount = self._pricing_service.calculate_order_total(
                order_items, customer, coupon
            )
            
            # 8. 创建订单聚合
            order = Order.create(
                customer_id=request.customer_id,
                items=order_items,
                shipping_address=self._to_address_value_object(request.shipping_address),
                total_amount=total_amount
            )
            
            # 9. 保存订单
            self._order_repository.save(order)
            
            # 10. 发布领域事件
            self._publish_order_created_event(order)
            
            # 11. 记录审计日志
            self._log_audit(
                action="ORDER_CREATED",
                user_id=current_user.user_id,
                order_id=order.order_id
            )
        
        return OrderResponse(
            order_id=order.order_id,
            status=order.status.value,
            total_amount=float(total_amount.amount),
            created_at=order.created_at
        )
    
    def confirm_order(
        self,
        order_id: str,
        current_user: 'CurrentUser'
    ) -> OrderResponse:
        """
        确认订单用例
        
        流程: 加载订单 -> 验证状态 -> 确认 -> 保存 -> 发布事件
        """
        # 1. 权限检查
        self._check_permission(current_user, "order:confirm")
        
        with self._transaction_scope():
            # 2. 加载订单
            order = self._order_repository.find_by_id(order_id)
            if not order:
                raise OrderNotFoundError(f"Order not found: {order_id}")
            
            # 3. 验证所有权
            self._verify_order_ownership(order, current_user)
            
            # 4. 执行领域操作
            order.confirm()
            
            # 5. 保存
            self._order_repository.save(order)
            
            # 6. 发布事件
            self._publish_order_confirmed_event(order)
            
            # 7. 触发支付
            self._payment_service.create_payment(order)
        
        return OrderResponse(
            order_id=order.order_id,
            status=order.status.value,
            total_amount=float(order.total_amount.amount),
            created_at=order.created_at
        )
    
    def cancel_order(
        self,
        order_id: str,
        reason: str,
        current_user: 'CurrentUser'
    ) -> OrderResponse:
        """
        取消订单用例
        
        流程: 加载订单 -> 验证权限 -> 取消 -> 释放库存 -> 保存
        """
        self._check_permission(current_user, "order:cancel")
        
        with self._transaction_scope():
            order = self._order_repository.find_by_id(order_id)
            if not order:
                raise OrderNotFoundError(f"Order not found: {order_id}")
            
            # 验证取消权限(只有管理员或订单所有者可以取消)
            if not self._can_cancel(order, current_user):
                raise PermissionDeniedError("Cannot cancel this order")
            
            # 执行领域操作
            order.cancel(reason)
            
            # 释放库存
            self._release_inventory(order.items)
            
            # 保存
            self._order_repository.save(order)
            
            # 发布事件
            self._publish_order_cancelled_event(order, reason)
        
        return OrderResponse(
            order_id=order.order_id,
            status=order.status.value,
            total_amount=float(order.total_amount.amount),
            created_at=order.created_at
        )
    
    def get_order_details(
        self,
        order_id: str,
        current_user: 'CurrentUser'
    ) -> 'OrderDetailsResponse':
        """
        查询订单详情用例
        
        这是一个只读操作，不涉及事务
        """
        # 1. 权限检查
        self._check_permission(current_user, "order:view")
        
        # 2. 加载订单(只读，不需要事务)
        order = self._order_repository.find_by_id(order_id)
        if not order:
            raise OrderNotFoundError(f"Order not found: {order_id}")
        
        # 3. 验证访问权限
        self._verify_order_ownership(order, current_user)
        
        # 4. 组装响应(可能涉及多个数据源)
        return self._build_order_details(order)
    
    # ============================================
    # 私有辅助方法
    # ============================================
    
    def _check_permission(self, user: 'CurrentUser', permission: str) -> None:
        """检查用户权限"""
        if not self._permission_checker.has_permission(user, permission):
            raise PermissionDeniedError(f"Missing permission: {permission}")
    
    def _validate_request(self, request: CreateOrderRequest) -> None:
        """验证请求参数"""
        if not request.items:
            raise ValidationError("Order must contain at least one item")
        if not request.customer_id:
            raise ValidationError("Customer ID is required")
        if request.quantity <= 0:
            raise ValidationError("Quantity must be positive")
    
    @contextmanager
    def _transaction_scope(self):
        """事务范围管理器"""
        try:
            yield
            # 提交事务
        except Exception as e:
            # 回滚事务
            raise
    
    def _build_order_items(
        self,
        item_dtos: List[OrderItemDTO]
    ) -> List['OrderItem']:
        """构建订单项领域对象"""
        items = []
        for dto in item_dtos:
            product = self._product_repository.find_by_id(dto.product_id)
            if not product:
                raise ProductNotFoundError(f"Product not found: {dto.product_id}")
            
            # 验证价格
            if abs(product.current_price - dto.unit_price) > 0.01:
                raise PricingError("Product price has changed")
            
            items.append(OrderItem(
                product_id=dto.product_id,
                quantity=dto.quantity,
                unit_price=Money(dto.unit_price)
            ))
        return items
    
    def _check_inventory(self, items: List['OrderItem']) -> None:
        """检查库存"""
        for item in items:
            available = self._inventory_service.get_available_stock(item.product_id)
            if available < item.quantity:
                raise InsufficientInventoryError(
                    f"Insufficient stock for product {item.product_id}"
                )
    
    def _reserve_inventory(self, items: List['OrderItem']) -> None:
        """预留库存"""
        for item in items:
            self._inventory_service.reserve(item.product_id, item.quantity)
    
    def _release_inventory(self, items: List['OrderItem']) -> None:
        """释放库存"""
        for item in items:
            self._inventory_service.release(item.product_id, item.quantity)
    
    def _get_customer(self, customer_id: str) -> 'Customer':
        """获取客户信息"""
        # 从客户上下文或客户仓储获取
        pass
    
    def _get_coupon(self, coupon_code: Optional[str]) -> Optional['Coupon']:
        """获取优惠券"""
        if not coupon_code:
            return None
        # 从优惠券服务获取
        pass
    
    def _to_address_value_object(self, dto: AddressDTO) -> 'Address':
        """DTO转换为值对象"""
        return Address(
            province=dto.province,
            city=dto.city,
            district=dto.district,
            street=dto.street,
            zip_code=dto.zip_code
        )
    
    def _verify_order_ownership(self, order: 'Order', user: 'CurrentUser') -> None:
        """验证订单所有权"""
        if order.customer_id != user.user_id and not user.is_admin:
            raise PermissionDeniedError("You don't own this order")
    
    def _can_cancel(self, order: 'Order', user: 'CurrentUser') -> bool:
        """检查是否可以取消订单"""
        if user.is_admin:
            return True
        if order.customer_id == user.user_id:
            return order.status in [OrderStatus.CREATED, OrderStatus.CONFIRMED]
        return False
    
    def _publish_order_created_event(self, order: 'Order') -> None:
        """发布订单创建事件"""
        event = OrderCreatedEvent(
            order_id=order.order_id,
            customer_id=order.customer_id,
            total_amount=float(order.total_amount.amount),
            created_at=order.created_at
        )
        self._event_publisher.publish(event)
    
    def _publish_order_confirmed_event(self, order: 'Order') -> None:
        """发布订单确认事件"""
        event = OrderConfirmedEvent(
            order_id=order.order_id,
            confirmed_at=datetime.now()
        )
        self._event_publisher.publish(event)
    
    def _publish_order_cancelled_event(self, order: 'Order', reason: str) -> None:
        """发布订单取消事件"""
        event = OrderCancelledEvent(
            order_id=order.order_id,
            reason=reason,
            cancelled_at=datetime.now()
        )
        self._event_publisher.publish(event)
    
    def _log_audit(self, action: str, user_id: str, **kwargs) -> None:
        """记录审计日志"""
        self._logger.info(
            f"Audit: action={action}, user={user_id}, details={kwargs}"
        )
    
    def _build_order_details(self, order: 'Order') -> 'OrderDetailsResponse':
        """构建订单详情响应"""
        # 组装详细响应数据
        pass


# ============================================
# 接口定义
# ============================================

class IOrderRepository(ABC):
    @abstractmethod
    def save(self, order: 'Order') -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional['Order']:
        pass


class IProductRepository(ABC):
    @abstractmethod
    def find_by_id(self, product_id: str) -> Optional['Product']:
        pass


class IInventoryApplicationService(ABC):
    @abstractmethod
    def get_available_stock(self, product_id: str) -> int:
        pass
    
    @abstractmethod
    def reserve(self, product_id: str, quantity: int) -> None:
        pass
    
    @abstractmethod
    def release(self, product_id: str, quantity: int) -> None:
        pass


class IPaymentApplicationService(ABC):
    @abstractmethod
    def create_payment(self, order: 'Order') -> None:
        pass


class IPricingService(ABC):
    @abstractmethod
    def calculate_order_total(
        self,
        items: List['OrderItem'],
        customer: 'Customer',
        coupon: Optional['Coupon'] = None
    ) -> 'Money':
        pass


class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, event: 'DomainEvent') -> None:
        pass


class IPermissionChecker(ABC):
    @abstractmethod
    def has_permission(self, user: 'CurrentUser', permission: str) -> bool:
        pass


# ============================================
# 异常定义
# ============================================

class ApplicationError(Exception):
    """应用层异常基类"""
    pass


class PermissionDeniedError(ApplicationError):
    """权限不足"""
    pass


class ValidationError(ApplicationError):
    """参数验证错误"""
    pass


class OrderNotFoundError(ApplicationError):
    """订单不存在"""
    pass


class ProductNotFoundError(ApplicationError):
    """商品不存在"""
    pass


class InsufficientInventoryError(ApplicationError):
    """库存不足"""
    pass


class PricingError(ApplicationError):
    """价格错误"""
    pass
