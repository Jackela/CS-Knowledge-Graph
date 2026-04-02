# 限界上下文 (Bounded Context)

## 简介

限界上下文（Bounded Context）是领域驱动设计（DDD）中的战略性模式，用于明确定义领域模型的适用范围和边界。在一个大型系统中，同一个业务术语在不同上下文中可能具有不同的含义，限界上下文通过显式边界来解决这种语义歧义。

例如，在产品管理系统中：
- **销售上下文**中的"产品"关注价格、促销、库存可售量
- **库存上下文**中的"产品"关注仓库位置、批次、保质期
- **采购上下文**中的"产品"关注供应商、成本价、最小订货量

这三个"产品"概念虽然相关，但属性、行为和约束各不相同，应该存在于各自的限界上下文中。

限界上下文的核心价值：
1. **语义清晰**：每个上下文内的术语具有精确、唯一的含义
2. **团队自治**：不同团队可以独立开发各自的上下文
3. **技术独立**：每个上下文可以选择最适合的技术栈
4. **演化独立**：上下文可以独立演进，减少耦合影响
5. **复杂性隔离**：将大型系统分解为可管理的单元

## 核心概念

### 1. 上下文边界（Context Boundary）

限界上下文的边界定义了模型的适用范围：
- **内部**：统一的领域模型，一致的通用语言
- **外部**：通过显式接口与其他上下文交互
- **边界保护**：防止外部概念污染内部模型

### 2. 通用语言的范围（Scope of Ubiquitous Language）

通用语言只在限界上下文内部通用：
```
┌─────────────────────────────────────────────────────────┐
│                    限界上下文 A                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │              通用语言（Context A）               │    │
│  │  - Customer: 购买商品的人                        │    │
│  │  - Account: 登录系统的凭证                       │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    限界上下文 B                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │              通用语言（Context B）               │    │
│  │  - Customer: 签订服务合同的企业                    │    │
│  │  - Account: 财务应收账户                         │    │
└─────────────────────────────────────────────────────────┘
```

### 3. 上下文映射（Context Mapping）

描述多个限界上下文之间的关系：

| 关系类型 | 描述 | 使用场景 |
|----------|------|----------|
| **合作关系** (Partnership) | 两个团队协作，相互影响 | 新功能同时影响两个上下文 |
| **共享内核** (Shared Kernel) | 共享部分模型，需共同维护 | 核心概念跨上下文通用 |
| **客户-供应商** (Customer-Supplier) | 上游优先满足下游需求 | 有依赖关系的服务 |
| **遵奉者** (Conformist) | 下游完全使用上游模型 | 上游强势，下游无力影响 |
| **防腐层** (Anti-Corruption Layer) | 隔离外部模型，转换为本模型 | 集成遗留系统或外部服务 |
| **开放主机服务** (Open Host Service) | 提供标准化协议供集成 | 作为平台被多个下游使用 |
| **发布语言** (Published Language) | 定义明确的交换格式 | 需要标准化文档的集成 |
| **各行其道** (Separate Ways) | 完全独立，不集成 | 功能完全独立 |
| **大泥球** (Big Ball of Mud) | 混乱的遗留系统 | 需要逐步重构的遗留代码 |

### 4. 核心域与支撑域

限界上下文可以根据业务重要性分类：

```
                    限界上下文分类
                         │
         ┌───────────────┼───────────────┐
         │               │               │
     核心域         支撑子域         通用子域
   (Core Domain)  (Supporting)   (Generic)
         │               │               │
    差异化竞争      支持核心业务      行业通用功能
    资源倾斜        可外包或简化      使用现成方案
```

## 实现方式

### 1. 上下文边界的代码体现

**模块/包结构**：
```
project/
├── context_sales/              # 销售上下文
│   ├── domain/
│   │   ├── product.py         # 销售视角的产品
│   │   ├── order.py
│   │   └── pricing.py
│   ├── application/
│   └── infrastructure/
│
├── context_inventory/          # 库存上下文
│   ├── domain/
│   │   ├── product.py         # 库存视角的产品
│   │   ├── warehouse.py
│   │   └── stock.py
│   ├── application/
│   └── infrastructure/
│
└── context_purchasing/         # 采购上下文
    ├── domain/
    │   ├── product.py         # 采购视角的产品
    │   ├── supplier.py
    │   └── purchase_order.py
    ├── application/
    └── infrastructure/
```

