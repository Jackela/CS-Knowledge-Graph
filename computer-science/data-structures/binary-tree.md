# 二叉树 (Binary Tree)

## 简介

**二叉树（Binary Tree）**是每个节点最多有两个子节点的树形数据结构，分别称为**左子节点（Left Child）**和**右子节点（Right Child）**。二叉树是计算机科学中最基础、最重要的非线性数据结构之一，广泛应用于搜索、排序、表达式解析等领域。

```
              1            ← 根节点 (Root)
            /   \
          2       3         ← 内部节点 (Internal Nodes)
         / \     /
        4   5   6           ← 叶节点 (Leaf Nodes)
       /
      7                     ← 叶节点

术语:
- 节点 2 是节点 4 和 5 的父节点
- 节点 4 和 5 是节点 2 的子节点
- 节点 4 和 5 互为兄弟节点
- 边: 1-2, 1-3, 2-4, 2-5, 3-6, 4-7
```

## 树的基本术语

| 术语 | 英文 | 定义 |
|------|------|------|
| 节点 | Node | 树的基本单位，包含数据和指向子节点的引用 |
| 边 | Edge | 连接两个节点的线 |
| 根 | Root | 树的顶端节点，唯一没有父节点的节点 |
| 叶节点 | Leaf | 没有子节点的节点 |
| 内部节点 | Internal Node | 至少有一个子节点的节点 |
| 父节点 | Parent | 某节点的直接上层节点 |
| 子节点 | Child | 某节点的直接下层节点 |
| 兄弟节点 | Sibling | 具有相同父节点的节点 |
| 深度 | Depth | 从根到该节点的边数 |
| 高度 | Height | 从该节点到最远叶节点的边数 |
| 层级 | Level | 深度 + 1 |
| 度 | Degree | 节点的子节点数 |

```
              A (深度0, 层级1)
            /   \
          B       C (深度1, 层级2)
         / \     /
        D   E   F (深度2, 层级3)
       /
      G (深度3, 层级4)

树的高度 = 3 (从A到G的边数)
节点B的高度 = 2 (从B到G)
```

## 原理 (Principles)

### 二叉树的数学性质

**性质1**：第 $i$ 层最多有 $2^{i-1}$ 个节点（$i \geq 1$）

**性质2**：深度为 $k$ 的二叉树最多有 $2^k - 1$ 个节点

**性质3**：对于任意二叉树，如果叶节点数为 $n_0$，度为2的节点数为 $n_2$，则：
$$n_0 = n_2 + 1$$

**性质4**：具有 $n$ 个节点的完全二叉树深度为：
$$\lfloor \log_2 n \rfloor + 1$$

### 节点数的递推关系

设 $N(h)$ 为高度为 $h$ 的二叉树的最大节点数：
$$N(h) = N(h-1) + N(h-1) + 1 = 2^{h+1} - 1$$

## 遍历方式 (Traversals)

遍历是二叉树最重要的操作，按访问根节点的时机分为三种深度优先遍历和一种广度优先遍历。

### 1. 前序遍历（Pre-order）

**顺序**：根 → 左子树 → 右子树

```
        1
      /   \
     2     3
    / \   /
   4   5 6

前序: 1, 2, 4, 5, 3, 6
```

**递归实现**：
```python
def preorder(root):
    if root is None:
        return
    print(root.val)      # 访问根
    preorder(root.left)  # 遍历左
    preorder(root.right) # 遍历右
```

**迭代实现**：
```python
def preorder_iterative(root):
    if not root:
        return
    stack = [root]
    while stack:
        node = stack.pop()
        print(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
```

**应用场景**：
- 复制二叉树
- 前缀表达式（波兰表示法）
- 目录结构打印

### 2. 中序遍历（In-order）

**顺序**：左子树 → 根 → 右子树

```
        1
      /   \
     2     3
    / \   /
   4   5 6

中序: 4, 2, 5, 1, 6, 3
```

