# 模拟测试 (Mocking)

## 简介

模拟测试（Mocking）是一种测试技术，通过创建测试替身（Test Doubles）来替代真实的依赖对象，从而隔离被测单元，控制测试环境，验证被测对象与依赖的交互行为。Mocking是现代单元测试的核心技术，它使得测试可以专注于单一组件的行为，而不受外部依赖的影响。

Mocking的核心价值在于：隔离被测代码、控制依赖行为、验证交互协议、加速测试执行。

## 核心概念

### 测试替身（Test Doubles）类型

| 类型 | 目的 | 使用场景 |
|------|------|----------|
| **Dummy** | 占位 | 参数占位，不被实际使用 |
| **Fake** | 简化实现 | 内存数据库、简化版服务 |
| **Stub** | 预设响应 | 返回固定数据 |
| **Spy** | 记录调用 | 验证方法是否被调用 |
| **Mock** | 验证交互 | 验证调用顺序和参数 |

```
测试场景示意图：

[被测单元] ──────▶ [真实依赖]
                     ↓
              网络调用/慢/不稳定
                     ↓
[被测单元] ──────▶ [Mock对象]
                     ↓
              快速、可控、可验证
```

### Mocking vs Stubbing

```python
# Stubbing - 关注状态
class PaymentGatewayStub:
    """Stub只返回预设值"""
    def charge(self, amount):
        return PaymentResult(success=True, transaction_id="stub-123")

# Mocking - 关注行为
payment_mock = Mock()
payment_mock.charge.return_value = PaymentResult(success=True)

# 执行被测代码
order_service.process_order(order, payment_mock)

# 验证行为（Mock的核心）
payment_mock.charge.assert_called_once_with(amount=100)
```

### 什么时候使用Mocking

**应该Mock：**
- 外部服务（HTTP API、数据库）
- 不确定性（随机数、当前时间）
- 慢操作（文件IO、网络请求）
- 难以设置的状态

**不应该Mock：**
- 被测单元本身的逻辑
- 纯函数和值对象
- 稳定的内部依赖
- 想要验证的真实行为

## 实现方式

### 1. Python - unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock, call
import pytest

class TestOrderService:
    """订单服务测试 - 使用Mocking"""
    
    def test_process_order_calls_payment_gateway(self):
        """测试处理订单时调用支付网关"""
        # Arrange
        payment_gateway = Mock()
        payment_gateway.charge.return_value = {
            "success": True,
            "transaction_id": "txn_123"
        }
        
        inventory_service = Mock()
        inventory_service.check_stock.return_value = True
        
        order_service = OrderService(
            payment_gateway=payment_gateway,
            inventory_service=inventory_service
        )
        
        order = Order(
            id="order_001",
            items=[{"product_id": "P1", "quantity": 2}],
            total_amount=100.0
        )
        
        # Act
        result = order_service.process_order(order)
        
        # Assert - 验证行为
        payment_gateway.charge.assert_called_once_with(
            amount=100.0,
            currency="USD",
            order_id="order_001"
        )
        assert result.status == "paid"
    
    def test_payment_failure_triggers_rollback(self):
        """测试支付失败触发回滚"""
        # Arrange
        payment_gateway = Mock()
        payment_gateway.charge.return_value = {"success": False, "error": "insufficient_funds"}
        
        inventory_service = Mock()
        order_service = OrderService(payment_gateway, inventory_service)
        
        order = Order(id="order_002", total_amount=50.0)
        
        # Act
        result = order_service.process_order(order)
        
        # Assert - 验证多个交互
        inventory_service.lock_stock.assert_called_once()
        payment_gateway.charge.assert_called_once()
        inventory_service.release_stock.assert_called_once_with("order_002")
        assert result.status == "failed"
    
    @patch('services.notification.EmailService')
    def test_order_confirmation_email(self, mock_email_class):
        """使用patch装饰器模拟类"""
        # Arrange
        mock_email_service = mock_email_class.return_value
        mock_email_service.send.return_value = {"status": "sent"}
        
        order_service = OrderService()
        order = Order(id="order_003", customer_email="user@example.com")
        
        # Act
        order_service.confirm_order(order)
        
        # Assert
        mock_email_service.send.assert_called_once()
        call_args = mock_email_service.send.call_args
        assert call_args.kwargs['to'] == "user@example.com"
        assert "order_003" in call_args.kwargs['subject']
    
    def test_multiple_payment_attempts(self):
        """测试多次支付尝试"""
        payment_gateway = Mock()
        # 第一次失败，第二次成功
        payment_gateway.charge.side_effect = [
            {"success": False, "error": "network_error"},
            {"success": True, "transaction_id": "txn_456"}
        ]
        
        order_service = OrderService(payment_gateway)
        order = Order(id="order_004", total_amount=200.0)
        
        result = order_service.process_with_retry(order, max_retries=3)
        
        # 验证调用了两次
        assert payment_gateway.charge.call_count == 2
        
        # 验证调用参数
        expected_calls = [
            call(amount=200.0, currency="USD", order_id="order_004"),
            call(amount=200.0, currency="USD", order_id="order_004")
        ]
        payment_gateway.charge.assert_has_calls(expected_calls)


