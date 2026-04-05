# 防腐层 (Anti-Corruption Layer)

## 简介

防腐层（Anti-Corruption Layer, ACL）是领域驱动设计（DDD）中的一个重要战术模式，用于隔离外部系统或遗留系统对领域模型的影响。它充当翻译和隔离层，确保外部模型的变化不会污染核心领域模型。

当系统集成外部服务、遗留系统或不同限界上下文时，防腐层保护领域模型的纯粹性，使领域模型免受外部概念和术语的污染。

## 核心概念

### 防腐层的职责

1. **模型转换**：将外部模型转换为领域模型，反之亦然
2. **协议转换**：处理不同的通信协议和数据格式
3. **错误隔离**：防止外部系统的错误传播到领域层
4. **概念隔离**：阻止外部术语渗透到 ubiquitous language 中

### 何时使用防腐层

- 集成遗留系统
- 调用第三方服务
- 与其他限界上下文交互（下游保护上游模型）
- 防止技术债务污染领域模型

### 防腐层的位置

```
┌─────────────────────────────────────────────────────────┐
│                    限界上下文 A                          │
│  ┌──────────────┐    ┌──────────┐    ┌──────────────┐  │
│  │   领域层      │◄───│  防腐层   │◄───│ 外部系统/    │  │
│  │  (Domain)    │    │   (ACL)  │    │ 限界上下文 B │  │
│  └──────────────┘    └──────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 实现方式

### 基础防腐层结构

```python
from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic

T = TypeVar('T')  # 领域模型类型
S = TypeVar('S')  # 外部模型类型

class ExternalServiceClient(ABC):
    """外部服务客户端接口"""
    
    @abstractmethod
    def fetch_data(self, identifier: str) -> dict:
        """从外部服务获取数据"""
        pass

class AntiCorruptionLayer(ABC, Generic[T, S]):
    """防腐层抽象基类"""
    
    @abstractmethod
    def to_domain_model(self, external_data: S) -> T:
        """将外部模型转换为领域模型"""
        pass
    
    @abstractmethod
    def from_domain_model(self, domain_model: T) -> S:
        """将领域模型转换为外部模型"""
        pass

class CustomerACL(AntiCorruptionLayer[Customer, ExternalCustomer]):
    """客户防腐层示例"""
    
    def __init__(self, external_client: ExternalServiceClient):
        self._client = external_client
    
    def to_domain_model(self, external_data: dict) -> Customer:
        """转换外部客户数据为领域客户"""
        # 处理字段名差异
        external_id = external_data.get('cust_id') or external_data.get('id')
        full_name = external_data.get('fullName') or \
                    f"{external_data.get('firstName', '')} {external_data.get('lastName', '')}"
        
        # 处理状态码映射
        status_map = {
            'A': CustomerStatus.ACTIVE,
            'I': CustomerStatus.INACTIVE,
            'S': CustomerStatus.SUSPENDED,
            'active': CustomerStatus.ACTIVE,
            'inactive': CustomerStatus.INACTIVE
        }
        external_status = external_data.get('status', 'I')
        status = status_map.get(external_status, CustomerStatus.INACTIVE)
        
        # 处理地址嵌套结构差异
        address_data = external_data.get('address', {})
        address = Address(
            street=address_data.get('street_line_1', ''),
            city=address_data.get('city', ''),
            postal_code=address_data.get('zip', address_data.get('postalCode', ''))
        )
        
        return Customer(
            customer_id=external_id,
            name=full_name.strip(),
            email=external_data.get('emailAddress', external_data.get('email', '')),
            status=status,
            address=address
        )
    
    def from_domain_model(self, customer: Customer) -> dict:
        """转换领域客户为外部格式"""
        return {
            'cust_id': customer.customer_id,
            'fullName': customer.name,
            'emailAddress': customer.email,
            'status': 'A' if customer.status == CustomerStatus.ACTIVE else 'I',
            'address': {
                'street_line_1': customer.address.street,
                'city': customer.address.city,
                'zip': customer.address.postal_code
            }
        }
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """获取客户（封装外部调用）"""
        try:
            external_data = self._client.fetch_data(customer_id)
            return self.to_domain_model(external_data)
        except ExternalServiceError as e:
            # 错误隔离：转换外部错误为领域错误
            raise CustomerNotFoundException(
                f"Customer {customer_id} not found in external system"
            ) from e
```

### 完整的防腐层实现

```python
class LegacyInventoryACL:
    """遗留库存系统防腐层"""
    
    def __init__(self, legacy_api: LegacyInventoryAPI):
        self._legacy_api = legacy_api
        self._cache = {}  # 本地缓存减少外部调用
    
    def check_availability(self, sku: str, quantity: int) -> bool:
        """检查库存可用性"""
        try:
            # 调用遗留系统API
            legacy_response = self._legacy_api.query_stock(sku)
            
            # 解析遗留格式
            available = self._parse_legacy_stock(legacy_response)
            
            return available >= quantity
            
        except LegacyAPIException as e:
            # 记录外部错误，抛出领域友好的异常
            logger.error(f"Legacy inventory API error: {e}")
            raise InventoryServiceUnavailable(
                "Unable to check inventory at this time"
            ) from e
    
    def reserve_stock(self, sku: str, quantity: int) -> Reservation:
        """预留库存"""
        try:
            # 转换领域概念为遗留系统概念
            legacy_request = {
                'productCode': sku,
                'amount': quantity,
                'operation': 'HOLD'
            }
            
            legacy_response = self._legacy_api.reserve(legacy_request)
            
            # 转换响应
            return Reservation(
                reservation_id=legacy_response['hold_id'],
                sku=sku,
                quantity=quantity,
                expires_at=self._parse_legacy_datetime(
                    legacy_response['expiry_date']
                )
            )
            
        except LegacyAPIException as e:
            logger.error(f"Failed to reserve stock: {e}")
            raise StockReservationFailed(
                f"Could not reserve {quantity} units of {sku}"
            ) from e
    
    def _parse_legacy_stock(self, response: dict) -> int:
        """解析遗留系统的库存格式"""
        # 遗留系统可能返回多种格式
        if 'current_stock' in response:
            return int(response['current_stock'])
        elif 'qty_available' in response:
            return int(response['qty_available'])
        elif 'inventory' in response:
            return int(response['inventory']['on_hand'])
        else:
            raise ValueError(f"Unknown legacy response format: {response}")
    
    def _parse_legacy_datetime(self, date_str: str) -> datetime:
        """解析遗留系统的时间格式"""
        # 处理多种日期格式
        formats = ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %I:%M %p', '%Y%m%d%H%M%S']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")