**Python 命名空间隔离**：
```python
# context_sales/domain/product.py
"""销售上下文中的产品概念"""
from decimal import Decimal
from dataclasses import dataclass
from typing import List

@dataclass
class SalesProduct:
    """销售视角的产品"""
    product_id: str
    name: str
    base_price: Decimal
    promotional_price: Optional[Decimal]
    is_active: bool
    category: str
    
    def calculate_price(self, customer_type: str) -> Decimal:
        """根据客户类型计算价格"""
        if self.promotional_price and customer_type == "VIP":
            return self.promotional_price
        return self.base_price
    
    def check_availability(self, quantity: int) -> bool:
        """检查可售库存（调用库存上下文）"""
        # 通过防腐层调用库存服务
        pass


# context_inventory/domain/product.py
"""库存上下文中的产品概念"""
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class InventoryProduct:
    """库存视角的产品"""
    product_id: str
    sku: str
    warehouse_locations: List[WarehouseLocation]
    batches: List[ProductBatch]
    
    def get_available_quantity(self, warehouse_id: str) -> int:
        """获取指定仓库的可用数量"""
        pass
    
    def reserve_stock(self, quantity: int, batch_id: str) -> Reservation:
        """预留库存"""
        pass


# context_purchasing/domain/product.py
"""采购上下文中的产品概念"""
from dataclasses import dataclass
from decimal import Decimal
from typing import List

@dataclass
class PurchasingProduct:
    """采购视角的产品"""
    product_id: str
    supplier_products: List[SupplierProduct]
    min_order_quantity: int
    lead_time_days: int
    
    def get_best_supplier(self, quantity: int) -> SupplierProduct:
        """根据数量选择最优供应商"""
        pass
```

### 2. 上下文映射的实现

**防腐层（Anti-Corruption Layer）模式**：
```python
# integration/acl/inventory_adapter.py
"""销售上下文对库存上下文的防腐层"""
from abc import ABC, abstractmethod
from typing import Optional

class InventoryServiceInterface(ABC):
    """库存服务接口 - 销售上下文定义"""
    
    @abstractmethod
    def check_availability(self, product_id: str, quantity: int) -> StockCheckResult:
        pass
    
    @abstractmethod
    def reserve_stock(self, product_id: str, quantity: int, order_id: str) -> Reservation:
        pass

class InventoryAdapter(InventoryServiceInterface):
    """防腐层适配器"""
    
    def __init__(self, inventory_client: InventoryAPIClient):
        self._client = inventory_client
        self._translator = InventoryTranslator()
    
    def check_availability(self, product_id: str, quantity: int) -> StockCheckResult:
        # 调用外部库存服务
        external_response = self._client.query_stock(product_id)
        
        # 转换外部模型为内部模型
        return self._translator.to_stock_check_result(external_response, quantity)
    
    def reserve_stock(self, product_id: str, quantity: int, order_id: str) -> Reservation:
        # 转换内部请求为外部格式
        external_request = self._translator.to_reserve_request(
            product_id, quantity, order_id
        )
        
        external_response = self._client.reserve(external_request)
        
        # 转换外部响应为内部模型
        return self._translator.to_reservation(external_response)


class InventoryTranslator:
    """模型转换器"""
    
    def to_stock_check_result(self, external_data: dict, requested_qty: int) -> StockCheckResult:
        """将库存API响应转换为内部领域对象"""
        available = external_data.get('available_quantity', 0)
        return StockCheckResult(
            is_available=available >= requested_qty,
            available_quantity=available,
            reserved_quantity=external_data.get('reserved_quantity', 0),
            warehouse_id=external_data.get('warehouse_id')
        )
```

