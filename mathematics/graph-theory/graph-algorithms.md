# 图算法 (Graph Algorithms)

## 简介

图算法是计算机科学中最重要的算法类别之一，用于解决与图结构相关的各种问题。图由顶点（节点）和边（连接）组成，能够建模现实世界中的许多复杂关系，如社交网络、道路网络、依赖关系等。

本文档总结常用的图算法及其应用，包括连通性分析、路径查找、拓扑排序等。

## 核心概念

### 图的表示方法

```python
from collections import defaultdict, deque

class GraphRepresentation:
    """图的多种表示方法"""
    
    @staticmethod
    def adjacency_list(edges, n):
        """
        邻接表表示
        空间复杂度: O(V + E)
        适合：稀疏图
        """
        graph = defaultdict(list)
        for u, v in edges:
            graph[u].append(v)
            graph[v].append(u)  # 无向图
        return graph
    
    @staticmethod
    def adjacency_matrix(edges, n):
        """
        邻接矩阵表示
        空间复杂度: O(V²)
        适合：稠密图
        """
        matrix = [[0] * n for _ in range(n)]
        for u, v in edges:
            matrix[u][v] = 1
            matrix[v][u] = 1  # 无向图
        return matrix
    
    @staticmethod
    def edge_list_to_adjacency(edges, directed=False):
        """边列表转邻接表"""
        graph = defaultdict(list)
        for edge in edges:
            if len(edge) == 2:
                u, v = edge
                weight = 1
            else:
                u, v, weight = edge
            
            graph[u].append((v, weight))
            if not directed:
                graph[v].append((u, weight))
        
        return graph
```

### 图的连通性

```python
class GraphConnectivity:
    """图连通性分析"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def is_connected(self, n):
        """
        检查无向图是否连通
        时间复杂度: O(V + E)
        """
        visited = [False] * n
        self._dfs(0, visited)
        return all(visited)
    
    def _dfs(self, u, visited):
        """DFS辅助函数"""
        visited[u] = True
        for v in self.graph.get(u, []):
            if isinstance(v, tuple):
                v = v[0]
            if not visited[v]:
                self._dfs(v, visited)
    
    def connected_components(self, n):
        """
        找出所有连通分量
        返回: 每个连通分量的顶点列表
        """
        visited = [False] * n
        components = []
        
        for i in range(n):
            if not visited[i]:
                component = []
                self._dfs_collect(i, visited, component)
                components.append(component)
        
        return components
    
    def _dfs_collect(self, u, visited, component):
        """收集连通分量"""
        visited[u] = True
        component.append(u)
        
        for v in self.graph.get(u, []):
            if isinstance(v, tuple):
                v = v[0]
            if not visited[v]:
                self._dfs_collect(v, visited, component)
    
    def count_components(self, n):
        """计算连通分量数量"""
        return len(self.connected_components(n))
```

## 实现方式

### 拓扑排序

```python
class TopologicalSort:
    """拓扑排序算法"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def kahn_algorithm(self, n):
        """
        Kahn算法（BFS实现）
        时间复杂度: O(V + E)
        适用于有向无环图（DAG）
        """
        # 计算入度
        in_degree = {i: 0 for i in range(n)}
        for u in self.graph:
            for v in self.graph[u]:
                if isinstance(v, tuple):
                    v = v[0]
                in_degree[v] += 1
        
        # 入度为0的顶点入队
        queue = deque([u for u in range(n) if in_degree[u] == 0])
        result = []
        
        while queue:
            u = queue.popleft()
            result.append(u)
            
            for v in self.graph.get(u, []):
                if isinstance(v, tuple):
                    v = v[0]
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        
        # 检查是否存在环
        if len(result) != n:
            return None  # 图中存在环
        
        return result
    
    def dfs_algorithm(self, n):
        """
        DFS实现拓扑排序
        """
        visited = [False] * n
        stack = []
        
        def dfs(u):
            visited[u] = True
            for v in self.graph.get(u, []):
                if isinstance(v, tuple):
                    v = v[0]
                if not visited[v]:
                    dfs(v)
            stack.append(u)
        
        for i in range(n):
            if not visited[i]:
                dfs(i)
        
        return stack[::-1]
```

### 强连通分量（SCC）

```python
class StronglyConnectedComponents:
    """强连通分量算法（Kosaraju算法）"""
    
    def __init__(self, graph):
        self.graph = graph
        self.n = len(graph)
    
    def find_scc(self):
        """
        找出所有强连通分量
        时间复杂度: O(V + E)
        """
        # 第一次DFS，记录完成时间
        visited = [False] * self.n
        stack = []
        
        def dfs1(u):
            visited[u] = True
            for v in self.graph.get(u, []):
                if isinstance(v, tuple):
                    v = v[0]
                if not visited[v]:
                    dfs1(v)
            stack.append(u)
        
        for i in range(self.n):
            if not visited[i]:
                dfs1(i)
        
        # 构建反向图
        reverse_graph = defaultdict(list)
        for u in self.graph:
            for v in self.graph[u]:
                if isinstance(v, tuple):
                    v = v[0]
                reverse_graph[v].append(u)
        
        # 第二次DFS，在反向图上按完成时间逆序
        visited = [False] * self.n
        sccs = []
        
        def dfs2(u, component):
            visited[u] = True
            component.append(u)
            for v in reverse_graph.get(u, []):
                if not visited[v]:
                    dfs2(v, component)
        
        while stack:
            u = stack.pop()
            if not visited[u]:
                component = []
                dfs2(u, component)
                sccs.append(component)
        
        return sccs
```

