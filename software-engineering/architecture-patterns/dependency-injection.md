# 依赖注入 (Dependency Injection)

## 概念

依赖注入（Dependency Injection, DI）是一种**设计模式**，是实现控制反转（IoC）的一种技术，通过外部注入依赖对象而非内部创建。

> **核心思想**: 不要自己创建依赖，让外部注入进来。

## 为什么需要DI

### 传统方式的问题
```python
# ❌ 高耦合：UserService 直接依赖 MySQLDatabase
class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # 硬编码依赖
```

### DI解决方案
```python
# ✅ 低耦合：依赖由外部注入
class UserService:
    def __init__(self, database):
        self.db = database  # 依赖注入

# 使用
mysql_db = MySQLDatabase()
service = UserService(mysql_db)
```

## 注入方式

| 方式 | 说明 | 示例 |
|------|------|------|
| **构造函数注入** | 通过构造函数传参 | 最推荐 |
| **Setter注入** | 通过setter方法 | 可选依赖 |
| **接口注入** | 实现注入接口 | 较少使用 |
| **字段注入** | 直接注入字段 | 不推荐 |

## DI容器

主流框架的DI实现：

| 框架 | 语言 | 特点 |
|------|------|------|
| **Spring** | Java | 注解驱动，功能强大 |
| **Dagger** | Java/Android | 编译时生成，性能优秀 |
| **Angular DI** | TypeScript | 层级注入器 |
| **InversifyJS** | TypeScript | IoC容器 |
| **Dependency Injector** | Python | 轻量级 |

## 相关概念

- [SOLID原则](../solid-principles.md) - DI是实现依赖倒置原则的技术
- [工厂模式](../design-patterns/creational/factory.md) - 对象创建模式
- 控制反转(IoC) - 更宽泛的设计原则
- [单例模式](../design-patterns/creational/singleton.md) - DI容器常用单例管理
