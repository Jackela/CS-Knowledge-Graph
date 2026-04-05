# 线段树 (Segment Tree)

## 简介
**线段树**是一种用于处理区间查询和修改的平衡二叉树数据结构。它通过将区间不断二分，构建出一棵二叉树，使得区间查询和单点修改的时间复杂度均为 $O(\log n)$，适用于需要频繁区间操作的场景。

## 核心概念
- **区间划分**：每个节点代表一个区间，根节点表示整个区间，叶子节点表示单个元素
- **递归构建**：从根节点开始，将区间不断二分，直到区间长度为1
- **延迟更新**：使用懒惰标记（Lazy Propagation）优化区间修改，推迟更新操作到必要时执行
- **信息聚合**：每个节点存储其代表区间的聚合信息（如区间和、区间最值等）

## 实现方式
```python
class SegmentTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)  # 线段树数组，4倍空间
        self.lazy = [0] * (4 * self.n)  # 懒惰标记
        self.arr = arr
        self.build(0, 0, self.n - 1, arr)
    
    def build(self, node, l, r, arr):
        """构建线段树"""
        if l == r:
            self.tree[node] = arr[l]
            return
        mid = (l + r) // 2
        self.build(2 * node + 1, l, mid, arr)
        self.build(2 * node + 2, mid + 1, r, arr)
        self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]
    
    def push_down(self, node, l, r):
        """下传懒惰标记"""
        if self.lazy[node] != 0:
            mid = (l + r) // 2
            # 更新左子树
            self.tree[2 * node + 1] += self.lazy[node] * (mid - l + 1)
            self.lazy[2 * node + 1] += self.lazy[node]
            # 更新右子树
            self.tree[2 * node + 2] += self.lazy[node] * (r - mid)
            self.lazy[2 * node + 2] += self.lazy[node]
            self.lazy[node] = 0
    
    def update(self, node, l, r, ql, qr, val):
        """区间修改 [ql, qr] 增加 val"""
        if ql <= l and r <= qr:
            self.tree[node] += val * (r - l + 1)
            self.lazy[node] += val
            return
        self.push_down(node, l, r)
        mid = (l + r) // 2
        if ql <= mid:
            self.update(2 * node + 1, l, mid, ql, qr, val)
        if qr > mid:
            self.update(2 * node + 2, mid + 1, r, ql, qr, val)
        self.tree[node] = self.tree[2 * node + 1] + self.tree[2 * node + 2]
    
    def query(self, node, l, r, ql, qr):
        """区间查询 [ql, qr] 的和"""
        if ql <= l and r <= qr:
            return self.tree[node]
        self.push_down(node, l, r)
        mid = (l + r) // 2
        res = 0
        if ql <= mid:
            res += self.query(2 * node + 1, l, mid, ql, qr)
        if qr > mid:
            res += self.query(2 * node + 2, mid + 1, r, ql, qr)
        return res

# 使用示例
arr = [1, 3, 5, 7, 9, 11]
st = SegmentTree(arr)
print(st.query(0, 0, len(arr) - 1, 1, 4))  # 查询区间[1,4]的和: 3+5+7+9=24
st.update(0, 0, len(arr) - 1, 2, 3, 2)     # 区间[2,3]每个元素加2
print(st.query(0, 0, len(arr) - 1, 1, 4))  # 再次查询: 3+7+9+9=28
```

## 应用场景
- **区间最值查询**：查询数组某区间的最大值或最小值
- **区间和查询**：计算数组某区间元素之和，支持动态修改
- **区间更新**：批量修改数组某区间的值（配合懒惰标记）
- **矩形面积并**：计算多个矩形的并集面积（扫描线算法）

## 面试要点
1. **Q: 线段树的空间复杂度是多少？为什么？**
   A: 空间复杂度为 $O(4n)$。最坏情况下，线段树是一棵近似完全二叉树，深度约为 $\log_2 n$，节点数约为 $2n$。但为了防止数组越界，通常开 $4n$ 的空间。

2. **Q: 线段树和树状数组（Fenwick Tree）的区别是什么？**
   A: 线段树支持任意区间查询和区间修改，功能更强大；树状数组通常用于前缀和查询，代码更简洁，空间占用更少。线段树常数较大，树状数组常数较小。

3. **Q: 什么是懒惰标记（Lazy Propagation）？**
   A: 懒惰标记用于优化区间修改操作。当修改一个大区间时，不立即更新所有子节点，而是在当前节点打上标记，等到需要查询子节点信息时才将标记下传，从而保证 $O(\log n)$ 的时间复杂度。

4. **Q: 线段树的构建时间复杂度是多少？**
   A: 构建时间复杂度为 $O(n)$。每个节点只被访问一次，共约 $2n$ 个节点。

## 相关概念

### 数据结构
- [树状数组](./fenwick-tree.md) - 前缀和查询的替代方案
- [二叉树](./binary-tree.md) - 线段树的基础结构
- [完全二叉树](./complete-binary-tree.md) - 线段树的存储形式

### 算法
- [二分查找](../algorithms/binary-search.md) - 线段树查询基于二分思想
- [分治算法](../algorithms/divide-conquer.md) - 线段树构建使用分治策略

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 区间查询 $O(\log n)$

### 系统实现
- [数据库索引](../databases/indexing.md) - 区间查询在数据库中的应用
