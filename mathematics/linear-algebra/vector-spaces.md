# 向量空间 (Vector Spaces)

## 简介

向量空间（Vector Space），又称线性空间，是线性代数最基础、最抽象的概念。它将从几何向量、多项式、函数到矩阵等看似不同的数学对象统一在一个框架下，使得我们可以用统一的语言讨论"线性结构"。

理解向量空间是掌握线性变换、特征分析、泛函分析等高级概念的前提。

## 核心概念

### 向量空间的定义

设 $V$ 是一个非空集合，$\mathbb{F}$ 是一个数域（通常是 $\mathbb{R}$ 或 $\mathbb{C}$），如果在 $V$ 上定义了加法和数乘运算，并满足以下8条公理，则称 $V$ 是 $\mathbb{F}$ 上的向量空间：

| 公理 | 加法性质 | 数乘性质 |
|------|----------|----------|
| 1 | **封闭性**: $\mathbf{u} + \mathbf{v} \in V$ | **封闭性**: $c\mathbf{v} \in V$ |
| 2 | **交换律**: $\mathbf{u} + \mathbf{v} = \mathbf{v} + \mathbf{u}$ | **分配律**: $c(\mathbf{u} + \mathbf{v}) = c\mathbf{u} + c\mathbf{v}$ |
| 3 | **结合律**: $(\mathbf{u} + \mathbf{v}) + \mathbf{w} = \mathbf{u} + (\mathbf{v} + \mathbf{w})$ | **分配律**: $(c + d)\mathbf{v} = c\mathbf{v} + d\mathbf{v}$ |
| 4 | **零元**: $\exists \mathbf{0}, \mathbf{v} + \mathbf{0} = \mathbf{v}$ | **结合律**: $c(d\mathbf{v}) = (cd)\mathbf{v}$ |
| 5 | **负元**: $\exists (-\mathbf{v}), \mathbf{v} + (-\mathbf{v}) = \mathbf{0}$ | **单位元**: $1\mathbf{v} = \mathbf{v}$ |

### 常见的向量空间

