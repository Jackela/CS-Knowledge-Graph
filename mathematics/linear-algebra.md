# 线性代数 (Linear Algebra)

## 简介

**线性代数 (Linear Algebra)** 是研究向量空间和线性变换的数学分支。在现代计算机科学中，线性代数是机器学习、计算机图形学、数据科学、密码学等领域的核心数学工具。

```
┌─────────────────────────────────────────────────────────────┐
│                   线性代数核心内容                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │ 向量空间 │  │ 矩阵运算 │  │ 线性变换 │  │ 特征分解 │   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │ 矩阵分解 │  │ 内积空间 │  │ 张量计算 │  │ 奇异值分解│   │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 向量与向量空间

### 向量基础

```
向量：具有大小和方向的量

n维向量：v = (v₁, v₂, ..., vₙ) ∈ ℝⁿ

向量运算：
- 加法：u + v = (u₁+v₁, u₂+v₂, ..., uₙ+vₙ)
- 数乘：cv = (cv₁, cv₂, ..., cvₙ)
- 点积：u · v = u₁v₁ + u₂v₂ + ... + uₙvₙ = Σuᵢvᵢ

向量长度（模）：
||v|| = √(v · v) = √(v₁² + v₂² + ... + vₙ²)

夹角：
cos θ = (u · v) / (||u|| ||v||)

Python实现：
import numpy as np

u = np.array([1, 2, 3])
v = np.array([4, 5, 6])

# 点积
dot = np.dot(u, v)  # 32

# 模长
norm_u = np.linalg.norm(u)  # 3.74

# 夹角
cos_theta = dot / (norm_u * np.linalg.norm(v))
theta = np.arccos(cos_theta)
```

### 向量空间

```
向量空间 (Vector Space)：
满足8条公理的集合，包括：
1. 加法封闭性
2. 加法交换律
3. 加法结合律
4. 零元存在
5. 负元存在
6. 数乘封闭性
7. 数乘分配律
8. 数乘结合律

子空间 (Subspace)：
向量空间的子集，本身也是向量空间

基 (Basis)：
线性无关的向量组，能张成整个空间
维度 (Dimension)：基中向量的个数

标准基：
ℝ³中：e₁ = (1,0,0), e₂ = (0,1,0), e₃ = (0,0,1)
```

## 矩阵基础

### 矩阵定义与运算

```
矩阵：m×n 的矩形数组

A = [aᵢⱼ] = | a₁₁  a₁₂  ...  a₁ₙ |
            | a₂₁  a₂₂  ...  a₂ₙ |
            |  ⋮    ⋮   ⋱    ⋮  |
            | aₘ₁  aₘ₂  ...  aₘₙ |

基本运算：
- 加法：(A + B)ᵢⱼ = aᵢⱼ + bᵢⱼ
- 数乘：(cA)ᵢⱼ = c × aᵢⱼ
- 乘法：(AB)ᵢⱼ = Σₖ aᵢₖ × bₖⱼ

矩阵乘法性质：
- 结合律：(AB)C = A(BC)
- 分配律：A(B+C) = AB + AC
- 一般不满足交换律：AB ≠ BA

转置：(Aᵀ)ᵢⱼ = aⱼᵢ
性质：(AB)ᵀ = BᵀAᵀ

特殊矩阵：
- 单位矩阵 I：对角线为1，其余为0
- 对角矩阵：非对角线元素全为0
- 对称矩阵：A = Aᵀ
- 正交矩阵：AᵀA = AAᵀ = I
```

```python
import numpy as np

# 矩阵创建
A = np.array([[1, 2], [3, 4], [5, 6]])  # 3×2
B = np.array([[7, 8], [9, 10]])  # 2×2

# 矩阵乘法
C = np.dot(A, B)  # 或 A @ B，结果 3×2

# 转置
A_T = A.T

# 逆矩阵（方阵）
D = np.array([[1, 2], [3, 4]])
D_inv = np.linalg.inv(D)

# 验证逆矩阵
print(np.dot(D, D_inv))  # 接近单位矩阵
```

### 矩阵的秩

```
秩 (Rank)：矩阵中线性无关的行（或列）的最大数目

性质：
- rank(A) ≤ min(m, n)
- rank(A) = rank(Aᵀ)
- rank(AB) ≤ min(rank(A), rank(B))

满秩：
- 行满秩：rank = m
- 列满秩：rank = n
- 满秩方阵：rank = n（可逆）

