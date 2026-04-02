# 集成测试 (Integration Testing)

## 简介

集成测试是软件测试的一个阶段，旨在验证多个模块、组件或服务在组合在一起时能否正确地协同工作。它关注的是模块之间的接口和交互，确保各个独立开发的单元能够无缝地集成在一起，形成完整的功能系统。

与单元测试不同，集成测试不关注单个模块的内部实现细节，而是关注模块之间的数据流、控制流和通信机制。它是单元测试之后的下一个测试阶段，也是系统测试之前的重要环节。

## 核心概念

### 什么是集成测试

集成测试是一种测试方法，通过组合软件模块并测试它们之间的接口，来发现模块间交互时可能出现的问题。

**主要目标：**
- 验证模块之间的接口是否正确实现
- 发现单元测试中无法发现的集成问题
- 确保数据在模块之间正确传递
- 验证系统的功能完整性

### 集成测试的层次

| 层次 | 描述 | 测试范围 |
|------|------|----------|
| 组件集成测试 | 测试同一应用内的模块 | 类、函数、模块之间 |
| 系统集成测试 | 测试不同应用之间的集成 | 服务、子系统之间 |
| 第三方集成测试 | 测试与外部系统的集成 | API、数据库、消息队列 |

### 集成测试 vs 其他测试类型

```
单元测试 → 集成测试 → 系统测试 → 验收测试
(最小单位)  (模块间)    (完整系统)  (用户视角)
   ↓           ↓           ↓           ↓
 函数/类    模块/服务   端到端流程   业务需求
```

## 实现方式

### 1. 大爆炸集成 (Big Bang)

一次性集成所有模块，然后进行测试。

```python
# 示例：同时测试用户服务和订单服务的集成
def test_user_order_integration():
    # 初始化所有组件
    db = Database()
    cache = Cache()
    user_service = UserService(db, cache)
    order_service = OrderService(db, cache)
    payment_service = PaymentService()
    
    # 测试完整流程
    user = user_service.create_user("test@example.com")
    order = order_service.create_order(user.id, ["item1", "item2"])
    result = payment_service.process_payment(order.id)
    
    assert result.status == "success"
```

**优点：** 快速验证整体流程
**缺点：** 难以定位问题来源

### 2. 自顶向下集成 (Top-Down)

从顶层模块开始，逐步向下集成底层模块，使用桩模块(Stub)模拟未完成的底层模块。

```python
# 桩模块示例 - 模拟支付服务
class PaymentServiceStub:
    def process_payment(self, order_id):
        return PaymentResult(
            order_id=order_id,
            status="success",
            transaction_id=f"stub_{order_id}"
        )

# 测试订单服务（顶层）与支付服务（底层）的集成
def test_order_payment_integration():
    order_service = OrderService()
    payment_stub = PaymentServiceStub()  # 使用桩模块
    order_service.set_payment_service(payment_stub)
    
    order = order_service.create_order(user_id=1, items=["book"])
    result = order_service.checkout(order.id)
    
    assert result.payment_status == "success"
```

### 3. 自底向上集成 (Bottom-Up)

从底层模块开始，逐步向上集成顶层模块，使用驱动模块(Driver)模拟未完成的顶层模块。

```python
# 驱动模块示例 - 模拟订单服务调用
class OrderServiceDriver:
    def __init__(self, payment_service):
        self.payment_service = payment_service
    
    def simulate_checkout(self, order_id, amount):
        return self.payment_service.process_payment(order_id, amount)

# 测试支付服务（底层）
def test_payment_service_integration():
    real_payment_service = PaymentService(PaymentGateway())
    driver = OrderServiceDriver(real_payment_service)
    
    result = driver.simulate_checkout(order_id=123, amount=100)
    
    assert result.success is True
```

### 4. 三明治集成 (Sandwich)

结合自顶向下和自底向上，同时从顶层和底层向中间层集成。

```
    顶层模块 ← 使用桩模块
       ↓
    中间层 ← 真实模块
       ↓
    底层模块 ← 使用驱动模块
```

## 示例

### 完整示例：电商系统集成测试

