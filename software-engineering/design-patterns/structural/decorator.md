# 装饰器模式 (Decorator Pattern)

## 概念

装饰器模式（Decorator Pattern）是一种**结构型设计模式**，它允许向一个现有的对象添加新的功能，同时又不改变其结构。装饰器模式作为现有的类的一个包装，比生成子类更为灵活。

> **核心思想**: 动态地给一个对象添加一些额外的职责，而不需要修改原对象的代码。

```
继承方式：                      装饰器方式：
                                
Coffee                          Coffee (Component)
  │                               ▲
  ├── SimpleCoffee                ├── SimpleCoffee (Concrete)
  ├── MilkCoffee                  ├── Milk (Decorator)
  ├── SugarCoffee                 ├── Sugar (Decorator)
  └── MilkSugarCoffee             └── Whip (Decorator)
  
每个组合都需要新类               组合通过链式包装实现
类爆炸问题                       灵活组合，无需额外类
```

---

## 原理

### 为什么需要装饰器模式？

1. **比继承更灵活**: 运行时动态添加功能，而不是编译时固定
2. **避免类爆炸**: 无需为每种组合创建新类
3. **单一职责**: 每个装饰器只负责一个功能
4. **可叠加**: 可以任意组合多个装饰器

### 核心角色

| 角色 | 职责 |
|------|------|
| Component | 定义对象接口，装饰器和被装饰对象的共同父类 |
| ConcreteComponent | 具体被装饰对象 |
| Decorator | 装饰器抽象类，维护 Component 引用 |
| ConcreteDecorator | 具体装饰器，实现具体功能增强 |

### 优缺点

**优点：**
- 比继承更灵活，运行时动态扩展
- 符合开闭原则，不修改原有代码
- 可以叠加多个装饰器
- 每个装饰器职责单一

**缺点：**
- 产生大量小对象
- 排查问题更复杂（需要层层追溯）
- 装饰顺序可能影响结果

---

## 实现方式

### 1. Python 实现

```python
from abc import ABC, abstractmethod


# 组件接口
class Coffee(ABC):
    @abstractmethod
    def cost(self) -> float:
        pass
    
    @abstractmethod
    def description(self) -> str:
        pass


# 具体组件 - 简单咖啡
class SimpleCoffee(Coffee):
    def cost(self) -> float:
        return 10.0
    
    def description(self) -> str:
        return "简单咖啡"


# 装饰器基类
class CoffeeDecorator(Coffee, ABC):
    def __init__(self, coffee: Coffee):
        self._coffee = coffee
    
    def cost(self) -> float:
        return self._coffee.cost()
    
    def description(self) -> str:
        return self._coffee.description()


# 具体装饰器 - 加奶
class MilkDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 2.0
    
    def description(self) -> str:
        return self._coffee.description() + ", 牛奶"


# 具体装饰器 - 加糖
class SugarDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 1.0
    
    def description(self) -> str:
        return self._coffee.description() + ", 糖"


# 具体装饰器 - 加奶油
class WhipDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 3.0
    
    def description(self) -> str:
        return self._coffee.description() + ", 奶油"


# 具体装饰器 - 加香草
class VanillaDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 1.5
    
    def description(self) -> str:
        return self._coffee.description() + ", 香草"


# 使用场景
coffee = SimpleCoffee()
print(f"{coffee.description()}: ¥{coffee.cost()}")

coffee = MilkDecorator(coffee)
print(f"{coffee.description()}: ¥{coffee.cost()}")

coffee = SugarDecorator(coffee)
print(f"{coffee.description()}: ¥{coffee.cost()}")

coffee = WhipDecorator(coffee)
print(f"{coffee.description()}: ¥{coffee.cost()}")

# 灵活组合
coffee2 = VanillaDecorator(MilkDecorator(MilkDecorator(SimpleCoffee())))
print(f"{coffee2.description()}: ¥{coffee2.cost()}")
```

### 2. 数据流处理示例

