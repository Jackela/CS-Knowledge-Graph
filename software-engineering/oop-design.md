# 面向对象设计 (Object-Oriented Design)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**面向对象设计 (Object-Oriented Design, OOD)** 是一种软件设计方法论，它将现实世界中的实体抽象为对象，通过对象之间的交互来构建软件系统。面向对象设计的核心思想是将数据（属性）和操作数据的方法（行为）封装在一起，形成独立的、可复用的软件组件。

```
┌─────────────────────────────────────────────────────────────────┐
│                   面向对象设计核心思想                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   现实世界 ──────抽象──────▶ 软件世界                            │
│                                                                 │
│   学生  ─────────────────▶  Student类                           │
│   ├─ 姓名                ├─ name属性                            │
│   ├─ 年龄                ├─ age属性                             │
│   ├─ 学习()              ├─ study()方法                         │
│   └─ 考试()              └─ exam()方法                          │
│                                                                 │
│   核心优势：                                                    │
│   • 模块化 - 高内聚、低耦合                                     │
│   • 可复用 - 继承、组合                                         │
│   • 易维护 - 封装隐藏实现细节                                   │
│   • 可扩展 - 多态支持新行为                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 面向对象 vs 面向过程

| 特性 | 面向过程 (Procedural) | 面向对象 (Object-Oriented) |
|------|----------------------|---------------------------|
| 核心单位 | 函数/过程 | 对象/类 |
| 数据与行为 | 分离 | 封装在一起 |
| 代码组织 | 按功能划分 | 按对象划分 |
| 复用方式 | 函数调用 | 继承、组合、多态 |
| 适用场景 | 简单脚本、算法 | 大型复杂系统 |
| 代表语言 | C, Pascal | Java, C++, Python, C# |

---

## 核心概念

### 1. 类与对象 (Class and Object)

**类 (Class)** 是对象的蓝图或模板，定义了对象具有的属性和方法。**对象 (Object)** 是类的实例，是内存中真实存在的数据结构。

```
┌─────────────────────────────────────────────────────────────────┐
│                      类与对象关系                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   类 (Class) - 模板                对象 (Object) - 实例          │
│   ┌─────────────────┐              ┌─────────────────┐          │
│   │   Car           │  实例化      │   car1          │          │
│   ├─────────────────┤  ────────▶   ├─────────────────┤          │
│   │ - brand         │              │ - brand: "Toyota"│         │
│   │ - color         │              │ - color: "Red"   │         │
│   │ - speed         │              │ - speed: 0       │         │
│   ├─────────────────┤              ├─────────────────┤          │
│   │ + start()       │              │ + start()       │          │
│   │ + accelerate()  │              │ + accelerate()  │          │
│   │ + brake()       │              │ + brake()       │          │
│   └─────────────────┘              └─────────────────┘          │
│                                                                 │
│                                     ┌─────────────────┐          │
│                                     │   car2          │          │
│                                     ├─────────────────┤          │
│                                     │ - brand: "BMW"  │          │
│                                     │ - color: "Black"│          │
│                                     │ - speed: 60     │          │
│                                     └─────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### UML类图表示

```
┌─────────────────────┐
│      Student        │
├─────────────────────┤
│ - name: String      │
│ - age: int          │
│ - grade: float      │
├─────────────────────┤
│ + study(): void     │
│ + exam(): float     │
│ + getName(): String │
└─────────────────────┘

符号说明：
-  `-` 表示 private (私有)
-  `+` 表示 public (公有)
-  `#` 表示 protected (保护)
```

#### 代码示例

```python
# Python中的类定义
class Student:
    # 类属性（所有实例共享）
    school = "University"
    
    # 构造方法 - 初始化对象
    def __init__(self, name, age):
        self.name = name      # 实例属性
        self._age = age       # 约定：受保护属性
        self.__grades = []    # 私有属性（名称修饰）
    
    # 实例方法
    def study(self, subject):
        print(f"{self.name} is studying {subject}")
    
    def exam(self, score):
        self.__grades.append(score)
        return sum(self.__grades) / len(self.__grades)
    
    # 属性装饰器
    @property
    def average_grade(self):
        if not self.__grades:
            return 0
        return sum(self.__grades) / len(self.__grades)

