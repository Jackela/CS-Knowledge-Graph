# 树 (Tree)

## 概述

树是一种非线性层次数据结构，由节点和边组成，模拟具有根、分支和叶子的树形结构。与线性结构（数组、链表）不同，树结构中的元素之间存在一对多的层次关系，这使得树成为表示层次数据、组织信息和实现高效搜索算法的理想选择。

在数学上，树被定义为**连通无向无环图**，或等价地定义为任意两个顶点间存在唯一简单路径的图。这个定义揭示了树与图论之间的深刻联系，同时也强调了树的两个核心性质：连通性与无环性。

---

## 原理 (Principles)

### 基本术语

#### 节点相关概念

| 术语 | 英文 | 定义 |
|------|------|------|
| 根节点 | Root | 树中唯一没有父节点的节点，是整棵树的起始点 |
| 子节点 | Child | 某节点的直接后继节点 |
| 父节点 | Parent | 某节点的直接前驱节点 |
| 兄弟节点 | Siblings | 具有相同父节点的节点集合 |
| 叶节点 | Leaf/External Node | 度为0的节点，即没有子节点的节点 |
| 内部节点 | Internal Node | 至少有一个子节点的节点 |
| 祖先节点 | Ancestor | 从根到该节点路径上的所有节点（包括根） |
| 后代节点 | Descendant | 以该节点为根的子树中的所有节点 |

#### 边与路径

- **边 (Edge)**：连接两个节点的线段，表示父子关系。具有 $n$ 个节点的树恰好有 $n-1$ 条边。
- **路径 (Path)**：节点序列 $v_1, v_2, ..., v_k$，其中每对相邻节点间都有边相连。
- **路径长度 (Path Length)**：路径上边的数量。

#### 层级度量

- **节点的深度 (Depth)**：从根节点到该节点的路径长度。根节点深度为0。
- **节点的高度 (Height)**：从该节点到叶节点的最长路径长度。叶节点高度为0。
- **树的深度 (Depth)**：树中所有节点深度的最大值，等于树的高度。
- **树的层数 (Level)**：深度为 $k$ 的节点位于第 $k$ 层（从0开始计数）。

### 数学性质

#### 基本定理

**定理 1（边数定理）**
对于任何具有 $n$ 个节点的树，边数 $m = n - 1$。

*证明*：通过数学归纳法。
- 基础：$n = 1$ 时，$m = 0 = 1 - 1$，成立。
- 归纳：假设对 $n$ 个节点的树成立。对于 $n+1$ 个节点的树，新增节点必须通过一条边连接到原树，因此 $m_{new} = (n-1) + 1 = n = (n+1) - 1$。

**定理 2（度数关系）**
设树中节点的度数为 $d_i$，则：
$$\sum_{i=1}^{n} d_i = 2(n-1) = 2m$$

对于树结构，由于每个非根节点都有且仅有一条入边（来自父节点）：
$$\sum_{i=1}^{n} d_i^{out} = n - 1$$
其中 $d_i^{out}$ 表示节点的出度（子节点数）。

**定理 3（叶节点数量下界）**
对于任意非空树，若每个内部节点至少有 $k$ 个子节点（$k \geq 2$），则叶节点数 $L$ 满足：
$$L \geq (k-1)I + 1$$
其中 $I$ 为内部节点数。

*证明*：设总节点数 $n = I + L$。由边数关系：
$$n - 1 = \sum_{i=1}^{I} d_i^{out} \geq k \cdot I$$
因此：
$$I + L - 1 \geq k \cdot I \Rightarrow L \geq (k-1)I + 1$$

### 树的分类

#### 按度数限制

| 类型 | 定义 |
|------|------|
| 二叉树 (Binary Tree) | 每个节点最多有2个子节点 |
| k叉树 (k-ary Tree) | 每个节点最多有 $k$ 个子节点 |
| 满k叉树 (Full k-ary Tree) | 每个内部节点恰好有 $k$ 个子节点 |
| 完全k叉树 (Complete k-ary Tree) | 除最后一层外完全填满，最后一层节点集中在左侧 |

#### 按结构特性

| 类型 | 特性 |
|------|------|
| 平衡树 (Balanced Tree) | 任意节点的左右子树高度差不超过某个常数（如AVL树的1，红黑树的2倍） |
| 有序树 (Ordered Tree) | 子节点的顺序有意义 |
| 无序树 (Unordered Tree) | 子节点的顺序无意义 |

