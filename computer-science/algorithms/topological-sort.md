# 拓扑排序 (Topological Sort)

## 简介

**拓扑排序（Topological Sort）**是对**有向无环图（DAG, Directed Acyclic Graph）**的顶点进行线性排序，使得对于图中的每条有向边 $(u, v)$，顶点 $u$ 在排序中都位于 $v$ 之前。

```
DAG:

    5 ──→ 0 ←── 4
    │         │
    ↓         ↓
    2 ──→ 3 ──→ 1

拓扑排序结果: [5, 4, 2, 3, 1, 0] 或 [4, 5, 2, 3, 0, 1] 等
```

拓扑排序存在的**充要条件**：图是有向无环图（DAG）。

## 算法

### 1. Kahn算法（BFS）

基于入度的算法。

```python
from collections import deque

def topological_sort_kahn(graph):
    """
    graph: {v: [neighbors]}
    返回: 拓扑排序列表，若存在环则返回空列表
    """
    n = len(graph)
    in_degree = {v: 0 for v in graph}
    
    # 计算入度
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1
    
    # 入度为0的顶点入队
    queue = deque([v for v in graph if in_degree[v] == 0])
    result = []
    
    while queue:
        u = queue.popleft()
        result.append(u)
        
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    
    # 检查是否有环
    if len(result) != n:
        return []  # 存在环
    
    return result
```

### 2. DFS算法

利用DFS的后序遍历。

```python
def topological_sort_dfs(graph):
    """DFS实现拓扑排序"""
    visited = set()
    rec_stack = set()  # 检测环
    result = []
    
    def dfs(u):
        visited.add(u)
        rec_stack.add(u)
        
        for v in graph[u]:
            if v not in visited:
                if not dfs(v):
                    return False
            elif v in rec_stack:
                return False  # 存在环
        
        rec_stack.remove(u)
        result.append(u)
        return True
    
    for u in graph:
        if u not in visited:
            if not dfs(u):
                return []  # 存在环
    
    return result[::-1]  # 反转
```

## 复杂度分析

| 算法 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| Kahn | $O(V + E)$ | $O(V)$ |
| DFS | $O(V + E)$ | $O(V)$ |

## 应用场景

### 1. 课程选修计划

```python
def can_finish_courses(num_courses, prerequisites):
    """
    prerequisites: [(课程, 先修课), ...]
    """
    # 构建图
    graph = {i: [] for i in range(num_courses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)
    
    # 拓扑排序
    order = topological_sort_kahn(graph)
    return len(order) == num_courses
```

### 2. 任务调度

确定任务执行顺序，满足依赖关系。

### 3. 编译顺序

Make文件、编译器确定源文件编译顺序。

### 4. 数据流分析

编译器优化中的数据依赖分析。

## 面试要点

### Q1: 检测有向图中的环

```python
def has_cycle(graph):
    """使用拓扑排序检测环"""
    return len(topological_sort_kahn(graph)) != len(graph)
```

### Q2: 所有拓扑排序

```python
def all_topological_sorts(graph):
    """生成所有拓扑排序"""
    n = len(graph)
    in_degree = {v: 0 for v in graph}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1
    
    result = []
    
    def backtrack(path, in_degree):
        if len(path) == n:
            result.append(path[:])
            return
        
        for v in list(graph.keys()):
            if in_degree[v] == 0 and v not in path:
                # 选择v
                path.append(v)
                for neighbor in graph[v]:
                    in_degree[neighbor] -= 1
                
                backtrack(path, in_degree)
                
                # 回溯
                path.pop()
                for neighbor in graph[v]:
                    in_degree[neighbor] += 1
    
    backtrack([], in_degree)
    return result
```

## 相关概念

### 数据结构
- [图](../data-structures/graph.md) - 拓扑排序的数据基础
- [树](../data-structures/tree.md) - 特殊的有向无环图
- [队列](../data-structures/queue.md) - Kahn算法的核心数据结构

### 算法
- [图遍历](../algorithms/graph-traversal.md) - DFS/BFS基础
- [最短路径](../algorithms/shortest-path.md) - 同为图算法
- [动态规划](../algorithms/dynamic-programming.md) - 任务调度优化

### 复杂度分析
- [时间复杂度分析](../../references/time-complexity.md) - $O(V+E)$分析
- [空间复杂度](../../references/space-complexity.md) - 入度数组与访问标记

### 系统实现
- [进程](../systems/process.md) - 编译依赖分析
- [调度](../systems/scheduling.md) - 任务执行顺序
- [死锁](../systems/deadlock.md) - 循环等待检测

- [图遍历](../algorithms/graph-traversal.md) - DFS是拓扑排序的基础
- [BFS](../algorithms/graph-traversal.md) - Kahn算法使用BFS
- [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph) - 有向无环图

## 参考资料

1. 《算法导论》第22章 - 拓扑排序
2. Topological sorting - Wikipedia
