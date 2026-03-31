# 机器学习概述 (Machine Learning Overview)

## 简介

**机器学习 (Machine Learning)** 是人工智能的一个分支，使计算机能够从数据中学习规律，而无需进行明确的编程。机器学习算法通过分析数据、识别模式，做出预测或决策。

```
┌─────────────────────────────────────────────────────────────┐
│                   机器学习核心概念                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   传统编程：                  机器学习：                       │
│                                                             │
│   数据 + 规则 ────▶ 答案       数据 + 答案 ────▶ 规则        │
│      │    │                    │      │      │              │
│      │    │                    │      │      │              │
│      ▼    ▼                    ▼      ▼      ▼              │
│   ┌──────────┐              ┌──────────────────┐            │
│   │  if-else │              │  模型训练        │            │
│   │  逻辑    │              │  (学习规律)      │            │
│   └──────────┘              └──────────────────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 机器学习分类

### 监督学习 (Supervised Learning)

```
监督学习：使用带标签的数据训练

训练数据：
┌─────────────┬─────────────┬─────────────┐
│ 特征1 (X1)  │ 特征2 (X2)  │ 标签 (Y)    │
├─────────────┼─────────────┼─────────────┤
│ 5.1         │ 3.5         │ 类别A       │
│ 4.9         │ 3.0         │ 类别A       │
│ 6.2         │ 3.4         │ 类别B       │
│ ...         │ ...         │ ...         │
└─────────────┴─────────────┴─────────────┘

算法学习：X → Y 的映射函数

应用场景：分类、回归
```

**常见算法：**
- **分类 (Classification)**：决策树、随机森林、SVM、逻辑回归
- **回归 (Regression)**：线性回归、多项式回归、岭回归

### 无监督学习 (Unsupervised Learning)

```
无监督学习：从无标签数据中发现模式

训练数据：
┌─────────────┬─────────────┐
│ 特征1 (X1)  │ 特征2 (X2)  │
├─────────────┼─────────────┤
│ 5.1         │ 3.5         │
│ 4.9         │ 3.0         │
│ 6.2         │ 3.4         │
│ ...         │ ...         │
└─────────────┴─────────────┘

算法发现：数据内在结构和分布

应用场景：聚类、降维、关联规则
```

**常见算法：**
- **聚类 (Clustering)**：K-Means、层次聚类、DBSCAN
- **降维 (Dimensionality Reduction)**：PCA、t-SNE、自编码器

### 强化学习 (Reinforcement Learning)

```
强化学习：通过试错学习最优策略

┌──────────┐      动作 (Action)      ┌──────────┐
│          │ ─────────────────────▶ │          │
│   智能体  │                        │   环境   │
│  (Agent) │ ◀───────────────────── │(Environment)
│          │      状态 + 奖励        │          │
└──────────┘                         └──────────┘

目标：最大化长期累积奖励

应用场景：游戏AI、自动驾驶、推荐系统
```

## 机器学习工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                   机器学习项目流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 问题定义         明确业务目标和评估指标                   │
│       │                                                     │
│       ▼                                                     │
│  2. 数据收集         获取相关数据集                          │
│       │                                                     │
│       ▼                                                     │
│  3. 数据预处理       清洗、转换、特征工程                     │
│       │                                                     │
│       ▼                                                     │
│  4. 模型选择         选择合适的算法                          │
│       │                                                     │
│       ▼                                                     │
│  5. 模型训练         使用训练数据拟合模型                    │
│       │                                                     │
│       ▼                                                     │
│  6. 模型评估         验证集/测试集评估                       │
│       │                                                     │
│       ▼                                                     │
│  7. 模型优化         调参、集成、特征选择                     │
│       │                                                     │
│       ▼                                                     │
│  8. 模型部署         生产环境上线                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 核心概念

### 特征工程 (Feature Engineering)

```python
# 特征工程示例
import pandas as pd
import numpy as np

# 原始数据
data = pd.DataFrame({
    'date': ['2024-01-01', '2024-01-02'],
    'price': [100, 150],
    'category': ['A', 'B']
})

