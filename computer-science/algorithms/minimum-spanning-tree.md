# 最小生成树 (Minimum Spanning Tree)

## 简介

**最小生成树（Minimum Spanning Tree, MST）**是连通无向图的生成树中，所有边的权重之和最小的那棵生成树。生成树包含图中所有顶点，且是一棵树（无环，$|V|-1$条边）。

```
带权连通图:

    A ──4── B ──2── C
    │       │       │
    1       3       5
    │       │       │
    D ──6── E ──4── F

最小生成树（总权重 = 1+3+2+4+4 = 14）:

    A ──4── B ──2── C
    │       │
    1       3
    │       │
    D       E ──4── F
```

## MST性质

### 割性质（Cut Property）

对于图的任意割，横切边中权重最小的边必属于某棵MST。

### 环性质（Cycle Property）

对于图中任意环，环上权重最大的边不属于任何MST。

## Kruskal算法

### 算法思想

按权重从小到大选择边，不形成环则加入MST。

```python
def kruskal(n, edges):
    """
    n: 顶点数
    edges: [(weight, u, v), ...]
    返回: MST的边列表
    """
    # 按权重排序
    edges.sort()
    
    # 并查集
    parent = list(range(n))
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
            return True
        return False
    
    mst = []
    for weight, u, v in edges:
        if union(u, v):  # 不形成环
            mst.append((u, v, weight))
        if len(mst) == n - 1:
            break
    
    return mst
```

### 复杂度

- **时间**：$O(E \log E)$（排序主导）
- **空间**：$O(V)$

## Prim算法

### 算法思想

从一个顶点开始，每次选择与当前树相连的最小权重边。

```python
import heapq

def prim(graph, start=0):
    """
    graph: {u: [(v, weight), ...]}
    返回: MST的边列表
    """
    n = len(graph)
    visited = set([start])
    mst = []
    
    # 优先队列: (权重, u, v)
    pq = [(weight, start, v) for v, weight in graph[start]]
    heapq.heapify(pq)
    
    while pq and len(visited) < n:
        weight, u, v = heapq.heappop(pq)
        
        if v in visited:
            continue
        
        visited.add(v)
        mst.append((u, v, weight))
        
        for next_v, next_w in graph[v]:
            if next_v not in visited:
                heapq.heappush(pq, (next_w, v, next_v))
    
    return mst
```

### 复杂度

- **时间**：$O(E \log V)$（二叉堆）
- **空间**：$O(V)$

## 算法对比

| 特性 | Kruskal | Prim |
|------|---------|------|
| 策略 | 全局选边 | 局部扩展 |
| 数据结构 | 并查集 | 优先队列 |
| 适用 | 稀疏图 | 稠密图 |
| 时间 | $O(E \log E)$ | $O(E \log V)$ |

## 应用场景

1. **网络设计**：最小成本构建通信网络
2. **电路布线**：最小化线路总长度
3. **聚类分析**：单链接聚类
4. **近似算法**：TSP近似解

## 面试要点

### Q1: 证明MST的唯一性条件

当图中所有边权重不同时，MST唯一。若有相同权重边，可能存在多个MST。

### Q2: 次小生成树

```python
def second_mst(n, edges):
    """求次小生成树"""
    # 1. 求MST
    mst_edges = kruskal(n, edges)
    mst_weight = sum(w for _, _, w in mst_edges)
    
    # 2. 尝试替换每条边
    second_weight = float('inf')
    for u, v, w in mst_edges:
        # 临时移除这条边，求新的MST
        temp_edges = [e for e in edges if not (e[1] == u and e[2] == v)]
        temp_mst = kruskal(n, temp_edges)
        if len(temp_mst) == n - 1:
            temp_weight = sum(w for _, _, w in temp_mst)
            second_weight = min(second_weight, temp_weight)
    
    return second_weight
```

## 相关概念

- [并查集](../data-structures/disjoint-set.md) - Kruskal使用
- [贪心算法](../algorithms/greedy.md) - MST算法都是贪心
- [图遍历](../algorithms/graph-traversal.md)

## 参考资料

1. 《算法导论》第23章 - 最小生成树
2. Minimum spanning tree - Wikipedia
