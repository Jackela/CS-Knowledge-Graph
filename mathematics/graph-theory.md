# 图论 (Graph Theory)

## 简介

**图论 (Graph Theory)** 是数学和计算机科学的重要分支，研究点（顶点）和线（边）构成的图的性质。图论在社交网络分析、网络路由、调度优化、编译器设计等领域有广泛应用。

```
┌─────────────────────────────────────────────────────────────┐
│                   图论核心内容                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │ 图的表示 │  │ 图遍历   │  │ 最短路径 │  │ 生成树   │   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │ 匹配问题 │  │ 网络流   │  │ 图着色   │  │ 拓扑排序 │   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 基本概念

### 图的定义

```
图 G = (V, E)

- V：顶点集合 (Vertices)
- E：边集合 (Edges)

示例图：
    A ───── B
    │ ╲     │
    │   ╲   │
    │     ╲ │
    C ───── D

V = {A, B, C, D}
E = {(A,B), (A,C), (A,D), (B,D), (C,D)}
```

### 图的分类

```
┌─────────────────────────────────────────────────────────────┐
│                     图的分类                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  按边是否有方向：                                            │
│  ├─ 无向图 (Undirected)：边无方向 (A,B) = (B,A)             │
│  └─ 有向图 (Directed)：边有方向 <A,B> ≠ <B,A>              │
│                                                             │
│  按边是否有权重：                                            │
│  ├─ 无权图 (Unweighted)：边仅表示连接关系                    │
│  └─ 加权图 (Weighted)：边有权重值                            │
│                                                             │
│  按是否有环：                                                │
│  ├─ 有环图 (Cyclic)：包含回路                                │
│  └─ 无环图 (Acyclic)：不含回路（如树、DAG）                  │
│                                                             │
│  特殊图：                                                    │
│  ├─ 完全图 (Complete)：每对顶点间都有边                       │
│  ├─ 二分图 (Bipartite)：顶点可分成两组，组内无边              │
│  ├─ 树 (Tree)：连通无向无环图                               │
│  └─ DAG (有向无环图)：有向图中无有向环                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 度 (Degree)

```
度：与顶点相连的边的数量

无向图：
- deg(v) = 与v相连的边数
- 握手定理：Σ deg(v) = 2|E|

有向图：
- 入度 (in-degree)：指向v的边数
- 出度 (out-degree)：从v出发的边数
- deg(v) = in-degree(v) + out-degree(v)

示例：
    A ──▶ B
    ▲     │
    │     ▼
    └── C
    
deg⁺(A) = 1, deg⁻(A) = 1
deg⁺(B) = 1, deg⁻(B) = 1
deg⁺(C) = 1, deg⁻(C) = 1
```

## 图的表示

### 邻接矩阵 (Adjacency Matrix)

```
邻接矩阵：n×n矩阵，A[i][j]表示i到j的边

无向图示例：
    A ── B
    │
    C

    A  B  C
A [ 0  1  1 ]
B [ 1  0  0 ]
C [ 1  0  0 ]

特点：
- 无向图矩阵对称
- 空间复杂度：O(V²)
- 查询边是否存在：O(1)
- 适合稠密图
```

### 邻接表 (Adjacency List)

```
邻接表：每个顶点存储相邻顶点列表

图：
    A ──▶ B
    │     │
    ▼     ▼
    C ◀── D

邻接表：
A: [B, C]
B: [D]
C: []
D: [C]

Python实现：
graph = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': [],
    'D': ['C']
}

特点：
- 空间复杂度：O(V + E)
- 适合稀疏图
- 遍历邻居：O(deg(v))
```

```python
class Graph:
    """图的邻接表表示"""
    def __init__(self, directed=False):
        self.graph = {}
        self.directed = directed
    
    def add_vertex(self, v):
        if v not in self.graph:
            self.graph[v] = []
    
    def add_edge(self, u, v, weight=None):
        self.add_vertex(u)
        self.add_vertex(v)
        
        if weight is not None:
            self.graph[u].append((v, weight))
        else:
            self.graph[u].append(v)
        
        if not self.directed:
            if weight is not None:
                self.graph[v].append((u, weight))
            else:
                self.graph[v].append(u)
    
    def get_neighbors(self, v):
        return self.graph.get(v, [])
    
    def display(self):
        for v in self.graph:
            print(f"{v} -> {self.graph[v]}")
```

