# 线性地址空间（Linear Address Space）

是一种特殊的[地址空间](./address-space.md)，其地址可以被视为从 0 开始的整数序列。

在这种模型下：

1. [地址](./address.md)之间存在自然的加减关系；

2. 相邻地址的[差值](./stride.md)代表实际距离；

3.. 任意[连续区间](./interval.md)可以[映射](./map.md)为一段可寻址的[存储块](./memory-block.md)。

这就是[数组](../computer-science/data-structures/array.md)、[缓冲区](./buffer.md)、[文件偏移](./file-offset.md)等[线性数据结构](../computer-science/data-structures/linear-data-structure.md)的数学前提。
