# 图 (Graph)

图（Graph）是离散数学中研究非线性结构的基础数据结构，由顶点（Vertex）的集合与边（Edge）的集合组成。与[树](./tree.md)相比，图没有层次约束，允许任意顶点之间存在多对多的关系。图论（Graph Theory）由欧拉（Leonhard Euler）在1736年解决柯尼斯堡七桥问题时开创，如今已成为网络科学、运筹学与计算理论的核心工具。

数学上，一个图 $G$ 定义为二元组 $G = (V, E)$，其中：
- $V$ 为顶点集（Vertex Set），$|V| = n$ 表示顶点数量
- $E$ 为边集（Edge Set），$E \subseteq V \times V$，$|E| = m$ 表示边的数量

#SW|
## 原理

### 有向图与无向图

**有向图（Directed Graph / Digraph）**

边具有方向性，记作有序对 $(u, v) \in E$，表示从顶点 $u$ 指向顶点 $v$ 的弧（Arc）。有向图中：
- 入度（In-degree）：$deg^-(v) = |\{u \in V : (u, v) \in E\}|$
- 出度（Out-degree）：$deg^+(v) = |\{u \in V : (v, u) \in E\}|$
- 握手定理：$\sum_{v \in V} deg^-(v) = \sum_{v \in V} deg^+(v) = |E|$

**无向图（Undirected Graph）**

边无方向，记作无序对 $\{u, v\} \in E$。无向图中：
- 度（Degree）：$deg(v) = |\{u \in V : \{u, v\} \in E\}|$
- 握手定理：$\sum_{v \in V} deg(v) = 2|E|$

### 带权图与无权图

**带权图（Weighted Graph）**

每条边关联一个权重函数 $w: E \rightarrow \mathbb{R}$，表示距离、成本或容量。带权图记作 $G = (V, E, w)$。实际应用包括：
- 交通网络中的距离或时间
- 通信网络中的带宽或延迟
- 社交网络中的亲密度或交互频率

**无权图（Unweighted Graph）**

所有边权重视为单位1，仅关注连通性与拓扑结构。

### 图的表示方法

#### 邻接矩阵（Adjacency Matrix）

对于图 $G = (V, E)$，邻接矩阵 $A$ 是一个 $n \times n$ 的矩阵，定义为：

$$
A_{ij} = \begin{cases}
w(i, j) & \text{if } (i, j) \in E \text{ (带权图)} \\
1 & \text{if } (i, j) \in E \text{ (无权图)} \\
0 & \text{otherwise}
\end{cases}
$$

**特性：**
- 无向图的邻接矩阵是对称矩阵：$A = A^T$
- 矩阵的 $k$ 次幂 $(A^k)_{ij}$ 表示从顶点 $i$ 到 $j$ 的长度为 $k$ 的路径数量
- 拉普拉斯矩阵：$L = D - A$，其中 $D$ 为度矩阵

**适用场景：**
- 稠密图（$|E| \approx |V|^2$）
- 需要快速查询任意两顶点间是否有边：$O(1)$
- 需要频繁进行矩阵运算（如谱聚类、随机游走）

#### 邻接表（Adjacency List）

为每个顶点 $v \in V$ 维护一个链表（或动态数组），存储其所有邻接顶点 $Adj(v) = \{u \in V : (v, u) \in E\}$。

**特性：**
- 空间效率优于邻接矩阵（稀疏图）
- 遍历顶点 $v$ 的所有邻居：$O(deg(v))$
- 查询任意两顶点间是否有边：$O(\min(deg(u), deg(v)))$

**适用场景：**
- 稀疏图（$|E| \ll |V|^2$）
- 需要遍历邻接顶点的算法（DFS、BFS）
- 顶点数量大但平均度数小的网络

### 图论术语

**路径（Path）**

顶点序列 $P = (v_0, v_1, \ldots, v_k)$，其中 $(v_i, v_{i+1}) \in E$ 对所有 $0 \leq i < k$ 成立。路径长度定义为边数 $|P| = k$（无权图）或权重之和 $\sum_{i=0}^{k-1} w(v_i, v_{i+1})$（带权图）。

**简单路径（Simple Path）**

路径中所有顶点互不相同，即 $v_i \neq v_j$ 对 $i \neq j$。

**环（Cycle）**

起点与终点相同的路径，即 $v_0 = v_k$ 且 $k \geq 1$。简单环要求除起点/终点外所有顶点互不相同。

**连通性（Connectivity）**

- **无向图**：若任意两顶点间存在路径，则称图是连通的
- **有向图**：
  - 强连通：任意两顶点间存在双向路径
  - 弱连通：忽略方向后的无向图是连通的

