# 支持向量机 (Support Vector Machine, SVM)

## 简介
支持向量机是一种强大的监督学习算法，通过寻找最优超平面来最大化类别之间的间隔，在高维空间和非线性分类问题中表现优异。

## 核心概念

### 基本思想
找到一个超平面 $w^Tx + b = 0$，使得：
1. 能够正确分类所有训练样本
2. 最大化间隔（margin），即超平面到最近样本点的距离

### 间隔计算
几何间隔：$\gamma = \frac{|w^Tx + b|}{||w||}$

函数间隔：$\hat{\gamma} = y(w^Tx + b)$，其中 $y \in \{-1, +1\}$

### 优化目标（硬间隔SVM）
$$\min_{w,b} \frac{1}{2}||w||^2$$

约束条件：$y_i(w^Tx_i + b) \geq 1, \quad i = 1,2,...,m$

### 软间隔SVM（处理噪声）
引入松弛变量 $\xi_i$ 和惩罚参数 $C$：

$$\min_{w,b,\xi} \frac{1}{2}||w||^2 + C\sum_{i=1}^{m}\xi_i$$

约束条件：$y_i(w^Tx_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0$

### 核技巧（Kernel Trick）
将数据映射到高维空间：$\phi(x): x \rightarrow \phi(x)$

常用核函数：
- **线性核**：$K(x_i, x_j) = x_i^T x_j$
- **多项式核**：$K(x_i, x_j) = (\gamma x_i^T x_j + r)^d$
- **RBF核（高斯核）**：$K(x_i, x_j) = \exp(-\gamma||x_i - x_j||^2)$
- **Sigmoid核**：$K(x_i, x_j) = \tanh(\gamma x_i^T x_j + r)$

## 实现方式

```python
import numpy as np
from sklearn import svm
from sklearn.datasets import make_classification, make_moons
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# ===== 线性SVM示例 =====
X, y = make_classification(n_samples=1000, n_features=2, n_redundant=0, 
                           n_informative=2, n_clusters_per_class=1, random_state=42)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 线性SVM
linear_svm = svm.SVC(kernel='linear', C=1.0)
linear_svm.fit(X_train_scaled, y_train)

y_pred = linear_svm.predict(X_test_scaled)
print(f"线性SVM准确率: {accuracy_score(y_test, y_pred):.4f}")
print(f"支持向量数量: {linear_svm.n_support_}")

# ===== 非线性SVM (RBF核) =====
X_moons, y_moons = make_moons(n_samples=500, noise=0.15, random_state=42)
X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(
    X_moons, y_moons, test_size=0.2, random_state=42)

# 网格搜索最优参数
param_grid = {'C': [0.1, 1, 10], 'gamma': ['scale', 'auto', 0.1, 1]}
rbf_svm = GridSearchCV(svm.SVC(kernel='rbf'), param_grid, cv=5)
rbf_svm.fit(X_train_m, y_train_m)

print(f"\n最优参数: {rbf_svm.best_params_}")
print(f"RBF SVM准确率: {rbf_svm.score(X_test_m, y_test_m):.4f}")

# ===== SVM回归 (SVR) =====
from sklearn.svm import SVR

X_reg = np.sort(5 * np.random.rand(100, 1), axis=0)
y_reg = np.sin(X_reg).ravel() + np.random.randn(100) * 0.1

svr_rbf = SVR(kernel='rbf', C=100, gamma=0.1, epsilon=0.1)
svr_rbf.fit(X_reg, y_reg)

print(f"\nSVR拟合完成，支持向量数量: {len(svr_rbf.support_)}")
```

## 应用场景
- **文本分类**：情感分析、垃圾邮件检测
- **图像识别**：人脸识别、手写数字识别
- **生物信息学**：基因分类、蛋白质结构预测
- **医学诊断**：疾病诊断、医学影像分析
- **金融风控**：欺诈检测、信用评分

## 面试要点

1. **Q: SVM为什么被称为最大间隔分类器？**
   A: SVM的优化目标是最大化分类超平面到最近样本点（支持向量）的几何间隔，这有助于提高模型的泛化能力，减少过拟合风险。

2. **Q: SVM中的支持向量是什么？**
   A: 支持向量是距离决策边界最近的样本点，它们决定了最优超平面的位置和方向。只有支持向量影响模型，其他样本可以被移除而不改变决策边界。

3. **Q: 核函数的作用是什么？如何选择？**
   A: 核函数隐式地将数据映射到高维空间，使其线性可分。RBF核适合大多数情况；线性核适合高维稀疏数据；多项式核适合已知特征交互的情况。

4. **Q: SVM和逻辑回归的比较？**
   A: SVM关注支持向量，寻找最大间隔；逻辑回归关注所有样本，输出概率。SVM在高维小样本表现好，逻辑回归在大样本、需要概率解释时更优。

## 相关概念

### AI & Data Systems
- [逻辑回归](./logistic-regression.md)
- [决策树](./decision-trees.md)
- [监督学习](./supervised-learning.md)
- [核方法](./kernel-methods.md)
- [神经网络基础](../deep-learning/neural-networks.md)

### 数学基础
- [线性代数](../../mathematics/linear-algebra.md)
- [最优化方法](../../mathematics/optimization.md)
- [凸优化](../../mathematics/convex-optimization.md)
- [拉格朗日乘子法](../../mathematics/lagrange-multipliers.md)
