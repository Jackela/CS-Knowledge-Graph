# 储存单元

储存单元（Storage Cell）是计算机内存中最基本的存储单位，用于存储一个单位的数据。每个储存单元通过唯一的内存地址进行标识和访问。

## 储存单元的组成

### 位与字节
- [位](./bit.md)（bit）是信息的最小单位，表示 0 或 1
- 字节（byte）是基本的储存单元，通常由 8 个位组成
- 现代计算机以字节为最小可寻址单位

### 地址映射
每个储存单元都有唯一的地址，通过[内存寻址](./memory-addressing.md)可以精确定位和访问特定的储存单元。

## 储存单元的应用

### 数组存储
[数组](../computer-science/data-structures/array.md)通过连续的储存单元存储元素，利用地址计算实现 O(1) 时间复杂度的随机访问。

### 内存管理
[内存管理](../computer-science/systems/memory-management.md)负责分配和回收储存单元，确保程序能够有效地使用内存资源。

### 基础单位
-  - 最小信息单位
- 字节 - 基本储存单元
- 地址 - 储存单元标识

### 寻址与访问
-  - 定位储存单元的方法
- [线性地址空间](./linear-address-space.md) - 连续储存单元布局
- [类型宽度](../computer-science/data-structures/stride.md) - 数据类型占用的储存单元数

### 数据结构
-  - 连续储存单元组织
- [链表](../computer-science/data-structures/linked-list.md) - 离散储存单元连接
- [栈](../computer-science/data-structures/stack.md) - 基于储存单元的 LIFO 结构
- [队列](../computer-science/data-structures/queue.md) - 基于储存单元的 FIFO 结构

## 相关概念 (Related Concepts)

### 计算机系统
-  - 操作系统内存分配与回收
- [虚拟内存](../computer-science/systems/virtual-memory.md) - 虚拟地址空间管理
- [进程](../computer-science/systems/process.md) - 程序执行的基本单位

### 数据存储
-  - 最小信息单位

### 编程基础
-  - 连续存储的数据结构
