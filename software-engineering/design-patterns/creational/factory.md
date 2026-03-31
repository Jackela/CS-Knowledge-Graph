# 工厂模式 (Factory Pattern)

## 概念

工厂模式（Factory Pattern）是一种**创建型设计模式**，定义创建对象的接口，让子类决定实例化哪个类。

> **核心思想**: 将对象创建逻辑封装，解耦创建与使用。

---

## 分类

### 1. 简单工厂 (Simple Factory)

```python
class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        raise ValueError(f"Unknown type: {animal_type}")
```

### 2. 工厂方法 (Factory Method)

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class AnimalFactory(ABC):
    @abstractmethod
    def create_animal(self):
        pass

class DogFactory(AnimalFactory):
    def create_animal(self):
        return Dog()
```

### 3. 抽象工厂 (Abstract Factory)

```python
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self):
        pass
    
    @abstractmethod
    def create_checkbox(self):
        pass

class WindowsFactory(GUIFactory):
    def create_button(self):
        return WindowsButton()
    
    def create_checkbox(self):
        return WindowsCheckbox()
```

---

## 使用场景

1. **对象创建复杂**: 需要大量配置
2. **运行时决定类型**: 根据配置创建不同对象
3. **解耦**: 分离创建逻辑与业务逻辑

---

## 优点与缺点

**优点**:
- 解耦创建与使用
- 符合开闭原则
- 易于扩展

**缺点**:
- 增加系统复杂度
- 可能需要更多类

---

## 面试要点

1. **三种工厂的区别**: 简单、方法、抽象
2. **vs 单例**: 工厂创建多种，单例创建唯一
3. **Spring 中的 BeanFactory**: 典型应用

---

## 相关概念

### 设计模式
- [单例模式](./singleton.md) - 唯一实例的创建
- [建造者模式](../creational/builder.md) - 复杂对象构建
- [抽象工厂](../creational/abstract-factory.md) - 产品族创建
- [依赖注入](../../architecture-patterns.md) - 依赖管理

### 面向对象
- [面向对象设计](../../oop-design.md) - 设计原则基础
- [SOLID原则](../../solid-principles.md) - 开闭原则应用

### 系统实现
- [数据库连接池](../../../computer-science/systems/memory-management.md) - 资源对象管理
- [线程池](../../../computer-science/systems/thread.md) - 线程对象创建

### 复杂度分析
- [时间复杂度](../../../references/time-complexity.md) - 对象创建开销

- [抽象工厂](./abstract-factory.md) - 产品族创建
- [建造者模式](./builder.md) - 复杂对象构建
