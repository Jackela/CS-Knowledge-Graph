# 矩阵运算 (Matrix Operations)

## 简介

矩阵运算（Matrix Operations）是线性代数的核心内容，也是计算机科学中最重要的数学工具之一。从神经网络的前向传播到图形的几何变换，从推荐系统的协同过滤到搜索引擎的PageRank算法，矩阵运算无处不在。

## 核心概念

### 矩阵基础

矩阵是 $m \times n$ 的矩形数组，记作 $A = [a_{ij}]$：

$$
A = \begin{bmatrix}
a_{11} & a_{12} & \cdots & a_{1n} \\
a_{21} & a_{22} & \cdots & a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
a_{m1} & a_{m2} & \cdots & a_{mn}
\end{bmatrix}
$$

其中 $a_{ij}$ 表示第 $i$ 行第 $j$ 列的元素。

### 基本运算

| 运算 | 定义 | 复杂度 |
|------|------|--------|
| **加法** | $(A + B)_{ij} = a_{ij} + b_{ij}$ | $O(mn)$ |
| **数乘** | $(cA)_{ij} = c \cdot a_{ij}$ | $O(mn)$ |
| **转置** | $(A^T)_{ij} = a_{ji}$ | $O(mn)$ |
| **乘法** | $(AB)_{ij} = \sum_{k=1}^{p} a_{ik} b_{kj}$ | $O(mnp)$ |

### 矩阵乘法

设 $A$ 为 $m \times p$ 矩阵，$B$ 为 $p \times n$ 矩阵：

$$
(AB)_{ij} = \sum_{k=1}^{p} a_{ik} b_{kj} = a_{i1}b_{1j} + a_{i2}b_{2j} + \cdots + a_{ip}b_{pj}
$$

**重要性质：**
- 结合律：$(AB)C = A(BC)$
- 分配律：$A(B+C) = AB + AC$
- **不满足交换律**：一般 $AB \neq BA$
- 转置性质：$(AB)^T = B^T A^T$

### 特殊矩阵

| 类型 | 定义 | 性质 |
|------|------|------|
| **单位矩阵 $I$** | 对角线为1，其余为0 | $AI = IA = A$ |
| **对角矩阵 $D$** | 非对角线元素全为0 | 乘法可交换：$D_1 D_2 = D_2 D_1$ |
| **对称矩阵** | $A = A^T$ | 特征值均为实数 |
| **正交矩阵** | $A^T A = AA^T = I$ | 保范数：$\|Ax\| = \|x\|$ |
| **幂等矩阵** | $A^2 = A$ | 投影矩阵的性质 |
| **零矩阵** | 所有元素为0 | $A + 0 = A$ |

## 数学原理

### 矩阵链乘法

给定 $n$ 个矩阵的链 $<A_1, A_2, ..., A_n>$，矩阵 $A_i$ 的维度为 $p_{i-1} \times p_i$，寻找最优的括号化方案使得标量乘法次数最少。

动态规划递推式：

$$
m[i,j] = \begin{cases}
0 & \text{if } i = j \\
\min_{i \leq k < j} \{m[i,k] + m[k+1,j] + p_{i-1} p_k p_j\} & \text{if } i < j
\end{cases}
$$

### Strassen算法

将 $n \times n$ 矩阵分块为 $2 \times 2$ 的块矩阵：

$$
\begin{bmatrix} C_{11} & C_{12} \\ C_{21} & C_{22} \end{bmatrix} = 
\begin{bmatrix} A_{11} & A_{12} \\ A_{21} & A_{22} \end{bmatrix} 
\begin{bmatrix} B_{11} & B_{12} \\ B_{21} & B_{22} \end{bmatrix}
$$

通过7次乘法而非8次，时间复杂度降为 $O(n^{\log_2 7}) \approx O(n^{2.807})$。

### 矩阵求逆

对于方阵 $A$，若存在 $A^{-1}$ 使得 $AA^{-1} = A^{-1}A = I$，则称 $A$ 可逆。

**逆矩阵存在的充要条件：**
- $\det(A) \neq 0$
- $A$ 是满秩矩阵
- $A$ 的行（列）向量线性无关

求逆公式：$A^{-1} = \frac{1}{\det(A)} \text{adj}(A)$

## 示例

