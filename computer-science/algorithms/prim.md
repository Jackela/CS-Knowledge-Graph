# Prim算法 (Prim's Algorithm)

## 简介

**Prim算法**是一种用于求解最小生成树（Minimum Spanning Tree, MST）的贪心算法。该算法从一个顶点开始，逐步扩展生成树，每次选择与当前树相连的最小权重边，直到包含所有顶点。

## 算法思想

从一个顶点开始，每次选择与当前树相连的最小权重边，将新顶点加入树中。

## 复杂度分析

- **时间**：$O(E \log V)$（使用二叉堆）
- **空间**：$O(V)$

## 应用场景

- 网络设计：最小成本构建通信网络
- 电路布线：最小化线路总长度
- 聚类分析：单链接聚类

## 相关概念

- [最小生成树](./minimum-spanning-tree.md) - Prim算法的完整实现与详细说明
- [Kruskal算法](./minimum-spanning-tree.md) - 另一种MST算法
- [贪心算法](./greedy.md) - Prim使用的策略
- [堆](../data-structures/heap.md) - 优先队列实现
- [图](../data-structures/graph.md) - Prim算法的基础数据结构
