# 排序算法 (Sorting Algorithms)

## 简介

**排序（Sorting）**是将一组数据按照特定顺序（通常是升序或降序）重新排列的算法。排序是计算机科学中最基础、最重要的算法之一，广泛应用于数据库查询、数据分析、信息检索等领域。

排序算法通常基于[数组](../data-structures/array.md)实现，利用数组的随机访问特性高效地交换和比较元素。

```
未排序: [64, 34, 25, 12, 22, 11, 90]
排序后: [11, 12, 22, 25, 34, 64, 90]
```

## 常见排序算法

### 1. 快速排序 (Quick Sort)

**思想**：选择基准元素，将数组划分为小于基准和大于基准的两部分，递归排序。

```python
def quick_sort(arr):
    """快速排序"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)
```

**复杂度**：
- 平均时间：$O(n \log n)$
- 最坏时间：$O(n^2)$
- 空间：$O(\log n)$（递归栈）

### 2. 归并排序 (Merge Sort)

**思想**：将数组分成两半，分别排序后合并。

```python
def merge_sort(arr):
    """归并排序"""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    """合并两个有序数组"""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

**复杂度**：
- 时间：$O(n \log n)$（稳定）
- 空间：$O(n)$

### 3. 堆排序 (Heap Sort)

**思想**：利用[堆](../data-structures/heap.md)数据结构，反复提取最大/最小元素。

```python
def heap_sort(arr):
    """堆排序"""
    import heapq
    heapq.heapify(arr)
    return [heapq.heappop(arr) for _ in range(len(arr))]
```

**复杂度**：
- 时间：$O(n \log n)$
- 空间：$O(1)$（原地排序）

### 4. 其他排序算法

| 算法 | 平均时间 | 最坏时间 | 空间 | 稳定性 |
|------|----------|----------|------|--------|
| 冒泡排序 | $O(n^2)$ | $O(n^2)$ | $O(1)$ | 稳定 |
| 选择排序 | $O(n^2)$ | $O(n^2)$ | $O(1)$ | 不稳定 |
| 插入排序 | $O(n^2)$ | $O(n^2)$ | $O(1)$ | 稳定 |
| 希尔排序 | $O(n^{1.3})$ | $O(n^2)$ | $O(1)$ | 不稳定 |
| 计数排序 | $O(n + k)$ | $O(n + k)$ | $O(k)$ | 稳定 |
| 桶排序 | $O(n + k)$ | $O(n^2)$ | $O(n + k)$ | 稳定 |
| 基数排序 | $O(d(n + k))$ | $O(d(n + k))$ | $O(n + k)$ | 稳定 |

## 算法选择指南

| 场景 | 推荐算法 |
|------|----------|
| 通用场景 | 快速排序 |
| 需要稳定性 | 归并排序、插入排序 |
| 内存受限 | 堆排序 |
| 数据范围小 | 计数排序、基数排序 |
| 近乎有序 | 插入排序 |

## 排序算法的应用

1. **数据库查询优化**：ORDER BY 子句依赖排序
2. **二分查找前提**：必须先排序才能使用二分查找
3. **去重统计**：排序后相同元素相邻，便于去重
4. **选择问题**：快速选择算法基于快速排序

## 相关概念 (Related Concepts)

### 数据结构
- ：排序的基础数据结构
- ：堆排序的数据结构基础
- [链表](../data-structures/linked-list.md)：链表排序实现

### 算法
- [二分查找](./binary-search.md)：依赖有序数据的前提
- [分治算法](./divide-conquer.md)：归并排序与快排的分治思想
- [图遍历](./graph-traversal.md)：拓扑排序等图排序算法

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：排序算法的时间效率分析
- [空间复杂度](../../references/space-complexity.md)：排序算法的空间开销评估


## 参考资料

1. 《算法导论》第6-8章 - 排序算法
2. Sorting algorithm - Wikipedia
3. 《数据结构与算法分析》
