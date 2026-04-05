# 设计模式 (Design Patterns)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、GoF经典著作及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**设计模式 (Design Patterns)** 是在软件设计中反复出现的问题的解决方案。它们是被反复使用、经过分类编目、代码设计经验的总结。使用设计模式是为了可重用代码、让代码更容易被他人理解、保证代码可靠性。

```
┌─────────────────────────────────────────────────────────────────┐
│                      设计模式分类                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   创建型 (Creational)        结构型 (Structural)               │
│   ├─ 单例 (Singleton)        ├─ 适配器 (Adapter)               │
│   ├─ 工厂 (Factory)          ├─ 装饰器 (Decorator)             │
│   ├─ 抽象工厂                 ├─ 代理 (Proxy)                  │
│   ├─ 建造者 (Builder)        ├─ 外观 (Facade)                 │
│   └─ 原型 (Prototype)        ├─ 桥接 (Bridge)                 │
│                              ├─ 组合 (Composite)               │
│   行为型 (Behavioral)        └─ 享元 (Flyweight)               │
│   ├─ 观察者 (Observer)                                        │
│   ├─ 策略 (Strategy)                                          │
│   ├─ 命令 (Command)                                           │
│   ├─ 模板方法                                                 │
│   ├─ 迭代器 (Iterator)                                        │
│   ├─ 状态 (State)                                             │
│   ├─ 责任链                                                   │
│   ├─ 访问者 (Visitor)                                         │
│   └─ 中介者 (Mediator)                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 设计模式 vs 架构模式

| 特性 | 设计模式 | 架构模式 |
|------|----------|----------|
| 粒度 | 类/对象级别 | 子系统/系统级别 |
| 范围 | 单个组件内部 | 整个应用结构 |
| 示例 | 单例、工厂、观察者 | MVC、微服务、事件驱动 |
| 语言依赖 | 相对独立 | 技术栈相关 |

---

## 创建型模式 (Creational Patterns)

创建型模式关注对象的创建机制，试图以适当的方式创建对象。

### 1. 单例模式 (Singleton)

**意图**：确保一个类只有一个实例，并提供一个全局访问点。

```
┌─────────────────────────────────────┐
│           Singleton                 │
├─────────────────────────────────────┤
│ - _instance: Singleton              │
├─────────────────────────────────────┤
│ + getInstance(): Singleton          │
│ + businessMethod()                  │
└─────────────────────────────────────┘
          │
          │ 唯一实例
          ▼
   ┌─────────────┐
   │  instance   │
   └─────────────┘
