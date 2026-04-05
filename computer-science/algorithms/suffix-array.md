# 后缀数组 (Suffix Array)

## 简介
后缀数组是将字符串的所有后缀按字典序排序后得到的数组。它是一个强大的字符串处理工具，可用于解决最长公共子串、最长重复子串、字符串匹配等问题。

## 核心概念
- **后缀数组SA**：SA[i]表示字典序第i小的后缀的起始位置
- **排名数组Rank**：Rank[i]表示从位置i开始的后缀的排名
- **高度数组LCP**：LCP[i]表示SA[i]和SA[i-1]的最长公共前缀长度
- **倍增算法**：按2^k长度排序，利用上一次结果加速

## 实现方式

### SA-IS算法（线性时间）
```python
def sa_is(s, alphabet_size=256):
    """
    SA-IS算法：线性时间构造后缀数组
    将字符分为L型（后缀>下一个后缀）和S型（后缀<下一个后缀）
    时间复杂度: O(n)
    """
    n = len(s)
    if n == 0:
        return []
    if n == 1:
        return [0]
    
    # 类型数组：True表示S型，False表示L型
    is_s = [False] * (n + 1)
    is_s[n] = True  # 哨兵是S型
    
    for i in range(n - 2, -1, -1):
        if s[i] < s[i + 1]:
            is_s[i] = True
        elif s[i] > s[i + 1]:
            is_s[i] = False
        else:
            is_s[i] = is_s[i + 1]
    
    # 寻找LMS（Left-Most-S）位置
    is_lms = [False] * (n + 1)
    for i in range(1, n + 1):
        is_lms[i] = is_s[i] and not is_s[i - 1]
    
    def induced_sort(lms_positions):
        """诱导排序"""
        sa = [-1] * (n + 1)
        
        # 计数排序初始化
        count = [0] * alphabet_size
        for c in s:
            count[c] += 1
        for i in range(1, alphabet_size):
            count[i] += count[i - 1]
        
        # L型从左到右填（按计数数组）
        buf = count[:]
        sa[0] = n  # 哨兵
        for d in reversed(lms_positions):
            if d > 0:
                c = s[d - 1]
                if not is_s[d - 1]:  # L型
                    buf[c] -= 1
                    sa[buf[c]] = d - 1
        
        # S型从右到左填
        buf = count[:]
        for i in range(n, -1, -1):
            d = sa[i] - 1 if sa[i] > 0 else -1
            if d >= 0 and is_s[d]:
                buf[s[d]] -= 1
                sa[buf[s[d]]] = d
        
        return sa
    
    # 初始LMS排序（粗略排序）
    lms_positions = [i for i in range(n + 1) if is_lms[i]]
    sa = induced_sort(lms_positions)
    
    # 给LMS子串编号
    def name_substrings():
        names = [-1] * (n + 1)
        names[n] = 0
        prev_lms = n
        count = 0
        
        for i in range(1, n + 1):
            d = sa[i]
            if is_lms[d]:
                if not lms_equal(prev_lms, d):
                    count += 1
                names[d] = count
                prev_lms = d
        
        return names, count + 1
    
    def lms_equal(i, j):
        """判断两个LMS子串是否相等"""
        while True:
            if s[i] != s[j]:
                return False
            i, j = i + 1, j + 1
            if is_lms[i] != is_lms[j]:
                return False
            if is_lms[i]:
                return s[i] == s[j]
    
    names, num_names = name_substrings()
    
    # 递归处理缩减后的字符串
    if num_names < len(lms_positions):
        # 构建缩减字符串
        reduced_s = [names[p] for p in lms_positions]
        reduced_sa = sa_is(reduced_s, num_names)
        
        # 根据递归结果重新排序LMS
        lms_positions = [lms_positions[i] for i in reduced_sa]
    
    # 最终诱导排序
    return induced_sort(lms_positions)
```

