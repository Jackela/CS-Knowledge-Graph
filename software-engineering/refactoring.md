# 重构 (Refactoring)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自Martin Fowler的《重构》及公开技术资料。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 定义

**重构 (Refactoring)** 是在不改变代码外在行为的前提下，对代码内部结构进行修改，以提高其可理解性和降低修改成本。

---

## 重构原则

### 何时重构

```
┌─────────────────────────────────────────────────────────────┐
│                      重构时机                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 预备式重构 (Preparatory)                                 │
│     添加新功能前，先重构现有代码使其易于扩展                   │
│                                                             │
│  2.  opportunistic重构 (Opportunistic)                      │
│     理解代码时，顺便改善其结构                                 │
│                                                             │
│  3. 长期重构 (Long-term)                                     │
│     大规模架构调整，分阶段进行                                 │
│                                                             │
│  ⚠️ 不要重构的情况：                                          │
│     - 代码已经够好（不需要完美）                               │
│     - 项目即将发布（风险太大）                                 │
│     - 不理解代码作用时（先学习再重构）                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 重构流程

```
1. 确保有可靠的[单元测试](../software-engineering/unit-testing.md)
2. 识别代码异味 (Code Smell)
3. 小步修改代码
4. 频繁运行测试
5. 提交代码（可工作的状态）
```

---

## 代码异味 (Code Smells)

### Bloaters（臃肿）

| 异味 | 描述 | 重构手法 |
|------|------|----------|
| **长方法** (Long Method) | 方法超过10-20行 | [提炼函数](#提炼函数-extract-function) |
| **大类** (Large Class) | 类承担过多职责 | [提炼类](#提炼类-extract-class) |
| **长参数列表** (Long Parameter List) | 参数超过3-4个 | [引入参数对象](#引入参数对象-introduce-parameter-object) |
| **数据泥团** (Data Clumps) | 总是一起出现的数据 | [提炼类](#提炼类-extract-class) |

### Object-Orientation Abusers（面向对象误用）

| 异味 | 描述 | 重构手法 |
|------|------|----------|
| ** switch惊悚** (Switch Statements) | 过多的条件分支 | [多态取代条件](#以多态取代条件表达式-replace-conditional-with-polymorphism) |
| **临时字段** (Temporary Field) | 对象中某些字段只在特定情况使用 | [提炼类](#提炼类-extract-class) |
| **被拒绝的遗赠** (Refused Bequest) | 子类不需要父类的方法 | [委托取代继承](#以委托取代继承-replace-inheritance-with-delegation) |

### Change Preventers（变革阻碍）

| 异味 | 描述 | 重构手法 |
|------|------|----------|
| **发散式变化** (Divergent Change) | 一个类因多种原因被修改 | [提炼类](#提炼类-extract-class) |
| **霰弹式修改** (Shotgun Surgery) | 一个修改需要改动多个类 | [搬移函数](#搬移函数-move-function) |
| **并行继承体系** (Parallel Inheritance) | 每新增一个类，另一个继承体系也要新增 | [合并继承体系 | 委托 |

### Dispensables（可有可无）

| 异味 | 描述 | 重构手法 |
|------|------|----------|
| **重复代码** (Duplicate Code) | 相同或相似的代码多处出现 | [提炼函数](#提炼函数-extract-function) |
| **死代码** (Dead Code) | 不再使用的代码 | [删除死代码](#移除死代码-remove-dead-code) |
| **注释过多** (Comments) | 用注释解释糟糕的代码 | [用代码说话](#用函数取代注释-replace-comment-with-function) |

---

## 重构手法目录

### 提炼函数 (Extract Function)

```python
# ❌ 重构前：长方法
def print_owing(self):
    outstanding = 0
    
    # 打印横幅
    print("***********************")
    print("**** Customer Owes ****")
    print("***********************")
    
    # 计算欠款
    for order in self.orders:
        outstanding += order.amount
    
    # 打印详情
    print(f"name: {self.name}")
    print(f"amount: {outstanding}")

# ✅ 重构后：职责分离
def print_owing(self):
    self.print_banner()
    outstanding = self.calculate_outstanding()
    self.print_details(outstanding)

def print_banner(self):
    print("***********************")
    print("**** Customer Owes ****")
    print("***********************")

def calculate_outstanding(self):
    return sum(order.amount for order in self.orders)

def print_details(self, outstanding):
    print(f"name: {self.name}")
    print(f"amount: {outstanding}")
