# 图表示 (Graph Representations)

## 简介

**图表示（Graph Representations）** 是图论中描述和存储图结构的基础方法。选择合适的图表示方式对算法的效率有着至关重要的影响。在实际应用中，常见的图表示方法包括**邻接矩阵（Adjacency Matrix）**、**邻接表（Adjacency List）**、**边列表（Edge List）**以及**关联矩阵（Incidence Matrix）**等。不同的表示方法在时间复杂度、空间复杂度和操作效率上各有优劣，需要根据具体场景灵活选择。

```
图表示方法选择决策树：

                    ┌─────────────────┐
                    │  图是否稠密？   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                              ▼
           是（稠密图）                   否（稀疏图）
              │                              │
              ▼                              ▼
      ┌───────────────┐              ┌───────────────┐
      │  邻接矩阵     │              │  邻接表       │
      │  O(V²)空间    │              │  O(V+E)空间   │
      │  O(1)查询边   │              │  O(deg)遍历   │
      └───────────────┘              └───────────────┘
```

## 核心概念

### 邻接矩阵 (Adjacency Matrix)

**邻接矩阵**使用一个二维数组来存储图中顶点之间的连接关系。对于具有 $n$ 个顶点的图，邻接矩阵是一个 $n \times n$ 的方阵。

```
无向图示例：

    A ───── B
    │       │
    │       │
    C ───── D

邻接矩阵表示：

      A  B  C  D
   A [0  1  1  0]
   B [1  0  0  1]
   C [1  0  0  1]
   D [0  1  1  0]

特性：
- 无向图的邻接矩阵是对称矩阵
- 对角线元素为0（无自环）
- 矩阵元素为1表示有边，0表示无边
```

**带权图的邻接矩阵：**

```
带权图示例：

    4      2
A ───── B ───── C
│              │
│3             │5
│              │
D ───────────── E
       1

邻接矩阵表示（∞表示无穷大/无边）：

      A    B    C    D    E
   A [0    4    ∞    3    ∞  ]
   B [4    0    2    ∞    ∞  ]
   C [∞    2    0    ∞    5  ]
   D [3    ∞    ∞    0    1  ]
   E [∞    ∞    5    1    0  ]
```

### 邻接表 (Adjacency List)

**邻接表**为每个顶点维护一个链表（或动态数组），存储该顶点的所有邻接顶点。这种表示方法特别适合稀疏图。

```
图结构：

    A ───── B
    │ ╲     │
    │   ╲   │
    │     ╲ │
    C ───── D

邻接表表示：

A: [B, C, D]
B: [A, D]
C: [A, D]
D: [B, C, A]
```

**带权图的邻接表：**

```
图结构：

    4      2
A ───── B ───── C
│              │
│3             │5
│              │
D ───────────── E
       1

邻接表表示：

A: [(B, 4), (D, 3)]
B: [(A, 4), (C, 2)]
C: [(B, 2), (E, 5)]
D: [(A, 3), (E, 1)]
E: [(D, 1), (C, 5)]
```

### 边列表 (Edge List)

**边列表**直接存储图中所有的边，每条边表示为三元组 $(u, v, w)$，其中 $u$ 是起点，$v$ 是终点，$w$ 是权重。

```
图结构：

    4      2
A ───── B ───── C
│              │
│3             │5
│              │
D ───────────── E
       1

边列表表示：

[(A, B, 4), (B, C, 2), (A, D, 3), (C, E, 5), (D, E, 1)]
```

### 关联矩阵 (Incidence Matrix)

**关联矩阵**描述顶点与边的关联关系，是一个 $n \times m$ 的矩阵（$n$ 为顶点数，$m$ 为边数）。

```
图结构：

    e1      e2
A ───── B ───── C
│ e3           │ e5
│              │
D ───────────── E
       e4

关联矩阵表示（无向图）：

      e1  e2  e3  e4  e5
   A [1   0   1   0   0 ]
   B [1   1   0   0   0 ]
   C [0   1   0   0   1 ]
   D [0   0   1   1   0 ]
   E [0   0   0   1   1 ]
```

