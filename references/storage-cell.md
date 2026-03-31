# 储存单元

储存单元（Storage Cell）是计算机[内存](../systems/memory.md)中最基本的存储单位，用于存储一个单位的[数据](./data.md)。每个储存单元通过唯一的[内存地址](./address.md)进行标识和访问。

## 储存单元的组成

### 位与字节
- [位](./bit.md)（bit）是信息的最小单位，表示 0 或 1
- [字节](./byte.md)（byte）是基本的储存单元，通常由 8 个位组成
- 现代计算机以字节为最小可寻址单位

### 地址映射
每个储存单元都有唯一的[地址](./address.md)，通过[内存寻址](./memory-addressing.md)可以精确定位和访问特定的储存单元。

## 储存单元的应用

### 数组存储
[数组](../computer-science/data-structures/array.md)通过连续的储存单元存储元素，利用地址计算实现 O(1) 时间复杂度的随机访问。

### 内存管理
[内存管理](../systems/memory-management.md)负责分配和回收储存单元，确保程序能够有效地使用内存资源。

## 相关概念

### 基础单位
- [位](./bit.md) - 最小信息单位
- [字节](./byte.md) - 基本储存单元
- [地址](./address.md) - 储存单元标识

### 寻址与访问
- [内存寻址](./memory-addressing.md) - 定位储存单元的方法
- [线性地址空间](./linear-address-space.md) - 连续储存单元布局
- [类型宽度](./type-width.md) - 数据类型占用的储存单元数

### 数据结构
- [数组](../computer-science/data-structures/array.md) - 连续储存单元组织
- [链表](../computer-science/data-structures/linked-list.md) - 离散储存单元连接
- [栈](../computer-science/data-structures/stack.md) - 基于储存单元的 LIFO 结构
- [队列](../computer-science/data-structures/queue.md) - 基于储存单元的 FIFO 结构