```python
import numpy as np
from typing import List, Tuple

# ==================== 基础矩阵运算 ====================

# 矩阵创建
A = np.array([[1, 2, 3],
              [4, 5, 6],
              [7, 8, 9]], dtype=float)

B = np.array([[9, 8, 7],
              [6, 5, 4],
              [3, 2, 1]], dtype=float)

# 矩阵加法
C_add = A + B
print("矩阵加法 A + B:")
print(C_add)

# 矩阵数乘
C_scalar = 2.5 * A
print("\n矩阵数乘 2.5 * A:")
print(C_scalar)

# 矩阵转置
A_T = A.T
print("\n矩阵转置 A^T:")
print(A_T)

# ==================== 矩阵乘法 ====================

# 创建兼容维度的矩阵
M = np.array([[1, 2],
              [3, 4],
              [5, 6]])  # 3×2

N = np.array([[7, 8, 9],
              [10, 11, 12]])  # 2×3

# 矩阵乘法 (3×2 @ 2×3 = 3×3)
C_mult = M @ N  # 或 np.dot(M, N)
print("\n矩阵乘法 M @ N (3×2 @ 2×3 = 3×3):")
print(C_mult)

# ==================== 矩阵求逆 ====================

# 可逆矩阵（行列式不为0）
D = np.array([[4, 7],
              [2, 6]], dtype=float)

print("\n矩阵 D:")
print(D)
print(f"行列式: {np.linalg.det(D):.4f}")

D_inv = np.linalg.inv(D)
print("\n逆矩阵 D^-1:")
print(D_inv)

# 验证逆矩阵
print("\n验证: D @ D^-1 = I:")
print(np.round(D @ D_inv, 10))

# ==================== 矩阵幂与指数 ====================

E = np.array([[1, 2],
              [0, 3]], dtype=float)

# 矩阵幂
E_power_3 = np.linalg.matrix_power(E, 3)
print("\n矩阵 E^3:")
print(E_power_3)

# 矩阵指数 (e^A)
from scipy.linalg import expm
E_exp = expm(E)
print("\n矩阵指数 e^E:")
print(E_exp)

# ==================== 矩阵链乘法优化 ====================

def matrix_chain_order(dimensions: List[int]) -> Tuple[np.ndarray, np.ndarray]:
    """
    使用动态规划求解矩阵链乘法最优顺序
    dimensions: 矩阵链的维度列表，如 [A1(10×30), A2(30×5), A3(5×60)] -> [10, 30, 5, 60]
    返回: (最少乘法次数表, 分割点表)
    """
    n = len(dimensions) - 1  # 矩阵个数
    m = np.zeros((n, n))     # 最少乘法次数
    s = np.zeros((n, n), dtype=int)  # 最优分割点
    
    # l 是链长度
    for l in range(2, n + 1):
        for i in range(n - l + 1):
            j = i + l - 1
            m[i, j] = float('inf')
            for k in range(i, j):
                # 计算在k处分割的代价
                cost = m[i, k] + m[k + 1, j] + dimensions[i] * dimensions[k + 1] * dimensions[j + 1]
                if cost < m[i, j]:
                    m[i, j] = cost
                    s[i, j] = k
    
    return m, s


def print_optimal_parens(s: np.ndarray, i: int, j: int, names: List[str]):
    """打印最优括号化方案"""
    if i == j:
        print(names[i], end="")
    else:
        print("(", end="")
        print_optimal_parens(s, i, s[i, j], names)
        print_optimal_parens(s, s[i, j] + 1, j, names)
        print(")", end="")


# 示例: A1(30×35), A2(35×15), A3(15×5), A4(5×10), A5(10×20), A6(20×25)
dims = [30, 35, 15, 5, 10, 20, 25]
names = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']

m, s = matrix_chain_order(dims)
print("\n\n矩阵链乘法优化:")
print(f"矩阵链维度: {dims}")
print(f"最少乘法次数: {int(m[0, 5])}")
print("最优括号化方案: ", end="")
print_optimal_parens(s, 0, 5, names)
print()

# ==================== 分块矩阵运算 ====================

def block_matrix_multiply(A: np.ndarray, B: np.ndarray, block_size: int) -> np.ndarray:
    """
    分块矩阵乘法 - 适合缓存优化的实现
    """
    n = A.shape[0]
    C = np.zeros((n, n))
    
    for i0 in range(0, n, block_size):
        for j0 in range(0, n, block_size):
            for k0 in range(0, n, block_size):
                # 计算块 (i0, j0)
                i_max = min(i0 + block_size, n)
                j_max = min(j0 + block_size, n)
                k_max = min(k0 + block_size, n)
                
                for i in range(i0, i_max):
                    for j in range(j0, j_max):
                        for k in range(k0, k_max):
                            C[i, j] += A[i, k] * B[k, j]
    
    return C


# 测试分块乘法
size = 256
A_test = np.random.randn(size, size)
B_test = np.random.randn(size, size)

# 标准乘法
C_standard = A_test @ B_test

# 分块乘法 (block_size=64)
C_block = block_matrix_multiply(A_test, B_test, block_size=64)

print(f"\n分块矩阵乘法验证: 误差 = {np.max(np.abs(C_standard - C_block)):.2e}")

# ==================== 特殊矩阵生成 ====================

# 单位矩阵
I = np.eye(4)
print("\n单位矩阵 I_4:")
print(I)

# 对角矩阵
diag_vals = [1, 2, 3, 4]
D = np.diag(diag_vals)
print("\n对角矩阵:")
print(D)

# 上三角矩阵
U = np.triu(np.random.randint(1, 10, (4, 4)))
print("\n上三角矩阵:")
print(U)

# 对称矩阵
S = np.random.randn(4, 4)
S = (S + S.T) / 2  # 对称化
print("\n对称矩阵 (验证: S = S^T):", np.allclose(S, S.T))

# 正交矩阵 (Householder变换生成)
v = np.random.randn(4)
v = v / np.linalg.norm(v)
H = np.eye(4) - 2 * np.outer(v, v)  # Householder矩阵
print("正交矩阵验证 (H @ H.T = I):", np.allclose(H @ H.T, np.eye(4)))
```

