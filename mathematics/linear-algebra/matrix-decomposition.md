# 矩阵分解 (Matrix Decomposition)

## 简介

矩阵分解（Matrix Decomposition）是将矩阵表示为若干更简单矩阵乘积的技术。如同整数可以分解为质因数，矩阵也可以"分解"为具有特定性质的因子矩阵。

矩阵分解是数值线性代数的核心，在求解线性方程组、最小二乘问题、特征值计算、数据降维等领域有广泛应用。

## 核心概念

### 为什么需要矩阵分解？

```
┌─────────────────────────────────────────────────────────────┐
│                    矩阵分解的价值                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   原始问题              分解后                求解          │
│   ─────────            ────────              ────          │
│                                                             │
│   Ax = b      ──→    LUx = b      ──→    先解 Ly = b       │
│                       (LU)                   再解 Ux = y    │
│                                                             │
│   A^k         ──→    P D^k P^-1   ──→    仅需计算对角幂    │
│                                                             │
│   min||Ax-b||  ──→   QR分解        ──→    上三角方程求解   │
│                                                             │
│   降维         ──→   SVD           ──→    低秩近似         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 常见分解概览

| 分解 | 形式 | 适用矩阵 | 主要应用 |
|------|------|----------|----------|
| **LU分解** | $A = LU$ | 方阵 | 解线性方程组 |
| **Cholesky** | $A = LL^T$ | 对称正定 | 优化、采样 |
| **QR分解** | $A = QR$ | 任意 | 最小二乘、特征值 |
| **特征分解** | $A = P\Lambda P^{-1}$ | 可对角化 | 矩阵幂、微分方程 |
| **SVD** | $A = U\Sigma V^T$ | 任意 | 降维、压缩、推荐 |
| **Schur分解** | $A = UTU^*$ | 任意方阵 | 数值稳定性 |

## 数学原理

### 1. LU分解

将矩阵 $A$ 分解为下三角矩阵 $L$（对角线为1）和上三角矩阵 $U$ 的乘积：

$$
A = LU = \begin{bmatrix} 1 & 0 & \cdots & 0 \\ l_{21} & 1 & \cdots & 0 \\ \vdots & \vdots & \ddots & \vdots \\ l_{n1} & l_{n2} & \cdots & 1 \end{bmatrix} \begin{bmatrix} u_{11} & u_{12} & \cdots & u_{1n} \\ 0 & u_{22} & \cdots & u_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ 0 & 0 & \cdots & u_{nn} \end{bmatrix}
$$

**求解 $Ax = b$**：
1. 前向替换：$Ly = b$
2. 后向替换：$Ux = y$

**复杂度**：分解 $O(n^3)$，求解 $O(n^2)$

**带主元的LU分解**（PLU）：$PA = LU$，提高数值稳定性

### 2. Cholesky分解

对于**对称正定矩阵** $A$，存在唯一的下三角矩阵 $L$：

$$
A = LL^T
$$

元素计算公式：

$$
l_{jj} = \sqrt{a_{jj} - \sum_{k=1}^{j-1} l_{jk}^2}
$$

$$
l_{ij} = \frac{1}{l_{jj}}\left(a_{ij} - \sum_{k=1}^{j-1} l_{ik}l_{jk}\right), \quad i > j
$$

**复杂度**：$O(n^3/3)$，约为LU的一半

### 3. QR分解

将矩阵 $A$（$m \times n$，$m \geq n$）分解为正交矩阵 $Q$ 和上三角矩阵 $R$：

$$
A = QR
$$

其中 $Q^TQ = I$，$R$ 是上三角矩阵。

**计算方法**：
- **Gram-Schmidt正交化**：理论简单，数值不稳定
- **Householder变换**：数值稳定，最常用
- **Givens旋转**：适合稀疏矩阵

**最小二乘问题**：

$$
\min_x \|Ax - b\|^2 = \min_x \|QRx - b\|^2 = \min_x \|Rx - Q^Tb\|^2
$$

### 4. 特征分解与谱分解

详见 [特征值与特征向量](./eigenvalues-eigenvectors.md)

### 5. SVD分解

详见 [奇异值分解](./svd.md)

## 示例

```python
import numpy as np
from scipy.linalg import lu, qr, cholesky, solve_triangular
from numpy.linalg import svd, eig, norm

# ==================== LU分解 ====================

print("=" * 60)
print("LU分解")
print("=" * 60)

A = np.array([[2, 1, 1],
              [4, 3, 3],
              [8, 7, 9]], dtype=float)

print("矩阵 A:")
print(A)

# LU分解 (带部分主元)
P, L, U = lu(A)

print("\n置换矩阵 P:")
print(P)
print("\n下三角矩阵 L:")
print(L)
print("\n上三角矩阵 U:")
print(U)

