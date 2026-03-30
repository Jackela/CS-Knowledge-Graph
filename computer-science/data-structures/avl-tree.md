# AVL树 (Adelson-Velsky and Landis Tree)

## 简介

**AVL树**是一种**自平衡二叉搜索树**，由苏联数学家 Georgy Adelson-Velsky 和 Evgenii Landis 于1962年发明。它通过维护一个平衡条件，确保树的任意节点的左右子树高度差不超过1，从而保证查找、插入和删除操作的时间复杂度始终为 $O(\log n)$。

```
        30                           30
      /     \                      /     \
    20       40                   20       40
   /  \     /  \        vs       /        /  \
 10   25   35   50             10        35   50
                                      /
                                    33

    AVL树 (平衡)              普通BST (可能不平衡)
```

AVL树是**严格平衡**的，任何时刻都维持平衡性质，适合查找密集的场景。

## 原理 (Principles)

### 平衡因子（Balance Factor）

$$\text{Balance Factor} = \text{左子树高度} - \text{右子树高度}$$

AVL树的条件：**每个节点的平衡因子只能是 -1, 0, 或 1**

```
        30 (BF=0)
      /     \
    20 (BF=0) 40 (BF=-1)
   /  \        /
 10   25      35

平衡因子计算:
- 节点10, 25, 35, 空节点: 高度=0, BF=0
- 节点20: 左高=1, 右高=1, BF=0, 高度=2
- 节点40: 左高=1, 右高=0, BF=1, 高度=2
- 节点30: 左高=2, 右高=2, BF=0, 高度=3
```

### 旋转操作

当插入或删除破坏平衡时，通过**旋转**恢复平衡。旋转分为四种情况：

#### 1. 右旋（Right Rotation）- 解决 LL 失衡

```
失衡情况 (节点A的BF=2, 左子节点BF≥0):

      z (BF=2)                    y
     /                         /   \
    y (BF=1)        →         x     z
   /                               /
  x (新插入)                       T3
 /
T1

旋转后所有节点平衡因子恢复
```

```python
def right_rotate(z):
    y = z.left
    T3 = y.right
    
    # 执行旋转
    y.right = z
    z.left = T3
    
    # 更新高度
    z.height = 1 + max(get_height(z.left), get_height(z.right))
    y.height = 1 + max(get_height(y.left), get_height(y.right))
    
    return y  # 新的根节点
```

#### 2. 左旋（Left Rotation）- 解决 RR 失衡

```
失衡情况 (节点A的BF=-2, 右子节点BF≤0):

  z (BF=-2)                       y
   \                           /   \
    y (BF=-1)        →        z     x
     \                         \
      x (新插入)               T1
       \
       T3
```

```python
def left_rotate(z):
    y = z.right
    T2 = y.left
    
    # 执行旋转
    y.left = z
    z.right = T2
    
    # 更新高度
    z.height = 1 + max(get_height(z.left), get_height(z.right))
    y.height = 1 + max(get_height(y.left), get_height(y.right))
    
    return y
```

#### 3. 左右旋（Left-Right Rotation）- 解决 LR 失衡

```
失衡情况 (节点A的BF=2, 左子节点BF=-1):

      z                          z                    x
     /                          /                   /   \
    y (BF=-1)        →         x         →         y     z
     \                        /
      x (新插入)             y
     /                       \
    T2                       T2

先对y左旋，再对z右旋
```

#### 4. 右左旋（Right-Left Rotation）- 解决 RL 失衡

```
失衡情况 (节点A的BF=-2, 右子节点BF=1):

  z                            z                      x
   \                            \                   /   \
    y (BF=1)        →            x       →         z     y
   /                              \
  x (新插入)                        y
   \                              /
    T2                           T2

先对y右旋，再对z左旋
```

### 旋转选择决策树

```
插入/删除后失衡节点为 z
        |
    计算 BF(z)
        |
    +2 ------→ 左子树过高
        |
    BF(y) where y = z.left
        |
    +1 ------→ LL → 右旋
        |
    -1 ------→ LR → 先左旋y，再右旋z

    -2 ------→ 右子树过高
        |
    BF(y) where y = z.right
        |
    -1 ------→ RR → 左旋
        |
    +1 ------→ RL → 先右旋y，再左旋z
```

## 实现 (Implementation)

