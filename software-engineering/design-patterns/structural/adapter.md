## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概念 (Concept)

**适配器模式 (Adapter Pattern)** 是一种结构型设计模式，它允许不兼容接口的对象能够相互合作。适配器将某个类的接口转换成客户端期望的另一个接口。

适配器模式就像现实生活中的电源适配器 - 不同国家的插座标准不同，通过适配器可以让电器在不同标准下工作。

```
┌─────────────────────────────────────────────────────────────┐
│                     适配器模式                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Client ──────▶ Target (interface)                         │
│   (期望接口)        ├─ request()                            │
│                     │                                       │
│                     ▼                                       │
│               ┌─────────────┐      ┌─────────────┐          │
│               │   Adapter   │─────▶│   Adaptee   │          │
│               │  (适配器)   │      │ (被适配者)  │          │
│               └─────────────┘      │ specificRequest()      │
│                                    └─────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 设计原则 (Principle)

适配器模式遵循以下设计原则：

1. **开闭原则 (Open/Closed Principle)**：使用适配器可以在不修改现有代码的情况下引入新功能
2. **单一职责原则 (Single Responsibility Principle)**：将接口转换逻辑与业务逻辑分离
3. **解耦 (Decoupling)**：客户端与具体实现解耦，只依赖于目标接口

**两种实现方式**：
- **对象适配器**：通过组合 (composition) 持有被适配者实例（更灵活，推荐）
- **类适配器**：通过继承 (inheritance) 实现（需要多重继承支持，如C++）

---

## 实现示例 (Example)

### 1. 对象适配器（Python推荐方式）

```python
from abc import ABC, abstractmethod

# 目标接口 - 客户端期望的接口
class MediaPlayer(ABC):
    @abstractmethod
    def play(self, filename: str) -> str:
        pass

# 被适配者 - 已存在的接口
class AdvancedMediaPlayer:
    """高级媒体播放器 - 只支持特定格式"""
    
    def play_mp4(self, filename: str) -> str:
        return f"Playing mp4 file: {filename}"
    
    def play_vlc(self, filename: str) -> str:
        return f"Playing vlc file: {filename}"
    
    def play_mkv(self, filename: str) -> str:
        return f"Playing mkv file: {filename}"

# 适配器
class MediaAdapter(MediaPlayer):
    """媒体适配器 - 将高级播放器适配为统一接口"""
    
    def __init__(self):
        self.advanced_player = AdvancedMediaPlayer()
    
    def play(self, filename: str) -> str:
        """统一播放接口"""
        if filename.endswith('.mp4'):
            return self.advanced_player.play_mp4(filename)
        elif filename.endswith('.vlc'):
            return self.advanced_player.play_vlc(filename)
        elif filename.endswith('.mkv'):
            return self.advanced_player.play_mkv(filename)
        else:
            return f"Unsupported format: {filename}"

# 客户端代码
class AudioPlayer(MediaPlayer):
    """音频播放器 - 支持MP3，其他格式使用适配器"""
    
    def __init__(self):
        self.adapter = None
    
    def play(self, filename: str) -> str:
        if filename.endswith('.mp3'):
            return f"Playing mp3 file: {filename}"
        
        # 使用适配器播放其他格式
        self.adapter = MediaAdapter()
        return self.adapter.play(filename)

# 使用示例
player = AudioPlayer()

print(player.play("song.mp3"))       # 原生支持
print(player.play("movie.mp4"))      # 通过适配器
print(player.play("video.vlc"))      # 通过适配器
print(player.play("hd_video.mkv"))   # 通过适配器
```

### 2. 第三方API适配器

```python
# 旧版支付系统接口（已存在）
class LegacyPaymentSystem:
    """旧版支付系统"""
    
    def make_payment(self, amount_in_cents: int, currency_code: str) -> dict:
        """金额以分为单位"""
        return {
            "success": True,
            "transaction_id": f"LEGACY_{amount_in_cents}_{currency_code}",
            "amount": amount_in_cents,
            "currency": currency_code
        }

# 新版支付接口（期望的接口）
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float, currency: str) -> dict:
        """金额以元为单位"""
        pass

