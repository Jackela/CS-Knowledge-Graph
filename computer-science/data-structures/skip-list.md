# 跳表 (Skip List)

## 简介
**跳表**是一种概率性平衡数据结构，通过在有序链表上增加多级索引，实现类似二分查找的效率。它以简单的链表结构提供 $O(\log n)$ 的期望查找时间，是平衡树的一种替代实现，常用于Redis的有序集合（Sorted Set）。

## 核心概念
- **多层索引**：在基础有序链表之上建立多级"快速通道"，上层稀疏下层密集
- **概率性平衡**：通过随机函数决定节点层数，期望保持平衡性质
- **前进指针**：每个节点包含多个指针，指向同层下一个节点
- **简单高效**：相比红黑树、AVL树，实现更简单，常数更小

## 实现方式
```python
import random

class SkipListNode:
    def __init__(self, val, level):
        self.val = val
        self.forward = [None] * level  # 前进指针数组

class SkipList:
    def __init__(self, max_level=16, p=0.5):
        self.max_level = max_level      # 最大层数
        self.p = p                      # 晋升概率
        self.head = SkipListNode(-1, max_level)
        self.level = 1                  # 当前层数
    
    def random_level(self):
        """随机生成节点层数"""
        level = 1
        while random.random() < self.p and level < self.max_level:
            level += 1
        return level
    
    def search(self, target):
        """查找目标值是否存在"""
        curr = self.head
        # 从最高层开始查找
        for i in range(self.level - 1, -1, -1):
            while curr.forward[i] and curr.forward[i].val < target:
                curr = curr.forward[i]
        curr = curr.forward[0]
        return curr is not None and curr.val == target
    
    def insert(self, num):
        """插入新元素"""
        update = [None] * self.max_level
        curr = self.head
        
        # 找到各层插入位置
        for i in range(self.level - 1, -1, -1):
            while curr.forward[i] and curr.forward[i].val < num:
                curr = curr.forward[i]
            update[i] = curr
        
        # 生成随机层数
        new_level = self.random_level()
        if new_level > self.level:
            for i in range(self.level, new_level):
                update[i] = self.head
            self.level = new_level
        
        # 创建新节点并插入
        new_node = SkipListNode(num, new_level)
        for i in range(new_level):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node
    
    def delete(self, num):
        """删除元素"""
        update = [None] * self.max_level
        curr = self.head
        
        for i in range(self.level - 1, -1, -1):
            while curr.forward[i] and curr.forward[i].val < num:
                curr = curr.forward[i]
            update[i] = curr
        
        target = curr.forward[0]
        if target is None or target.val != num:
            return False
        
        # 在各层删除节点
        for i in range(self.level):
            if update[i].forward[i] != target:
                break
            update[i].forward[i] = target.forward[i]
        
        # 更新当前层数
        while self.level > 1 and self.head.forward[self.level - 1] is None:
            self.level -= 1
        return True
    
    def display(self):
        """打印跳表结构"""
        for i in range(self.level - 1, -1, -1):
            curr = self.head.forward[i]
            level_str = f"Level {i}: "
            while curr:
                level_str += str(curr.val) + " -> "
                curr = curr.forward[i]
            print(level_str + "None")

# 使用示例
skiplist = SkipList()
for val in [3, 6, 7, 9, 12, 17, 19, 21, 25, 26]:
    skiplist.insert(val)

skiplist.display()
print(f"Search 17: {skiplist.search(17)}")   # True
print(f"Search 15: {skiplist.search(15)}")   # False
```

## 应用场景
- **Redis有序集合**：Redis的ZSet底层使用跳表实现
- **LevelDB存储引擎**：内部使用跳表作为MemTable的实现
- **有序集合维护**：需要频繁插入、删除、查找的有序数据
- **排行榜系统**：实时维护用户排名，支持范围查询

## 面试要点
1. **Q: 跳表的查询复杂度是多少？为什么是期望复杂度？**
   A: 跳表的期望查询复杂度为 $O(\log n)$。因为节点层数通过随机函数生成，第k层节点的期望数量是 $n \times p^k$。从概率角度分析，期望查找路径长度与 $\log n$ 成正比。

2. **Q: 跳表和红黑树/AVL树的比较？**
   A: 跳表实现更简单，无需复杂的旋转操作；常数较小，缓存友好；支持高效的范围查询。但跳表是概率性平衡，最坏情况 $O(n)$，而平衡树是确定性 $O(\log n)$。

3. **Q: 为什么Redis选择跳表而不是红黑树？**
   A: 跳表实现简单、代码量少；范围查询效率高（可以直接遍历Level 0链表）；插入删除不需要旋转调整；支持按照rank获取元素，适合排行榜场景。

4. **Q: 跳表的空间复杂度是多少？**
   A: 空间复杂度为 $O(n)$。每个节点平均有 $1/(1-p)$ 个指针，当 $p=0.5$ 时，平均每个节点有2个指针，空间开销约为普通链表的两倍。

## 相关概念

### 数据结构
- [链表](./linked-list.md) - 跳表的基础结构
- [红黑树](./red-black-tree.md) - 跳表的替代方案
- [AVL树](./avl-tree.md) - 严格平衡的二叉搜索树

### 算法
- [二分查找](../algorithms/binary-search.md) - 跳表模拟二分查找思想
- [排序算法](../algorithms/sorting.md) - 维护有序性

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 期望 $O(\log n)$

### 系统实现
- [Redis有序集合](../systems/redis.md) - 跳表的实际应用
