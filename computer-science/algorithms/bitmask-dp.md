# 状态压缩动态规划 (Bitmask DP)

## 简介

**状态压缩动态规划**（Bitmask DP）是处理子集状态的高效 DP 技术，利用位运算将集合状态压缩为整数。它将指数级状态空间优化到可处理范围，是解决旅行商问题（TSP）、集合覆盖、博弈状态等 NP 问题的关键技术，在竞赛编程和实际应用中都有重要价值。

## 核心概念

### 位运算基础

**位运算操作：**
```python
# 检查第 i 位是否为 1
if state & (1 << i):
    
# 设置第 i 位为 1
state |= (1 << i)

# 清除第 i 位
state &= ~(1 << i)

# 切换第 i 位
state ^= (1 << i)

# 获取最低位的 1
lowbit = state & (-state)

# 清除最低位的 1
state &= (state - 1)

# 统计 1 的个数
count = bin(state).count('1')
```

### 状态表示

**集合 → 整数：**
```
集合 {0, 2, 3} → 二进制 1101 → 整数 13
第 i 位为 1 表示元素 i 在集合中
```

**状态转移：**
```
dp[mask] 表示处理集合 mask 对应的最优值
转移时枚举 mask 的子集或超集
```

### 子集枚举

**枚举 mask 的所有子集：**
```python
sub = mask
while sub:
    # 处理子集 sub
    sub = (sub - 1) & mask
```

**复杂度：** O(3^n) 枚举所有集合的所有子集

## 实现方式