class TestMockAdvancedFeatures:
    """Mock高级特性"""
    
    def test_mock_spy_functionality(self):
        """测试Mock的Spy功能"""
        calculator = Calculator()
        calculator.add = Mock(wraps=calculator.add)  # 包装真实方法
        
        result = calculator.add(2, 3)
        
        assert result == 5  # 真实返回值
        calculator.add.assert_called_with(2, 3)  # 验证调用
    
    def test_mock_context_manager(self):
        """测试模拟上下文管理器"""
        mock_file = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=False)
        mock_file.read.return_value = "file content"
        
        with mock_file as f:
            content = f.read()
        
        assert content == "file content"
        mock_file.__exit__.assert_called_once()
    
    def test_mock_async_functions(self):
        """测试模拟异步函数"""
        import asyncio
        
        async_mock = Mock()
        async_mock.fetch_data = Mock(return_value=asyncio.Future())
        async_mock.fetch_data.return_value.set_result({"data": "test"})
        
        async def test():
            result = await async_mock.fetch_data("url")
            assert result == {"data": "test"}
        
        asyncio.run(test())
```

### 2. JavaScript - Jest

```javascript
// services/PaymentService.js
class PaymentService {
  constructor(gateway, logger) {
    this.gateway = gateway;
    this.logger = logger;
  }

  async processPayment(order) {
    this.logger.info(`Processing payment for order ${order.id}`);
    
    const result = await this.gateway.charge({
      amount: order.amount,
      currency: order.currency,
      orderId: order.id
    });

    if (result.success) {
      this.logger.info(`Payment successful: ${result.transactionId}`);
      return { status: 'paid', transactionId: result.transactionId };
    } else {
      this.logger.error(`Payment failed: ${result.error}`);
      throw new PaymentError(result.error);
    }
  }
}

// __tests__/PaymentService.test.js
describe('PaymentService', () => {
  let mockGateway;
  let mockLogger;
  let paymentService;

  beforeEach(() => {
    // 创建Mock对象
    mockGateway = {
      charge: jest.fn()
    };
    
    mockLogger = {
      info: jest.fn(),
      error: jest.fn()
    };
    
    paymentService = new PaymentService(mockGateway, mockLogger);
  });

  test('should call gateway with correct parameters', async () => {
    // Arrange
    const order = { id: 'ORD-001', amount: 100, currency: 'USD' };
    mockGateway.charge.mockResolvedValue({
      success: true,
      transactionId: 'TXN-123'
    });

    // Act
    await paymentService.processPayment(order);

    // Assert
    expect(mockGateway.charge).toHaveBeenCalledWith({
      amount: 100,
      currency: 'USD',
      orderId: 'ORD-001'
    });
    expect(mockGateway.charge).toHaveBeenCalledTimes(1);
  });

  test('should return success result on successful payment', async () => {
    // Arrange
    const order = { id: 'ORD-002', amount: 200, currency: 'EUR' };
    mockGateway.charge.mockResolvedValue({
      success: true,
      transactionId: 'TXN-456'
    });

    // Act
    const result = await paymentService.processPayment(order);

    // Assert
    expect(result).toEqual({
      status: 'paid',
      transactionId: 'TXN-456'
    });
  });

  test('should throw error on payment failure', async () => {
    // Arrange
    const order = { id: 'ORD-003', amount: 300, currency: 'GBP' };
    mockGateway.charge.mockResolvedValue({
      success: false,
      error: 'Insufficient funds'
    });

    // Act & Assert
    await expect(paymentService.processPayment(order))
      .rejects.toThrow('Insufficient funds');
    
    expect(mockLogger.error).toHaveBeenCalledWith(
      'Payment failed: Insufficient funds'
    );
  });

  test('should log payment attempt', async () => {
    const order = { id: 'ORD-004', amount: 150, currency: 'USD' };
    mockGateway.charge.mockResolvedValue({ success: true, transactionId: 'TXN-789' });

    await paymentService.processPayment(order);

    expect(mockLogger.info).toHaveBeenCalledWith(
      'Processing payment for order ORD-004'
    );
    expect(mockLogger.info).toHaveBeenCalledWith(
      'Payment successful: TXN-789'
    );
  });

  test('should handle sequential calls with different responses', async () => {
    // 设置连续调用的不同返回值
    mockGateway.charge
      .mockResolvedValueOnce({ success: true, transactionId: 'TXN-1' })
      .mockResolvedValueOnce({ success: false, error: 'Network error' })
      .mockResolvedValueOnce({ success: true, transactionId: 'TXN-3' });

    const result1 = await paymentService.processPayment({ id: '1', amount: 10 });
    expect(result1.transactionId).toBe('TXN-1');

    await expect(paymentService.processPayment({ id: '2', amount: 20 }))
      .rejects.toThrow('Network error');

    const result3 = await paymentService.processPayment({ id: '3', amount: 30 });
    expect(result3.transactionId).toBe('TXN-3');
  });
});