## 图遍历

### 深度优先搜索 (DFS)

```
DFS：尽可能深地探索分支

算法：
1. 访问起始顶点，标记为已访问
2. 对每个未访问的邻居，递归执行DFS

示例图：
    A ── B ── D
    │         │
    C ─────── E

DFS遍历（从A开始）：
A → B → D → E → C

Python实现：
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    
    visited.add(start)
    print(start, end=' ')
    
    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    
    return visited
```

### 广度优先搜索 (BFS)

```
BFS：先访问所有邻居，再访问邻居的邻居

算法：
1. 将起始顶点入队，标记为已访问
2. 出队一个顶点，访问其所有未访问邻居并入队
3. 重复直到队列为空

BFS遍历（从A开始）：
A → B → C → D → E

Python实现：
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    
    while queue:
        vertex = queue.popleft()
        print(vertex, end=' ')
        
        for neighbor in graph.get(vertex, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return visited
```

## 最短路径算法

### Dijkstra算法

```
Dijkstra算法：单源最短路径（非负权边）

算法步骤：
1. 初始化：起点距离=0，其他=∞
2. 选择距离最小的未确定顶点u
3. 对u的每个邻居v，松弛操作：
   if dist[u] + w(u,v) < dist[v]:
      dist[v] = dist[u] + w(u,v)
4. 重复2-3直到所有顶点确定

时间复杂度：O((V+E)logV) 使用优先队列

示例：
    4      1
A ───── B ───── C
│       │       │
│ 2     │ 3     │ 5
│       │       │
D ───── E ───── F
    1      2

从A到各点最短距离：
A:0, B:4, C:5, D:2, E:3, F:5
```

```python
import heapq

def dijkstra(graph, start):
    """Dijkstra算法"""
    dist = {v: float('infinity') for v in graph}
    dist[start] = 0
    pq = [(0, start)]
    
    while pq:
        d, u = heapq.heappop(pq)
        
        if d > dist[u]:
            continue
        
        for v, weight in graph[u]:
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(pq, (dist[v], v))
    
    return dist
```

### Floyd-Warshall算法

```
Floyd-Warshall：所有顶点对最短路径

动态规划思想：
dist[i][j][k] = min(dist[i][j][k-1], 
                    dist[i][k][k-1] + dist[k][j][k-1])

即：从i到j的最短路径，要么不经过k，要么经过k

时间复杂度：O(V³)
空间复杂度：O(V²)

Python实现：
def floyd_warshall(graph):
    n = len(graph)
    dist = [[float('inf')] * n for _ in range(n)]
    
    # 初始化
    for i in range(n):
        for j in range(n):
            if i == j:
                dist[i][j] = 0
            elif graph[i][j] != 0:
                dist[i][j] = graph[i][j]
    
    # 动态规划
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    return dist
```

## 最小生成树

### Kruskal算法

```
Kruskal算法：按边权从小到大选边，不形成环

算法步骤：
1. 将所有边按权重排序
2. 依次选择最小边，如果不形成环则加入
3. 使用并查集检查是否形成环
4. 直到选了V-1条边

时间复杂度：O(E log E)

示例：
A ──4── B ──2── C
│       │       │
1       3       5
│       │       │
D ──6── E ──4── F

MST包含边：(A,D,1), (B,C,2), (B,E,3), (A,B,4), (E,F,4)
总权重：14
```

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px != py:
            self.parent[px] = py
            return True
        return False

def kruskal(edges, n):
    """edges: [(u, v, weight), ...]"""
    edges.sort(key=lambda x: x[2])
    uf = UnionFind(n)
    mst = []
    
    for u, v, w in edges:
        if uf.union(u, v):
            mst.append((u, v, w))
            if len(mst) == n - 1:
                break
    
    return mst
```

### Prim算法

```
Prim算法：从起点开始，逐步扩展树

算法步骤：
1. 选择起始顶点加入MST
2. 选择连接MST和外部顶点的最小边
3. 将该边和顶点加入MST
4. 重复直到包含所有顶点