```

**Python实现**：

```python
class Singleton:
    """单例模式 - 线程安全实现"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                # 双重检查锁定
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

# 使用
s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True - 同一实例

# Pythonic方式 - 使用模块
# Python模块天然是单例
# config.py
class Config:
    setting = "value"
# 所有import config的地方共享同一对象
```

**使用场景**：
- 数据库连接池
- 配置管理器
- 日志记录器
- 缓存管理器

---

### 2. 工厂模式 (Factory)

**意图**：定义创建对象的接口，让子类决定实例化哪个类。

```
┌─────────────────────────────────────────────────────────────┐
│                      工厂模式结构                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐                                           │
│   │   Product   │◀──────────────────────┐                   │
│   │  (interface)│                       │                   │
│   └─────────────┘                       │                   │
│          ▲                              │                   │
│          │ implements                   │                   │
│   ┌──────┴──────┐  ┌──────────────┐    │                   │
│   │ ConcreteProductA│ ConcreteProductB│ │                   │
│   └─────────────┘  └──────────────┘    │                   │
│                                         │                   │
│   ┌─────────────┐      createProduct() │                   │
│   │    Creator  │───────────────────────┘                   │
│   │  (factory)  │                                           │
│   └─────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Python实现**：

```python
from abc import ABC, abstractmethod

# 产品接口
class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

# 具体产品
class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class Bird(Animal):
    def speak(self):
        return "Tweet!"

# 工厂类
class AnimalFactory:
    """简单工厂"""
    @staticmethod
    def create_animal(animal_type):
        animals = {
            'dog': Dog,
            'cat': Cat,
            'bird': Bird
        }
        animal_class = animals.get(animal_type)
        if animal_class:
            return animal_class()
        raise ValueError(f"Unknown animal type: {animal_type}")

# 使用
factory = AnimalFactory()
dog = factory.create_animal('dog')
print(dog.speak())  # Woof!
```

**工厂方法模式**：

```python
# 工厂方法 - 让子类决定创建什么
class Logistics(ABC):
    """物流"""
    @abstractmethod
    def create_transport(self):
        """工厂方法"""
        pass
    
    def plan_delivery(self):
        transport = self.create_transport()
        return f"Deliver by {transport.deliver()}"

class RoadLogistics(Logistics):
    def create_transport(self):
        return Truck()

class SeaLogistics(Logistics):
    def create_transport(self):
        return Ship()

class Transport(ABC):
    @abstractmethod
    def deliver(self):
        pass

class Truck(Transport):
    def deliver(self):
        return "Truck on road"

class Ship(Transport):
    def deliver(self):
        return "Ship on sea"
```

---

### 3. 建造者模式 (Builder)

**意图**：将一个复杂对象的构建与它的表示分离，使得同样的构建过程可以创建不同的表示。

```
┌─────────────────────────────────────────────────────────────┐
│                     建造者模式                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Director ──────▶ Builder (interface)                      │
│   (构建流程)        ├─ buildPartA()                         │
│                     ├─ buildPartB()                         │
│                     └─ getResult()                          │
│                            ▲                                │
│               ┌────────────┴────────────┐                   │
│               ▼                         ▼                   │
│        ConcreteBuilder1          ConcreteBuilder2           │
│        (Product A)               (Product B)                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Python实现**：

```python
class Computer:
    """产品 - 计算机"""
    def __init__(self):
        self.cpu = None
        self.memory = None
        self.storage = None
        self.gpu = None
    
    def __str__(self):
        return f"Computer(CPU={self.cpu}, Memory={self.memory}, " \
               f"Storage={self.storage}, GPU={self.gpu})"

class ComputerBuilder:
    """建造者"""
    def __init__(self):
        self.computer = Computer()
    
    def set_cpu(self, cpu):
        self.computer.cpu = cpu
        return self  # 链式调用
    
    def set_memory(self, memory):
        self.computer.memory = memory
        return self
    
    def set_storage(self, storage):
        self.computer.storage = storage
        return self
    
    def set_gpu(self, gpu):
        self.computer.gpu = gpu
        return self
    
    def build(self):
        return self.computer

# 使用 - 链式调用构建
computer = (ComputerBuilder()
    .set_cpu("Intel i9")
    .set_memory("32GB")
    .set_storage("1TB SSD")
    .set_gpu("RTX 4090")
    .build())

print(computer)

# 预设配置
class ComputerDirector:
    """指导者 - 提供预设构建方案"""
    def __init__(self, builder):
        self.builder = builder
    
    def build_gaming_pc(self):
        return (self.builder
            .set_cpu("Intel i9")
            .set_memory("32GB")
            .set_storage("1TB SSD")
            .set_gpu("RTX 4090")
            .build())
    
    def build_office_pc(self):
        return (self.builder
            .set_cpu("Intel i5")
            .set_memory("16GB")
            .set_storage("512GB SSD")
            .build())
```

---

### 4. 原型模式 (Prototype)

**意图**：通过复制现有对象来创建新对象。

```python
import copy

class Prototype:
    """原型基类"""
    def clone(self):
        """浅拷贝"""
        return copy.copy(self)
    
    def deep_clone(self):
        """深拷贝"""
        return copy.deepcopy(self)

class Document(Prototype):
    """文档 - 可复制"""
    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author
        self.comments = []
    
    def add_comment(self, comment):
        self.comments.append(comment)
    
    def __str__(self):
        return f"Document(title={self.title}, comments={len(self.comments)})"

# 使用
original = Document("Template", "Content...", "Admin")
original.add_comment("Important")

# 克隆
copy1 = original.clone()      # 浅拷贝
copy2 = original.deep_clone() # 深拷贝

# 修改验证
copy1.comments.append("New")  # 影响original（浅拷贝）
copy2.comments.append("New2") # 不影响original（深拷贝）
```

---

## 结构型模式 (Structural Patterns)

结构型模式关注如何组合类和对象以形成更大的结构。

### 5. 适配器模式 (Adapter)

**意图**：将一个类的接口转换成客户希望的另外一个接口。

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

**Python实现**：

```python
# 目标接口
class MediaPlayer:
    def play(self, filename):
        pass

# 被适配的类
class AdvancedMediaPlayer:
    """高级播放器 - 只支持特定格式"""
    def play_mp4(self, filename):
        return f"Playing mp4: {filename}"
    
    def play_vlc(self, filename):
        return f"Playing vlc: {filename}"

# 适配器
class MediaAdapter(MediaPlayer):
    """适配器 - 统一接口"""
    def __init__(self):
        self.advanced_player = AdvancedMediaPlayer()
    
    def play(self, filename):
        if filename.endswith('.mp4'):
            return self.advanced_player.play_mp4(filename)
        elif filename.endswith('.vlc'):
            return self.advanced_player.play_vlc(filename)
        return f"Cannot play: {filename}"

# 使用
player = MediaAdapter()
print(player.play("movie.mp4"))   # Playing mp4: movie.mp4
print(player.play("music.vlc"))   # Playing vlc: music.vlc
```

---

### 6. 装饰器模式 (Decorator)

**意图**：动态地给一个对象添加一些额外的职责。

```
┌─────────────────────────────────────────────────────────────┐
│                    装饰器模式                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Component ──────▶ ConcreteComponent                       │
│   (component)         (基础组件)                            │
│       ▲                                                     │
│       │ implements                                          │
│   Decorator ──────▶ ConcreteDecoratorA                      │
│   (装饰器基类)      ConcreteDecoratorB                      │
│   ├─ component                                          │
│   ├─ operation()                                          │
│                                                             │
│   特点：可嵌套、可组合、保持接口一致                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Python实现**：

```python
from abc import ABC, abstractmethod

class Coffee(ABC):
    """咖啡接口"""
    @abstractmethod
    def cost(self):
        pass
    
    @abstractmethod
    def description(self):
        pass

class SimpleCoffee(Coffee):
    """基础咖啡"""
    def cost(self):
        return 10
    
    def description(self):
        return "Simple coffee"

class CoffeeDecorator(Coffee):
    """装饰器基类"""
    def __init__(self, coffee):
        self._coffee = coffee
    
    def cost(self):
        return self._coffee.cost()
    
    def description(self):
        return self._coffee.description()

class Milk(CoffeeDecorator):
    """牛奶装饰"""
    def cost(self):
        return self._coffee.cost() + 2
    
    def description(self):
        return self._coffee.description() + ", milk"

class Sugar(CoffeeDecorator):
    """糖装饰"""
    def cost(self):
        return self._coffee.cost() + 1
    
    def description(self):
        return self._coffee.description() + ", sugar"

class Whip(CoffeeDecorator):
    ""奶泡装饰"""
    def cost(self):
        return self._coffee.cost() + 3
    
    def description(self):
        return self._coffee.description() + ", whip"