```
┌─────────────────────────────────────────────────────────────┐
│                    常见的向量空间示例                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ℝⁿ: n维实向量空间                                         │
│   ├── (x₁, x₂, ..., xₙ) 形式的n元组                         │
│   └── 机器学习中的特征向量、数据点                          │
│                                                             │
│   ℝ^(m×n): m×n 实矩阵空间                                   │
│   ├── 所有m行n列的实矩阵                                    │
│   └── 深度学习中的权重矩阵、梯度                            │
│                                                             │
│   Pₙ: 次数≤n的多项式空间                                    │
│   ├── a₀ + a₁x + ... + aₙxⁿ                                 │
│   └── 插值、逼近理论                                        │
│                                                             │
│   C[a,b]: [a,b]上的连续函数空间                             │
│   ├── 无限维向量空间                                        │
│   └── 泛函分析、信号处理                                    │
│                                                             │
│   L²(ℝ): 平方可积函数空间                                   │
│   ├── ∫|f(x)|²dx < ∞ 的函数                                │
│   └── 量子力学、傅里叶分析                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 子空间

设 $W \subseteq V$，若 $W$ 关于 $V$ 的运算也构成向量空间，则称 $W$ 是 $V$ 的**子空间**。

**判定条件**（子空间判定定理）：
$W$ 是子空间当且仅当：
1. $\mathbf{0} \in W$（包含零向量）
2. $\mathbf{u}, \mathbf{v} \in W \Rightarrow \mathbf{u} + \mathbf{v} \in W$（加法封闭）
3. $\mathbf{v} \in W, c \in \mathbb{F} \Rightarrow c\mathbf{v} \in W$（数乘封闭）

**等价条件**：$a\mathbf{u} + b\mathbf{v} \in W$ 对所有 $\mathbf{u}, \mathbf{v} \in W$ 和 $a, b \in \mathbb{F}$ 成立

### 线性相关与线性无关

**定义**：
- 向量组 $\{\mathbf{v}_1, \mathbf{v}_2, ..., \mathbf{v}_n\}$ 称为**线性相关**，若存在不全为零的标量 $c_1, c_2, ..., c_n$ 使得：
  $$c_1\mathbf{v}_1 + c_2\mathbf{v}_2 + ... + c_n\mathbf{v}_n = \mathbf{0}$$
- 否则称为**线性无关**

**几何解释**：
- 线性相关：至少有一个向量可以表示为其他向量的线性组合
- 线性无关：每个向量都"贡献"新的方向

### 基与维度

**基（Basis）**：向量空间 $V$ 的一组基是 $V$ 的一个线性无关子集，且能张成整个空间 $V$。

**维度（Dimension）**：基中向量的个数，记作 $\dim(V)$。

**标准基示例**：
- $\mathbb{R}^3$：$\mathbf{e}_1 = (1,0,0), \mathbf{e}_2 = (0,1,0), \mathbf{e}_3 = (0,0,1)$
- $\mathbb{R}^{m \times n}$：$E_{ij}$（$(i,j)$位置为1，其余为0）
- $P_n$：$\{1, x, x^2, ..., x^n\}$

### 张成空间

给定向量组 $S = \{\mathbf{v}_1, \mathbf{v}_2, ..., \mathbf{v}_n\}$，其**张成空间**定义为：

$$\text{span}(S) = \{c_1\mathbf{v}_1 + c_2\mathbf{v}_2 + ... + c_n\mathbf{v}_n \mid c_i \in \mathbb{F}\}$$

即所有线性组合构成的集合，是包含 $S$ 的最小子空间。

## 数学原理

### 坐标与坐标变换

设 $\mathcal{B} = \{\mathbf{b}_1, \mathbf{b}_2, ..., \mathbf{b}_n\}$ 是 $V$ 的一组基，则任意 $\mathbf{v} \in V$ 可唯一表示为：

$$\mathbf{v} = x_1\mathbf{b}_1 + x_2\mathbf{b}_2 + ... + x_n\mathbf{b}_n$$

称 $[\mathbf{v}]_{\mathcal{B}} = (x_1, x_2, ..., x_n)^T$ 为 $\mathbf{v}$ 关于基 $\mathcal{B}$ 的**坐标**。

**基变换**：
设 $\mathcal{B}$ 和 $\mathcal{C}$ 是 $V$ 的两组基，**过渡矩阵** $P_{\mathcal{C} \leftarrow \mathcal{B}}$ 满足：

$$[\mathbf{v}]_{\mathcal{C}} = P_{\mathcal{C} \leftarrow \mathcal{B}} [\mathbf{v}]_{\mathcal{B}}$$

### 四个基本子空间

对于 $m \times n$ 矩阵 $A$，有四个重要的子空间：

| 子空间 | 定义 | 维度 | 关系 |
|--------|------|------|------|
| **列空间** $C(A)$ | $\{A\mathbf{x} \mid \mathbf{x} \in \mathbb{R}^n\}$ | $\text{rank}(A)$ | $\subseteq \mathbb{R}^m$ |
| **行空间** $C(A^T)$ | $\{A^T\mathbf{y} \mid \mathbf{y} \in \mathbb{R}^m\}$ | $\text{rank}(A)$ | $\subseteq \mathbb{R}^n$ |
| **零空间** $N(A)$ | $\{\mathbf{x} \mid A\mathbf{x} = \mathbf{0}\}$ | $n - \text{rank}(A)$ | $\subseteq \mathbb{R}^n$ |
| **左零空间** $N(A^T)$ | $\{\mathbf{y} \mid A^T\mathbf{y} = \mathbf{0}\}$ | $m - \text{rank}(A)$ | $\subseteq \mathbb{R}^m$ |

**正交关系**：
- $N(A) = C(A^T)^\perp$（零空间是行空间的正交补）
- $N(A^T) = C(A)^\perp$（左零空间是列空间的正交补）

### 直和分解

设 $U, W$ 是 $V$ 的子空间，若 $U \cap W = \{\mathbf{0}\}$，则定义**直和**：

$$U \oplus W = \{\mathbf{u} + \mathbf{w} \mid \mathbf{u} \in U, \mathbf{w} \in W\}$$

**性质**：
- $\dim(U \oplus W) = \dim(U) + \dim(W)$
- 每个向量 $\mathbf{v} \in U \oplus W$ 有唯一的分解 $\mathbf{v} = \mathbf{u} + \mathbf{w}$

**重要例子**：$\mathbb{R}^n = C(A^T) \oplus N(A)$

## 示例

```python
import numpy as np
from numpy.linalg import matrix_rank, qr, svd
from scipy.linalg import null_space, orth