### DC3/Skew算法（线性时间）
```python
def dc3_suffix_array(s):
    """
    DC3/Skew算法：分治构造后缀数组
    将位置按模3分类，递归处理模0和模1的位置
    时间复杂度: O(n)
    """
    n = len(s)
    if n < 3:
        return sorted(range(n), key=lambda i: s[i:])
    
    # 将字符映射到整数（保证>0）
    s = [ord(c) for c in s] + [0, 0, 0]
    
    def sort_triples(triples, max_val):
        """对三元组进行基数排序"""
        # 基数排序实现
        sorted_triples = sorted(triples, key=lambda x: (s[x], s[x+1], s[x+2]))
        return sorted_triples
    
    # 收集模1和模2的位置
    positions_12 = [i for i in range(n) if i % 3 != 0]
    
    # 对三元组排序并编号
    sorted_pos = sort_triples(positions_12, max(s) + 1)
    
    # 给三元组分配排名
    rank = {}
    current_rank = 1
    for pos in sorted_pos:
        triple = (s[pos], s[pos+1], s[pos+2])
        if triple not in rank:
            rank[triple] = current_rank
            current_rank += 1
    
    # 构建缩减字符串
    s12 = [rank[(s[i], s[i+1], s[i+2])] for i in positions_12]
    
    # 递归求解（如果排名不唯一）
    if current_rank <= len(positions_12):
        sa12 = dc3_suffix_array(s12)
    else:
        sa12 = list(range(len(s12)))
    
    # 将递归结果映射回原位置
    sa12 = [positions_12[i] for i in sa12]
    
    # 对模0位置排序（利用SA12）
    positions_0 = [i for i in range(n) if i % 3 == 0]
    # 使用SA12中的信息对positions_0进行排序
    sa0 = sorted(positions_0, key=lambda x: (s[x], sa12.index(x+1) if x+1 < n else -1))
    
    # 合并SA0和SA12
    def merge():
        result = []
        i = j = 0
        while i < len(sa0) and j < len(sa12):
            p0, p12 = sa0[i], sa12[j]
            # 比较后缀
            if s[p0:p0+3] < s[p12:p12+3]:
                result.append(p0)
                i += 1
            else:
                result.append(p12)
                j += 1
        result.extend(sa0[i:])
        result.extend(sa12[j:])
        return result
    
    return merge()
```

### LCP数组计算
```python
def build_lcp(s, sa):
    """
     Kasai算法：线性时间计算LCP数组
    LCP[i] = 后缀SA[i]与SA[i-1]的最长公共前缀
    """
    n = len(s)
    rank = [0] * n
    for i, pos in enumerate(sa):
        rank[pos] = i
    
    lcp = [0] * n
    k = 0
    
    for i in range(n):
        if rank[i] == 0:
            k = 0
            continue
        
        j = sa[rank[i] - 1]
        while i + k < n and j + k < n and s[i + k] == s[j + k]:
            k += 1
        
        lcp[rank[i]] = k
        if k > 0:
            k -= 1
    
    return lcp
```

## 应用场景
- **最长公共子串**：两个字符串的LCS查询
- **最长重复子串**：LCP数组中的最大值
- **字符串匹配**：模式串在后缀数组中二分查找
- **后缀树构建**：后缀数组+LCP可线性构造后缀树

## 面试要点
1. **Q**: 后缀数组与后缀树的关系？
   **A**: 后缀数组是后缀树的后序遍历结果，结合LCP数组可以在O(n)时间内从后缀数组构造后缀树。后缀数组空间更省，常数更小。

2. **Q**: 如何用后缀数组解决最长公共子串问题？
   **A**: 将两个字符串用特殊分隔符连接，构造后缀数组。在LCP数组中，来自不同字符串的后缀间的最大LCP即为答案。

3. **Q**: SA-IS算法中LMS和诱导排序的作用？
   **A**: LMS（Left-Most S-type）是S型后缀的左边界，是关键的采样点。诱导排序利用已排序的LMS位置，通过L型和S型的依赖关系，线性时间完成整体排序。

4. **Q**: 后缀数组二分查找的时间复杂度？
   **A**: 单次查询O(|P| log n)，其中|P|是模式串长度。可结合LCP数组优化到O(|P| + log n)。若预处理RMQ，可做到O(|P|)。

## 相关概念

### 数据结构
- [数组](../data-structures/array.md) - 后缀数组的基础存储
- [字符串](../data-structures/string.md) - 后缀数组处理的对象

### 算法
- [字符串匹配](./string-matching.md) - 后缀数组的应用场景
- [基数排序](./radix-sort.md) - 构造后缀数组的基础排序算法

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 线性时间构造算法的分析

### 系统实现
- [搜索引擎](../systems/search-engine.md) - 后缀数组在全文检索中的应用