## 实现方式

### Python：邻接矩阵完整实现

```python
class AdjacencyMatrixGraph:
    """基于邻接矩阵的图实现，支持带权有向图"""
    
    def __init__(self, num_vertices, directed=False, weighted=False):
        self.n = num_vertices
        self.directed = directed
        self.weighted = weighted
        self.INF = float('inf')
        
        # 初始化邻接矩阵
        if weighted:
            # 带权图：初始化为无穷大
            self.matrix = [[self.INF for _ in range(num_vertices)] 
                          for _ in range(num_vertices)]
            # 对角线为0
            for i in range(num_vertices):
                self.matrix[i][i] = 0
        else:
            # 无权图：初始化为0
            self.matrix = [[0 for _ in range(num_vertices)] 
                          for _ in range(num_vertices)]
    
    def add_edge(self, u, v, weight=1):
        """添加边 (u, v)，带权图需指定权重"""
        if self.weighted:
            self.matrix[u][v] = weight
        else:
            self.matrix[u][v] = 1
            
        if not self.directed:
            if self.weighted:
                self.matrix[v][u] = weight
            else:
                self.matrix[v][u] = 1
    
    def remove_edge(self, u, v):
        """删除边 (u, v)"""
        if self.weighted:
            self.matrix[u][v] = self.INF
        else:
            self.matrix[u][v] = 0
            
        if not self.directed:
            if self.weighted:
                self.matrix[v][u] = self.INF
            else:
                self.matrix[v][u] = 0
    
    def has_edge(self, u, v):
        """判断顶点 u 和 v 之间是否存在边"""
        if self.weighted:
            return self.matrix[u][v] != self.INF and self.matrix[u][v] != 0
        return self.matrix[u][v] != 0
    
    def get_weight(self, u, v):
        """获取边 (u, v) 的权重"""
        return self.matrix[u][v]
    
    def get_neighbors(self, v):
        """获取顶点 v 的所有邻接顶点"""
        neighbors = []
        for u in range(self.n):
            if self.has_edge(v, u):
                neighbors.append(u)
        return neighbors
    
    def get_degree(self, v):
        """获取顶点 v 的度数"""
        if self.directed:
            raise ValueError("有向图请使用入度/出度方法")
        return len(self.get_neighbors(v))
    
    def get_in_degree(self, v):
        """获取有向图中顶点 v 的入度"""
        if not self.directed:
            return self.get_degree(v)
        count = 0
        for u in range(self.n):
            if self.has_edge(u, v):
                count += 1
        return count
    
    def get_out_degree(self, v):
        """获取有向图中顶点 v 的出度"""
        if not self.directed:
            return self.get_degree(v)
        return len(self.get_neighbors(v))
    
    def display(self):
        """打印邻接矩阵"""
        print("邻接矩阵：")
        for row in self.matrix:
            print([x if x != self.INF else '∞' for x in row])
```

### Python：邻接表完整实现