# 使用 - 自由组合
coffee = SimpleCoffee()
coffee = Milk(coffee)
coffee = Sugar(coffee)
coffee = Whip(coffee)

print(f"{coffee.description()} = ${coffee.cost()}")
# Simple coffee, milk, sugar, whip = $16
```

---

### 7. 代理模式 (Proxy)

**意图**：为其他对象提供一种代理以控制对这个对象的访问。

```python
from abc import ABC, abstractmethod

class Image(ABC):
    """图片接口"""
    @abstractmethod
    def display(self):
        pass

class RealImage(Image):
    """真实图片 - 加载成本高"""
    def __init__(self, filename):
        self.filename = filename
        self._load_from_disk()
    
    def _load_from_disk(self):
        print(f"Loading {self.filename} from disk...")
    
    def display(self):
        print(f"Displaying {self.filename}")

class ProxyImage(Image):
    """代理图片 - 延迟加载"""
    def __init__(self, filename):
        self.filename = filename
        self._real_image = None  # 延迟创建
    
    def display(self):
        # 首次访问时才加载
        if self._real_image is None:
            self._real_image = RealImage(self.filename)
        self._real_image.display()

# 使用
images = [ProxyImage(f"photo{i}.jpg") for i in range(5)]
# 此时没有加载任何图片

images[0].display()  # 此时才加载 photo0.jpg
images[0].display()  # 直接使用缓存的

# 代理类型：
# 1. 虚拟代理 - 延迟加载（如上）
# 2. 保护代理 - 访问控制
# 3. 远程代理 - 访问远程对象
# 4. 缓存代理 - 缓存结果
```

---

## 行为型模式 (Behavioral Patterns)

行为型模式关注对象之间的通信和责任分配。

### 8. 观察者模式 (Observer)

**意图**：定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖者自动收到通知。

```
┌─────────────────────────────────────────────────────────────┐
│                    观察者模式                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Subject ──────▶ Observer (interface)                      │
│   ├─ observers[]    ├─ update()                             │
│   ├─ attach()           ▲                                   │
│   ├─ detach()           │ implements                        │
│   └─ notify()    ┌──────┴──────┐                            │
│                  │             │                            │
│                  ▼             ▼                            │
│            ConcreteObserverA  ConcreteObserverB               │
│                                                             │
│   典型应用：事件监听、MVC模式、消息队列                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Python实现**：

