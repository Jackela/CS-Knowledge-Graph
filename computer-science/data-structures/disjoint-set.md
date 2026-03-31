# 并查集 (Disjoint Set Union / Union-Find)

## 简介

**并查集（Disjoint Set Union, DSU）**，又称**联合-查找数据结构（Union-Find）**，是一种用于处理**不相交集合**的合并与查询问题的数据结构。它支持两种高效操作：

1. **Find（查找）**：确定元素属于哪个集合
2. **Union（合并）**：将两个集合合并为一个

```
初始: {1}, {2}, {3}, {4}, {5}

Union(1, 2):    {1, 2}, {3}, {4}, {5}
Union(3, 4):    {1, 2}, {3, 4}, {5}
Union(2, 3):    {1, 2, 3, 4}, {5}

Find(1) = Find(4) = 集合 {1,2,3,4} 的代表
Find(5) = 集合 {5} 的代表
```

并查集是**近乎常数时间**的数据结构，在图算法中有广泛应用。

## 原理 (Principles)

### 基本表示

使用**父指针数组**表示集合：

```
集合: {0, 1, 2}, {3, 4}, {5}

索引:  0  1  2  3  4  5
父节点: 0  0  0  3  3  5

树形表示:
    0      3      5
   / \     |
  1   2    4
```

- 根节点的父节点指向自己
- 每个集合是一棵树

### 优化策略

#### 1. 路径压缩（Path Compression）

查找时将路径上所有节点直接连接到根节点。

```
查找 4 前:         查找 4 后（路径压缩）:
    0                 0
   /|\               /|\
  1 2 3             1 2 3
     /                  |
    4                   4

Find(4) 路径: 4→3→0
压缩后: 4和3都直接指向0
```

#### 2. 按秩合并（Union by Rank/Size）

将较小的树合并到较大的树下，避免树过深。

```
按大小合并:

集合A: 100个元素    集合B: 10个元素
   0                   10
  /|\                 /|
 ...                 ...

合并: 将B的根指向A的根（小树并入大树）
```

## 实现 (Implementation)

```python
class UnionFind:
    def __init__(self, n):
        """初始化n个元素，每个元素自成一个集合"""
        self.parent = list(range(n))
        self.rank = [0] * n  # 秩（树的深度估计）
        self.size = [1] * n  # 集合大小
        self.count = n       # 连通分量数
    
    def find(self, x):
        """查找x的根节点（带路径压缩）"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # 递归压缩
        return self.parent[x]
    
    def union(self, x, y):
        """合并x和y所在的集合"""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False  # 已在同一集合
        
        # 按秩合并：将秩小的树合并到秩大的树下
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        
        self.parent[py] = px
        self.size[px] += self.size[py]
        
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        
        self.count -= 1
        return True
    
    def connected(self, x, y):
        """判断x和y是否连通"""
        return self.find(x) == self.find(y)
    
    def get_size(self, x):
        """获取x所在集合的大小"""
        return self.size[self.find(x)]
```

## 复杂度分析

使用**路径压缩**和**按秩合并**后：

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| Find | $O(\alpha(n))$ | 阿克曼函数的反函数 |
| Union | $O(\alpha(n))$ | 近似常数 |
| Connected | $O(\alpha(n))$ | 近似常数 |

其中 $\alpha(n)$ 是**阿克曼函数的反函数**，增长极其缓慢：
- $\alpha(n) < 5$ 对于所有实际应用的 $n$（$n < 2^{2^{2^{2^{16}}}}$）

因此，并查集操作可视为**常数时间** $O(1)$。

## 应用场景

### 1. 连通分量检测

```python
def count_components(n, edges):
    """统计无向图的连通分量数"""
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.count
```

### 2. Kruskal 最小生成树

```python
def kruskal(n, edges):
    """Kruskal算法求MST"""
    # edges: (weight, u, v)
    edges.sort()  # 按权重排序
    uf = UnionFind(n)
    mst = []
    
    for w, u, v in edges:
        if uf.union(u, v):  # 不形成环
            mst.append((u, v, w))
        if len(mst) == n - 1:
            break
    
    return mst
```

### 3. 检测环

```python
def has_cycle(n, edges):
    """检测无向图是否有环"""
    uf = UnionFind(n)
    for u, v in edges:
        if uf.connected(u, v):
            return True  # 形成环
        uf.union(u, v)
    return False
```

## 面试要点

### Q1: 并查集时间复杂度的证明

使用**逆阿克曼函数** $\alpha(n)$ 分析，增长极慢，实际可视为 $O(1)$。

### Q2: 带权并查集

维护节点到根节点的距离/关系。

```python
class WeightedUnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.weight = [0] * n  # 到父节点的权重
    
    def find(self, x):
        if self.parent[x] != x:
            root = self.find(self.parent[x])
            self.weight[x] += self.weight[self.parent[x]]
            self.parent[x] = root
        return self.parent[x]
```

## 相关概念

- [图](./graph.md) - 并查集的图论应用
- [树](./tree.md) - 父指针树表示
- [数组](./array.md) - 父指针数组实现
- [图](../data-structures/graph.md) - 并查集的图论应用
- [树](../data-structures/tree.md) - 父指针树表示
- [数组](../data-structures/array.md) - 父指针数组实现

### 算法
- [最小生成树](../algorithms/minimum-spanning-tree.md) - Kruskal算法核心
- [图遍历](../algorithms/graph-traversal.md) - 连通分量检测
- [动态规划](../algorithms/dynamic-programming.md) - 带权并查集优化

### 复杂度分析
- [时间复杂度分析](../../references/time-complexity.md) - 逆阿克曼函数分析
- [摊还分析](../../references/time-complexity.md) - 路径压缩的摊还复杂度
- [摊还分析](../../references/time-complexity.md) - 路径压缩的摊还复杂度

### 系统实现
- [网络](../../computer-science/networks/network-layer.md) - 网络连通性检测
- [数据库](../../computer-science/databases/indexing.md) - 等价类查询

- [图](./graph.md)
- [最小生成树](../algorithms/minimum-spanning-tree.md)
- [最小生成树](../algorithms/minimum-spanning-tree.md)
- [Kruskal算法](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)

## 参考资料

1. 《算法导论》第21章 - 用于不相交集合的数据结构
2. Disjoint-set data structure - Wikipedia
3. LeetCode 并查集专题
