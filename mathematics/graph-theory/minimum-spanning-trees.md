# 最小生成树 (Minimum Spanning Trees)

## 简介

最小生成树（Minimum Spanning Tree, MST）是图论中的经典问题，旨在找到连接图中所有顶点的权重和最小的无环子图。MST在网络设计、聚类分析、近似算法等领域有广泛应用。

对于连通无向图，最小生成树具有以下性质：
- 包含图中所有顶点
- 恰好有V-1条边（V为顶点数）
- 无环
- 所有边的权重和最小

## 核心概念

### Kruskal算法

```python
class UnionFind:
    """并查集数据结构"""
    
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        """查找根节点（带路径压缩）"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        """合并两个集合（按秩合并）"""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        
        return True

class Kruskal:
    """
    Kruskal最小生成树算法
    贪心策略：按权重排序，选择不形成环的边
    时间复杂度: O(E log E) - 主要是排序
    空间复杂度: O(V)
    """
    
    def __init__(self, vertices):
        self.vertices = vertices
        self.edges = []  # [(weight, u, v), ...]
    
    def add_edge(self, u, v, weight):
        """添加边"""
        self.edges.append((weight, u, v))
    
    def find_mst(self):
        """
        查找最小生成树
        返回: (mst_edges, total_weight)
        """
        # 按权重排序
        self.edges.sort()
        
        # 初始化并查集
        vertex_index = {v: i for i, v in enumerate(self.vertices)}
        uf = UnionFind(len(self.vertices))
        
        mst_edges = []
        total_weight = 0
        
        for weight, u, v in self.edges:
            ui, vi = vertex_index[u], vertex_index[v]
            
            # 如果u和v不在同一集合，添加这条边
            if uf.union(ui, vi):
                mst_edges.append((u, v, weight))
                total_weight += weight
                
                # 已选择V-1条边，完成
                if len(mst_edges) == len(self.vertices) - 1:
                    break
        
        if len(mst_edges) != len(self.vertices) - 1:
            raise ValueError("Graph is not connected")
        
        return mst_edges, total_weight

# 示例
kruskal = Kruskal(['A', 'B', 'C', 'D', 'E'])
kruskal.add_edge('A', 'B', 4)
kruskal.add_edge('A', 'C', 2)
kruskal.add_edge('B', 'C', 1)
kruskal.add_edge('B', 'D', 5)
kruskal.add_edge('C', 'D', 8)
kruskal.add_edge('C', 'E', 10)
kruskal.add_edge('D', 'E', 2)

mst_edges, total = kruskal.find_mst()
print("MST edges:", mst_edges)
print("Total weight:", total)
```

### Prim算法

```python
import heapq

class Prim:
    """
    Prim最小生成树算法
    贪心策略：从起点开始，逐步扩展树
    时间复杂度: O((V + E) log V) 使用优先队列
    适合：稠密图
    """
    
    def __init__(self, graph):
        """
        graph: dict, graph[u] = [(v, weight), ...]
        """
        self.graph = graph
    
    def find_mst(self, start):
        """
        从start顶点开始构建MST
        返回: (mst_edges, total_weight)
        """
        visited = {start}
        mst_edges = []
        total_weight = 0
        
        # 优先队列: (weight, u, v)
        # u已在树中，v是候选顶点
        pq = []
        for v, weight in self.graph[start]:
            heapq.heappush(pq, (weight, start, v))
        
        while pq and len(visited) < len(self.graph):
            weight, u, v = heapq.heappop(pq)
            
            if v in visited:
                continue
            
            # 添加边到MST
            visited.add(v)
            mst_edges.append((u, v, weight))
            total_weight += weight
            
            # 添加v的邻接边
            for next_v, next_weight in self.graph[v]:
                if next_v not in visited:
                    heapq.heappush(pq, (next_weight, v, next_v))
        
        if len(visited) != len(self.graph):
            raise ValueError("Graph is not connected")
        
        return mst_edges, total_weight

# 示例
graph = {
    'A': [('B', 4), ('C', 2)],
    'B': [('A', 4), ('C', 1), ('D', 5)],
    'C': [('A', 2), ('B', 1), ('D', 8), ('E', 10)],
    'D': [('B', 5), ('C', 8), ('E', 2)],
    'E': [('C', 10), ('D', 2)]
}

prim = Prim(graph)
mst_edges, total = prim.find_mst('A')
print("MST edges:", mst_edges)
print("Total weight:", total)
```

## 实现方式

### 次小生成树