```python
from abc import ABC, abstractmethod

class Observer(ABC):
    """观察者接口"""
    @abstractmethod
    def update(self, subject):
        pass

class Subject:
    """主题 - 被观察者"""
    def __init__(self):
        self._observers = []
        self._state = None
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self):
        """通知所有观察者"""
        for observer in self._observers:
            observer.update(self)
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        self._state = value
        self.notify()  # 状态变化时通知

class NewsPublisher(Subject):
    """新闻发布者"""
    def publish(self, news):
        self.state = news

class EmailSubscriber(Observer):
    """邮件订阅者"""
    def __init__(self, name):
        self.name = name
    
    def update(self, subject):
        print(f"[Email to {self.name}] Breaking news: {subject.state}")

class SMSSubscriber(Observer):
    """短信订阅者"""
    def __init__(self, phone):
        self.phone = phone
    
    def update(self, subject):
        print(f"[SMS to {self.phone}] {subject.state[:20]}...")

# 使用
publisher = NewsPublisher()

# 订阅
publisher.attach(EmailSubscriber("Alice"))
publisher.attach(EmailSubscriber("Bob"))
publisher.attach(SMSSubscriber("13800138000"))

# 发布新闻 - 自动通知所有订阅者
publisher.publish("Python 4.0 Released!")
```

---

### 9. 策略模式 (Strategy)

**意图**：定义一系列算法，把它们一个个封装起来，并且使它们可以互相替换。

```python
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    """支付策略接口"""
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    """信用卡支付"""
    def __init__(self, card_number, cvv):
        self.card_number = card_number
        self.cvv = cvv
    
    def pay(self, amount):
        return f"Paid ${amount} using Credit Card ending in {self.card_number[-4:]}"

class PayPalPayment(PaymentStrategy):
    """PayPal支付"""
    def __init__(self, email):
        self.email = email
    
    def pay(self, amount):
        return f"Paid ${amount} using PayPal account {self.email}"

class CryptoPayment(PaymentStrategy):
    """加密货币支付"""
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address
    
    def pay(self, amount):
        return f"Paid ${amount} using Crypto wallet {self.wallet_address[:10]}..."

class ShoppingCart:
    """购物车 - 使用策略模式"""
    def __init__(self):
        self.items = []
        self._payment_strategy = None
    
    def add_item(self, item, price):
        self.items.append((item, price))
    
    def set_payment_strategy(self, strategy):
        """动态设置支付策略"""
        self._payment_strategy = strategy
    
    def checkout(self):
        total = sum(price for _, price in self.items)
        if self._payment_strategy:
            return self._payment_strategy.pay(total)
        return "No payment method selected"

# 使用
cart = ShoppingCart()
cart.add_item("Laptop", 1000)
cart.add_item("Mouse", 50)

# 选择支付方式
cart.set_payment_strategy(CreditCardPayment("1234567890123456", "123"))
print(cart.checkout())

# 切换支付方式
cart.set_payment_strategy(PayPalPayment("user@example.com"))
print(cart.checkout())
```

---

### 10. 命令模式 (Command)

**意图**：将请求封装为对象，从而可以用不同的请求、队列或日志来参数化其他对象。

```python
from abc import ABC, abstractmethod
from collections import deque

class Command(ABC):
    """命令接口"""
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

class Light:
    """接收者 - 灯"""
    def __init__(self, location):
        self.location = location
        self.is_on = False
    
    def on(self):
        self.is_on = True
        return f"{self.location} light is ON"
    
    def off(self):
        self.is_on = False
        return f"{self.location} light is OFF"

class LightOnCommand(Command):
    """开灯命令"""
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        return self.light.on()
    
    def undo(self):
        return self.light.off()

class LightOffCommand(Command):
    """关灯命令"""
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        return self.light.off()
    
    def undo(self):
        return self.light.on()

class RemoteControl:
    """调用者 - 遥控器"""
    def __init__(self):
        self._commands = {}
        self._history = deque(maxlen=10)  # 命令历史
    
    def set_command(self, slot, command):
        self._commands[slot] = command
    
    def press_button(self, slot):
        if slot in self._commands:
            result = self._commands[slot].execute()
            self._history.append(self._commands[slot])
            return result
    
    def press_undo(self):
        if self._history:
            command = self._history.pop()
            return command.undo()

# 使用
living_room_light = Light("Living Room")

remote = RemoteControl()
remote.set_command("A", LightOnCommand(living_room_light))
remote.set_command("B", LightOffCommand(living_room_light))

print(remote.press_button("A"))   # 开灯
print(remote.press_button("B"))   # 关灯
print(remote.press_undo())        # 撤销 - 开灯
```

