# 网络流 (Network Flow)

## 简介
网络流研究在容量限制的网络中从源点到汇点的最大流量问题。该问题有广泛的实际应用，包括交通网络、通信网络、资源分配等场景。

## 核心概念
- **流网络**：有向图G=(V,E)，每条边有容量c(u,v)≥0
- **可行流**：满足容量约束和流量守恒的函数f(u,v)
- **残量网络**：剩余可用容量的网络G_f
- **增广路径**：残量网络中从源到汇的路径
- **最大流最小割定理**：最大流等于最小割容量

## 实现方式

### Ford-Fulkerson方法（ Edmonds-Karp实现）
```python
from collections import deque

def edmonds_karp(capacity, source, sink, n):
    """
    Edmonds-Karp算法：使用BFS找最短增广路径
    时间复杂度: O(V * E²)
    """
    flow = [[0] * n for _ in range(n)]
    max_flow = 0
    
    while True:
        # BFS找增广路径
        parent = [-1] * n
        parent[source] = source
        queue = deque([source])
        
        while queue and parent[sink] == -1:
            u = queue.popleft()
            for v in range(n):
                if parent[v] == -1 and capacity[u][v] - flow[u][v] > 0:
                    parent[v] = u
                    queue.append(v)
        
        # 无增广路径，结束
        if parent[sink] == -1:
            break
        
        # 计算路径上的最小残量
        path_flow = float('inf')
        s = sink
        while s != source:
            path_flow = min(path_flow, capacity[parent[s]][s] - flow[parent[s]][s])
            s = parent[s]
        
        # 更新流量
        v = sink
        while v != source:
            u = parent[v]
            flow[u][v] += path_flow
            flow[v][u] -= path_flow  # 反向边
            v = u
        
        max_flow += path_flow
    
    return max_flow
```

### Dinic算法
```python
def dinic(capacity, source, sink, n):
    """
    Dinic算法：分层图 + 多路增广
    时间复杂度: O(V² * E)，对于单位容量图O(E * √V)
    """
    def bfs():
        """构建分层图"""
        level = [-1] * n
        level[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in range(n):
                if level[v] < 0 and capacity[u][v] - flow[u][v] > 0:
                    level[v] = level[u] + 1
                    queue.append(v)
        return level
    
    def dfs(u, f):
        """在分层图上DFS增广"""
        if u == sink:
            return f
        for i in range(ptr[u], n):
            ptr[u] = i
            v = i
            if level[v] == level[u] + 1 and capacity[u][v] - flow[u][v] > 0:
                pushed = dfs(v, min(f, capacity[u][v] - flow[u][v]))
                if pushed > 0:
                    flow[u][v] += pushed
                    flow[v][u] -= pushed
                    return pushed
        return 0
    
    flow = [[0] * n for _ in range(n)]
    max_flow = 0
    
    while True:
        level = bfs()
        if level[sink] < 0:
            break
        ptr = [0] * n  # 当前弧优化
        while True:
            pushed = dfs(source, float('inf'))
            if pushed == 0:
                break
            max_flow += pushed
    
    return max_flow
```

## 应用场景
- **交通调度**：道路网络的最大通行能力规划
- **二分图匹配**：将匹配问题转化为网络流问题
- **项目选择**：带依赖关系的收益最大化
- **图像分割**：基于最小割的图像前景背景分离

## 面试要点
1. **Q**: 为什么需要反向边（残量网络）？
   **A**: 反向边允许算法"撤销"之前的流量分配。当发现更优路径时，可以通过反向边调整流量，保证最终得到最优解。

2. **Q**: Edmonds-Karp与Dinic算法的时间复杂度差异原因？
   **A**: Edmonds-Karp每次只找一条最短增广路径，可能经过O(VE)次迭代；Dinic使用分层图一次性阻塞所有最短路径，迭代次数降至O(V)，配合当前弧优化效率更高。

3. **Q**: 最大流最小割定理的直观理解？
   **A**: 任何s-t割都将源汇分开，流必须经过割边，故最大流≤最小割容量；而最大流对应的残量网络中，源点可达集形成割，此时流等于割容量。

4. **Q**: 如何处理多源多汇的网络流问题？
   **A**: 添加超级源点连接所有源点（容量无穷大），添加超级汇点被所有汇点连接（容量无穷大），转化为单源单汇问题。

## 相关概念

### 数据结构
- [图](../data-structures/graph.md) - 流网络的底层表示
- [队列](../data-structures/queue.md) - BFS实现需要

### 算法
- [最短路径](./dijkstra.md) - 最小费用最大流的基础
- [二分图匹配](./bipartite-matching.md) - 可转化为最大流问题

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 不同实现的时间复杂度对比

### 系统实现
- [负载均衡](../systems/load-balancing.md) - 网络流在资源分配中的应用
