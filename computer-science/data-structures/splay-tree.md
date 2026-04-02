# 伸展树 (Splay Tree)

## 简介
**伸展树**（Splay Tree）是一种自调整二叉搜索树，通过**伸展（Splay）操作**将最近访问的节点旋转到根位置。它不需要存储平衡因子等额外信息，平摊时间复杂度为 $O(\log n)$，且最近访问的元素可以快速再次访问，具有较好的缓存局部性。

## 核心概念
- **伸展操作（Splay）**：通过旋转将指定节点移动到根位置
- **自调整性**：频繁访问的元素靠近根节点，形成"热点"效应
- **平摊分析**：单次操作可能 $O(n)$，但m次操作平摊 $O(\log n)$
- **三种旋转**：单旋（Zig）、之字旋（Zig-Zag）、一字旋（Zig-Zig）

## 实现方式
```python
class SplayTreeNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.parent = None  # 父节点指针（可选）

class SplayTree:
    def __init__(self):
        self.root = None
    
    def right_rotate(self, x):
        """右旋"""
        y = x.left
        x.left = y.right
        if y.right:
            y.right.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.right = x
        x.parent = y
    
    def left_rotate(self, x):
        """左旋"""
        y = x.right
        x.right = y.left
        if y.left:
            y.left.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
    
    def splay(self, x):
        """伸展操作：将节点x旋转到根"""
        while x.parent:
            p = x.parent
            g = p.parent
            
            if not g:  # Zig：父节点是根
                if x == p.left:
                    self.right_rotate(p)
                else:
                    self.left_rotate(p)
            elif x == p.left and p == g.left:  # Zig-Zig
                self.right_rotate(g)
                self.right_rotate(p)
            elif x == p.right and p == g.right:  # Zig-Zig
                self.left_rotate(g)
                self.left_rotate(p)
            elif x == p.right and p == g.left:  # Zig-Zag
                self.left_rotate(p)
                self.right_rotate(g)
            else:  # Zig-Zag
                self.right_rotate(p)
                self.left_rotate(g)
    
    def insert(self, key):
        """插入新元素"""
        if not self.root:
            self.root = SplayTreeNode(key)
            return
        
        curr = self.root
        parent = None
        while curr:
            parent = curr
            if key < curr.key:
                curr = curr.left
            elif key > curr.key:
                curr = curr.right
            else:  # 重复元素
                self.splay(curr)
                return
        
        new_node = SplayTreeNode(key)
        new_node.parent = parent
        if key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node
        self.splay(new_node)
    
    def search(self, key):
        """查找元素"""
        curr = self.root
        parent = None
        while curr:
            parent = curr
            if key < curr.key:
                curr = curr.left
            elif key > curr.key:
                curr = curr.right
            else:
                self.splay(curr)
                return True
        
        # 未找到，将最后一个访问节点伸展到根
        if parent:
            self.splay(parent)
        return False
    
    def find_min(self, node):
        """找到子树的最小节点"""
        while node.left:
            node = node.left
        return node
    
    def delete(self, key):
        """删除元素"""
        if not self.search(key):
            return False
        
        # 此时key所在节点已在根
        left_subtree = self.root.left
        right_subtree = self.root.right
        
        if not left_subtree:
            self.root = right_subtree
            if right_subtree:
                right_subtree.parent = None
        elif not right_subtree:
            self.root = left_subtree
            left_subtree.parent = None
        else:
            # 将左子树的最大值伸展到左子树根
            left_subtree.parent = None
            self.root = left_subtree
            max_node = self.find_max(left_subtree)
            self.splay(max_node)
            # 连接右子树
            max_node.right = right_subtree
            right_subtree.parent = max_node
        
        return True
    
    def find_max(self, node):
        """找到子树的最大节点"""
        while node.right:
            node = node.right
        return node
    
    def inorder(self, node):
        """中序遍历"""
        if node:
            self.inorder(node.left)
            print(node.key, end=' ')
            self.inorder(node.right)

# 使用示例
st = SplayTree()
for val in [10, 20, 30, 25, 5, 15]:
    st.insert(val)

print("Search 25:", st.search(25))  # True，25被伸展到根
print("Root after search:", st.root.key)  # 25
```

## 应用场景
- **缓存实现**：频繁访问的数据靠近根，访问更快
- **内存管理**：操作系统内存分配器（如Doug Lea Malloc）
- **数据压缩**：Gzip使用的LZ77算法中的滑动窗口
- **网络路由**：最近使用的路由信息优先查询

## 面试要点
1. **Q: 伸展树的时间复杂度是多少？为什么？**
   A: 伸展树的平摊时间复杂度为 $O(\log n)$。虽然单次操作最坏 $O(n)$，但通过势能分析法可以证明，m次操作的总时间复杂度为 $O(m \log n)$，即平摊每次 $O(\log n)$。

2. **Q: 伸展树和AVL树/红黑树的区别？**
   A: 伸展树是"自调整"的，不需要维护平衡信息，实现简单；访问模式局部性强时性能更好。AVL树和红黑树是"严格平衡"的，每次操作后保持平衡，最坏情况保证 $O(\log n)$。

3. **Q: 什么是伸展树的"热点"效应？**
   A: 由于频繁访问的节点会被伸展到根附近，形成热点聚集。如果访问模式具有局部性（某些元素被频繁访问），伸展树的实际性能会优于理论平摊复杂度。

4. **Q: 为什么伸展树使用Zig-Zig而不是两次Zig？**
   A: 使用Zig-Zig（祖父-父-孙同向时）可以保证平摊复杂度为 $O(\log n)$。如果只用简单的旋转，平摊复杂度会变成 $O(n)$。

## 相关概念

### 数据结构
- [AVL树](./avl-tree.md) - 严格平衡的二叉搜索树
- [红黑树](./red-black-tree.md) - 另一种自平衡二叉搜索树
- [二叉搜索树](./bst.md) - 伸展树的基础

### 算法
- [旋转操作](../algorithms/binary-search-tree.md) - 伸展的核心操作
- [摊还分析](../algorithms/amortized-analysis.md) - 分析伸展树复杂度的方法

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 平摊 $O(\log n)$

### 系统实现
- [内存管理](../systems/memory-management.md) - 伸展树的实际应用
