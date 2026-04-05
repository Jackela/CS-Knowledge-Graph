# 线性回归 (Linear Regression)

## 简介
线性回归是一种基本的监督学习算法，通过拟合一条直线（或超平面）来建立输入特征与连续目标变量之间的线性关系。

## 核心概念

### 数学模型
假设目标变量 $y$ 与特征 $x$ 之间存在线性关系：

$$y = \beta_0 + \beta_1 x_1 + \beta_2 x_2 + ... + \beta_n x_n + \epsilon$$

或矩阵形式：

$$\mathbf{y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\epsilon}$$

其中：
- $\beta_0$：截距（偏置）
- $\beta_i$：各特征的权重系数
- $\epsilon$：误差项，服从均值为0的正态分布

### 损失函数
采用均方误差（Mean Squared Error, MSE）：

$$J(\boldsymbol{\beta}) = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2 = \frac{1}{n} \sum_{i=1}^{n} (y_i - \mathbf{x}_i^T\boldsymbol{\beta})^2$$

### 参数求解
- **解析解（正规方程）**：$\boldsymbol{\beta} = (\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{y}$
- **迭代解（梯度下降）**：$\boldsymbol{\beta} := \boldsymbol{\beta} - \alpha \nabla J(\boldsymbol{\beta})$

### 假设条件
1. 线性关系：特征与目标变量呈线性关系
2. 独立性：观测值相互独立
3. 同方差性：误差项方差恒定
4. 正态性：误差项服从正态分布

## 实现方式

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# 生成模拟数据
np.random.seed(42)
X = 2 * np.random.rand(100, 1)
y = 4 + 3 * X + np.random.randn(100, 1)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建并训练线性回归模型
model = LinearRegression()
model.fit(X_train, y_train)

# 预测
y_pred = model.predict(X_test)

# 输出结果
print(f"截距 (β₀): {model.intercept_[0]:.4f}")
print(f"系数 (β₁): {model.coef_[0][0]:.4f}")
print(f"MSE: {mean_squared_error(y_test, y_pred):.4f}")
print(f"R² Score: {r2_score(y_test, y_pred):.4f}")

# ===== 带正则化的线性回归 =====
# Ridge回归 (L2正则化)
ridge = Ridge(alpha=1.0)
ridge.fit(X_train, y_train)

# Lasso回归 (L1正则化)
lasso = Lasso(alpha=0.1)
lasso.fit(X_train, y_train)

print(f"\nRidge系数: {ridge.coef_[0]:.4f}")
print(f"Lasso系数: {lasso.coef_[0]:.4f}")
```

## 应用场景
- **房价预测**：根据房屋特征预测价格
- **销售预测**：基于历史数据预测未来销售额
- **风险评估**：信用评分、保险定价
- **医学研究**：分析药物剂量与疗效关系
- **经济学**：分析各因素对GDP的影响

## 面试要点

1. **Q: 线性回归中的R²代表什么？**
   A: R²（决定系数）表示模型解释的目标变量方差比例，取值0到1，越接近1说明模型拟合越好。计算公式：$R^2 = 1 - \frac{SS_{res}}{SS_{tot}}$。

2. **Q: 多重共线性是什么？如何解决？**
   A: 多重共线性指特征间高度相关，会导致系数估计不稳定。可通过VIF检测，解决方法包括：移除相关特征、PCA降维、使用Ridge回归等正则化方法。

3. **Q: 梯度下降和正规方程的优缺点？**
   A: 正规方程无需选择学习率、无需迭代，但计算复杂度$O(n^3)$，不适合大规模数据；梯度下降适合大规模数据，需要选择学习率和迭代次数，可能陷入局部最优。

4. **Q: Ridge和Lasso回归的区别？**
   A: Ridge使用L2正则化（$\lambda\sum\beta_j^2$），使系数趋于0但不等于0，适合处理多重共线性；Lasso使用L1正则化（$\lambda\sum|\beta_j|$），可产生稀疏解实现特征选择。

## 相关概念

### AI & Data Systems
- [逻辑回归](./logistic-regression.md)
- [监督学习](./supervised-learning.md)
- [多项式回归](./polynomial-regression.md)
- [神经网络基础](../deep-learning/neural-networks.md)

### 数学基础
- [线性代数](../../mathematics/linear-algebra.md)
- [概率论与统计](../../mathematics/probability-statistics.md)
- [微积分](../../mathematics/calculus.md)
- [最优化方法](../../mathematics/optimization.md)