```python
from abc import ABC, abstractmethod
import base64
import zlib


# 组件接口
class DataSource(ABC):
    @abstractmethod
    def write_data(self, data: str):
        pass
    
    @abstractmethod
    def read_data(self) -> str:
        pass


# 具体组件 - 文件数据源
class FileDataSource(DataSource):
    def __init__(self, filename: str):
        self.filename = filename
        self._data = ""
    
    def write_data(self, data: str):
        self._data = data
        print(f"写入文件 {self.filename}: {data[:50]}...")
    
    def read_data(self) -> str:
        print(f"从文件 {self.filename} 读取数据")
        return self._data


# 装饰器基类
class DataSourceDecorator(DataSource, ABC):
    def __init__(self, source: DataSource):
        self._source = source
    
    def write_data(self, data: str):
        self._source.write_data(data)
    
    def read_data(self) -> str:
        return self._source.read_data()


# 具体装饰器 - 加密
class EncryptionDecorator(DataSourceDecorator):
    def write_data(self, data: str):
        encrypted = self._encrypt(data)
        super().write_data(encrypted)
    
    def read_data(self) -> str:
        data = super().read_data()
        return self._decrypt(data)
    
    def _encrypt(self, data: str) -> str:
        return base64.b64encode(data.encode()).decode()
    
    def _decrypt(self, data: str) -> str:
        return base64.b64decode(data.encode()).decode()


# 具体装饰器 - 压缩
class CompressionDecorator(DataSourceDecorator):
    def write_data(self, data: str):
        compressed = self._compress(data)
        super().write_data(compressed)
    
    def read_data(self) -> str:
        data = super().read_data()
        return self._decompress(data)
    
    def _compress(self, data: str) -> str:
        return zlib.compress(data.encode()).hex()
    
    def _decompress(self, data: str) -> str:
        return zlib.decompress(bytes.fromhex(data)).decode()


# 使用场景
source = FileDataSource("data.txt")

# 仅加密
encrypted_source = EncryptionDecorator(source)
encrypted_source.write_data("敏感数据: 密码123456")
data = encrypted_source.read_data()
print(f"读取结果: {data}\n")

# 压缩 + 加密
compressed_encrypted = EncryptionDecorator(CompressionDecorator(
    FileDataSource("secure_data.bin")
))
compressed_encrypted.write_data("这是一段很长很长很长的文本数据..." * 100)
data = compressed_encrypted.read_data()
print(f"读取结果: {data[:50]}...")
```

### 3. Java 实现示例

```java
// 组件接口
public interface Pizza {
    String getDescription();
    double getCost();
}

// 具体组件
public class PlainPizza implements Pizza {
    @Override
    public String getDescription() {
        return "薄饼";
    }
    
    @Override
    public double getCost() {
        return 20.0;
    }
}

// 装饰器基类
public abstract class PizzaDecorator implements Pizza {
    protected Pizza pizza;
    
    public PizzaDecorator(Pizza pizza) {
        this.pizza = pizza;
    }
    
    @Override
    public String getDescription() {
        return pizza.getDescription();
    }
    
    @Override
    public double getCost() {
        return pizza.getCost();
    }
}

// 具体装饰器 - 芝士
public class CheeseDecorator extends PizzaDecorator {
    public CheeseDecorator(Pizza pizza) {
        super(pizza);
    }
    
    @Override
    public String getDescription() {
        return pizza.getDescription() + ", 芝士";
    }
    
    @Override
    public double getCost() {
        return pizza.getCost() + 5.0;
    }
}

// 具体装饰器 - 火腿
public class HamDecorator extends PizzaDecorator {
    public HamDecorator(Pizza pizza) {
        super(pizza);
    }
    
    @Override
    public String getDescription() {
        return pizza.getDescription() + ", 火腿";
    }
    
    @Override
    public double getCost() {
        return pizza.getCost() + 8.0;
    }
}

// 使用
public class Client {
    public static void main(String[] args) {
        Pizza pizza = new PlainPizza();
        pizza = new CheeseDecorator(pizza);
        pizza = new HamDecorator(pizza);
        System.out.println(pizza.getDescription() + " ¥" + pizza.getCost());
    }
}
```

