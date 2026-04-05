# 动态规划优化 (Dynamic Programming Optimization)

## 简介
动态规划优化技术用于降低DP问题的时空复杂度。常见的优化方法包括单调队列优化、斜率优化、四边形不等式优化等，可将某些问题的复杂度从O(n²)或O(n³)降至O(n log n)甚至O(n)。

## 核心概念
- **单调队列优化**：利用决策单调性，维护候选决策的单调队列
- **斜率优化**：将DP转移转化为直线，利用凸包性质加速
- **四边形不等式**：证明决策单调性，允许二分查找最优决策点
- **决策单调性**：最优决策点随状态单调变化

## 实现方式

### 单调队列优化（滑动窗口最值）
```python
from collections import deque

def monotone_queue_optimization_dp(arr, k):
    """
    单调队列优化DP：求解滑动窗口内的最值问题
    示例：最大子数组和，窗口大小为k
    时间复杂度: O(n)
    """
    n = len(arr)
    dp = [0] * n  # dp[i]表示以i结尾的最大和
    dp[0] = arr[0]
    
    # 单调递减队列，存储(dp[j] - sum[j+1:i])的最大值对应的索引
    # 这里简化为直接维护前缀和的单调队列
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]
    
    # 求长度不超过k的最大子数组和
    q = deque()  # 存储索引，对应prefix值单调递增
    max_sum = float('-inf')
    
    for i in range(n + 1):
        # 窗口外的元素出队
        while q and q[0] < i - k:
            q.popleft()
        
        # 当前元素作为右端点的答案
        if q:
            max_sum = max(max_sum, prefix[i] - prefix[q[0]])
        
        # 维护单调性：新元素比队尾更小则出队
        while q and prefix[i] <= prefix[q[-1]]:
            q.pop()
        
        q.append(i)
    
    return max_sum
```

### 斜率优化（Convex Hull Trick）
```python
def slope_optimization_dp(points, n):
    """
    斜率优化：适用于形如 dp[i] = min(dp[j] + (x[i] - x[j])²) 的转移
    将转移式整理为 y = kx + b 的形式，维护下凸壳
    时间复杂度: O(n)
    """
    # 示例：DP[i] = min{DP[j] + (H[i] - H[j])²} + C
    # 整理: DP[i] = H[i]² + C + min{DP[j] + H[j]² - 2*H[i]*H[j]}
    # 令 y = DP[j] + H[j]², x = H[j], k = 2*H[i]
    # 则 DP[i] = H[i]² + C + min{y - k*x} = H[i]² + C - max{k*x - y}
    
    dp = [float('inf')] * n
    dp[0] = 0
    
    # 凸壳：维护点集 (x[j], y[j]) 的上凸壳
    # 使用双端队列维护
    hull = deque()
    hull.append((0, 0))  # (x, y)
    
    def slope(p1, p2):
        """计算两点间的斜率"""
        if p1[0] == p2[0]:
            return float('inf')
        return (p2[1] - p1[1]) / (p2[0] - p1[0])
    
    def query(k):
        """查询斜率为k的直线切凸壳的最小值"""
        while len(hull) >= 2 and slope(hull[0], hull[1]) <= k:
            hull.popleft()
        x, y = hull[0]
        return y - k * x
    
    def add_point(new_point):
        """向凸壳添加新点，维护凸性"""
        while len(hull) >= 2 and slope(hull[-2], hull[-1]) >= slope(hull[-1], new_point):
            hull.pop()
        hull.append(new_point)
    
    # 主DP过程
    for i in range(1, n):
        k = 2 * points[i]  # 当前斜率
        dp[i] = points[i]**2 + query(k)
        
        # 添加当前点
        y = dp[i] + points[i]**2
        add_point((points[i], y))
    
    return dp
```

### 四边形不等式优化
```python
def quadrilateral_inequality_dp(cost, n):
    """
    四边形不等式优化：适用于满足四边形不等式的DP
    若 opt[i][j-1] <= opt[i][j] <= opt[i+1][j]，则可用分治或单调队列优化
    时间复杂度从O(n³)降至O(n²)或O(n log n)
    """
    # 示例：石子合并问题，DP[i][j] = min{DP[i][k] + DP[k+1][j]} + sum(i,j)
    # 若cost满足四边形不等式，则决策点单调
    
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + cost[i]
    
    # dp[i][j]: 合并区间[i,j]的最小代价
    dp = [[0] * n for _ in range(n)]
    opt = [[0] * n for _ in range(n)]  # 记录最优决策点
    
    # 初始化：长度为1的区间
    for i in range(n):
        dp[i][i] = 0
        opt[i][i] = i
    
    # 按区间长度递增计算
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            
            # 决策单调性：最优k在[opt[i][j-1], opt[i+1][j]]范围内
            left = opt[i][j - 1] if j > i else i
            right = opt[i + 1][j] if i < j else j
            
            for k in range(left, min(right + 1, j)):
                val = dp[i][k] + dp[k + 1][j] + prefix[j + 1] - prefix[i]
                if val < dp[i][j]:
                    dp[i][j] = val
                    opt[i][j] = k
    
    return dp[0][n - 1]
```

## 应用场景
- **区间DP优化**：石子合并、矩阵链乘等问题的加速
- **背包问题优化**：单调队列优化多重背包
- **字符串编辑距离**：斜率优化加速特定形式的状态转移
- **资源分配问题**：四边形不等式优化决策查找

## 面试要点
1. **Q**: 如何判断DP是否可以用单调队列优化？
   **A**: 当DP转移式可写成 dp[i] = min/max{f(j)} + g(i) 的形式，且j的取值范围是滑动窗口[i-k, i-1]时，可用单调队列维护候选j，时间复杂度从O(nk)降至O(n)。

2. **Q**: 斜率优化的适用条件是什么？
   **A**: 当DP转移式可整理为 dp[i] = min{dp[j] + (x[i]-x[j])²} 或更一般的 dp[i] = min{y[j] - k[i]*x[j]} 形式时，可将(j, dp[j])看作点，用凸包性质加速查询。

3. **Q**: 四边形不等式与决策单调性的关系？
   **A**: 若cost函数满足四边形不等式w(i,j)+w(i',j')<=w(i,j')+w(i',j)（i<=i'<=j<=j'），则DP的最优决策点opt[i][j]满足opt[i][j-1]<=opt[i][j]<=opt[i+1][j]，可用二分或分治优化。

4. **Q**: 凸包优化的查询可以用二分查找代替线性扫描吗？
   **A**: 可以。如果查询的斜率是单调递增的，可用双端队列+队首出队实现O(1)均摊；如果斜率不单调，则需用二分查找或李超线段树，复杂度O(log n)。

## 相关概念

### 数据结构
- [单调队列](../data-structures/monotonic-queue.md) - 滑动窗口优化的核心结构
- [凸包](../data-structures/convex-hull.md) - 斜率优化的几何基础

### 算法
- [动态规划](./dynamic-programming.md) - 优化的基础算法
- [分治算法](./divide-and-conquer.md) - 四边形不等式优化的实现方式

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 从O(n³)到O(n²)的优化分析

### 系统实现
- [编译器优化](../systems/compiler-optimization.md) - 编译器中的动态规划应用