对于二叉搜索树，中序遍历产生有序序列！

**递归实现**：
```python
def inorder(root):
    if root is None:
        return
    inorder(root.left)
    print(root.val)
    inorder(root.right)
```

**迭代实现**：
```python
def inorder_iterative(root):
    stack = []
    current = root
    
    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        print(current.val)
        current = current.right
```

**应用场景**：
- 二叉搜索树的有序输出
- 中缀表达式

### 3. 后序遍历（Post-order）

**顺序**：左子树 → 右子树 → 根

```
        1
      /   \
     2     3
    / \   /
   4   5 6

后序: 4, 5, 2, 6, 3, 1
```

**递归实现**：
```python
def postorder(root):
    if root is None:
        return
    postorder(root.left)
    postorder(root.right)
    print(root.val)
```

**迭代实现**：
```python
def postorder_iterative(root):
    if not root:
        return
    stack = [(root, False)]
    while stack:
        node, visited = stack.pop()
        if visited:
            print(node.val)
        else:
            stack.append((node, True))
            if node.right:
                stack.append((node.right, False))
            if node.left:
                stack.append((node.left, False))
```

**应用场景**：
- 删除二叉树（先删子节点）
- 后缀表达式（逆波兰表示法）
- 计算目录大小

### 4. 层序遍历（Level-order / BFS）

按层次从上到下、从左到右遍历。

```
        1
      /   \
     2     3
    / \   /
   4   5 6

层序: 1, 2, 3, 4, 5, 6
```

**实现（使用队列）**：
```python
from collections import deque

def levelorder(root):
    if not root:
        return
    
    queue = deque([root])
    while queue:
        level_size = len(queue)
        for _ in range(level_size):
            node = queue.popleft()
            print(node.val, end=' ')
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        print()  # 换行，区分层次
```

**应用场景**：
- 查找最短路径
- 按层次处理问题
- 序列化/反序列化二叉树

### 遍历对比表

| 遍历方式 | 顺序 | 典型应用 |
|---------|------|---------|
| 前序 | 根-左-右 | 复制树、前缀表达式 |
| 中序 | 左-根-右 | BST有序遍历、中缀表达式 |
| 后序 | 左-右-根 | 删除树、后缀表达式 |
| 层序 | 逐层 | BFS、最短路径 |

## 特殊二叉树

### 1. 满二叉树（Full Binary Tree）

每个节点要么是叶节点，要么有两个子节点。

```
        1
      /   \
     2     3
    / \   / \
   4   5 6   7
```

**性质**：节点数 $n = 2^{h+1} - 1$（高度为 $h$）

### 2. 完全二叉树（Complete Binary Tree）

除最后一层外完全填满，最后一层节点集中在左侧。

```
        1
      /   \
     2     3
    / \   /
   4   5 6

✓ 完全二叉树        ✗ 非完全二叉树
        1                 1
      /   \             /   \
     2     3           2     3
    /       \               /
   4         5             4
```

**性质**：可用数组高效存储。

### 3. 完美二叉树（Perfect Binary Tree）

所有内部节点都有两个子节点，所有叶节点在同一层。

```
        1
      /   \
     2     3
    / \   / \
   4   5 6   7
```

### 4. 平衡二叉树（Balanced Binary Tree）

任意节点的左右子树高度差不超过1。

```
        1              ✗ 不平衡
      /   \
     2     3
    /
   4
  /
 5
```

详见 [AVL树](../data-structures/avl-tree.md)

## 实现 (Implementation)

### 链表实现（标准）

```python
class TreeNode:
    """二叉树节点"""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# 创建二叉树
#        1
#      /   \
#     2     3
#    /
#   4
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
```

### 数组实现（完全二叉树）

对于完全二叉树，可用数组存储，父子关系通过索引计算：

```
        1(0)
      /      \
    2(1)     3(2)
    /  \     /
  4(3) 5(4) 6(5)

数组: [1, 2, 3, 4, 5, 6]

父节点 i 的:
- 左子节点: 2i + 1
- 右子节点: 2i + 2

子节点 i 的父节点: (i-1) // 2
```