---

## 示例

### Python 装饰器语法糖

```python
from functools import wraps
import time


# 功能：计算函数执行时间
def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} 执行时间: {elapsed:.4f}秒")
        return result
    return wrapper


# 功能：记录函数调用日志
def logging_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}, 参数: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} 返回: {result}")
        return result
    return wrapper


# 功能：缓存函数结果
def memoize_decorator(func):
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper


# 使用多个装饰器
@timing_decorator
@logging_decorator
@memoize_decorator
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# 调用
print(f"fibonacci(10) = {fibonacci(10)}")
print(f"fibonacci(10) = {fibonacci(10)}")  # 第二次从缓存读取
```

### UML 图

```
┌─────────────────────────────────────────────────────────────────┐
│                       装饰器模式 UML                            │
│                    （咖啡示例）                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  <<interface>>                                          │   │
│  │          Coffee                                         │   │
│  │                                                         │   │
│  │  +cost(): float                                         │   │
│  │  +description(): str                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ▲                                    ▲               │
│           │                                    │               │
│  ┌────────┴────────┐              ┌────────────┴────────────┐  │
│  │                 │              │                         │  │
│  │  SimpleCoffee   │              │   CoffeeDecorator       │  │
│  │                 │              │   (Abstract)            │  │
│  │ +cost()         │              │                         │  │
│  │ +description()  │              │ -_coffee: Coffee        │  │
│  │                 │              │                         │  │
│  └─────────────────┘              └───────────┬─────────────┘  │
│                                               │                │
│                              ┌────────────────┼────────────────┤
│                              │                │                │
│                     ┌────────▼───────┐ ┌──────▼──────┐ ┌──────▼──────┐
│                     │ MilkDecorator  │ │SugarDecorator│ │WhipDecorator│
│                     │                │ │              │ │             │
│                     │ +cost()        │ │ +cost()      │ │ +cost()     │
│                     │ +description() │ │+description()│ │+description()│
│                     └────────────────┘ └──────────────┘ └─────────────┘
│                                                                 │
│  调用链示意：                                                    │
│                                                                 │
│  cost()                                                         │
│    │                                                            │
│    ▼                                                            │
│  WhipDecorator.cost() ──┐                                       │
│    │                     │ calls                                │
│    ▼                     │                                      │
│  SugarDecorator.cost() ──┤                                       │
│    │                     │ calls                                │
│    ▼                     │                                      │
│  MilkDecorator.cost() ───┤                                       │
│    │                     │ calls                                │
│    ▼                     │                                      │
│  SimpleCoffee.cost() ◀───┘                                       │
│    │                                                            │
│    └── return 10.0                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

1. **Q: 什么是装饰器模式？**
   
   A: 装饰器模式是一种结构型设计模式，允许向现有对象动态添加新功能，同时不改变其结构。它通过包装对象来实现，比继承更灵活。

2. **Q: 装饰器模式与继承的区别？**
   
   A: 继承在编译时确定功能，不够灵活；装饰器在运行时动态添加功能，可以任意组合。继承会导致类爆炸，装饰器通过组合避免这个问题。

3. **Q: 装饰器模式与代理模式的区别？**
   
   A: 装饰器模式目的是**增强功能**，可以叠加多个装饰器；代理模式目的是**控制访问**，通常只有一个代理层。装饰器关注功能扩展，代理关注访问控制。

4. **Q: 装饰器模式与适配器模式的区别？**
   
   A: 装饰器模式保持接口不变，添加新功能；适配器模式转换接口使其兼容。装饰器增强同类型对象，适配器连接不同类型对象。

5. **Q: 实际应用场景有哪些？**
   
   A: 常见场景包括：
   - Java IO 流（BufferedReader、FileReader 等）
   - Web 框架中间件（Django/Flask 装饰器）
   - 数据流处理（加密、压缩、编码）
   - GUI 组件样式叠加
   - Python @decorator 语法

---

## 相关概念

### 数据结构
- [链表](../../../computer-science/data-structures/linked-list.md) - 装饰器链式结构
- [栈](../../../computer-science/data-structures/stack.md) - 嵌套调用顺序

### 算法
- [递归](../../../computer-science/algorithms/recursion.md) - 装饰器链递归调用

### 复杂度分析
- [时间复杂度](../../../references/time-complexity.md) - 多层装饰开销
- [空间复杂度](../../../references/space-complexity.md) - 装饰器对象内存

### 系统实现
- [I/O 系统](../../../computer-science/systems/file-systems.md) - Java IO 装饰器
- [网络协议](../../../computer-science/systems/network.md) - 协议栈分层

### 设计模式
- [代理模式](./proxy.md) - 访问控制
- [适配器模式](./adapter.md) - 接口转换
- [策略模式](../behavioral/strategy.md) - 算法替换
- [责任链模式](../behavioral/chain-of-responsibility.md) - 请求链处理


> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概念 (Concept)

**装饰器模式 (Decorator Pattern)** 是一种结构型设计模式，它允许你通过将对象放入包含行为的特殊包装对象中来为原对象绑定新的行为。

装饰器模式的核心思想是**动态地给对象添加额外的职责**，而不会影响其他对象。这提供了一种比继承更灵活的扩展功能的方式。

```
┌─────────────────────────────────────────────────────────────┐
│                    装饰器模式 (Decorator)                    │
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

