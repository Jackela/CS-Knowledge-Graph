# 逻辑回归 (Logistic Regression)

## 简介
逻辑回归是一种广泛应用于二分类问题的统计方法，通过Sigmoid函数将线性组合映射到(0,1)区间，表示样本属于某一类别的概率。

## 核心概念

### Sigmoid函数
$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

其中 $z = \mathbf{w}^T\mathbf{x} + b$ 是特征的线性组合。

### 概率模型
给定输入 $\mathbf{x}$，属于类别1的概率：

$$P(y=1|\mathbf{x}) = \sigma(\mathbf{w}^T\mathbf{x} + b) = \frac{1}{1 + e^{-(\mathbf{w}^T\mathbf{x} + b)}}$$

属于类别0的概率：

$$P(y=0|\mathbf{x}) = 1 - P(y=1|\mathbf{x})$$

### 决策边界
当 $P(y=1|\mathbf{x}) \geq 0.5$ 时预测为类别1，即：

$$\mathbf{w}^T\mathbf{x} + b \geq 0$$

### 损失函数（对数损失/交叉熵）
$$L(\mathbf{w}, b) = -\frac{1}{m} \sum_{i=1}^{m} [y^{(i)}\log(\hat{y}^{(i)}) + (1-y^{(i)})\log(1-\hat{y}^{(i)})]$$

### 梯度下降更新
$$\frac{\partial L}{\partial w_j} = \frac{1}{m} \sum_{i=1}^{m} (\hat{y}^{(i)} - y^{(i)}) x_j^{(i)}$$

## 实现方式

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score

# 生成二分类数据
X, y = make_classification(
    n_samples=1000, 
    n_features=2, 
    n_redundant=0, 
    n_informative=2,
    n_clusters_per_class=1,
    random_state=42
)

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建并训练逻辑回归模型
model = LogisticRegression(max_iter=1000, C=1.0)
model.fit(X_train, y_train)

# 预测
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# 评估
print(f"截距: {model.intercept_[0]:.4f}")
print(f"系数: {model.coef_[0]}")
print(f"准确率: {accuracy_score(y_test, y_pred):.4f}")
print(f"AUC-ROC: {roc_auc_score(y_test, y_prob):.4f}")
print(f"\n混淆矩阵:\n{confusion_matrix(y_test, y_pred)}")

# ===== 多分类逻辑回归 (Softmax) =====
from sklearn.datasets import load_iris

iris = load_iris()
X_multi, y_multi = iris.data, iris.target

X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(
    X_multi, y_multi, test_size=0.2, random_state=42
)

# multinomial使用Softmax回归
model_multi = LogisticRegression(multi_class='multinomial', max_iter=200)
model_multi.fit(X_train_m, y_train_m)

print(f"\n多分类准确率: {model_multi.score(X_test_m, y_test_m):.4f}")
```

## 应用场景
- **医疗诊断**：预测疾病发生概率
- **信用评估**：判断用户违约风险
- **垃圾邮件识别**：区分正常邮件和垃圾邮件
- **广告点击率预测**：预测用户点击广告的概率
- **客户流失预测**：识别可能流失的客户

## 面试要点

1. **Q: 逻辑回归为什么使用Sigmoid函数？**
   A: Sigmoid函数将线性输出映射到(0,1)区间，可解释为概率；它是指数族分布的自然参数化，保证对数似然函数是凹函数，有全局最优解。

2. **Q: 逻辑回归是线性模型还是非线性模型？**
   A: 逻辑回归关于参数是线性的，但决策边界可以是线性或非线性的（通过特征工程或核技巧）。本质上属于广义线性模型(GLM)。

3. **Q: 如何处理逻辑回归中的类别不平衡问题？**
   A: 可采用：1) 调整类别权重（class_weight='balanced'）；2) 过采样/欠采样；3) 调整分类阈值；4) 使用F1-score等平衡评估指标。

4. **Q: 逻辑回归和线性回归的区别？**
   A: 线性回归预测连续值，使用MSE损失，假设误差正态分布；逻辑回归预测概率/类别，使用对数损失，输出经Sigmoid映射到(0,1)。

## 相关概念

### AI & Data Systems
- [线性回归](./linear-regression.md)
- [支持向量机](./svm.md)
- [监督学习](./supervised-learning.md)
- [神经网络基础](../deep-learning/neural-networks.md)
- [Softmax回归](./softmax-regression.md)

### 数学基础
- [概率论与统计](../../mathematics/probability-statistics.md)
- [微积分](../../mathematics/calculus.md)
- [最优化方法](../../mathematics/optimization.md)
- [指数族分布](../../mathematics/exponential-family.md)