```python
import pytest
from datetime import datetime

class TestECommerceIntegration:
    """电商系统集成测试示例"""
    
    @pytest.fixture(scope="module")
    def services(self):
        """初始化所有相关服务"""
        db = TestDatabase()
        cache = TestCache()
        
        return {
            'user': UserService(db, cache),
            'product': ProductService(db),
            'order': OrderService(db, cache),
            'inventory': InventoryService(db),
            'payment': PaymentService(TestPaymentGateway())
        }
    
    def test_complete_purchase_flow(self, services):
        """测试完整的购买流程集成"""
        # Step 1: 创建用户
        user = services['user'].register(
            email="buyer@example.com",
            password="secure123"
        )
        assert user.id is not None
        
        # Step 2: 添加商品到购物车
        cart = services['order'].create_cart(user.id)
        product = services['product'].get_product("SKU001")
        services['order'].add_to_cart(cart.id, product.id, quantity=2)
        
        # Step 3: 检查库存
        available = services['inventory'].check_stock(product.id, quantity=2)
        assert available is True
        
        # Step 4: 创建订单
        order = services['order'].checkout(cart.id, shipping_address="...")
        assert order.status == "pending_payment"
        
        # Step 5: 锁定库存
        lock_result = services['inventory'].lock_stock(order.id, product.id, 2)
        assert lock_result.success is True
        
        # Step 6: 处理支付
        payment = services['payment'].charge(
            order_id=order.id,
            amount=order.total_amount,
            card_token="tok_visa"
        )
        assert payment.status == "succeeded"
        
        # Step 7: 确认订单
        services['order'].confirm_payment(order.id, payment.transaction_id)
        updated_order = services['order'].get_order(order.id)
        assert updated_order.status == "confirmed"
        
        # Step 8: 扣除库存
        services['inventory'].deduct_stock(order.id)
        final_stock = services['inventory'].get_stock(product.id)
        assert final_stock == initial_stock - 2
    
    def test_order_cancel_with_inventory_release(self, services):
        """测试订单取消时释放库存的集成"""
        # 创建订单并锁定库存
        order = create_test_order(services)
        services['inventory'].lock_stock(order.id, "SKU001", 5)
        
        initial_available = services['inventory'].get_available_stock("SKU001")
        
        # 取消订单
        services['order'].cancel_order(order.id)
        services['inventory'].release_stock(order.id)
        
        # 验证库存已释放
        current_available = services['inventory'].get_available_stock("SKU001")
        assert current_available == initial_available + 5
    
    def test_concurrent_order_stock_consistency(self, services):
        """测试并发订单下的库存一致性"""
        product_id = "SKU002"
        initial_stock = services['inventory'].get_stock(product_id)
        
        # 模拟并发购买
        orders = []
        for i in range(5):
            order = services['order'].create_order(
                user_id=i+1,
                items=[{"product_id": product_id, "quantity": 2}]
            )
            orders.append(order)
        
        # 验证总锁定数量不超过库存
        total_locked = services['inventory'].get_total_locked_stock(product_id)
        assert total_locked <= initial_stock
        
        # 验证不能超卖
        with pytest.raises(InsufficientStockError):
            services['order'].create_order(
                user_id=999,
                items=[{"product_id": product_id, "quantity": initial_stock}]
            )
```

### 数据库集成测试

```python
class TestDatabaseIntegration:
    """数据库集成测试"""
    
    @pytest.fixture
    def db(self):
        """使用测试数据库实例"""
        connection = create_test_connection()
        transaction = connection.begin()
        yield connection
        transaction.rollback()  # 测试后回滚，保持数据库干净
    
    def test_user_repository_with_real_db(self, db):
        """测试用户仓储层与真实数据库的集成"""
        repo = UserRepository(db)
        
        # 创建
        user = User(email="test@example.com", name="Test User")
        saved_user = repo.save(user)
        assert saved_user.id is not None
        
        # 查询
        found = repo.find_by_email("test@example.com")
        assert found.name == "Test User"
        
        # 更新
        saved_user.name = "Updated Name"
        repo.update(saved_user)
        updated = repo.find_by_id(saved_user.id)
        assert updated.name == "Updated Name"
        
        # 删除
        repo.delete(saved_user.id)
        assert repo.find_by_id(saved_user.id) is None
```

### API集成测试