```

## 示例

### 第三方支付系统防腐层

```python
class PaymentProviderACL:
    """支付提供商防腐层"""
    
    def __init__(self, provider: PaymentProvider):
        self._provider = provider
    
    def process_payment(self, payment: Payment) -> PaymentResult:
        """处理支付"""
        # 转换领域支付对象为提供商格式
        provider_request = self._adapt_payment_request(payment)
        
        try:
            # 调用外部API
            provider_response = self._provider.charge(provider_request)
            
            # 转换响应
            return self._adapt_payment_response(provider_response)
            
        except ProviderError as e:
            # 统一错误处理
            error_type = self._classify_error(e)
            raise PaymentProcessingException(
                message="Payment processing failed",
                error_type=error_type,
                original_error=e
            )
    
    def _adapt_payment_request(self, payment: Payment) -> dict:
        """适配支付请求"""
        return {
            'amount': {
                'value': float(payment.amount),
                'currency': payment.currency.value
            },
            'payment_method': {
                'type': self._map_payment_method(payment.method),
                'details': self._extract_method_details(payment.method)
            },
            'metadata': {
                'order_id': payment.order_id,
                'customer_id': payment.customer_id
            }
        }
    
    def _adapt_payment_response(self, response: dict) -> PaymentResult:
        """适配支付响应"""
        status_map = {
            'succeeded': PaymentStatus.COMPLETED,
            'pending': PaymentStatus.PENDING,
            'failed': PaymentStatus.FAILED,
            'cancelled': PaymentStatus.CANCELLED
        }
        
        return PaymentResult(
            transaction_id=response['transaction_id'],
            status=status_map.get(response['status'], PaymentStatus.UNKNOWN),
            amount=Decimal(str(response['amount']['value'])),
            processed_at=datetime.fromisoformat(response['processed_at']),
            provider_reference=response['reference']
        )
    
    def _map_payment_method(self, method: PaymentMethod) -> str:
        """映射支付方式"""
        mapping = {
            CreditCard: 'card',
            PayPal: 'paypal',
            BankTransfer: 'bank_transfer'
        }
        return mapping.get(type(method), 'unknown')
    
    def _classify_error(self, error: ProviderError) -> PaymentErrorType:
        """分类错误类型"""
        if error.code == 'insufficient_funds':
            return PaymentErrorType.INSUFFICIENT_FUNDS
        elif error.code == 'card_declined':
            return PaymentErrorType.CARD_DECLINED
        elif error.code == 'network_error':
            return PaymentErrorType.NETWORK_ERROR
        else:
            return PaymentErrorType.UNKNOWN
```

## 应用场景

### 必须使用防腐层的场景

1. **遗留系统集成**：旧系统使用过时技术栈
2. **第三方服务**：API可能变化，需要隔离
3. **多团队协作**：保护领域模型免受其他团队影响
4. **数据迁移期间**：新旧系统并行运行时

### 防腐层的复杂度考量

| 场景 | 复杂度 | 建议 |
|-----|-------|-----|
| 简单数据查询 | 低 | 简单转换函数即可 |
| 复杂双向同步 | 高 | 完整ACL + 同步机制 |
| 实时交互 | 中 | ACL + 缓存策略 |
| 批量集成 | 中 | ACL + 批处理优化 |

## 面试要点

**Q: 防腐层和适配器模式有什么区别？**
A: 适配器模式主要解决接口不兼容问题，而防腐层更强调概念隔离和模型保护。防腐层不仅做技术转换，还防止外部概念渗透到领域语言中。

**Q: 防腐层应该放在哪个架构层？**
A: 防腐层通常位于基础设施层或作为独立层，但紧挨着需要保护的上限界上下文。它向下连接外部系统，向上提供领域友好的接口。

**Q: 如何处理防腐层中的错误？**
A: 推荐做法：
- 捕获所有外部异常
- 记录详细错误信息（用于调试）
- 转换为领域友好的异常
- 考虑熔断和降级策略

**Q: 防腐层会影响性能吗？如何优化？**
A: 是的，额外的转换层会增加开销。优化策略：
- 使用缓存减少外部调用
- 异步处理非关键同步
- 批量转换减少往返

## 相关概念

### 数据结构
- [适配器模式](../design-patterns/structural/adapter.md) - 接口转换基础

### 算法
- [数据转换](../computer-science/algorithms/data-transformation.md) - 模型映射算法

### 复杂度分析
- [集成复杂度](../system-design/integration-complexity.md) - 系统间集成复杂度

### 系统实现
- [限界上下文](./bounded-context.md) - 防腐层保护的边界
- [领域服务](./domain-services.md) - 使用防腐层的客户端
- [集成模式](../system-design/integration-patterns.md) - 系统集成最佳实践