```python
from collections import defaultdict, deque

class AdjacencyListGraph:
    """基于邻接表的图实现，支持带权有向图"""
    
    def __init__(self, directed=False, weighted=False):
        self.directed = directed
        self.weighted = weighted
        self.adj = defaultdict(list)
        self.vertices = set()
    
    def add_vertex(self, v):
        """添加顶点"""
        self.vertices.add(v)
    
    def add_edge(self, u, v, weight=None):
        """添加边 (u, v)"""
        self.vertices.add(u)
        self.vertices.add(v)
        
        if self.weighted:
            self.adj[u].append((v, weight if weight is not None else 1))
        else:
            self.adj[u].append(v)
        
        if not self.directed:
            if self.weighted:
                self.adj[v].append((u, weight if weight is not None else 1))
            else:
                self.adj[v].append(u)
    
    def remove_edge(self, u, v):
        """删除边 (u, v)"""
        if self.weighted:
            self.adj[u] = [(n, w) for n, w in self.adj[u] if n != v]
        else:
            self.adj[u] = [n for n in self.adj[u] if n != v]
        
        if not self.directed:
            if self.weighted:
                self.adj[v] = [(n, w) for n, w in self.adj[v] if n != u]
            else:
                self.adj[v] = [n for n in self.adj[v] if n != u]
    
    def has_edge(self, u, v):
        """判断边 (u, v) 是否存在"""
        if self.weighted:
            return any(n == v for n, _ in self.adj[u])
        return v in self.adj[u]
    
    def get_neighbors(self, v):
        """获取顶点 v 的所有邻接顶点"""
        if self.weighted:
            return [n for n, _ in self.adj[v]]
        return self.adj[v]
    
    def get_neighbors_with_weight(self, v):
        """获取顶点 v 的所有邻接顶点及其权重（带权图）"""
        if not self.weighted:
            raise ValueError("非带权图")
        return self.adj[v]
    
    def get_degree(self, v):
        """获取顶点 v 的度数"""
        if self.directed:
            raise ValueError("有向图请使用入度/出度方法")
        return len(self.adj[v])
    
    def get_in_degree(self, v):
        """获取有向图中顶点 v 的入度"""
        if not self.directed:
            return self.get_degree(v)
        count = 0
        for u in self.vertices:
            if self.has_edge(u, v):
                count += 1
        return count
    
    def get_out_degree(self, v):
        """获取有向图中顶点 v 的出度"""
        if not self.directed:
            return self.get_degree(v)
        return len(self.adj[v])
    
    def display(self):
        """打印邻接表"""
        print("邻接表表示：")
        for v in sorted(self.vertices):
            print(f"{v}: {self.adj[v]}")
```

### Python：边列表完整实现

```python
class EdgeListGraph:
    """基于边列表的图实现"""
    
    def __init__(self, directed=False, weighted=False):
        self.directed = directed
        self.weighted = weighted
        self.edges = []  # 边列表
        self.vertices = set()
    
    def add_vertex(self, v):
        """添加顶点"""
        self.vertices.add(v)
    
    def add_edge(self, u, v, weight=None):
        """添加边 (u, v)"""
        self.vertices.add(u)
        self.vertices.add(v)
        
        if self.weighted:
            self.edges.append((u, v, weight if weight is not None else 1))
        else:
            self.edges.append((u, v))
    
    def remove_edge(self, u, v):
        """删除边 (u, v)"""
        if self.weighted:
            self.edges = [e for e in self.edges if not (e[0] == u and e[1] == v)]
        else:
            self.edges = [e for e in self.edges if not (e[0] == u and e[1] == v)]
        
        if not self.directed:
            if self.weighted:
                self.edges = [e for e in self.edges if not (e[0] == v and e[1] == u)]
            else:
                self.edges = [e for e in self.edges if not (e[0] == v and e[1] == u)]
    
    def has_edge(self, u, v):
        """判断边 (u, v) 是否存在"""
        for e in self.edges:
            if e[0] == u and e[1] == v:
                return True
        return False
    
    def get_neighbors(self, v):
        """获取顶点 v 的所有邻接顶点"""
        neighbors = []
        for e in self.edges:
            if e[0] == v:
                neighbors.append(e[1])
            if not self.directed and e[1] == v:
                neighbors.append(e[0])
        return neighbors
    
    def display(self):
        """打印边列表"""
        print("边列表表示：")
        for edge in self.edges:
            print(edge)
```

## 示例

### 不同表示方式的比较示例

