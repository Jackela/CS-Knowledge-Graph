# 树状数组 (Fenwick Tree / Binary Indexed Tree)

## 简介
**树状数组**（又称**二叉索引树**，Binary Indexed Tree，简称BIT）是一种高效支持前缀和查询和单点更新的数据结构。它利用二进制表示的特性，在 $O(\log n)$ 时间内完成查询和更新操作，比线段树更省空间，代码更简洁。

## 核心概念
- **lowbit操作**：$lowbit(x) = x \& (-x)$，获取x的最低位1对应的值
- **树形结构**：利用数组模拟树结构，节点间通过lowbit建立父子关系
- **前缀和**：每个节点存储某一段区间的和，区间长度为lowbit(index)
- **高效更新**：单点更新时，只需修改相关的 $O(\log n)$ 个节点

## 实现方式
```python
class FenwickTree:
    def __init__(self, size):
        self.n = size
        self.tree = [0] * (self.n + 1)  # 1-indexed
    
    def lowbit(self, x):
        """获取最低位的1对应的值"""
        return x & (-x)
    
    def update(self, index, delta):
        """在位置index增加delta（单点更新）"""
        while index <= self.n:
            self.tree[index] += delta
            index += self.lowbit(index)
    
    def query(self, index):
        """查询前缀和 [1, index]"""
        res = 0
        while index > 0:
            res += self.tree[index]
            index -= self.lowbit(index)
        return res
    
    def range_query(self, left, right):
        """查询区间和 [left, right]"""
        return self.query(right) - self.query(left - 1)

# 使用示例
arr = [0, 1, 3, 5, 7, 9, 11]  # 1-indexed，arr[0]不使用
ft = FenwickTree(len(arr) - 1)

# 初始化树状数组
for i in range(1, len(arr)):
    ft.update(i, arr[i])

print(ft.query(4))           # 前缀和 1+3+5+7 = 16
print(ft.range_query(2, 5))  # 区间和 3+5+7+9 = 24

ft.update(3, 2)              # 位置3增加2，arr[3]从5变为7
print(ft.range_query(2, 5))  # 新区间和 3+7+7+9 = 26
```

## 应用场景
- **前缀和查询**：快速计算数组前n项的和
- **区间求和**：通过前缀和差分计算任意区间和
- **逆序对统计**：归并排序或树状数组统计逆序对数量
- **动态频率统计**：实时统计元素出现频率的累积分布

## 面试要点
1. **Q: 树状数组为什么叫"树状"？它是树吗？**
   A: 树状数组使用数组实现，但节点间的关系形成树形结构。每个节点负责一个区间，区间长度为lowbit(index)。父子关系通过index ± lowbit(index) 建立，逻辑上是一棵树。

2. **Q: lowbit操作的原理是什么？**
   A: 利用补码表示，-x的二进制是x的补码（按位取反后加1）。x & (-x)可以提取出最低位的1。例如：x=12(1100)，-x=0100，x&(-x)=0100=4。

3. **Q: 树状数组支持区间修改吗？**
   A: 普通树状数组支持单点修改、区间查询。通过差分技巧可以实现区间修改、单点查询，或者使用两个树状数组实现区间修改、区间查询。

4. **Q: 树状数组和线段树的比较？**
   A: 树状数组代码短、常数小、空间省（$O(n)$ vs $O(4n)$），但功能较弱，通常只用于前缀和相关操作。线段树功能更强大，支持任意区间操作。

## 相关概念

### 数据结构
- [线段树](./segment-tree.md) - 功能更强大的区间数据结构
- [数组](./array.md) - 树状数组的底层存储
- [二叉树](./binary-tree.md) - 树状数组的逻辑结构

### 算法
- [二分查找](../algorithms/binary-search.md) - 利用前缀和进行二分
- [前缀和技巧](../algorithms/dynamic-programming.md) - 相关应用场景

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 查询/更新 $O(\log n)$

### 系统实现
- [数据库索引](../databases/indexing.md) - 前缀查询的应用
