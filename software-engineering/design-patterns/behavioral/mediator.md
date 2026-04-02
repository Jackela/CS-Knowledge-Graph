# 中介者模式 (Mediator Pattern)

## 概念

中介者模式（Mediator Pattern）是一种**行为型设计模式**，定义一个对象来封装一组对象的交互，使对象之间不需要显式地相互引用。

> **核心思想**: 集中管理对象间的通信，降低耦合。

## 适用场景

- 对象间通信复杂（网状依赖）
- 需要复用组件
- 需要集中控制交互

## 与外观模式的区别

| 模式 | 方向 | 目的 |
|------|------|------|
| 外观模式 | 单向简化 | 为子系统提供简化接口 |
| 中介者模式 | 双向协调 | 管理组件间的通信 |

## 相关概念

- [外观模式](../structural/facade.md) - 单向简化接口
- [观察者模式](./observer.md) - 发布订阅通信
- [组合模式](../structural/composite.md) - 对象结构组织

## 参考资料

- [Refactoring Guru - Mediator](https://refactoring.guru/design-patterns/mediator)
