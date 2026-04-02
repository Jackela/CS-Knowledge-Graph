# 线性代数在计算机科学中的应用 (Applications of Linear Algebra in CS)

## 简介

**线性代数**是计算机科学的数学基础，其概念和方法渗透到图形学、机器学习、密码学、优化算法等各个领域。理解线性代数在CS中的具体应用，有助于建立从数学理论到工程实践的桥梁，是高级算法设计和系统实现的关键能力。

## 核心概念

### 1. 计算机图形学

**变换矩阵链：**
```
最终位置 = 投影矩阵 × 视图矩阵 × 模型矩阵 × 顶点坐标
```

**关键应用：**
- **3D变换**：平移、旋转、缩放、剪切
- **投影变换**：透视投影、正交投影
- **光照计算**：法线变换、光照模型
- **骨骼动画**：关节变换矩阵的级联
- **纹理映射**：UV坐标变换

**齐次坐标：**
- 使用4D向量 (x, y, z, w) 表示3D点
- 使平移可以用矩阵乘法表示

### 2. 机器学习

**线性模型：**
- **线性回归**：y = Xw + b，最小化‖y - Xw‖²
- **逻辑回归**：sigmoid(Xw)的概率模型
- **支持向量机**：寻找最优分类超平面

**神经网络：**
- **前向传播**：层间权重矩阵与激活值的乘法
- **反向传播**：梯度通过矩阵链式法则传播
- **卷积运算**：特殊的矩阵乘法形式

**降维技术：**
- **PCA**：协方差矩阵的特征分解
- **LDA**：类间/类内散度矩阵的广义特征值问题
- **t-SNE**：基于概率分布的降维

### 3. 数据压缩

**图像压缩（JPEG）：**
- **DCT变换**：将图像块转换到频域
- **量化**：舍弃高频信息
- **熵编码**：霍夫曼编码压缩

**视频压缩：**
- **运动估计**：块匹配寻找运动向量
- **帧间预测**：利用时间冗余

**主成分压缩：**
- 保留数据的主要变异方向
- 应用：人脸压缩、基因表达数据

### 4. 优化算法

**梯度下降：**
```
w := w - α∇J(w)
```

**牛顿法：**
```
w := w - H⁻¹∇J(w)
```
其中 H 是Hessian矩阵

**共轭梯度法：**
- 求解大型稀疏线性系统的迭代方法
- 应用于有限元分析

### 5. 密码学

**RSA加密：**
- 基于大整数分解的困难性
- 模幂运算的矩阵快速幂优化

**椭圆曲线密码学：**
- 有限域上的代数曲线运算
- 双线性配对（椭圆曲线上的线性代数）

**格密码学（后量子密码）：**
- 基于格中最短向量问题（SVP）
- LLL算法等格基约简

### 6. 图算法

**图表示：**
- **邻接矩阵**：图的矩阵表示，A[i][j]表示边权重
- **拉普拉斯矩阵**：L = D - A，用于谱聚类

**PageRank算法：**
- 将网页排名建模为马尔可夫链
- 求解特征向量问题

**谱聚类：**
- 利用图的谱（特征值）进行聚类
- 应用于图像分割、社区发现

## 实现方式