```python
class TestAPIIntegration:
    """API集成测试"""
    
    BASE_URL = "http://localhost:8080/api"
    
    def test_user_api_flow(self):
        """测试用户API完整流程"""
        # 注册
        register_response = requests.post(
            f"{self.BASE_URL}/users",
            json={"email": "api@test.com", "password": "pass123"}
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]
        
        # 登录
        login_response = requests.post(
            f"{self.BASE_URL}/auth/login",
            json={"email": "api@test.com", "password": "pass123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # 获取用户信息
        profile_response = requests.get(
            f"{self.BASE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        assert profile_response.json()["email"] == "api@test.com"
        
        # 更新用户信息
        update_response = requests.patch(
            f"{self.BASE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Updated Name"}
        )
        assert update_response.status_code == 200
```

## 应用场景

### 1. 微服务架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  用户服务    │────▶│  订单服务    │────▶│  支付服务    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│  通知服务    │     │  库存服务    │
└─────────────┘     └─────────────┘
```

- **服务间通信测试**：验证HTTP/gRPC/消息队列通信
- **数据一致性测试**：验证分布式事务
- **故障恢复测试**：验证服务降级和熔断

### 2. 数据库集成

- ORM与数据库的兼容性
- 数据库迁移脚本验证
- 复杂查询性能验证
- 事务隔离级别验证

### 3. 第三方服务集成

- 支付网关（Stripe、支付宝）
- 消息推送（Firebase、极光）
- 文件存储（S3、OSS）
- 邮件服务（SendGrid、SES）

### 4. 遗留系统集成

- 与新系统的数据同步
- API适配层测试
- 数据格式转换验证

## 面试要点

### 常见问题

**Q1: 集成测试和单元测试的主要区别是什么？**

| 方面 | 单元测试 | 集成测试 |
|------|----------|----------|
| 测试范围 | 单个模块/函数 | 多个模块的交互 |
| 依赖处理 | 全部Mock | 使用真实或测试双 |
| 执行速度 | 快（毫秒级） | 慢（秒级或更长） |
| 定位问题 | 精确到函数 | 可能涉及多个模块 |
| 编写成本 | 较低 | 较高 |

**Q2: 什么是测试双(Test Double)？有哪些类型？**

- **Dummy**: 占位符，不实际使用
- **Fake**: 简化的实现，如内存数据库
- **Stub**: 预设返回值的固定响应
- **Spy**: 记录调用信息的对象
- **Mock**: 预设期望行为的对象

**Q3: 如何处理集成测试中的外部依赖？**

1. **使用Testcontainers**：运行真实服务的Docker容器
2. **契约测试**：使用Pact验证服务间契约
3. **服务虚拟化**：使用WireMock模拟外部API
4. **本地替身**：使用内存数据库或模拟实现

**Q4: 集成测试的最佳实践有哪些？**

- 保持测试独立，避免测试间依赖
- 使用事务回滚保持测试环境干净
- 配置专门的测试环境
- 区分快速集成测试和慢速集成测试
- 在CI/CD流水线中合理安排执行时机

**Q5: 如何设计微服务的集成测试策略？**

```
策略层次：
1. 契约测试（Consumer-Driven Contract Testing）
2. 组件测试（隔离测试单个服务）
3. 集成测试（测试服务间交互）
4. 端到端测试（完整业务流程）
```

## 相关概念

### 相关测试类型

- [单元测试](unit-testing.md) - 测试最小代码单元
- [端到端测试](e2e-testing.md) - 从用户角度测试完整流程
- [契约测试](contract-testing.md) - 验证服务间API契约
- [组件测试](component-testing.md) - 测试单个组件的行为

### 相关工具和框架

| 类型 | 工具 | 用途 |
|------|------|------|
| 测试框架 | Jest, pytest, JUnit | 编写和执行测试 |
| HTTP测试 | REST Assured, Supertest | API集成测试 |
| 数据库 | Testcontainers, H2 | 数据库集成测试 |
| 消息队列 | Embedded Kafka, TestContainers | 消息系统测试 |
| 契约测试 | Pact, Spring Cloud Contract | 服务间契约验证 |
| Mock服务 | WireMock, Mountebank | 模拟外部服务 |

### 设计原则

- **测试金字塔**：单元测试 > 集成测试 > E2E测试
- **契约优先**：先定义API契约再实现
- **环境隔离**：测试环境与生产环境隔离
- **数据管理**：使用种子数据和清理策略