---

## 树的遍历 (Tree Traversals)

树的遍历是按照某种顺序访问树中所有节点的过程。遍历策略的选择取决于具体应用场景。

### 深度优先遍历 (DFS - Depth-First Search)

深度优先遍历沿着树的深度方向进行，尽可能深地探索分支。

#### 前序遍历 (Pre-order)

**访问顺序**：根节点 → 左子树 → 右子树

**伪代码**：
```
preorder(node):
    if node is null:
        return
    visit(node)           // 处理当前节点
    for each child in node.children:
        preorder(child)   // 递归遍历子节点
```

**应用**：复制树结构、序列化树、表达式的前缀表示。

#### 中序遍历 (In-order)

**访问顺序**：左子树 → 根节点 → 右子树

*注意：中序遍历严格定义于二叉树。对于一般树，中序遍历概念不适用或需要扩展定义。*

对于二叉树的中序遍历：
```
inorder(node):
    if node is null:
        return
    inorder(node.left)    // 遍历左子树
    visit(node)           // 处理当前节点
    inorder(node.right)   // 遍历右子树
```

**应用**：二叉搜索树的中序遍历产生有序序列。

#### 后序遍历 (Post-order)

**访问顺序**：左子树 → 右子树 → 根节点

**伪代码**：
```
postorder(node):
    if node is null:
        return
    for each child in node.children:
        postorder(child)  // 递归遍历所有子节点
    visit(node)           // 处理当前节点
```

**应用**：删除树、计算目录大小、表达式的后缀表示（逆波兰表示法）。

### 广度优先遍历 (BFS - Breadth-First Search)

**层次遍历 (Level-order)**：按层次从上到下、同层从左到右访问节点。

**伪代码**（使用队列）：
```
levelorder(root):
    if root is null:
        return
    queue = new Queue()
    queue.enqueue(root)
    
    while queue is not empty:
        node = queue.dequeue()
        visit(node)
        for each child in node.children:
            queue.enqueue(child)
```

**应用**：查找最短路径、按层次处理数据、树的宽度计算。

### 遍历复杂度分析

| 遍历方式 | 时间复杂度 | 空间复杂度 | 说明 |
|----------|------------|------------|------|
| 前序/中序/后序 DFS | $O(n)$ | $O(h)$ | $h$ 为树高，最坏 $O(n)$ |
| 层次遍历 BFS | $O(n)$ | $O(w)$ | $w$ 为最大宽度，最坏 $O(n)$ |

---

## 复杂度分析 (Complexity Analysis)

### 基本操作复杂度

对于具有 $n$ 个节点的树：

| 操作 | 时间复杂度 | 空间复杂度 | 说明 |
|------|------------|------------|------|
| 搜索 | $O(n)$ | $O(h)$ | 一般树需遍历所有节点 |
| 插入 | $O(1)$ ~ $O(n)$ | $O(1)$ | 已知父节点时 $O(1)$ |
| 删除 | $O(n)$ | $O(h)$ | 需先定位节点 |
| 遍历 | $O(n)$ | $O(h)$ ~ $O(w)$ | 取决于遍历策略 |

### 特殊树结构的优化

| 树类型 | 搜索 | 插入 | 删除 | 特点 |
|--------|------|------|------|------|
| 二叉搜索树 (BST) | $O(h)$ | $O(h)$ | $O(h)$ | $h$ 平均 $O(\log n)$，最坏 $O(n)$ |
| AVL树 | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | 严格平衡 |
| 红黑树 | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | 近似平衡，旋转更少 |
| B树/B+树 | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | 多路搜索，适合外存 |
| 堆 | $O(n)$ | $O(\log n)$ | $O(\log n)$ | 优先队列优化 |

### 数学关系

对于**满 $k$ 叉树**：
- 高度为 $h$ 的满 $k$ 叉树节点数：$n = \frac{k^{h+1} - 1}{k - 1}$
- 节点数为 $n$ 的满 $k$ 叉树高度：$h = \log_k(n(k-1) + 1) - 1 = O(\log n)$

对于**完全二叉树**（$k=2$）：
- 高度 $h = \lfloor \log_2 n \rfloor$
- 第 $i$ 层最多有 $2^i$ 个节点（$i$ 从0开始）

---

## 实现示例 (Implementation)

### 1. 孩子-兄弟表示法 (Child-Sibling Representation)

