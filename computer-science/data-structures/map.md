# 映射

一种[关系](../../references/relation.md)：表示[集合](../../references/set.md) A 中的每个[元素](../../references/element.md)都对应[集合](../../references/set.md) B 中的某个[元素](../../references/element.md)。

如果这种对应在 A 上是唯一的（同一个[键](../../references/key.md)不会映射到两个[值](../../references/value.md)），我们称它是一个[函数](../../references/function.md)。

| 属性                     | 说明                  |
| ---------------------- | ------------------- |
| **[定义域](../../references/domain.md)**        | 所有可能的[键](../../references/key.md)的[集合](../../references/set.md)      |
| **[值域](../../references/range.md)**          | 所有可能的[值](../../references/value.md)的[集合](../../references/set.md)    |
| **[确定性](../../references/deterministic.md)** | 给定[键](../../references/key.md)能确定唯一[值](../../references/value.md)           |
| **[非对称性](../../references/asymmetry.md)**               | 不保证反向唯一（多个[键](../../references/key.md)可映射到同一[值](../../references/value.md)） |


## 相关概念 (Related Concepts)

### 数据结构
- [哈希表](./hash-table.md) ⏳：Map的底层实现基础
- [数组](./array.md)：开放寻址法实现
- [红黑树](./red-black-tree.md)：有序Map的实现
- [集合](./set.md) ⏳：基于Map实现的集合

### 算法
- [哈希算法](../algorithms/hash-functions.md) ⏳：键的哈希计算
- [冲突解决](../algorithms/collision-resolution.md) ⏳：哈希冲突处理
- [排序](../algorithms/sorting.md)：Map键的有序遍历

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) ⏳：Map操作的时间复杂度
- [空间复杂度](../../references/space-complexity.md) ⏳：Map的空间开销

### 系统实现
- [内存管理](../systems/memory-management.md)：Map的动态扩容
- [并发控制](../databases/concurrency-control.md)：并发Map实现
- [同步机制](../systems/synchronization.md)：线程安全Map