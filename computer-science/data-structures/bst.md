# 二叉搜索树 (Binary Search Tree - BST)

## 简介

**二叉搜索树（Binary Search Tree, BST）**是一种特殊的二叉树，满足以下性质：

> 对于树中的任意节点，其左子树中的所有节点值都小于该节点值，右子树中的所有节点值都大于该节点值。

```
        8
      /   \
     3     10
    / \      \
   1   6      14
      / \    /
     4   7  13

BST 性质验证:
- 节点 8: 左子树(3,1,6,4,7) < 8 < 右子树(10,14,13) ✓
- 节点 3: 左子树(1) < 3 < 右子树(6,4,7) ✓
- 节点 6: 左子树(4) < 6 < 右子树(7) ✓
```

BST 结合了链表的快速插入删除和数组的快速查找优点，是实现有序映射（Map）和集合（Set）的基础数据结构。

## 原理 (Principles)

### BST 核心性质

1. **有序性**：中序遍历 BST 得到递增有序序列
2. **唯一性**：每个节点的键值唯一（一般情况）
3. **递归性**：BST 的任意子树也是 BST

### 数学性质

- 对于 $n$ 个节点的 BST，高度最坏为 $O(n)$（退化为链表）
- 平均情况下高度为 $O(\log n)$
- 最优 BST（完全平衡）高度为 $\lfloor \log_2 n \rfloor$

## 核心操作

### 1. 查找（Search）

```
查找 6:

        8
      /   \
     3     10   6 < 8, 去左子树
    / \      \
   1   6      14  6 > 3, 去右子树
      / \    /
     4   7  13     6 = 6, 找到!
```

```python
def search(root, key):
    """递归查找"""
    if not root or root.val == key:
        return root
    if key < root.val:
        return search(root.left, key)
    return search(root.right, key)

def search_iterative(root, key):
    """迭代查找"""
    while root and root.val != key:
        if key < root.val:
            root = root.left
        else:
            root = root.right
    return root
```

**时间复杂度**：$O(h)$，其中 $h$ 为树高

### 2. 插入（Insert）

```
插入 5:

        8
      /   \
     3     10
    / \      \
   1   6      14
      / \    /
     4   7  13
    /
   5  ← 新节点

路径: 8 → 3 → 6 → 4 → 插入到4的右子树
```

```python
def insert(root, key):
    """递归插入"""
    if not root:
        return TreeNode(key)
    
    if key < root.val:
        root.left = insert(root.left, key)
    elif key > root.val:
        root.right = insert(root.right, key)
    # key == root.val: 已存在，不做操作
    
    return root
```

### 3. 删除（Delete）

删除是 BST 最复杂的操作，分三种情况：

#### 情况1：删除叶节点

直接删除。

```
删除 1:

    3          3
   / \   →    / \
  1   6      ∅   6
```

#### 情况2：删除只有一个子节点的节点

用子节点替代被删除节点。

```
删除 10:

    8              8
   / \            / \
  3  10    →     3  14
    / \
   ∅  14
```

#### 情况3：删除有两个子节点的节点

用**后继节点**（右子树的最小值）或**前驱节点**（左子树的最大值）替代。

```
删除 3 (有两个子节点):

    8                 8
   / \               / \
  3   10    →       4   10    (用后继4替换)
 / \    \          / \    \
1   6    14       1   6    14
   / \              / \
  4   7            5   7
 /
5
```

```python
def delete(root, key):
    """删除节点"""
    if not root:
        return None
    
    # 查找要删除的节点
    if key < root.val:
        root.left = delete(root.left, key)
    elif key > root.val:
        root.right = delete(root.right, key)
    else:
        # 找到要删除的节点
        # 情况1: 叶节点或只有一个子节点
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        
        # 情况2: 有两个子节点，找后继
        successor = find_min(root.right)
        root.val = successor.val
        root.right = delete(root.right, successor.val)
    
    return root

def find_min(root):
    """找最小值（最左节点）"""
    while root.left:
        root = root.left
    return root

def find_max(root):
    """找最大值（最右节点）"""
    while root.right:
        root = root.right
    return root
```

### 4. 查找最值

```python
def find_min(root):
    """BST中最小值在最左"""
    while root and root.left:
        root = root.left
    return root.val if root else None

def find_max(root):
    """BST中最大值在最右"""
    while root and root.right:
        root = root.right
    return root.val if root else None
```

### 5. 查找前驱和后继

```python
def find_successor(root, key):
    """查找大于key的最小值"""
    successor = None
    current = root
    
    while current:
        if key < current.val:
            successor = current
            current = current.left
        else:
            current = current.right
    
    return successor.val if successor else None

def find_predecessor(root, key):
    """查找小于key的最大值"""
    predecessor = None
    current = root
    
    while current:
        if key > current.val:
            predecessor = current
            current = current.right
        else:
            current = current.left
    
    return predecessor.val if predecessor else None
```

## 完整实现

```python
class TreeNode:
    def __init__(self, val=0):
        self.val = val
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        self.root = self._insert(self.root, val)
    
    def _insert(self, node, val):
        if not node:
            return TreeNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        return node
    
    def search(self, val):
        return self._search(self.root, val)
    
    def _search(self, node, val):
        if not node or node.val == val:
            return node
        if val < node.val:
            return self._search(node.left, val)
        return self._search(node.right, val)
    
    def delete(self, val):
        self.root = self._delete(self.root, val)
    
    def _delete(self, node, val):
        if not node:
            return None
        
        if val < node.val:
            node.left = self._delete(node.left, val)
        elif val > node.val:
            node.right = self._delete(node.right, val)
        else:
            if not node.left:
                return node.right
            if not node.right:
                return node.left
            
            # 找后继
            min_node = self._find_min(node.right)
            node.val = min_node.val
            node.right = self._delete(node.right, min_node.val)
        
        return node
    
    def _find_min(self, node):
        while node.left:
            node = node.left
        return node
    
    def inorder(self):
        """中序遍历 - 返回有序序列"""
        result = []
        self._inorder(self.root, result)
        return result
    
    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)
```