---

## 设计原则 (Principle)

装饰器模式遵循以下设计原则：

1. **开闭原则 (Open/Closed Principle)**：对扩展开放，对修改关闭。无需修改现有代码即可添加新功能
2. **单一职责原则 (Single Responsibility Principle)**：每个装饰器只负责一个特定功能的添加
3. **组合优于继承 (Favor Composition Over Inheritance)**：使用组合而非继承来扩展功能

**与继承的区别**：
- **继承**：静态扩展，编译时确定，只能单继承
- **装饰器**：动态扩展，运行时确定，可多层嵌套

---

## 实现示例 (Example)

### 1. 咖啡订购系统（经典示例）

```python
from abc import ABC, abstractmethod

# ============== 组件接口 ==============

class Coffee(ABC):
    """咖啡接口"""
    
    @abstractmethod
    def get_description(self) -> str:
        pass
    
    @abstractmethod
    def get_cost(self) -> float:
        pass

# ============== 具体组件 ==============

class SimpleCoffee(Coffee):
    """简单咖啡 - 基础组件"""
    
    def get_description(self) -> str:
        return "简单咖啡"
    
    def get_cost(self) -> float:
        return 10.0

# ============== 装饰器基类 ==============

class CoffeeDecorator(Coffee):
    """咖啡装饰器基类"""
    
    def __init__(self, coffee: Coffee):
        self._coffee = coffee
    
    def get_description(self) -> str:
        return self._coffee.get_description()
    
    def get_cost(self) -> float:
        return self._coffee.get_cost()

# ============== 具体装饰器 ==============

class Milk(CoffeeDecorator):
    """牛奶装饰"""
    
    def get_description(self) -> str:
        return self._coffee.get_description() + " + 牛奶"
    
    def get_cost(self) -> float:
        return self._coffee.get_cost() + 2.0

class Sugar(CoffeeDecorator):
    """糖装饰"""
    
    def get_description(self) -> str:
        return self._coffee.get_description() + " + 糖"
    
    def get_cost(self) -> float:
        return self._coffee.get_cost() + 0.5

class Whip(CoffeeDecorator):
    """奶泡装饰"""
    
    def get_description(self) -> str:
        return self._coffee.get_description() + " + 奶泡"
    
    def get_cost(self) -> float:
        return self._coffee.get_cost() + 3.0

class Vanilla(CoffeeDecorator):
    """香草糖浆装饰"""
    
    def get_description(self) -> str:
        return self._coffee.get_description() + " + 香草糖浆"
    
    def get_cost(self) -> float:
        return self._coffee.get_cost() + 4.0

class ExtraShot(CoffeeDecorator):
    """加浓咖啡装饰"""
    
    def get_description(self) -> str:
        return self._coffee.get_description() + " + 加浓"
    
    def get_cost(self) -> float:
        return self._coffee.get_cost() + 5.0

# ============== 使用示例 ==============

# 简单咖啡
coffee = SimpleCoffee()
print(f"{coffee.get_description()}: ¥{coffee.get_cost()}")

# 加牛奶
coffee_with_milk = Milk(SimpleCoffee())
print(f"{coffee_with_milk.get_description()}: ¥{coffee_with_milk.get_cost()}")

# 加牛奶和糖
coffee_with_milk_and_sugar = Sugar(Milk(SimpleCoffee()))
print(f"{coffee_with_milk_and_sugar.get_description()}: ¥{coffee_with_milk_and_sugar.get_cost()}")

# 复杂组合 - 摩卡风格
mocha = Whip(Vanilla(Milk(SimpleCoffee())))
print(f"{mocha.get_description()}: ¥{mocha.get_cost()}")

# 超复杂组合 - 可以根据需要任意组合
super_coffee = Whip(Vanilla(Sugar(Milk(ExtraShot(SimpleCoffee())))))
print(f"{super_coffee.get_description()}: ¥{super_coffee.get_cost()}")
```

