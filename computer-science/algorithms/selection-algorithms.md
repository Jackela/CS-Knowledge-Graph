# 选择算法 (Selection Algorithms)

## 简介
选择算法用于在无序序列中找到第k小的元素，或求解中位数问题。与排序不同，选择算法的目标是最小化时间复杂度，理想情况下达到线性时间O(n)。

## 核心概念
- **QuickSelect**：基于快速排序的分区思想，平均时间复杂度O(n)，最坏情况O(n²)
- **Median of Medians**：通过递归选择中位数的中位数作为枢轴，保证最坏情况O(n)
- **分区策略**：将数组分为小于枢轴、等于枢轴、大于枢轴三部分
- **递归选择**：根据k与枢轴位置的关系，决定递归左半部分或右半部分

## 实现方式

### QuickSelect算法
```python
def quick_select(arr, left, right, k):
    """
    在arr[left:right+1]范围内查找第k小的元素（0-based）
    平均时间复杂度: O(n), 最坏情况: O(n²)
    """
    if left == right:
        return arr[left]
    
    # 随机选择枢轴避免最坏情况
    pivot_idx = partition(arr, left, right)
    
    if k == pivot_idx:
        return arr[k]
    elif k < pivot_idx:
        return quick_select(arr, left, pivot_idx - 1, k)
    else:
        return quick_select(arr, pivot_idx + 1, right, k)

def partition(arr, left, right):
    """Lomuto分区方案"""
    pivot = arr[right]
    i = left
    for j in range(left, right):
        if arr[j] <= pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[right] = arr[right], arr[i]
    return i
```

### Median of Medians算法
```python
def median_of_medians(arr, k):
    """
    最坏情况下O(n)的选择算法
    通过选择中位数的中位数作为枢轴保证性能
    """
    if len(arr) <= 5:
        return sorted(arr)[k]
    
    # 将数组分为每组5个元素，找出每组的中位数
    chunks = [arr[i:i+5] for i in range(0, len(arr), 5)]
    medians = [sorted(chunk)[len(chunk)//2] for chunk in chunks]
    
    # 递归找出中位数的中位数
    pivot = median_of_medians(medians, len(medians)//2)
    
    # 根据枢轴分区
    lows = [x for x in arr if x < pivot]
    highs = [x for x in arr if x > pivot]
    pivots = [x for x in arr if x == pivot]
    
    if k < len(lows):
        return median_of_medians(lows, k)
    elif k < len(lows) + len(pivots):
        return pivot
    else:
        return median_of_medians(highs, k - len(lows) - len(pivots))
```

## 应用场景
- **快速查找中位数**：在流式数据中找到中位数而不需要完全排序
- **Top-K问题**：找到前K大或前K小的元素
- **统计计算**：计算百分位数、四分位数等统计量
- **负载均衡**：分布式系统中选择合适的中位数节点

## 面试要点
1. **Q**: QuickSelect与排序后选择的时间复杂度差异？
   **A**: QuickSelect平均O(n)，排序需要O(n log n)。选择算法避免了不必要的全排序，只处理包含目标元素的分区。

2. **Q**: 如何避免QuickSelect的最坏情况O(n²)？
   **A**: 使用随机化选择枢轴，或采用Median of Medians方法选择枢轴，保证每次至少淘汰30%的元素。

3. **Q**: Median of Medians的时间复杂度证明思路？
   **A**: 递归式T(n) ≤ T(n/5) + T(7n/10) + O(n)，其中T(n/5)是找中位数的中位数，T(7n/10)是递归处理的最大分区，可证明为O(n)。

4. **Q**: 如何在O(n)时间内找到两个有序数组的中位数？
   **A**: 使用二分查找思想，每次比较两个数组的中位数，排除不可能包含目标的一半，时间复杂度O(log(m+n))。

## 相关概念

### 数据结构
- [数组](../data-structures/array.md) - 选择算法的基础存储结构
- [堆](../data-structures/heap.md) - 可用于堆选择算法

### 算法
- [快速排序](./quick-sort.md) - QuickSelect基于相同的分区思想
- [二分查找](./binary-search.md) - 有序数组选择的优化方法

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 线性时间O(n)的严格证明

### 系统实现
- [分布式系统](../systems/distributed-systems.md) - 分布式选择算法的实现挑战