# ==================== 线性相关与线性无关 ====================

print("=" * 60)
print("线性相关与线性无关")
print("=" * 60)

# 线性无关的向量
v1 = np.array([1, 0, 0])
v2 = np.array([0, 1, 0])
v3 = np.array([0, 0, 1])

print("向量组:")
print(f"v1 = {v1}")
print(f"v2 = {v2}")
print(f"v3 = {v3}")

# 构造矩阵并计算秩
V_indep = np.vstack([v1, v2, v3])
print(f"\n矩阵 V 的秩: {matrix_rank(V_indep)}")
print("秩 = 向量个数 (3)，说明线性无关")

# 线性相关的向量
print("\n" + "-" * 40)
w1 = np.array([1, 2, 3])
w2 = np.array([2, 4, 6])  # w2 = 2*w1
w3 = np.array([1, 1, 1])

print("\n向量组:")
print(f"w1 = {w1}")
print(f"w2 = {w2} = 2*w1")
print(f"w3 = {w3}")

V_dep = np.vstack([w1, w2, w3])
print(f"\n矩阵 V 的秩: {matrix_rank(V_dep)}")
print("秩 < 向量个数 (3)，说明线性相关")

# 找线性关系
# 解 V_dep^T * c = 0
coeffs = null_space(V_dep.T)
print(f"\n线性关系系数: {coeffs.flatten()}")
print("验证: c1*w1 + c2*w2 + c3*w3 = 0")

# ==================== 基与维度 ====================

print("\n" + "=" * 60)
print("基与维度")
print("=" * 60)

# 矩阵的列空间基
A = np.array([[1, 2, 3, 4],
              [2, 4, 6, 8],
              [1, 0, 1, 2]], dtype=float)

print("矩阵 A:")
print(A)
print(f"\n矩阵 A 的秩: {matrix_rank(A)}")

# 列空间的一组标准正交基
Q, _ = qr(A, mode='reduced')
col_space_basis = Q[:, :matrix_rank(A)]
print(f"\n列空间的维度: {matrix_rank(A)}")
print("列空间的一组标准正交基:")
print(col_space_basis)

# 零空间的基
null_basis = null_space(A)
print(f"\n零空间的维度: {null_basis.shape[1]}")
print("零空间的一组基:")
print(null_basis)

# 验证零空间
print("\n验证 A @ (零空间基) = 0:")
print(np.round(A @ null_basis, 10))

# ==================== 坐标与坐标变换 ====================

print("\n" + "=" * 60)
print("坐标与坐标变换")
print("=" * 60)

# 定义两组基
# 标准基
e1 = np.array([1, 0])
e2 = np.array([0, 1])
std_basis = np.column_stack([e1, e2])

# 新基 (旋转45度)
angle = np.pi / 4
b1 = np.array([np.cos(angle), np.sin(angle)])
b2 = np.array([-np.sin(angle), np.cos(angle)])
new_basis = np.column_stack([b1, b2])

print("标准基:")
print(std_basis)
print("\n新基 (旋转45°):")
print(new_basis)

# 向量 v 在标准基下的坐标
v_std = np.array([2, 0])
print(f"\n向量 v 在标准基下的坐标: {v_std}")

# 求 v 在新基下的坐标: v = x1*b1 + x2*b2
# 即 new_basis @ [x1, x2]^T = v_std
v_new = np.linalg.solve(new_basis, v_std)
print(f"向量 v 在新基下的坐标: {v_new}")

# 验证
v_reconstructed = new_basis @ v_new
print(f"验证重构: {v_reconstructed}")

# 过渡矩阵
# 从标准基到新基的过渡矩阵就是新基矩阵
P = new_basis
print(f"\n过渡矩阵 P (标准基 → 新基):")
print(P)

# ==================== 四个基本子空间 ====================

print("\n" + "=" * 60)
print("四个基本子空间")
print("=" * 60)