孩子-兄弟表示法（也称为左孩子-右兄弟表示法）将一般树转换为二叉树形式存储，是存储一般树最节省空间的方法。

**结构定义**：
```cpp
template <typename T>
struct TreeNode {
    T data;                    // 节点数据
    TreeNode* firstChild;      // 第一个孩子节点
    TreeNode* nextSibling;     // 下一个兄弟节点
    
    TreeNode(T val) : data(val), firstChild(nullptr), nextSibling(nullptr) {}
};
```

**优势**：
- 空间复杂度：$O(n)$，每个节点仅需2个指针
- 可将一般树操作转化为二叉树操作
- 便于实现森林到二叉树的转换

**遍历实现**：
```cpp
template <typename T>
class GeneralTree {
private:
    TreeNode<T>* root;
    
    // 前序遍历（先根遍历）
    void preorder(TreeNode<T>* node, vector<T>& result) {
        if (!node) return;
        result.push_back(node->data);
        // 遍历所有孩子
        for (TreeNode<T>* child = node->firstChild; child; child = child->nextSibling) {
            preorder(child, result);
        }
    }
    
    // 后序遍历
    void postorder(TreeNode<T>* node, vector<T>& result) {
        if (!node) return;
        for (TreeNode<T>* child = node->firstChild; child; child = child->nextSibling) {
            postorder(child, result);
        }
        result.push_back(node->data);
    }
    
public:
    // 添加子节点
    void addChild(TreeNode<T>* parent, T value) {
        TreeNode<T>* newNode = new TreeNode<T>(value);
        if (!parent->firstChild) {
            parent->firstChild = newNode;
        } else {
            TreeNode<T>* sibling = parent->firstChild;
            while (sibling->nextSibling) {
                sibling = sibling->nextSibling;
            }
            sibling->nextSibling = newNode;
        }
    }
};
```

### 2. 父指针表示法 (Parent Pointer Representation)

适用于需要频繁查找父节点的场景，如并查集 (Union-Find) 数据结构。

```cpp
template <typename T>
struct ParentTreeNode {
    T data;
    int parent;  // 父节点在数组中的索引，-1表示根
};

template <typename T>
class ParentTree {
private:
    vector<ParentTreeNode<T>> nodes;
    
public:
    int addNode(T data, int parentIdx = -1) {
        nodes.push_back({data, parentIdx});
        return nodes.size() - 1;
    }
    
    // 查找根节点
    int findRoot(int idx) {
        while (nodes[idx].parent != -1) {
            idx = nodes[idx].parent;
        }
        return idx;
    }
    
    // 获取路径（从节点到根）
    vector<T> getPath(int idx) {
        vector<T> path;
        while (idx != -1) {
            path.push_back(nodes[idx].data);
            idx = nodes[idx].parent;
        }
        return path;
    }
};
```

### 3. 孩子链表表示法

每个节点维护一个孩子链表，适合子节点数量变化较大的场景。

```cpp
template <typename T>
struct ChildLinkNode {
    int childIdx;           // 孩子在数组中的索引
    ChildLinkNode* next;    // 下一个孩子
};

template <typename T>
struct TreeNodeWithChildren {
    T data;
    ChildLinkNode* firstChild;  // 指向孩子链表头
};

template <typename T>
class ChildrenListTree {
private:
    vector<TreeNodeWithChildren<T>> nodes;
    
public:
    int addNode(T data) {
        nodes.push_back({data, nullptr});
        return nodes.size() - 1;
    }
    
    void addChild(int parentIdx, int childIdx) {
        ChildLinkNode* newLink = new ChildLinkNode{childIdx, nodes[parentIdx].firstChild};
        nodes[parentIdx].firstChild = newLink;
    }
    
    // 获取所有孩子
    vector<int> getChildren(int parentIdx) {
        vector<int> children;
        ChildLinkNode* curr = nodes[parentIdx].firstChild;
        while (curr) {
            children.push_back(curr->childIdx);
            curr = curr->next;
        }
        return children;
    }
};
```

### 4. 数组表示法（适用于完全树）

对于完全二叉树，可以使用数组高效存储：

