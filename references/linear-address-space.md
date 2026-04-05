# 线性地址空间（Linear Address Space）

是一种特殊的[地址空间](./address-space.md)，其地址可以被视为从 0 开始的整数序列。

在这种模型下：

1. [地址](./address.md)之间存在自然的加减关系；

2. 相邻地址的[差值](../computer-science/data-structures/stride.md)代表实际距离；

3.. 任意连续区间可以[映射](../computer-science/data-structures/map.md)为一段可寻址的存储块。

这就是[数组](../computer-science/data-structures/array.md)等数据结构的数学前提。

## 相关概念

- [内存管理](../computer-science/systems/memory-management.md) - 操作系统内存分配