B = np.array([[1, 2, 0, 1],
              [2, 4, 1, 3],
              [3, 6, 1, 4]], dtype=float)

print("矩阵 B (3×4):")
print(B)

rank_B = matrix_rank(B)
print(f"\n矩阵 B 的秩: {rank_B}")

# 1. 列空间 (Column Space)
col_basis = orth(B)
print(f"\n1. 列空间 C(B):")
print(f"   维度: {col_basis.shape[1]}")
print(f"   一组标准正交基:")
print(col_basis)

# 2. 行空间 (Row Space)
row_basis = orth(B.T)
print(f"\n2. 行空间 C(B^T):")
print(f"   维度: {row_basis.shape[1]}")
print(f"   一组标准正交基 (转置后):")
print(row_basis.T)

# 3. 零空间 (Null Space)
null_B = null_space(B)
print(f"\n3. 零空间 N(B):")
print(f"   维度 (零化度): {null_B.shape[1]} = n - rank = {B.shape[1]} - {rank_B}")
print(f"   一组基:")
print(null_B)

# 4. 左零空间 (Left Null Space)
left_null_B = null_space(B.T)
print(f"\n4. 左零空间 N(B^T):")
print(f"   维度: {left_null_B.shape[1]} = m - rank = {B.shape[0]} - {rank_B}")
print(f"   一组基:")
print(left_null_B)

# 验证正交关系
print("\n" + "-" * 40)
print("验证正交关系:")
print(f"行空间与零空间正交: {np.allclose(row_basis.T @ null_B, 0)}")
print(f"列空间与左零空间正交: {np.allclose(col_basis.T @ left_null_B, 0)}")

# ==================== 张成空间 ====================

print("\n" + "=" * 60)
print("张成空间")
print("=" * 60)

# 给定向量组
vectors = [
    np.array([1, 1, 0]),
    np.array([1, 0, 1]),
    np.array([0, 1, 1]),
    np.array([2, 2, 0])  # 这个与前一个线性相关
]

print("给定向量组:")
for i, v in enumerate(vectors):
    print(f"  v{i+1} = {v}")

# 构造矩阵
V_matrix = np.vstack(vectors).T
print(f"\n向量组矩阵 (按列):")
print(V_matrix)

# 张成空间的维度
span_dim = matrix_rank(V_matrix)
print(f"\n张成空间的维度: {span_dim}")

# 找出一组基
span_basis = orth(V_matrix)
print(f"\n张成空间的一组标准正交基:")
print(span_basis)

# 判断向量是否在张成空间中
test_vector = np.array([3, 2, 2])
print(f"\n测试向量: {test_vector}")

# 尝试表示为线性组合
try:
    # 使用伪逆求解最小二乘
    coeffs = np.linalg.lstsq(V_matrix, test_vector, rcond=None)[0]
    residual = test_vector - V_matrix @ coeffs
    
    if np.allclose(residual, 0):
        print(f"该向量在张成空间中")
        print(f"线性组合系数: {coeffs}")
    else:
        print(f"该向量不在张成空间中")
        print(f"最近近似系数: {coeffs}")
        print(f"残差: {np.linalg.norm(residual):.4f}")
except:
    print("求解失败")

# ==================== 子空间判定 ====================

print("\n" + "=" * 60)
print("子空间判定")
print("=" * 60)

def is_subspace(V, W_generators, tolerance=1e-10):
    """
    判定由 W_generators 张成的空间是否是 V 的子空间
    V: 母空间的基矩阵
    W_generators: 待判定子空间的生成向量
    """
    # 检查每个生成向量是否在V的张成空间中
    for w in W_generators:
        # 解 V @ x = w
        coeffs = np.linalg.lstsq(V, w, rcond=None)[0]
        residual = w - V @ coeffs
        if np.linalg.norm(residual) > tolerance:
            return False
    return True


# 定义 ℝ³ 的标准基
R3_basis = np.eye(3)

# 测试1: xy平面是否是子空间
xy_plane = [np.array([1, 0, 0]), np.array([0, 1, 0])]
print("ℝ³ 中的 xy 平面:")
print(f"  是子空间? {is_subspace(R3_basis, xy_plane)}")