# 验证 PA = LU
print("\n验证 PA ≈ LU:")
print("PA =")
print(P @ A)
print("LU =")
print(L @ U)
print("误差:", norm(P @ A - L @ U))

# 使用LU分解求解 Ax = b
b = np.array([4, 10, 26], dtype=float)

# 解 Ly = Pb (前向替换)
y = solve_triangular(L, P @ b, lower=True)
print(f"\n中间解 y: {y}")

# 解 Ux = y (后向替换)
x = solve_triangular(U, y, lower=False)
print(f"解 x: {x}")

# 验证
print(f"验证 Ax = b: A @ x = {A @ x}")

# ==================== Cholesky分解 ====================

print("\n" + "=" * 60)
print("Cholesky分解")
print("=" * 60)

# 对称正定矩阵
S = np.array([[4, 2, 1],
              [2, 5, 3],
              [1, 3, 6]], dtype=float)

print("对称正定矩阵 S:")
print(S)

# 验证正定性（所有特征值>0）
eigvals_S = eig(S)[0]
print(f"特征值: {eigvals_S} (全部>0，确认正定)")

# Cholesky分解
L_chol = cholesky(S, lower=True)
print("\nCholesky因子 L:")
print(L_chol)

# 验证 S = LL^T
print("\n验证 S = LL^T:")
print("LL^T =")
print(L_chol @ L_chol.T)
print("误差:", norm(S - L_chol @ L_chol.T))

# 应用：从标准正态分布采样到多元正态
print("\n应用: 多元正态分布采样")
mu = np.array([1, 2, 3])
# 使用Cholesky生成相关样本
n_samples = 5
z = np.random.randn(n_samples, 3)
samples = mu + z @ L_chol.T
print(f"均值: {mu}")
print("生成的样本:")
print(samples)

# ==================== QR分解 ====================

print("\n" + "=" * 60)
print("QR分解")
print("=" * 60)

# 超定方程组 (m > n)
A_ls = np.array([[1, 1],
                 [1, 2],
                 [1, 3],
                 [1, 4]], dtype=float)

print("矩阵 A (4×2):")
print(A_ls)

# QR分解
Q, R = qr(A_ls, mode='reduced')  # 经济型QR

print("\n正交矩阵 Q (4×2):")
print(Q)
print("\n验证 Q^T Q = I:")
print(np.round(Q.T @ Q, 10))

print("\n上三角矩阵 R (2×2):")
print(R)

# 验证 A = QR
print("\n验证 A ≈ QR:")
print("QR =")
print(Q @ R)
print("误差:", norm(A_ls - Q @ R))

# 最小二乘求解: min ||Ax - b||
b_ls = np.array([2, 3, 5, 7], dtype=float)
print(f"\n最小二乘问题: ||Ax - b||, b = {b_ls}")

# 解法: R x = Q^T b
c = Q.T @ b_ls
x_ls = solve_triangular(R, c)
print(f"最小二乘解 x: {x_ls}")

# 验证
residual = A_ls @ x_ls - b_ls
print(f"残差 ||Ax - b||: {norm(residual):.4f}")

# 与numpy的lstsq比较
x_np = np.linalg.lstsq(A_ls, b_ls, rcond=None)[0]
print(f"numpy lstsq 解: {x_np}")

# ==================== 特征分解 ====================

print("\n" + "=" * 60)
print("特征分解 (对角化)")
print("=" * 60)

B = np.array([[4, 2],
              [1, 3]], dtype=float)

print("矩阵 B:")
print(B)

# 特征分解
eigvals, eigvecs = eig(B)

print(f"\n特征值: {eigvals}")
print("特征向量矩阵 P:")
print(eigvecs)

# 对角矩阵
Lambda = np.diag(eigvals)
print("\n对角矩阵 Λ:")
print(Lambda)

# 重构 B = P Λ P^-1
P_inv = np.linalg.inv(eigvecs)
B_reconstructed = eigvecs @ Lambda @ P_inv

print("\n验证 B = P Λ P^-1:")
print("重构的 B:")
print(B_reconstructed)
print("误差:", norm(B - B_reconstructed))

# 应用: 计算 B^100
k = 100
Lambda_k = np.diag(eigvals ** k)
B_power_100 = eigvecs @ Lambda_k @ P_inv
print(f"\nB^{k} (通过特征分解):")
print(B_power_100)

# ==================== SVD分解 ====================

print("\n" + "=" * 60)
print("SVD分解")
print("=" * 60)

# 任意矩阵（可以是非方阵）
C = np.array([[1, 2, 3],
              [4, 5, 6]], dtype=float)

print("矩阵 C (2×3):")
print(C)

# SVD分解
U, S, Vt = svd(C, full_matrices=False)