```python
import numpy as np
from typing import List, Tuple

class LinearAlgebraApplications:
    """线性代数在CS中的应用示例"""
    
    @staticmethod
    def transformation_chain():
        """图形学中的变换矩阵链"""
        # 模型变换：旋转45度
        theta = np.pi / 4
        R = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]
        ])
        
        # 平移变换
        T = np.array([
            [1, 0, 2],
            [0, 1, 3],
            [0, 0, 1]
        ])
        
        # 组合变换（注意：矩阵乘法顺序从右到左）
        M = T @ R
        
        # 应用变换到顶点
        vertex = np.array([1, 0, 1])  # 齐次坐标
        transformed = M @ vertex
        
        return M, transformed
    
    @staticmethod
    def linear_regression(X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        线性回归：最小二乘解
        w = (XᵀX)⁻¹Xᵀy
        """
        return np.linalg.inv(X.T @ X) @ X.T @ y
    
    @staticmethod
    def pca_dimension_reduction(X: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        PCA降维
        
        Returns:
            X_reduced: 降维后的数据
            explained_variance_ratio: 各主成分解释的方差比例
        """
        # 中心化
        X_centered = X - np.mean(X, axis=0)
        
        # 协方差矩阵
        cov = X_centered.T @ X_centered / (X.shape[0] - 1)
        
        # 特征分解
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        
        # 按特征值降序排序
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # 选择前k个主成分
        components = eigenvectors[:, :k]
        
        # 投影
        X_reduced = X_centered @ components
        
        # 解释方差比例
        explained_variance_ratio = eigenvalues[:k] / np.sum(eigenvalues)
        
        return X_reduced, explained_variance_ratio
    
    @staticmethod
    def pagerank(adjacency_matrix: np.ndarray, damping: float = 0.85, 
                 max_iter: int = 100, tol: float = 1e-6) -> np.ndarray:
        """
        PageRank算法实现
        
        Args:
            adjacency_matrix: 邻接矩阵（出链权重）
            damping: 阻尼系数
            max_iter: 最大迭代次数
            tol: 收敛阈值
        
        Returns:
            页面排名向量
        """
        n = adjacency_matrix.shape[0]
        
        # 构建转移概率矩阵
        out_degree = np.sum(adjacency_matrix, axis=1)
        M = adjacency_matrix / out_degree[:, np.newaxis]
        M = np.nan_to_num(M)  # 处理除以0
        
        # 初始化排名向量
        r = np.ones(n) / n
        
        # 迭代求解
        for _ in range(max_iter):
            r_new = damping * M.T @ r + (1 - damping) / n
            if np.linalg.norm(r_new - r) < tol:
                break
            r = r_new
        
        return r
    
    @staticmethod
    def image_compression_svd(image: np.ndarray, k: int) -> Tuple[np.ndarray, float]:
        """
        使用SVD压缩图像
        
        Returns:
            compressed_image: 压缩后的图像
            compression_ratio: 压缩比
        """
        U, S, Vt = np.linalg.svd(image, full_matrices=False)
        
        # 保留前k个奇异值
        compressed = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]
        
        # 计算压缩比
        original_size = image.shape[0] * image.shape[1]
        compressed_size = k * (image.shape[0] + 1 + image.shape[1])
        compression_ratio = original_size / compressed_size
        
        return np.clip(compressed, 0, 255).astype(np.uint8), compression_ratio


# 推荐系统：协同过滤
def collaborative_filtering_svd(ratings: np.ndarray, k: int) -> np.ndarray:
    """
    基于SVD的协同过滤推荐
    
    Args:
        ratings: 用户-物品评分矩阵（缺失值用0填充）
        k: 潜在因子数量
    
    Returns:
        预测评分矩阵
    """
    # SVD分解
    U, S, Vt = np.linalg.svd(ratings, full_matrices=False)
    
    # 截断SVD
    U_k = U[:, :k]
    S_k = np.diag(S[:k])
    Vt_k = Vt[:k, :]
    
    # 重构评分矩阵
    predicted_ratings = U_k @ S_k @ Vt_k
    
    return predicted_ratings


# 图分割：谱聚类
def spectral_clustering(adjacency: np.ndarray, n_clusters: int) -> np.ndarray:
    """
    谱聚类算法
    
    Args:
        adjacency: 邻接矩阵
        n_clusters: 聚类数量
    
    Returns:
        聚类标签
    """
    n = adjacency.shape[0]
    
    # 计算度矩阵
    degree = np.sum(adjacency, axis=1)
    D = np.diag(degree)
    
    # 拉普拉斯矩阵
    L = D - adjacency
    
    # 对称归一化拉普拉斯矩阵
    D_inv_sqrt = np.diag(1.0 / np.sqrt(degree + 1e-10))
    L_sym = D_inv_sqrt @ L @ D_inv_sqrt
    
    # 特征分解（取最小的n_clusters个特征值对应的特征向量）
    eigenvalues, eigenvectors = np.linalg.eigh(L_sym)
    
    # 使用k-means对特征向量聚类
    from sklearn.cluster import KMeans
    X = eigenvectors[:, 1:n_clusters+1]  # 跳过第一个特征向量
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)
    
    return labels


# 使用示例
if __name__ == "__main__":
    app = LinearAlgebraApplications()
    
    # 1. 线性回归
    X = np.random.randn(100, 3)
    true_w = np.array([2, -1, 0.5])
    y = X @ true_w + np.random.randn(100) * 0.1
    w_estimated = app.linear_regression(X, y)
    print("线性回归系数:", w_estimated)
    
    # 2. PCA降维
    X_high_dim = np.random.randn(100, 10)
    X_reduced, variance_ratio = app.pca_dimension_reduction(X_high_dim, k=2)
    print(f"PCA降维: {X_high_dim.shape} -> {X_reduced.shape}")
    print(f"解释方差比例: {variance_ratio}")
    
    # 3. PageRank
    # 简单的4页面网络
    adj = np.array([
        [0, 1, 1, 0],
        [0, 0, 1, 1],
        [1, 0, 0, 1],
        [0, 1, 0, 0]
    ])
    ranks = app.pagerank(adj)
    print("PageRank:", ranks)
```