```cpp
// 对于节点在索引 i 处：
// 左孩子索引：2*i + 1
// 右孩子索引：2*i + 2  
// 父节点索引：(i-1)/2

template <typename T>
class ArrayBinaryTree {
private:
    vector<T> tree;
    
public:
    void setValue(int idx, T value) {
        if (idx >= tree.size()) {
            tree.resize(idx + 1);
        }
        tree[idx] = value;
    }
    
    T getValue(int idx) {
        return (idx < tree.size()) ? tree[idx] : T();
    }
    
    int leftChild(int idx) { return 2 * idx + 1; }
    int rightChild(int idx) { return 2 * idx + 2; }
    int parent(int idx) { return (idx - 1) / 2; }
};
```

---

## 应用场景 (Applications)

### 1. 文件系统

文件系统的目录结构是典型的树结构应用：
- **根目录**：树的根节点
- **目录**：内部节点
- **文件**：叶节点
- **路径**：从根到节点的路径字符串

**特性**：
- 支持高效的文件查找（通过路径遍历）
- 便于实现权限继承（子节点继承父节点权限）
- 支持目录的递归操作（复制、删除、搜索）

### 2. 组织架构图

企业或机构的组织结构天然具有层次性：
- CEO/总裁：根节点
- 部门经理：内部节点
- 普通员工：叶节点

**应用价值**：
- 汇报关系可视化
- 权限层级管理
- 资源分配追踪

### 3. DOM树 (Document Object Model)

Web页面的HTML/XML文档被解析为DOM树：
- **Document**：根节点
- **Element节点**：内部节点（如 `<div>`, `<p>`）
- **Text节点**：叶节点
- **Attribute**：节点的属性

**操作场景**：
- JavaScript通过DOM API遍历和修改页面
- CSS选择器基于树的层次关系匹配元素
- 浏览器渲染引擎按树结构计算布局

### 4. 抽象语法树 (AST)

编译器将源代码解析为抽象语法树：
- **程序/函数定义**：根节点
- **语句/表达式**：内部节点
- **标识符/常量**：叶节点

**编译流程**：
```
源代码 → 词法分析 → 语法分析 → AST → 语义分析 → 中间代码 → 优化 → 目标代码
```

### 5. 决策树与机器学习

决策树是机器学习中的经典算法：
- **根节点**：最优划分特征
- **内部节点**：特征测试
- **叶节点**：类别标签或预测值

**算法变体**：ID3、C4.5、CART、随机森林（多棵决策树的集成）。

### 6. 游戏树 (Game Tree)

博弈论和AI游戏玩家使用游戏树：
- **根节点**：当前游戏状态
- **子节点**：可能的下一步状态
- **叶节点**：游戏结束状态（胜负平）

**算法**：Minimax算法、Alpha-Beta剪枝用于在博弈树中搜索最优策略。

### 7. 数据库索引

B树和B+树是数据库索引的核心数据结构：
- 支持高效的磁盘块访问
- 保持数据有序
- 支持范围查询

---

## 面试要点 (Interview Questions)

### Q1: 证明具有 $n$ 个节点的树有 $n-1$ 条边

**答案**：
数学归纳法：
- **基础**：$n=1$ 时，单个节点无边，$0 = 1-1$，成立。
- **归纳假设**：假设对 $k$ 个节点的树成立。
- **归纳步骤**：考虑 $k+1$ 个节点的树。删除任意一条边会将树分成两个连通分量，每个分量都是树。设分量大小为 $n_1$ 和 $n_2$（$n_1 + n_2 = k+1$）。由归纳假设，边数为 $(n_1-1) + (n_2-1) + 1 = n_1 + n_2 - 1 = k$。

另一种证明：每个非根节点有且仅有一条来自父节点的边，共 $n-1$ 个非根节点，因此 $n-1$ 条边。

---

### Q2: 如何判断两棵树是否相同（结构相同且对应节点值相同）？

**答案**：
递归比较：
1. 两棵树都为空，返回 true
2. 一棵为空一棵非空，返回 false
3. 当前节点值不同，返回 false
4. 递归比较所有对应子树

```cpp
bool isSameTree(TreeNode* p, TreeNode* q) {
    if (!p && !q) return true;
    if (!p || !q) return false;
    if (p->val != q->val) return false;
    return isSameTree(p->left, q->left) && 
           isSameTree(p->right, q->right);
}
```

时间复杂度：$O(n)$，空间复杂度：$O(h)$。

---

### Q3: 如何在不使用递归的情况下实现树的前序遍历？

**答案**：
使用栈模拟递归过程：