print(f"\n左奇异向量 U (2×2):")
print(U)
print(f"奇异值: {S}")
print(f"右奇异向量 V^T (2×3):")
print(Vt)

# 重构
Sigma = np.diag(S)
C_reconstructed = U @ Sigma @ Vt

print("\n验证 C = U Σ V^T:")
print("重构的 C:")
print(C_reconstructed)
print("误差:", norm(C - C_reconstructed))

# 低秩近似
print("\n低秩近似:")
for k in range(1, min(C.shape) + 1):
    C_approx = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
    error = norm(C - C_approx, 'fro')
    print(f"秩{k}近似误差 (Frobenius范数): {error:.4f}")

# ==================== 对比各种分解 ====================

print("\n" + "=" * 60)
print("分解方法对比")
print("=" * 60)

def compare_decompositions(matrix, name):
    """对比不同分解方法的特性和复杂度"""
    print(f"\n矩阵: {name}")
    print(matrix)
    
    n = matrix.shape[0]
    
    # LU
    try:
        _, L, U = lu(matrix)
        print(f"✓ LU分解: 适用于一般方阵")
    except:
        print("✗ LU分解失败")
    
    # Cholesky (仅对称正定)
    if np.allclose(matrix, matrix.T):
        try:
            L_chol = cholesky(matrix, lower=True)
            print(f"✓ Cholesky分解: 对称正定，复杂度 O(n³/3)")
        except:
            print("✗ Cholesky分解失败（非正定）")
    
    # 特征分解 (仅方阵)
    try:
        eigvals, eigvecs = eig(matrix)
        if np.allclose(matrix @ eigvecs, eigvecs @ np.diag(eigvals)):
            print(f"✓ 特征分解: 可对角化")
        else:
            print("~ 特征分解: 数值误差较大")
    except:
        print("✗ 特征分解失败")
    
    # SVD (总是可行)
    U, S, Vt = svd(matrix)
    print(f"✓ SVD分解: 总是可行，最稳定，复杂度 O(mn²)")

# 对称正定矩阵
S_pd = np.array([[2, 1],
                 [1, 2]], dtype=float)
compare_decompositions(S_pd, "对称正定矩阵")

# 一般方阵
A_general = np.array([[1, 2],
                      [3, 4]], dtype=float)
compare_decompositions(A_general, "一般方阵")

# ==================== 实际应用：协方差矩阵分解 ====================

print("\n" + "=" * 60)
print("实际应用：协方差矩阵的各种分解")
print("=" * 60)

# 生成数据
np.random.seed(42)
data = np.random.multivariate_normal([0, 0], [[2, 1], [1, 3]], 100)

# 计算协方差矩阵
cov_matrix = np.cov(data.T)
print("协方差矩阵:")
print(cov_matrix)

print("\n1. Cholesky分解 (用于生成相关随机数):")
L = cholesky(cov_matrix, lower=True)
print("L =")
print(L)

print("\n2. 特征分解 (PCA的基础):")
eigvals_cov, eigvecs_cov = eig(cov_matrix)
idx = np.argsort(eigvals_cov)[::-1]
eigvals_cov = eigvals_cov[idx]
eigvecs_cov = eigvecs_cov[:, idx]
print("特征值 (方差):", eigvals_cov)
print("特征向量 (主成分方向):")
print(eigvecs_cov)

print("\n3. SVD分解 (数值最稳定):")
U_svd, S_svd, Vt_svd = svd(cov_matrix)
print("奇异值:", S_svd)
print("注意: 对于对称矩阵，奇异值 = |特征值|")

# ==================== 矩阵求逆的各种方法 ====================

print("\n" + "=" * 60)
print("矩阵求逆的不同分解方法")
print("=" * 60)

D = np.array([[4, 7],
              [2, 6]], dtype=float)
print("矩阵 D:")
print(D)

# 方法1: 直接求逆
D_inv_direct = np.linalg.inv(D)
print("\n1. 直接求逆:")
print(D_inv_direct)

# 方法2: LU分解求逆
P, L, U = lu(D)
# D = P^T L U
# D^-1 = U^-1 L^-1 P
I = np.eye(2)
D_inv_lu = np.zeros_like(D)
for i in range(2):
    # 解 D x = e_i
    y = solve_triangular(L, P @ I[:, i], lower=True)
    D_inv_lu[:, i] = solve_triangular(U, y, lower=False)

print("\n2. LU分解求逆:")
print(D_inv_lu)

# 方法3: SVD求逆 (最稳定)
U_svd, S_svd, Vt_svd = svd(D)
# D = U Σ V^T
# D^-1 = V Σ^-1 U^T
S_inv = np.diag(1.0 / S_svd)
D_inv_svd = Vt_svd.T @ S_inv @ U_svd.T

print("\n3. SVD求逆 (最数值稳定):")
print(D_inv_svd)

