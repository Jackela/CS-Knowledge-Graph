# 矩阵快速幂 (Matrix Exponentiation)

## 简介

**矩阵快速幂**（Matrix Exponentiation）是快速幂算法在矩阵上的推广，能够高效计算矩阵的高次幂，时间复杂度为 O(n³ log k)。它是解决线性递推问题的强大工具，可以在 O(log k) 时间内计算斐波那契数列的第 k 项，广泛应用于动态规划优化、图论、线性递推等问题。

## 核心概念

### 矩阵乘法

**定义：**
```
C[i][j] = Σ(A[i][k] × B[k][j])
```

**时间复杂度：** O(n³) 对于 n×n 矩阵

**性质：**
- 结合律：(AB)C = A(BC)
- 不满足交换律：AB ≠ BA（一般情况）

### 快速幂推广

**原理：**
```
A^k = (A^(k/2))^2      (k 偶数)
A^k = A × (A^((k-1)/2))^2 (k 奇数)
```

**与普通快速幂的区别：**
- 乘法换成矩阵乘法
- 单位元是单位矩阵 I

### 线性递推关系

**斐波那契数列：**
```
[F(n+1)]   [1 1] [F(n)  ]
[F(n)  ] = [1 0] [F(n-1)]

即: A^n × [F(1), F(0)]^T = [F(n+1), F(n)]^T
```

**一般形式：**
```
x(n) = c1·x(n-1) + c2·x(n-2) + ... + ck·x(n-k)

可以写成 k×k 矩阵的幂
```

### 图论应用

**邻接矩阵的 k 次幂：**
- A^k[i][j] = 从 i 到 j 的长度为 k 的路径数
- 可用于计算最短路径（用 min-plus 代数）

## 实现方式

```python
from typing import List, TypeVar

T = TypeVar('T')

class Matrix:
    """矩阵类，支持快速幂"""
    
    def __init__(self, data: List[List[int]], mod: int = None):
        self.data = data
        self.n = len(data)
        self.m = len(data[0]) if data else 0
        self.mod = mod
    
    def __mul__(self, other: 'Matrix') -> 'Matrix':
        """矩阵乘法"""
        if self.m != other.n:
            raise ValueError("矩阵维度不匹配")
        
        result = [[0] * other.m for _ in range(self.n)]
        
        for i in range(self.n):
            for k in range(self.m):
                if self.data[i][k] == 0:
                    continue
                for j in range(other.m):
                    result[i][j] += self.data[i][k] * other.data[k][j]
                    if self.mod:
                        result[i][j] %= self.mod
        
        return Matrix(result, self.mod)
    
    def __pow__(self, power: int) -> 'Matrix':
        """矩阵快速幂"""
        if self.n != self.m:
            raise ValueError("只有方阵可以求幂")
        
        # 初始化结果为单位矩阵
        result = Matrix.identity(self.n, self.mod)
        base = self
        
        while power > 0:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        
        return result
    
    @staticmethod
    def identity(n: int, mod: int = None) -> 'Matrix':
        """创建 n×n 单位矩阵"""
        data = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        return Matrix(data, mod)
    
    def __repr__(self):
        return f"Matrix({self.data})"


class MatrixExponentiation:
    """矩阵快速幂应用"""
    
    MOD = 10**9 + 7
    
    @staticmethod
    def fibonacci(n: int) -> int:
        """
        计算第 n 个斐波那契数
        F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)
        
        时间: O(log n)
        """
        if n <= 1:
            return n
        
        # 转移矩阵
        A = Matrix([[1, 1], [1, 0]], MatrixExponentiation.MOD)
        
        # A^n × [F(1), F(0)]^T = [F(n+1), F(n)]^T
        result = A ** n
        return result.data[1][0]
    
    @staticmethod
    def fibonacci_general(n: int, a: int, b: int, c1: int, c2: int) -> int:
        """
        广义斐波那契
        F(0)=a, F(1)=b, F(n)=c1·F(n-1)+c2·F(n-2)
        """
        if n == 0:
            return a
        if n == 1:
            return b
        
        A = Matrix([[c1, c2], [1, 0]], MatrixExponentiation.MOD)
        result = A ** (n - 1)
        
        # [F(n), F(n-1)]^T = A^(n-1) × [F(1), F(0)]^T
        return (result.data[0][0] * b + result.data[0][1] * a) % MatrixExponentiation.MOD
    
    @staticmethod
    def linear_recurrence(n: int, init: List[int], coeffs: List[int]) -> int:
        """
        一般线性递推
        F(n) = coeffs[0]·F(n-1) + coeffs[1]·F(n-2) + ...
        
        Args:
            n: 要求的位置
            init: 初始值 [F(0), F(1), ..., F(k-1)]
            coeffs: 系数 [c1, c2, ..., ck]
        
        Returns:
            F(n)
        """
        k = len(coeffs)
        
        if n < k:
            return init[n]
        
        # 构建 k×k 伴随矩阵
        # [c1 c2 c3 ... ck]
        # [1  0  0  ... 0 ]
        # [0  1  0  ... 0 ]
        # [...          ...]
        A_data = [[0] * k for _ in range(k)]
        for j in range(k):
            A_data[0][j] = coeffs[j]
        for i in range(1, k):
            A_data[i][i-1] = 1
        
        A = Matrix(A_data, MatrixExponentiation.MOD)
        result = A ** (n - k + 1)
        
        # 计算结果
        ans = 0
        for j in range(k):
            ans = (ans + result.data[0][j] * init[k - 1 - j]) % MatrixExponentiation.MOD
        
        return ans
    
    @staticmethod
    def count_paths(adj: List[List[int]], k: int) -> List[List[int]]:
        """
        统计长度为 k 的路径数
        
        Args:
            adj: 邻接矩阵
            k: 路径长度
        
        Returns:
            A^k，其中 A^k[i][j] 表示 i 到 j 长度为 k 的路径数
        """
        A = Matrix(adj, MatrixExponentiation.MOD)
        return (A ** k).data
    
    @staticmethod
    def dp_optimization(states: int, transitions: List[List[int]], n: int) -> int:
        """
        线性 DP 的矩阵优化
        
        适用于：DP[n][state] = Σ(DP[n-1][prev_state] × trans[prev_state][state])
        
        Args:
            states: 状态数
            transitions: 转移矩阵
            n: 步数
        
        Returns:
            最终状态向量
        """
        T = Matrix(transitions, MatrixExponentiation.MOD)
        T_n = T ** n
        return T_n.data


# 使用示例
if __name__ == "__main__":
    me = MatrixExponentiation()
    
    # 斐波那契数列
    print("斐波那契数列:")
    for i in range(10):
        print(f"F({i}) = {me.fibonacci(i)}")
    
    print(f"\nF(100) = {me.fibonacci(100)}")
    print(f"F(1000000) mod 1e9+7 = {me.fibonacci(1000000)}")
    
    # 广义斐波那契 (Tribonacci)
    print("\nTribonacci (系数 [1,1,1]):")
    init = [0, 0, 1]
    coeffs = [1, 1, 1]
    for n in range(10):
        val = me.linear_recurrence(n, init, coeffs)
        print(f"T({n}) = {val}")
    
    # 图的路径计数
    print("\n图的路径计数:")
    # 三角形图: 0-1, 1-2, 2-0
    adj = [
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ]
    paths = me.count_paths(adj, 3)
    print("长度为 3 的路径数矩阵:")
    for row in paths:
        print(row)
```