# 测试2: 过原点的直线
line = [np.array([1, 1, 1])]
print("\n过原点的直线 (方向 [1,1,1]):")
print(f"  是子空间? {is_subspace(R3_basis, line)}")

# 测试3: 不过原点的平面（不是子空间）
# 注意：实际的集合应该是 {v + b | v ∈ span{[1,0,0], [0,1,0]}}
# 这无法通过生成向量直接表示，但概念上不是子空间

# ==================== 维数公式 ====================

print("\n" + "=" * 60)
print("维数公式")
print("=" * 60)

# 定义两个子空间
# U: x轴上的所有向量
U_basis = np.array([[1, 0, 0]]).T

# W: xy平面上的所有向量
W_basis = np.array([[1, 0, 0], [0, 1, 0]]).T

print("子空间 U (x轴):")
print(f"  基: {U_basis.T}")
print(f"  维度: {U_basis.shape[1]}")

print("\n子空间 W (xy平面):")
print(f"  基:")
print(W_basis.T)
print(f"  维度: {W_basis.shape[1]}")

# 交集 U ∩ W
# U是W的子集，所以交集就是U
intersection_basis = U_basis
print(f"\n交集 U ∩ W:")
print(f"  维度: {intersection_basis.shape[1]}")

# 和空间 U + W
sum_basis = orth(np.hstack([U_basis, W_basis]))
print(f"\n和空间 U + W:")
print(f"  维度: {sum_basis.shape[1]}")

# 验证维数公式: dim(U) + dim(W) = dim(U ∩ W) + dim(U + W)
dim_U = U_basis.shape[1]
dim_W = W_basis.shape[1]
dim_intersection = intersection_basis.shape[1]
dim_sum = sum_basis.shape[1]

print(f"\n维数公式验证:")
print(f"  dim(U) + dim(W) = {dim_U} + {dim_W} = {dim_U + dim_W}")
print(f"  dim(U ∩ W) + dim(U + W) = {dim_intersection} + {dim_sum} = {dim_intersection + dim_sum}")
print(f"  等式成立: {dim_U + dim_W == dim_intersection + dim_sum}")

# ==================== 多项式向量空间 ====================

print("\n" + "=" * 60)
print("多项式向量空间 (离散表示)")
print("=" * 60)

# 用系数向量表示多项式
# p(x) = a0 + a1*x + a2*x^2 + ... + an*x^n
# 对应向量 [a0, a1, a2, ..., an]

# 多项式: 1 + 2x + 3x^2
p_coeffs = np.array([1, 2, 3])

# 多项式: 2 - x + x^2
q_coeffs = np.array([2, -1, 1])

print(f"多项式 p(x) = 1 + 2x + 3x^2, 系数: {p_coeffs}")
print(f"多项式 q(x) = 2 - x + x^2, 系数: {q_coeffs}")

# 多项式加法对应系数相加
r_coeffs = p_coeffs + q_coeffs
print(f"\np(x) + q(x) = 3 + x + 4x^2, 系数: {r_coeffs}")

# 数乘
s_coeffs = 3 * p_coeffs
print(f"3 * p(x) = 3 + 6x + 9x^2, 系数: {s_coeffs}")

# 多项式求值
def evaluate_polynomial(coeffs, x):
    """求多项式在x处的值"""
    return sum(c * (x ** i) for i, c in enumerate(coeffs))

x_val = 2
print(f"\n在 x = {x_val} 处求值:")
print(f"  p({x_val}) = {evaluate_polynomial(p_coeffs, x_val)}")
print(f"  q({x_val}) = {evaluate_polynomial(q_coeffs, x_val)}")

