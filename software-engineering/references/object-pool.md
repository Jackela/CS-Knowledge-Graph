# 对象池模式 (Object Pool Pattern)

## 概念

对象池模式（Object Pool Pattern）是一种**创建型设计模式**，用于管理可复用对象的集合，以减少频繁创建和销毁对象的开销。

> **核心思想**: 预创建对象，用完后归还，重复利用。

## 与享元模式的区别

| 模式 | 关注点 | 对象状态 |
|------|--------|----------|
| 享元模式 | 共享不可变对象 | 内部状态不可变 |
| 对象池 | 复用可变对象 | 对象状态可变，用完重置 |

## 常见应用

- 数据库连接池
- 线程池
- 内存池

## 相关概念

- [享元模式](../../software-engineering/design-patterns/structural/flyweight.md) - 另一种对象复用模式
- [单例模式](../../software-engineering/design-patterns/creational/singleton.md) - 池管理器常用单例
- [数据库连接池](../../computer-science/systems/memory-management.md) - 对象池典型应用

## 参考资料

- [Object Pool Pattern](https://sourcemaking.com/design_patterns/object_pool)
