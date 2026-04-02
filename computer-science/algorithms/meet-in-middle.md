# 中途相遇法 (Meet-in-the-Middle)

## 简介

**中途相遇法**（Meet-in-the-Middle）是一种分治策略，通过将问题分成两半分别求解，然后在中间汇合，将指数级复杂度 O(2^n) 降低到 O(2^(n/2))。它适用于子集和问题、密码学攻击、博弈状态搜索等场景，是处理中等规模 NP 问题的有效技术。

## 核心概念

### 基本思想

**传统方法：**
```
枚举所有子集: O(2^n)
```

**中途相遇：**
```
将集合分成两半 A 和 B
枚举 A 的所有子集和: O(2^(n/2))
枚举 B 的所有子集和: O(2^(n/2))
合并结果: O(2^(n/2) log 2^(n/2)) = O(n · 2^(n/2))

总复杂度: O(n · 2^(n/2))
```

### 子集和问题

**问题：** 找子集使其和等于目标值 T

**算法：**
1. 分成两半
2. 计算左半所有子集和，排序
3. 枚举右半每个子集和 s，在左半二分查找 T-s

### 密码学应用

**双重加密攻击：**
```
C = E_k2(E_k1(P))

从明文端加密: P -> E_k1(P) 存储
从密文端解密: C -> D_k2(C) 查找匹配

将 O(|K|^2) 降到 O(|K|)
```

## 实现方式

```python
from typing import List, Tuple, Optional
import bisect

class MeetInTheMiddle:
    """中途相遇法实现"""
    
    @staticmethod
    def subset_sum(arr: List[int], target: int) -> Optional[List[int]]:
        """
        子集和问题：找和等于 target 的子集
        
        时间: O(n · 2^(n/2))
        空间: O(2^(n/2))
        
        Returns:
            找到的子集，无解返回 None
        """
        n = len(arr)
        if n == 0:
            return [] if target == 0 else None
        
        # 分成两半
        mid = n // 2
        left = arr[:mid]
        right = arr[mid:]
        
        # 计算左半所有子集和
        left_sums = []
        def generate_left(i: int, current_sum: int, indices: List[int]):
            if i == len(left):
                left_sums.append((current_sum, indices.copy()))
                return
            # 不选
            generate_left(i + 1, current_sum, indices)
            # 选
            indices.append(i)
            generate_left(i + 1, current_sum + left[i], indices)
            indices.pop()
        
        generate_left(0, 0, [])
        
        # 按和排序
        left_sums.sort()
        left_values = [s for s, _ in left_sums]
        
        # 枚举右半，查找补集
        result = None
        
        def search_right(i: int, current_sum: int, indices: List[int]):
            nonlocal result
            if result is not None:
                return
            if i == len(right):
                need = target - current_sum
                # 在左半二分查找
                pos = bisect.bisect_left(left_values, need)
                if pos < len(left_values) and left_values[pos] == need:
                    # 找到解
                    left_indices = left_sums[pos][1]
                    result = [left[idx] for idx in left_indices] + \
                             [right[idx] for idx in indices]
                return
            
            # 不选
            search_right(i + 1, current_sum, indices)
            # 选
            indices.append(i)
            search_right(i + 1, current_sum + right[i], indices)
            indices.pop()
        
        search_right(0, 0, [])
        return result
    
    @staticmethod
    def max_subset_sum(arr: List[int], limit: int) -> int:
        """
        最大子集和问题：找子集使其和不超过 limit 且最大
        
        时间: O(n · 2^(n/2))
        """
        n = len(arr)
        if n == 0:
            return 0
        
        mid = n // 2
        left = arr[:mid]
        right = arr[mid:]
        
        # 生成左半所有子集和
        def generate_sums(nums: List[int]) -> List[int]:
            sums = [0]
            for num in nums:
                new_sums = [s + num for s in sums]
                sums.extend(new_sums)
            return sums
        
        left_sums = generate_sums(left)
        right_sums = generate_sums(right)
        
        # 排序并去重左半和
        left_sums = sorted(set(left_sums))
        
        # 对右半每个和，找左半最优补集
        ans = 0
        for rs in right_sums:
            if rs > limit:
                continue
            # 找左半最大的 ls，使得 ls + rs <= limit
            remaining = limit - rs
            pos = bisect.bisect_right(left_sums, remaining) - 1
            if pos >= 0:
                ans = max(ans, left_sums[pos] + rs)
        
        return ans
    
    @staticmethod
    def knapsack(weights: List[int], values: List[int], capacity: int) -> int:
        """
        0/1 背包问题的中途相遇解法
        
        时间: O(n · 2^(n/2))
        适用: n <= 40 的情况
        
        Returns:
            最大价值
        """
        n = len(weights)
        if n == 0:
            return 0
        
        mid = n // 2
        left_w, left_v = weights[:mid], values[:mid]
        right_w, right_v = weights[mid:], values[mid:]
        
        # 生成左半所有 (weight, value) 对
        def generate(items_w: List[int], items_v: List[int]) -> List[Tuple[int, int]]:
            result = [(0, 0)]  # (weight, value)
            for w, v in zip(items_w, items_v):
                new_items = [(cw + w, cv + v) for cw, cv in result]
                result.extend(new_items)
            return result
        
        left_items = generate(left_w, left_v)
        right_items = generate(right_w, right_v)
        
        # 优化左半：对于相同重量保留最大价值
        left_items.sort()
        optimized = []
        max_val = -1
        for w, v in left_items:
            if w > capacity:
                break
            if v > max_val:
                max_val = v
                optimized.append((w, v))
        
        # 枚举右半，在左半二分查找
        ans = 0
        for rw, rv in right_items:
            if rw > capacity:
                continue
            remaining = capacity - rw
            # 找左半重量不超过 remaining 的最大价值
            pos = bisect.bisect_right(optimized, (remaining, float('inf'))) - 1
            if pos >= 0:
                ans = max(ans, optimized[pos][1] + rv)
        
        return ans
    
    @staticmethod
    def count_subsets_with_sum(arr: List[int], target: int) -> int:
        """
        统计和等于 target 的子集数量
        
        时间: O(n · 2^(n/2))
        """
        n = len(arr)
        if n == 0:
            return 1 if target == 0 else 0
        
        mid = n // 2
        left = arr[:mid]
        right = arr[mid:]
        
        from collections import Counter
        
        def count_sums(nums: List[int]) -> Counter:
            counts = Counter({0: 1})
            for num in nums:
                new_counts = Counter({s + num: c for s, c in counts.items()})
                counts.update(new_counts)
            return counts
        
        left_counts = count_sums(left)
        right_counts = count_sums(right)
        
        ans = 0
        for s, c in left_counts.items():
            ans += c * right_counts.get(target - s, 0)
        
        return ans


# 使用示例
if __name__ == "__main__":
    mitm = MeetInTheMiddle()
    
    # 子集和问题
    print("子集和问题:")
    arr = [3, 34, 4, 12, 5, 2]
    target = 9
    result = mitm.subset_sum(arr, target)
    print(f"数组: {arr}, 目标和: {target}")
    print(f"解: {result}")
    if result:
        print(f"验证: sum = {sum(result)}")
    
    # 最大子集和
    print("\n最大子集和:")
    arr = [3, 34, 4, 12, 5, 2]
    limit = 20
    max_sum = mitm.max_subset_sum(arr, limit)
    print(f"数组: {arr}, 限制: {limit}, 最大和: {max_sum}")
    
    # 0/1 背包
    print("\n0/1 背包:")
    weights = [3, 4, 5, 8, 10]
    values = [30, 50, 60, 100, 120]
    capacity = 20
    max_value = mitm.knapsack(weights, values, capacity)
    print(f"重量: {weights}")
    print(f"价值: {values}")
    print(f"容量: {capacity}, 最大价值: {max_value}")
    
    # 统计子集数
    print("\n统计子集数:")
    arr = [1, 2, 3, 4, 5]
    target = 5
    count = mitm.count_subsets_with_sum(arr, target)
    print(f"数组: {arr}, 目标和: {target}, 子集数: {count}")
```

