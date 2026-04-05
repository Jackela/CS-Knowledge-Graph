# SOLID原则 (SOLID Principles)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、Robert C. Martin的著作及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**SOLID原则** 是由Robert C. Martin（"Uncle Bob"）提出的五个[面向对象设计](./oop-design.md)原则的首字母缩写，旨在使软件设计更易于理解、维护和扩展。

```
┌─────────────────────────────────────────────────────────────┐
│                      SOLID 原则                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  S - Single Responsibility Principle (单一职责原则)         │
│  O - Open/Closed Principle (开闭原则)                       │
│  L - Liskov Substitution Principle (里氏替换原则)           │
│  I - Interface Segregation Principle (接口隔离原则)         │
│  D - Dependency Inversion Principle (依赖倒置原则)          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## S - 单一职责原则 (SRP)

### 定义

> **一个类应该只有一个引起它变化的原因。**

### 解释

```
如果一个类承担了多个职责，当其中一个职责变化时，
可能会影响到其他职责的实现。
```

### 示例

```python
# ❌ 违反SRP：一个类处理用户数据和邮件发送
class UserManager:
    def create_user(self, name, email):
        # 创建用户
        pass
    
    def save_user(self, user):
        # 保存到数据库
        pass
    
    def send_email(self, user, message):
        # 发送邮件
        pass

# ✅ 遵循SRP：职责分离
class UserService:
    """负责用户业务逻辑"""
    def create_user(self, name, email):
        pass

class UserRepository:
    """负责数据持久化"""
    def save(self, user):
        pass

class EmailService:
    """负责邮件发送"""
    def send(self, to, message):
        pass
```

### 如何判断

```
□ 类名是否能准确描述其职责？
□ 类中的方法是否都围绕同一目标？
□ 修改一个功能是否会影响其他功能？
```

---

## O - 开闭原则 (OCP)

### 定义

> **软件实体应该对扩展开放，对修改关闭。**

### 解释

```
当需要新功能时，应该通过扩展现有代码来实现，
而不是修改原有代码。
```

### 示例

```python
# ❌ 违反OCP：新增图形类型需要修改原有代码
class AreaCalculator:
    def calculate(self, shape):
        if shape.type == "rectangle":
            return shape.width * shape.height
        elif shape.type == "circle":
            return 3.14 * shape.radius ** 2
        # 新增三角形需要在这里添加代码

# ✅ 遵循OCP：通过多态扩展
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

# 新增三角形，无需修改原有代码
class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height
    
    def area(self):
        return 0.5 * self.base * self.height
```

---

## L - 里氏替换原则 (LSP)

### 定义

> **子类型必须能够替换其基类型而不影响程序正确性。**

### 解释

```
如果S是T的子类，那么程序中使用T的地方都可以用S替换，
而不会产生错误。
```

### 示例

```python
# ❌ 违反LSP：正方形不是长方形的合适子类
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height
    
    @property
    def width(self):
        return self._width
    
    @width.setter
    def width(self, value):
        self._width = value
    
    @property
    def height(self):
        return self._height
    
    @height.setter
    def height(self, value):
        self._height = value

class Square(Rectangle):
    """正方形：违反LSP"""
    @width.setter
    def width(self, value):
        self._width = value
        self._height = value  # 副作用！
    
    @height.setter
    def height(self, value):
        self._width = value   # 副作用！
        self._height = value

# 违反LSP的使用
def resize(rectangle, new_width):
    rectangle.width = new_width
    # 对于正方形，height也被改变了！
    assert rectangle.width != rectangle.height  # 失败！

# ✅ 正确做法：正方形和长方形不是继承关系
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    # ... 不变
    pass

class Square(Shape):
    def __init__(self, side):
        self._side = side
    
    @property
    def side(self):
        return self._side
    
    def area(self):
        return self._side ** 2
```

---

## I - 接口隔离原则 (ISP)

### 定义

> **客户端不应该被迫依赖它们不使用的接口。**

### 解释

```
大的接口应该拆分成更小的、更具体的接口，
这样客户端只需要知道它们感兴趣的方法。
```

### 示例

```python
# ❌ 违反ISP：胖接口
class WorkerInterface:
    def work(self):
        pass
    
    def eat(self):
        pass
    
    def sleep(self):
        pass