## 示例

### 课程选修计划

```python
class CourseScheduler:
    """课程表规划（拓扑排序应用）"""
    
    def __init__(self, num_courses):
        self.n = num_courses
        self.graph = defaultdict(list)
    
    def add_prerequisite(self, course, prereq):
        """添加先修课程关系：prereq -> course"""
        self.graph[prereq].append(course)
    
    def can_finish(self):
        """判断是否可能完成所有课程"""
        topo = TopologicalSort(self.graph)
        result = topo.kahn_algorithm(self.n)
        return result is not None
    
    def find_order(self):
        """找到一种可行的修课顺序"""
        topo = TopologicalSort(self.graph)
        return topo.kahn_algorithm(self.n)
    
    def minimum_semesters(self):
        """
        计算完成所有课程所需的最少学期数
        使用动态规划思想
        """
        # 计算每个课程的最早完成时间
        in_degree = [0] * self.n
        for u in self.graph:
            for v in self.graph[u]:
                in_degree[v] += 1
        
        # 每个课程的最早学期
        semester = [1] * self.n
        queue = deque()
        
        for i in range(self.n):
            if in_degree[i] == 0:
                queue.append(i)
        
        while queue:
            u = queue.popleft()
            for v in self.graph[u]:
                in_degree[v] -= 1
                # 更新最早学期
                semester[v] = max(semester[v], semester[u] + 1)
                if in_degree[v] == 0:
                    queue.append(v)
        
        return max(semester)

# 示例
cs = CourseScheduler(4)
cs.add_prerequisite(1, 0)  # 课程0是课程1的先修
cs.add_prerequisite(2, 1)
cs.add_prerequisite(3, 2)

print("Can finish:", cs.can_finish())  # True
print("Order:", cs.find_order())  # [0, 1, 2, 3]
print("Min semesters:", cs.minimum_semesters())  # 4
```

### 关键路径分析

```python
class CriticalPath:
    """AOE网络的关键路径分析"""
    
    def __init__(self, n):
        self.n = n
        self.graph = defaultdict(list)
        self.edges = []
    
    def add_activity(self, u, v, duration):
        """添加活动：从u到v，持续duration时间"""
        self.graph[u].append((v, duration))
        self.edges.append((u, v, duration))
    
    def find_critical_path(self):
        """
        找到关键路径
        返回: (critical_activities, project_duration)
        """
        # 计算最早开始时间（拓扑序）
        topo = TopologicalSort(self.graph)
        order = topo.dfs_algorithm(self.n)
        
        earliest = [0] * self.n
        for u in order:
            for v, duration in self.graph[u]:
                earliest[v] = max(earliest[v], earliest[u] + duration)
        
        project_duration = max(earliest)
        
        # 计算最晚开始时间（逆拓扑序）
        latest = [project_duration] * self.n
        for u in reversed(order):
            for v, duration in self.graph[u]:
                latest[u] = min(latest[u], latest[v] - duration)
        
        # 关键活动：最早开始时间 = 最晚开始时间
        critical = []
        for u, v, duration in self.edges:
            if earliest[u] == latest[u]:
                critical.append((u, v, duration))
        
        return critical, project_duration
```

## 应用场景

### 图算法的典型应用

| 应用领域 | 算法 | 问题描述 |
|---------|-----|---------|
| 社交网络 | BFS/DFS | 好友推荐、社区发现 |
| 导航系统 | Dijkstra/A* | 最短路径规划 |
| 编译器 | 拓扑排序 | 依赖分析、代码优化 |
| 项目管理 | 关键路径 | 工期估算、资源调度 |
| 网络安全 | SCC | 僵尸网络检测 |

## 面试要点

**Q: 如何判断有向图是否有环？**
A: 三种方法：
1. 拓扑排序：Kahn算法无法处理所有顶点则存在环
2. DFS三色标记：遇到灰色顶点（访问中）说明有环
3. 计算完成时间：存在回边则有环

**Q: 强连通分量和连通分量的区别？**
A: 连通分量用于无向图，基于可达性；强连通分量用于有向图，要求双向可达（u可到v且v可到u）。

**Q: 拓扑排序的时间复杂度？**
A: O(V + E)。每个顶点和边只处理一次。

## 相关概念

### 数据结构
- [图](../../computer-science/data-structures/graph.md) - 图的表示方法
- [并查集](../../computer-science/data-structures/union-find.md) - 连通性分析

### 算法
- [图遍历](./graph-traversal.md) - DFS和BFS基础
- [最短路径](./shortest-paths.md) - 路径查找算法
- [最小生成树](./minimum-spanning-trees.md) - 连通子图

### 复杂度分析
- [时间复杂度](../../computer-science/algorithms/time-complexity.md)

### 系统实现
- [依赖管理](../../software-engineering/system-design/dependency-management.md) - 拓扑排序应用
- [工作流引擎](../../software-engineering/system-design/workflow-engine.md) - 图调度
