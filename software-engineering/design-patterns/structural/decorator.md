## 版权声明

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

---
## 相关引用 (References)

- 返回：[设计模式总览](../../design-patterns.md)
- 相关：[代理模式](./proxy.md) - 控制对象访问
- 相关：[适配器模式](./adapter.md) - 接口转换
- 相关：[组合模式](./composite.md) - 树形结构
- 原理：[SOLID原则](../../solid-principles.md)
