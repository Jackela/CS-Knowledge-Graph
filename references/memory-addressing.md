# 寻址

寻址公式 [地址](./address.md) = 起始[地址](./address.md) + [i](./indexing.md) × [步长](./stride.md)

每个元素在[线性地址空间](../../references/linear-address-space.md)上占据相同数量的[字节](../../references/byte.md)，这个数量被称为[类型宽度](../../references/type-width.md)。

相邻元素之间的距离就是[步长](../../references/stride.md)，通常与[类型宽度](../../references/type-width.md)相等。

## 相关概念

- [内存管理](../systems/memory-management.md) - 操作系统内存分配与回收
- [虚拟内存](../systems/virtual-memory.md) - 虚拟地址空间管理
- [储存单元](../references/storage-cell.md) - 内存寻址的基本单位
