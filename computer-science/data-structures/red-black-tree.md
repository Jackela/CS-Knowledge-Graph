# 红黑树 (Red-Black Tree)

## 简介

**红黑树（Red-Black Tree）**是一种**自平衡二叉搜索树**，由 Rudolf Bayer 于 1972 年发明。它在每个节点上增加了一个存储位表示节点的**颜色**（红色或黑色），通过特定的颜色规则确保树始终保持近似平衡，从而保证查找、插入和删除操作的时间复杂度为 $O(\log n)$。

```
              10B
            /     \
          5R       15R
         /  \     /   \
       3B   7B  13B   20B
      /
    1R

B = Black (黑色)    R = Red (红色)

红黑树性质:
1. 根是黑色
2. 所有叶子(NIL)是黑色
3. 红色节点的子节点必须是黑色
4. 从任一节点到其叶子的所有路径包含相同数目的黑色节点
```

红黑树是许多编程语言标准库有序容器的底层实现：
- Java: `TreeMap`, `TreeSet`
- C++: `std::map`, `std::set` (通常实现)
- Linux内核: 完全公平调度器(CFS)

## 原理 (Principles)

### 红黑树的五个性质

1. **节点是红色或黑色**
2. **根是黑色**
3. **所有叶子（NIL）是黑色**
4. **红色节点的子节点必须是黑色**（即不能有两个连续的红色节点）
5. **从任一节点到其每个叶子的所有简单路径都包含相同数目的黑色节点**（黑高相同）

### 黑高（Black Height）

从节点 $x$ 到其叶子节点的任意路径上的黑色节点数（不包括 $x$ 自身）。

```
              10 (bh=2)
            /     \
          5        15 (bh=1)
         / \      /   \
       3    7   13     20 (bh=1)
      / \
    1   NIL

节点10到各叶子的黑节点数:
10(黑)→5(红)→3(黑)→1(红)→NIL: 黑节点=3 (10,3,NIL)
10(黑)→5(红)→3(黑)→NIL: 黑节点=3
10(黑)→5(红)→7(黑)→NIL: 黑节点=3
10(黑)→15(红)→13(黑)→NIL: 黑节点=3
10(黑)→15(红)→20(黑)→NIL: 黑节点=3
```

**重要推论**：含有 $n$ 个内部节点的红黑树高度最多为 $2\log(n+1)$

## 插入操作

### 插入步骤

1. **标准 BST 插入**，新节点涂为**红色**
2. **修复红黑树性质**（如果需要）

### 插入修复情况

设新插入节点为 $z$，父节点为 $p$，祖父节点为 $g$，叔节点为 $u$。

#### 情况1：$z$ 是根节点

将 $z$ 涂黑。

#### 情况2：$p$ 是黑色

无需修复，性质已满足。

#### 情况3：$p$ 是红色，$u$ 是红色

```
      g(黑)                   g(红)
     /    \                  /    \
   p(红)   u(红)    →      p(黑)  u(黑)
   /                       /
 z(红)                   z(红)

将p和u涂黑，g涂红，然后递归修复g
```

#### 情况4：$p$ 是红色，$u$ 是黑色，$z$ 是右子节点（LR情况）

先对 $p$ 左旋，转换为情况5。

#### 情况5：$p$ 是红色，$u$ 是黑色，$z$ 是左子节点（LL情况）

```
      g(黑)                   p(黑)
     /                       /    \
   p(红)        →          z(红)   g(红)
   /                                 \
 z(红)                               u(黑)

右旋g，交换p和g的颜色
```

### 插入修复代码

```python
def insert_fixup(self, z):
    while z.parent and z.parent.color == RED:
        if z.parent == z.parent.parent.left:
            y = z.parent.parent.right  # 叔节点
            
            if y and y.color == RED:
                # 情况3: 叔节点红色
                z.parent.color = BLACK
                y.color = BLACK
                z.parent.parent.color = RED
                z = z.parent.parent
            else:
                if z == z.parent.right:
                    # 情况4: LR，转为LL
                    z = z.parent
                    self.left_rotate(z)
                # 情况5: LL
                z.parent.color = BLACK
                z.parent.parent.color = RED
                self.right_rotate(z.parent.parent)
        else:
            # 对称情况
            y = z.parent.parent.left
            
            if y and y.color == RED:
                z.parent.color = BLACK
                y.color = BLACK
                z.parent.parent.color = RED
                z = z.parent.parent
            else:
                if z == z.parent.left:
                    z = z.parent
                    self.right_rotate(z)
                z.parent.color = BLACK
                z.parent.parent.color = RED
                self.left_rotate(z.parent.parent)
    
    self.root.color = BLACK
```

## 删除操作

删除比插入更复杂。基本策略：

1. **标准 BST 删除**
2. **如果被删除节点或替代节点是黑色，需要修复**

### 删除修复情况

设被删除节点的替代节点为 $x$，其兄弟节点为 $w$。

#### 情况1：$x$ 的兄弟 $w$ 是红色

```
      p                     w
     / \                   / \
    x   w      →          p   w右
       / \               / \
    w左  w右            x  w左

左旋p，交换p和w的颜色，进入其他情况
```

#### 情况2：$w$ 是黑色，且 $w$ 的两个子节点都是黑色

```
将w涂红，x上移指向p，继续循环
```

#### 情况3：$w$ 是黑色，$w$ 的左子红、右子黑

```
右旋w，交换w和其左子的颜色，进入情况4
```

#### 情况4：$w$ 是黑色，$w$ 的右子红

```
左旋p，w继承p的颜色，p和w右涂黑，结束
```

## 完整实现

