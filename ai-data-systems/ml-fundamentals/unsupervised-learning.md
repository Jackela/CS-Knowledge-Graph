# 无监督学习 (Unsupervised Learning)

## 简介
无监督学习是从无标签数据中发现隐藏模式、结构和关系的一类机器学习方法，常用于数据探索、降维和聚类分析。

## 核心概念

### 基本定义
给定数据集 $D = \{x_1, x_2, ..., x_n\}$，没有对应的标签 $y$。目标是发现数据的内在结构，如聚类、降维或密度估计。

### 主要任务
- **聚类 (Clustering)**：将数据分成若干组，组内相似度高，组间相似度低
- **降维 (Dimensionality Reduction)**：减少数据维度，同时保留重要信息
- **密度估计**：估计数据的概率分布
- **关联规则学习**：发现数据项之间的关联关系

### 常用算法
- K-Means、层次聚类、DBSCAN（聚类）
- PCA、t-SNE、UMAP（降维）
- 高斯混合模型（密度估计）
- Apriori、FP-Growth（关联规则）

## 实现方式

```python
from sklearn.datasets import make_blobs, load_digits
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np

# ===== 聚类示例 =====
# 生成模拟数据
X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=42)

# K-Means聚类
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
labels = kmeans.fit_predict(X)

print(f"聚类中心: \n{kmeans.cluster_centers_}")
print(f"惯性 (Inertia): {kmeans.inertia_:.4f}")

# ===== 降维示例 =====
# 加载手写数字数据
digits = load_digits()
X_digits = digits.data

# PCA降维
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_digits)

print(f"\n原始维度: {X_digits.shape}")
print(f"降维后维度: {X_pca.shape}")
print(f"解释方差比: {pca.explained_variance_ratio_}")
print(f"累计解释方差: {sum(pca.explained_variance_ratio_):.4f}")
```

## 应用场景
- **客户细分**：根据购买行为将客户分群，用于精准营销
- **异常检测**：识别欺诈交易、设备故障等异常数据
- **推荐系统**：发现用户和物品之间的潜在关系
- **基因表达分析**：对基因数据进行聚类分析
- **图像压缩**：使用降维技术减少图像存储空间

## 面试要点

1. **Q: K-Means算法的K值如何选择？**
   A: 可以使用肘部法则（Elbow Method）观察惯性下降曲线的拐点，或使用轮廓系数（Silhouette Score）评估聚类质量，也可结合业务理解确定。

2. **Q: PCA和t-SNE有什么区别？**
   A: PCA是线性降维方法，计算快，适合保留全局结构；t-SNE是非线性降维，更适合可视化高维数据的局部结构，但计算成本高且结果具有随机性。

3. **Q: 如何评估无监督学习的效果？**
   A: 聚类可使用轮廓系数、Davies-Bouldin指数、Calinski-Harabasz指数；若有真实标签可用ARI、NMI；降维可通过重构误差或下游任务性能评估。

4. **Q: K-Means和DBSCAN的主要区别？**
   A: K-Means需要预设聚类数，假设簇为球形，对所有点进行划分；DBSCAN无需预设聚类数，可发现任意形状簇，能识别噪声点，但对密度不均匀的数据效果不佳。

## 相关概念

### AI & Data Systems
- [监督学习](./supervised-learning.md)
- [K-Means聚类](../../data-processing/kmeans-clustering.md)
- [主成分分析](../../data-processing/pca.md)
- [神经网络基础](../deep-learning/neural-networks.md)
- [自编码器](../deep-learning/autoencoder.md)

### 数学基础
- [线性代数](../../mathematics/linear-algebra.md)
- [概率论与统计](../../mathematics/probability-statistics.md)
- [最优化方法](../../mathematics/optimization.md)