# 创建对象实例
student1 = Student("Alice", 20)
student2 = Student("Bob", 21)

# 使用对象
student1.study("Mathematics")
student1.exam(85)
student1.exam(90)
print(f"Average: {student1.average_grade}")  # 输出: Average: 87.5
```

---

### 2. 封装 (Encapsulation)

**封装**是面向对象的核心特性之一，它将数据（属性）和操作数据的方法绑定在一起，并隐藏对象的内部实现细节，仅对外暴露有限的接口。

```
┌─────────────────────────────────────────────────────────────────┐
│                      封装原理                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   外部世界          公共接口           内部实现                   │
│      │                  │                  │                    │
│      │    getBalance()  │                  │                    │
│      │◀─────────────────┤                  │                    │
│      │                  │                  │                    │
│      │   deposit(100)   │    ┌─────────────┴─────────────┐      │
│      │──────────────────▶───▶│  __balance: 1000          │      │
│      │                  │    │  __transaction_log: []    │      │
│      │                  │    │                           │      │
│      │   无法直接访问   │    │  def __validate():        │      │
│      │   account.__     │    │      # 内部验证逻辑       │      │
│      │   balance        │    │                           │      │
│      │        ❌        │    └───────────────────────────┘      │
│      │                  │                                       │
│                                                                 │
│   封装的优点：                                                  │
│   ✓ 数据保护 - 防止外部随意修改                                 │
│   ✓ 接口隔离 - 隐藏复杂实现                                     │
│   ✓ 易于维护 - 内部修改不影响外部                               │
│   ✓ 控制访问 - 通过getter/setter控制                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 访问修饰符

| 修饰符 | Python | Java/C++ | 访问范围 |
|--------|--------|----------|----------|
| 公有 (Public) | `name` | `public` | 任何地方都可访问 |
| 保护 (Protected) | `_name` | `protected` | 类内部及子类可访问 |
| 私有 (Private) | `__name` | `private` | 仅类内部可访问 |

#### 封装示例

```python
class BankAccount:
    """银行账户类 - 展示封装原则"""
    
    def __init__(self, account_number, owner, initial_balance=0):
        self.account_number = account_number  # 公有
        self._owner = owner                   # 保护
        self.__balance = initial_balance      # 私有
        self.__transaction_history = []       # 私有
    
    # Getter方法
    @property
    def balance(self):
        """获取余额 - 只读属性"""
        return self.__balance
    
    @property
    def owner(self):
        """获取账户持有人"""
        return self._owner
    
    # 业务方法
    def deposit(self, amount):
        """存款"""
        if amount <= 0:
            raise ValueError("存款金额必须大于0")
        self.__balance += amount
        self.__transaction_history.append(f"存款: +{amount}")
        return self.__balance
    
    def withdraw(self, amount):
        """取款 - 包含业务规则验证"""
        if amount <= 0:
            raise ValueError("取款金额必须大于0")
        if amount > self.__balance:
            raise ValueError("余额不足")
        self.__balance -= amount
        self.__transaction_history.append(f"取款: -{amount}")
        return self.__balance
    
    def get_transaction_history(self, limit=10):
        """获取交易历史 - 受控访问"""
        return self.__transaction_history[-limit:]

# 使用封装好的类
account = BankAccount("123456789", "张三", 1000)

# 正确的访问方式
print(account.balance)           # ✓ 通过getter访问
account.deposit(500)             # ✓ 通过业务方法修改
account.withdraw(200)            # ✓ 通过业务方法修改

# 错误的访问方式（在Python中仍可执行，但不建议）
# print(account.__balance)       # ✗ 直接访问私有属性 - AttributeError
# account.__balance = 999999     # ✗ 绕过业务规则
```

