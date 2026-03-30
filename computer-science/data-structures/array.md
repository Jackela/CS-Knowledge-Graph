# 数组

计算机只有[线性地址空间](../../references/linear-address-space.md)上的[比特](../../references/bit.md)。
要把"第 i 个[元素](.../references/element.md)"放进机器，就必须给出从[索引](../../references/indexing.md)到地址的稳定[映射](./map.md)规则。

数组不是“某种神秘的容器”，而是对下述两件事的[约定](./convention.md)：

1. 一个有限、连续的索引集合：{0, 1, 2, …, n-1}

2. 一条可计算、与 i 成线性关系的[寻址](../../references/memory-addressing.md)规则：给定起始[地址](./address.md)与固定[差值](./stride.md)，立刻算出第 i 个[元素](.../references/element.md)的地址