# 多项式空间的基
print(f"\n次数 ≤ 2 的多项式空间 P_2:")
print(f"  标准基: {{1, x, x^2}}")
print(f"  维度: 3")
```

## 应用场景

### 1. 数据降维
- **PCA**：找到数据变化最大的方向（主成分基）
- **子空间方法**：将高维数据投影到低维子空间

### 2. 信号处理
- **傅里叶分析**：将信号表示为正弦/余弦基的线性组合
- **小波分析**：多分辨率分析的基函数

### 3. 机器学习
- **特征提取**：将原始特征映射到新的基下
- **流形学习**：发现数据的低维流形结构

### 4. 优化理论
- **可行域**：约束优化问题的可行解空间
- **KKT条件**：在最优解处的切空间分析

### 5. 计算机图形学
- **坐标系变换**：世界坐标、相机坐标、屏幕坐标
- **投影变换**：将3D场景投影到2D屏幕

## 面试要点

### Q1: 如何判定一个向量组是否线性无关？

**方法**：
1. **定义法**：检查 $c_1\mathbf{v}_1 + ... + c_n\mathbf{v}_n = \mathbf{0}$ 是否只有零解
2. **秩判定**：构造矩阵，秩 = 向量个数则线性无关
3. **行列式**（方阵）：$\det(V) \neq 0$ 则线性无关
4. **Gram矩阵**：$G = V^TV$，$\det(G) \neq 0$ 则线性无关

**计算示例**：
```python
V = np.vstack([v1, v2, v3])
rank = np.linalg.matrix_rank(V)
is_independent = (rank == V.shape[0])
```

### Q2: 什么是向量空间的维度？如何计算？

**定义**：向量空间的维度是该空间任意一组基中向量的个数。

**计算方法**：
- 有限维空间：找到一组基，计数
- 矩阵的列空间：$\dim(C(A)) = \text{rank}(A)$
- 矩阵的零空间：$\dim(N(A)) = n - \text{rank}(A)$（零化度）

**重要关系**：
$$\dim(V) = \dim(C(A^T)) + \dim(N(A))$$

### Q3: 四个基本子空间的关系是什么？

```
ℝⁿ                          ℝᵐ
┌─────────────────┐        ┌─────────────────┐
│                 │        │                 │
│   行空间         │        │   列空间         │
│  C(Aᵀ)          │   A    │    C(A)         │
│  dim = r        │  ───→  │   dim = r       │
│                 │        │                 │
│   ↑             │        │   ↑             │
│   正交补         │        │   正交补         │
│   ↓             │        │   ↓             │
│                 │        │                 │
│   零空间         │        │  左零空间        │
│   N(A)          │        │   N(Aᵀ)         │
│ dim = n-r       │        │  dim = m-r      │
│                 │        │                 │
└─────────────────┘        └─────────────────┘

ℝⁿ = C(Aᵀ) ⊕ N(A)         ℝᵐ = C(A) ⊕ N(Aᵀ)
```

### Q4: 什么是正交补？

**定义**：子空间 $W$ 的正交补 $W^\perp$ 是所有与 $W$ 中向量正交的向量：

$$W^\perp = \{\mathbf{v} \in V \mid \langle \mathbf{v}, \mathbf{w} \rangle = 0, \forall \mathbf{w} \in W\}$$

**性质**：
- $(W^\perp)^\perp = W$
- $V = W \oplus W^\perp$
- $\dim(W) + \dim(W^\perp) = \dim(V)$

**例子**：$\mathbb{R}^3$ 中，平面的正交补是该平面的法线方向。

### Q5: 基变换的实际意义是什么？

**直观理解**：同一向量在不同坐标系下的坐标表示不同。

**应用场景**：
1. **坐标系转换**：世界坐标 ↔ 相机坐标 ↔ 屏幕坐标
2. **特征变换**：将数据从原始特征空间映射到主成分空间
3. **简化计算**：选择适当的基使问题简化（如对角化）

**变换公式**：
$$[\mathbf{v}]_{\text{new}} = P^{-1} [\mathbf{v}]_{\text{old}}$$
其中 $P$ 是新基在旧基下的坐标矩阵。

## 相关概念

### 数据结构
- [数组](../computer-science/data-structures/array.md) - 向量的计算机表示
- [矩阵运算](./matrix-operations.md) - 向量空间的运算实现

### 算法
- [线性变换](./linear-transformations.md) - 向量空间之间的映射
- [特征值与特征向量](./eigenvalues-eigenvectors.md) - 特殊方向的基
- [SVD分解](./svd.md) - 正交基的构造

### 复杂度分析
- [时间复杂度](../references/time-complexity.md) - 基运算的复杂度

### 系统实现
- [主成分分析](./applications-in-cs.md) - 基变换的实际应用
- [计算机图形学](./applications-in-cs.md) - 坐标系变换
