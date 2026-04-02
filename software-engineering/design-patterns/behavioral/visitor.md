# 访问者模式 (Visitor Pattern)

## 概念

访问者模式（Visitor Pattern）是一种**行为型设计模式**，允许在不改变元素类的前提下定义新的操作。

> **核心思想**: 将操作与对象结构分离。

## 适用场景

- 需要对对象结构中的元素执行多种不同操作
- 对象结构稳定，但操作经常变化
- 需要避免污染元素类

## 相关概念

- [迭代器模式](./iterator.md) - 另一种遍历方式
- [组合模式](../structural/composite.md) - 常与访问者配合使用
- [策略模式](./strategy.md) - 类似的解耦思想

## 参考资料

- [Refactoring Guru - Visitor](https://refactoring.guru/design-patterns/visitor)
