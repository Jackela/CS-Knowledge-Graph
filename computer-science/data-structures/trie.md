# Trie树 (Prefix Tree)

## 简介

**Trie树**（发音同 "try"），又称**前缀树（Prefix Tree）**或**字典树**，是一种专门用于**字符串存储和查找**的树形数据结构。它利用字符串的公共前缀来减少查询时间，最大限度地减少无谓的字符串比较。

```
存储: "cat", "car", "dog", "door"

              root
            /      \
           c        d
          /          \
         a            o
        / \          / \
       t   r        g   o
                        |
                        r

查找 "car":
root → c → a → r ✓ (3步)

查找 "cab":
root → c → a → ? ✗ (b不存在，2步即可确定不存在)
```

Trie树在 $O(m)$ 时间内完成字符串查找，其中 $m$ 为字符串长度，与存储的字符串数量无关。

## 原理 (Principles)

### 核心思想

- **边存储字符**：从父节点到子节点的边代表一个字符
- **路径表示字符串**：从根到某节点的路径上的字符连起来构成字符串
- **节点标记结束**：表示某个字符串在此结束

```
存储 "a", "to", "tea", "ted", "ten", "i", "in", "inn"

                    root
                   /  |  \
                  a   t   i
                  |   |   |
                  $   e   n
                     /|\   |
                    a d n  $
                    | | |  |
                    $ $ $  n
                           |
                           $

$ 表示字符串结束标记

路径 root→t→e→a 表示 "tea"
路径 root→t→e→d 表示 "ted"
```

### Trie 节点结构

```python
class TrieNode:
    def __init__(self):
        self.children = {}  # 字符 -> TrieNode 的映射
        self.is_end = False  # 是否有字符串在此结束
        self.count = 0       # 经过此节点的字符串数（可选）
```

## 操作详解

### 1. 插入

```python
def insert(self, word):
    """插入一个单词"""
    node = self.root
    for char in word:
        if char not in node.children:
            node.children[char] = TrieNode()
        node = node.children[char]
        node.count += 1  # 统计
    node.is_end = True
```

### 2. 查找

```python
def search(self, word):
    """查找完整单词"""
    node = self.root
    for char in word:
        if char not in node.children:
            return False
        node = node.children[char]
    return node.is_end
```

### 3. 前缀匹配

```python
def starts_with(self, prefix):
    """是否有单词以prefix开头"""
    node = self.root
    for char in prefix:
        if char not in node.children:
            return False
        node = node.children[char]
    return True
```

## 复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| 插入 | $O(m)$ | $O(m)$ |
| 查找 | $O(m)$ | $O(1)$ |
| 前缀匹配 | $O(m)$ | $O(1)$ |

其中 $m$ 为字符串长度。

## 应用场景

1. **自动补全（Autocomplete）**
2. **拼写检查**
3. **IP路由查找**（最长前缀匹配）
4. **词频统计**

## 相关概念

### 数据结构
- [二叉树](./binary-tree.md) - 树的特例形式
- [树](./tree.md) - Trie的通用性质
- [哈希表](./hash-table.md) - 另一种快速查找结构
- [前缀树](./trie.md) - 本文主题

### 算法
- [字符串匹配](../algorithms/string-matching.md) - KMP、Rabin-Karp等算法
- [图遍历](../algorithms/graph-traversal.md) - Trie的遍历
- [动态规划](../algorithms/dynamic-programming.md) - 字符串DP问题

### 复杂度分析
- [时间复杂度分析](../../references/time-complexity.md) - $O(m)$查找效率
- [空间复杂度](../../references/space-complexity.md) - 节点存储开销

### 系统实现
- [网络](../networks/network-layer.md) - IP路由最长前缀匹配
- [DNS](../networks/dns.md) - 域名解析的前缀查找
- [数据库](../databases/indexing.md) - 前缀索引


## 参考资料

1. Trie - Wikipedia
2. LeetCode Trie 专题
