# 内存管理 (Memory Management)

## 简介

**内存管理**是操作系统的核心功能，负责分配、回收和保护内存资源。有效的内存管理对系统性能和稳定性至关重要。

## 内存分配方式

### 1. 连续分配

#### 固定分区

```
内存划分为固定大小的分区:
┌─────────┐
│ 分区1   │ 100KB
├─────────┤
│ 分区2   │ 200KB
├─────────┤
│ 分区3   │ 300KB
├─────────┤
│ 分区4   │ 400KB
└─────────┘

内部碎片: 分配单元大于实际需要
```

#### 动态分区

```
初始空闲内存:
┌─────────────────────┐
│       空闲          │ 1MB
└─────────────────────┘

分配P1(200KB), P2(300KB):
┌─────────┬─────────┬─────────────┐
│   P1    │   P2    │    空闲      │
│  200KB  │  300KB  │    500KB    │
└─────────┴─────────┴─────────────┘

外部碎片: 空闲内存分散，无法满足大进程需求
```

### 2. 非连续分配

#### 分页（Paging）

```
逻辑地址空间          物理内存
┌─────────┐         ┌─────────┐
│  页0    │───────→│  帧0    │
├─────────┤         ├─────────┤
│  页1    │───────→│  帧3    │
├─────────┤         ├─────────┤
│  页2    │───────→│  帧1    │
└─────────┘         ├─────────┤
                    │  帧2    │
                    └─────────┘

页表: [0→0, 1→3, 2→1]
```

**地址转换**：
```
逻辑地址 = 页号 | 页内偏移
          
物理地址 = 帧号 | 页内偏移
```

#### 分段（Segmentation）

```
程序自然分段:
┌─────────────┐
│  代码段     │
├─────────────┤
│  数据段     │
├─────────────┤
│  堆栈段     │
└─────────────┘

段表:
段号 | 基址 | 长度 | 权限
 0   │ 1000 │ 500 │ R-X
 1   │ 2000 │ 800 │ RW-
 2   │ 5000 │ 400 │ RW-
```

## 页面置换算法

当物理内存不足时，需要置换页面。

### 1. 最佳置换（OPT）

置换未来最久不被访问的页面。**理论最优，不可实现**。

### 2. 先进先出（FIFO）

```python
def fifo(pages, capacity):
    """FIFO页面置换"""
    memory = []
    page_faults = 0
    
    for page in pages:
        if page not in memory:
            page_faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                memory.pop(0)  # 移除最早进入
                memory.append(page)
    
    return page_faults
```

**Belady异常**：物理页增加，缺页率反而上升。

### 3. 最近最少使用（LRU）

```python
from collections import OrderedDict

def lru(pages, capacity):
    """LRU页面置换"""
    memory = OrderedDict()
    page_faults = 0
    
    for page in pages:
        if page in memory:
            # 移动到末尾（最近使用）
            memory.move_to_end(page)
        else:
            page_faults += 1
            if len(memory) >= capacity:
                memory.popitem(last=False)  # 移除最久未使用
            memory[page] = True
    
    return page_faults
```

**实现方式**：
- 计数器
- 栈
- 近似实现：引用位（Clock算法）

### 4. 时钟算法（Clock / Second Chance）

```python
def clock(pages, capacity):
    """时钟页面置换"""
    frames = [None] * capacity  # 帧
    ref_bits = [0] * capacity   # 引用位
    hand = 0                    # 时钟指针
    page_faults = 0
    
    page_to_frame = {}
    
    for page in pages:
        if page in page_to_frame:
            # 页面在内存中，设置引用位
            frame = page_to_frame[page]
            ref_bits[frame] = 1
        else:
            # 缺页
            page_faults += 1
            
            # 找置换页面
            while True:
                if frames[hand] is None or ref_bits[hand] == 0:
                    # 找到可置换的
                    if frames[hand] is not None:
                        del page_to_frame[frames[hand]]
                    
                    frames[hand] = page
                    ref_bits[hand] = 0
                    page_to_frame[page] = hand
                    hand = (hand + 1) % capacity
                    break
                else:
                    # 给第二次机会
                    ref_bits[hand] = 0
                    hand = (hand + 1) % capacity
    
    return page_faults
```

## 内存碎片

| 类型 | 原因 | 解决 |
|------|------|------|
| 内部碎片 | 分配单元 > 请求大小 | 使用更小的分配单元 |
| 外部碎片 | 空闲内存分散 | 压缩、分页 |

## 面试要点

### Q1: 分页 vs 分段

| 特性 | 分页 | 分段 |
|------|------|------|
| 单位大小 | 固定（页） | 可变（段） |
| 透明性 | 对用户透明 | 用户可见 |
| 目的 | 消除外部碎片 | 满足逻辑需求 |
| 内部碎片 | 有 | 无（外部碎片） |

### Q2: 页面置换算法比较

| 算法 | 实现复杂度 | 性能 | 适用 |
|------|-----------|------|------|
| OPT | 不可能 | 最优 | 理论基准 |
| FIFO | 简单 | 差 | 教学 |
| LRU | 中等 | 好 | 通用 |
| Clock | 简单 | 接近LRU | 实际系统 |

## 相关概念 (Related Concepts)

### 数据结构
- [数组](../data-structures/array.md)：内存的连续分配
- [树](../data-structures/tree.md)：内存分配的树形结构

### 算法
- [内存管理](./memory-management.md)：内存分配策略

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：内存访问与分配的时间效率
- [空间复杂度](../../references/space-complexity.md)：内存碎片与利用率

### 系统实现
- [虚拟内存](./virtual-memory.md)：分页与分段机制
- [进程](./process.md)：进程的地址空间
- [文件系统](./file-systems.md)：磁盘管理与内存映射
- [虚拟内存](../systems/virtual-memory.md)：分页与分段机制
- [操作系统](./os.md) - 内存管理的系统基础

- [内存寻址](../../references/memory-addressing.md) - 地址转换基础
- [线性地址空间](../../references/linear-address-space.md) - 连续地址管理

## 参考资料

1. 《操作系统概念》第8章 - 内存管理策略
2. Memory management - Wikipedia
