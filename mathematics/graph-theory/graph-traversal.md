# 图遍历 (Graph Traversal)

## 简介

图遍历（Graph Traversal）是图论中的基本算法，用于系统地访问图中的所有顶点。与树的遍历不同，图可能包含环，因此需要额外机制避免重复访问。两种主要的图遍历算法是深度优先搜索（DFS）和广度优先搜索（BFS），它们是解决许多图问题的基础。

## 核心概念

### 深度优先搜索 (DFS)

```python
from collections import defaultdict

class Graph:
    """图的基本实现"""
    
    def __init__(self):
        self.graph = defaultdict(list)
    
    def add_edge(self, u, v):
        """添加边（无向图）"""
        self.graph[u].append(v)
        self.graph[v].append(u)
    
    def add_directed_edge(self, u, v):
        """添加有向边"""
        self.graph[u].append(v)

class DFS:
    """深度优先搜索"""
    
    def __init__(self, graph):
        self.graph = graph
        self.visited = set()
        self.discovery_time = {}
        self.finish_time = {}
        self.time = 0
        self.parent = {}
    
    def traverse(self, start):
        """
        从start顶点开始DFS遍历
        时间复杂度: O(V + E)
        空间复杂度: O(V)
        """
        self.visited.clear()
        self.discovery_time.clear()
        self.finish_time.clear()
        self.time = 0
        self.parent.clear()
        
        self._dfs_util(start)
        return list(self.visited)
    
    def _dfs_util(self, vertex):
        """DFS递归辅助函数"""
        self.visited.add(vertex)
        self.time += 1
        self.discovery_time[vertex] = self.time
        
        for neighbor in self.graph.graph[vertex]:
            if neighbor not in self.visited:
                self.parent[neighbor] = vertex
                self._dfs_util(neighbor)
        
        self.time += 1
        self.finish_time[vertex] = self.time
    
    def traverse_all(self):
        """遍历所有连通分量"""
        self.visited.clear()
        result = []
        
        for vertex in self.graph.graph:
            if vertex not in self.visited:
                component = []
                self._dfs_collect(vertex, component)
                result.append(component)
        
        return result
    
    def _dfs_collect(self, vertex, component):
        """收集连通分量的所有顶点"""
        self.visited.add(vertex)
        component.append(vertex)
        
        for neighbor in self.graph.graph[vertex]:
            if neighbor not in self.visited:
                self._dfs_collect(neighbor, component)

# 示例
g = Graph()
g.add_edge(0, 1)
g.add_edge(0, 2)
g.add_edge(1, 3)
g.add_edge(2, 4)

dfs = DFS(g)
print("DFS from 0:", dfs.traverse(0))  # [0, 1, 3, 2, 4]
```

### 广度优先搜索 (BFS)

```python
from collections import deque

class BFS:
    """广度优先搜索"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def traverse(self, start):
        """
        从start顶点开始BFS遍历
        时间复杂度: O(V + E)
        空间复杂度: O(V)
        """
        visited = {start}
        queue = deque([start])
        result = [start]
        
        while queue:
            vertex = queue.popleft()
            
            for neighbor in self.graph.graph[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    result.append(neighbor)
        
        return result
    
    def shortest_path(self, start, end):
        """
        求最短路径（无权图）
        BFS保证找到的路径是最短的
        """
        if start == end:
            return [start]
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            vertex, path = queue.popleft()
            
            for neighbor in self.graph.graph[vertex]:
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # 无路径
    
    def level_order(self, start):
        """按层级遍历"""
        visited = {start}
        queue = deque([start])
        levels = [[start]]
        
        while queue:
            level_size = len(queue)
            current_level = []
            
            for _ in range(level_size):
                vertex = queue.popleft()
                
                for neighbor in self.graph.graph[vertex]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        current_level.append(neighbor)
            
            if current_level:
                levels.append(current_level)
        
        return levels

# 示例
bfs = BFS(g)
print("BFS from 0:", bfs.traverse(0))  # [0, 1, 2, 3, 4]
print("Shortest path 0 to 4:", bfs.shortest_path(0, 4))  # [0, 2, 4]
print("Level order:", bfs.level_order(0))  # [[0], [1, 2], [3, 4]]
```

## 实现方式

### 图的连通性

