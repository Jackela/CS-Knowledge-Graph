# 分治算法 (Divide and Conquer)

分治算法（Divide and Conquer）是一种重要的算法设计范式，将问题分解为若干个规模较小的子问题，递归解决子问题，然后合并子问题的解得到原问题的解。

## 原理

### 分治三部曲

1. **分解**（Divide）：将原问题分解为若干个子问题
2. **解决**（Conquer）：递归地解决子问题
3. **合并**（Combine）：将子问题的解合并为原问题的解

### 算法框架

```
function divide_and_conquer(问题):
    if 问题规模足够小:
        return 直接求解(问题)
    
    子问题1, 子问题2, ... = 分解(问题)
    
    解1 = divide_and_conquer(子问题1)
    解2 = divide_and_conquer(子问题2)
    ...
    
    return 合并(解1, 解2, ...)
```

## 复杂度分析

### 主定理 (Master Theorem)

对于形如 `T(n) = aT(n/b) + f(n)` 的递归式：

- **情况1**：若 `f(n) = O(n^c)` 且 `c < log_b(a)`，则 `T(n) = Θ(n^(log_b(a)))`
- **情况2**：若 `f(n) = Θ(n^(log_b(a)))`，则 `T(n) = Θ(n^(log_b(a)) * log n)`
- **情况3**：若 `f(n) = Ω(n^c)` 且 `c > log_b(a)`，则 `T(n) = Θ(f(n))`

### 常见复杂度

| 算法 | 递推式 | 复杂度 |
|------|--------|--------|
| 归并排序 | T(n) = 2T(n/2) + O(n) | O(n log n) |
| 快速排序(平均) | T(n) = 2T(n/2) + O(n) | O(n log n) |
| 二分查找 | T(n) = T(n/2) + O(1) | O(log n) |
| 二分搜索树 | T(n) = 2T(n/2) + O(1) | O(n) |

## 实现示例

### 归并排序

```python
def merge_sort(arr):
    """归并排序 - 经典分治算法"""
    if len(arr) <= 1:
        return arr
    
    # 分解
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    # 合并
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

# 示例
arr = [64, 34, 25, 12, 22, 11, 90]
sorted_arr = merge_sort(arr)
print(f"排序结果: {sorted_arr}")
```

### 快速排序

```python
def quick_sort(arr, low=0, high=None):
    """快速排序 - 原地分治"""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        # 分区
        pivot_idx = partition(arr, low, high)
        
        # 递归排序
        quick_sort(arr, low, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, high)
    
    return arr

def partition(arr, low, high):
    """分区操作"""
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# 示例
arr = [64, 34, 25, 12, 22, 11, 90]
quick_sort(arr)
print(f"排序结果: {arr}")
```

### 二分查找

```python
def binary_search(arr, target):
    """二分查找 - 分治思想"""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# 示例
arr = [1, 3, 5, 7, 9, 11, 13, 15]
target = 7
idx = binary_search(arr, target)
print(f"目标 {target} 在索引 {idx}")
```

### 计算逆序对数量

```python
def count_inversions(arr):
    """
    计算数组中的逆序对数量
    逆序对：i < j 且 arr[i] > arr[j]
    """
    if len(arr) <= 1:
        return 0, arr
    
    mid = len(arr) // 2
    left_count, left = count_inversions(arr[:mid])
    right_count, right = count_inversions(arr[mid:])
    merge_count, merged = merge_and_count(left, right)
    
    return left_count + right_count + merge_count, merged

def merge_and_count(left, right):
    """合并并计算跨区逆序对"""
    result = []
    count = 0
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            # left[i:] 都大于 right[j]，形成逆序对
            count += len(left) - i
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return count, result

# 示例
arr = [1, 20, 6, 4, 5]
count, _ = count_inversions(arr)
print(f"逆序对数量: {count}")  # 5
```

### 最近点对问题

```python
import math

def closest_pair(points):
    """
    平面最近点对问题
    points: [(x, y), ...]
    """
    # 按x坐标排序
    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])
    
    return closest_pair_recursive(px, py)

def closest_pair_recursive(px, py):
    n = len(px)
    
    # 基本情况
    if n <= 3:
        return brute_force(px)
    
    # 分解
    mid = n // 2
    mid_point = px[mid]
    
    # 分割py
    pyl = [p for p in py if p[0] <= mid_point[0]]
    pyr = [p for p in py if p[0] > mid_point[0]]
    
    # 递归求解
    dl = closest_pair_recursive(px[:mid], pyl)
    dr = closest_pair_recursive(px[mid:], pyr)
    d = min(dl, dr)
    
    # 合并 - 检查跨中线的点对
    strip = [p for p in py if abs(p[0] - mid_point[0]) < d]
    
    for i in range(len(strip)):
        # 只需检查后面最多7个点
        for j in range(i + 1, min(i + 8, len(strip))):
            d = min(d, distance(strip[i], strip[j]))
    
    return d

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def brute_force(points):
    min_dist = float('inf')
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            min_dist = min(min_dist, distance(points[i], points[j]))
    return min_dist

# 示例
points = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
dist = closest_pair(points)
print(f"最近点对距离: {dist:.2f}")
```

## 应用场景

| 应用场景 | 算法 | 说明 |
|----------|------|------|
| **排序** | 归并排序、快速排序 | O(n log n) 排序 |
| **查找** | 二分查找 | O(log n) 查找 |
| **几何** | 最近点对、凸包 | 计算几何问题 |
| **大整数** | Karatsuba乘法 | 快速乘法算法 |
| **矩阵** | Strassen矩阵乘法 | 快速矩阵乘法 |
| **选择** | 快速选择 | 第k小元素 |

## 面试要点

**Q1: 分治和动态规划的区别？**
> - 分治：子问题独立，不重叠
> - DP：子问题重叠，需要记忆化
> - 分治通常递归，DP可递归或迭代

**Q2: 什么时候使用分治？**
> - 问题可分解为相似子问题
> - 子问题相互独立
> - 子问题解可合并为原问题解
> - 有明确的基本情况

**Q3: 快速排序最坏情况如何避免？**
> - 最坏情况：O(n²) 当数组已排序
> - 随机选择pivot
> - 三数取中法
> - 当子数组较小时切换插入排序

**Q4: 归并排序和快排的区别？**
> - 归并：稳定，O(n log n) 保证，需要O(n)额外空间
> - 快排：不稳定，平均O(n log n)，最坏O(n²)，原地排序
> - 归并适合链表，快排适合数组

**Q5: 主定理的三个条件分别对应什么情况？**
> - 情况1：分解工作量大于合并（如T(n)=2T(n/2)+O(1)）
> - 情况2：分解与合并工作量平衡（如归并排序）
> - 情况3：合并工作量大于分解（如T(n)=2T(n/2)+O(n²)）

## 相关概念

- [递归](./recursion.md) - 分治的实现基础
- [动态规划](./dynamic-programming.md) - 子问题重叠时使用
- [二分查找](./binary-search.md) - 简单分治应用
- [归并排序](../algorithms/sorting.md) - 经典分治排序

## 参考资料

- 《算法导论》第4章 - 分治策略
- 《编程珠玑》 - 算法设计技巧
- [Divide and Conquer - GeeksforGeeks](https://www.geeksforgeeks.org/divide-and-conquer/)
