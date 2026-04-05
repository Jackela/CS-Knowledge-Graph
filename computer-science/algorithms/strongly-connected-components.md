# 强连通分量 (Strongly Connected Components)

## 简介
强连通分量（Strongly Connected Components, SCC）是有向图中的极大子图，其中任意两个顶点互相可达。SCC分解可以将有向图转化为有向无环图（DAG），简化许多图算法问题。

## 核心概念
- **强连通**：顶点u到v有路径，且v到u也有路径
- **极大子图**：无法通过添加更多顶点保持强连通性质
- **缩点**：将每个SCC收缩为单个节点，得到DAG
- **转置图**：将所有边反向得到的图G^T

## 实现方式

### Kosaraju算法
```python
def kosaraju_scc(graph, n):
    """
    Kosaraju算法求强连通分量
    步骤1: 在G上DFS，记录完成顺序
    步骤2: 在G^T上按逆序DFS，每棵树是一个SCC
    时间复杂度: O(V + E)
    """
    def dfs1(u):
        visited[u] = True
        for v in graph[u]:
            if not visited[v]:
                dfs1(v)
        order.append(u)  # 后序遍历记录完成时间
    
    def dfs2(u, component):
        visited[u] = True
        component.append(u)
        for v in rev_graph[u]:
            if not visited[v]:
                dfs2(v, component)
    
    # 第一步：在G上DFS，获取完成顺序
    visited = [False] * n
    order = []
    for i in range(n):
        if not visited[i]:
            dfs1(i)
    
    # 构建转置图
    rev_graph = [[] for _ in range(n)]
    for u in range(n):
        for v in graph[u]:
            rev_graph[v].append(u)
    
    # 第二步：在G^T上按逆序DFS
    visited = [False] * n
    sccs = []
    for u in reversed(order):
        if not visited[u]:
            component = []
            dfs2(u, component)
            sccs.append(component)
    
    return sccs
```

### Tarjan算法
```python
def tarjan_scc(graph, n):
    """
    Tarjan算法求强连通分量（单遍DFS）
    使用dfn（访问次序）和low（最低可到达点）
    时间复杂度: O(V + E)，空间更优
    """
    index = 0
    stack = []
    on_stack = [False] * n
    indices = [-1] * n      # dfn: DFS访问次序
    lowlink = [0] * n       # low: 能到达的最小dfn
    sccs = []
    
    def strongconnect(v):
        nonlocal index
        indices[v] = lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack[v] = True
        
        # 访问邻接点
        for w in graph[v]:
            if indices[w] == -1:  # 未访问
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack[w]:     # w在当前DFS栈中，形成回边
                lowlink[v] = min(lowlink[v], indices[w])
        
        # v是SCC的根节点
        if lowlink[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)
    
    for v in range(n):
        if indices[v] == -1:
            strongconnect(v)
    
    return sccs
```

## 应用场景
- **社交网络分析**：识别紧密联系的社区群体
- **编译器优化**：控制流图的循环检测与优化
- **网页排名**：2SCC算法用于Web图的连通性分析
- **游戏开发**：状态机的等价状态合并

## 面试要点
1. **Q**: Kosaraju与Tarjan算法的主要区别？
   **A**: Kosaraju需要两遍DFS和构建转置图，实现简单但空间复杂度较高；Tarjan只需一遍DFS，使用显式栈，空间更优但实现稍复杂。

2. **Q**: 为什么Tarjan算法中low[v] == dfn[v]时表示找到SCC？
   **A**: low[v]表示v能到达的最小dfn，若low[v]等于dfn[v]，说明v无法到达任何更早的节点，v就是该SCC的根节点，栈中v之上的节点都属于同一SCC。

3. **Q**: 如何判断有向图是否强连通？
   **A**: 从任意节点出发DFS能否访问所有节点，且在转置图上从同一节点出发DFS能否访问所有节点。或直接使用SCC算法判断分量数是否为1。

4. **Q**: SCC缩点后的图有什么性质？
   **A**: 缩点后的图是DAG（有向无环图）。原图中不同SCC之间的边在缩点图中保持，且不存在环路，可进行拓扑排序。

## 相关概念

### 数据结构
- [图](../data-structures/graph.md) - SCC的基础数据结构
- [栈](../data-structures/stack.md) - Tarjan算法的核心辅助结构

### 算法
- [深度优先搜索](./dfs.md) - SCC算法的核心遍历方式
- [拓扑排序](./topological-sort.md) - SCC缩点后DAG的处理方法

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - O(V+E)线性时间分析

### 系统实现
- [编译器](../systems/compilers.md) - 控制流分析与优化