---

## 模式选择指南

```
┌─────────────────────────────────────────────────────────────────┐
│                  设计模式选择决策树                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   需要创建对象？                                                │
│   ├─ 是 → 需要控制实例数量？                                    │
│   │       ├─ 是 → 单例模式                                      │
│   │       └─ 否 → 需要复杂构建过程？                            │
│   │               ├─ 是 → 建造者模式                            │
│   │               └─ 否 → 需要根据条件创建不同类型？            │
│   │                       ├─ 是 → 工厂模式                      │
│   │                       └─ 否 → 需要复制现有对象？            │
│   │                               └─ 是 → 原型模式              │
│   │                                                             │
│   └─ 否 → 需要组织类或对象？                                    │
│           ├─ 是 → 需要统一接口？                                │
│           │       ├─ 是 → 适配器模式                            │
│           │       └─ 否 → 需要动态添加功能？                    │
│           │               ├─ 是 → 装饰器模式                    │
│           │               └─ 否 → 需要控制访问？                │
│           │                       └─ 是 → 代理模式              │
│           │                                                     │
│           └─ 否 → 需要处理对象间的通信？                        │
│                   ├─ 需要一对多通知？                           │
│                   │       └─ 是 → 观察者模式                    │
│                   ├─ 需要封装算法？                             │
│                   │       └─ 是 → 策略模式                      │
│                   └─ 需要解耦请求发送者和接收者？               │
│                           └─ 是 → 命令模式                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 最佳实践

### 使用设计模式的检查清单

```
□ 不要过度设计
  □ 简单问题不要用复杂模式
  □ YAGNI原则 (You Aren't Gonna Need It)

□ 理解模式的意图
  □ 不仅要知道怎么做，更要知道为什么
  □ 模式解决的问题是什么

□ 灵活应用
  □ 模式不是教条，可以根据需要调整
  □ 可以组合多个模式

□ 考虑维护性
  □ 模式应该让代码更易理解
  □ 如果增加了复杂度， reconsider

□ 命名规范
  □ 使用模式名作为类名的一部分（如UserFactory）
  □ 便于理解代码意图
```

---

## 面试要点

### 常见问题

**Q1: 单例模式的线程安全问题如何解决？**
> 使用双重检查锁定（Double-Checked Locking）：第一次检查避免不必要的锁，第二次检查在锁内确保只有一个实例被创建。Python中还可使用模块级别的单例（模块天然单例）或`__new__`方法。

**Q2: 工厂模式和建造者模式有什么区别？**> 工厂模式关注"创建什么"，根据条件返回不同类型的对象；建造者模式关注"如何构建"，通过步骤化构建复杂对象。工厂是一次性返回完整对象，建造者是分步骤配置最终构建。

**Q3: 装饰器模式和代理模式的区别？**> 装饰器模式目的是动态添加功能，被装饰者和装饰器实现同一接口；代理模式目的是控制访问，代理和被代理者也是同一接口，但代理通常不增强功能，而是添加访问控制、延迟加载等。Python中的装饰器语法`@decorator`是语法糖，与装饰器模式相关但不完全相同。

**Q4: 观察者模式和发布-订阅模式的区别？**> 观察者模式中Subject和Observer是直接耦合的，Subject维护Observer列表；发布-订阅模式引入事件通道（Event Bus），发布者和订阅者完全解耦，彼此不知道对方存在。发布-订阅是观察者模式的变体/演进。

**Q5: 什么时候不应该使用设计模式？**> 当：1) 问题很简单，模式反而增加复杂度；2) 团队不熟悉该模式；3) 过早优化（YAGNI）；4) 模式不能很好地适应特定场景。好的代码应该是"显而易见的"，而不是"巧妙的设计"。

---

## 相关概念

- [面向对象设计](./oop-design.md) - 设计模式的基础
- [SOLID原则](./solid-principles.md) - 设计模式遵循的原则
- [领域驱动设计](./ddd.md) - 复杂系统的面向对象设计方法
- [约定](../computer-science/data-structures/convention.md) - 设计模式中的约定

---

## 参考资料

1. "Design Patterns: Elements of Reusable Object-Oriented Software" by GoF (Gang of Four)
2. "Head First Design Patterns" by Eric Freeman
3. Refactoring.Guru: https://refactoring.guru/design-patterns
4. SourceMaking: https://sourcemaking.com/design_patterns
5. Python设计模式: https://python-patterns.guide/