---

### 3. 继承 (Inheritance)

**继承**允许一个类（子类/派生类）基于另一个类（父类/基类）来构建，子类自动获得父类的属性和方法，并可以添加新的特性或重写父类的方法。

```
┌─────────────────────────────────────────────────────────────────┐
│                      继承层次结构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌─────────────┐                              │
│                    │   Animal    │  ← 基类/父类                  │
│                    ├─────────────┤                              │
│                    │ - name      │                              │
│                    │ - age       │                              │
│                    ├─────────────┤                              │
│                    │ + eat()     │                              │
│                    │ + sleep()   │                              │
│                    │ + speak()   │  ← 虚方法/抽象方法            │
│                    └──────┬──────┘                              │
│                           │                                     │
│           ┌───────────────┼───────────────┐                     │
│           │               │               │                     │
│           ▼               ▼               ▼                     │
│    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│    │    Dog      │ │     Cat     │ │    Bird     │  ← 派生类    │
│    ├─────────────┤ ├─────────────┤ ├─────────────┤              │
│    │ - breed     │ │ - color     │ │ - wing_span │              │
│    ├─────────────┤ ├─────────────┤ ├─────────────┤              │
│    │ + speak()   │ │ + speak()   │ │ + speak()   │  ← 重写      │
│    │ + fetch()   │ │ + climb()   │ │ + fly()     │  ← 扩展      │
│    └─────────────┘ └─────────────┘ └─────────────┘              │
│                                                                 │
│   继承类型：                                                    │
│   • 单继承 - 一个子类只有一个父类 (Java, Python支持)            │
│   • 多继承 - 一个子类有多个父类 (C++, Python支持)               │
│   • 多层继承 - A→B→C 的继承链                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 继承代码示例

```python
# 基类
class Animal:
    """动物基类"""
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def eat(self):
        print(f"{self.name} is eating")
    
    def sleep(self):
        print(f"{self.name} is sleeping")
    
    def speak(self):
        """抽象方法 - 子类必须重写"""
        raise NotImplementedError("子类必须实现speak方法")
    
    def introduce(self):
        return f"我是{self.name}，今年{self.age}岁"

# 派生类 - Dog
class Dog(Animal):
    """狗类"""
    
    def __init__(self, name, age, breed):
        super().__init__(name, age)  # 调用父类构造方法
        self.breed = breed           # 新增属性
    
    def speak(self):
        """重写父类方法"""
        return f"{self.name} says: Woof!"
    
    def fetch(self):
        """新增方法"""
        print(f"{self.name} is fetching the ball")

# 派生类 - Cat
class Cat(Animal):
    """猫类"""
    
    def __init__(self, name, age, color):
        super().__init__(name, age)
        self.color = color
    
    def speak(self):
        """重写父类方法"""
        return f"{self.name} says: Meow!"
    
    def climb(self):
        """新增方法"""
        print(f"{self.name} is climbing the tree")

# 使用继承
dog = Dog("Buddy", 3, "Golden Retriever")
cat = Cat("Whiskers", 2, "Orange")

# 继承的方法
print(dog.introduce())   # 继承自Animal
dog.eat()                # 继承自Animal

# 重写的方法
print(dog.speak())       # Dog的speak: Woof!
print(cat.speak())       # Cat的speak: Meow!

# 新增的方法
dog.fetch()
cat.climb()
```

#### 方法重写 vs 方法重载

| 特性 | 方法重写 (Override) | 方法重载 (Overload) |
|------|--------------------|--------------------|
| 发生位置 | 父子类之间 | 同一个类中 |
| 方法签名 | 必须完全相同 | 必须不同（参数列表） |
| 目的 | 改变父类行为 | 提供多种调用方式 |
| Python支持 | ✓ | ✗（可通过默认参数模拟） |
| Java/C++支持 | ✓ | ✓ |

```python
# Python中的"重载"模拟（使用默认参数和*args）
class Calculator:
    def add(self, a, b=0, c=0):
        """支持add(x), add(x,y), add(x,y,z)"""
        return a + b + c
    
    def sum_all(self, *args):
        """接受任意数量的参数"""
        return sum(args)

