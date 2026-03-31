# 数组

计算机只有线性地址空间上的比特。
要把"第 i 个元素"放进机器，就必须给出从[索引](../../references/indexing.md)到地址的稳定[映射](./map.md)规则。

数组不是“某种神秘的容器”，而是对下述两件事的[约定](./convention.md)：

1. 一个有限、连续的索引集合：{0, 1, 2, …, n-1}

[数组](./array.md) 是最基础的抽象数据类型之一。

## 相关概念

### 数据结构
- [数组](./array.md) - 连续内存存储结构
- [链表](./linked-list.md) - 动态链式存储
- [栈](./stack.md) - LIFO 数据结构
- [队列](./queue.md) - FIFO 数据结构

### 算法
- [排序算法](../algorithms/sorting.md) - 数组是最常用的排序数据结构
- [二分查找](../algorithms/binary-search.md) - 依赖有序数组
- [分治算法](../algorithms/divide-conquer.md) - 基于数组划分

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 数组操作复杂度分析
- [空间复杂度](./space-complexity.md) - 内存占用评估

### 系统实现
- [内存寻址](../../references/memory-addressing.md) - 数组底层内存映射
- [储存单元](../../references/storage-cell.md) - 数组元素存储的基本单元
- 线性地址空间 - 连续内存管理
- [步长](./stride.md) - 元素间距与缓存优化
- [储存单元](../../references/storage-cell.md) - 数组元素存储的基本单元
- [线性地址空间](../../references/linear-address-space.md) - 连续内存管理
- [步长](./stride.md) - 元素间距与缓存优化
- [约定](./convention.md) - 数组的实现约定
