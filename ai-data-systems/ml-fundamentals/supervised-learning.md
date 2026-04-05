# 监督学习 (Supervised Learning)

## 简介
监督学习是机器学习中最基本的方法，通过使用带有标签的训练数据来学习输入与输出之间的映射关系，从而能够对新的、未见过的数据进行预测。

## 核心概念

### 基本定义
给定训练集 $D = \{(x_1, y_1), (x_2, y_2), ..., (x_n, y_n)\}$，其中 $x_i$ 是输入特征，$y_i$ 是对应的标签。目标是学习一个函数 $f: X \rightarrow Y$，使得对于新的输入 $x$，能够预测出正确的输出 $y = f(x)$。

### 主要类型
- **分类 (Classification)**：预测离散标签，如二分类、多分类
- **回归 (Regression)**：预测连续值，如房价预测、股票价格

### 关键要素
- **损失函数**：衡量预测值与真实值的差距，如均方误差 (MSE)、交叉熵损失
- **优化算法**：梯度下降、随机梯度下降 (SGD)、Adam
- **评估指标**：准确率、精确率、召回率、F1分数、AUC-ROC

## 实现方式

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# 加载数据
iris = load_iris()
X, y = iris.data, iris.target

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 创建并训练模型
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# 预测与评估
y_pred = model.predict(X_test)
print(f"准确率: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=iris.target_names))
```

## 应用场景
- **图像分类**：识别照片中的物体类别
- **垃圾邮件检测**：判断邮件是否为垃圾邮件
- **医疗诊断**：根据症状预测疾病
- **信用评分**：评估用户的信用风险

## 面试要点

1. **Q: 监督学习和非监督学习的区别是什么？**
   A: 监督学习使用带标签的数据进行训练，目标明确；非监督学习使用无标签数据，目标是发现数据内在结构和模式。

2. **Q: 如何防止监督学习中的过拟合？**
   A: 可以通过正则化（L1/L2）、交叉验证、早停、数据增强、减少模型复杂度、增加训练数据等方法防止过拟合。

3. **Q: 什么是偏差-方差权衡？**
   A: 高偏差模型欠拟合，过于简单；高方差模型过拟合，过于复杂。需要在两者之间找到平衡以获得最佳泛化性能。

4. **Q: 如何处理类别不平衡问题？**
   A: 可以采用过采样（SMOTE）、欠采样、调整类别权重、使用对不平衡数据鲁棒的评估指标（如F1、AUC）等方法。

## 相关概念

### AI & Data Systems
- [无监督学习](./unsupervised-learning.md)
- [线性回归](./linear-regression.md)
- [逻辑回归](./logistic-regression.md)
- [决策树](./decision-trees.md)
- [支持向量机](./svm.md)
- [神经网络基础](../deep-learning/neural-networks.md)

### 数学基础
- [线性代数](../../mathematics/linear-algebra.md)
- [概率论与统计](../../mathematics/probability-statistics.md)
- [微积分](../../mathematics/calculus.md)