// 模块Mock示例
describe('Module Mocking', () => {
  // 模拟整个模块
  jest.mock('../utils/email', () => ({
    sendEmail: jest.fn().mockResolvedValue({ messageId: 'mock-123' }),
    validateEmail: jest.fn().mockReturnValue(true)
  }));

  test('should use mocked module', async () => {
    const { sendEmail } = require('../utils/email');
    
    await sendEmail('to@example.com', 'subject', 'body');
    
    expect(sendEmail).toHaveBeenCalledWith(
      'to@example.com',
      'subject',
      'body'
    );
  });

  // 使用spy保留原实现
  test('should spy on method', () => {
    const calculator = {
      add: (a, b) => a + b,
      multiply: (a, b) => a * b
    };

    const addSpy = jest.spyOn(calculator, 'add');
    
    const result = calculator.add(2, 3);
    
    expect(result).toBe(5);  // 原实现仍然工作
    expect(addSpy).toHaveBeenCalledWith(2, 3);  // 可以验证调用
    
    addSpy.mockRestore();
  });
});
```

### 3. Java - Mockito

```java
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    
    @Mock
    private PaymentGateway paymentGateway;
    
    @Mock
    private InventoryService inventoryService;
    
    @Mock
    private NotificationService notificationService;
    
    @InjectMocks
    private OrderService orderService;
    
    @Test
    void shouldProcessOrderSuccessfully() {
        // Arrange
        Order order = new Order("ORD-001", 100.0, "USD");
        
        when(inventoryService.checkStock(any())).thenReturn(true);
        when(paymentGateway.charge(any()))
            .thenReturn(new PaymentResult(true, "TXN-123", null));
        
        // Act
        OrderResult result = orderService.process(order);
        
        // Assert - 验证状态
        assertTrue(result.isSuccess());
        assertEquals("TXN-123", result.getTransactionId());
        
        // Assert - 验证交互
        verify(inventoryService).checkStock(any());
        verify(paymentGateway).charge(argThat(charge -> 
            charge.getAmount() == 100.0 && 
            charge.getCurrency().equals("USD")
        ));
        verify(notificationService).sendOrderConfirmation(order);
    }
    
    @Test
    void shouldRollbackOnPaymentFailure() {
        // Arrange
        Order order = new Order("ORD-002", 200.0, "EUR");
        
        when(inventoryService.checkStock(any())).thenReturn(true);
        when(inventoryService.lockStock(any())).thenReturn(true);
        when(paymentGateway.charge(any()))
            .thenReturn(new PaymentResult(false, null, "Card declined"));
        
        // Act & Assert
        assertThrows(PaymentException.class, () -> orderService.process(order));
        
        // 验证回滚
        verify(inventoryService).releaseStock(order.getId());
        verify(notificationService, never()).sendOrderConfirmation(any());
    }
    
    @Test
    void shouldRetryOnTransientFailure() {
        Order order = new Order("ORD-003", 50.0, "USD");
        
        // 前两次失败，第三次成功
        when(paymentGateway.charge(any()))
            .thenReturn(new PaymentResult(false, null, "Network error"))
            .thenReturn(new PaymentResult(false, null, "Timeout"))
            .thenReturn(new PaymentResult(true, "TXN-789", null));
        
        OrderResult result = orderService.processWithRetry(order, 3);
        
        assertTrue(result.isSuccess());
        verify(paymentGateway, times(3)).charge(any());
    }
    
    @Test
    void shouldVerifyCallOrder() {
        Order order = new Order("ORD-004", 75.0, "GBP");
        
        when(inventoryService.checkStock(any())).thenReturn(true);
        when(paymentGateway.charge(any()))
            .thenReturn(new PaymentResult(true, "TXN-999", null));
        
        orderService.process(order);
        
        // 验证调用顺序
        InOrder inOrder = inOrder(inventoryService, paymentGateway);
        inOrder.verify(inventoryService).checkStock(any());
        inOrder.verify(paymentGateway).charge(any());
    }
    
    @Test
    void shouldHandleMultipleOrders() {
        // Arrange
        Order order1 = new Order("ORD-005", 100.0);
        Order order2 = new Order("ORD-006", 200.0);
        
        when(paymentGateway.charge(any()))
            .thenReturn(new PaymentResult(true, "TXN-001", null))
            .thenReturn(new PaymentResult(true, "TXN-002", null));
        
        // Act
        orderService.process(order1);
        orderService.process(order2);
        
        // Assert
        ArgumentCaptor<ChargeRequest> captor = ArgumentCaptor.forClass(ChargeRequest.class);
        verify(paymentGateway, times(2)).charge(captor.capture());
        
        List<ChargeRequest> captured = captor.getAllValues();
        assertEquals(100.0, captured.get(0).getAmount());
        assertEquals(200.0, captured.get(1).getAmount());
    }
    
    // Spy示例 - 部分Mock
    @Test
    void shouldSpyOnRealObject() {
        List<String> list = spy(new ArrayList<>());
        
        // 真实调用
        list.add("one");
        list.add("two");
        
        // 模拟特定方法
        when(list.size()).thenReturn(100);
        
        assertEquals(100, list.size());  // Mock返回值
        assertEquals("one", list.get(0));  // 真实值
        verify(list).add("one");
    }
}
```

### 4. 手动实现Mock

```python
class ManualMockExamples:
    """手动实现测试替身"""
    
    class StubPaymentGateway:
        """Stub - 返回固定响应"""
        def __init__(self, should_succeed=True):
            self.should_succeed = should_succeed
        
        def charge(self, amount, currency):
            if self.should_succeed:
                return PaymentResult(
                    success=True,
                    transaction_id=f"stub_txn_{int(time.time())}",
                    error=None
                )
            return PaymentResult(
                success=False,
                transaction_id=None,
                error="Payment declined"
            )
    
    class SpyEmailService:
        """Spy - 记录调用信息"""
        def __init__(self):
            self.sent_emails = []
        
        def send(self, to, subject, body):
            self.sent_emails.append({
                'to': to,
                'subject': subject,
                'body': body,
                'timestamp': datetime.now()
            })
            return {'status': 'sent', 'message_id': f'msg_{len(self.sent_emails)}'}
        
        def was_email_sent_to(self, email):
            return any(e['to'] == email for e in self.sent_emails)
        
        def get_sent_count(self):
            return len(self.sent_emails)
    
    class FakeUserRepository:
        """Fake - 内存实现"""
        def __init__(self):
            self.users = {}
            self.next_id = 1
        
        def save(self, user):
            if not user.id:
                user.id = f"user_{self.next_id}"
                self.next_id += 1
            self.users[user.id] = user
            return user
        
        def find_by_id(self, user_id):
            return self.users.get(user_id)
        
        def find_by_email(self, email):
            return next(
                (u for u in self.users.values() if u.email == email),
                None
            )
        
        def delete(self, user_id):
            del self.users[user_id]
