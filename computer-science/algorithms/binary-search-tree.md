# 二叉搜索树 (Binary Search Tree)

## 简介

**二叉搜索树（Binary Search Tree, BST）**是一种特殊的二叉树，它满足以下性质：对于树中的每个节点，其左子树中的所有节点的值都小于该节点的值，其右子树中的所有节点的值都大于该节点的值。这个性质使得BST支持高效的查找、插入和删除操作。

## 性质

- 左子树所有节点值 < 根节点值
- 右子树所有节点值 > 根节点值
- 左右子树也是二叉搜索树
- 中序遍历产生有序序列

## 复杂度分析

| 操作 | 平均情况 | 最坏情况 |
|------|---------|---------|
| 查找 | O(log n) | O(n) |
| 插入 | O(log n) | O(n) |
| 删除 | O(log n) | O(n) |

## 相关概念

- [二叉树](../data-structures/binary-tree.md) - BST的基础结构
- [AVL树](../data-structures/avl-tree.md) - 自平衡二叉搜索树
- [红黑树](../data-structures/red-black-tree.md) - 近似平衡的二叉搜索树
- [二分查找](./binary-search.md) - 相同的查找思想，用于数组
