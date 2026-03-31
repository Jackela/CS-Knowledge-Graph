# 单例模式 (Singleton Pattern)

## 概念

单例模式（Singleton Pattern）是一种**创建型设计模式**，确保一个类只有一个实例，并提供一个全局访问点。

> **核心思想**: 控制实例化过程，保证全局唯一性。

---

## 原理

### 为什么需要单例？

1. **资源共享**: 数据库连接池、线程池
2. **配置管理**: 全局配置对象
3. **硬件访问**: 打印机、文件系统

### 实现要点

```python
class Singleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

---

## 实现方式

### 1. 懒汉式（线程安全）

```python
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
```

### 2. 饿汉式

```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 3. 装饰器方式

```python
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    pass
```

---

## 示例

### 数据库连接池

```python
class DatabasePool:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connections = []
            cls._instance.max_connections = 10
        return cls._instance
    
    def get_connection(self):
        # 返回可用连接
        pass
```

---

## 面试要点

1. **线程安全**: 双重检查锁定（DCL）
2. **序列化**: 防止反序列化创建新实例
3. **反射**: 防止反射攻击
4. **缺点**: 违反单一职责原则，难以测试

---

## 相关概念

### 设计模式
- [工厂模式](./factory.md) - 对象创建模式对比
- [建造者模式](../creational/builder.md) - 复杂对象创建
- [享元模式](../structural/flyweight.md) - 共享实例

### 并发编程
- [线程同步](../../../computer-science/systems/synchronization.md) - 双重检查锁定
- [线程安全](../../../computer-science/systems/thread.md) - 并发访问控制
- [锁机制](../../../computer-science/systems/synchronization.md) - 互斥实现

### 系统实现
- [数据库连接池](../../../computer-science/databases/indexing.md) - 单例应用
- [缓存系统](../../../computer-science/systems/memory-management.md) - 全局缓存
- [配置管理](../../../computer-science/systems/file-systems.md) - 全局配置

### 复杂度分析
- [空间复杂度](../../../references/time-complexity.md) - 内存占用优化

- [工厂模式](./factory.md) - 另一种创建型模式
- [依赖注入](../architecture-patterns/dependency-injection.md) - 替代方案