```python
class SecondMST:
    """次小生成树算法"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def find_second_mst(self):
        """
        找到权重第二小的生成树
        方法：
        1. 先找到MST
        2. 尝试用非树边替换树边
        3. 选择增量最小的替换方案
        """
        # 找到MST
        prim = Prim(self.graph)
        mst_edges, mst_weight = prim.find_mst(next(iter(self.graph)))
        
        # 构建MST的边集合
        mst_set = set()
        for u, v, w in mst_edges:
            mst_set.add((min(u, v), max(u, v)))
        
        second_mst_weight = float('inf')
        
        # 遍历所有非树边
        for u in self.graph:
            for v, weight in self.graph[u]:
                edge_key = (min(u, v), max(u, v))
                if edge_key in mst_set:
                    continue
                
                # 添加这条边会形成环
                # 找到环上的最大边权（不包括新边）
                max_edge_in_cycle = self._find_max_edge_in_cycle(
                    mst_edges, u, v
                )
                
                # 计算新的生成树权重
                new_weight = mst_weight - max_edge_in_cycle + weight
                if new_weight > mst_weight and new_weight < second_mst_weight:
                    second_mst_weight = new_weight
        
        return second_mst_weight
    
    def _find_max_edge_in_cycle(self, mst_edges, u, v):
        """在MST中找到u到v路径上的最大边权"""
        # 构建MST的邻接表
        mst_graph = {}
        for a, b, w in mst_edges:
            if a not in mst_graph:
                mst_graph[a] = []
            if b not in mst_graph:
                mst_graph[b] = []
            mst_graph[a].append((b, w))
            mst_graph[b].append((a, w))
        
        # BFS找路径并记录最大边权
        from collections import deque
        visited = {u}
        queue = deque([(u, 0)])
        parent = {u: None}
        
        while queue:
            node, _ = queue.popleft()
            if node == v:
                break
            
            for next_node, weight in mst_graph.get(node, []):
                if next_node not in visited:
                    visited.add(next_node)
                    parent[next_node] = (node, weight)
                    queue.append((next_node, weight))
        
        # 回溯找到最大边权
        max_weight = 0
        current = v
        while current != u:
            prev_node, weight = parent[current]
            max_weight = max(max_weight, weight)
            current = prev_node
        
        return max_weight
```

### 最小生成森林

```python
class MinimumSpanningForest:
    """最小生成森林（针对不连通图）"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def find_msf(self):
        """
        找到最小生成森林
        每个连通分量一棵MST
        """
        vertices = set(self.graph.keys())
        msf_edges = []
        total_weight = 0
        
        while vertices:
            # 选择一个未访问的顶点
            start = vertices.pop()
            component = {start}
            
            # Prim算法构建该连通分量的MST
            pq = []
            for v, weight in self.graph[start]:
                heapq.heappush(pq, (weight, start, v))
            
            while pq:
                weight, u, v = heapq.heappop(pq)
                
                if v in component:
                    continue
                
                component.add(v)
                vertices.discard(v)
                msf_edges.append((u, v, weight))
                total_weight += weight
                
                for next_v, next_weight in self.graph[v]:
                    if next_v not in component:
                        heapq.heappush(pq, (next_weight, v, next_v))
        
        return msf_edges, total_weight
```

## 示例

### 网络设计应用

```python
class NetworkDesign:
    """网络设计中的MST应用"""
    
    def __init__(self, locations):
        """
        locations: dict, {name: (x, y), ...}
        """
        self.locations = locations
    
    def euclidean_distance(self, p1, p2):
        """计算欧几里得距离"""
        import math
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def build_network(self):
        """
        设计连接所有站点的最小成本网络
        """
        # 构建完全图
        graph = {name: [] for name in self.locations}
        
        names = list(self.locations.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                u, v = names[i], names[j]
                dist = self.euclidean_distance(
                    self.locations[u], self.locations[v]
                )
                graph[u].append((v, dist))
                graph[v].append((u, dist))
        
        # 使用Prim算法找到MST
        prim = Prim(graph)
        mst_edges, total_cost = prim.find_mst(names[0])
        
        return mst_edges, total_cost

# 示例：连接5个城市
locations = {
    '北京': (0, 0),
    '上海': (10, 5),
    '广州': (12, -8),
    '深圳': (13, -9),
    '杭州': (9, 3)
}

network = NetworkDesign(locations)
edges, cost = network.build_network()
print(f"Network edges: {edges}")
print(f"Total cost: {cost:.2f}")
```

## 应用场景

### 最小生成树的应用

1. **网络设计**：通信网络、电力网络、水管网络的最小成本设计
2. **聚类分析**：基于MST的层次聚类
3. **图像分割**：计算机视觉中的分割算法
4. **近似算法**：TSP等NP难问题的近似解
5. **电路设计**：VLSI芯片的布线优化

## 面试要点

**Q: Kruskal和Prim算法如何选择？**
A: 
- Kruskal：适合稀疏图（E ≈ V），边排序O(E log E)
- Prim：适合稠密图（E ≈ V²），使用优先队列O((V+E) log V)

**Q: 如何证明MST算法的正确性？**
A: 使用割性质（Cut Property）：对于图的任意割，跨越割的最小权重边必在MST中。两种算法都是贪心选择满足割性质的边。

**Q: 如果边权可以相同，MST唯一吗？**
A: 不一定唯一。当存在相同权重的边时，可能有多个MST。

## 相关概念

### 数据结构
- [并查集](../../computer-science/data-structures/union-find.md) - Kruskal使用
- [优先队列](../../computer-science/data-structures/priority-queue.md) - Prim使用
- [图](../../computer-science/data-structures/graph.md) - 图的表示

### 算法
- [贪心算法](../../computer-science/algorithms/greedy.md) - MST基础
- [图遍历](./graph-traversal.md) - 连通性检查

### 复杂度分析
- [时间复杂度](../../computer-science/algorithms/time-complexity.md)

### 系统实现
- [网络设计](../../software-engineering/system-design/network-design.md) - 实际应用