**开放主机服务（Open Host Service）模式**：
```python
# context_inventory/interface/api.py
"""库存上下文提供的开放主机服务"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Inventory Service API", version="1.0.0")

# 发布语言定义
class StockQueryRequest(BaseModel):
    product_id: str
    warehouse_id: Optional[str] = None

class StockQueryResponse(BaseModel):
    product_id: str
    total_available: int
    warehouses: List[WarehouseStock]

class ReservationRequest(BaseModel):
    product_id: str
    quantity: int
    reference_id: str
    reference_type: str  # "ORDER", "PURCHASE", etc.

class ReservationResponse(BaseModel):
    reservation_id: str
    status: str
    reserved_quantity: int
    expires_at: datetime

# 开放主机服务端点
@app.get("/api/v1/stock/{product_id}", response_model=StockQueryResponse)
async def query_stock(product_id: str, warehouse_id: Optional[str] = None):
    """查询库存 - 标准接口"""
    service = get_stock_query_service()
    result = service.query(product_id, warehouse_id)
    return StockQueryResponse(
        product_id=result.product_id,
        total_available=result.total_available,
        warehouses=[
            WarehouseStock(
                warehouse_id=w.warehouse_id,
                available=w.available,
                reserved=w.reserved
            )
            for w in result.warehouses
        ]
    )

@app.post("/api/v1/reservations", response_model=ReservationResponse)
async def create_reservation(request: ReservationRequest):
    """创建库存预留"""
    service = get_reservation_service()
    try:
        reservation = service.reserve(
            product_id=request.product_id,
            quantity=request.quantity,
            reference_id=request.reference_id,
            reference_type=request.reference_type
        )
        return ReservationResponse(
            reservation_id=reservation.id,
            status=reservation.status.value,
            reserved_quantity=reservation.quantity,
            expires_at=reservation.expires_at
        )
    except InsufficientStockError as e:
        raise HTTPException(status_code=409, detail=str(e))
```

### 3. 跨上下文通信

**领域事件集成**：
```python
# context_sales/domain/events.py
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True)
class OrderConfirmedEvent:
    """订单确认事件"""
    event_id: str
    order_id: str
    customer_id: str
    items: List[OrderItemData]
    total_amount: Decimal
    confirmed_at: datetime

@dataclass(frozen=True)
class OrderItemData:
    product_id: str
    quantity: int
    unit_price: Decimal


# context_inventory/application/event_handlers.py
class OrderConfirmedEventHandler:
    """库存上下文处理销售上下文的事件"""
    
    def __init__(self, reservation_service: ReservationService):
        self._reservation_service = reservation_service
    
    async def handle(self, event: OrderConfirmedEvent) -> None:
        """处理订单确认事件，扣减库存"""
        for item in event.items:
            await self._reservation_service.convert_to_actual_deduction(
                reference_id=event.order_id,
                product_id=item.product_id,
                quantity=item.quantity
            )
```

**同步调用与异步事件的选择**：
```python
# 同步调用 - 需要即时结果的场景
class OrderService:
    def create_order(self, customer_id: str, items: List[CartItem]) -> Order:
        # 1. 检查库存（同步调用，需要立即知道结果）
        for item in items:
            availability = self._inventory_adapter.check_availability(
                item.product_id, item.quantity
            )
            if not availability.is_available:
                raise OutOfStockError(item.product_id)
        
        # 2. 创建订单
        order = Order.create(customer_id, items)
        
        # 3. 预留库存（同步，确保库存被锁定）
        for item in items:
            self._inventory_adapter.reserve_stock(
                item.product_id, item.quantity, order.order_id
            )
        
        return order

# 异步事件 - 最终一致性场景
class OrderApplicationService:
    async def confirm_order(self, order_id: str) -> None:
        order = self._order_repository.find_by_id(order_id)
        
        # 执行确认逻辑
        order.confirm()
        
        # 保存订单
        await self._order_repository.save(order)
        
        # 发布事件（异步，不需要等待处理结果）
        events = order.pop_domain_events()
        for event in events:
            await self._event_publisher.publish(event)
```

## 示例

### 电商平台限界上下文设计

