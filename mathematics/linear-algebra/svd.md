# 奇异值分解 (Singular Value Decomposition - SVD)

## 简介

**奇异值分解**（Singular Value Decomposition，SVD）是线性代数中最重要的矩阵分解方法之一。任何 m×n 矩阵 A 都可以分解为 A = UΣVᵀ，其中 U 和 V 是正交矩阵，Σ 是对角矩阵。SVD 在数据压缩、推荐系统、信号处理、机器学习降维等领域有核心应用。

## 核心概念

### 数学定义

**SVD 分解：**
```
A = UΣVᵀ

其中：
- A: m×n 原始矩阵
- U: m×m 左奇异向量矩阵（正交矩阵，UᵀU = I）
- Σ: m×n 对角矩阵，对角线元素为奇异值 σ₁ ≥ σ₂ ≥ ... ≥ σᵣ ≥ 0
- Vᵀ: n×n 右奇异向量矩阵的转置（正交矩阵，VᵀV = I）
```

**与特征值分解的关系：**
- AᵀA 的特征值是奇异值的平方：λᵢ = σᵢ²
- AᵀA 的特征向量构成 V 的列
- AAᵀ 的特征向量构成 U 的列

### 奇异值的性质

1. **非负性**：所有 σᵢ ≥ 0
2. **降序排列**：σ₁ ≥ σ₂ ≥ ... ≥ σᵣ ≥ 0
3. **秩的关系**：非零奇异值个数 = rank(A)
4. **Frobenius范数**：‖A‖_F² = Σσᵢ²

### 低秩近似

**截断SVD（Truncated SVD）：**
```
Aₖ = UₖΣₖVₖᵀ = Σᵢ₌₁ᵏ σᵢuᵢvᵢᵀ
```
- 保留前 k 个最大奇异值
- 是秩为 k 的矩阵中对 A 的最佳近似（Frobenius范数意义下）

**误差分析：**
```
‖A - Aₖ‖_F² = Σᵢ₌ₖ₊₁ʳ σᵢ²
```

## 实现方式

```python
import numpy as np
from typing import Tuple, Optional

class SVDDecomposition:
    """SVD分解类"""
    
    @staticmethod
    def decompose(A: np.ndarray, full_matrices: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        对矩阵A进行SVD分解
        返回: (U, S, Vt) 其中 A = U @ diag(S) @ Vt
        """
        U, S, Vt = np.linalg.svd(A, full_matrices=full_matrices)
        return U, S, Vt
    
    @staticmethod
    def reconstruct(U: np.ndarray, S: np.ndarray, Vt: np.ndarray) -> np.ndarray:
        """从SVD分量重构原始矩阵"""
        Sigma = np.diag(S)
        if U.shape[0] > S.shape[0]:
            Sigma = np.pad(Sigma, ((0, U.shape[0] - S.shape[0]), (0, 0)), mode='constant')
        if Vt.shape[0] > S.shape[0]:
            Sigma = np.pad(Sigma, ((0, 0), (0, Vt.shape[0] - S.shape[0])), mode='constant')
        return U @ Sigma @ Vt
    
    @staticmethod
    def low_rank_approximation(A: np.ndarray, k: int) -> Tuple[np.ndarray, float]:
        """
        使用截断SVD进行低秩近似
        返回: (近似矩阵, 近似误差)
        """
        U, S, Vt = np.linalg.svd(A, full_matrices=False)
        
        # 保留前k个奇异值
        U_k = U[:, :k]
        S_k = S[:k]
        Vt_k = Vt[:k, :]
        
        # 重构
        A_k = U_k @ np.diag(S_k) @ Vt_k
        
        # 计算误差
        error = np.linalg.norm(A - A_k, 'fro')
        
        return A_k, error
    
    @staticmethod
    def pseudo_inverse(A: np.ndarray) -> np.ndarray:
        """计算Moore-Penrose伪逆"""
        U, S, Vt = np.linalg.svd(A, full_matrices=False)
        
        # 计算伪逆: A⁺ = V @ Σ⁺ @ Uᵀ
        S_inv = np.diag([1/s if s > 1e-10 else 0 for s in S])
        A_pinv = Vt.T @ S_inv @ U.T
        
        return A_pinv
    
    @staticmethod
    def condition_number(A: np.ndarray) -> float:
        """计算矩阵条件数"""
        S = np.linalg.svd(A, compute_uv=False)
        return S[0] / S[-1] if S[-1] > 1e-10 else float('inf')
    
    @staticmethod
    def effective_rank(A: np.ndarray, threshold: float = 1e-10) -> int:
        """计算有效秩（基于奇异值阈值）"""
        S = np.linalg.svd(A, compute_uv=False)
        return np.sum(S > threshold)
    
    @staticmethod
    def variance_explained(S: np.ndarray) -> np.ndarray:
        """计算每个奇异值解释的方差比例"""
        return S**2 / np.sum(S**2)


# PCA实现（基于SVD）
def pca_svd(X: np.ndarray, n_components: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    使用SVD实现PCA降维
    
    Args:
        X: 数据矩阵 (n_samples, n_features)
        n_components: 降维后的维度
    
    Returns:
        X_reduced: 降维后的数据
        components: 主成分
    """
    # 中心化数据
    X_centered = X - np.mean(X, axis=0)
    
    # SVD分解
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    
    # 选择前n_components个成分
    components = Vt[:n_components, :].T
    
    # 降维后的数据
    X_reduced = U[:, :n_components] * S[:n_components]
    
    return X_reduced, components


# 图像压缩示例
def compress_image(image: np.ndarray, k: int) -> np.ndarray:
    """
    使用SVD压缩图像
    
    Args:
        image: 输入图像（灰度图）
        k: 保留的奇异值数量
    
    Returns:
        compressed: 压缩后的图像
    """
    U, S, Vt = np.linalg.svd(image, full_matrices=False)
    
    # 保留前k个奇异值
    compressed = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
    
    return np.clip(compressed, 0, 255).astype(np.uint8)


# 使用示例
if __name__ == "__main__":
    # 创建测试矩阵
    A = np.array([
        [3, 2, 2],
        [2, 3, -2]
    ])
    
    # SVD分解
    U, S, Vt = SVDDecomposition.decompose(A)
    print("奇异值:", S)
    
    # 重构
    A_reconstructed = SVDDecomposition.reconstruct(U, S, Vt)
    print("重构误差:", np.linalg.norm(A - A_reconstructed))
    
    # 低秩近似
    A_approx, error = SVDDecomposition.low_rank_approximation(A, k=1)
    print(f"秩1近似误差: {error:.4f}")
    
    # 条件数
    print(f"条件数: {SVDDecomposition.condition_number(A):.4f}")
    
    # PCA示例
    X = np.random.randn(100, 5)
    X_pca, components = pca_svd(X, n_components=2)
    print(f"PCA降维: {X.shape} -> {X_pca.shape}")
```

