# 步长 (Stride)

步长（Stride）是内存寻址中的重要概念，指相邻元素在内存地址上的间隔。

## 基本定义

```
地址计算公式：
address = base_address + index × stride

- base_address: 起始地址
- index: 元素索引
- stride: 步长（相邻元素间的字节数）
```

## 步长示例

### 数组访问
```
数组元素大小为4字节（int32）：
- 连续存储：stride = 4
  arr[0] @ 0x1000
  arr[1] @ 0x1004  (stride = 4)
  arr[2] @ 0x1008  (stride = 4)

- 跨步访问（矩阵行优先取列）：stride = 行大小
  matrix[0][0] @ 0x1000
  matrix[1][0] @ 0x1040  (stride = 64, 假设每行16个int)
  matrix[2][0] @ 0x1080
```

### 不同数据类型的步长
| 数据类型 | 大小 | 步长（连续存储） |
|---------|------|-----------------|
| int8/byte | 1字节 | 1 |
| int16 | 2字节 | 2 |
| int32/float | 4字节 | 4 |
| int64/double | 8字节 | 8 |
| 结构体 | 依定义 | sizeof(struct) |

## 步长与缓存性能

### 空间局部性
```
良好空间局部性（小步长）：
for i in range(n):
    access arr[i]  // stride = 4, 缓存友好

不良空间局部性（大步长）：
for i in range(n):
    access arr[i * 1024]  // stride = 4096, 缓存不友好
```

### 预取与向量化
- 固定小步长便于硬件预取
- SIMD指令需要连续内存访问（stride = 1）

## 相关概念

### 内存与寻址
- [内存寻址](./memory-addressing.md) - 步长在地址计算中的应用
- [内存管理](../computer-science/systems/memory-management.md) - 内存分配与布局
- [数组](../computer-science/data-structures/array.md) - 最基本的使用步长的数据结构
- [缓存](../computer-science/systems/cache.md) - 步长对缓存命中率的影响
