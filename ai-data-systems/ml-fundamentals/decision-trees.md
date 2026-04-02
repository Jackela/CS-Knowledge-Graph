# 决策树 (Decision Trees)

## 简介
决策树是一种直观且可解释性强的监督学习算法，通过递归地根据特征值进行分割，构建树形结构来进行分类或回归预测。

## 核心概念

### 树结构组成
- **根节点**（Root）：包含所有数据的起始节点
- **内部节点**（Internal Node）：进行特征判断的节点
- **叶节点**（Leaf）：输出最终预测结果的终端节点
- **分支**（Branch）：表示特征判断的不同结果路径

### 分裂准则

**信息增益（ID3算法）**
基于熵的减少：$IG(D, A) = H(D) - \sum_{v \in Values(A)} \frac{|D_v|}{|D|}H(D_v)$

其中熵：$H(D) = -\sum_{i=1}^{k} p_i \log_2 p_i$

**信息增益率（C4.5算法）**
$Gain\_ratio(D, A) = \frac{IG(D, A)}{H_A(D)}$

**基尼指数（CART分类树）**
$Gini(D) = 1 - \sum_{i=1}^{k} p_i^2$

$Gini\_index(D, A) = \sum_{v} \frac{|D_v|}{|D|}Gini(D_v)$

**均方误差（CART回归树）**
$MSE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \bar{y})^2$

### 剪枝策略
- **预剪枝**：在树构建过程中提前停止，限制深度、叶节点数或最小样本数
- **后剪枝**：先构建完整树，再自底向上剪枝，使用验证集评估

## 实现方式

```python
import numpy as np
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_text, plot_tree
from sklearn.datasets import load_iris, fetch_california_housing
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, mean_squared_error
import matplotlib.pyplot as plt

# ===== 分类树示例 =====
iris = load_iris()
X, y = iris.data, iris.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建决策树分类器
dt_clf = DecisionTreeClassifier(
    criterion='gini',      # 分裂准则: 'gini' 或 'entropy'
    max_depth=3,           # 最大深度
    min_samples_split=5,   # 分裂最小样本数
    min_samples_leaf=2,    # 叶节点最小样本数
    random_state=42
)

dt_clf.fit(X_train, y_train)

# 预测与评估
y_pred = dt_clf.predict(X_test)
print(f"分类准确率: {accuracy_score(y_test, y_pred):.4f}")
print(f"特征重要性: {dict(zip(iris.feature_names, dt_clf.feature_importances_))}")

# 文本可视化
print("\n树结构:")
print(export_text(dt_clf, feature_names=list(iris.feature_names)))

# ===== 回归树示例 =====
housing = fetch_california_housing()
X_reg, y_reg = housing.data, housing.target

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42)

dt_reg = DecisionTreeRegressor(
    max_depth=5,
    min_samples_split=20,
    random_state=42
)
dt_reg.fit(X_train_r, y_train_r)

y_pred_r = dt_reg.predict(X_test_r)
print(f"\n回归MSE: {mean_squared_error(y_test_r, y_pred_r):.4f}")
print(f"R² Score: {dt_reg.score(X_test_r, y_test_r):.4f}")

# ===== 交叉验证选择最佳深度 =====
depths = range(1, 11)
cv_scores = []

for depth in depths:
    dt = DecisionTreeClassifier(max_depth=depth, random_state=42)
    scores = cross_val_score(dt, X, y, cv=5)
    cv_scores.append(scores.mean())

best_depth = list(depths)[np.argmax(cv_scores)]
print(f"\n最佳深度: {best_depth}, 交叉验证得分: {max(cv_scores):.4f}")
```

## 应用场景
- **信用评估**：根据用户特征判断信用等级
- **医疗诊断**：基于症状和检查结果辅助诊断
- **客户流失预测**：识别可能流失的客户特征
- **推荐系统**：基于用户行为特征进行推荐
- **欺诈检测**：识别异常交易模式

## 面试要点

1. **Q: 决策树的优缺点？**
   A: 优点：可解释性强，无需特征缩放，可处理非线性关系；缺点：容易过拟合，对数据微小变化敏感，难以捕捉特征间的复杂交互。

2. **Q: 信息增益和基尼指数的区别？**
   A: 信息增益基于熵，计算对数运算较慢，偏好取值多的特征；基尼指数计算更快，偏好大的分支。实践中两者效果相近，基尼指数更常用。

3. **Q: 如何处理决策树的过拟合？**
   A: 1) 限制树的深度和叶节点数量；2) 设置最小分裂样本数和叶节点最小样本数；3) 剪枝（预剪枝/后剪枝）；4) 使用随机森林等集成方法。

4. **Q: 决策树和随机森林的关系？**
   A: 随机森林是多个决策树的集成，通过Bagging和特征随机性减少过拟合。单棵决策树方差大易过拟合，随机森林通过平均降低方差提高泛化能力。

## 相关概念

### AI & Data Systems
- [随机森林](./random-forest.md)
- [梯度提升树](./gradient-boosting.md)
- [XGBoost/LightGBM](./xgboost-lightgbm.md)
- [监督学习](./supervised-learning.md)
- [集成学习](./ensemble-learning.md)

### 数学基础
- [信息论](../../mathematics/information-theory.md)
- [概率论与统计](../../mathematics/probability-statistics.md)
- [熵与交叉熵](../../mathematics/entropy-crossentropy.md)
