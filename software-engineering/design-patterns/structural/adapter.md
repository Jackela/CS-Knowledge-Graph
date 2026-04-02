# 适配器模式 (Adapter Pattern)

## 概念

适配器模式（Adapter Pattern）是一种**结构型设计模式**，它允许将一个类的接口转换成客户希望的另一个接口。适配器让原本接口不兼容的类可以一起工作。

> **核心思想**: 通过引入一个中间层（适配器）来解决接口不兼容的问题，无需修改原有代码。

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│     Client      │────────▶│  Target(目标)   │◀────────│    Adapter      │
│                 │         │  接口           │         │  (适配器)       │
└─────────────────┘         └─────────────────┘         └────────┬────────┘
                                                                 │
                                                                 │ 继承/组合
                                                                 ▼
                                                          ┌──────────────┐
                                                          │ Adaptee      │
                                                          │ (被适配者)    │
                                                          └──────────────┘
```

---

## 原理

### 为什么需要适配器模式？

1. **遗留系统集成**: 复用已有类，但其接口不符合新系统要求
2. **第三方库集成**: 集成外部库时接口不匹配
3. **版本兼容**: 新老版本接口不兼容
4. **接口统一**: 统一多个不兼容类的接口

### 两种实现方式

| 方式 | 特点 | 适用场景 |
|------|------|----------|
| 类适配器 | 使用继承 | 需要重写部分方法时 |
| 对象适配器 | 使用组合 | 更灵活，推荐方式 |

### 优缺点

**优点：**
- 符合开闭原则，无需修改原有代码
- 提高类的复用性
- 灵活性和扩展性好

**缺点：**
- 增加系统的复杂性
- 过多的适配器会使系统难以理解

---

## 实现方式

### 1. 对象适配器（组合方式）

```python
from abc import ABC, abstractmethod


# 目标接口
class MediaPlayer(ABC):
    @abstractmethod
    def play(self, filename: str):
        pass


# 被适配者 - 高级媒体播放器
class AdvancedMediaPlayer(ABC):
    @abstractmethod
    def play_vlc(self, filename: str):
        pass
    
    @abstractmethod
    def play_mp4(self, filename: str):
        pass


class VlcPlayer(AdvancedMediaPlayer):
    def play_vlc(self, filename: str):
        print(f"播放 VLC 文件: {filename}")
    
    def play_mp4(self, filename: str):
        pass


class Mp4Player(AdvancedMediaPlayer):
    def play_vlc(self, filename: str):
        pass
    
    def play_mp4(self, filename: str):
        print(f"播放 MP4 文件: {filename}")


# 适配器
class MediaAdapter(MediaPlayer):
    def __init__(self, audio_type: str):
        self.audio_type = audio_type.lower()
        if audio_type == "vlc":
            self.advanced_player = VlcPlayer()
        elif audio_type == "mp4":
            self.advanced_player = Mp4Player()
    
    def play(self, filename: str):
        if self.audio_type == "vlc":
            self.advanced_player.play_vlc(filename)
        elif self.audio_type == "mp4":
            self.advanced_player.play_mp4(filename)


# 客户端
class AudioPlayer(MediaPlayer):
    def __init__(self):
        self.adapter = None
    
    def play(self, filename: str):
        audio_type = filename.split('.')[-1].lower()
        
        # 原生支持的格式
        if audio_type == "mp3":
            print(f"播放 MP3 文件: {filename}")
        # 需要适配的格式
        elif audio_type in ["vlc", "mp4"]:
            self.adapter = MediaAdapter(audio_type)
            self.adapter.play(filename)
        else:
            print(f"不支持的音频格式: {audio_type}")


# 使用
player = AudioPlayer()
player.play("song.mp3")      # 原生支持
player.play("movie.vlc")     # 通过适配器
player.play("video.mp4")     # 通过适配器
```

### 2. 类适配器（继承方式）

```python
from abc import ABC, abstractmethod


# 目标接口
class Target(ABC):
    @abstractmethod
    def request(self):
        pass


# 被适配者
class Adaptee:
    def specific_request(self):
        return "被适配者的特殊请求"


# 类适配器 - 通过继承实现
class ClassAdapter(Target, Adaptee):
    def request(self):
        # 调用父类的方法并转换
        return f"适配器转换: {self.specific_request()}"


