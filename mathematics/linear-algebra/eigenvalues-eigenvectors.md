# 特征值与特征向量 (Eigenvalues and Eigenvectors)

## 简介

特征值（Eigenvalue）与特征向量（Eigenvector）是线性代数中最深刻、最优美的概念之一。它们揭示了线性变换的本质结构——在变换中保持方向不变的"主轴"，以及沿这些主轴的"缩放因子"。

在机器学习、量子力学、振动分析、PageRank算法等领域，特征分解都是核心工具。

## 核心概念

### 定义

对于方阵 $A$，若存在非零向量 $\mathbf{v}$ 和标量 $\lambda$，使得：

$$
A\mathbf{v} = \lambda\mathbf{v}
$$

则称：
- $\lambda$ 为 **特征值**（Eigenvalue）
- $\mathbf{v}$ 为 **特征向量**（Eigenvector）

### 几何意义

```
┌─────────────────────────────────────────────────────────────┐
│                    特征向量的几何意义                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│     原始向量 v              变换后 Av = λv                  │
│          ↗                      ↗                           │
│        /                        / (方向不变)                 │
│       /                        /                             │
│      ●───────────→            ●───────────→ (长度缩放λ倍)    │
│                                                             │
│   线性变换 A 将特征向量 v 映射为 λv：                        │
│   - 方向不变（保持在同一直线上）                              │
│   - 长度缩放 λ 倍                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 特征方程

由 $A\mathbf{v} = \lambda\mathbf{v}$，得 $(A - \lambda I)\mathbf{v} = 0$。

有非零解当且仅当：

$$
\det(A - \lambda I) = 0
$$

此称为**特征方程**（Characteristic Equation）。左边是关于 $\lambda$ 的 $n$ 次多项式，称为**特征多项式**。

### 重要性质

| 性质 | 公式 | 说明 |
|------|------|------|
| **迹与特征值** | $\text{tr}(A) = \sum_{i=1}^{n} \lambda_i$ | 特征值之和等于迹 |
| **行列式与特征值** | $\det(A) = \prod_{i=1}^{n} \lambda_i$ | 特征值之积等于行列式 |
| **逆矩阵特征值** | $A^{-1}$ 的特征值为 $\frac{1}{\lambda_i}$ | 若 $A$ 可逆 |
| **幂矩阵特征值** | $A^k$ 的特征值为 $\lambda_i^k$ | 特征向量不变 |
| **转置特征值** | $A^T$ 与 $A$ 特征值相同 | 特征向量可能不同 |
| **相似矩阵** | $P^{-1}AP$ 与 $A$ 特征值相同 | 特征向量变为 $P^{-1}\mathbf{v}$ |

### 对称矩阵的特殊性质

若 $A = A^T$（实对称矩阵）：
- 所有特征值为**实数**
- 不同特征值对应的特征向量**相互正交**
- 存在**标准正交的特征向量基**
- 可对角化为 $A = Q\Lambda Q^T$，其中 $Q$ 为正交矩阵

## 数学原理

### 对角化

若 $n \times n$ 矩阵 $A$ 有 $n$ 个线性无关的特征向量，则 $A$ **可对角化**：

$$
A = P\Lambda P^{-1}
$$

其中：
- $P = [\mathbf{v}_1, \mathbf{v}_2, ..., \mathbf{v}_n]$（特征向量矩阵）
- $\Lambda = \text{diag}(\lambda_1, \lambda_2, ..., \lambda_n)$（特征值对角矩阵）

**应用**：
- 矩阵幂：$A^k = P\Lambda^k P^{-1}$
- 矩阵指数：$e^A = Pe^{\Lambda}P^{-1}$
- 解线性微分方程组

### 谱定理（Spectral Theorem）

对于实对称矩阵 $A$：

$$
A = Q\Lambda Q^T = \sum_{i=1}^{n} \lambda_i \mathbf{q}_i \mathbf{q}_i^T
$$

其中 $Q$ 为正交矩阵（$Q^TQ = QQ^T = I$），列向量为标准正交特征向量。

这是**主成分分析（PCA）**的理论基础。

### 广义特征值问题

对于矩阵对 $(A, B)$，求解：

$$
A\mathbf{v} = \lambda B\mathbf{v}
$$

应用：
- 振动分析中的模态分析
- 判别分析（Fisher's Linear Discriminant）
- 正则化优化问题

## 示例

```python
import numpy as np
from numpy.linalg import eig, eigh, norm
import matplotlib.pyplot as plt

# ==================== 基础特征值计算 ====================

