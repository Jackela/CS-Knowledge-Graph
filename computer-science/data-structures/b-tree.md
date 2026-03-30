# B树 (B-Tree)

## 简介

**B树（B-Tree）**是一种**多路自平衡搜索树**，由 Rudolf Bayer 和 Edward McCreight 于 1970 年在波音研究实验室发明。B树专为**磁盘存储**设计，通过减少磁盘I/O次数来优化大规模数据存取。它是现代数据库和文件系统的核心数据结构。

```
        [20, 50]
       /    |    \
  [5,10] [30,40] [60,70,80]
  /  |   /  |   /   |   \
... ... ... ... ... ... ...

特点:
- 每个节点可以有多个键和多个子节点
- 所有叶子在同一层
- 节点大小通常设计为磁盘页大小(4KB)
```

B树被广泛应用于：
- 数据库索引（MySQL InnoDB、PostgreSQL）
- 文件系统（NTFS、HFS+、ext4）
- 键值存储（LevelDB、RocksDB）

## 原理 (Principles)

### B树性质

对于 **M阶B树**（每个节点最多M个子节点）：

1. **每个节点最多有 M 个子节点，M-1 个键**
2. **除根节点外，每个节点至少有 ⌈M/2⌉ 个子节点**
3. **根节点至少有 2 个子节点（除非它是叶子）**
4. **所有叶子节点在同一层**
5. **节点内的键按升序排列**
6. **子节点键的范围由父节点键分隔**

```
阶数 M=3 (2-3树):

      [50]
     /    \
  [20]    [70, 90]
  /  \    /   |   \
...  ... ... ...  ...

节点 [70, 90]:
- 有3个子节点
- 左子树键 < 70
- 中间子树: 70 < 键 < 90
- 右子树键 > 90
```

### 为什么适合磁盘？

```
磁盘访问 vs 内存访问:

内存: 访问任意地址 ≈ 100ns
磁盘: 随机读取一页(4KB) ≈ 10ms = 10,000,000ns

磁盘慢 100,000 倍！

B树设计目标: 减少磁盘访问次数
- 将多个键放在一个节点（一页）
- 树高度低，访问节点少
- 局部性好，预读有效
```

## 操作详解

### 1. 查找

```
查找 45:

        [30, 60]
       /   |    \
   [10,20] [40,50] [70,80]
            ↑
        40 < 45 < 50
        
继续搜索 [40,50] 的对应子节点
```

```python
def search(root, key):
    """在B树中查找key"""
    node = root
    while node:
        i = 0
        # 在节点内查找
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        # 找到
        if i < len(node.keys) and key == node.keys[i]:
            return node, i
        
        # 去子节点继续查找
        if node.is_leaf:
            return None, -1
        node = node.children[i]
    
    return None, -1
```

**时间复杂度**：$O(\log_M n)$ 次磁盘访问

### 2. 插入

#### 插入策略：分裂（Split）

```
向满节点插入时分裂:

    [20, 40, 60] (满, M=4)        [40]
    /   |    |   \          →     /   \
   ... ...  ...  ...          [20]   [60]
                              /  \   /  \
插入50:                     ... ... ... ...
1. 临时插入: [20, 40, 50, 60]
2. 分裂中间键 40 提升
3. 剩余分成两个节点
```

#### 插入过程

```python
def insert(self, key):
    root = self.root
    
    # 根满，分裂
    if len(root.keys) == self.max_keys:
        new_root = BTreeNode()
        new_root.children.append(root)
        self._split_child(new_root, 0)
        self.root = new_root
    
    self._insert_non_full(self.root, key)

def _split_child(self, parent, i):
    """分裂parent的第i个子节点"""
    full_child = parent.children[i]
    new_child = BTreeNode(leaf=full_child.leaf)
    
    mid = len(full_child.keys) // 2
    mid_key = full_child.keys[mid]
    
    # 新节点得到右半部分
    new_child.keys = full_child.keys[mid+1:]
    full_child.keys = full_child.keys[:mid]
    
    if not full_child.leaf:
        new_child.children = full_child.children[mid+1:]
        full_child.children = full_child.children[:mid+1]
    
    # 中间键提升到父节点
    parent.keys.insert(i, mid_key)
    parent.children.insert(i+1, new_child)

def _insert_non_full(self, node, key):
    """向非满节点插入"""
    if node.leaf:
        # 叶节点，直接插入
        idx = bisect_left(node.keys, key)
        node.keys.insert(idx, key)
    else:
        # 找到合适的子节点
        idx = bisect_left(node.keys, key)
        
        # 子节点满，先分裂
        if len(node.children[idx].keys) == self.max_keys:
            self._split_child(node, idx)
            # 分裂后可能需要调整idx
            if key > node.keys[idx]:
                idx += 1
        
        self._insert_non_full(node.children[idx], key)
```

### 3. 删除

删除最复杂，分多种情况：

