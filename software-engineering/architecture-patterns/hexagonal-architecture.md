# 六边形架构 (Hexagonal Architecture)

## 简介

**六边形架构**（Hexagonal Architecture），又称**端口与适配器架构**（Ports and Adapters），由 Alistair Cockburn 提出。该架构通过明确的端口和适配器，将核心业务逻辑与外部技术细节隔离，使应用可以在不同环境中运行，易于测试和演进。

## 核心概念

| 概念 | 说明 |
|------|------|
| **Domain** | 领域，核心业务逻辑，独立于技术细节 |
| **Port** | 端口，定义应用与外部交互的接口 |
| **Adapter** | 适配器，实现端口的技术细节 |
| **Primary Adapter** | 驱动适配器，驱动应用运行（如 Web UI）|
| **Secondary Adapter** | 被驱动适配器，应用调用的外部服务（如数据库）|

## 架构图示

```
         ┌─────────────┐
         │   Web UI    │
         └──────┬──────┘
                │
┌───────────────┼───────────────┐
│               ▼               │
│  ┌─────────────────────────┐  │
│  │      Application        │  │
│  │      (Domain Logic)     │  │
│  │  ┌───────────────────┐  │  │
│  │  │      Ports        │  │  │
│  │  └───────────────────┘  │  │
│  └─────────────────────────┘  │
│               │               │
└───────────────┼───────────────┘
                │
         ┌──────┴──────┐
         │  Database   │
         └─────────────┘
```

## 实现方式

### 1. 领域层

```python
# domain/order.py
from dataclasses import dataclass
from typing import List
from decimal import Decimal

@dataclass
class OrderItem:
    product_id: str
    quantity: int
    price: Decimal
    
    def total(self) -> Decimal:
        return self.price * self.quantity

@dataclass
class Order:
    order_id: str
    customer_id: str
    items: List[OrderItem]
    
    def total_amount(self) -> Decimal:
        return sum(item.total() for item in self.items)
    
    def add_item(self, item: OrderItem) -> None:
        self.items.append(item)
```

### 2. 端口定义

```python
# ports/order_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from domain.order import Order

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, order_id: str) -> Optional[Order]:
        pass

# ports/payment_gateway.py
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: Decimal, currency: str) -> bool:
        pass
```

### 3. 应用服务

```python
# application/order_service.py
from domain.order import Order, OrderItem
from ports.order_repository import OrderRepository
from ports.payment_gateway import PaymentGateway

class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        payment_gateway: PaymentGateway
    ):
        self.order_repository = order_repository
        self.payment_gateway = payment_gateway
    
    def create_order(
        self,
        customer_id: str,
        items: List[OrderItem]
    ) -> Order:
        order_id = self._generate_order_id()
        order = Order(order_id, customer_id, items)
        self.order_repository.save(order)
        return order
    
    def pay_order(self, order_id: str) -> bool:
        order = self.order_repository.find_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        return self.payment_gateway.charge(
            order.total_amount(),
            "USD"
        )
    
    def _generate_order_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
```

### 4. 适配器实现

```python
# adapters/db/order_repository_sql.py
from ports.order_repository import OrderRepository
from domain.order import Order, OrderItem

class SqlOrderRepository(OrderRepository):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def save(self, order: Order) -> None:
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO orders (id, customer_id) VALUES (?, ?)",
            (order.order_id, order.customer_id)
        )
        for item in order.items:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
                (order.order_id, item.product_id, item.quantity, float(item.price))
            )
        self.db.commit()
    
    def find_by_id(self, order_id: str) -> Optional[Order]:
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        # 加载订单项...
        return Order(row['id'], row['customer_id'], [])

# adapters/payment/stripe_gateway.py
from ports.payment_gateway import PaymentGateway
from decimal import Decimal
import stripe

class StripePaymentGateway(PaymentGateway):
    def __init__(self, api_key: str):
        stripe.api_key = api_key
    
    def charge(self, amount: Decimal, currency: str) -> bool:
        try:
            stripe.Charge.create(
                amount=int(amount * 100),  # 转为分
                currency=currency.lower(),
                source="tok_visa"  # 测试 token
            )
            return True
        except stripe.error.CardError:
            return False
```

### 5. 主适配器

```python
# adapters/web/order_controller.py
from flask import Flask, request, jsonify
from application.order_service import OrderService
from adapters.db.order_repository_sql import SqlOrderRepository
from adapters.payment.stripe_gateway import StripePaymentGateway

app = Flask(__name__)

# 依赖注入
order_repo = SqlOrderRepository(get_db())
payment_gateway = StripePaymentGateway(get_stripe_key())
order_service = OrderService(order_repo, payment_gateway)

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    items = [OrderItem(**item) for item in data['items']]
    order = order_service.create_order(data['customer_id'], items)
    return jsonify({'order_id': order.order_id}), 201

@app.route('/orders/<order_id>/pay', methods=['POST'])
def pay_order(order_id):
    success = order_service.pay_order(order_id)
    return jsonify({'success': success})
```

## 测试优势

```python
# test_order_service.py
import pytest
from unittest.mock import Mock
from application.order_service import OrderService
from domain.order import Order, OrderItem

class TestOrderService:
    def test_create_order(self):
        # 使用内存仓库测试，无需真实数据库
        mock_repo = Mock()
        mock_payment = Mock()
        service = OrderService(mock_repo, mock_payment)
        
        items = [OrderItem("P1", 2, Decimal("10.00"))]
        order = service.create_order("C1", items)
        
        assert order.customer_id == "C1"
        mock_repo.save.assert_called_once()
    
    def test_pay_order_success(self):
        mock_repo = Mock()
        mock_payment = Mock()
        mock_payment.charge.return_value = True
        
        order = Order("O1", "C1", [OrderItem("P1", 1, Decimal("50.00"))])
        mock_repo.find_by_id.return_value = order
        
        service = OrderService(mock_repo, mock_payment)
        result = service.pay_order("O1")
        
        assert result is True
        mock_payment.charge.assert_called_with(Decimal("50.00"), "USD")
```

## 应用场景

- **微服务**: 服务边界清晰，易于独立部署
- **事件驱动系统**: 通过端口处理事件
- **多界面应用**: 相同核心逻辑支持 Web、CLI、API

## 面试要点

**Q: 六边形架构与整洁架构的区别？**
A: 两者都强调业务逻辑独立于框架，但六边形架构更强调"端口和适配器"的概念，清晰地划分了驱动和被驱动的边界。

**Q: 端口和适配器的区别？**
A: 端口是业务逻辑定义的接口（契约），适配器是对该接口的技术实现。业务逻辑只依赖端口，不关心具体适配器。

**Q: 为什么叫"六边形"？**
A: 六边形只是为了图示美观，表示可以有多个端口和适配器连接，没有特殊含义。

## 相关概念

- [整洁架构](./clean-architecture.md)
- [分层架构](./layered-architecture.md)
- [端口适配器模式](../design-patterns/structural/adapter.md)