## 应用场景

### 1. 实时渲染引擎
- **GPU着色器**：矩阵运算硬件加速
- **骨骼动画**：100+关节的变换级联
- **粒子系统**：大规模并行向量运算

### 2. 大规模机器学习
- **分布式训练**：参数服务器的矩阵更新
- **模型压缩**：低秩分解减少参数量
- **特征工程**：稀疏矩阵高效运算

### 3. 计算机视觉
- **相机标定**：内外参矩阵估计
- **图像配准**：仿射/透视变换估计
- **结构光3D重建**：三角测量计算

### 4. 自然语言处理
- **词嵌入**：Word2Vec的矩阵分解视角
- **注意力机制**：Query-Key-Value矩阵运算
- **Transformer**：自注意力的大规模矩阵乘法

### 5. 网络分析
- **社交网络**：影响力最大化、社区检测
- **交通网络**：最短路径、流量优化
- **知识图谱**：图嵌入、链路预测

## 面试要点

**Q1: 线性回归的闭式解是什么？什么时候不能用？**
A: w = (XᵀX)⁻¹Xᵀy。当XᵀX不可逆（特征相关或特征数>样本数）时需要使用正则化或梯度下降。

**Q2: PCA降维的数学原理是什么？**
A: 找到数据方差最大的方向作为主成分。等价于对协方差矩阵进行特征分解，选择最大特征值对应的特征向量作为投影方向。

**Q3: PageRank算法为什么可以收敛？**
A: 将网页链接看作马尔可夫链，转移矩阵是随机矩阵。根据Perron-Frobenius定理，存在唯一的平稳分布，幂迭代法可以收敛到这个特征向量。

**Q4: 图像SVD压缩的原理是什么？**
A: 图像是低秩矩阵的近似。保留大奇异值对应的主要结构信息，丢弃小奇异值对应的细节/噪声，实现有损压缩。

**Q5: 神经网络中为什么需要矩阵运算？**
A: 全连接层是权重矩阵与输入向量的乘法；卷积可以转化为矩阵乘法（im2col）；反向传播涉及Jacobian矩阵的链式乘法。

**Q6: 谱聚类为什么有效？**
A: 图的拉普拉斯矩阵的特征向量将图嵌入到低维空间，使得在原始图上的聚类问题转化为在嵌入空间中的简单聚类问题。

## 相关概念

### 数据结构
- [矩阵](../data-structures/matrix.md) - 核心数据结构
- [图](../data-structures/graph.md) - 邻接矩阵表示
- [数组](../data-structures/array.md) - 向量存储

### 算法
- [矩阵乘法](../algorithms/matrix-multiplication.md) - 基础运算
- [特征值分解](../algorithms/eigenvalue-decomposition.md) - PCA基础
- [SVD分解](../algorithms/svd-algorithm.md) - 推荐系统基础
- [梯度下降](../algorithms/gradient-descent.md) - 优化算法

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 矩阵运算复杂度
- [空间复杂度](../../references/space-complexity.md) - 存储需求

### 系统实现
- [计算机图形学](../../references/computer-graphics.md) - 变换应用
- [机器学习](../../references/machine-learning.md) - 线性模型
- [推荐系统](../../references/recommendation-systems.md) - 协同过滤
- [CUDA](../../references/cuda.md) - GPU加速
- [NumPy](../../references/numpy.md) - 线性代数库