```

## 示例

### 完整示例：订单处理系统

```python
import pytest
from unittest.mock import Mock, patch, create_autospec
from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OrderProcessor:
    """订单处理器"""
    
    def __init__(self, payment_gateway, inventory_service, 
                 notification_service, analytics_service):
        self.payment = payment_gateway
        self.inventory = inventory_service
        self.notification = notification_service
        self.analytics = analytics_service
    
    def process_order(self, order):
        """处理订单完整流程"""
        try:
            # 1. 检查库存
            if not self.inventory.check_availability(order.items):
                raise InsufficientStockError("库存不足")
            
            # 2. 锁定库存
            lock_id = self.inventory.lock_stock(order.id, order.items)
            
            # 3. 处理支付
            payment_result = self.payment.process({
                'amount': order.total,
                'currency': order.currency,
                'order_id': order.id
            })
            
            if not payment_result.success:
                self.inventory.release_stock(lock_id)
                order.status = OrderStatus.FAILED
                self.notification.send_payment_failure(order.customer_email, payment_result.error)
                return OrderResult.failed(payment_result.error)
            
            # 4. 确认库存扣减
            self.inventory.confirm_deduction(lock_id)
            
            # 5. 更新订单状态
            order.status = OrderStatus.PAID
            order.payment_id = payment_result.transaction_id
            order.paid_at = datetime.now()
            
            # 6. 发送确认通知
            self.notification.send_order_confirmation(order)
            
            # 7. 记录分析数据
            self.analytics.track_order_completed(order)
            
            return OrderResult.success(order.payment_id)
            
        except Exception as e:
            order.status = OrderStatus.FAILED
            self.analytics.track_order_failed(order, str(e))
            raise