```
┌─────────────────────────────────────────────────────────────────┐
│                         电商平台限界上下文                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │  商品上下文   │◄──►│  订单上下文   │◄──►│  库存上下文   │          │
│  │  Product    │    │   Order     │    │  Inventory  │          │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘          │
│         │                  │                  │                  │
│         │            ┌─────┴─────┐            │                  │
│         │            │           │            │                  │
│  ┌──────▼──────┐    ▼           ▼    ┌──────▼──────┐          │
│  │  搜索上下文   │    │  支付上下文  │    │  物流上下文   │          │
│  │   Search    │    │  Payment    │    │  Shipping   │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│         ▲                  ▲                  ▲                  │
│         │                  │                  │                  │
│  ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐          │
│  │  用户上下文   │    │  营销上下文   │    │  通知上下文   │          │
│  │    User     │    │  Marketing  │    │ Notification│          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**完整实现示例**：
```python
# 销售上下文核心代码
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from enum import Enum, auto

class OrderStatus(Enum):
    PENDING_PAYMENT = auto()
    PAID = auto()
    SHIPPED = auto()
    COMPLETED = auto()
    CANCELLED = auto()

@dataclass
class OrderItem:
    product_id: str
    product_name: str  # 冗余存储，避免跨上下文查询
    unit_price: Decimal
    quantity: int
    
    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity

class Order:
    def __init__(self, order_id: str, customer_id: str, 
                 customer_name: str, shipping_address: str):
        self._order_id = order_id
        self._customer_id = customer_id
        self._customer_name = customer_name
        self._shipping_address = shipping_address
        self._items: List[OrderItem] = []
        self._status = OrderStatus.PENDING_PAYMENT
        self._total_amount = Decimal('0')
        self._events = []
    
    def add_item(self, product_id: str, product_name: str,
                 unit_price: Decimal, quantity: int) -> None:
        item = OrderItem(product_id, product_name, unit_price, quantity)
        self._items.append(item)
        self._recalculate_total()
    
    def _recalculate_total(self) -> None:
        self._total_amount = sum(item.subtotal for item in self._items)
    
    def confirm_payment(self, payment_id: str, paid_amount: Decimal) -> None:
        if self._status != OrderStatus.PENDING_PAYMENT:
            raise ValueError("Order is not pending payment")
        if paid_amount < self._total_amount:
            raise ValueError("Insufficient payment")
        
        self._status = OrderStatus.PAID
        self._payment_id = payment_id
        self._paid_at = datetime.now()
        
        # 发布订单支付事件
        self._events.append(OrderPaidEvent(
            order_id=self._order_id,
            customer_id=self._customer_id,
            items=[
                PaidItem(item.product_id, item.quantity)
                for item in self._items
            ],
            shipping_address=self._shipping_address,
            paid_at=self._paid_at
        ))


# 库存上下文通过事件监听处理
class OrderPaidEventHandler:
    """库存上下文中的订单支付事件处理器"""
    
    def __init__(self, inventory_service: InventoryService,
                 shipping_service: ShippingServiceInterface):
        self._inventory = inventory_service
        self._shipping = shipping_service
    
    async def handle(self, event: OrderPaidEvent) -> None:
        # 1. 扣减库存
        for item in event.items:
            await self._inventory.deduct_stock(
                product_id=item.product_id,
                quantity=item.quantity,
                reason=f"Order: {event.order_id}"
            )
        
        # 2. 通知物流上下文发货
        await self._shipping.create_shipment(
            order_id=event.order_id,
            items=event.items,
            shipping_address=event.shipping_address
        )