class Robot(WorkerInterface):
    def work(self):
        print("Working...")
    
    def eat(self):
        raise NotImplementedError("Robot doesn't eat!")
    
    def sleep(self):
        raise NotImplementedError("Robot doesn't sleep!")

# ✅ 遵循ISP：接口拆分
from abc import ABC, abstractmethod

class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

class Human(Workable, Eatable, Sleepable):
    def work(self): print("Working...")
    def eat(self): print("Eating...")
    def sleep(self): print("Sleeping...")

class Robot(Workable):
    def work(self): print("Working...")
```

---

## D - 依赖倒置原则 (DIP)

### 定义

> **高层模块不应该依赖低层模块，两者都应该依赖抽象。**
> **抽象不应该依赖细节，细节应该依赖抽象。**

### 解释

```
通过接口或抽象类进行依赖，而不是具体实现。
这使得系统更灵活，易于测试和扩展。
```

### 示例

```python
# ❌ 违反DIP：高层依赖低层具体实现
class MySQLDatabase:
    def connect(self):
        pass
    
    def query(self, sql):
        pass

class UserService:
    """高层模块依赖低层具体类"""
    def __init__(self):
        self.db = MySQLDatabase()  # 硬编码依赖
    
    def get_user(self, id):
        return self.db.query(f"SELECT * FROM users WHERE id={id}")

# ✅ 遵循DIP：依赖抽象
from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def query(self, sql):
        pass

class MySQLDatabase(DatabaseInterface):
    def query(self, sql):
        # MySQL实现
        pass

class PostgreSQLDatabase(DatabaseInterface):
    def query(self, sql):
        # PostgreSQL实现
        pass

class UserService:
    """高层模块依赖抽象"""
    def __init__(self, db: DatabaseInterface):
        self.db = db  # 依赖注入
    
    def get_user(self, id):
        return self.db.query(f"SELECT * FROM users WHERE id={id}")

# 使用
mysql_db = MySQLDatabase()
service = UserService(mysql_db)

# 可以轻松切换数据库
postgres_db = PostgreSQLDatabase()
service = UserService(postgres_db)
```

---

## 原则之间的关系

```
┌─────────────────────────────────────────────────────────────┐
│                    SOLID 原则关系图                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│         SRP ────────┐                                       │
│        (单一职责)    │                                       │
│            │        │                                       │
│            ▼        │                                       │
│         ISP ◀───────┤──────► DIP                            │
│      (接口隔离)      │      (依赖倒置)                        │
│            │        │        ▲                              │
│            ▼        │        │                              │
│         OCP ◀───────┴────────┘                              │
│      (开闭原则)                                              │
│            ▲                                                │
│            │                                                │
│         LSP                                                 │
│      (里氏替换)                                              │
│                                                             │
│  SRP是其他原则的基础                                          │
│  LSP保证继承体系的正确性                                       │
│  ISP和DIP是实现OCP的手段                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 应用检查清单

```
□ SRP: 每个类/模块只有一个明确的职责
□ OCP: 新增功能时无需修改现有代码
□ LSP: 子类可以完全替换父类使用
□ ISP: 接口精简，不包含客户端不需要的方法
□ DIP: 依赖接口/抽象，而非具体实现
```


## 相关概念

### 软件工程

-  - OOD基础
- [设计模式](./design-patterns.md) - SOLID原则的具体应用
- [依赖注入](./architecture-patterns/dependency-injection.md) - 实现DIP的技术
- [领域驱动设计](./ddd.md) - 战略设计方法
- [TDD](./testing/tdd.md) - 测试驱动开发中的SOLID应用
- [代码覆盖率](./testing/code-coverage.md) - 验证原则实施效果的度量
#### 计算机科学基础

- 抽象数据类型 - 数据抽象与封装原则
- 面向对象范式 - OOP在数据结构中的应用
- [面向对象范式](../computer-science/data-structures/convention.md) - OOP在数据结构中的应用

---

## 参考资料

1. "Clean Code" by Robert C. Martin
2. "Agile Software Development, Principles, Patterns, and Practices" by Robert C. Martin
3. "Head First Design Patterns" by Eric Freeman
4. [Wikipedia: SOLID](https://en.wikipedia.org/wiki/SOLID)

---

*最后更新：2024年*