### 2. 数据流处理管道

```python
from abc import ABC, abstractmethod
from typing import Any

class DataSource(ABC):
    """数据源接口"""
    
    @abstractmethod
    def read(self) -> str:
        pass
    
    @abstractmethod
    def write(self, data: str):
        pass

class FileDataSource(DataSource):
    """文件数据源 - 基础组件"""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.data = ""
    
    def read(self) -> str:
        return self.data
    
    def write(self, data: str):
        self.data = data
        print(f"写入文件 {self.filename}: {len(data)} 字符")

class DataSourceDecorator(DataSource):
    """数据源装饰器基类"""
    
    def __init__(self, source: DataSource):
        self._source = source
    
    def read(self) -> str:
        return self._source.read()
    
    def write(self, data: str):
        self._source.write(data)

class EncryptionDecorator(DataSourceDecorator):
    """加密装饰器"""
    
    def read(self) -> str:
        """读取时解密"""
        encrypted = self._source.read()
        return self._decrypt(encrypted)
    
    def write(self, data: str):
        """写入时加密"""
        encrypted = self._encrypt(data)
        self._source.write(encrypted)
    
    def _encrypt(self, data: str) -> str:
        # 简单替换加密示例
        return ''.join(chr(ord(c) + 1) for c in data)
    
    def _decrypt(self, data: str) -> str:
        return ''.join(chr(ord(c) - 1) for c in data)

class CompressionDecorator(DataSourceDecorator):
    """压缩装饰器"""
    
    def read(self) -> str:
        """读取时解压"""
        compressed = self._source.read()
        return self._decompress(compressed)
    
    def write(self, data: str):
        """写入时压缩"""
        compressed = self._compress(data)
        self._source.write(compressed)
    
    def _compress(self, data: str) -> str:
        # 简单压缩示例 - 重复字符压缩
        if not data:
            return data
        result = []
        count = 1
        for i in range(1, len(data)):
            if data[i] == data[i-1]:
                count += 1
            else:
                result.append(f"{data[i-1]}{count}")
                count = 1
        result.append(f"{data[-1]}{count}")
        compressed = ''.join(result)
        print(f"压缩: {len(data)} -> {len(compressed)} 字符")
        return compressed
    
    def _decompress(self, data: str) -> str:
        # 解压实现...
        return data

class LoggingDecorator(DataSourceDecorator):
    """日志装饰器"""
    
    def read(self) -> str:
        print(f"[LOG] 读取数据从 {self._source}")
        result = self._source.read()
        print(f"[LOG] 读取完成，{len(result)} 字符")
        return result
    
    def write(self, data: str):
        print(f"[LOG] 准备写入 {len(data)} 字符")
        self._source.write(data)
        print(f"[LOG] 写入完成")

# ============== 使用示例 ==============

# 基础文件数据源
source = FileDataSource("data.txt")
source.write("Hello World!")
print(f"读取: {source.read()}\n")

# 添加加密
encrypted_source = EncryptionDecorator(FileDataSource("encrypted.dat"))
encrypted_source.write("Secret Message!")
print(f"加密后读取: {encrypted_source.read()}\n")

# 加密 + 压缩
secure_source = CompressionDecorator(EncryptionDecorator(FileDataSource("secure.dat")))
secure_source.write("AAAAAAAAAABBBBBBBBBB")
print(f"解密解压后: {secure_source.read()}\n")

# 添加日志
logged_source = LoggingDecorator(CompressionDecorator(EncryptionDecorator(FileDataSource("full.dat"))))
logged_source.write("Important Data")
```