# 使用
calc = Calculator()
print(calc.add(5))           # 5
print(calc.add(5, 3))        # 8
print(calc.add(5, 3, 2))     # 10
print(calc.sum_all(1,2,3,4,5)) # 15
```

---

### 4. 多态 (Polymorphism)

**多态**意味着"多种形式"，它允许子类对象被当作父类对象使用，同时保持各自的行为特性。多态使得同样的接口可以有不同的实现。

```
┌─────────────────────────────────────────────────────────────────┐
│                      多态原理                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   统一接口调用                    不同实际执行                   │
│                                                                 │
│   ┌─────────────┐                                               │
│   │  animal:    │                                               │
│   │  Animal     │                                               │
│   └──────┬──────┘                                               │
│          │                                                      │
│          │ animal.speak()   ┌─────────────────────────────┐     │
│          │ ◀────────────────│ 实际对象类型决定执行哪个方法 │     │
│          │                  └─────────────────────────────┘     │
│          │                                                      │
│    ┌─────┴─────┬─────────┐                                      │
│    ▼           ▼         ▼                                      │
│ ┌──────┐   ┌──────┐  ┌──────┐                                   │
│ │ Dog  │   │ Cat  │  │ Bird │  ← 实际对象                       │
│ └──┬───┘   └──┬───┘  └──┬───┘                                   │
│    │          │         │                                       │
│    ▼          ▼         ▼                                       │
│ "Woof!"   "Meow!"   "Tweet!"  ← 不同结果                        │
│                                                                 │
│   多态实现方式：                                                │
│   • 编译时多态 - 方法重载 (静态绑定)                            │
│   • 运行时多态 - 方法重写 + 动态绑定 (动态派发)                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 多态示例

```python
# 多态演示
class Animal:
    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class Cow(Animal):
    def speak(self):
        return "Moo!"

# 多态函数 - 接受任何Animal类型
def animal_concert(animals):
    """动物音乐会 - 展示多态"""
    for animal in animals:
        print(f"{type(animal).__name__}: {animal.speak()}")

# 使用多态
animals = [Dog(), Cat(), Cow(), Dog()]
animal_concert(animals)

# 输出:
# Dog: Woof!
# Cat: Meow!
# Cow: Moo!
# Dog: Woof!
```

#### 鸭子类型 (Duck Typing)

Python是动态类型语言，支持"鸭子类型"——如果一个对象走起来像鸭子、叫起来像鸭子，那它就是鸭子。

```python
# 鸭子类型示例 - 不继承自同一基类，但有相同接口
class Duck:
    def quack(self):
        return "Quack!"
    def fly(self):
        return "Flapping wings"

class Person:
    def quack(self):
        return "I'm quacking like a duck!"
    def fly(self):
        return "I'm flapping my arms"

# 鸭子类型函数
def make_it_quack(duck_like):
    """不要求继承关系，只要有quack方法即可"""
    print(duck_like.quack())

# 两者都可以调用
make_it_quack(Duck())   # Quack!
make_it_quack(Person()) # I'm quacking like a duck!
```

---

### 5. 抽象 (Abstraction)

**抽象**是隐藏复杂实现细节，只展示必要功能的过程。在面向对象中，抽象通过抽象类和接口来实现。

