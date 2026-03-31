# 最短路径 (Shortest Path)

## 简介

**最短路径问题**是图论中的经典问题，旨在寻找图中两个顶点之间的路径，使得路径上所有边的权重之和最小。最短路径算法在网络路由、地图导航、物流规划等领域有广泛应用。

```
带权图:

    4       1
A ───── B ───── C
│       │       │
│2      │3      │5
│       │       │
D ───── E ───── F
    1       2

A到F的最短路径: A → B → C → F (权重: 4+1+5=10)
              或 A → D → E → F (权重: 2+1+2=5) ✓
```

## 单源最短路径算法

### 1. Dijkstra算法

适用于**非负权重图**。

#### 算法思想

贪心策略：每次选择距离源点最近的未确定顶点，松弛其邻接边。

```python
import heapq

def dijkstra(graph, start):
    """
    graph: {u: [(v, weight), ...]}
    返回: (distances, predecessors)
    """
    dist = {v: float('inf') for v in graph}
    dist[start] = 0
    prev = {v: None for v in graph}
    
    pq = [(0, start)]  # (距离, 顶点)
    visited = set()
    
    while pq:
        d, u = heapq.heappop(pq)
        
        if u in visited:
            continue
        visited.add(u)
        
        for v, weight in graph[u]:
            if v not in visited:
                new_dist = dist[u] + weight
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    prev[v] = u
                    heapq.heappush(pq, (new_dist, v))
    
    return dist, prev
```

#### 复杂度

- **时间**：$O((V + E) \log V)$（二叉堆）
- **空间**：$O(V)$

### 2. Bellman-Ford算法

适用于**含负权边**的图。

```python
def bellman_ford(graph, start):
    """
    检测负权环并计算最短路径
    """
    dist = {v: float('inf') for v in graph}
    dist[start] = 0
    
    # 松弛 V-1 次
    for _ in range(len(graph) - 1):
        for u in graph:
            for v, weight in graph[u]:
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
    
    # 检测负权环
    for u in graph:
        for v, weight in graph[u]:
            if dist[u] + weight < dist[v]:
                raise ValueError("图中存在负权环")
    
    return dist
```

#### 复杂度

- **时间**：$O(VE)$
- **空间**：$O(V)$

### 3. SPFA算法

Bellman-Ford的队列优化版本。

```python
from collections import deque

def spfa(graph, start):
    dist = {v: float('inf') for v in graph}
    dist[start] = 0
    
    queue = deque([start])
    in_queue = {v: False for v in graph}
    in_queue[start] = True
    
    count = {v: 0 for v in graph}  # 入队次数
    
    while queue:
        u = queue.popleft()
        in_queue[u] = False
        
        for v, weight in graph[u]:
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                if not in_queue[v]:
                    queue.append(v)
                    in_queue[v] = True
                    count[v] += 1
                    if count[v] > len(graph):
                        raise ValueError("存在负权环")
    
    return dist
```

## 全源最短路径

### Floyd-Warshall算法

动态规划求解所有顶点对的最短路径。

```python
def floyd_warshall(graph):
    """
    graph: 邻接矩阵，graph[i][j]表示i到j的权重
    """
    n = len(graph)
    dist = [row[:] for row in graph]
    
    # 动态规划: dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    return dist
```

#### 复杂度

- **时间**：$O(V^3)$
- **空间**：$O(V^2)$

## 算法对比

| 算法 | 适用场景 | 时间复杂度 | 空间复杂度 | 负权边 |
|------|---------|-----------|-----------|--------|
| Dijkstra | 非负权图 | $O((V+E)\log V)$ | $O(V)$ | ✗ |
| Bellman-Ford | 含负权图 | $O(VE)$ | $O(V)$ | ✓ |
| SPFA | 稀疏负权图 | $O(VE)$最坏，$O(E)$平均 | $O(V)$ | ✓ |
| Floyd-Warshall | 全源最短路径 | $O(V^3)$ | $O(V^2)$ | ✓ |

## 应用场景

### 1. 地图导航

GPS使用Dijkstra或A*算法规划路线。

### 2. 网络路由

OSPF、BGP等路由协议使用最短路径算法。

### 3. 物流规划

计算最优运输路线。

## 面试要点

### Q1: Dijkstra为什么不能用负权边？

贪心策略假设已确定的最短路径不会被后续更新。负权边可能导致已确定路径被更短路径替代。

### Q2: 如何重构最短路径？

```python
def reconstruct_path(prev, start, end):
    """根据前驱数组重构路径"""
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()
    return path if path[0] == start else []
```

## 相关概念 (Related Concepts)

### 数据结构
- [图](../data-structures/graph.md)：最短路径算法的基础数据结构
- [堆](../data-structures/heap.md)：Dijkstra 算法的优先队列实现
- [树](../data-structures/tree.md)：最短路径树的构建

### 算法
- [图遍历](./graph-traversal.md)：BFS 是最短路径的特例
- [动态规划](./dynamic-programming.md)：Floyd-Warshall 使用 DP 思想
- [贪心算法](./greedy.md)：Dijkstra 是贪心算法的典型应用

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：最短路径算法的时间效率
- [空间复杂度](../../references/space-complexity.md)：路径存储的空间评估

### 系统实现
- [网络路由](../systems/network.md)：最短路径在路由协议中的应用
- [地图导航](../../references/navigation.md)：实际导航系统的路径规划

- [图遍历](../algorithms/graph-traversal.md) - BFS是特例
- [动态规划](../algorithms/dynamic-programming.md) - Floyd-Warshall使用DP
- [贪心算法](../algorithms/greedy.md) - Dijkstra是贪心算法
- [堆](../data-structures/heap.md) - Dijkstra算法的优先队列实现

## 参考资料

1. 《算法导论》第24章 - 单源最短路径
2. 《算法导论》第25章 - 全源最短路径
3. Shortest path problem - Wikipedia
