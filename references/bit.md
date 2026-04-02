# 比特

计算机硬件只会区分两种物理状态——导通 / 断开、电压高 / 低、磁极正 / 负。
要让这些状态可被逻辑系统识别，就必须赋予它们一个抽象的名字：

"这两种状态" → 0 与 1（二元）

于是得到计算机信息的最小可区分单位：bit（比特）。

bit 是“二元信息单元”

| 概念           | 含义                      |
| ------------ | ----------------------- |
| **[比特](./bit.md)**  | 1 或 0 的单个状态             |
| **字节** | 通常为 8 bit 的最小可[寻址](./memory-addressing.md)单元      |
| **字**  | 由若干字节组成，是 CPU 一次操作的基本宽度 |


## 相关概念

- [内存寻址](./memory-addressing.md) — 比特在内存中的定位与访问机制
- [存储单元](./storage-cell.md) — 物理层面存储比特的硬件单元
- [内存管理](../computer-science/systems/memory-management.md) — 操作系统如何管理比特组成的内存空间
- [进程](../computer-science/systems/process.md) — 程序运行时对比特数据的处理与状态管理
- [数组](../computer-science/data-structures/array.md) — 比特按特定组织方式构成的线性数据结构
- [虚拟内存](../computer-science/systems/virtual-memory.md) — 通过地址映射扩展比特寻址能力的机制