class TestOrderProcessor:
    """订单处理器测试"""
    
    @pytest.fixture
    def processor(self):
        """创建带有Mock依赖的处理器"""
        return OrderProcessor(
            payment_gateway=Mock(),
            inventory_service=Mock(),
            notification_service=Mock(),
            analytics_service=Mock()
        )
    
    @pytest.fixture
    def sample_order(self):
        """示例订单"""
        return Order(
            id="ORD-2024-001",
            items=[{"sku": "ITEM-1", "qty": 2}],
            total=199.99,
            currency="USD",
            customer_email="customer@example.com"
        )
    
    def test_successful_order_processing(self, processor, sample_order):
        """测试成功订单处理"""
        # 设置Mock行为
        processor.inventory.check_availability.return_value = True
        processor.inventory.lock_stock.return_value = "LOCK-123"
        processor.payment.process.return_value = Mock(
            success=True,
            transaction_id="TXN-456"
        )
        
        # 执行
        result = processor.process_order(sample_order)
        
        # 验证结果
        assert result.success is True
        assert result.transaction_id == "TXN-456"
        assert sample_order.status == OrderStatus.PAID
        
        # 验证调用序列
        processor.inventory.check_availability.assert_called_once_with(sample_order.items)
        processor.inventory.lock_stock.assert_called_once_with(sample_order.id, sample_order.items)
        processor.payment.process.assert_called_once()
        processor.inventory.confirm_deduction.assert_called_once_with("LOCK-123")
        processor.notification.send_order_confirmation.assert_called_once_with(sample_order)
        processor.analytics.track_order_completed.assert_called_once_with(sample_order)
    
    def test_insufficient_stock(self, processor, sample_order):
        """测试库存不足场景"""
        processor.inventory.check_availability.return_value = False
        
        with pytest.raises(InsufficientStockError):
            processor.process_order(sample_order)
        
        # 验证没有后续调用
        processor.inventory.lock_stock.assert_not_called()
        processor.payment.process.assert_not_called()
    
    def test_payment_failure_with_rollback(self, processor, sample_order):
        """测试支付失败时的回滚"""
        processor.inventory.check_availability.return_value = True
        processor.inventory.lock_stock.return_value = "LOCK-789"
        processor.payment.process.return_value = Mock(
            success=False,
            error="Card declined",
            transaction_id=None
        )
        
        result = processor.process_order(sample_order)
        
        # 验证失败处理
        assert result.success is False
        assert result.error == "Card declined"
        
        # 验证回滚
        processor.inventory.release_stock.assert_called_once_with("LOCK-789")
        processor.notification.send_payment_failure.assert_called_once_with(
            sample_order.customer_email,
            "Card declined"
        )
        processor.inventory.confirm_deduction.assert_not_called()
    
    def test_analytics_tracking_on_exception(self, processor, sample_order):
        """测试异常时的分析追踪"""
        processor.inventory.check_availability.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            processor.process_order(sample_order)
        
        processor.analytics.track_order_failed.assert_called_once()
        call_args = processor.analytics.track_order_failed.call_args
        assert call_args[0][0] == sample_order
        assert "Database error" in call_args[0][1]


