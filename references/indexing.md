# 索引

索引是一个[映射](./map.md)[键](../../references/key.md)，把某个集合中的元素[映射](./map.md)到可被区分的位置。
索引是“命名方式”，不是[数据](./data.md)本身。


## 相关概念 (Related Concepts)

### 数据结构
- [B树](../computer-science/data-structures/b-tree.md)：数据库索引的核心数据结构，支持高效的范围查询
- [哈希表](../computer-science/data-structures/hash-table.md)：哈希索引的底层实现，支持 O(1) 等值查询
- [树](../computer-science/data-structures/tree.md)：索引结构的逻辑组织形式
- [数组](../computer-science/data-structures/array.md)：索引的物理存储实现基础

### 数据库
- [数据库索引](../computer-science/databases/indexing.md)：B+Tree 在数据库系统中的具体应用
- [关系模型](../computer-science/databases/relational-model.md)：索引在关系数据库中的组织方式
- [数据库范式](../computer-science/databases/normalization.md)：表结构设计对索引效率的影响

### 复杂度分析
- [时间复杂度](./time-complexity.md) ⏳：索引查询的时间复杂度分析
- [空间复杂度](./space-complexity.md) ⏳：索引存储的空间开销与权衡

### 系统实现
- [内存管理](../computer-science/systems/memory-management.md)：索引数据的内存分配与缓存策略
- [文件系统](../computer-science/systems/file-systems.md)：磁盘索引与文件存储的关系
- [地址](../address.md)：索引键到存储位置的映射机制
- [抽象数据类型](./adt.md)：索引作为抽象数据类型的定义与实现