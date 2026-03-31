# 图遍历 (Graph Traversal)

## 简介

**图遍历（Graph Traversal）**是指从图中某一顶点出发，系统地访问图中所有顶点且每个顶点只访问一次的过程。图遍历是图算法的基础，主要分为**深度优先搜索（DFS）**和**广度优先搜索（BFS）**两种策略。

```
图结构:

    0 ──── 1
    │      │
    │      │
    2 ──── 3

DFS遍历(从0开始): 0 → 1 → 3 → 2
BFS遍历(从0开始): 0 → 1 → 2 → 3
```

## 原理 (Principles)

### DFS vs BFS 对比

| 特性 | DFS | BFS |
|------|-----|-----|
| 数据结构 | 栈（递归/显式） | 队列 |
| 搜索策略 | 深入到底，回溯 | 层层扩展 |
| 空间复杂度 | $O(V)$ | $O(V)$ |
| 适用场景 | 路径存在、连通性 | 最短路径、层次遍历 |
| 完整代码 | 简洁（递归） | 稍复杂 |

## 深度优先搜索 (DFS)

### 递归实现

```python
def dfs_recursive(graph, start, visited=None):
    """递归DFS"""
    if visited is None:
        visited = set()
    
    visited.add(start)
    print(start, end=' ')
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    
    return visited
```

### 迭代实现

```python
def dfs_iterative(graph, start):
    """迭代DFS（使用栈）"""
    visited = set()
    stack = [start]
    
    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            print(vertex, end=' ')
            # 将未访问的邻居压栈
            for neighbor in reversed(graph[vertex]):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return visited
```

### DFS追踪示例

```
图:
    0 ──── 1
    │      │
    │      │
    2 ──── 3

DFS(0)执行过程:

栈: [0]          访问: {}
栈: [1, 2]       访问: {0}      弹出0，压入1,2
栈: [1]          访问: {0, 2}   弹出2，邻居0已访问
栈: [3]          访问: {0, 2, 1} 弹出1，压入3
栈: []           访问: {0, 2, 1, 3} 弹出3，邻居都已访问

结果: 0, 2, 1, 3
```

## 广度优先搜索 (BFS)

### 标准实现

```python
from collections import deque

def bfs(graph, start):
    """BFS遍历"""
    visited = set([start])
    queue = deque([start])
    
    while queue:
        vertex = queue.popleft()
        print(vertex, end=' ')
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return visited
```

### BFS追踪示例

```
BFS(0)执行过程:

队列: [0]          访问: {0}
队列: [1, 2]       访问: {0, 1, 2}    弹出0，加入邻居1,2
队列: [2, 3]       访问: {0, 1, 2, 3} 弹出1，加入邻居3
队列: [3]          访问: ...          弹出2，邻居都已访问
队列: []                              弹出3

结果: 0, 1, 2, 3
```

### 分层BFS

```python
def bfs_level(graph, start):
    """按层输出BFS"""
    visited = set([start])
    queue = deque([start])
    level = 0
    
    while queue:
        level_size = len(queue)
        print(f"Level {level}:", end=' ')
        
        for _ in range(level_size):
            vertex = queue.popleft()
            print(vertex, end=' ')
            
            for neighbor in graph[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        print()
        level += 1
```

## 复杂度分析

| 算法 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| DFS | $O(V + E)$ | $O(V)$ |
| BFS | $O(V + E)$ | $O(V)$ |

其中 $V$ 是顶点数，$E$ 是边数。

## 应用场景

### 1. 连通分量

```python
def count_components(graph):
    """统计连通分量数"""
    visited = set()
    count = 0
    
    for vertex in graph:
        if vertex not in visited:
            dfs_recursive(graph, vertex, visited)
            count += 1
    
    return count
```

### 2. 最短路径（无权图）

```python
def shortest_path(graph, start, end):
    """BFS求无权图最短路径"""
    from collections import deque
    
    queue = deque([(start, [start])])
    visited = set([start])
    
    while queue:
        vertex, path = queue.popleft()
        
        if vertex == end:
            return path
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None  # 无路径
```

### 3. 环检测

```python
def has_cycle_dfs(graph):
    """检测无向图是否有环"""
    visited = set()
    
    def dfs(vertex, parent):
        visited.add(vertex)
        
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                if dfs(neighbor, vertex):
                    return True
            elif neighbor != parent:
                return True  # 发现回边
        
        return False
    
    for vertex in graph:
        if vertex not in visited:
            if dfs(vertex, None):
                return True
    
    return False
```

### 4. 拓扑排序（DFS实现）

```python
def topological_sort_dfs(graph):
    """DFS实现拓扑排序"""
    visited = set()
    stack = []
    
    def dfs(vertex):
        visited.add(vertex)
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                dfs(neighbor)
        stack.append(vertex)  # 后序加入
    
    for vertex in graph:
        if vertex not in visited:
            dfs(vertex)
    
    return stack[::-1]  # 反转得到拓扑序
```

## 面试要点

### Q1: DFS vs BFS如何选择？

- **找最短路径**：BFS（无权图）
- **连通性检测**：两者皆可
- **空间受限**：DFS通常占用更少空间
- **拓扑排序**：DFS
- **层次相关**：BFS

### Q2: 双向BFS

从起点和终点同时BFS，在中间相遇。

```python
def bidirectional_bfs(graph, start, end):
    if start == end:
        return [start]
    
    visited_start = {start: None}
    visited_end = {end: None}
    queue_start = deque([start])
    queue_end = deque([end])
    
    while queue_start and queue_end:
        # 扩展较小的一边
        if len(queue_start) <= len(queue_end):
            meet = bfs_step(graph, queue_start, visited_start, visited_end)
        else:
            meet = bfs_step(graph, queue_end, visited_end, visited_start)
        
        if meet:
            return reconstruct_path(visited_start, visited_end, meet)
    
    return None
```

## 相关概念 (Related Concepts)

### 数据结构
- [图](../data-structures/graph.md)：遍历的基础数据结构
- [树](../data-structures/tree.md)：图遍历适用于树的遍历
- [队列](../data-structures/queue.md)：BFS 的底层数据结构
- [栈](../data-structures/stack.md)：DFS 的底层数据结构

### 算法
- [最短路径](./shortest-path.md)：Dijkstra 等算法基于图遍历
- [拓扑排序](./topological-sort.md)：有向图的线性排序
- [最小生成树](./minimum-spanning-tree.md)：图遍历的应用

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：遍历算法的时间效率
- [空间复杂度](../../references/space-complexity.md)：遍历的空间开销评估

### 系统实现
- [网络路由](../systems/network.md)：图遍历在网络中的应用
- [社交网络分析](../../references/social-network.md)：图遍历在关系分析中的应用

- [图](../data-structures/graph.md) - 基础数据结构
- [最短路径](../algorithms/shortest-path.md) - Dijkstra等算法
- [拓扑排序](../algorithms/topological-sort.md) - 有向图排序
- [树](../data-structures/tree.md) - 图遍历适用于树的遍历

## 参考资料

1. 《算法导论》第22章 - 基本的图算法
2. Graph traversal - Wikipedia
3. LeetCode 图论专题