时间复杂度：O((V+E)logV)
```

## 拓扑排序

```
拓扑排序：对有向无环图(DAG)的顶点线性排序
          使得对每条边(u,v)，u在v之前

算法（Kahn）：
1. 计算所有顶点的入度
2. 将入度为0的顶点入队
3. 依次出队，将其邻居入度减1
4. 若邻居入度变为0，入队
5. 重复直到队列为空

应用：任务调度、编译顺序、课程选修计划

示例：
A ──▶ B ──▶ D
│     │
▼     ▼
C ──▶ E

拓扑排序结果：A, B, C, D, E 或 A, C, B, E, D
```

```python
def topological_sort(graph):
    """Kahn算法"""
    from collections import deque
    
    # 计算入度
    in_degree = {v: 0 for v in graph}
    for v in graph:
        for neighbor in graph[v]:
            in_degree[neighbor] += 1
    
    # 入度为0的入队
    queue = deque([v for v in graph if in_degree[v] == 0])
    result = []
    
    while queue:
        v = queue.popleft()
        result.append(v)
        
        for neighbor in graph[v]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(result) != len(graph):
        raise ValueError("图中有环，无法拓扑排序")
    
    return result
```

## 强连通分量 (SCC)

```
强连通分量：有向图中互相可达的极大顶点集

Kosaraju算法：
1. 对原图做DFS，记录完成顺序
2. 转置图（所有边反向）
3. 按完成顺序的逆序对转置图做DFS
4. 每次DFS访问的顶点构成一个SCC

Tarjan算法：
使用DFS和栈，一次遍历找出所有SCC

应用：社交网络分析、网页聚类
```

## 二分图匹配

```
二分图：顶点可分成两组L和R，边只在L-R之间

最大匹配：找到最多的无公共顶点的边

匈牙利算法：
- 对L中每个顶点，找增广路径
- 增广路径：交替的未匹配边和匹配边
- 翻转增广路径上的匹配状态

应用：任务分配、婚姻匹配、资源分配
```

## 网络流

### 最大流问题

```
最大流：从源点到汇点的最大流量

Ford-Fulkerson方法：
1. 在残差网络中找到增广路径
2. 沿增广路径推送流量
3. 更新残差网络
4. 直到不存在增广路径

Edmonds-Karp：使用BFS找增广路径，O(VE²)
Dinic算法：分层图+阻塞流，O(V²E)

最小割最大流定理：
最大流 = 最小割容量
```

## 面试要点

### 常见问题

**Q1: DFS和BFS的区别和应用？**
> DFS使用栈（递归），适合路径搜索、拓扑排序、连通分量；BFS使用队列，适合最短路径（无权图）、层次遍历、最小步数问题。

**Q2: Dijkstra和Bellman-Ford的区别？**> Dijkstra要求边权非负，使用贪心策略，时间O((V+E)logV)；Bellman-Ford可处理负权边，可检测负环，时间O(VE)。

**Q3: Kruskal和Prim的选择？**> Kruskal适合稀疏图（边少），使用并查集；Prim适合稠密图（边多），类似Dijkstra。Kruskal需要排序所有边，Prim只需维护局部最小边。

**Q4: 如何判断图中有环？**> 无向图：DFS遇到已访问且非父节点的邻居则有环；有向图：DFS遇到当前递归栈中的节点则有环，或拓扑排序后顶点数少于原图。

**Q5: 二分图的判定？**> 使用双色染色法（BFS/DFS），若能用两种颜色染色且相邻顶点颜色不同，则是二分图。等价于图中无奇数长度环。

## 相关概念

- [数据结构-图](../computer-science/data-structures/graph.md) - 图的实现
- [算法-图遍历](../computer-science/algorithms/graph-traversal.md) - 遍历算法详解
- [组合数学](./combinatorics.md) - 图的组合问题
- [树](../computer-science/data-structures/tree.md) - 特殊图结构

## 参考资料

1. "Introduction to Graph Theory" by Douglas West
2. "Graph Theory" by Reinhard Diestel
3. "Algorithm Design" by Kleinberg & Tardos
4. CLRS算法导论（图算法章节）
5. Wikipedia: [Graph Theory](https://en.wikipedia.org/wiki/Graph_theory)