## 复杂度分析

| 操作 | 最好情况 | 平均情况 | 最坏情况 |
|------|---------|---------|---------|
| 查找 | $O(\log n)$ | $O(\log n)$ | $O(n)$ |
| 插入 | $O(\log n)$ | $O(\log n)$ | $O(n)$ |
| 删除 | $O(\log n)$ | $O(\log n)$ | $O(n)$ |
| 最值 | $O(\log n)$ | $O(\log n)$ | $O(n)$ |
| 空间 | $O(n)$ | $O(n)$ | $O(n)$ |

### 最坏情况示例

```
按顺序插入: 1, 2, 3, 4, 5

1
 \
  2
   \
    3
     \
      4
       \
        5

BST 退化为链表！
```

**解决方案**：使用自平衡 BST，如 [AVL树](./avl-tree.md) 或 [红黑树](./red-black-tree.md)

## BST vs 其他结构

| 特性 | BST | 数组 | 链表 | 哈希表 |
|------|-----|------|------|--------|
| 查找 | $O(\log n)$~$O(n)$ | $O(\log n)$ 有序/$O(n)$ | $O(n)$ | $O(1)$ |
| 插入 | $O(\log n)$~$O(n)$ | $O(n)$ | $O(1)$ | $O(1)$ |
| 删除 | $O(\log n)$~$O(n)$ | $O(n)$ | $O(n)$ | $O(1)$ |
| 有序遍历 | $O(n)$ | $O(n)$ | $O(n \log n)$ | $O(n \log n)$ |
| 范围查询 | $O(\log n + k)$ | $O(\log n + k)$ | $O(n)$ | $O(n)$ |

## 应用场景

### 1. 数据库索引

早期数据库使用 BST 作为索引结构（现在多使用 B+树）。

### 2. 内存有序映射

C++ `std::map`（通常用红黑树实现）
Java `TreeMap`

### 3. 表达式解析

编译器使用 BST 存储和查找符号表。

### 4. 范围查询

```python
def range_query(root, low, high):
    """查找 [low, high] 范围内的所有值"""
    result = []
    
    def dfs(node):
        if not node:
            return
        if low <= node.val <= high:
            dfs(node.left)
            result.append(node.val)
            dfs(node.right)
        elif node.val < low:
            dfs(node.right)
        else:  # node.val > high
            dfs(node.left)
    
    dfs(root)
    return result
```

## 面试要点

### Q1: 验证 BST

```python
def is_valid_bst(root):
    """验证是否为合法BST"""
    def helper(node, min_val, max_val):
        if not node:
            return True
        if node.val <= min_val or node.val >= max_val:
            return False
        return (helper(node.left, min_val, node.val) and
                helper(node.right, node.val, max_val))
    
    return helper(root, float('-inf'), float('inf'))
```

### Q2: 第 K 小的元素

```python
def kth_smallest(root, k):
    """BST中第K小的元素"""
    count = 0
    result = None
    
    def inorder(node):
        nonlocal count, result
        if not node or result is not None:
            return
        inorder(node.left)
        count += 1
        if count == k:
            result = node.val
            return
        inorder(node.right)
    
    inorder(root)
    return result
```

**优化**：维护子树大小，可做到 $O(\log n)$

### Q3: 最近公共祖先（LCA）

```python
def lowest_common_ancestor(root, p, q):
    """BST中的LCA利用大小关系"""
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root
```

**时间复杂度**：$O(h)$

### Q4: 将有序数组转换为高度平衡的 BST

```python
def sorted_array_to_bst(nums):
    """有序数组转平衡BST"""
    if not nums:
        return None
    
    mid = len(nums) // 2
    root = TreeNode(nums[mid])
    root.left = sorted_array_to_bst(nums[:mid])
    root.right = sorted_array_to_bst(nums[mid+1:])
    
    return root
```

### Q5: BST 迭代器

```python
class BSTIterator:
    """中序遍历迭代器，平均O(1)时间"""
    def __init__(self, root):
        self.stack = []
        self._push_left(root)
    
    def _push_left(self, node):
        while node:
            self.stack.append(node)
            node = node.left
    
    def next(self):
        node = self.stack.pop()
        self._push_left(node.right)
        return node.val
    
    def has_next(self):
        return len(self.stack) > 0
```

## 相关概念

- [二叉树](./binary-tree.md) - BST 的基础结构
- [AVL树](./avl-tree.md) - 严格平衡的 BST
- [红黑树](./red-black-tree.md) - 宽松平衡的 BST
- [B树](./b-tree.md) - 多路搜索树，用于磁盘
- [堆](./heap.md) - 特殊的完全二叉树
- [二叉搜索](../algorithms/binary-search.md) - BST 的算法思想
- [二叉搜索](../algorithms/binary-search.md) - BST 的算法思想

## 参考资料

1. 《算法导论》第12章 - 二叉搜索树
2. 《数据结构与算法分析》Mark Allen Weiss
3. Binary search tree - Wikipedia
4. LeetCode BST 专题