# 定义矩阵
A = np.array([[4, 2],
              [1, 3]], dtype=float)

print("矩阵 A:")
print(A)

# 计算特征值和特征向量
eigenvalues, eigenvectors = eig(A)
print("\n特征值:", eigenvalues)
print("特征向量（列向量）:")
print(eigenvectors)

# 验证 Av = λv
print("\n验证 Av = λv:")
for i in range(len(eigenvalues)):
    v = eigenvectors[:, i]
    lhs = A @ v
    rhs = eigenvalues[i] * v
    print(f"λ = {eigenvalues[i]:.4f}: ||Av - λv|| = {norm(lhs - rhs):.2e}")

# ==================== 对称矩阵特征分解 ====================

# 对称矩阵
S = np.array([[4, 2, 1],
              [2, 5, 3],
              [1, 3, 6]], dtype=float)

print("\n" + "="*50)
print("对称矩阵特征分解")
print("="*50)
print("对称矩阵 S:")
print(S)

# 使用eigh（针对Hermitian/symmetric矩阵优化）
eigvals_symm, eigvecs_symm = eigh(S)

print("\n特征值（升序）:", eigvals_symm)
print("特征向量:")
print(eigvecs_symm)

# 验证正交性: Q^T Q = I
print("\n验证正交性 (Q^T Q ≈ I):")
print(np.round(eigvecs_symm.T @ eigvecs_symm, 10))

# 重构 S = QΛQ^T
Lambda = np.diag(eigvals_symm)
S_reconstructed = eigvecs_symm @ Lambda @ eigvecs_symm.T
print("\n重构误差 ||S - QΛQ^T||:", norm(S - S_reconstructed))

# ==================== 矩阵幂的计算 ====================

print("\n" + "="*50)
print("利用特征分解计算矩阵幂")
print("="*50)

B = np.array([[2, 1],
              [1, 2]], dtype=float)

# 特征分解
eigvals_B, eigvecs_B = eig(B)

# 计算 B^10
k = 10
Lambda_k = np.diag(eigvals_B ** k)
B_power_k = eigvecs_B @ Lambda_k @ np.linalg.inv(eigvecs_B)

# 直接计算验证
B_power_k_direct = np.linalg.matrix_power(B, k)

print(f"B^{k} (通过特征分解):")
print(B_power_k)
print(f"\nB^{k} (直接计算):")
print(B_power_k_direct)
print(f"\n误差: {norm(B_power_k - B_power_k_direct):.2e}")

# ==================== 矩阵指数 ====================

from scipy.linalg import expm

print("\n" + "="*50)
print("矩阵指数 e^A")
print("="*50)

C = np.array([[0, 1],
              [-1, 0]], dtype=float)  # 旋转生成元

# 通过特征分解计算（理论）
eigvals_C, eigvecs_C = eig(C)
exp_lambda = np.exp(eigvals_C)
exp_C_via_eig = eigvecs_C @ np.diag(exp_lambda) @ np.linalg.inv(eigvecs_C)

# 使用scipy计算
exp_C_direct = expm(C)

print("矩阵 C (旋转生成元):")
print(C)
print("\ne^C (通过特征分解):")
print(exp_C_via_eig)
print("\ne^C (直接计算):")
print(exp_C_direct)

# ==================== PageRank 简化示例 ====================

print("\n" + "="*50)
print("PageRank 算法示例 (幂迭代)")
print("="*50)

# 简化的网页链接图: 4个页面
# 0 -> 1, 2
# 1 -> 2, 3
# 2 -> 0, 3
# 3 -> 0, 1, 2

# 构建转移矩阵 (列随机)
M = np.array([
    [0,    0,    0.5,  1/3],   # 到页面0的概率
    [0.5,  0,    0,    1/3],   # 到页面1的概率
    [0.5,  0.5,  0,    1/3],   # 到页面2的概率
    [0,    0.5,  0.5,  0   ]    # 到页面3的概率
])

print("转移矩阵 M:")
print(M)

# 计算特征值
eigvals_M, eigvecs_M = eig(M)

# 找到特征值1对应的特征向量（PageRank）
idx = np.argmin(np.abs(eigvals_M - 1))
pagerank = eigvecs_M[:, idx].real
pagerank = pagerank / np.sum(pagerank)  # 归一化

print("\n特征值:", np.round(eigvals_M, 4))
print("\nPageRank (特征值1对应的特征向量):")
print(pagerank)

# 幂迭代验证
r = np.ones(4) / 4
for _ in range(100):
    r = M @ r