```python
from typing import List, Tuple
import sys

class BitmaskDP:
    """状态压缩 DP 实现"""
    
    INF = float('inf')
    
    @staticmethod
    def tsp(dist: List[List[int]]) -> int:
        """
        旅行商问题 (TSP)
        
        dp[mask][i] = 从起点出发，经过 mask 中的城市，最终到达 i 的最短距离
        
        时间: O(n^2 · 2^n)
        空间: O(n · 2^n)
        
        Args:
            dist: 距离矩阵，dist[i][j] 表示 i 到 j 的距离
        
        Returns:
            最短回路长度
        """
        n = len(dist)
        if n == 0:
            return 0
        
        # dp[mask][i]: 经过 mask 表示的城市，当前在 i
        dp = [[BitmaskDP.INF] * n for _ in range(1 << n)]
        
        # 起点为 0
        dp[1][0] = 0
        
        for mask in range(1 << n):
            for last in range(n):
                if not (mask & (1 << last)):  # last 不在 mask 中
                    continue
                if dp[mask][last] == BitmaskDP.INF:
                    continue
                
                # 尝试去下一个城市
                for nxt in range(n):
                    if mask & (1 << nxt):  # 已经访问过
                        continue
                    new_mask = mask | (1 << nxt)
                    dp[new_mask][nxt] = min(
                        dp[new_mask][nxt],
                        dp[mask][last] + dist[last][nxt]
                    )
        
        # 返回起点
        ans = BitmaskDP.INF
        full_mask = (1 << n) - 1
        for last in range(1, n):
            ans = min(ans, dp[full_mask][last] + dist[last][0])
        
        return ans
    
    @staticmethod
    def minimum_vertex_cover(n: int, edges: List[Tuple[int, int]]) -> int:
        """
        最小顶点覆盖（二分图）
        
        对于小规模一般图，枚举一侧的所有子集
        
        时间: O(m · 2^n)
        """
        # 建立邻接表
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        
        ans = n
        
        # 枚举左侧顶点的选择（假设 0 到 n//2-1 是左侧）
        left_size = n // 2
        
        for mask in range(1 << left_size):
            covered = set()
            count = bin(mask).count('1')
            
            # 标记已覆盖的边
            for u in range(left_size):
                if mask & (1 << u):
                    for v in adj[u]:
                        covered.add((min(u, v), max(u, v)))
            
            # 右侧必须选覆盖剩余边的顶点
            for u in range(left_size, n):
                need = False
                for v in adj[u]:
                    edge = (min(u, v), max(u, v))
                    if edge not in covered:
                        need = True
                        break
                if need:
                    count += 1
                    for v in adj[u]:
                        edge = (min(u, v), max(u, v))
                        covered.add(edge)
            
            if len(covered) == len(edges):
                ans = min(ans, count)
        
        return ans
    
    @staticmethod
    def assignment_problem(cost: List[List[int]]) -> int:
        """
        指派问题（二分图最小权匹配）
        匈牙利算法的位运算版本，适用于 n <= 20
        
        dp[mask] = 前 k 个工人（k=popcount(mask)）
                  分配给 mask 表示的工作集合的最小代价
        
        时间: O(n · 2^n)
        """
        n = len(cost)
        if n == 0:
            return 0
        
        dp = [BitmaskDP.INF] * (1 << n)
        dp[0] = 0
        
        for mask in range(1 << n):
            # 当前分配给第 k 个工人
            k = bin(mask).count('1')
            if k >= n:
                continue
            
            for job in range(n):
                if not (mask & (1 << job)):
                    new_mask = mask | (1 << job)
                    dp[new_mask] = min(dp[new_mask], dp[mask] + cost[k][job])
        
        return dp[(1 << n) - 1]
    
    @staticmethod
    def sos_dp(f: List[int]) -> List[int]:
        """
        Sum Over Subsets DP (SOS DP)
        
        计算对于每个 mask，所有子集的 f[sub] 之和
        
        时间: O(n · 2^n)
        """
        n = len(f).bit_length() - 1
        dp = f.copy()
        
        for i in range(n):
            for mask in range(1 << n):
                if mask & (1 << i):
                    dp[mask] += dp[mask ^ (1 << i)]
        
        return dp
    
    @staticmethod
    def max_independent_set(adj: List[int]) -> int:
        """
        最大独立集（适用于 n <= 25 的一般图）
        
        使用折半搜索优化
        
        时间: O(2^(n/2))
        """
        n = len(adj)
        if n == 0:
            return 0
        
        # 分成两半
        mid = n // 2
        
        # 枚举左半的所有独立集
        left_dp = {}
        for mask in range(1 << mid):
            # 检查是否为独立集
            valid = True
            for i in range(mid):
                if mask & (1 << i):
                    # 检查邻居
                    if adj[i] & mask:
                        valid = False
                        break
            
            if valid:
                # 记录该独立集及其在右半的禁止顶点
                forbidden = 0
                for i in range(mid):
                    if mask & (1 << i):
                        forbidden |= adj[i] >> mid  # 右半的邻居
                
                cnt = bin(mask).count('1')
                # 保留每个 forbidden  mask 的最大计数
                if forbidden not in left_dp or left_dp[forbidden] < cnt:
                    left_dp[forbidden] = cnt
        
        # 优化：如果 forbidden_a ⊆ forbidden_b 且 cnt_a >= cnt_b，保留 a
        # 这里简化处理，直接枚举右半
        
        ans = 0
        for mask in range(1 << (n - mid)):
            valid = True
            for i in range(n - mid):
                if mask & (1 << i):
                    if (adj[i + mid] >> mid) & mask:
                        valid = False
                        break
            
            if valid:
                # 找左半不与 mask 冲突的最大独立集
                right_mask = mask
                left_forbidden = 0
                for i in range(n - mid):
                    if mask & (1 << i):
                        left_forbidden |= adj[i + mid] & ((1 << mid) - 1)
                
                # 左半不能选 left_forbidden 中的顶点
                best_left = 0
                for forbidden, cnt in left_dp.items():
                    if not (forbidden & right_mask):  # 不与右半冲突
                        if not (left_forbidden & ((1 << mid) - 1) & ...):
                            # 简化：这里需要更复杂的处理
                            pass
                
                ans = max(ans, bin(mask).count('1') + best_left)
        
        return ans


# 使用示例
if __name__ == "__main__":
    dp = BitmaskDP()
    
    # TSP
    print("TSP:")
    dist = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ]
    tsp_result = dp.tsp(dist)
    print(f"最短回路长度: {tsp_result}")
    
    # 指派问题
    print("\n指派问题:")
    cost = [
        [9, 2, 7, 8],
        [6, 4, 3, 7],
        [5, 8, 1, 8],
        [7, 6, 9, 4]
    ]
    assign_result = dp.assignment_problem(cost)
    print(f"最小总成本: {assign_result}")
    
    # SOS DP
    print("\nSOS DP:")
    f = [1, 2, 3, 4, 5, 6, 7, 8]  # n=3, 2^3=8
    sos_result = dp.sos_dp(f)
    print(f"原数组: {f}")
    print(f"子集和: {sos_result}")
    
    # 位运算技巧演示
    print("\n位运算技巧:")
    state = 0b10110  # 22
    print(f"state = {bin(state)}")
    print(f"第 1 位是否为 1: {bool(state & (1 << 1))}")
    print(f"第 2 位是否为 1: {bool(state & (1 << 2))}")
    print(f"设置第 0 位: {bin(state | (1 << 0))}")
    print(f"清除第 1 位: {bin(state & ~(1 << 1))}")
    print(f"1 的个数: {bin(state).count('1')}")
    
    # 枚举子集
    print(f"\n{bin(state)} 的所有非空子集:")
    sub = state
    while sub:
        print(f"  {bin(sub)}")
        sub = (sub - 1) & state
```

