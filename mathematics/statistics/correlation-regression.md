# 相关与回归 (Correlation and Regression)

## 简介
相关分析研究变量间的关联程度，回归分析则建立变量间的定量关系模型。这两者是统计学和机器学习的基石，广泛应用于预测建模、因果推断和特征工程，从简单的线性回归到复杂的非线性模型构成了数据科学的核心工具集。

## 核心概念

### 相关分析

**皮尔逊相关系数 (Pearson Correlation)：**
衡量两个连续变量线性相关程度，取值范围[-1, 1]：

$$r = \frac{\sum_{i=1}^{n} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{n} (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^{n} (y_i - \bar{y})^2}}$$

等价形式：
$$r = \frac{\text{Cov}(X, Y)}{\sigma_X \sigma_Y}$$

**解释标准：**
- |r| = 0：无线性相关
- 0 < |r| < 0.3：弱相关
- 0.3 ≤ |r| < 0.7：中等相关
- 0.7 ≤ |r| < 1：强相关
- |r| = 1：完全线性相关

**斯皮尔曼等级相关 (Spearman Correlation)：**
基于秩次的非参数相关系数，对异常值稳健：
$$\rho = 1 - \frac{6\sum d_i^2}{n(n^2 - 1)}$$

适用于：(1) 数据非正态分布；(2) 存在异常值；(3) 变量为序数类型；(4) 关系单调但非线性。

**肯德尔τ相关 (Kendall's Tau)：**
另一非参数相关系数，基于一致对和不一致对：
$$\tau = \frac{n_c - n_d}{\frac{1}{2}n(n-1)}$$

**相关 vs 因果：**
- 相关不等于因果：冰淇淋销量与溺水事件相关（共同原因：天气炎热）
- 混淆变量：影响X和Y的第三方变量
- 确立因果需要：随机化实验、时间先后、排除其他解释

### 简单线性回归

**模型：**
$$Y = \beta_0 + \beta_1 X + \epsilon, \quad \epsilon \sim N(0, \sigma^2)$$

**最小二乘估计：**
最小化残差平方和：
$$\min_{\beta_0, \beta_1} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2 = \sum_{i=1}^{n} (y_i - \beta_0 - \beta_1 x_i)^2$$

参数估计：
$$\hat{\beta}_1 = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2} = r \frac{s_y}{s_x}$$
$$\hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}$$

**模型评估：**

**决定系数 $R^2$：**
$$R^2 = 1 - \frac{SS_{res}}{SS_{tot}} = \frac{\sum (\hat{y}_i - \bar{y})^2}{\sum (y_i - \bar{y})^2}$$

表示Y的变异中能被X解释的比例。简单线性回归中 $R^2 = r^2$。

**残差分析：**
- 残差应随机分布在0周围
- 残差方差应恒定（同方差性）
- 残差应近似正态分布
- 不应有模式（表明模型设定错误）

### 多元线性回归

**模型：**
$$Y = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + ... + \beta_p X_p + \epsilon$$

矩阵形式：
$$\mathbf{y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\epsilon}$$