```cpp
vector<int> preorderIterative(TreeNode* root) {
    vector<int> result;
    if (!root) return result;
    
    stack<TreeNode*> stk;
    stk.push(root);
    
    while (!stk.empty()) {
        TreeNode* node = stk.top();
        stk.pop();
        result.push_back(node->val);
        
        // 右孩子先入栈，确保左孩子先处理
        if (node->right) stk.push(node->right);
        if (node->left) stk.push(node->left);
    }
    return result;
}
```

---

### Q4: 什么是树的直径？如何求解？

**答案**：
**树的直径**是树中任意两节点间路径的最大长度（边数）。

**求解算法**（两次DFS/BFS）：
1. 从任意节点 $u$ 出发，找到最远节点 $v$
2. 从 $v$ 出发，找到最远节点 $w$
3. $v$ 到 $w$ 的路径即为直径

**证明**：
设直径为 $a$ 到 $b$ 的路径。从任意节点 $u$ 出发的最远节点 $v$ 必为 $a$ 或 $b$ 之一。否则可以构造出更长的路径，与直径定义矛盾。

时间复杂度：$O(n)$。

---

### Q5: 如何将一棵多叉树序列化为字符串，并能反序列化复原？

**答案**：
使用前序遍历配合特殊标记（如 `#` 表示空孩子）：

```cpp
// 序列化
string serialize(TreeNode* root) {
    if (!root) return "#";
    string result = to_string(root->val);
    for (TreeNode* child : root->children) {
        result += "," + serialize(child);
    }
    result += ",#";  // 标记孩子列表结束
    return result;
}

// 反序列化（使用索引引用）
TreeNode* deserialize(vector<string>& nodes, int& idx) {
    if (idx >= nodes.size() || nodes[idx] == "#") {
        idx++;
        return nullptr;
    }
    TreeNode* root = new TreeNode(stoi(nodes[idx++]));
    while (idx < nodes.size() && nodes[idx] != "#") {
        root->children.push_back(deserialize(nodes, idx));
    }
    idx++;  // 跳过结束标记
    return root;
}
```

---

## 相关概念 (Related Concepts)

### 数据结构
- [二叉树](./binary-tree.md)：每个节点最多两个子节点的有序树
- [图](./graph.md)：树是连通无环图，是图的特例
- [堆](./heap.md)：基于完全二叉树实现的优先队列
- [二叉搜索树](./binary-search-tree.md)：支持高效查找的树结构

### 算法
- [图遍历](../algorithms/graph-traversal.md)：DFS/BFS 遍历算法在树上的应用
- [排序](../algorithms/sorting.md)：树结构在排序中的应用（如二叉搜索树排序）
- [分治算法](../algorithms/divide-conquer.md)：树的分治策略

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：分析树操作的时间效率
- [空间复杂度](./space-complexity.md)：评估树的内存占用
- [空间复杂度](../../references/space-complexity.md)：评估树的内存占用

### 系统实现
- [文件系统](../systems/file-system.md)：目录树结构
- [DOM 操作](../../references/dom.md)：浏览器文档对象模型树
- [数据库索引](../../references/database-index.md)：B树/B+树索引结构

## 参考资料 (References)

1. **Donald E. Knuth**, *The Art of Computer Programming, Vol. 1: Fundamental Algorithms*, 3rd Edition, Addison-Wesley, 1997.
   - 第2章详细论述了树结构的信息表示与遍历算法

2. **Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein**, *Introduction to Algorithms*, 4th Edition, MIT Press, 2022.
   - 第10章（基本数据结构）和第12章（二叉搜索树）

3. **Mark Allen Weiss**, *Data Structures and Algorithm Analysis in C++*, 4th Edition, Pearson, 2013.
   - 第4章系统讲解树结构，包括AVL树、伸展树等高级主题

4. **Robert Sedgewick, Kevin Wayne**, *Algorithms*, 4th Edition, Addison-Wesley, 2011.
   - 第3章涵盖基本树结构，第4章讨论图与树的联系

5. **Alfred V. Aho, John E. Hopcroft, Jeffrey D. Ullman**, *Data Structures and Algorithms*, Addison-Wesley, 1983.
   - 经典教材，第3章深入分析树的数学性质

6. **Wikipedia**: [Tree (data structure)](https://en.wikipedia.org/wiki/Tree_(data_structure))
   - 全面的术语定义与分类体系

---

*文档版本：1.0*  
*最后更新：2025年*
- [抽象数据类型](../../references/adt.md) - 树的 ADT 定义