# 使用autospec确保Mock与真实接口一致
def test_with_autospec():
    """使用autospec确保接口兼容性"""
    from unittest.mock import create_autospec
    
    # 创建严格遵循接口的Mock
    payment_gateway = create_autospec(PaymentGateway, instance=True)
    payment_gateway.process.return_value = Mock(success=True)
    
    # 这会通过
    payment_gateway.process({'amount': 100})
    
    # 这会失败 - 方法不存在
    # payment_gateway.nonexistent_method()  # AttributeError
```

## 应用场景

### 1. 测试隔离

```python
# 隔离外部HTTP调用
@patch('requests.get')
def test_weather_service(mock_get):
    mock_get.return_value.json.return_value = {
        'temperature': 25,
        'humidity': 60
    }
    
    service = WeatherService()
    result = service.get_current('Beijing')
    
    assert result.temperature == 25
```

### 2. 模拟时间

```python
from freezegun import freeze_time

@freeze_time("2024-01-15 12:00:00")
def test_time_dependent_logic():
    result = calculate_expiry_date(days=7)
    assert result == datetime(2024, 1, 22, 12, 0, 0)
```

### 3. 数据库Mock

```python
@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    return Mock(
        query=Mock(return_value=Mock(
            filter=Mock(return_value=Mock(
                first=Mock(return_value=Mock(id=1, name="Test"))
            ))
        )),
        add=Mock(),
        commit=Mock()
    )
```

### 4. 并发测试

```python
from concurrent.futures import ThreadPoolExecutor

def test_concurrent_access():
    lock_mock = Mock()
    lock_mock.acquire.return_value = True
    
    with patch('threading.Lock', return_value=lock_mock):
        # 测试并发逻辑
        pass
```

## 面试要点

### 常见问题

**Q1: Mock和Stub的区别是什么？**

- **Stub**：关注状态，提供预设的返回值，用于替代真实对象
- **Mock**：关注行为，验证被测对象与依赖的交互方式

```python
# Stub - 提供数据
stub = StubRepository()
stub.find.return_value = User("test")

# Mock - 验证行为
mock = Mock()
service.process(mock)
mock.save.assert_called_once()
```

**Q2: 什么时候应该使用Mock，什么时候不应该？**

**应该Mock：**
- 外部依赖（HTTP、数据库、文件系统）
- 不确定性（随机、时间）
- 慢速操作
- 尚未实现的依赖

**不应该Mock：**
- 被测单元本身的逻辑
- 简单值对象
- 稳定的内部工具类
- 需要验证真实行为的场景

**Q3: 如何避免Mock过度？**

1. **遵循测试金字塔**：更多单元测试，更少集成测试，适量E2E测试
2. **真实优先**：能用真实对象就不用Mock
3. **契约测试**：验证服务间契约而非Mock具体行为
4. **集成测试补充**：Mock测试后要有集成测试验证

**Q4: Mock测试有哪些陷阱？**

- **误报**：Mock行为与实际不符，导致测试通过但生产失败
- **维护成本**：Mock过多导致测试脆弱
- **实现泄露**：测试知道太多实现细节
- **虚假信心**：高覆盖率但低有效性

**Q5: 如何验证Mock测试的有效性？**

- 契约测试验证接口一致性
- 集成测试验证真实交互
- 定期审查Mock与实际实现的差异

## 相关概念

### 相关测试技术

- [单元测试](unit-testing.md) - Mocking的主要应用场景
- [集成测试](integration-testing.md) - Mock的补充
- [测试替身](test-doubles.md) - Mocking的理论基础
- [依赖注入](dependency-injection.md) - 使Mocking更容易的设计模式

### 常用工具框架

| 语言 | 工具 | 特点 |
|------|------|------|
| Python | unittest.mock, pytest-mock | 标准库支持 |
| JavaScript | Jest, Sinon.js | 丰富的匹配器 |
| Java | Mockito, EasyMock | 类型安全 |
| C# | Moq, NSubstitute | 表达式树支持 |
| Go | gomock, testify | 代码生成 |
| Ruby | RSpec Mocks | DSL友好 |

### 设计模式

- **依赖注入**：使Mocking成为可能
- **接口隔离**：减少需要Mock的范围
- **工厂模式**：便于替换实现
- **适配器模式**：隔离外部依赖
