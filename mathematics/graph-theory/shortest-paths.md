# 最短路径 (Shortest Paths)

## 简介

最短路径问题是图论中最重要的问题之一，旨在找到图中两个顶点之间权重和最小的路径。该问题在许多实际应用中都有出现，包括GPS导航、网络路由、物流配送、社交网络分析等。

根据图的特性和需求，有多种算法可以解决最短路径问题，包括Dijkstra算法、Bellman-Ford算法、Floyd-Warshall算法等。

## 核心概念

### Dijkstra算法

```python
import heapq
from math import inf

class Dijkstra:
    """
    Dijkstra最短路径算法
    适用于：带权有向图/无向图，边权重非负
    时间复杂度: O((V + E) log V) 使用优先队列
    """
    
    def __init__(self, graph):
        """
        graph: dict, graph[u] = [(v, weight), ...]
        """
        self.graph = graph
    
    def shortest_path(self, start):
        """
        从start到所有其他顶点的最短路径
        返回: (distances, predecessors)
        """
        distances = {v: inf for v in self.graph}
        distances[start] = 0
        predecessors = {v: None for v in self.graph}
        
        # 优先队列: (distance, vertex)
        pq = [(0, start)]
        visited = set()
        
        while pq:
            dist_u, u = heapq.heappop(pq)
            
            if u in visited:
                continue
            visited.add(u)
            
            for v, weight in self.graph[u]:
                if v not in visited:
                    new_dist = dist_u + weight
                    if new_dist < distances[v]:
                        distances[v] = new_dist
                        predecessors[v] = u
                        heapq.heappush(pq, (new_dist, v))
        
        return distances, predecessors
    
    def path_to(self, start, end):
        """获取从start到end的具体路径"""
        distances, predecessors = self.shortest_path(start)
        
        if distances[end] == inf:
            return None, inf
        
        # 重建路径
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        return path[::-1], distances[end]

# 示例
graph = {
    'A': [('B', 4), ('C', 2)],
    'B': [('C', 1), ('D', 5)],
    'C': [('D', 8), ('E', 10)],
    'D': [('E', 2)],
    'E': []
}

dijkstra = Dijkstra(graph)
distances, _ = dijkstra.shortest_path('A')
print("Distances from A:", distances)

path, dist = dijkstra.path_to('A', 'E')
print(f"Path A to E: {' -> '.join(path)}, distance: {dist}")
```

### Bellman-Ford算法

```python
class BellmanFord:
    """
    Bellman-Ford算法
    适用于：带权图，可处理负权边（无负权环）
    时间复杂度: O(V * E)
    """
    
    def __init__(self, vertices, edges):
        """
        vertices: 顶点列表
        edges: [(u, v, weight), ...] 边列表
        """
        self.vertices = vertices
        self.edges = edges
    
    def shortest_path(self, start):
        """
        计算最短路径
        返回: (distances, predecessors, has_negative_cycle)
        """
        distances = {v: inf for v in self.vertices}
        distances[start] = 0
        predecessors = {v: None for v in self.vertices}
        
        # 松弛操作，重复V-1次
        for _ in range(len(self.vertices) - 1):
            for u, v, weight in self.edges:
                if distances[u] != inf and distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u
        
        # 检查负权环
        has_negative_cycle = False
        for u, v, weight in self.edges:
            if distances[u] != inf and distances[u] + weight < distances[v]:
                has_negative_cycle = True
                break
        
        return distances, predecessors, has_negative_cycle

# 示例（含负权边）
vertices = ['A', 'B', 'C', 'D']
edges = [
    ('A', 'B', 1),
    ('B', 'C', -2),
    ('C', 'D', 3),
    ('A', 'D', 10)
]

bf = BellmanFord(vertices, edges)
distances, _, has_neg_cycle = bf.shortest_path('A')
print("Distances:", distances)
print("Has negative cycle:", has_neg_cycle)
```

## 实现方式

### Floyd-Warshall算法

```python
class FloydWarshall:
    """
    Floyd-Warshall算法
    适用于：所有顶点对之间的最短路径
    可处理负权边（无负权环）
    时间复杂度: O(V³)
    空间复杂度: O(V²)
    """
    
    def __init__(self, n):
        """
        n: 顶点数量，顶点编号0到n-1
        """
        self.n = n
        self.dist = [[inf] * n for _ in range(n)]
        self.next_vertex = [[None] * n for _ in range(n)]
        
        # 初始化对角线
        for i in range(n):
            self.dist[i][i] = 0
    
    def add_edge(self, u, v, weight):
        """添加边"""
        self.dist[u][v] = weight
        self.next_vertex[u][v] = v
    
    def compute(self):
        """计算所有顶点对的最短路径"""
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    if (self.dist[i][k] != inf and 
                        self.dist[k][j] != inf and
                        self.dist[i][k] + self.dist[k][j] < self.dist[i][j]):
                        
                        self.dist[i][j] = self.dist[i][k] + self.dist[k][j]
                        self.next_vertex[i][j] = self.next_vertex[i][k]
    
    def get_distance(self, u, v):
        """获取u到v的最短距离"""
        return self.dist[u][v]
    
    def get_path(self, u, v):
        """获取u到v的最短路径"""
        if self.dist[u][v] == inf:
            return None
        
        path = [u]
        current = u
        while current != v:
            current = self.next_vertex[current][v]
            path.append(current)
        
        return path

# 示例
fw = FloydWarshall(4)
fw.add_edge(0, 1, 5)
fw.add_edge(0, 3, 10)
fw.add_edge(1, 2, 3)
fw.add_edge(2, 3, 1)
fw.compute()

print("Distance 0 to 3:", fw.get_distance(0, 3))
print("Path 0 to 3:", fw.get_path(0, 3))
```