```python
class Color:
    RED = 0
    BLACK = 1

class RBNode:
    def __init__(self, key, color=Color.RED):
        self.key = key
        self.color = color
        self.left = None
        self.right = None
        self.parent = None

class RedBlackTree:
    def __init__(self):
        self.NIL = RBNode(0, Color.BLACK)  # 哨兵叶子
        self.root = self.NIL
    
    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
    
    def right_rotate(self, y):
        x = y.left
        y.left = x.right
        if x.right != self.NIL:
            x.right.parent = y
        x.parent = y.parent
        if y.parent == self.NIL:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x
    
    def insert(self, key):
        z = RBNode(key)
        z.left = self.NIL
        z.right = self.NIL
        
        y = self.NIL
        x = self.root
        
        while x != self.NIL:
            y = x
            if z.key < x.key:
                x = x.left
            else:
                x = x.right
        
        z.parent = y
        if y == self.NIL:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z
        
        self._insert_fixup(z)
    
    def _insert_fixup(self, z):
        while z.parent and z.parent.color == Color.RED:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right
                if y.color == Color.RED:
                    z.parent.color = Color.BLACK
                    y.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    z = z.parent.parent
                else:
                    if z == z.parent.right:
                        z = z.parent
                        self.left_rotate(z)
                    z.parent.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    self.right_rotate(z.parent.parent)
            else:
                # 对称情况
                y = z.parent.parent.left
                if y.color == Color.RED:
                    z.parent.color = Color.BLACK
                    y.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self.right_rotate(z)
                    z.parent.color = Color.BLACK
                    z.parent.parent.color = Color.RED
                    self.left_rotate(z.parent.parent)
        self.root.color = Color.BLACK
```

## 复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| 查找 | $O(\log n)$ | $O(1)$ |
| 插入 | $O(\log n)$ | $O(1)$ |
| 删除 | $O(\log n)$ | $O(1)$ |
| 旋转 | $O(1)$ | $O(1)$ |
| 遍历 | $O(n)$ | $O(\log n)$ |

### 为什么高度是 $O(\log n)$？

设 $n$ 为内部节点数，$h$ 为树高。

由性质4和5：
- 最短路径（全黑）：至少 $h/2$ 个黑节点
- 从根到叶的任意路径黑节点数相同

因此：
$$n \geq 2^{h/2} - 1$$
$$h \leq 2\log(n+1) = O(\log n)$$

## 红黑树 vs AVL树

| 特性 | 红黑树 | AVL树 |
|------|--------|-------|
| 平衡条件 | 黑高相等 | 高度差 ≤ 1 |
| 严格程度 | 较宽松 | 较严格 |
| 查找 | 稍慢 | 稍快 (~20%) |
| 插入旋转 | ≤ 2次 | ≤ 2次 |
| 删除旋转 | ≤ 3次 | $O(\log n)$ 次 |
| 实现难度 | 较复杂 | 中等 |
| 实际应用 | 更广泛使用 | 查找密集场景 |

## 实际应用

### 1. C++ STL

```cpp
#include <map>
#include <set>

std::map<int, string> m;  // 通常用红黑树实现
std::set<int> s;          // 有序集合
```

### 2. Java 集合框架

```java
TreeMap<Integer, String> map = new TreeMap<>();
TreeSet<Integer> set = new TreeSet<>();
```

### 3. Linux 内核 CFS

完全公平调度器使用红黑树管理可运行进程，按虚拟运行时间(vruntime)排序。

### 4. 内存管理

某些内存分配器使用红黑树管理空闲内存块。

## 面试要点

### Q1: 为什么红黑树的插入比 AVL 树更高效？

- **红黑树**：插入最多2次旋转，且是局部调整
- **AVL树**：插入最多2次旋转，但删除可能需要 $O(\log n)$ 次
- 红黑树整体旋转次数更少，实现更高效

### Q2: 为什么新插入节点是红色？

如果插入黑色会违反性质5（黑高相同），需要调整整棵树。
插入红色只可能违反性质4（父子不能同红），局部修复即可。

### Q3: 证明红黑树高度上界

```
设 bh(x) 为节点x的黑高

性质5: 从x到叶子的路径上至少有 bh(x) 个黑节点
性质4: 路径上不能有连续红节点，所以红节点 ≤ 黑节点

因此: 任意路径长度 ≤ 2 * bh(x)

又: 以x为根的子树至少包含 2^bh(x) - 1 个内部节点

所以: n ≥ 2^bh(root) - 1
    bh(root) ≤ log(n+1)
    h ≤ 2 * bh(root) ≤ 2log(n+1)
```

### Q4: 红黑树 vs B树

- **红黑树**：二叉，内存优化
- **B树**：多路，磁盘优化
- 数据库索引多用 B+树，内存结构多用红黑树

## 相关概念

- [二叉搜索树](./bst.md) - 红黑树的基础
- [AVL树](./avl-tree.md) - 另一种自平衡BST
- [B树](./b-tree.md) - 磁盘优化的多路树
- [二叉树](./binary-tree.md) - 基础树结构
- [AVL树](../data-structures/avl-tree.md) - 另一种自平衡BST
- [B树](../data-structures/b-tree.md) - 磁盘优化的多路树
- [二叉树](../data-structures/binary-tree.md) - 基础树结构
- [Red-Black Tree Visualization](https://www.cs.usfca.edu/~galles/visualization/RedBlack.html)

## 参考资料

1. 《算法导论》第13章 - 红黑树
2. 《数据结构与算法分析》Mark Allen Weiss
3. Red–black tree - Wikipedia
4. Linux Kernel CFS Documentation