**连通分量（Connected Components）**

极大连通子图。无向图的连通分量划分是唯一的，可通过[图遍历](../algorithms/graph-traversal.md)（DFS/BFS）在 $O(|V| + |E|)$ 时间内找出。

### 特殊图类型

**有向无环图（DAG, Directed Acyclic Graph）**

无有向环的有向图。DAG的核心性质：存在拓扑排序（Topological Sort）。应用包括：
- 任务调度与依赖管理
- 编译系统中的编译依赖
- 表达式求值的语法树

**完全图（Complete Graph）**

无向完全图 $K_n$ 有 $\binom{n}{2} = \frac{n(n-1)}{2}$ 条边；有向完全图有 $n(n-1)$ 条弧。

**二分图（Bipartite Graph）**

顶点集可划分为两个不相交子集 $V = L \cup R$，满足 $L \cap R = \emptyset$，且所有边连接 $L$ 与 $R$ 中的顶点（无内部边）。等价判定：图中无奇数长度的环。

**多重图与简单图**

- 简单图：无自环（self-loop），无多重边
- 多重图：允许同一对顶点间存在多条边

**稠密图与稀疏图**

- 稠密图：$|E| = \Theta(|V|^2)$
- 稀疏图：$|E| = O(|V|)$ 或 $|E| \ll |V|^2$

#KM|
## 复杂度分析

| 操作 | 邻接矩阵 | 邻接表 |
|------|----------|--------|
| 空间复杂度 | $O(|V|^2)$ | $O(|V| + |E|)$ |
| 添加顶点 | $O(|V|)$（可能需要扩容） | $O(1)$ |
| 删除顶点 | $O(|V|^2)$ | $O(|V| + |E|)$ |
| 添加边 | $O(1)$ | $O(1)$ |
| 删除边 | $O(1)$ | $O(deg(v))$ |
| 查询边 $(u,v)$ | $O(1)$ | $O(\min(deg(u), deg(v)))$ |
| 遍历邻接顶点 | $O(|V|)$ | $O(deg(v))$ |
| 遍历全图 | $O(|V|^2)$ | $O(|V| + |E|)$ |

**选择建议：**
- 稠密图（边数接近 $|V|^2$）或需要快速边查询：使用邻接矩阵
- 稀疏图（边数远小于 $|V|^2$）或需要遍历邻居：使用邻接表
- 现代大型网络（社交网络、Web图）通常极度稀疏，优先选择邻接表

#MY|
## 实现示例

### Python：邻接矩阵实现

```python
class GraphAdjMatrix:
    """基于邻接矩阵的图实现（支持带权图）"""
    
    def __init__(self, num_vertices: int, directed: bool = False, weighted: bool = False):
        self.n = num_vertices
        self.directed = directed
        self.weighted = weighted
        # 使用无穷大表示无边，0表示无权图的单位权重
        self.INF = float('inf')
        self.matrix = [[0 if not weighted else self.INF 
                       for _ in range(num_vertices)] 
                      for _ in range(num_vertices)]
        # 对角线初始化为0（顶点到自身的距离为0）
        for i in range(num_vertices):
            self.matrix[i][i] = 0
    
    def add_edge(self, u: int, v: int, weight: int = 1):
        """添加边 (u, v)，若为带权图则指定权重"""
        self.matrix[u][v] = weight
        if not self.directed:
            self.matrix[v][u] = weight
    
    def remove_edge(self, u: int, v: int):
        """删除边 (u, v)"""
        self.matrix[u][v] = 0 if not self.weighted else self.INF
        if not self.directed:
            self.matrix[v][u] = 0 if not self.weighted else self.INF
    
    def has_edge(self, u: int, v: int) -> bool:
        """查询两顶点间是否有边"""
        return self.matrix[u][v] != (0 if not self.weighted else self.INF)
    
    def get_weight(self, u: int, v: int) -> float:
        """获取边权重"""
        return self.matrix[u][v]
    
    def get_neighbors(self, v: int) -> list:
        """获取顶点 v 的所有邻接顶点"""
        neighbors = []
        for u in range(self.n):
            if self.has_edge(v, u) and u != v:
                neighbors.append(u)
        return neighbors
    
    def __str__(self):
        return '\n'.join(str(row) for row in self.matrix)
```

### Python：邻接表实现

