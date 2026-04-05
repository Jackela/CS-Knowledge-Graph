# 迭代器模式 (Iterator Pattern)

## 概念

迭代器模式（Iterator Pattern）是一种**行为型设计模式**，提供一种方法来顺序访问聚合对象中的元素，而无需暴露其内部表示。

> **核心思想**: 将遍历逻辑从聚合对象中分离出来。

## 适用场景

- 需要遍历聚合对象
- 需要多种遍历方式
- 需要统一遍历接口

## 相关概念

- [组合模式](../structural/composite.md) - 常与迭代器配合使用遍历树形结构
- [访问者模式](./visitor.md) - 另一种遍历方式
- [集合](../../../computer-science/data-structures/array.md) - 被遍历的数据结构

## 参考资料

- [Refactoring Guru - Iterator](https://refactoring.guru/design-patterns/iterator)