```
┌─────────────────────────────────────────────────────────────────┐
│                      抽象类 vs 接口                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   抽象类 (Abstract Class)        接口 (Interface)               │
│   ┌─────────────────────┐        ┌─────────────────────┐        │
│   │    Shape            │        │    Drawable         │        │
│   ├─────────────────────┤        ├─────────────────────┤        │
│   │ - x, y: 位置坐标    │        │ + draw(): void      │        │
│   ├─────────────────────┤        │ + resize(): void    │        │
│   │ + move()            │        └─────────────────────┘        │
│   │ + draw() [抽象]     │                  ▲                    │
│   │ + area() [抽象]     │                  │ 实现               │
│   └─────────────────────┘                  │                    │
│            ▲                               │                    │
│            │ 继承                   ┌──────┴──────┐             │
│   ┌────────┴────────┐               │  Circle     │             │
│   │                 │               │  Rectangle  │             │
│   ▼                 ▼               └─────────────┘             │
│ ┌───────┐      ┌────────┐                                       │
││Circle │      │Rectangle│                                       │
│└───────┘      └────────┘                                       │
│                                                                 │
│   区别：                                                        │
│   • 抽象类可以有实现代码，接口只有声明                          │
│   • 单继承（一个类只能有一个父类）                              │
│   • 多实现（一个类可以实现多个接口）                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Python中的抽象类

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    """抽象基类 - 形状"""
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def move(self, dx, dy):
        """具体方法 - 所有形状都可以移动"""
        self.x += dx
        self.y += dy
        print(f"Moved to ({self.x}, {self.y})")
    
    @abstractmethod
    def area(self):
        """抽象方法 - 子类必须实现"""
        pass
    
    @abstractmethod
    def draw(self):
        """抽象方法 - 子类必须实现"""
        pass

class Circle(Shape):
    """圆形"""
    
    def __init__(self, x, y, radius):
        super().__init__(x, y)
        self.radius = radius
    
    def area(self):
        """实现抽象方法"""
        import math
        return math.pi * self.radius ** 2
    
    def draw(self):
        """实现抽象方法"""
        print(f"Drawing circle at ({self.x}, {self.y}) with radius {self.radius}")

class Rectangle(Shape):
    """矩形"""
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height
    
    def area(self):
        """实现抽象方法"""
        return self.width * self.height
    
    def draw(self):
        """实现抽象方法"""
        print(f"Drawing rectangle at ({self.x}, {self.y}) "
              f"with size {self.width}x{self.height}")

# 使用
shapes = [Circle(0, 0, 5), Rectangle(10, 10, 4, 6)]

for shape in shapes:
    shape.draw()
    print(f"Area: {shape.area():.2f}")
    shape.move(5, 5)
    print()

# 错误：不能直接实例化抽象类
# shape = Shape()  # TypeError: Can't instantiate abstract class
```

---

## 关系类型

### 1. 关联 (Association)

两个类之间存在语义连接，但彼此独立。

```python
class Professor:
    def __init__(self, name):
        self.name = name

class Student:
    def __init__(self, name):
        self.name = name
        self.advisor = None  # 关联关系
    
    def set_advisor(self, professor):
        self.advisor = professor

# 使用
prof = Professor("Dr. Smith")
student = Student("Alice")
student.set_advisor(prof)  # 建立关联
```

### 2. 聚合 (Aggregation)

"has-a"关系，整体包含部分，但部分可以独立存在。

```python
class Department:
    """部门 - 整体"""
    def __init__(self, name):
        self.name = name
        self.professors = []  # 聚合关系
    
    def add_professor(self, professor):
        self.professors.append(professor)

class Professor:
    """教授 - 部分"""
    def __init__(self, name):
        self.name = name

# 教授可以独立存在
prof1 = Professor("Dr. A")
prof2 = Professor("Dr. B")

# 部门包含教授（聚合）
dept = Department("CS")
dept.add_professor(prof1)
dept.add_professor(prof2)

# 部门解散，教授仍然存在
```

### 3. 组合 (Composition)

强"has-a"关系，部分不能脱离整体存在。