```python
class ArrayBinaryTree:
    def __init__(self):
        self.tree = []
    
    def parent(self, i):
        if i == 0:
            return None
        return (i - 1) // 2
    
    def left_child(self, i):
        left = 2 * i + 1
        return left if left < len(self.tree) else None
    
    def right_child(self, i):
        right = 2 * i + 2
        return right if right < len(self.tree) else None
```

## 复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| 遍历 | $O(n)$ | $O(h)$ 递归栈 |
| 查找 | $O(n)$ | $O(h)$ |
| 插入 | $O(n)$ | $O(h)$ |
| 删除 | $O(n)$ | $O(h)$ |
| 求高度 | $O(n)$ | $O(h)$ |

其中 $h$ 为树高，最坏 $O(n)$（退化为链表），平衡时 $O(\log n)$

## 应用场景

### 1. 表达式树

```
        *
      /   \
     +     -
    / \   / \
   3   4 5   2

中序: 3 + 4 * 5 - 2 (需要括号)
后序: 3 4 + 5 2 - * (逆波兰)
```

### 2. 霍夫曼树（Huffman Tree）

用于数据压缩的最优前缀编码树。

### 3. 决策树

机器学习中用于分类的树形模型。

### 4. 文件系统

目录结构天然是树形结构。

## 面试要点

### Q1: 求二叉树的最大深度

```python
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

**时间复杂度**：$O(n)$
**空间复杂度**：$O(h)$

### Q2: 判断二叉树是否对称

```python
def is_symmetric(root):
    def mirror(left, right):
        if not left and not right:
            return True
        if not left or not right:
            return False
        return (left.val == right.val and
                mirror(left.left, right.right) and
                mirror(left.right, right.left))
    
    return not root or mirror(root.left, root.right)
```

### Q3: 路径总和

```python
def has_path_sum(root, target):
    if not root:
        return False
    if not root.left and not root.right:
        return root.val == target
    return (has_path_sum(root.left, target - root.val) or
            has_path_sum(root.right, target - root.val))
```

### Q4: 从前序和中序重建二叉树

```python
def build_tree(preorder, inorder):
    if not preorder:
        return None
    
    root_val = preorder[0]
    root = TreeNode(root_val)
    
    root_idx = inorder.index(root_val)
    
    root.left = build_tree(preorder[1:1+root_idx], 
                           inorder[:root_idx])
    root.right = build_tree(preorder[1+root_idx:], 
                            inorder[root_idx+1:])
    
    return root
```

### Q5: 序列化与反序列化

```python
class Codec:
    def serialize(self, root):
        """前序遍历序列化"""
        if not root:
            return '#'
        return f'{root.val},{self.serialize(root.left)},{self.serialize(root.right)}'
    
    def deserialize(self, data):
        """前序遍历反序列化"""
        def helper(values):
            val = next(values)
            if val == '#':
                return None
            node = TreeNode(int(val))
            node.left = helper(values)
            node.right = helper(values)
            return node
        
        return helper(iter(data.split(',')))
```

## 相关概念

- [二叉搜索树](../data-structures/bst.md) - 有序二叉树
- [AVL树](../data-structures/avl-tree.md) - 平衡二叉搜索树
- [红黑树](../data-structures/red-black-tree.md) - 自平衡二叉搜索树
- [堆](../data-structures/heap.md) - 完全二叉树实现
- [B树](../data-structures/b-tree.md) - 多路搜索树
- [Trie](../data-structures/trie.md) - 前缀树
- [图遍历](../algorithms/graph-traversal.md) - 树的遍历是图遍历的特例

## 参考资料

1. 《算法导论》第12章 - 二叉搜索树
2. 《数据结构（C语言版）》严蔚敏 - 第六章树和二叉树
3. Binary tree - Wikipedia
4. LeetCode 二叉树专题