print("\n幂迭代结果 (100次):")
print(r)

# ==================== 主成分分析 (PCA) 基础 ====================

print("\n" + "="*50)
print("PCA: 协方差矩阵特征分解")
print("="*50)

# 生成二维数据
np.random.seed(42)
n_samples = 100

# 相关数据
data = np.random.multivariate_normal(
    mean=[0, 0],
    cov=[[3, 2],
         [2, 2]],
    size=n_samples
)

# 数据中心化
data_centered = data - np.mean(data, axis=0)

# 计算协方差矩阵
cov_matrix = (data_centered.T @ data_centered) / (n_samples - 1)
print("协方差矩阵:")
print(cov_matrix)

# 特征分解（协方差矩阵是对称的）
eigvals_cov, eigvecs_cov = eigh(cov_matrix)

# 按特征值降序排列
idx = np.argsort(eigvals_cov)[::-1]
eigvals_cov = eigvals_cov[idx]
eigvecs_cov = eigvecs_cov[:, idx]

print("\n特征值 (方差解释):", eigvals_cov)
print("特征向量 (主成分方向):")
print(eigvecs_cov)

# 方差解释比例
explained_variance_ratio = eigvals_cov / np.sum(eigvals_cov)
print("方差解释比例:", explained_variance_ratio)

# 投影到第一主成分
pc1_projection = data_centered @ eigvecs_cov[:, 0]
print(f"\n投影到第一主成分后的方差: {np.var(pc1_projection):.4f}")

# ==================== 可视化特征向量 ====================

