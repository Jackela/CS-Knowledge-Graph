# 网络流 (Network Flow)

## 简介

网络流（Network Flow）是图论中研究如何在网络中传输物质（如数据、货物、电流）的理论。网络流问题在物流、通信、交通等领域有广泛应用。最大流问题是最经典的网络流问题，旨在找到从源点到汇点的最大传输量。

## 核心概念

### 最大流问题

```python
from collections import deque

class MaxFlow:
    """
    Edmonds-Karp算法实现最大流
    Ford-Fulkerson方法的BFS实现
    时间复杂度: O(V * E²)
    """
    
    def __init__(self, graph):
        """
        graph: 残量网络，dict of dict
        graph[u][v] = capacity from u to v
        """
        self.graph = graph
        self.n = len(graph)
    
    def bfs(self, source, sink, parent):
        """
        使用BFS寻找增广路径
        返回: 是否找到路径
        """
        visited = {source}
        queue = deque([source])
        
        while queue:
            u = queue.popleft()
            
            for v in self.graph[u]:
                if v not in visited and self.graph[u][v] > 0:
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)
                    
                    if v == sink:
                        return True
        
        return False
    
    def ford_fulkerson(self, source, sink):
        """
        Ford-Fulkerson算法（Edmonds-Karp实现）
        返回最大流值
        """
        parent = {}
        max_flow = 0
        
        # 当存在增广路径时
        while self.bfs(source, sink, parent):
            # 找到路径上的最小残量
            path_flow = float('inf')
            s = sink
            while s != source:
                path_flow = min(path_flow, self.graph[parent[s]][s])
                s = parent[s]
            
            # 更新残量网络
            v = sink
            while v != source:
                u = parent[v]
                self.graph[u][v] -= path_flow
                
                # 添加反向边
                if v not in self.graph:
                    self.graph[v] = {}
                if u not in self.graph[v]:
                    self.graph[v][u] = 0
                self.graph[v][u] += path_flow
                
                v = u
            
            max_flow += path_flow
            parent = {}
        
        return max_flow

# 示例
graph = {
    'S': {'A': 10, 'B': 5},
    'A': {'B': 15, 'C': 5},
    'B': {'C': 10, 'D': 10},
    'C': {'T': 10},
    'D': {'T': 5},
    'T': {}
}

mf = MaxFlow(graph)
max_flow = mf.ford_fulkerson('S', 'T')
print(f"Maximum flow: {max_flow}")  # 15
```

### Dinic算法

```python
class Dinic:
    """
    Dinic算法实现最大流
    使用分层图和阻塞流
    时间复杂度: O(V² * E)（一般图），O(E * V^0.5)（单位容量）
    """
    
    def __init__(self, n):
        self.n = n
        self.graph = [[] for _ in range(n)]
        self.capacity = {}
    
    def add_edge(self, u, v, cap):
        """添加边"""
        self.graph[u].append(v)
        self.graph[v].append(u)
        self.capacity[(u, v)] = cap
        self.capacity[(v, u)] = 0
    
    def bfs_level(self, source, sink):
        """构建分层图"""
        self.level = [-1] * self.n
        self.level[source] = 0
        queue = deque([source])
        
        while queue:
            u = queue.popleft()
            for v in self.graph[u]:
                if self.level[v] < 0 and self.capacity[(u, v)] > 0:
                    self.level[v] = self.level[u] + 1
                    queue.append(v)
        
        return self.level[sink] >= 0
    
    def dfs_flow(self, u, sink, flow):
        """在分层图中寻找阻塞流"""
        if u == sink:
            return flow
        
        for v in self.graph[u]:
            if (self.level[v] == self.level[u] + 1 and 
                self.capacity[(u, v)] > 0):
                
                min_flow = min(flow, self.capacity[(u, v)])
                result = self.dfs_flow(v, sink, min_flow)
                
                if result > 0:
                    self.capacity[(u, v)] -= result
                    self.capacity[(v, u)] += result
                    return result
        
        return 0
    
    def max_flow(self, source, sink):
        """计算最大流"""
        total_flow = 0
        
        while self.bfs_level(source, sink):
            while True:
                flow = self.dfs_flow(source, sink, float('inf'))
                if flow == 0:
                    break
                total_flow += flow
        
        return total_flow
```

## 实现方式

### 最小割

