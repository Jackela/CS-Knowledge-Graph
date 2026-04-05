# 字符串匹配 (String Matching)

## 简介

**字符串匹配（String Matching）**是在一个文本（Text）中查找一个模式（Pattern）出现位置的问题。这是计算机科学中最基础的问题之一，在文本编辑、搜索引擎、DNA序列分析、网络安全等领域有广泛应用。

```
文本:    "ABABDABACDABABCABAB"
模式:    "ABABCABAB"

匹配位置: 索引 10

ABABDABACDABABCABAB
          ABABCABAB  ← 匹配成功
```

## 经典算法

### 1. 暴力算法（Naive）

逐个位置比较。

```python
def naive_search(text, pattern):
    """暴力字符串匹配"""
    n, m = len(text), len(pattern)
    positions = []
    
    for i in range(n - m + 1):
        j = 0
        while j < m and text[i + j] == pattern[j]:
            j += 1
        if j == m:
            positions.append(i)
    
    return positions
```

**时间复杂度**：$O(nm)$

### 2. KMP算法

利用已匹配信息，避免重复比较。

```python
def kmp_search(text, pattern):
    """KMP字符串匹配"""
    n, m = len(text), len(pattern)
    
    # 构建前缀函数（部分匹配表）
    def build_lps(pattern):
        lps = [0] * m
        length = 0
        i = 1
        
        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps
    
    lps = build_lps(pattern)
    positions = []
    i = j = 0
    
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            
            if j == m:
                positions.append(i - j)
                j = lps[j - 1]
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return positions
```

**时间复杂度**：$O(n + m)$

### 3. Rabin-Karp算法

使用滚动哈希。

```python
def rabin_karp(text, pattern, prime=101):
    """Rabin-Karp字符串匹配"""
    n, m = len(text), len(pattern)
    d = 256  # 字符集大小
    h = pow(d, m - 1) % prime
    
    pattern_hash = 0
    text_hash = 0
    
    # 计算初始哈希值
    for i in range(m):
        pattern_hash = (d * pattern_hash + ord(pattern[i])) % prime
        text_hash = (d * text_hash + ord(text[i])) % prime
    
    positions = []
    
    for i in range(n - m + 1):
        if pattern_hash == text_hash:
            # 验证
            if text[i:i+m] == pattern:
                positions.append(i)
        
        # 滚动哈希
        if i < n - m:
            text_hash = (d * (text_hash - ord(text[i]) * h) + ord(text[i + m])) % prime
            if text_hash < 0:
                text_hash += prime
    
    return positions
```

**时间复杂度**：$O(n + m)$ 平均，最坏 $O(nm)$

## 算法对比

| 算法 | 预处理 | 匹配时间 | 空间 | 特点 |
|------|--------|---------|------|------|
| 暴力 | 无 | $O(nm)$ | $O(1)$ | 简单 |
| KMP | $O(m)$ | $O(n)$ | $O(m)$ | 无回退，确定性强 |
| Rabin-Karp | $O(m)$ | $O(n+m)$平均 | $O(1)$ | 适合多模式匹配 |

## 应用场景

1. **文本编辑器**：查找替换功能
2. **搜索引擎**：关键词匹配
3. **DNA测序**：基因序列分析
4. **入侵检测**：网络流量模式匹配

## 相关概念

### 数据结构
- [数组](../data-structures/array.md) - 字符串的存储基础
- [哈希表](../data-structures/hash-table.md) - Rabin-Karp算法的核心
- [Trie树](../data-structures/trie.md) - 多模式字符串匹配

### 算法
- [KMP算法](#2-kmp算法) - 经典字符串匹配
- [Rabin-Karp算法](#3-rabin-karp算法) - 哈希-based匹配
- [动态规划](../algorithms/dynamic-programming.md) - 编辑距离等变种问题

### 复杂度分析
- [时间复杂度分析](../../references/time-complexity.md) - $O(nm)$ vs $O(n+m)$
- [空间复杂度](../../references/space-complexity.md) - 前缀数组存储

### 系统实现
- [网络](../networks/transport-layer.md) - 入侵检测系统中的应用
- [Web安全](../../security/web-security.md) - 输入验证与过滤

- [正则表达式](https://en.wikipedia.org/wiki/Regular_expression) - 复杂模式匹配

## 参考资料

1. 《算法导论》第32章 - 字符串匹配
2. String-searching algorithm - Wikipedia