```python
class AVLNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1  # 叶节点高度为1

class AVLTree:
    def get_height(self, node):
        return node.height if node else 0
    
    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0
    
    def right_rotate(self, z):
        y = z.left
        T3 = y.right
        
        y.right = z
        z.left = T3
        
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        
        return y
    
    def left_rotate(self, z):
        y = z.right
        T2 = y.left
        
        y.left = z
        z.right = T2
        
        z.height = 1 + max(self.get_height(z.left), self.get_height(z.right))
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        
        return y
    
    def insert(self, node, key):
        # 1. 标准BST插入
        if not node:
            return AVLNode(key)
        
        if key < node.key:
            node.left = self.insert(node.left, key)
        elif key > node.key:
            node.right = self.insert(node.right, key)
        else:
            return node  # 重复键
        
        # 2. 更新高度
        node.height = 1 + max(self.get_height(node.left), 
                              self.get_height(node.right))
        
        # 3. 获取平衡因子
        balance = self.get_balance(node)
        
        # 4. 如果不平衡，有4种情况
        
        # LL
        if balance > 1 and key < node.left.key:
            return self.right_rotate(node)
        
        # RR
        if balance < -1 and key > node.right.key:
            return self.left_rotate(node)
        
        # LR
        if balance > 1 and key > node.left.key:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        
        # RL
        if balance < -1 and key < node.right.key:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)
        
        return node
    
    def delete(self, node, key):
        # 1. 标准BST删除
        if not node:
            return node
        
        if key < node.key:
            node.left = self.delete(node.left, key)
        elif key > node.key:
            node.right = self.delete(node.right, key)
        else:
            # 找到要删除的节点
            if not node.left:
                return node.right
            elif not node.right:
                return node.left
            
            # 有两个子节点，找后继
            temp = self.get_min(node.right)
            node.key = temp.key
            node.right = self.delete(node.right, temp.key)
        
        if not node:
            return node
        
        # 2. 更新高度
        node.height = 1 + max(self.get_height(node.left),
                              self.get_height(node.right))
        
        # 3. 获取平衡因子
        balance = self.get_balance(node)
        
        # 4. 重新平衡
        
        # LL
        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.right_rotate(node)
        
        # LR
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        
        # RR
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.left_rotate(node)
        
        # RL
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)
        
        return node
    
    def get_min(self, node):
        while node.left:
            node = node.left
        return node
```

## 复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| 查找 | $O(\log n)$ | $O(1)$ |
| 插入 | $O(\log n)$ | $O(\log n)$ 递归栈 |
| 删除 | $O(\log n)$ | $O(\log n)$ 递归栈 |
| 旋转 | $O(1)$ | $O(1)$ |
| 遍历 | $O(n)$ | $O(\log n)$~$O(n)$ |

### 为什么是 $O(\log n)$？

设 $N(h)$ 为高度为 $h$ 的 AVL 树的最少节点数：
$$N(h) = N(h-1) + N(h-2) + 1$$

这与斐波那契数列相似，因此：
$$h = O(\log n)$$

## AVL vs 红黑树

| 特性 | AVL树 | 红黑树 |
|------|-------|--------|
| 平衡条件 | 严格（BF ∈ {-1,0,1}） | 宽松（黑高相等） |
| 查找速度 | 更快 | 稍慢 |
| 插入旋转 | 最多2次 | 最多2次 |
| 删除旋转 | 最多 $O(\log n)$ 次 | 最多3次 |
| 实现复杂度 | 较复杂 | 更复杂 |
| 适用场景 | 查找密集 | 插入删除密集 |

```
查找密集应用: 选择 AVL
插入删除频繁: 选择红黑树
```

## 应用场景

### 1. 数据库索引（内存中）

需要快速查找且数据相对稳定的场景。

### 2. 内存有序集合

对查找性能要求极高的有序集合实现。

### 3. 实时系统

需要严格最坏情况时间保证的系统。

## 面试要点

### Q1: 为什么 AVL 树的高度是 $O(\log n)$？

设 $n_h$ 为高度为 $h$ 的 AVL 树的最少节点数：
- $n_0 = 0, n_1 = 1$
- $n_h = n_{h-1} + n_{h-2} + 1$

这个递推与斐波那契数列类似，因此 $n_h \approx \phi^h$，其中 $\phi$ 为黄金比例。
$$h = O(\log n)$$

### Q2: AVL 树 vs 红黑树的选择？

- **查找操作为主**（$> 80\%$）：选 AVL，更严格平衡
- **插入删除频繁**：选红黑树，旋转次数更少
- **实现简单性**：AVL 更容易理解和实现

### Q3: 如何在不旋转的情况下判断 AVL 树是否平衡？

```python
def is_balanced(root):
    """返回 (是否平衡, 高度)"""
    if not root:
        return True, 0
    
    left_balanced, left_height = is_balanced(root.left)
    right_balanced, right_height = is_balanced(root.right)
    
    balanced = (left_balanced and right_balanced and
                abs(left_height - right_height) <= 1)
    height = max(left_height, right_height) + 1
    
    return balanced, height
```

## 相关概念

- [二叉搜索树](../data-structures/bst.md) - AVL树的基础
- [红黑树](../data-structures/red-black-tree.md) - 另一种自平衡BST
- [B树](../data-structures/b-tree.md) - 磁盘优化的平衡树
- [二叉树](../data-structures/binary-tree.md) - 基础树结构
- [旋转操作可视化](https://www.cs.usfca.edu/~galles/visualization/AVLtree.html)

## 参考资料

1. 《算法导论》第13章 - 红黑树（AVL树思想类似）
2. 《数据结构与算法分析》Mark Allen Weiss
3. AVL tree - Wikipedia
4. AVL Tree Visualization - USFCA