print("\n验证: D @ D^-1 = I")
print("直接求逆:", np.round(D @ D_inv_direct, 10))
print("LU求逆:", np.round(D @ D_inv_lu, 10))
print("SVD求逆:", np.round(D @ D_inv_svd, 10))
```

## 应用场景

### 1. 线性方程组求解
- **LU分解**：多次求解相同系数矩阵的问题
- **Cholesky**：对称正定系统的优化求解

### 2. 最小二乘问题
- **QR分解**：数值稳定的最小二乘求解
- **SVD**：病态问题的稳健求解

### 3. 数据降维与压缩
- **SVD**：图像压缩、推荐系统、降噪
- **特征分解**：PCA、谱聚类

### 4. 优化问题
- **Cholesky**：高斯过程的协方差矩阵处理
- **LU/KKT**：约束优化问题的求解

### 5. 机器学习
- **矩阵分解**：协同过滤、潜在因子模型
- **SVD++**：Netflix Prize 的核心算法

## 面试要点

### Q1: LU分解和Cholesky分解有什么区别？

| 特性 | LU分解 | Cholesky分解 |
|------|--------|--------------|
| 适用矩阵 | 一般方阵 | 对称正定矩阵 |
| 形式 | $A = LU$ | $A = LL^T$ |
| 存储需求 | $n^2$ | $n^2/2$ |
| 复杂度 | $O(n^3)$ | $O(n^3/3)$ |
| 数值稳定性 | 需要主元 | 天然稳定 |
| 唯一性 | 不唯一 | 唯一（正定情况下）|

**选择建议**：
- 对称正定 → Cholesky（快2倍）
- 一般方阵 → LU（带主元）

### Q2: 为什么QR分解适合求解最小二乘问题？

**几何解释**：
QR分解将 $A$ 的列空间转化为 $Q$ 的正交基。最小二乘解是 $b$ 在 $A$ 列空间上的正交投影。

**数值优势**：
1. **避免计算 $A^TA$**：直接求解，条件数不平方
2. **数值稳定**：正交变换保持范数
3. **上三角系统易解**：$Rx = Q^Tb$

**与正规方程对比**：
- 正规方程：$A^TAx = A^Tb$，复杂度低但条件数平方
- QR分解：复杂度较高但数值稳定

### Q3: SVD分解什么时候优于特征分解？

**SVD的优势**：
1. **适用范围**：任意矩阵（非方阵也可）
2. **总是存在**：无需可对角化条件
3. **数值稳定**：计算过程更稳定
4. **低秩近似**：截断SVD给出最优低秩近似

**选择建议**：
| 场景 | 推荐方法 |
|------|----------|
| 方阵、关注特征结构 | 特征分解 |
| 非方阵、降维 | SVD |
| 数值计算、大规模 | SVD（随机SVD） |
| 理论分析 | 均可 |

### Q4: 矩阵分解的时间复杂度如何？

| 分解 | 复杂度 | 备注 |
|------|--------|------|
| LU | $O(n^3)$ | 实际约 $\frac{2}{3}n^3$ |
| Cholesky | $O(n^3/3)$ | 对称性带来的优化 |
| QR (Householder) | $O(2mn^2 - \frac{2}{3}n^3)$ | $m \times n$ 矩阵 |
| 特征分解 | $O(n^3)$ | QR迭代 |
| SVD | $O(mn^2)$ | 通常比特征分解慢2-3倍 |

### Q5: 实际编程中如何选择分解方法？

**决策流程**：
```
矩阵是否对称正定？
├── 是 → Cholesky分解
└── 否 → 是否方阵？
    ├── 是 → 需要特征结构？
    │   ├── 是 → 特征分解
    │   └── 否 → LU分解（带主元）
    └── 否（或需要降维）→ SVD或QR
```

**库函数推荐**：
- NumPy/SciPy：`scipy.linalg.lu`, `numpy.linalg.qr`, `numpy.linalg.svd`
- 稀疏矩阵：`scipy.sparse.linalg`
- GPU加速：`cuSOLVER` (CUDA)

## 相关概念

### 数据结构
- [矩阵运算](./matrix-operations.md) - 分解的基础
- [稀疏矩阵](../computer-science/data-structures/sparse-matrix.md) - 大规模分解

### 算法
- [特征值与特征向量](./eigenvalues-eigenvectors.md) - 特征分解详情
- [SVD分解](./svd.md) - 奇异值分解详情
- [数值稳定性](../references/numerical-analysis.md) - 分解的数值问题

### 复杂度分析
- [时间复杂度](../references/time-complexity.md) - 分解复杂度分析

### 系统实现
- [线性方程组求解](../computer-science/algorithms/linear-equations.md) - 分解的应用
- [GPU计算](../ai-data-systems/gpu-computing.md) - 并行分解算法