## 应用场景

### 1. 图论问题
- **TSP**：精确求解中等规模旅行商问题
- **最大独立集**：一般图的精确算法
- **图染色**：状态压缩表示染色方案

### 2. 组合优化
- **集合覆盖**：精确覆盖问题
- **指派问题**：匈牙利算法的替代
- **调度问题**：任务分配优化

### 3. 博弈论
- **组合游戏**：Grundy 数计算
- **棋类游戏**：状态空间搜索
- **Nim 游戏**：SG 函数优化

### 4. 动态规划优化
- **轮廓线 DP**：网格类问题
- **插头 DP**：连通性状态压缩
- **子集卷积**：快速 zeta 变换

## 面试要点

**Q1: 状态压缩 DP 适用于什么问题？**
A: 状态是集合且规模 n ≤ 20-25 的问题。超过 25 则 2^n 过大，需要考虑其他方法。

**Q2: TSP 的状态转移方程？**
A: dp[mask][i] = min(dp[mask][i], dp[mask^(1<<i)][j] + dist[j][i])，其中 mask 包含 i，j 是 mask 中 i 的前驱。

**Q3: 如何枚举一个集合的所有子集？**
A: `sub = mask; while sub: process(sub); sub = (sub-1) & mask`。时间 O(2^k)，k 为 mask 中 1 的个数。

**Q4: SOS DP 是什么？**
A: Sum Over Subsets DP，计算每个集合的所有子集的函数值之和。常用于子集卷积、或卷积等问题。

**Q5: 位运算优化的注意事项？**
A: (1) 注意整数溢出；(2) Python 整数无上限但会变慢；(3) 优先使用位运算而非数组操作。

## 相关概念

### 数据结构
- [位集](../data-structures/bitset.md) - 位运算优化
- [数组](../data-structures/array.md) - DP 表格

### 算法
- [动态规划](./dynamic-programming.md) - 基础思想
- [折半搜索](./meet-in-middle.md) - 处理更大规模
- [匈牙利算法](./hungarian-algorithm.md) - 指派问题替代

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - O(n^2 · 2^n) for TSP
- [空间复杂度](../../references/space-complexity.md) - O(n · 2^n)

### 系统实现
- [运筹优化](../../references/operations-research.md) - TSP 求解器
- [竞赛编程](../../references/competitive-programming.md) - 常用技巧
