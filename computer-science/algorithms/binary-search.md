# 二分查找 (Binary Search)

## 简介

**二分查找（Binary Search）**是一种在有序数组中查找目标元素的高效算法。其核心思想是每次将搜索范围缩小一半，通过比较中间元素与目标值来决定搜索方向。

二分查找与[二叉搜索树](../data-structures/bst.md)有着深刻的联系：二者都利用了"分而治之"的思想，通过比较操作将搜索空间减半。

```
有序数组: [1, 3, 5, 7, 9, 11, 13, 15]

查找 9:
  第1轮: [1, 3, 5, 7, 9, 11, 13, 15]
              ↑ mid=7 < 9, 向右
  第2轮: [9, 11, 13, 15]
              ↑ mid=11 > 9, 向左
  第3轮: [9]
         ↑ mid=9 = 9, 找到!
```

## 算法原理

### 基本步骤

1. **确定边界**：初始化左右指针 `left = 0`, `right = n - 1`
2. **计算中点**：`mid = left + (right - left) / 2`（防止溢出）
3. **比较判断**：
   - 若 `arr[mid] == target`，找到目标
   - 若 `arr[mid] < target`，目标在右半部分，`left = mid + 1`
   - 若 `arr[mid] > target`，目标在左半部分，`right = mid - 1`
4. **重复步骤2-3**直到找到目标或 `left > right`

### 代码实现

```python
def binary_search(arr, target):
    """
    标准二分查找
    返回目标索引，不存在返回 -1
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1
```

## 复杂度分析

| 指标 | 复杂度 | 说明 |
|------|--------|------|
| 时间复杂度 | $O(\log n)$ | 每次搜索范围减半 |
| 空间复杂度 | $O(1)$ | 仅使用常数额外空间 |

## 变体问题

### 查找左边界

```python
def find_left_bound(arr, target):
    """查找第一个等于 target 的位置"""
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid + 1
        elif arr[mid] > target:
            right = mid - 1
        else:
            result = mid
            right = mid - 1  # 继续在左半部分查找
    
    return result
```

### 查找右边界

```python
def find_right_bound(arr, target):
    """查找最后一个等于 target 的位置"""
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid + 1
        elif arr[mid] > target:
            right = mid - 1
        else:
            result = mid
            left = mid + 1  # 继续在右半部分查找
    
    return result
```

## 应用场景

1. **数据库索引**：B+树索引的内部节点使用二分查找定位子节点
2. **查找表**：在静态有序数据中快速定位
3. **求根问题**：在单调函数中查找满足条件的值
4. **旋转数组**：在旋转有序数组中查找元素

## 二分查找 vs 二叉搜索树

| 特性 | 二分查找 | 二叉搜索树 |
|------|----------|------------|
| 数据结构 | 有序数组 | 树形结构 |
| 查找时间 | $O(\log n)$ | $O(\log n)$ ~ $O(n)$ |
| 插入删除 | $O(n)$ | $O(\log n)$ |
| 适用场景 | 静态数据，频繁查找 | 动态数据，频繁增删 |

## 相关概念

- [二叉搜索树](../data-structures/bst.md) - 相同的分治思想，树形实现
- [数组](../data-structures/array.md) - 二分查找的基础数据结构
- [排序算法](./sorting.md) - 二分查找要求数据有序

## 参考资料

1. 《算法导论》第2.3章 - 分治策略
2. Binary search algorithm - Wikipedia