## 应用场景

### 1. 递推加速
- **斐波那契数列**：O(log n) 计算第 n 项
- **线性递推**：齐次线性递推的一般解法
- **卡特兰数**：组合数递推加速

### 2. 图论算法
- **路径计数**：固定长度路径数
- **传递闭包**：可达性矩阵
- **最小最大路径**：用 min-max 代数

### 3. 动态规划优化
- **状态压缩 DP**：状态转移矩阵化
- **字符串自动机**：AC 自动机转移
- **博弈论 SG 函数**：状态递推

### 4. 数值计算
- **马尔可夫链**：状态转移
- **PageRank**：迭代矩阵幂
- **线性变换**：重复应用

## 面试要点

**Q1: 为什么矩阵快速幂能加速递推？**
A: 线性递推可以写成矩阵形式。矩阵幂的结合律允许我们使用快速幂，将 O(n) 的递推降到 O(log n) 的矩阵幂计算。

**Q2: 斐波那契的转移矩阵是什么？**
A: [[1,1],[1,0]]。因为 [F(n+1),F(n)]^T = [[1,1],[1,0]] × [F(n),F(n-1)]^T。

**Q3: 矩阵乘法和快速幂的时间复杂度？**
A: 矩阵乘法 O(n³)，快速幂 O(log k)，总共 O(n³ log k)。对于 n=2 的斐波那契，就是 O(log k)。

**Q4: 邻接矩阵的 k 次幂表示什么？**
A: A^k[i][j] 表示从顶点 i 到 j 的长度恰好为 k 的路径数。这是矩阵乘法的组合意义。

**Q5: 什么情况下用矩阵快速幂优化 DP？**
A: 当 DP 转移是线性的，且需要计算很远的状态（如 DP[10^9]）时。普通 DP 是 O(n)，矩阵快速幂是 O(log n)。

## 相关概念

### 数据结构
- [矩阵](../data-structures/matrix.md) - 二维数组表示
- [图](../data-structures/graph.md) - 邻接矩阵

### 算法
- [快速幂](./modular-arithmetic.md) - 标量快速幂
- [动态规划](./dynamic-programming.md) - 递推基础
- [线性代数](../mathematics/linear-algebra/matrix-operations.md) - 矩阵理论

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - O(n³ log k)
- [空间复杂度](../../references/space-complexity.md) - O(n²)

### 系统实现
- [数值计算库](../../references/numpy.md) - 矩阵运算
- [图计算引擎](../../references/graph-engines.md) - 大规模图算法
