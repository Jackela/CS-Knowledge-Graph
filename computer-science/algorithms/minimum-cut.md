# 最小割 (Minimum Cut)

## 简介
最小割问题是寻找将图中源点和汇点分离的边集，使得这些边的容量之和最小。根据最大流最小割定理，最小割容量等于最大流值，两者可以互相求解。

## 核心概念
- **s-t割**：将顶点划分为包含源点s的集合S和包含汇点t的集合T
- **割容量**：从S指向T的所有边的容量之和
- **全局最小割**：不指定源汇，找容量最小的割
- **边收缩**：将两个顶点合并，用于Karger算法

## 实现方式

### Karger算法（全局最小割）
```python
import random

def karger_min_cut(graph, n):
    """
    Karger随机收缩算法求全局最小割
    每次随机选择一条边收缩，直到只剩两个顶点
    时间复杂度: O(n²)，重复运行可提高正确率
    """
    # 并查集实现
    parent = list(range(n))
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
    
    # 构建边列表
    edges = []
    for u in range(n):
        for v, w in graph[u]:
            if u < v:  # 避免重复边
                edges.append((u, v, w))
    
    vertices = n
    # 随机收缩直到只剩2个顶点
    while vertices > 2:
        # 随机选择一条边
        idx = random.randint(0, len(edges) - 1)
        u, v, w = edges[idx]
        
        if find(u) != find(v):
            union(u, v)
            vertices -= 1
        
        # 移除自环
        edges = [(a, b, c) for a, b, c in edges if find(a) != find(b)]
    
    # 剩余边即为割边
    min_cut_weight = sum(w for u, v, w in edges if find(u) != find(v))
    return min_cut_weight
```

### Stoer-Wagner算法（全局最小割）
```python
import heapq

def stoer_wagner(graph, n):
    """
    Stoer-Wagner算法：确定性算法求全局最小割
    基于最大邻接搜索（Maximum Adjacency Search）
    时间复杂度: O(n³) 或 O(nm log n)使用堆优化
    """
    def min_cut_phase(vertices, adj):
        """一个phase找出一个s-t最小割"""
        added = [False] * n
        weights = [0] * n
        prev = [-1] * n  # 记录添加顺序
        
        # 最大邻接搜索
        for i in range(len(vertices)):
            # 选择连接最紧密的顶点
            selected = -1
            for v in vertices:
                if not added[v] and (selected == -1 or weights[v] > weights[selected]):
                    selected = v
            
            if selected == -1:
                break
            
            added[selected] = True
            if i == len(vertices) - 1:
                # 最后添加的是t，倒数第二是s
                s, t = prev[selected], selected
                cut_weight = weights[t]
                
                # 合并s和t
                for v in vertices:
                    adj[s][v] += adj[t][v]
                    adj[v][s] += adj[v][t]
                vertices.remove(t)
                return cut_weight, vertices, adj
            
            prev[selected] = selected if i == 0 else [v for v in vertices if added[v] and v != selected][-1] if i > 0 else -1
            
            # 更新权重
            for v in vertices:
                if not added[v]:
                    weights[v] += adj[selected][v]
                    prev[v] = selected
        
        return float('inf'), vertices, adj
    
    # 构建邻接矩阵
    adj = [[0] * n for _ in range(n)]
    for u in range(n):
        for v, w in graph[u]:
            adj[u][v] += w
    
    vertices = list(range(n))
    min_cut = float('inf')
    
    while len(vertices) > 1:
        cut_weight, vertices, adj = min_cut_phase(vertices, adj)
        min_cut = min(min_cut, cut_weight)
    
    return min_cut
```

## 应用场景
- **图像分割**：基于最小割的图像前景背景分离
- **网络可靠性**：评估网络在边失效时的连通性
- **社区发现**：社交网络中的社区边界识别
- **VLSI设计**：芯片布线的最小切割优化

## 面试要点
1. **Q**: 最大流与最小割的关系是什么？
   **A**: 最大流最小割定理指出：在任何流网络中，从源点到汇点的最大流值等于分离源汇的最小割容量。最大流对应的残量网络中，从源点可达的顶点构成割的一侧。

2. **Q**: Karger算法为何需要重复运行多次？
   **A**: Karger是随机算法，单次成功概率为2/(n(n-1))。重复O(n² log n)次可将失败概率降至任意小。每次独立随机选择边进行收缩。

3. **Q**: Stoer-Wagner与Karger的主要区别？
   **A**: Stoer-Wagner是确定性算法，时间复杂度O(n³)或O(nm log n)，保证正确结果；Karger是随机算法，期望时间复杂度O(n²)但需要多次运行保证正确率。

4. **Q**: 如何在一个phase中保证找到的割是s-t最小割？
   **A**: Stoer-Wagner算法使用最大邻接搜索，按顶点与已选集合的连接强度顺序添加顶点。可以证明最后添加的两个顶点之间的割是该phase的s-t最小割。

## 相关概念

### 数据结构
- [图](../data-structures/graph.md) - 割问题的基础数据结构
- [并查集](../data-structures/disjoint-set.md) - Karger算法的边收缩实现

### 算法
- [网络流](./network-flow.md) - 最小割与最大流的对偶关系
- [最大流](./max-flow.md) - 通过最大流求解最小割

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 随机算法与确定性算法复杂度对比

### 系统实现
- [分布式系统](../systems/distributed-systems.md) - 网络分区与容错设计