```python
# 创建同一个图，使用不同表示方式

# 测试图结构：
#     4      2
# 0 ───── 1 ───── 2
# │              │
# │3             │5
# │              │
# 3 ───────────── 4
#        1

print("=== 邻接矩阵表示 ===")
matrix_graph = AdjacencyMatrixGraph(5, directed=False, weighted=True)
edges = [(0, 1, 4), (1, 2, 2), (0, 3, 3), (2, 4, 5), (3, 4, 1)]
for u, v, w in edges:
    matrix_graph.add_edge(u, v, w)
matrix_graph.display()
# 输出：
# 邻接矩阵：
# [0, 4, '∞', 3, '∞']
# [4, 0, 2, '∞', '∞']
# ['∞', 2, 0, '∞', 5]
# [3, '∞', '∞', 0, 1]
# ['∞', '∞', 5, 1, 0]

print("\n=== 邻接表表示 ===")
list_graph = AdjacencyListGraph(directed=False, weighted=True)
for u, v, w in edges:
    list_graph.add_edge(u, v, w)
list_graph.display()
# 输出：
# 邻接表表示：
# 0: [(1, 4), (3, 3)]
# 1: [(0, 4), (2, 2)]
# 2: [(1, 2), (4, 5)]
# 3: [(0, 3), (4, 1)]
# 4: [(3, 1), (2, 5)]

print("\n=== 边列表表示 ===")
edge_graph = EdgeListGraph(directed=False, weighted=True)
for u, v, w in edges:
    edge_graph.add_edge(u, v, w)
edge_graph.display()
# 输出：
# 边列表表示：
# (0, 1, 4)
# (1, 2, 2)
# (0, 3, 3)
# (2, 4, 5)
# (3, 4, 1)
```

### 表示方式转换

```python
def adjacency_matrix_to_list(matrix):
    """邻接矩阵转换为邻接表"""
    n = len(matrix)
    adj_list = defaultdict(list)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] != 0 and matrix[i][j] != float('inf'):
                adj_list[i].append(j)
    return adj_list

def adjacency_list_to_matrix(adj_list, n, weighted=False):
    """邻接表转换为邻接矩阵"""
    INF = float('inf')
    if weighted:
        matrix = [[INF for _ in range(n)] for _ in range(n)]
        for i in range(n):
            matrix[i][i] = 0
    else:
        matrix = [[0 for _ in range(n)] for _ in range(n)]
    
    for u in adj_list:
        for v in adj_list[u]:
            if weighted and isinstance(v, tuple):
                matrix[u][v[0]] = v[1]
            else:
                matrix[u][v] = 1
    return matrix

def edge_list_to_adjacency_list(edge_list, weighted=False):
    """边列表转换为邻接表"""
    adj_list = defaultdict(list)
    for edge in edge_list:
        if weighted:
            u, v, w = edge
            adj_list[u].append((v, w))
        else:
            u, v = edge
            adj_list[u].append(v)
    return adj_list
```

## 应用场景

### 1. 社交网络分析

社交网络通常具有**稀疏性**特征（每个用户只有少量好友），使用**邻接表**更为高效：

```python
# Facebook社交网络示例：10亿用户，平均每个用户有几百个好友
# 邻接矩阵需要：10^9 × 10^9 = 10^18 个元素（约8 EB存储）
# 邻接表需要：10^9 × 500 = 5 × 10^11 条边（约4 TB存储）

social_graph = AdjacencyListGraph(directed=False, weighted=False)
# 添加好友关系
social_graph.add_edge("user_123", "user_456")
social_graph.add_edge("user_123", "user_789")
```

### 2. 地图导航系统

地图网络需要快速查询两点间距离，使用**邻接表**配合坐标信息：

```python
class NavigationGraph:
    """导航系统图表示"""
    
    def __init__(self):
        self.adj = defaultdict(list)  # 邻接表
        self.coordinates = {}  # 顶点坐标
        self.street_names = {}  # 街道名称
    
    def add_intersection(self, id, lat, lon):
        """添加路口"""
        self.coordinates[id] = (lat, lon)
    
    def add_road(self, u, v, distance, street_name, speed_limit):
        """添加道路"""
        travel_time = distance / speed_limit
        self.adj[u].append((v, travel_time, distance, street_name))
        self.adj[v].append((u, travel_time, distance, street_name))
```

### 3. 网页链接分析

搜索引擎的网页图通常使用**边列表**配合**邻接表**：