计算：高斯消元后非零行的数量
```

## 线性方程组

### 解的存在性

```
线性方程组：Ax = b

A：m×n 系数矩阵
x：n×1 未知数向量
b：m×1 常数向量

解的情况：
1. 唯一解：rank(A) = rank([A|b]) = n
2. 无穷多解：rank(A) = rank([A|b]) < n
3. 无解：rank(A) < rank([A|b])

齐次方程 Ax = 0：
- 总有零解
- 有非零解当且仅当 rank(A) < n
- 解空间维数 = n - rank(A) (零化度)
```

### 求解方法

```python
import numpy as np

# 方法1：使用numpy.linalg.solve（方阵）
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
x = np.linalg.solve(A, b)

# 方法2：最小二乘法（超定方程组）
A = np.array([[1, 1], [1, 2], [1, 3], [1, 4]])
b = np.array([2, 3, 5, 7])
x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

# 方法3：LU分解
from scipy.linalg import lu_factor, lu_solve
lu, piv = lu_factor(A)
x = lu_solve((lu, piv), b)
```

## 特征值与特征向量

### 定义与计算

```
特征值与特征向量：

对于方阵A，若存在非零向量v和标量λ，使得：
Av = λv

则：
- λ 称为特征值 (Eigenvalue)
- v 称为特征向量 (Eigenvector)

求解：
Av = λv  ⟹  (A - λI)v = 0

有非零解当且仅当：
det(A - λI) = 0  （特征方程）

性质：
- 特征值之和 = 迹(trace)：Σλᵢ = Σaᵢᵢ
- 特征值之积 = 行列式：Πλᵢ = det(A)
- 对称矩阵的特征值都是实数
- 对称矩阵的特征向量两两正交
```

```python
import numpy as np

A = np.array([[4, 2], [1, 3]])

# 计算特征值和特征向量
eigenvalues, eigenvectors = np.linalg.eig(A)

print("特征值:", eigenvalues)
print("特征向量:", eigenvectors)

# 验证 Av = λv
for i in range(len(eigenvalues)):
    v = eigenvectors[:, i]
    lhs = np.dot(A, v)
    rhs = eigenvalues[i] * v
    print(f"λ={eigenvalues[i]}: Av ≈ λv ? {np.allclose(lhs, rhs)}")
```

### 特征分解

```
对角化：
若A有n个线性无关的特征向量，则：
A = PDP⁻¹

其中：
- P：特征向量组成的矩阵
- D：对角矩阵，对角线为特征值

应用：
- 矩阵幂：Aᵏ = PDᵏP⁻¹
- 矩阵指数：e^A = Pe^DP⁻¹
- 解微分方程

对称矩阵的谱分解：
A = QΛQᵀ

其中Q为正交矩阵（QᵀQ = I），Λ为对角矩阵
```

## 矩阵分解

### LU分解

```
LU分解：A = LU

- L：下三角矩阵（对角线为1）
- U：上三角矩阵

求解Ax = b：
1. Ly = b（前向替代）
2. Ux = y（后向替代）

时间复杂度：O(n³)分解，O(n²)求解
```

### QR分解

```
QR分解：A = QR

- Q：正交矩阵（QᵀQ = I）
- R：上三角矩阵

应用：
- 最小二乘法
- 特征值计算
- 正交化（Gram-Schmidt）
```

### 奇异值分解 (SVD)

```
SVD：A = UΣVᵀ

- U：m×m 正交矩阵（左奇异向量）
- Σ：m×n 对角矩阵（奇异值 σ₁ ≥ σ₂ ≥ ... ≥ 0）
- V：n×n 正交矩阵（右奇异向量）

与特征值关系：
- σᵢ = √λᵢ(AᵀA)
- U的列是AAᵀ的特征向量
- V的列是AᵀA的特征向量

低秩近似：
Aₖ = Σᵢ₌₁ᵏ σᵢuᵢvᵢᵀ

应用：
- 降维（PCA）
- 推荐系统
- 图像压缩
- 降噪
```

```python
import numpy as np

# SVD分解
A = np.array([[1, 2], [3, 4], [5, 6]])  # 3×2

U, S, Vt = np.linalg.svd(A, full_matrices=False)

print("U形状:", U.shape)      # (3, 2)
print("奇异值:", S)           # (2,)
print("Vt形状:", Vt.shape)    # (2, 2)

# 重构
Sigma = np.diag(S)
A_reconstructed = np.dot(U, np.dot(Sigma, Vt))
print("重构误差:", np.allclose(A, A_reconstructed))