# 特征提取
# 1. 时间特征
data['year'] = pd.to_datetime(data['date']).dt.year
data['month'] = pd.to_datetime(data['date']).dt.month
data['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek

# 2. 数值变换
data['price_log'] = np.log(data['price'])
data['price_squared'] = data['price'] ** 2

# 3. 独热编码 (One-Hot Encoding)
data = pd.get_dummies(data, columns=['category'])

print(data)
```

### 模型评估指标

#### 分类任务

```
混淆矩阵：

                预测值
              正类    负类
           ┌────────┬────────┐
    正类   │   TP   │   FN   │
实际值      ├────────┼────────┤
    负类   │   FP   │   TN   │
           └────────┴────────┘

准确率 (Accuracy) = (TP + TN) / (TP + TN + FP + FN)
精确率 (Precision) = TP / (TP + FP)
召回率 (Recall) = TP / (TP + FN)
F1分数 = 2 * (Precision * Recall) / (Precision + Recall)

ROC曲线：
True Positive Rate (TPR) vs False Positive Rate (FPR)
AUC：ROC曲线下面积（0.5随机，1.0完美）
```

#### 回归任务

```
均方误差 (MSE) = Σ(y_true - y_pred)² / n
均方根误差 (RMSE) = √MSE
平均绝对误差 (MAE) = Σ|y_true - y_pred| / n
R²分数 = 1 - (SS_res / SS_tot)
```

### 过拟合与欠拟合

```
模型复杂度 vs 误差：

误差 │
     │      ╲ 验证误差
     │       ╲________
     │        ╲      ╱
     │   ______╲    ╱ 最优模型
     │  ╱       ╲__╱
     │ ╱ 训练误差
     │╱
     └──────────────────▶ 模型复杂度
          ↑
       欠拟合        过拟合

欠拟合 (Underfitting)：
- 训练误差高，验证误差高
- 模型过于简单，无法捕捉数据规律
- 解决：增加模型复杂度、添加特征

过拟合 (Overfitting)：
- 训练误差低，验证误差高
- 模型过于复杂，记住了训练数据的噪声
- 解决：正则化、增加数据、简化模型
```

### 正则化技术

```python
# L1正则化 (Lasso) - 产生稀疏权重
# L2正则化 (Ridge) - 权重衰减

from sklearn.linear_model import Lasso, Ridge

# L1正则化
lasso = Lasso(alpha=0.1)  # alpha是正则化强度
lasso.fit(X_train, y_train)

# L2正则化
ridge = Ridge(alpha=0.1)
ridge.fit(X_train, y_train)

# ElasticNet (L1 + L2)
from sklearn.linear_model import ElasticNet
elastic = ElasticNet(alpha=0.1, l1_ratio=0.5)
```

## 经典算法详解

### 线性回归 (Linear Regression)

```
模型：y = w₁x₁ + w₂x₂ + ... + wₙxₙ + b

目标：最小化均方误差
J(w) = (1/2m) Σ(y_pred - y_true)²

求解方法：
- 正规方程：w = (XᵀX)⁻¹Xᵀy
- 梯度下降：w := w - α * ∂J/∂w

梯度下降过程：
        J(w)
         │    ╲
         │     ╲
         │      ╲____
         │           ╲
         │            ╲
         └──────────────▶ w
              ↓
         全局最优
```

### 逻辑回归 (Logistic Regression)

```
用于二分类问题

sigmoid函数：σ(z) = 1 / (1 + e^(-z))

模型：P(y=1|x) = σ(wᵀx + b) = 1 / (1 + e^-(wᵀx+b))

决策边界：wᵀx + b = 0

损失函数（交叉熵）：
L = -[y*log(ŷ) + (1-y)*log(1-ŷ)]

        σ(z)
         │
    1.0 ─┤        ___________
         │       /
    0.5 ─┤──────●
         │     /
    0.0 ─┤____/
         └──────────────▶ z
              0
```

### 决策树 (Decision Tree)

```
决策树结构：

         ┌─────────────┐
         │  年龄 > 30?  │
         └──────┬──────┘
           是  /    \  否
              /      \
       ┌─────▼───┐  ┌▼────────┐
       │收入>50k?│  │学生?    │
       └────┬────┘  └────┬────┘
      是  / \ 否    是  / \ 否
         /   \          /   \
    ┌───▼─┐ ┌─▼──┐  ┌──▼┐ ┌─▼──┐
    │购买 │ │不买│  │买 │ │不买│
    └─────┘ └────┘  └───┘ └────┘

分裂标准：
- 信息增益（ID3）
- 信息增益率（C4.5）
- 基尼指数（CART）
```

### 支持向量机 (SVM)

```
最大化分类间隔：

      ●           ○
         ●    ○
    ───────●─○───────  最优超平面
         ○    ●
      ○           ●
      
      ↑               ↑
   支持向量        支持向量

目标：max (2/||w||)  即 min (1/2)||w||²
约束：yᵢ(wᵀxᵢ + b) ≥ 1

核技巧：将数据映射到高维空间
- 线性核：K(x,y) = xᵀy
- 多项式核：K(x,y) = (γxᵀy + r)^d
- RBF核：K(x,y) = exp(-γ||x-y||²)
```

### K-Means聚类

```
K-Means算法步骤：

1. 随机选择K个中心点
        ●
     ○  ★  ●
   ●    ○
      ★
   
2. 将每个点分配到最近的中心
   ┌─────────┐
   │ ●    ●  │
   │    ★    │
   │  ○   ★  │
   │   ○     │
   └─────────┘
   
3. 重新计算中心点
4. 重复2-3直到收敛
```

## 集成学习

### Bagging (Bootstrap Aggregating)

```
随机森林 (Random Forest)：

训练数据 ──┬──▶ 子集1 ──▶ 决策树1 ──┐
         ├──▶ 子集2 ──▶ 决策树2 ──┤
         ├──▶ 子集3 ──▶ 决策树3 ──┼──▶ 投票/平均 ──▶ 最终预测
         ...                       │
         └──▶ 子集N ──▶ 决策树N ──┘
         
特点：
- 有放回抽样（Bootstrap）
- 随机特征选择
- 并行训练
- 降低方差
```

### Boosting

```
AdaBoost / Gradient Boosting：

序列训练，关注错分样本：

轮次1：平等权重 ──▶ 弱分类器1 ──▶ 计算误差
                    ↓
轮次2：增加错分样本权重 ──▶ 弱分类器2
                    ↓
轮次3：继续调整权重 ──▶ 弱分类器3
                    ↓
              加权组合 ──▶ 强分类器

代表算法：
- AdaBoost
- Gradient Boosting
- XGBoost
- LightGBM
- CatBoost
```

## 神经网络基础

### 感知机 (Perceptron)

```
基本结构：

x₁ ────┐
       │
x₂ ────┼──▶ Σ ──▶ 激活函数 ──▶ 输出
       │   ↑
x₃ ────┘   │
          w₀ (偏置)

输出：y = f(w₁x₁ + w₂x₂ + w₃x₃ + w₀)

激活函数 f：
- 阶跃函数（原始感知机）
- Sigmoid
- ReLU
- Tanh
```

### 多层感知机 (MLP)

```
全连接神经网络：

输入层      隐藏层1      隐藏层2      输出层

x₁ ──┐                  h₁' ──┐
     │    ┌──┐   ┌──┐         │
x₂ ──┼───▶│  │──▶│  │──▶ h₂' ──┼──▶  ŷ
     │    └──┘   └──┘         │
x₃ ──┘    ↑        ↑      h₃' ──┘
         w¹        w²

前向传播：计算预测值
反向传播：更新权重（链式法则）
```

## Scikit-Learn实践

```python
# 完整机器学习流程示例
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. 加载数据
iris = load_iris()
X, y = iris.data, iris.target

# 2. 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. 特征缩放
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4. 模型训练
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# 5. 预测
y_pred = model.predict(X_test_scaled)

# 6. 评估
print(f"准确率: {accuracy_score(y_test, y_pred):.2f}")
print(classification_report(y_test, y_pred, target_names=iris.target_names))

# 7. 交叉验证
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
print(f"交叉验证得分: {cv_scores.mean():.2f} (+/- {cv_scores.std():.2f})")

# 8. 特征重要性
importances = model.feature_importances_
for feature, importance in zip(iris.feature_names, importances):
    print(f"{feature}: {importance:.3f}")
```

## 面试要点

### 常见问题

**Q1: 监督学习和无监督学习的区别？**
> 监督学习使用带标签的数据训练，目标是学习输入到输出的映射；无监督学习使用无标签数据，目标是发现数据的内在结构和模式。

**Q2: 什么是过拟合，如何解决？**
> 过拟合是模型在训练数据上表现很好但在新数据上表现差。解决方法：1) 增加训练数据 2) 正则化（L1/L2）3) 特征选择 4) 交叉验证 5) 提前停止 6) 集成方法。

**Q3: 精确率和召回率的区别？**
> 精确率 = TP/(TP+FP)，表示预测为正类中实际为正类的比例；召回率 = TP/(TP+FN)，表示实际正类中被正确预测的比例。F1是两者的调和平均。

**Q4: Bagging和Boosting的区别？**
> Bagging并行训练多个模型，通过平均/投票降低方差；Boosting串行训练，每个模型关注前一个模型的错误，降低偏差。Bagging代表是随机森林，Boosting代表是XGBoost。

## 相关概念 (Related Concepts)

### 数据结构
- [数组](../data-structures/array.md)：特征向量与数据矩阵
- [树](../data-structures/tree.md)：决策树模型
- [图](../data-structures/graph.md)：图神经网络与关系数据

### 算法
- [CNN](./cnn.md)：卷积神经网络
- [Transformer](./transformers.md)：注意力机制模型
- [优化算法](../../references/optimization.md)：梯度下降与优化器

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：模型训练与推理时间
- [空间复杂度](../../references/space-complexity.md)：模型参数与内存占用

### 系统实现
- [概率论](../../mathematics/probability.md)：概率统计基础
- [线性代数](../../mathematics/linear-algebra.md)：矩阵运算与向量空间
- [分布式训练](../../references/distributed-training.md)：大规模模型训练

- [CNN](./cnn.md) - 卷积神经网络
- [RNN与LSTM](./rnn-lstm.md) - 循环神经网络
- [Transformer](./transformers.md) - 注意力机制模型
- [概率论](../../mathematics/probability.md) - 概率统计基础
- [线性代数](../../mathematics/linear-algebra.md) - 矩阵运算与向量空间
- [图论](../../mathematics/graph-theory.md) - 图神经网络数学基础

## 参考资料

1. "Pattern Recognition and Machine Learning" by Bishop
2. "The Elements of Statistical Learning" by Hastie, Tibshirani, Friedman
3. "Hands-On Machine Learning with Scikit-Learn and TensorFlow" by Géron
4. Andrew Ng机器学习课程
5. Scikit-Learn官方文档