def plot_transformation(matrix, title):
    """可视化矩阵变换对单位圆的影响"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 计算特征值和特征向量
    eigvals, eigvecs = eig(matrix)
    
    # 生成单位圆上的点
    theta = np.linspace(0, 2*np.pi, 100)
    circle = np.array([np.cos(theta), np.sin(theta)])
    
    # 原始单位圆
    axes[0].plot(circle[0], circle[1], 'b-', label='Unit Circle')
    axes[0].axhline(y=0, color='k', linewidth=0.5)
    axes[0].axvline(x=0, color='k', linewidth=0.5)
    axes[0].set_aspect('equal')
    axes[0].set_title('Before Transformation')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    
    # 变换后的椭圆
    transformed = matrix @ circle
    axes[1].plot(transformed[0], transformed[1], 'r-', label='Transformed')
    
    # 绘制特征向量方向
    for i, (val, vec) in enumerate(zip(eigvals, eigvecs.T)):
        scaled_vec = vec * np.sqrt(abs(val))
        axes[1].arrow(0, 0, scaled_vec[0], scaled_vec[1], 
                     head_width=0.1, head_length=0.1, 
                     fc='green', ec='green', linewidth=2,
                     label=f'λ={val:.2f}' if i == 0 else '')
        axes[1].arrow(0, 0, -scaled_vec[0], -scaled_vec[1],
                     head_width=0.1, head_length=0.1,
                     fc='green', ec='green', linewidth=2)
    
    axes[1].axhline(y=0, color='k', linewidth=0.5)
    axes[1].axvline(x=0, color='k', linewidth=0.5)
    axes[1].set_aspect('equal')
    axes[1].set_title(f'After: {title}')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    
    plt.tight_layout()
    return fig

# 示例：对角缩放矩阵
D = np.array([[3, 0],
              [0, 1]], dtype=float)
print("\n" + "="*50)
print("可视化: 对角缩放变换")
print("="*50)
print("矩阵:", D.tolist())
print("特征值: [3, 1]")
print("特征向量: [[1, 0], [0, 1]] (标准基)")

# 示例：旋转变换
angle = np.pi / 6  # 30度
R = np.array([[np.cos(angle), -np.sin(angle)],
              [np.sin(angle), np.cos(angle)]], dtype=float)
print("\n旋转矩阵:", np.round(R, 4).tolist())
print("旋转矩阵特征值: 复数 (无实特征向量)")

# 示例：剪切变换
Shear = np.array([[1, 1],
                  [0, 1]], dtype=float)
print("\n剪切矩阵:", Shear.tolist())
eigvals_shear, _ = eig(Shear)
print("特征值:", eigvals_shear)
```

## 应用场景

### 1. 主成分分析（PCA）
- **协方差矩阵**的特征分解
- 特征向量 = 主成分方向
- 特征值 = 方差大小

### 2. PageRank算法
- 将网页链接建模为**转移矩阵**
- 平稳分布 = 特征值1对应的特征向量
- 幂迭代：$\mathbf{r}_{k+1} = M\mathbf{r}_k$

### 3. 振动分析与模态分析
- 特征值 = 固有频率的平方
- 特征向量 = 振型（模态形状）
- 用于结构工程、声学设计

### 4. 图分析与谱聚类
- **图拉普拉斯矩阵** $L = D - A$
- 特征向量用于图嵌入和聚类
- 谱图理论的基础

### 5. 深度学习
- **注意力机制**：特征值分析理解注意力权重
- **归一化流**：行列式计算使用特征值
- **稳定性分析**：RNN/LSTM的动态分析

### 6. 量子力学
- 可观测量 = 厄米特矩阵
- 特征值 = 测量结果
- 特征向量 = 量子态

## 面试要点

### Q1: 特征值和特征向量的几何意义是什么？

**核心回答**：
特征向量是线性变换中**只被拉伸、不被旋转**的方向。特征值是该方向上拉伸的倍数。

**几何理解**：
- 单位圆经过线性变换变成椭圆
- 椭圆的主轴方向就是特征向量方向
- 主轴长度比例就是特征值

**重要性**：
特征分解将复杂的线性变换分解为沿特定方向的简单缩放，揭示了变换的本质结构。

### Q2: 什么条件下矩阵可以对角化？

**可对角化的充要条件**：
1. 矩阵有 $n$ 个线性无关的特征向量
2. 每个特征值的几何重数 = 代数重数

**总是可对角化的矩阵**：
- 对称矩阵（$A = A^T$）
- 正规矩阵（$A^*A = AA^*$）
- 有 $n$ 个不同特征值的矩阵

**不可对角化的例子**：
$\begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix}$（Jordan块，代数重数2，几何重数1）

### Q3: 对称矩阵的特征值有什么特殊性质？

1. **特征值都是实数**
2. **不同特征值对应的特征向量正交**
3. **总可以选取一组标准正交的特征向量基**
4. **谱分解**：$A = Q\Lambda Q^T = \sum \lambda_i \mathbf{q}_i\mathbf{q}_i^T$

**应用**：
- PCA使用协方差矩阵（对称）的特征分解
- 物理中的惯性张量
- 图拉普拉斯矩阵（对称）

### Q4: 如何用特征分解计算矩阵的幂？

若 $A = P\Lambda P^{-1}$，则：

$$
A^k = P\Lambda^k P^{-1} = P \begin{bmatrix} \lambda_1^k & & \\ & \ddots & \\ & & \lambda_n^k \end{bmatrix} P^{-1}
$$

**复杂度分析**：
- 特征分解：$O(n^3)$（一次）
- 每次幂运算：$O(n^3)$（矩阵乘法）
- 通过特征分解后：$O(n^3 + kn^2)$ 对于计算多个幂

### Q5: 数值计算特征值时可能遇到什么问题？

**数值稳定性问题**：
1. **病态矩阵**：相近的特征值导致特征向量计算不稳定
2. **大型矩阵**：$O(n^3)$ 复杂度，不适合大规模问题
3. **复数特征值**：实矩阵可能有复数特征值

**解决方法**：
1. **QR算法**：最常用的数值稳定方法
2. **幂迭代**：求最大/最小特征值
3. **Lanczos/Arnoldi迭代**：大型稀疏矩阵
4. **随机SVD**：大规模近似计算

### Q6: 广义特征值问题是什么？应用场景？

**定义**：求解 $A\mathbf{v} = \lambda B\mathbf{v}$

**应用场景**：
- **Fisher判别分析**：类间散度 / 类内散度最大化
- **振动分析**：$K\mathbf{x} = \omega^2 M\mathbf{x}$
- **正则化最小二乘**：$A^TA\mathbf{x} + \lambda I\mathbf{x} = A^T\mathbf{b}$

## 相关概念

### 数据结构
- [矩阵运算](./matrix-operations.md) - 特征分解的基础运算
- [稀疏矩阵](../computer-science/data-structures/sparse-matrix.md) - 大规模特征问题

### 算法
- [SVD分解](./svd.md) - 与特征分解的关系
- [PCA应用](./applications-in-cs.md) - 特征分解的实际应用
- [幂迭代](../computer-science/algorithms/numerical-methods.md) - 特征值计算算法

### 复杂度分析
- [时间复杂度](../references/time-complexity.md) - 特征分解复杂度 $O(n^3)$

### 系统实现
- [机器学习应用](./applications-in-cs.md) - 特征分解在ML中的使用
- [数值计算库](../software-engineering/libraries/numpy-scipy.md) - 特征值计算实现