# 低秩近似（取前k个奇异值）
k = 1
A_approx = np.dot(U[:, :k] * S[:k], Vt[:k, :])
print(f"秩{k}近似误差:", np.linalg.norm(A - A_approx))
```

## 内积空间

### 内积与正交性

```
内积 (Inner Product)：
<u, v> = uᵀv = Σuᵢvᵢ

性质：
1. 对称性：<u, v> = <v, u>
2. 线性性：<cu, v> = c<u, v>
3. 分配律：<u+v, w> = <u, w> + <v, w>
4. 正定性：<u, u> ≥ 0，等号当且仅当u=0

正交：<u, v> = 0

正交投影：
projᵥ(u) = (<u, v> / <v, v>) v

正交补：V的正交补是所有与V正交的向量
```

### Gram-Schmidt正交化

```
将给定向量组转化为正交向量组

算法：
给定线性无关向量 {v₁, v₂, ..., vₙ}

u₁ = v₁
u₂ = v₂ - proj_{u₁}(v₂)
u₃ = v₃ - proj_{u₁}(v₃) - proj_{u₂}(v₃)
...

然后单位化：eᵢ = uᵢ / ||uᵢ||

应用：
- QR分解
- 正交基构造
- 最小二乘问题
```

## 在机器学习中的应用

### 主成分分析 (PCA)

```
PCA：通过SVD进行降维

步骤：
1. 数据中心化（减去均值）
2. 计算协方差矩阵 C = XᵀX / (n-1)
3. 对C进行特征分解或X进行SVD
4. 取前k个主成分（最大特征值对应的特征向量）
5. 投影：Z = XW

SVD视角：
X = UΣVᵀ
主成分 = V的列（右奇异向量）
```

```python
from sklearn.decomposition import PCA
import numpy as np

# 数据
X = np.random.randn(100, 10)

# PCA降维
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X)

print("原始维度:", X.shape)
print("降维后:", X_reduced.shape)
print("解释方差比:", pca.explained_variance_ratio_)
```

### 线性回归

```
最小二乘法：
min ||Ax - b||²

解析解：x = (AᵀA)⁻¹Aᵀb

梯度下降：
x := x - αAᵀ(Ax - b)

几何解释：
在A的列空间中找到最接近b的向量
```

## 面试要点

### 常见问题

**Q1: 矩阵乘法的时间复杂度？**
> 标准矩阵乘法为O(n³)，Strassen算法为O(n^2.807)，当前最优理论算法低于O(n^2.373)。实践中使用分块和并行优化。

**Q2: 特征值和特征向量的几何意义？**> 特征向量是线性变换中只被拉伸不被旋转的方向，特征值是拉伸的倍数。特征分解揭示了线性变换的本质结构。

**Q3: 什么情况下矩阵可对角化？**> n×n矩阵可对角化当且仅当它有n个线性无关的特征向量。对称矩阵、正交矩阵、正规矩阵都可对角化。

**Q4: SVD与特征分解的区别？**> 特征分解只适用于方阵，要求有n个线性无关特征向量；SVD适用于任意矩阵，总是存在且唯一（奇异值有序）。PCA使用SVD而不是特征分解更数值稳定。

**Q5: 矩阵的秩的几何意义？**> 秩表示线性变换后输出空间的维度，即线性无关的列（或行）向量的最大数目。rank(A) = dim(col(A)) = dim(row(A))。

## 相关概念

- [概率论](./probability.md) - 多元统计基础
- [机器学习概述](../ai-data-systems/ml-overview.md) - 线性代数在ML中的应用
- [CNN](../ai-data-systems/cnn.md) - 卷积神经网络的矩阵运算
- [Transformer](../ai-data-systems/transformers.md) - 注意力机制的矩阵计算
- [RNN/LSTM](../ai-data-systems/rnn-lstm.md) - 循环神经网络的矩阵表示
- [动态规划](../computer-science/algorithms/dynamic-programming.md) - 矩阵链乘法与优化
- [图遍历](../computer-science/algorithms/graph-traversal.md) - 邻接矩阵与图算法
- [Kubernetes](../cloud-devops/kubernetes.md) - 分布式系统矩阵运算

1. "Linear Algebra Done Right" by Sheldon Axler
2. "Introduction to Linear Algebra" by Gilbert Strang
3. "Matrix Computations" by Golub & Van Loan
4. 3Blue1Brown线性代数系列（YouTube）
5. MIT 18.06 Linear Algebra（OpenCourseWare）