```python
class Car:
    """汽车 - 整体"""
    def __init__(self, model):
        self.model = model
        # 组合关系 - 引擎随汽车创建而创建
        self.engine = Engine(200)  
        self.wheels = [Wheel() for _ in range(4)]

class Engine:
    """引擎 - 部分"""
    def __init__(self, horsepower):
        self.horsepower = horsepower

class Wheel:
    """轮子 - 部分"""
    def __init__(self):
        self.size = 17

# 创建汽车时，引擎和轮子自动创建
car = Car("Tesla Model 3")
# 汽车销毁时，引擎和轮子也应销毁
```

### 4. 依赖 (Dependency)

一个类使用另一个类，是最弱的关系。

```python
class PaymentProcessor:
    """支付处理器"""
    def process(self, order, payment_method):
        """依赖于Order和PaymentMethod"""
        amount = order.calculate_total()  # 使用Order
        return payment_method.charge(amount)  # 使用PaymentMethod

class Order:
    def calculate_total(self):
        return 100.0

class CreditCard:
    def charge(self, amount):
        return f"Charged ${amount} to credit card"
```

---

## 面向对象设计原则

### 1. 高内聚低耦合

- **高内聚 (High Cohesion)**：类的职责应该单一且相关，内部元素紧密联系
- **低耦合 (Low Coupling)**：类之间的依赖应最小化，修改一个类不影响其他类

```python
# ❌ 低内聚 - 一个类做太多不相关的事
class EmployeeManager:
    def calculate_pay(self): ...      # 工资计算
    def save_to_database(self): ...   # 数据存储
    def generate_report(self): ...    # 报表生成
    def send_email(self): ...         # 邮件发送

# ✅ 高内聚 - 职责分离
class PayrollCalculator: ...   # 只负责工资计算
class EmployeeRepository: ...  # 只负责数据存储
class ReportGenerator: ...     # 只负责报表生成
class EmailService: ...        # 只负责邮件发送
```

### 2. 迪米特法则 (Law of Demeter)

"只与直接的朋友交谈"——一个对象应尽量少地了解其他对象。

```python
# ❌ 违反迪米特法则 - 链式调用
customer.get_account().get_balance().deduct(amount)

# ✅ 遵循迪米特法则 - 封装细节
customer.deduct_from_account(amount)  # 由customer内部处理
```

### 3. 组合优于继承

优先使用组合来获得代码复用，而非继承。

```python
# ❌ 继承 - 脆弱的基类问题
class Bird:
    def fly(self):
        pass

class Ostrich(Bird):  # 鸵鸟是鸟，但不会飞！
    def fly(self):
        raise Exception("Ostriches can't fly!")

# ✅ 组合 - 行为委托
class FlyBehavior:
    def fly(self):
        pass

class CanFly(FlyBehavior):
    def fly(self):
        print("Flying!")

class CannotFly(FlyBehavior):
    def fly(self):
        print("I can't fly")

class Bird:
    def __init__(self, fly_behavior):
        self.fly_behavior = fly_behavior
    
    def perform_fly(self):
        self.fly_behavior.fly()

# 使用
sparrow = Bird(CanFly())
ostrich = Bird(CannotFly())
```

---

## 设计过程

```
面向对象设计的标准流程：

1. 需求分析
   └─ 识别名词（类候选）和动词（方法候选）

2. 识别对象和类
   └─ 从问题域提取关键实体

3. 确定关系
   └─ 继承、关联、聚合、组合

4. 定义属性和方法
   └─ 每个类的数据和行为

5. 设计模式应用
   └─ 在合适的地方使用设计模式

6. 迭代优化
   └─ 重构，应用SOLID原则
```

---

## 最佳实践

### 设计检查清单

```
□ 类的单一职责
  □ 每个类只有一个改变的理由
  □ 类名能准确描述其职责

□ 封装完整性
  □ 属性私有，通过方法访问
  □ 暴露最小必要接口

□ 继承正确使用
  □ "is-a"关系成立
  □ 里氏替换原则（LSP）满足
  □ 考虑组合是否更合适

□ 多态应用
  □ 使用接口/抽象类定义契约
  □ 避免类型检查（isinstance）

□ 代码复用
  □ 消除重复代码
  □ 使用模板方法或策略模式

□ 可测试性
  □ 依赖可注入
  □ 避免静态方法和单例滥用
```