### 3. Web中间件装饰器

```python
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any
import time

class RequestHandler(ABC):
    """请求处理器接口"""
    
    @abstractmethod
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        pass

class BaseHandler(RequestHandler):
    """基础处理器"""
    
    def __init__(self, name: str):
        self.name = name
    
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[{self.name}] 处理请求: {request}")
        return {"status": "success", "handler": self.name}

class HandlerDecorator(RequestHandler):
    """处理器装饰器基类"""
    
    def __init__(self, handler: RequestHandler):
        self._handler = handler
    
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return self._handler.handle(request)

class AuthenticationDecorator(HandlerDecorator):
    """认证装饰器"""
    
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # 检查认证
        token = request.get("token")
        if not token:
            return {"status": "error", "message": "未认证"}
        
        print("[Auth] 认证通过")
        return self._handler.handle(request)

class LoggingDecorator(HandlerDecorator):
    """日志装饰器"""
    
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Log] 请求开始: {request}")
        start = time.time()
        
        result = self._handler.handle(request)
        
        elapsed = time.time() - start
        print(f"[Log] 请求完成，耗时: {elapsed:.3f}s")
        return result

class RateLimitDecorator(HandlerDecorator):
    """限流装饰器"""
    
    def __init__(self, handler: RequestHandler, max_requests: int = 10):
        super().__init__(handler)
        self.max_requests = max_requests
        self.requests = []
    
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        now = time.time()
        # 清理过期请求记录
        self.requests = [t for t in self.requests if now - t < 60]
        
        if len(self.requests) >= self.max_requests:
            return {"status": "error", "message": "请求过于频繁"}
        
        self.requests.append(now)
        print(f"[RateLimit] 当前请求数: {len(self.requests)}/{self.max_requests}")
        return self._handler.handle(request)

class CacheDecorator(HandlerDecorator):
    """缓存装饰器"""
    
    def __init__(self, handler: RequestHandler):
        super().__init__(handler)
        self.cache = {}
    
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # 简单缓存键生成
        cache_key = str(request)
        
        if cache_key in self.cache:
            print("[Cache] 命中缓存")
            return self.cache[cache_key]
        
        result = self._handler.handle(request)
        self.cache[cache_key] = result
        print("[Cache] 已缓存")
        return result

# ============== 使用示例 ==============

# 基础处理器
base_handler = BaseHandler("UserService")

# 添加各种中间件 - 可自由组合
handler = base_handler
handler = LoggingDecorator(handler)           # 添加日志
handler = CacheDecorator(handler)             # 添加缓存
handler = RateLimitDecorator(handler, 5)      # 添加限流
handler = AuthenticationDecorator(handler)    # 添加认证

# 执行请求
print("=== 第一次请求 ===")
result = handler.handle({"action": "get_user", "user_id": "123", "token": "abc123"})
print(f"结果: {result}\n")

print("=== 第二次请求（命中缓存） ===")
result = handler.handle({"action": "get_user", "user_id": "123", "token": "abc123"})
print(f"结果: {result}\n")

print("=== 无认证请求 ===")
result = handler.handle({"action": "get_user", "user_id": "456"})
print(f"结果: {result}")
```