```python
class MinCut:
    """最小割算法"""
    
    def __init__(self, max_flow_solver):
        self.solver = max_flow_solver
    
    def find_min_cut(self, source, sink):
        """
        找到最小割
        根据最大流最小割定理：最大流 = 最小割容量
        返回: (cut_edges, min_cut_capacity, reachable_from_source)
        """
        # 先计算最大流
        max_flow = self.solver.ford_fulkerson(source, sink)
        
        # 在残量网络中从源点DFS，找到可达集合
        visited = set()
        self._dfs_residual(source, visited)
        
        # 割边：从可达集合指向不可达集合的边
        cut_edges = []
        for u in visited:
            for v in self.solver.graph[u]:
                if v not in visited and self.solver.graph[u][v] == 0:
                    # 这是原始图中的边，且在割上
                    cut_edges.append((u, v))
        
        return cut_edges, max_flow, visited
    
    def _dfs_residual(self, u, visited):
        """在残量网络中DFS"""
        visited.add(u)
        for v in self.solver.graph[u]:
            if v not in visited and self.solver.graph[u][v] > 0:
                self._dfs_residual(v, visited)
```

### 多源多汇最大流

```python
class MultiSourceMaxFlow:
    """多源多汇最大流"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def solve(self, sources, sinks):
        """
        解决多源多汇问题
        方法：添加超级源点和超级汇点
        """
        # 创建扩展图
        extended_graph = {k: dict(v) for k, v in self.graph.items()}
        
        # 添加超级源点'S'
        extended_graph['S'] = {}
        for s in sources:
            extended_graph['S'][s] = float('inf')
        
        # 添加超级汇点'T'
        extended_graph['T'] = {}
        for t in sinks:
            if t not in extended_graph:
                extended_graph[t] = {}
            extended_graph[t]['T'] = float('inf')
        
        # 使用普通最大流算法
        mf = MaxFlow(extended_graph)
        return mf.ford_fulkerson('S', 'T')
```

## 示例

### 二分图匹配

```python
class BipartiteMatching:
    """
    二分图最大匹配
    使用网络流方法
    """
    
    def __init__(self, left_set, right_set, edges):
        """
        left_set: 左侧顶点集合
        right_set: 右侧顶点集合
        edges: 边列表 [(u, v), ...]
        """
        self.left = left_set
        self.right = right_set
        self.edges = edges
    
    def max_matching(self):
        """找到最大匹配"""
        # 构建流网络
        graph = {'S': {}, 'T': {}}
        
        # 添加源点到左侧的边
        for u in self.left:
            graph['S'][u] = 1
            graph[u] = {}
        
        # 添加右侧到汇点的边
        for v in self.right:
            graph[v] = {'T': 1}
        
        # 添加左右之间的边
        for u, v in self.edges:
            graph[u][v] = 1
        
        mf = MaxFlow(graph)
        return mf.ford_fulkerson('S', 'T')
    
    def find_matching_pairs(self):
        """找到具体的匹配对"""
        # 运行最大流
        self.max_matching()
        
        # 从残量网络中提取匹配
        matching = []
        for u in self.left:
            for v in self.right:
                if (u, v) in [(e[0], e[1]) for e in self.edges]:
                    # 检查反向边流量
                    # 如果存在从v到u的反向边且有流量，说明匹配
                    pass  # 简化处理
        
        return matching

# 示例：工作分配
left = ['Worker1', 'Worker2', 'Worker3']
right = ['JobA', 'JobB', 'JobC']
edges = [
    ('Worker1', 'JobA'),
    ('Worker1', 'JobB'),
    ('Worker2', 'JobB'),
    ('Worker2', 'JobC'),
    ('Worker3', 'JobA'),
    ('Worker3', 'JobC')
]

bm = BipartiteMatching(left, right, edges)
print(f"Maximum matching: {bm.max_matching()}")  # 3
```

## 应用场景

### 网络流的应用

1. **交通网络**：最大车流量计算
2. **物流配送**：运输网络优化
3. **网络通信**：带宽分配、拥塞控制
4. **任务分配**：二分图匹配问题
5. **图像分割**：最小割用于图像分割

## 面试要点

**Q: 最大流最小割定理的内容？**
A: 在任何流网络中，从源点到汇点的最大流值等于分离源点和汇点的最小割的容量。

**Q: Ford-Fulkerson和Edmonds-Karp的区别？**
A: Ford-Fulkerson是方法框架，使用任意方法找增广路径。Edmonds-Karp是其具体实现，使用BFS找最短增广路径，保证多项式时间复杂度。

**Q: 如何处理边的容量为无穷大的情况？**
A: 实际实现中使用一个足够大的数（如10^9）代替无穷大，或在算法中特殊处理。

## 相关概念

### 数据结构
- [图](../../computer-science/data-structures/graph.md) - 流网络表示
- [队列](../../computer-science/data-structures/queue.md) - BFS使用

### 算法
- [图遍历](./graph-traversal.md) - 寻找增广路径
- [二分图匹配](../../computer-science/algorithms/bipartite-matching.md) - 网络流应用

### 复杂度分析
- [时间复杂度](../../computer-science/algorithms/time-complexity.md)

### 系统实现
- [网络路由](../../computer-science/networks/routing.md) - 流量工程