## 应用场景

### 1. 组合优化
- **子集和**：精确解中等规模问题
- **背包问题**：n ≤ 40 的精确解
- **旅行商问题**：Held-Karp 的优化版本

### 2. 密码学攻击
- **双重 DES 攻击**：从两端同时破解
- **哈希碰撞**：生日攻击的变种
- **离散对数**：某些群的攻击

### 3. 博弈搜索
- **棋类游戏**：从初始状态和目标状态双向搜索
- **滑动拼图**：双向 BFS 的优化
- **魔方**：从初始和完成状态同时搜索

### 4. 生物信息学
- **序列比对**：某些动态规划的优化
- **结构预测**：蛋白质折叠的分治策略

## 面试要点

**Q1: 中途相遇法的时间复杂度优势？**
A: 将 O(2^n) 降到 O(2^(n/2))。n=40 时，2^40 ≈ 1万亿，2^20 ≈ 100万，差距巨大。

**Q2: 适用于哪些问题？**
A: (1) 子集和问题；(2) 0/1 背包 n≤40；(3) 密码学中间相遇攻击；(4) 双向搜索问题。

**Q3: 如何处理重复元素？**
A: 用哈希表或 Counter 统计每个和的出现次数，合并时相乘。

**Q4: 空间复杂度是多少？**
A: O(2^(n/2))，存储一半的所有子集和。

**Q5: 与动态规划相比的优劣？**
A: DP 是伪多项式 O(n·target)，MITM 是指数级 O(2^(n/2))。target 很大时用 MITM，target 小但 n 大时用 DP。

## 相关概念

### 数据结构
- [哈希表](../data-structures/hash-table.md) - 快速查找
- [数组](../data-structures/array.md) - 子集存储

### 算法
- [二分搜索](./binary-search.md) - 合并阶段
- [分治法](./divide-conquer.md) - 核心思想
- [动态规划](./dynamic-programming.md) - 替代方案

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - O(n · 2^(n/2))
- [空间复杂度](../../references/space-complexity.md) - O(2^(n/2))
- [NP完全理论](../../references/np-completeness.md) - 问题难度

### 系统实现
- [密码分析](../../references/cryptanalysis.md) - 安全评估
- [组合优化求解器](../../references/optimization-solvers.md) - OR-Tools
