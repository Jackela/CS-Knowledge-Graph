# 步长

在一个连续的地址空间里，如果我们按固定间距存放等宽元素，那么从一个元素的起始地址到下一个元素的起始地址之间就存在一个固定距离。


## 相关概念 (Related Concepts)

### 数据结构
- [数组](./array.md)：步长优化的基础数据结构
- [链表](./linked-list.md)：对比连续内存访问
- [堆](./heap.md)：利用步长优化的典型数据结构

### 算法
- [排序算法](../algorithms/sorting.md) ⏳：步长与缓存友好的排序
- [二分查找](../algorithms/binary-search.md) ⏳：步长为 1 的线性访问
- [分治算法](../algorithms/divide-conquer.md) ⏳：分块处理与步长选择
- [递归](../algorithms/recursion.md) ⏳：递归遍历中的步长模式

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) ⏳：步长访问的时间特性
- 空间局部性 ⏳：空间局部性原理与步长

- 空间局部性 ⏳：空间局部性原理与步长

### 系统实现
- 内存寻址：内存地址计算与步长
- 线性地址空间 - 连续内存与步长关系
- 线性地址空间：连续内存与步长关系
- [内存管理](../systems/memory-management.md) ⏳：内存分配与步长优化
- [虚拟内存](../systems/virtual-memory.md) ⏳：页式内存与步长访问