```python
from collections import defaultdict, deque

class GraphAdjList:
    """基于邻接表的图实现（支持带权有向图）"""
    
    def __init__(self, directed: bool = False, weighted: bool = False):
        self.directed = directed
        self.weighted = weighted
        # 邻接表：顶点 -> [(邻居, 权重), ...]
        self.adj = defaultdict(list)
        self.vertices = set()
    
    def add_vertex(self, v):
        """添加顶点"""
        self.vertices.add(v)
    
    def add_edge(self, u, v, weight: int = 1):
        """添加边 (u, v)"""
        self.vertices.add(u)
        self.vertices.add(v)
        self.adj[u].append((v, weight) if self.weighted else v)
        if not self.directed:
            self.adj[v].append((u, weight) if self.weighted else u)
    
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
    
    def has_edge(self, u, v) -> bool:
        """查询边是否存在"""
        if self.weighted:
            return any(n == v for n, _ in self.adj[u])
        return v in self.adj[u]
    
    def get_neighbors(self, v):
        """获取邻接顶点"""
        if self.weighted:
            return [n for n, _ in self.adj[v]]
        return self.adj[v]
    
    def get_degree(self, v) -> int:
        """获取顶点度数"""
        return len(self.adj[v])
    
    def bfs(self, start):
        """广度优先搜索"""
        visited = set([start])
        queue = deque([start])
        result = []
        
        while queue:
            v = queue.popleft()
            result.append(v)
            for neighbor in self.get_neighbors(v):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return result
    
    def dfs(self, start):
        """深度优先搜索"""
        visited = set()
        result = []
        
        def _dfs(v):
            visited.add(v)
            result.append(v)
            for neighbor in self.get_neighbors(v):
                if neighbor not in visited:
                    _dfs(neighbor)
        
        _dfs(start)
        return result
    
    def find_connected_components(self):
        """查找连通分量（仅适用于无向图）"""
        visited = set()
        components = []
        
        for v in self.vertices:
            if v not in visited:
                component = []
                stack = [v]
                while stack:
                    node = stack.pop()
                    if node not in visited:
                        visited.add(node)
                        component.append(node)
                        for neighbor in self.get_neighbors(node):
                            if neighbor not in visited:
                                stack.append(neighbor)
                components.append(component)
        return components
```

#HK|
## 应用场景

### 社交网络分析

社交网络天然是图结构：用户为顶点，关注/好友关系为边。图算法用于：
- **影响力传播**：识别关键意见领袖（KOL），使用PageRank或度中心性
- **社区发现**：通过模块度（Modularity）最大化或谱聚类识别社群
- **好友推荐**：基于共同邻居数的链路预测算法
- **信息扩散**：独立级联（Independent Cascade）模型模拟病毒式传播

### 地图与导航系统

道路网络建模为带权图：交叉口为顶点，道路段为边，权重可以是距离或通行时间。核心算法：
- [最短路径](../algorithms/shortest-path.md)：Dijkstra、A*、Contraction Hierarchies
- 多模式路径规划：结合公交、地铁、步行的时间依赖图
- 实时交通：动态更新边权重，支持快速重算路径

### 编译器与依赖管理

- **构建系统**：Makefile、CMake中的目标依赖构成DAG，拓扑排序确定编译顺序
- **包管理器**：npm、pip解析依赖版本冲突，检测循环依赖
- **数据流分析**：控制流图（CFG）、数据依赖图用于代码优化

### 知识图谱与推荐系统

- **实体关系建模**：知识图谱将实体表示为顶点，关系表示为带标签的边
- **图神经网络（GNN）**：通过消息传递机制学习顶点嵌入
- **推荐算法**：基于图卷积网络（GCN）的协同过滤

### 计算机网络

- **路由协议**：OSPF使用链路状态算法，BGP基于路径向量
- **网络拓扑**：数据中心网络拓扑设计（Fat-Tree、Jellyfish）
- **流量工程**：多商品流问题优化网络利用率

### 生物信息学

- **蛋白质相互作用网络**：PPI网络分析关键蛋白质
- **基因调控网络**：推断基因间的调控关系
- **系统发育树**：基于图的最小生成树重建进化关系

#BT|
## 面试要点

### 1. 如何检测有向图中的环？

**答案：** 使用三色标记的DFS或Kahn算法（拓扑排序）。

三色标记法：白色（未访问）、灰色（访问中）、黑色（已完成）。若在DFS过程中遇到灰色顶点，说明存在回边，即存在环。时间复杂度 $O(|V| + |E|)$。

```python
def has_cycle(graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {v: WHITE for v in graph.vertices}
    
    def dfs(v):
        color[v] = GRAY
        for neighbor in graph.get_neighbors(v):
            if color[neighbor] == GRAY:  # 遇到回边
                return True
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[v] = BLACK
        return False
    
    for v in graph.vertices:
        if color[v] == WHITE and dfs(v):
            return True
    return False
```