# 使用
adapter = ClassAdapter()
print(adapter.request())  # 适配器转换: 被适配者的特殊请求
```

### 3. Java 实现示例

```java
// 目标接口
public interface Target {
    void request();
}

// 被适配者
public class Adaptee {
    public void specificRequest() {
        System.out.println("被适配者的特殊请求");
    }
}

// 对象适配器（推荐）
public class ObjectAdapter implements Target {
    private Adaptee adaptee;
    
    public ObjectAdapter(Adaptee adaptee) {
        this.adaptee = adaptee;
    }
    
    @Override
    public void request() {
        System.out.println("适配器转换中...");
        adaptee.specificRequest();
    }
}

// 类适配器（多重继承）
public class ClassAdapter extends Adaptee implements Target {
    @Override
    public void request() {
        System.out.println("适配器转换中...");
        specificRequest();
    }
}

// 使用
public class Client {
    public static void main(String[] args) {
        // 对象适配器方式
        Adaptee adaptee = new Adaptee();
        Target target = new ObjectAdapter(adaptee);
        target.request();
        
        // 类适配器方式
        Target target2 = new ClassAdapter();
        target2.request();
    }
}
```

---

## 示例

### 电源适配器

```python
from abc import ABC, abstractmethod


# 目标接口 - 中国标准插座
class ChineseSocket(ABC):
    @abstractmethod
    def provide_power(self):
        pass


# 被适配者 - 美国电器
class USElectricalDevice:
    def __init__(self, name: str):
        self.name = name
    
    def use_110v_power(self):
        return f"{self.name} 使用 110V 电压运行"


# 被适配者 - 欧洲电器
class EuropeanElectricalDevice:
    def __init__(self, name: str):
        self.name = name
    
    def use_220v_power(self):
        return f"{self.name} 使用 220V 电压运行"


# 电源适配器 - 电压转换
class PowerAdapter(ChineseSocket):
    def __init__(self, device):
        self.device = device
    
    def provide_power(self):
        if isinstance(self.device, USElectricalDevice):
            print("适配器: 220V -> 110V 降压转换")
            return self.device.use_110v_power()
        elif isinstance(self.device, EuropeanElectricalDevice):
            print("适配器: 电压兼容，直接供电")
            return self.device.use_220v_power()
        else:
            return "不支持的设备类型"


# 中国家庭
class ChineseHome:
    def __init__(self):
        self.socket = None
    
    def plug_in(self, socket: ChineseSocket):
        self.socket = socket
        print(self.socket.provide_power())


# 使用场景
home = ChineseHome()

# 使用美国电器
us_laptop = USElectricalDevice("MacBook Pro")
adapter1 = PowerAdapter(us_laptop)
home.plug_in(adapter1)
# 输出:
# 适配器: 220V -> 110V 降压转换
# MacBook Pro 使用 110V 电压运行

# 使用欧洲电器
eu_kettle = EuropeanElectricalDevice("Philips 电水壶")
adapter2 = PowerAdapter(eu_kettle)
home.plug_in(adapter2)
# 输出:
# 适配器: 电压兼容，直接供电
# Philips 电水壶 使用 220V 电压运行
```

### UML 图

```
┌─────────────────────────────────────────────────────────────────┐
│                         适配器模式示例                          │
│                      （电源适配器场景）                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐                                           │
│  │  <<interface>>  │                                           │
│  │  ChineseSocket  │◀─────────────────────────────────┐        │
│  │  +provide_power()│                                 │        │
│  └─────────────────┘                                 │        │
│           ▲                                          │        │
│           │ implements                               │        │
│           │                                          │        │
│  ┌─────────────────┐      ┌─────────────────┐       │        │
│  │   PowerAdapter  │──────│    device       │       │        │
│  │  -device        │      │  (Adaptee)      │       │        │
│  │  +provide_power()│     └─────────────────┘       │        │
│  └─────────────────┘              ▲                 │        │
│                                   │                 │        │
│                    ┌──────────────┴──────────┐      │        │
│                    │                         │      │        │
│           ┌────────▼────────┐      ┌────────▼──────┴─┐       │
│           │USElectricalDevice│      │EuropeanElectrical│      │
│           │ +use_110v_power() │      │Device            │      │
│           └─────────────────┘      │ +use_220v_power() │      │
│                                    └─────────────────┘       │
│                                                                 │
│  ┌─────────────────┐                                           │
│  │   ChineseHome   │                                           │
│  │  -socket        │                                           │
│  │  +plug_in()     │                                           │
│  └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