## 应用场景

### 1. 神经网络前向传播

```
每一层计算: Z = WX + b
其中 W 是权重矩阵, X 是输入, b 是偏置向量
```

### 2. 计算机图形学
- **变换矩阵**：平移、旋转、缩放、投影
- **3D渲染**：顶点变换使用 $4 \times 4$ 齐次坐标矩阵

### 3. 推荐系统
- **协同过滤**：用户-物品评分矩阵分解
- **矩阵分解**：$R \approx PQ^T$

### 4. 搜索引擎
- **PageRank**：邻接矩阵的幂迭代
- **TF-IDF**：文档-词项矩阵运算

### 5. 图算法
- **邻接矩阵**：图结构的矩阵表示
- **最短路径**：Floyd-Warshall 使用矩阵乘法变体

## 面试要点

### Q1: 矩阵乘法的时间复杂度是多少？如何优化？

**标准算法**：$O(n^3)$ 对于 $n \times n$ 矩阵

**优化方法**：
1. **Strassen算法**：$O(n^{2.807})$，将矩阵分块，减少乘法次数
2. **Coppersmith-Winograd**：理论最优 $O(n^{2.373})$，但常数太大不实用
3. **分块缓存优化**：利用CPU缓存，提高实际运行效率
4. **并行计算**：GPU加速（CUDA/cuBLAS）、分布式计算
5. **稀疏矩阵优化**：只存储非零元素，使用CSR/CSC格式

### Q2: 矩阵乘法的几何意义是什么？

矩阵乘法代表**线性变换的复合**。$AB$ 表示先应用 $B$ 变换，再应用 $A$ 变换。

几何解释：
- 矩阵 $A$ 将单位基向量变换为 $A$ 的列向量
- $AB$ 的列向量是 $A$ 对 $B$ 的列向量进行变换的结果

### Q3: 如何判断矩阵是否可逆？有哪些求逆方法？

**可逆条件**：
- 行列式 $\det(A) \neq 0$
- 满秩：$\text{rank}(A) = n$
- 所有特征值非零

**求逆方法**：
1. **伴随矩阵法**：$A^{-1} = \frac{1}{\det(A)} \text{adj}(A)$（理论用，计算量大）
2. **高斯消元**：$[A|I] \rightarrow [I|A^{-1}]$
3. **LU分解**：$A = LU$，分别求逆
4. **SVD分解**：最稳定的数值方法

### Q4: 为什么矩阵乘法不满足交换律？

矩阵乘法代表变换的复合，而变换顺序通常影响结果。

反例：
- 旋转30°再缩放2倍 ≠ 缩放2倍再旋转30°
- 具体矩阵：$A = \begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix}$, $B = \begin{bmatrix} 1 & 0 \\ 1 & 1 \end{bmatrix}$

特殊情况下可交换：同时是对角矩阵、单位矩阵倍数、或满足特定关系。

### Q5: 什么是Hadamard积？与矩阵乘法有何区别？

**Hadamard积**（逐元素积）：$(A \circ B)_{ij} = a_{ij} \cdot b_{ij}$

区别：
| 运算 | 符号 | 结果维度 | 用途 |
|------|------|----------|------|
| 矩阵乘法 | $AB$ | $m \times n$ | 线性变换、复合操作 |
| Hadamard积 | $A \circ B$ | 相同 | 逐元素操作、激活函数 |

深度学习应用：
- 矩阵乘法：全连接层、卷积
- Hadamard积：Dropout、注意力掩码、逐层归一化

## 相关概念

### 数据结构
- [数组](../computer-science/data-structures/array.md) - 矩阵的底层存储
- [稀疏矩阵](../computer-science/data-structures/sparse-matrix.md) - 大规模稀疏数据存储

### 算法
- [动态规划](../computer-science/algorithms/dynamic-programming.md) - 矩阵链乘法优化
- [分治算法](../computer-science/algorithms/divide-conquer.md) - Strassen算法基础

### 复杂度分析
- [时间复杂度](../references/time-complexity.md) - 矩阵运算的渐近分析

### 系统实现
- [GPU加速计算](../ai-data-systems/gpu-computing.md) - CUDA矩阵运算
- [并行计算](../computer-science/distributed-systems/parallel-computing.md) - 分布式矩阵操作