#### 情况1：键在叶节点

直接删除，如果节点键数低于最小值，需要调整（借用或合并）。

#### 情况2：键在内部节点

用前驱或后继替换，然后删除前驱/后继。

#### 情况3：节点键数不足

```
从兄弟借用:

    [30, 50]                   [20, 50]
   /   |    \                 /   |    \
[10] [40] [60,70]    →    [10] [30,40] [60,70]
  ↑                       ↑
 键数不足                从右兄弟借用

合并:

    [30, 50]                   [50]
   /   |    \                 /    \
[10] [40] [60,70]    →    [10,30,40] [60,70]
  ↑
 键数不足，兄弟也不够，合并
```

## B+树（B树的改进）

B+树是B树的变种，更常用于数据库索引：

### B+树特点

1. **所有数据都在叶子节点**，内部节点只存键
2. **叶子节点形成链表**，支持范围查询
3. **内部节点更小**，可以容纳更多键，树更矮

```
B树:                    B+树:

    [20, 50]               [20, 50]
   /   |    \             /   |    \
[10:1] [30:2] [60:3]   [20]  [50]  [∞]
 数据在内部和叶子        / \   /  \
                       ... 所有数据在叶子
                            叶子间有指针连接
```

### B+树优势

- **范围查询快**：顺序扫描叶子链表
- **树更矮**：内部节点不存数据，分支因子更大
- **缓存友好**：热点数据在内部节点，常驻内存

## 复杂度分析

| 操作 | 时间复杂度 | 磁盘I/O |
|------|-----------|---------|
| 查找 | $O(\log_M n)$ | $O(\log_M n)$ |
| 插入 | $O(\log_M n)$ | $O(\log_M n)$ |
| 删除 | $O(\log_M n)$ | $O(\log_M n)$ |
| 范围查询 | $O(\log_M n + k)$ | $O(\log_M n + k/M)$ |

其中：
- $M$：阶数（通常 100~1000）
- $k$：范围内键的数量

### 为什么 $O(\log_M n)$ 比 $O(\log_2 n)$ 好？

```
假设 n = 1,000,000,000 (10亿)

二叉树 (M=2):
高度 ≈ log₂(10^9) ≈ 30
磁盘访问: 30次

B树 (M=1000):
高度 ≈ log₁₀₀₀(10^9) ≈ 3
磁盘访问: 3次

B树快10倍！
```

## B树 vs B+树 vs LSM树

| 特性 | B树 | B+树 | LSM树 |
|------|-----|------|-------|
| 读性能 | 好 | 很好 | 一般 |
| 写性能 | 一般 | 一般 | 很好 |
| 范围查询 | 一般 | 很好 | 好 |
| 空间放大 | 小 | 小 | 大 |
| 写放大 | 大 | 大 | 小 |
| 适用 | 通用 | 数据库索引 | 写入密集 |

## 实际应用

### 1. MySQL InnoDB

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

-- 主键索引是聚簇B+树索引
-- 叶子节点存储完整行数据
```

### 2. PostgreSQL

使用B树作为默认索引类型。

```sql
CREATE INDEX idx_name ON users(name);
-- 默认使用B树
```

### 3. 文件系统

- **NTFS**：MFT（Master File Table）使用B+树
- **ext4**：目录使用HTree（B树变种）
- **HFS+**：目录使用B树

## 面试要点

### Q1: B树 vs 红黑树

| B树 | 红黑树 |
|-----|--------|
| 多路 | 二叉 |
| 磁盘优化 | 内存优化 |
| 节点大（4KB） | 节点小 |
| 高度低 | 高度高 |
| 适合大数据量 | 适合内存数据 |

### Q2: 为什么数据库索引用B+树不用哈希？

- **哈希**：只支持等值查询 $O(1)$
- **B+树**：支持范围查询、排序、前缀匹配 $O(\log n)$
- 数据库需要范围查询能力

### Q3: B树高度计算

```
M=1000, n=1,000,000,000

最小高度: log₁₀₀₀(10^9) = 3
最大高度: log₅₀₀(10^9) ≈ 3.3

实际高度: 3-4层
```

### Q4: B树分裂和合并的触发条件

- **分裂**：节点键数 = M-1（满）
- **合并**：节点键数 = ⌈M/2⌉ - 1（低于最小值）

## 相关概念

- [红黑树](../data-structures/red-black-tree.md) - 内存平衡树
- [AVL树](../data-structures/avl-tree.md) - 严格平衡二叉树
- [哈希表](../data-structures/hash-table.md) - 等值查询结构
- [数据库索引](../databases/indexing.md) - B+树的应用
- [LSM树](https://en.wikipedia.org/wiki/Log-structured_merge-tree) - 写优化结构

## 参考资料

1. 《算法导论》第18章 - B树
2. 《数据库系统概念》Silberschatz
3. B-tree - Wikipedia
4. MySQL Internals Manual - InnoDB B+树