---

## 面试要点

### 常见问题

**Q1: 面向对象的四大特性是什么？**
> **封装**：隐藏内部实现，暴露接口；**继承**：复用代码，建立层次；**多态**：同一接口，不同实现；**抽象**：提取共性，简化复杂。其中封装是基础，多态是最高境界。

**Q2: 抽象类和接口有什么区别？**
> 抽象类可以有实现代码和状态，接口只有方法声明；一个类只能继承一个抽象类，但可以实现多个接口；抽象类表示"is-a"关系，接口表示"can-do"能力。Java 8+接口可以有默认方法，但目的不同。

**Q3: 多态是如何实现的？**
> 运行时多态通过虚函数表（vtable）实现。编译器为每个类创建虚函数表，对象持有指向该表的指针。调用虚方法时，通过对象指针找到vtable，再找到实际方法地址。这个过程称为动态绑定或后期绑定。

**Q4: 组合和继承的区别？什么时候用哪个？**
> 继承是"is-a"关系（狗是动物），组合是"has-a"关系（汽车有引擎）。优先使用组合，因为它更灵活、耦合更低。只有当真正的层次关系存在且LSP满足时才使用继承。组合可以在运行时改变行为，继承是静态的。

**Q5: 什么是高内聚低耦合？**
> 高内聚指模块内部元素紧密相关，职责单一；低耦合指模块间依赖最小。好处是：易于理解、测试、维护和复用。实现方式：单一职责原则、依赖注入、接口隔离、迪米特法则等。

**Q6: Python中的`__init__`、`__new__`、`__call__`有什么区别？**
> `__new__`是构造方法，创建并返回实例，在`__init__`之前执行；`__init__`是初始化方法，设置实例属性；`__call__`使实例可调用，实现函数对象。元类可以通过`__new__`控制实例创建过程。

---

## 相关概念

### 设计原则与模式 (Design Principles & Patterns)
- [SOLID原则](./solid-principles.md) - 面向对象设计的五个基本原则
- [设计模式](./design-patterns.md) - 面向对象设计模式的分类和应用

### 软件架构 (Software Architecture)
- [架构模式](./architecture-patterns.md) - 软件架构的通用解决方案
- [微服务架构](./architecture-patterns/microservices.md) - 分布式服务架构设计
- [事件驱动架构](./architecture-patterns/event-driven.md) - 基于事件的系统架构

### 编程范式 (Programming Paradigms)
- [单元测试](./unit-testing.md) - 面向对象代码的测试策略
- [代码审查](./code-review.md) - 面向对象设计的代码评审实践
- [重构](./refactoring.md) - 改善既有代码的设计

### 领域建模 (Domain Modeling)
- [领域驱动设计](./ddd.md) - 复杂的面向对象设计方法论
- [API设计](./api-design.md) - 面向对象系统的接口设计
### 数据结构基础 (Data Structures)

- [数组](../computer-science/data-structures/array.md) - 面向对象中的集合与容器实现基础
- [链表](../computer-science/data-structures/linked-list.md) - 动态数据结构的面向对象设计
- [哈希表](../computer-science/data-structures/hash-table.md) - 集合类与映射类的内部实现

### 系统与安全 (Systems & Security)

- [进程与线程](../computer-science/systems/process.md) - 面向对象并发编程的基础
- [内存管理](../computer-science/systems/memory-management.md) - 对象生命周期与内存分配
- [身份认证](../security/authentication.md) - 面向对象系统的安全设计

---

## 参考资料

1. "Object-Oriented Analysis and Design with Applications" by Grady Booch
2. "Design Patterns: Elements of Reusable Object-Oriented Software" by GoF
3. "Clean Code" by Robert C. Martin
4. Python官方文档: https://docs.python.org/3/tutorial/classes.html
5. Wikipedia: Object-oriented programming
