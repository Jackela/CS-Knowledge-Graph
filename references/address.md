# 地址

计算机的物理世界只有[存储单元](./storage-cell.md)。
要在程序中“找到”某个单元，就需要给它一个可被[引用](./reference.md)的名字。

地址是机器可识别的“位置[标识符](./identifier.md)”

一种从地址集合到[存储单元](./storage-cell.md)集合的[映射](./map.md)。
每个地址唯一对应一个可读写的[存储单元](./storage-cell.md)。

| 层次                         | 地址含义         | 举例          |
| -------------------------- | ------------ | ----------- |
| **[物理地址](./physical-address.md)** | [硬件总线](./hardware-bus.md)上的真实位置   | [DRAM](./dram.md) 中的单元编号 |
| **[线性地址](./linear-address.md)**   | 连续可加的逻辑位置    | [数组](../computer-science/data-structures/array.md)、[缓冲区](./buffer.md)、[文件偏移](./file-offset.md) |
| **[虚拟地址](./virtual-address.md)**  | 由操作系统映射的抽象位置 | [进程](./process.md)视角下的[指针](./pointer.md)    |
| **[符号地址](./symbol-address.md)** | 编译器/链接器分配的名字 | [变量名](./variable-name.md)、[函数名](./function-name.md)     |

## 相关概念

- [进程](../systems/process.md) - 进程地址空间视角