# 适配器
class LegacyPaymentAdapter(PaymentProcessor):
    """将旧版支付系统适配为新版接口"""
    
    def __init__(self):
        self.legacy_system = LegacyPaymentSystem()
    
    def process_payment(self, amount: float, currency: str) -> dict:
        """新版接口 - 转换为旧版调用"""
        # 转换金额：元 → 分
        amount_in_cents = int(amount * 100)
        
        # 转换货币代码
        currency_map = {
            "CNY": "RMB",
            "USD": "USD",
            "EUR": "EUR"
        }
        legacy_currency = currency_map.get(currency, currency)
        
        # 调用旧版系统
        result = self.legacy_system.make_payment(amount_in_cents, legacy_currency)
        
        # 转换返回结果格式
        return {
            "status": "success" if result["success"] else "failed",
            "transaction_id": result["transaction_id"],
            "amount": amount,
            "currency": currency,
            "processor": "legacy"
        }

# 使用 - 客户端使用统一接口
class CheckoutService:
    """结账服务 - 使用新版接口"""
    
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor
    
    def checkout(self, order_total: float, currency: str = "CNY"):
        print(f"Processing checkout: {order_total} {currency}")
        result = self.payment_processor.process_payment(order_total, currency)
        print(f"Payment result: {result}")
        return result

# 客户端代码 - 可以无缝切换新旧支付系统
legacy_adapter = LegacyPaymentAdapter()
checkout = CheckoutService(legacy_adapter)
checkout.checkout(99.99, "CNY")
```

### 3. 数据结构适配器

```python
# 第三方库的数据结构（假设）
class ThirdPartyDataSource:
    """第三方数据源 - 返回XML格式"""
    
    def fetch_data(self) -> str:
        return """
        <users>
            <user>
                <name>张三</name>
                <age>30</age>
            </user>
            <user>
                <name>李四</name>
                <age>25</age>
            </user>
        </users>
        """

# 目标接口
class UserRepository(ABC):
    @abstractmethod
    def get_all_users(self) -> list:
        pass

# 适配器
class XmlToJsonAdapter(UserRepository):
    """将XML数据源适配为JSON接口"""
    
    def __init__(self, data_source: ThirdPartyDataSource):
        self.data_source = data_source
    
    def get_all_users(self) -> list:
        """返回JSON格式的用户列表"""
        import xml.etree.ElementTree as ET
        
        xml_data = self.data_source.fetch_data()
        root = ET.fromstring(xml_data)
        
        users = []
        for user_elem in root.findall('user'):
            user = {
                "name": user_elem.find('name').text,
                "age": int(user_elem.find('age').text)
            }
            users.append(user)
        
        return users

# 使用
xml_source = ThirdPartyDataSource()
adapter = XmlToJsonAdapter(xml_source)
users = adapter.get_all_users()
print(f"Users: {users}")
```

---

## 使用场景 (Use Cases)

| 场景 | 说明 |
|------|------|
| 遗留系统集成 | 将旧系统接口适配为新接口 |
| 第三方库集成 | 统一不同库的接口风格 |
| 数据格式转换 | XML↔JSON、Protocol Buffers等转换 |
| 跨平台兼容 | 不同操作系统API的统一封装 |
| 标准适配 | 不同行业标准之间的转换 |

---

## 面试要点 (Interview Points)

**Q1: 适配器模式和装饰器模式的区别？**

> - **适配器模式**：改变接口以匹配客户端期望，目的是接口兼容
> - **装饰器模式**：保持接口不变，动态添加功能，目的是功能增强
>
> 适配器是"翻译官"，装饰器是"增强器"。

**Q2: 对象适配器和类适配器的区别？**

> - **对象适配器**：通过组合持有被适配者，更灵活，可以适配多个对象
> - **类适配器**：通过继承实现，需要多重继承支持，只能适配一个类
>
> Python/Java 推荐使用对象适配器。

**Q3: 适配器模式和代理模式的区别？**

> 适配器改变接口使其兼容；代理模式保持相同接口，控制访问（如权限检查、延迟加载）。适配器解决"接口不匹配"问题，代理解决"访问控制"问题。

**Q4: 实际项目中如何使用适配器模式？**

> 典型场景：
> 1. 整合遗留系统时保持新接口不变
> 2. 统一多个第三方SDK的调用方式
> 3. 实现多数据库支持（统一JDBC接口）
> 4. API版本兼容（v1/v2适配）

---

## 相关引用 (References)

- 返回：[设计模式总览](../../design-patterns.md)
- 相关：[装饰器模式](./decorator.md) - 动态添加功能
- 相关：[代理模式](./proxy.md) - 控制对象访问
- 原理：[SOLID原则](../../solid-principles.md)