### SPFA算法

```python
from collections import deque

class SPFA:
    """
    Shortest Path Faster Algorithm (SPFA)
    Bellman-Ford的队列优化版本
    平均性能较好，最坏情况O(V * E)
    """
    
    def __init__(self, graph):
        self.graph = graph
    
    def shortest_path(self, start):
        distances = {v: inf for v in self.graph}
        distances[start] = 0
        
        queue = deque([start])
        in_queue = {v: False for v in self.graph}
        in_queue[start] = True
        
        # 记录入队次数，用于检测负权环
        count = {v: 0 for v in self.graph}
        
        while queue:
            u = queue.popleft()
            in_queue[u] = False
            
            for v, weight in self.graph[u]:
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True
                        count[v] += 1
                        
                        if count[v] > len(self.graph):
                            raise ValueError("Negative cycle detected")
        
        return distances
```

## 示例

### 多源最短路径应用

```python
class MultiSourceShortestPath:
    """多源最短路径问题"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def nearest_facility(self, sources, targets):
        """
        找到每个目标到最近设施的距离
        例如：找到每个住宅到最近的医院/学校的距离
        
        方法：从所有设施同时运行多源Dijkstra
        """
        distances = {v: inf for v in self.graph}
        sources_info = {}
        
        pq = []
        for source in sources:
            distances[source] = 0
            sources_info[source] = source
            heapq.heappush(pq, (0, source))
        
        while pq:
            dist_u, u = heapq.heappop(pq)
            
            if dist_u > distances[u]:
                continue
            
            for v, weight in self.graph[u]:
                new_dist = dist_u + weight
                if new_dist < distances[v]:
                    distances[v] = new_dist
                    sources_info[v] = sources_info[u]
                    heapq.heappush(pq, (new_dist, v))
        
        return {t: (distances[t], sources_info.get(t)) for t in targets}

# 示例：配送中心选址
graph = {
    'A': [('B', 2), ('C', 4)],
    'B': [('A', 2), ('C', 1), ('D', 7)],
    'C': [('A', 4), ('B', 1), ('D', 3)],
    'D': [('B', 7), ('C', 3), ('E', 2)],
    'E': [('D', 2)]
}

sources = ['A', 'C']  # 两个配送中心
targets = ['B', 'D', 'E']

mssp = MultiSourceShortestPath(graph)
result = mssp.nearest_facility(sources, targets)
for t, (dist, source) in result.items():
    print(f"{t}: distance={dist}, nearest source={source}")
```

## 应用场景

### 最短路径算法的应用

| 应用场景 | 推荐算法 | 原因 |
|---------|---------|-----|
| GPS导航 | A* / Dijkstra | 需要实时响应 |
| 网络路由 | Dijkstra / SPF | 无负权，需要稳定性 |
| 货币套利 | Bellman-Ford | 检测负权环 |
| 全对全距离 | Floyd-Warshall | 预计算所有路径 |
| 动态图 | SPFA | 适应边权重变化 |

## 面试要点

**Q: Dijkstra算法为什么不能处理负权边？**
A: Dijkstra贪心选择最短路径后不再更新，但负权边可能导致之前确定的最短路径不是真正的最短。例如：A→B(5)，A→C(3)，C→B(-2)，Dijkstra会先选B的距离为5，但实际最短是A→C→B=1。

**Q: 如何选择最短路径算法？**
A: 
- 单源、无负权：Dijkstra
- 单源、有负权：Bellman-Ford/SPFA
- 所有顶点对：Floyd-Warshall
- 大规模稀疏图：Dijkstra + 优先队列

**Q: Floyd-Warshall算法的动态规划状态定义？**
A: `dist[i][j][k]`表示从i到j只经过顶点{1,2,...,k}的最短距离。递推：`dist[i][j][k] = min(dist[i][j][k-1], dist[i][k][k-1] + dist[k][j][k-1])`

## 相关概念

### 数据结构
- [图](../../computer-science/data-structures/graph.md) - 图的表示
- [优先队列](../../computer-science/data-structures/priority-queue.md) - Dijkstra使用

### 算法
- [图遍历](./graph-traversal.md) - 最短路径基础
- [A*算法](../../computer-science/algorithms/a-star.md) - 启发式最短路径

### 复杂度分析
- [时间复杂度](../../computer-science/algorithms/time-complexity.md)

### 系统实现
- [网络路由](../../computer-science/networks/routing.md) - 路由算法应用