**参数估计：**
$$\hat{\boldsymbol{\beta}} = (\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T\mathbf{y}$$

**假设检验：**
- 整体显著性：F检验 $H_0: \beta_1 = \beta_2 = ... = \beta_p = 0$
- 单个系数：t检验 $H_0: \beta_j = 0$

**调整 $R^2$：**
$$R^2_{adj} = 1 - (1 - R^2)\frac{n-1}{n-p-1}$$

惩罚添加不必要的预测变量。

**多重共线性：**
当预测变量高度相关时，$(\mathbf{X}^T\mathbf{X})^{-1}$ 不稳定，导致：
- 系数估计方差大
- 系数符号可能不合理
- 对数据微小变化敏感

诊断：方差膨胀因子 $VIF_j = \frac{1}{1 - R_j^2}$，$VIF > 10$ 表示严重共线性。

### 回归诊断

**经典假设：**
1. 线性关系：Y与X的关系是线性的
2. 独立性：观测值相互独立
3. 同方差性：残差方差恒定
4. 正态性：残差近似正态分布
5. 无异常值/强影响点

**诊断方法：**
- 残差图 vs 拟合值
- Q-Q图检验正态性
- 杠杆值和Cook距离识别异常值

### 正则化回归

**岭回归 (Ridge)：**
L2正则化：
$$\min_{\beta} \left\{ \sum_{i=1}^{n} (y_i - \hat{y}_i)^2 + \lambda \sum_{j=1}^{p} \beta_j^2 \right\}$$

**Lasso回归：**
L1正则化：
$$\min_{\beta} \left\{ \sum_{i=1}^{n} (y_i - \hat{y}_i)^2 + \lambda \sum_{j=1}^{p} |\beta_j| \right\}$$

可产生稀疏解（特征选择）。

**弹性网络 (Elastic Net)：**
结合L1和L2：
$$\min_{\beta} \left\{ RSS + \lambda \left[ (1-\alpha)\sum \beta_j^2 + \alpha \sum |\beta_j| \right] \right\}$$

## 实现方式

```python
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# 生成数据
np.random.seed(42)
n = 200
X = np.random.randn(n, 3)
# 真实关系：y = 2 + 3*x1 + 2*x2 + 噪声
y = 2 + 3*X[:, 0] + 2*X[:, 1] + np.random.randn(n) * 0.5

# ========== 相关分析 ==========

# 皮尔逊相关系数
x1, x2 = X[:, 0], X[:, 1]
r_pearson, p_value = stats.pearsonr(x1, x2)
print(f"Pearson correlation: r = {r_pearson:.4f}, p = {p_value:.4f}")

# 相关系数矩阵
corr_matrix = np.corrcoef(X.T)
print(f"\nCorrelation matrix:\n{corr_matrix}")

# 斯皮尔曼相关
x1_ranked = stats.rankdata(x1)
y_ranked = stats.rankdata(y)
r_spearman, p_value = stats.spearmanr(x1, y)
print(f"\nSpearman correlation: ρ = {r_spearman:.4f}, p = {p_value:.4f}")

# 肯德尔τ相关
tau, p_value = stats.kendalltau(x1, y)
print(f"Kendall's tau: τ = {tau:.4f}, p = {p_value:.4f}")

# ========== 简单线性回归 ==========

# 使用sklearn
lr_simple = LinearRegression()
lr_simple.fit(X[:, 0].reshape(-1, 1), y)

print(f"\nSimple Linear Regression (y ~ x1):")
print(f"Intercept: {lr_simple.intercept_:.4f}")
print(f"Coefficient: {lr_simple.coef_[0]:.4f}")
print(f"R²: {lr_simple.score(X[:, 0].reshape(-1, 1), y):.4f}")

# 手动计算
r_xy = np.corrcoef(X[:, 0], y)[0, 1]
beta_1_manual = r_xy * (np.std(y) / np.std(X[:, 0]))
print(f"Manual β₁ calculation: {beta_1_manual:.4f}")

# ========== 多元线性回归 ==========

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

lr_multi = LinearRegression()
lr_multi.fit(X_train, y_train)

print(f"\nMultiple Linear Regression:")
print(f"Intercept: {lr_multi.intercept_:.4f}")
print(f"Coefficients: {lr_multi.coef_}")

y_pred = lr_multi.predict(X_test)
print(f"R² (test): {r2_score(y_test, y_pred):.4f}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")

# 调整R²
n, p = X_test.shape
r2 = r2_score(y_test, y_pred)
r2_adj = 1 - (1 - r2) * (n - 1) / (n - p - 1)
print(f"Adjusted R²: {r2_adj:.4f}")

# ========== 正则化回归 ==========

# 数据标准化（正则化需要）
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 岭回归
ridge = Ridge(alpha=1.0)
ridge.fit(X_train_scaled, y_train)
print(f"\nRidge Regression:")
print(f"Coefficients: {ridge.coef_}")
print(f"R² (test): {ridge.score(X_test_scaled, y_test):.4f}")

# Lasso
lasso = Lasso(alpha=0.1)
lasso.fit(X_train_scaled, y_train)
print(f"\nLasso Regression:")
print(f"Coefficients: {lasso.coef_}")
print(f"R² (test): {lasso.score(X_test_scaled, y_test):.4f}")

# 弹性网络
elastic = ElasticNet(alpha=0.1, l1_ratio=0.5)
elastic.fit(X_train_scaled, y_train)
print(f"\nElastic Net:")
print(f"Coefficients: {elastic.coef_}")
print(f"R² (test): {elastic.score(X_test_scaled, y_test):.4f}")

# ========== 回归诊断 ==========

# 残差分析
y_train_pred = lr_multi.predict(X_train)
residuals = y_train - y_train_pred

# 同方差性检验（视觉检查）
# 残差应随机分布在0周围，无漏斗形状
print(f"\nResidual Analysis:")
print(f"Mean of residuals: {np.mean(residuals):.6f}")
print(f"Std of residuals: {np.std(residuals):.4f}")

# Shapiro-Wilk正态性检验（小样本）
w_stat, p_value = stats.shapiro(residuals[:50])  # 限制样本量
print(f"Shapiro-Wilk test: W={w_stat:.4f}, p={p_value:.4f}")

# 多重共线性检查 - VIF
from statsmodels.stats.outliers_influence import variance_inflation_factor

X_with_const = np.column_stack([np.ones(X_train.shape[0]), X_train])
vif_data = pd.DataFrame()
vif_data["Variable"] = ['const', 'X1', 'X2', 'X3']
vif_data["VIF"] = [variance_inflation_factor(X_with_const, i) 
                   for i in range(X_with_const.shape[1])]
print(f"\nVariance Inflation Factors:\n{vif_data}")

# ========== 统计显著性检验 ==========

import statsmodels.api as sm

# 使用statsmodels获取详细的统计摘要
X_train_const = sm.add_constant(X_train)
model = sm.OLS(y_train, X_train_const).fit()
print(f"\nOLS Regression Summary (statsmodels):")
print(model.summary().tables[1])  # 只打印系数表
```

## 应用场景

### 预测建模
- **销售预测**：基于历史数据和市场因素预测未来销售
- **房价评估**：基于房屋特征（面积、位置、房龄）估计价格
- **需求预测**：库存管理和供应链优化
- **用户LTV预测**：基于早期行为预测用户生命周期价值

### 因果推断
- **A/B测试分析**：量化处理效应大小
- **政策评估**：回归断点设计、双重差分
- **营销归因**：多渠道贡献度分析
- **定价策略**：价格弹性分析

### 特征工程
- **特征选择**：基于相关系数筛选特征
- **多重共线性处理**：VIF分析、PCA降维
- **特征构造**：基于残差分析发现非线性关系
- **目标编码**：回归目标编码处理高基数分类变量

### 数据理解
- **变量关系探索**：相关矩阵热力图
- **异常值检测**：残差分析识别异常观测
- **变量重要性**：标准化系数比较
- **交互效应发现**：引入交互项分析

## 面试要点

1. **Q: 相关系数r=0.8是否意味着X可以很好地预测Y？**  
   A: 不一定。相关只表示线性关系强度，(1) 可能有过拟合，(2) 相关不等于预测能力，(3) 可能存在混杂因素，(4) 关系可能是非线性的。$R^2=0.64$表示Y的64%变异可被X解释，但预测误差还取决于具体应用场景。此外，相关是双向的，而回归有方向性。

2. **Q: 多重共线性有什么问题？如何解决？**  
   A: 问题：(1) 系数估计方差大，不稳定；(2) 系数符号可能与直觉相反；(3) 难以区分各变量的独立贡献。解决方案：(1) 删除高度相关的变量之一；(2) 组合相关变量（如PCA）；(3) 使用正则化（岭回归）；(4) 收集更多数据；(5) 使用领域知识进行变量选择。

3. **Q: R²高就代表模型好吗？什么情况下R²可能误导？**  
   A: 不一定。问题情况：(1) 过拟合时训练R²高但测试性能差；(2) 时间序列中伪回归可能产生高R²；(3) 异常值可能人为抬高R²；(4) 样本量小的高R²不可靠；(5) R²不考虑模型复杂度。应同时看：调整R²、交叉验证性能、残差分析、业务合理性。

4. **Q: L1和L2正则化有什么区别？如何选择？**  
   A: L1(Lasso)产生稀疏解，可进行特征选择，适合高维数据；L2(Ridge)收缩系数但不为零，适合处理多重共线性。L1对异常值更敏感。选择：(1) 需要特征选择选L1；(2) 共线性严重选L2；(3) 两者都重要用弹性网络；(4) 通过交叉验证选择λ参数。实践中，弹性网络通常效果最好。

## 相关概念

### 数据结构
- [数组](../../computer-science/data-structures/array.md) - 数据矩阵存储
- [矩阵](../linear-algebra/matrix-operations.md) - 回归的矩阵表示

### 算法
- [梯度下降](../../computer-science/algorithms/optimization.md) - 参数估计优化
- [最小二乘法](../../computer-science/algorithms/linear-algebra.md) - 解析解计算

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 矩阵运算复杂度

### 系统实现
- [特征工程](../../ai-data-systems/feature-engineering.md) - 回归建模准备
- [机器学习平台](../../ai-data-systems/ml-platform.md) - 模型训练部署

### 数学基础
- [概率分布](./probability-distributions.md) - 误差分布假设
- [假设检验](./hypothesis-testing.md) - 系数显著性检验
- [描述统计](./descriptive-statistics.md) - 相关与回归基础
- [线性代数](../linear-algebra/matrix-operations.md) - 矩阵计算
- [微积分](../calculus/derivatives.md) - 优化基础