1. **Q: 什么是适配器模式？**
   
   A: 适配器模式是一种结构型设计模式，用于将一个类的接口转换成客户端希望的另一个接口。它解决了接口不兼容的问题，使得原本无法一起工作的类能够协同工作。

2. **Q: 类适配器和对象适配器的区别？**
   
   A: 类适配器使用多重继承（Python/Java 8 接口默认方法），在编译时确定适配关系，可以重写被适配者的方法；对象适配器使用组合关系，更加灵活，可以在运行时动态适配不同的被适配者对象，是更推荐的方式。

3. **Q: 适配器模式与装饰器模式的区别？**
   
   A: 适配器模式目的是**接口转换**，使不兼容的接口能够协同工作；装饰器模式目的是**增强功能**，在不改变原有接口的情况下添加新功能。适配器改变接口，装饰器保持接口。

4. **Q: 实际应用场景有哪些？**
   
   A: 常见场景包括：
   - 集成第三方库或 API 时接口不匹配
   - 系统升级时兼容旧版本接口
   - 不同数据库驱动的统一封装（JDBC）
   - 各种转接头（电源适配器、HDMI 转 VGA 等）

5. **Q: 适配器模式和代理模式的区别？**
   
   A: 适配器模式改变对象的接口以兼容客户端；代理模式保持接口不变，控制对对象的访问。适配器关注的是接口转换，代理关注的是访问控制。

---

## 相关概念

### 数据结构
- [接口与抽象类](../../oop-design.md) - 多态实现的基础
- [Hash Table](../../../computer-science/data-structures/hash-table.md) - 适配器缓存实现

### 算法
- [字符串匹配](../../../computer-science/algorithms/string-matching.md) - 数据格式转换

### 复杂度分析
- [时间复杂度](../../../references/time-complexity.md) - 适配器调用开销分析
- [空间复杂度](../../../references/space-complexity.md) - 适配器对象内存占用

### 系统实现
- [数据库连接池](../../../computer-science/databases/indexing.md) - JDBC 驱动适配
- [网络协议](../../../computer-science/systems/network.md) - 协议转换层

### 设计模式
- [装饰器模式](./decorator.md) - 功能增强而非接口转换
- [桥接模式](./bridge.md) - 抽象与实现的分离
- [代理模式](./proxy.md) - 访问控制而非接口转换
- [外观模式](./facade.md) - 简化接口而非转换接口


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

## 相关概念 (Related Concepts)

适配器模式与其他设计模式和软件工程概念密切相关：

### 结构型模式（Structural Patterns）

与其他结构型模式一样，适配器模式关注如何组合类和对象以形成更大的结构：

- [桥接模式](./bridge.md) - 将抽象与实现分离，两者独立变化；适配器解决接口不兼容，桥接解决多维变化
- [组合模式](./composite.md) - 统一单个对象和组合对象的接口；适配器也可用于统一不同组件的接口
- [装饰器模式](./decorator.md) - 动态地给对象添加职责（功能增强）；适配器改变接口形式（接口转换）
- [外观模式](./facade.md) - 为子系统提供统一的高层接口；适配器为特定类提供接口转换
- [享元模式](./flyweight.md) - 共享细粒度对象以节省内存；与适配器都涉及对象复用但目的不同
- [代理模式](./proxy.md) - 控制对象的访问；适配器改变对象的接口，代理保持接口不变

### 设计原则与架构

- [SOLID原则](../../solid-principles.md) - 适配器模式体现开闭原则和单一职责原则
- [设计模式总览](../../design-patterns.md) - 查看所有设计模式的分类与关系

### 相关设计模式

- [单例模式](../creational/singleton.md) - 适配器对象常设计为单例以复用
- [工厂模式](../creational/factory.md) - 工厂可创建不同类型的适配器实例

#### 计算机科学基础

- 数据结构接口设计 - 不同数据结构的统一访问接口
- [队列与栈适配](../../../computer-science/data-structures/queue.md) - 双端队列作为栈和队列的适配器
- [树结构遍历适配](../../../computer-science/data-structures/tree.md) - 统一不同树结构的遍历接口

---

## 相关引用 (References)

- 返回：
- 相关： - 动态添加功能
- 相关： - 控制对象访问