```python
# 网页链接图
web_graph = EdgeListGraph(directed=True, weighted=False)

# 添加网页链接
web_graph.add_edge("https://example.com", "https://example.com/page1")
web_graph.add_edge("https://example.com", "https://example.com/page2")
```

### 4. 电路网络分析

电路网络分析使用**关联矩阵**进行基尔霍夫定律计算：

```python
def build_incidence_matrix(circuit):
    """构建电路的关联矩阵"""
    n = len(circuit.nodes)
    m = len(circuit.edges)
    incidence = [[0] * m for _ in range(n)]
    
    for edge_idx, (u, v, component) in enumerate(circuit.edges):
        incidence[u][edge_idx] = 1
        incidence[v][edge_idx] = -1
    
    return incidence
```

## 面试要点

**Q: 邻接矩阵和邻接表的时间/空间复杂度各是多少？**

A:

| 操作 | 邻接矩阵 | 邻接表 |
|------|----------|--------|
| 空间复杂度 | $O(V^2)$ | $O(V + E)$ |
| 添加边 | $O(1)$ | $O(1)$ |
| 删除边 | $O(1)$ | $O(deg(v))$ |
| 查询边 $(u,v)$ | $O(1)$ | $O(deg(u))$ |
| 遍历所有邻接点 | $O(V)$ | $O(deg(v))$ |
| 遍历全图 | $O(V^2)$ | $O(V + E)$ |

**Q: 什么时候应该选择邻接矩阵而不是邻接表？**

A: 选择邻接矩阵的情况：
1. 图是稠密的（$E \approx V^2$）
2. 需要频繁查询任意两点间是否有边
3. 需要进行矩阵运算（如计算路径数量、谱聚类）
4. 顶点数量较少（几百以内）

**Q: 如何在一个有向图中存储多组边权（如时间和距离）？**

A: 使用邻接表，每个邻接项存储多个属性：

```python
# 存储时间和距离两种权重
graph[u].append({
    'to': v,
    'time': 30,      # 分钟
    'distance': 15,  # 公里
    'toll': 5        # 通行费
})
```

**Q: 邻接矩阵中如何判断无向图、有向图、带权图？**

A:
- **无向图**：矩阵对称，即 $A[i][j] = A[j][i]$
- **有向图**：矩阵不一定对称
- **带权图**：矩阵元素为权值（非0/1值）

**Q: 边列表适合什么场景？**

A: 边列表适合：
1. Kruskal算法等需要按边权排序的场景
2. 需要遍历所有边的算法
3. 图的输入/输出（如文件存储）
4. 稀疏图的紧凑存储

## 相关概念

### 数据结构
- [图](../../computer-science/data-structures/graph.md) - 图的抽象数据类型定义
- [树](../../computer-science/data-structures/tree.md) - 特殊的无环连通图
- [哈希表](../../computer-science/data-structures/hash-table.md) - 可用于高效存储邻接关系
- [队列](../../computer-science/data-structures/queue.md) - 图遍历的辅助数据结构
- [栈](../../computer-science/data-structures/stack.md) - 图遍历的辅助数据结构

### 算法
- [图遍历](../../computer-science/algorithms/graph-traversal.md) - DFS、BFS遍历算法
- [最短路径](../../computer-science/algorithms/shortest-path.md) - Dijkstra、Floyd-Warshall算法
- [最小生成树](../../computer-science/algorithms/minimum-spanning-tree.md) - Kruskal、Prim算法
- [拓扑排序](../../computer-science/algorithms/topological-sort.md) - DAG的线性排序

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 图表示操作的时间复杂度
- [空间复杂度](../../references/space-complexity.md) - 不同表示方法的空间开销

### 系统实现
- [内存管理](../../computer-science/systems/memory-management.md) - 图的内存布局优化
- [数据库系统](../../computer-science/databases/database-systems.md) - 图数据库的存储方案

## 参考资料

1. 《算法导论》第22章 - 基本的图算法
2. 《离散数学》第10章 - 图论基础
3. Sedgewick & Wayne《算法》第4版 - 图算法
4. Graph Representation - Wikipedia