```

### 提炼类 (Extract Class)

```python
# ❌ 重构前：类承担多个职责
class Person:
    def __init__(self):
        self.name = ""
        self.office_area_code = ""
        self.office_number = ""
    
    def get_office_phone(self):
        return f"({self.office_area_code}) {self.office_number}"

# ✅ 重构后：职责分离
class PhoneNumber:
    def __init__(self):
        self.area_code = ""
        self.number = ""
    
    def __str__(self):
        return f"({self.area_code}) {self.number}"

class Person:
    def __init__(self):
        self.name = ""
        self.office_phone = PhoneNumber()
```

### 搬移函数 (Move Function)

```python
# ❌ 重构前：函数放在错误的类中
class Account:
    def __init__(self, type, days_overdrawn):
        self.type = type
        self.days_overdrawn = days_overdrawn
    
    def overdraft_charge(self):
        if self.type.is_premium:
            # ... 复杂计算
            pass
        else:
            return self.days_overdrawn * 1.75

# ✅ 重构后：函数放到使用它数据更多的类
class Account:
    def __init__(self, type, days_overdrawn):
        self.type = type
        self.days_overdrawn = days_overdrawn
    
    def overdraft_charge(self):
        return self.type.overdraft_charge(self.days_overdrawn)

class AccountType:
    def __init__(self, is_premium):
        self.is_premium = is_premium
    
    def overdraft_charge(self, days_overdrawn):
        if self.is_premium:
            # ... 复杂计算
            pass
        else:
            return days_overdrawn * 1.75
```

### 以多态取代条件表达式 (Replace Conditional with Polymorphism)

```python
# ❌ 重构前：大量条件分支
class Bird:
    def __init__(self, type):
        self.type = type
    
    def get_speed(self):
        if self.type == "EUROPEAN":
            return self.get_base_speed()
        elif self.type == "AFRICAN":
            return self.get_base_speed() - self.get_load_factor() * self.number_of_coconuts
        elif self.type == "NORWEGIAN_BLUE":
            return 0 if self.is_nailed else self.get_base_speed()

# ✅ 重构后：使用多态
from abc import ABC, abstractmethod

class Bird(ABC):
    @abstractmethod
    def get_speed(self):
        pass
    
    def get_base_speed(self):
        return 10

class EuropeanBird(Bird):
    def get_speed(self):
        return self.get_base_speed()

class AfricanBird(Bird):
    def __init__(self, number_of_coconuts):
        self.number_of_coconuts = number_of_coconuts
    
    def get_speed(self):
        return self.get_base_speed() - self.get_load_factor() * self.number_of_coconuts
    
    def get_load_factor(self):
        return 2

class NorwegianBlueBird(Bird):
    def __init__(self, is_nailed):
        self.is_nailed = is_nailed
    
    def get_speed(self):
        return 0 if self.is_nailed else self.get_base_speed()
```

---

## 重构与[设计模式](./design-patterns.md)

| 重构目标 | 适用的设计模式 |
|----------|----------------|
| 消除重复代码 | [策略模式](./design-patterns/behavioral/strategy.md) |
| 解耦对象创建 | [工厂模式](./design-patterns/creational/factory.md) |
| 动态改变行为 | [策略模式](./design-patterns/behavioral/strategy.md) |
| 统一接口 | [适配器模式](./design-patterns/structural/adapter.md) |
| 减少直接依赖 | [观察者模式](./design-patterns/behavioral/observer.md) |

---

## 工具支持

| 工具 | 语言 | 功能 |
|------|------|------|
| **PyCharm** | Python | 自动重构、代码分析 |
| **IntelliJ IDEA** | Java/Kotlin | 全面的重构支持 |
| **Visual Studio** | C# | 智能重构 |
| **Eclipse** | Java | 经典重构工具 |
| **Resharper** | .NET | 高级重构功能 |

---

## 相关概念

- [代码审查](../software-engineering/code-review.md) - 重构的触发点
- [单元测试](../software-engineering/unit-testing.md) - 重构的安全网
- [设计模式](../software-engineering/design-patterns.md) - 重构的目标结构
- [SOLID原则](../software-engineering/solid-principles.md) - 重构的指导原则
- [技术债务](../software-engineering/technical-debt.md) - 重构要解决的核心问题

---

## 参考资料

1. "Refactoring: Improving the Design of Existing Code" by Martin Fowler
2. "Refactoring to Patterns" by Joshua Kerievsky
3. "Clean Code" by Robert C. Martin
4. [Refactoring Guru](https://refactoring.guru/)

---

*最后更新：2024年*
