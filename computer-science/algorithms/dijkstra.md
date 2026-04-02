# Dijkstra算法 (Dijkstra's Algorithm)

## 简介

**Dijkstra算法**是由荷兰计算机科学家艾兹赫尔·戴克斯特拉（Edsger Dijkstra）于1956年提出的，用于在带权图中求解单源最短路径问题。该算法要求图中所有边的权重必须为非负数。

## 算法思想

贪心策略：每次选择距离源点最近的未确定顶点，松弛其邻接边。

## 复杂度分析

- **时间**：$O((V + E) \log V)$（使用二叉堆）
- **空间**：$O(V)$

## 应用场景

- 地图导航与路径规划
- 网络路由协议（OSPF）
- 物流运输优化

## 相关概念

- [最短路径](./shortest-path.md) - Dijkstra算法的完整实现与详细说明
- [图遍历](./graph-traversal.md) - 图的遍历算法
- [贪心算法](./greedy.md) - Dijkstra使用的策略
- [堆](../data-structures/heap.md) - 优先队列实现
- [图](../data-structures/graph.md) - Dijkstra算法的基础数据结构