---

## 使用场景 (Use Cases)

| 场景 | 说明 |
|------|------|
| 动态添加功能 | 运行时决定添加哪些功能 |
| 可撤销的责任 | 可以动态移除添加的功能 |
| 功能组合 | 多种功能可以任意组合 |
| 替代继承 | 避免子类爆炸 |
| I/O流包装 | Java IO、Python IO的包装 |
| Web中间件 | HTTP请求的处理链 |
| UI组件 | 动态添加边框、滚动条等 |

---

## 面试要点 (Interview Points)

**Q1: 装饰器模式和代理模式的区别？**

> - **装饰器模式**：目的是增强功能，保持接口不变，可以嵌套多层
> - **代理模式**：目的是控制访问（如延迟加载、权限控制），通常只包装一层
>
> 装饰器是"功能增强"，代理是"访问控制"。

**Q2: 装饰器模式和继承的区别？**

> - **继承**：静态扩展，编译时确定，只能单继承，类爆炸问题
> - **装饰器**：动态扩展，运行时确定，可多层嵌套，更灵活
>
> 装饰器模式比继承更符合开闭原则。

**Q3: Python 装饰器语法 `@decorator` 和装饰器模式的关系？**

> Python的`@decorator`语法是一种语法糖，用于包装函数或类。它实现了类似装饰器模式的思想，但更侧重于函数/方法级别的增强。装饰器模式是面向对象设计模式，适用于类的组合。

**Q4: 装饰器模式的缺点？**

> - 会产生大量小对象，影响性能
> - 调试困难，调用栈较深
> - 需要保持接口一致，装饰器过多时接口难以维护
> - 不能替代原始对象的类型检查（`isinstance` 会失败）

**Q5: 如何实现一个"可移除"的装饰器？**

> 通常装饰器设计为不可移除。如果需要移除功能，应该：
> 1. 不添加该装饰器
> 2. 使用空对象模式（Null Object Pattern）
> 3. 在装饰器内部添加开关控制

---

## 相关概念 (Related Concepts)

### 结构型设计模式

- [代理模式](./proxy.md) - 控制对象访问，与装饰器模式结构相似但目的不同
- [适配器模式](./adapter.md) - 接口转换，使不兼容接口协同工作
- [桥接模式](./bridge.md) - 分离抽象与实现，应对多维度变化
- [组合模式](./composite.md) - 树形结构，统一处理单个对象和组合对象
- [外观模式](./facade.md) - 简化复杂子系统的接口
- [享元模式](./flyweight.md) - 共享细粒度对象，优化内存使用

### 面向对象设计原则

- [SOLID原则](../../solid-principles.md) - 单一职责、开闭原则等核心设计准则
- [面向对象设计](../../oop-design.md) - 封装、继承、多态等OOP基础概念

### 软件架构与设计

- [设计模式总览](../../design-patterns.md) - 23种经典设计模式完整索引
- [架构模式](../../architecture-patterns.md) - 更高层次的系统架构设计方法

#### 计算机科学基础

- I/O流包装 - 数据流的层级包装与装饰
- [递归与迭代增强](../../../computer-science/algorithms/recursion.md) - 算法行为的动态增强
- [内存管理装饰](../../../computer-science/systems/memory-management.md) - 内存分配器的包装与增强

---

## 相关引用 (References)

- 相关： - 控制对象访问
- 相关： - 接口转换
- 相关： - 树形结构