## 应用场景

### 1. 推荐系统
- **协同过滤**：用户-物品评分矩阵的低秩近似
- **矩阵补全**：利用SVD填充缺失评分
- **隐语义模型**：Latent Factor Model

### 2. 图像处理
- **图像压缩**：保留主要奇异值丢弃次要细节
- **去噪**：去除对应小奇异值的噪声分量
- **人脸识别**：Eigenfaces方法

### 3. 自然语言处理
- **潜在语义分析**（LSA）：文档-词矩阵降维
- **词向量降维**：高维词嵌入的压缩表示
- **主题建模**：发现文档的潜在主题

### 4. 信号处理
- **主成分分析**（PCA）：数据降维和特征提取
- **降噪**：信号与噪声的分离
- **数据压缩**：音频、视频压缩

### 5. 数值计算
- **求解线性方程组**：病态矩阵的处理
- **计算伪逆**：最小二乘问题的求解
- **条件数估计**：矩阵稳定性的度量

## 面试要点

**Q1: SVD分解的数学形式是什么？各矩阵的维度？**
A: A = UΣVᵀ
- A: m×n
- U: m×m（左奇异向量，正交矩阵）
- Σ: m×n（对角矩阵，对角线为奇异值）
- Vᵀ: n×n（右奇异向量转置，正交矩阵）

**Q2: 奇异值与特征值有什么关系？**
A: AᵀA的特征值是奇异值的平方：λᵢ = σᵢ²。AᵀA的特征向量构成V，AAᵀ的特征向量构成U。

**Q3: 如何用SVD进行降维？**
A: 使用截断SVD，保留前k个最大奇异值及其对应的奇异向量：Aₖ = UₖΣₖVₖᵀ。这是秩为k的矩阵中对原矩阵的最佳Frobenius近似。

**Q4: PCA与SVD的关系？**
A: 对中心化数据X进行SVD分解：X = UΣVᵀ，则XV = UΣ就是PCA投影后的数据，V的列就是主成分。

**Q5: 什么是矩阵的条件数？如何用SVD计算？**
A: 条件数 = σ_max / σ_min，衡量矩阵求逆的数值稳定性。条件数越大，矩阵越接近奇异（病态）。

**Q6: SVD在推荐系统中的应用？**
A: 用户-物品评分矩阵通常是稀疏且低秩的。通过SVD低秩近似可以发现用户的潜在兴趣因子和物品的潜在特征，用于预测缺失评分。

## 相关概念

### 数据结构
- [矩阵](../data-structures/matrix.md) - SVD操作的对象
- [数组](../data-structures/array.md) - 数据存储

### 算法
- [特征值分解](../algorithms/eigenvalue-decomposition.md) - 与SVD相关
- [矩阵乘法](../algorithms/matrix-multiplication.md) - 重构运算
- [PCA算法](../algorithms/pca.md) - SVD的应用

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - SVD复杂度通常为O(min(mn², m²n))
- [空间复杂度](../../references/space-complexity.md) - 存储U、Σ、V需要O(m² + n²)

### 系统实现
- [推荐系统](../../references/recommendation-systems.md) - SVD应用
- [图像压缩](../../references/image-compression.md) - 数据压缩应用
- [NumPy](../../references/numpy.md) - SVD实现库
- [SciPy](../../references/scipy.md) - 稀疏矩阵SVD