### 2. 什么时候选择邻接矩阵而不是邻接表？

**答案：** 以下情况优先选择邻接矩阵：
- 图是稠密的（边数接近 $|V|^2$），邻接矩阵的空间效率反而更高
- 需要频繁查询任意两顶点间是否有边，要求 $O(1)$ 时间复杂度
- 需要进行矩阵运算（如通过矩阵幂计算路径数量、谱聚类）
- 图的规模较小（顶点数在几百以内）

否则，对于稀疏图（大多数实际网络），邻接表的空间和时间效率都更优。

### 3. 解释强连通分量（SCC）及如何求解

**答案：** 强连通分量是有向图中的极大强连通子图。求解算法：

**Kosaraju算法**（两遍DFS）：
1. 第一遍DFS计算顶点的完成时间顺序
2. 转置图（反转所有边的方向）
3. 按完成时间逆序在转置图上进行第二遍DFS，每次DFS访问到的顶点构成一个SCC

时间复杂度 $O(|V| + |E|)$，空间复杂度 $O(|V|)$。

**Tarjan算法**（单遍DFS）：
使用DFS序和Low-Link值，在DFS过程中实时识别SCC，效率更高。

### 4. 二分图的判定方法是什么？

**答案：** 二分图当且仅当图中不存在奇数长度的环。判定算法：

使用双色标记的BFS/DFS：
1. 任选起始顶点，染为颜色A
2. 将所有邻居染为颜色B
3. 继续BFS，若发现某顶点已被染为相同颜色，则不是二分图

等价地，图是二分图当且仅当它是2-可染色的。时间复杂度 $O(|V| + |E|)$。

### 5. 在有向无环图（DAG）中如何找到所有拓扑排序？

**答案：** 使用回溯法结合Kahn算法的思想：

```python
def all_topological_sorts(graph):
    result = []
    in_degree = {v: 0 for v in graph.vertices}
    for v in graph.vertices:
        for neighbor in graph.get_neighbors(v):
            in_degree[neighbor] += 1
    
    def backtrack(path, in_degree):
        if len(path) == len(graph.vertices):
            result.append(path[:])
            return
        
        # 选择所有入度为0的顶点
        for v in list(graph.vertices):
            if in_degree[v] == 0 and v not in path:
                # 选择v
                for neighbor in graph.get_neighbors(v):
                    in_degree[neighbor] -= 1
                path.append(v)
                
                backtrack(path, in_degree)
                
                # 回溯
                path.pop()
                for neighbor in graph.get_neighbors(v):
                    in_degree[neighbor] += 1
    
    backtrack([], in_degree)
    return result
```

时间复杂度取决于拓扑排序的数量，最坏情况 $O(|V|! \cdot |E|)$。

#TY|
## 相关概念 (Related Concepts)

### 数据结构
- [树](./tree.md)：无环连通图，是图的特例
- [二叉树](./binary-tree.md)：树的重要子类
- [堆](./heap.md)：优先队列，在图算法中常用

### 算法
- [图遍历](../algorithms/graph-traversal.md)：DFS 与 BFS，是图算法的基础
- [最短路径](../algorithms/shortest-path.md)：Dijkstra、Bellman-Ford、Floyd-Warshall 算法
- [最小生成树](../algorithms/minimum-spanning-tree.md)：Kruskal 与 Prim 算法
- [拓扑排序](../algorithms/topological-sort.md)：DAG 的线性排序

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：图算法的时间效率分析
- [空间复杂度](./space-complexity.md)：图存储的空间评估

### 系统实现
- [网络协议](../systems/network.md)：图在计算机网络中的应用
- [数据库](../systems/database.md)：图数据库与关系型数据库对比
- [进程调度](../systems/scheduling.md)：任务依赖图与调度
## 参考资料

1. **Corman, T. H., et al.** *Introduction to Algorithms* (4th ed.). MIT Press, 2022. 第22-26章图算法基础
2. **Sedgewick, R., & Wayne, K.** *Algorithms* (4th ed.). Addison-Wesley, 2011. 第4章图论
3. **Bondy, J. A., & Murty, U. S. R.** *Graph Theory*. Springer, 2008. 图论经典教材
4. **Kleinberg, J., & Tardos, É.** *Algorithm Design*. Pearson, 2005. 图算法设计与分析
5. **Newman, M.** *Networks: An Introduction*. Oxford University Press, 2010. 复杂网络科学
6. **Hamilton, W. L.** *Graph Representation Learning*. Morgan & Claypool, 2020. 图表示学习综述
- [抽象数据类型](../../references/adt.md) - 图的 ADT 定义