```

## 应用场景

### 1. 大型企业级系统

适用于具有复杂业务领域的大型系统：
- **银行核心系统**：账户管理、贷款、信用卡、投资理财等不同子域
- **保险核心系统**：保单、理赔、核保、保全、再保险等独立上下文
- **ERP系统**：财务、采购、生产、销售、人力资源等模块

### 2. 微服务架构

限界上下文是微服务划分的黄金标准：
- 每个限界上下文可映射为一个微服务
- 上下文边界成为服务边界
- 上下文映射指导服务间集成策略

### 3. 遗留系统现代化

通过限界上下文逐步重构遗留系统：
- 识别遗留系统中的隐式上下文
- 通过防腐层隔离遗留代码
- 逐步提取和重构核心域

### 4. 多团队协作

支持大型团队的并行开发：
- 每个上下文由独立团队负责
- 上下文间通过契约和API协作
- 减少团队间的沟通成本和依赖

## 面试要点

Q: 什么是限界上下文？为什么需要它？
A: 限界上下文是DDD中定义领域模型适用范围的显式边界。需要它的原因包括：
   - 解决同名概念在不同上下文中语义不同的问题
   - 为团队提供清晰的开发边界和所有权
   - 支持大型系统的分解和并行开发
   - 允许不同上下文使用不同的技术栈
   - 隔离复杂性，防止模型腐化

Q: 限界上下文与微服务的关系是什么？
A: 限界上下文与微服务的关系：
   - 限界上下文是业务边界，微服务是技术边界
   - 理想情况下，一个限界上下文对应一个微服务
   - 但实际中可能多对一（多个小上下文合并）或一对多（大上下文拆分）
   - 限界上下文指导微服务的拆分，是服务边界的决策依据
   - 上下文映射指导服务间的集成模式选择

Q: 什么是上下文映射？列举几种常见的集成模式。
A: 上下文映射是描述多个限界上下文之间关系的模式。常见集成模式：
   - 防腐层（ACL）：隔离外部模型，防止污染内部领域
   - 开放主机服务（OHS）：提供标准化API供集成
   - 发布语言（PL）：定义明确的交换数据格式
   - 客户-供应商：上下游协作，上游优先满足下游需求
   - 共享内核：两个上下文共享部分领域模型
   - 遵奉者：下游完全采用上游模型

Q: 如何实现限界上下文之间的通信？
A: 实现方式：
   - 同步调用：REST API、gRPC，适用于需要即时结果的场景
   - 异步消息：消息队列、领域事件，适用于最终一致性场景
   - 数据同步：CDC（变更数据捕获）、ETL，适用于数据复制场景
   - 选择依据：是否需要即时响应、事务边界、一致性要求

Q: 如何识别限界上下文？
A: 识别方法：
   - 业务语义分析：同一个术语是否有不同含义
   - 组织边界：不同部门关注的业务对象
   - 变化频率：一起变化的概念属于同一上下文
   - 用例分析：完成一个业务功能所需的对象集合
   - 领域专家边界：不同专家的专业领域

Q: 核心域、支撑域和通用域的区别是什么？
A: 区别：
   - 核心域：提供竞争优势的核心业务，需要投入最好资源
   - 支撑域：支持核心域但不是差异化来源，可以简化或外包
   - 通用域：行业通用功能，如认证、通知，建议使用现成方案
   核心域是系统存在的理由，其他两个是必要条件。

Q: 什么是防腐层（ACL）？什么场景下使用？
A: 防腐层是隔离外部模型与内部领域模型的转换层。使用场景：
   - 集成遗留系统：防止旧模型污染新系统
   - 集成第三方服务：屏蔽外部API的变化
   - 上下游模型差异大：将外部概念转换为本域概念
   - 保护核心域：核心域保持纯净，不被外部影响

Q: 限界上下文与模块/包的关系？
A: 关系：
   - 限界上下文是概念边界，模块是代码组织方式
     - 一个限界上下文通常对应代码库中的一个顶级模块
   - 通过包/命名空间严格隔离不同上下文的代码
   - 编译时或代码审查时禁止跨上下文直接引用
   - 跨上下文通信必须通过定义的集成接口

## 相关概念

### 数据结构
- [领域模型](./domain-model.md) - 限界上下文内部的领域模型
- [实体与值对象](./entities-value-objects.md) - 限界上下文内的对象类型
- [聚合](./aggregates.md) - 上下文内的一致性边界

### 算法
- 上下文映射算法 - 识别和分析上下文间关系
- 事件驱动集成 - 跨上下文的异步通信模式
- Saga模式 - 分布式事务的长事务处理

### 复杂度分析
- 限界上下文将O(n²)的复杂度降为O(n)的局部复杂度
- 上下文间通信引入网络延迟：REST约100-500ms，gRPC约10-50ms
- 事件驱动架构下最终一致性通常在秒级到分钟级达成
- 上下文数量增加会带来集成复杂度，需要权衡粒度

### 系统实现
- 微服务架构 - 限界上下文的技术映射
- API网关 - 统一暴露开放主机服务
- 消息队列（Kafka/RabbitMQ）- 跨上下文事件通信
- 服务网格（Service Mesh）- 上下文间通信的基础设施
- 契约测试（Pact）- 验证上下文间接口契约