```python
class GraphConnectivity:
    """图的连通性分析"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def is_connected(self):
        """检查无向图是否连通"""
        if not self.graph.graph:
            return True
        
        start = next(iter(self.graph.graph))
        dfs = DFS(self.graph)
        dfs.traverse(start)
        
        return len(dfs.visited) == len(self.graph.graph)
    
    def connected_components(self):
        """找出所有连通分量"""
        dfs = DFS(self.graph)
        return dfs.traverse_all()
    
    def count_components(self):
        """计算连通分量数量"""
        return len(self.connected_components())
    
    def is_bipartite(self):
        """
        检查图是否为二分图
        使用BFS进行二染色
        """
        if not self.graph.graph:
            return True
        
        color = {}
        
        for start in self.graph.graph:
            if start in color:
                continue
            
            queue = deque([start])
            color[start] = 0
            
            while queue:
                vertex = queue.popleft()
                
                for neighbor in self.graph.graph[vertex]:
                    if neighbor not in color:
                        color[neighbor] = 1 - color[vertex]
                        queue.append(neighbor)
                    elif color[neighbor] == color[vertex]:
                        return False
        
        return True

# 示例
conn = GraphConnectivity(g)
print("Is connected:", conn.is_connected())  # True
print("Components:", conn.connected_components())  # [[0, 1, 2, 3, 4]]
print("Is bipartite:", conn.is_bipartite())  # True
```

### 环检测

```python
class CycleDetection:
    """环检测算法"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def has_cycle_undirected(self):
        """
        检测无向图中的环
        使用DFS，记录父节点避免误判
        """
        visited = set()
        
        def dfs(vertex, parent):
            visited.add(vertex)
            
            for neighbor in self.graph.graph[vertex]:
                if neighbor not in visited:
                    if dfs(neighbor, vertex):
                        return True
                elif neighbor != parent:
                    return True
            
            return False
        
        for vertex in self.graph.graph:
            if vertex not in visited:
                if dfs(vertex, None):
                    return True
        
        return False
    
    def has_cycle_directed(self):
        """
        检测有向图中的环
        使用三色标记法：0=未访问, 1=访问中, 2=已完成
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {v: WHITE for v in self.graph.graph}
        
        def dfs(vertex):
            color[vertex] = GRAY
            
            for neighbor in self.graph.graph[vertex]:
                if color[neighbor] == GRAY:
                    return True  # 发现回边，存在环
                if color[neighbor] == WHITE and dfs(neighbor):
                    return True
            
            color[vertex] = BLACK
            return False
        
        for vertex in self.graph.graph:
            if color[vertex] == WHITE:
                if dfs(vertex):
                    return True
        
        return False

# 示例
cycle_det = CycleDetection(g)
print("Has cycle (undirected):", cycle_det.has_cycle_undirected())  # False
```

## 示例

### 拓扑排序（DFS实现）

```python
class TopologicalSort:
    """拓扑排序"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def sort(self):
        """
        使用DFS进行拓扑排序
        时间复杂度: O(V + E)
        仅适用于DAG（有向无环图）
        """
        visited = set()
        stack = []
        
        def dfs(vertex):
            visited.add(vertex)
            
            for neighbor in self.graph.graph[vertex]:
                if neighbor not in visited:
                    dfs(neighbor)
            
            stack.append(vertex)
        
        for vertex in self.graph.graph:
            if vertex not in visited:
                dfs(vertex)
        
        return stack[::-1]  # 反转得到拓扑序

# 示例：课程先修关系
course_graph = Graph()
course_graph.add_directed_edge("CS101", "CS102")
course_graph.add_directed_edge("CS102", "CS201")
course_graph.add_directed_edge("Math101", "CS201")

topo = TopologicalSort(course_graph)
print("Topological order:", topo.sort())
# 可能输出: ['Math101', 'CS101', 'CS102', 'CS201']
```

## 应用场景

### 图遍历的应用

1. **路径查找**：最短路径、迷宫求解
2. **连通性分析**：网络连通性、社交网络分析
3. **拓扑排序**：任务调度、编译顺序
4. **环检测**：死锁检测、依赖分析
5. **二分图判断**：匹配问题、着色问题

## 面试要点

**Q: DFS和BFS的区别是什么？**
A: 
- DFS使用栈（递归），探索深度优先，适合找路径、检测环
- BFS使用队列，按层级扩展，适合找最短路径、层级遍历

**Q: 如何判断图是否有环？**
A: 
- 无向图：DFS时遇到已访问的非父节点
- 有向图：三色标记法或计算完成时间判断回边

**Q: 图的遍历时间复杂度是多少？**
A: O(V + E)，其中V是顶点数，E是边数。每个顶点和边只访问一次。

## 相关概念

### 数据结构
- [图](../../computer-science/data-structures/graph.md) - 图的存储结构
- [队列](../../computer-science/data-structures/queue.md) - BFS使用
- [栈](../../computer-science/data-structures/stack.md) - DFS使用

### 算法
- [最短路径](./shortest-paths.md) - BFS应用
- [拓扑排序](../../computer-science/algorithms/topological-sort.md) - DFS应用

### 复杂度分析
- [时间复杂度](../../computer-science/algorithms/time-complexity.md)

### 系统实现
- [网络爬虫](../../software-engineering/system-design/web-crawler.md) - BFS/DFS应用
