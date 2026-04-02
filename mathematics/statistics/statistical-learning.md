# 统计学习基础 (Statistical Learning Theory)

## 简介

**统计学习**（Statistical Learning）是机器学习理论的数学基础，研究从数据中学习的统计原理。涵盖偏差-方差分解、PAC 学习理论、VC 维等核心概念，为理解模型的泛化能力、过拟合与欠拟合、以及学习算法的样本复杂度提供了理论框架。

## 核心概念

### 学习问题框架

**基本设定：**
- 输入空间 X，输出空间 Y
- 训练集 D = {(x₁,y₁), ..., (xₙ,yₙ)} 从分布 P(X,Y) 独立采样
- 假设空间 H：所有候选模型
- 损失函数 L(y, f(x))：预测误差度量

**风险（期望风险）：**
```
R(f) = E[L(y, f(x))] = ∫ L(y, f(x)) dP(x,y)
```

**经验风险：**
```
R_emp(f) = (1/n) Σ L(yᵢ, f(xᵢ))
```

### 偏差-方差分解

**对于平方损失：**
```
E[(y - f̂(x))²] = Bias² + Variance + Noise

Bias² = (E[f̂(x)] - f*(x))²  # 模型偏差
Variance = E[(f̂(x) - E[f̂(x)])²]  # 模型方差
Noise = 数据本身的不可约误差
```

**权衡（Bias-Variance Tradeoff）：**
- 高偏差 → 欠拟合（模型太简单）
- 高方差 → 过拟合（模型太复杂）

### PAC 学习理论

**Probably Approximately Correct：**

**定义：** 算法 A 是 PAC 可学习的，如果：
- 对于任意 ε > 0（精度）、δ > 0（置信度）
- 存在多项式 poly(1/ε, 1/δ, n, size(c))
- 使得在样本数 m ≥ poly(...) 时，以概率 ≥ 1-δ 找到假设 h 满足 error(h) ≤ ε

**样本复杂度：**
```
对于有限假设空间 |H|：
m ≥ (1/ε)(ln|H| + ln(1/δ))
```

### VC 维

**打散（Shatter）：**
假设空间 H 能打散样本集 S，如果对 S 的任意标签赋值，H 中都有假设能完美分类。

**VC 维：**
H 能打散的最大样本集的大小。

**泛化界：**
```
以概率 ≥ 1-δ：
R(h) ≤ R_emp(h) + O(√((VC(H)ln(n) + ln(1/δ))/n))
```

**常见模型的 VC 维：**
- 线性分类器（d 维）：d+1
- 神经网络：与参数数量相关
- 决策树：与节点数相关
- k-NN：无限（记忆训练集）

### 正则化理论

**目标：**
```
min R_emp(f) + λ·Ω(f)
```

**常见正则化：**
- L1（Lasso）：Ω(f) = ||w||₁，产生稀疏解
- L2（Ridge）：Ω(f) = ||w||₂²，权重衰减
- 弹性网络：L1 + L2 的组合

**贝叶斯解释：**
正则化等价于最大后验估计（MAP）

## 实现方式

```python
import numpy as np
from typing import List, Tuple, Callable
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt

class StatisticalLearning:
    """统计学习理论演示"""
    
    @staticmethod
    def bias_variance_decomposition(estimators: List, 
                                     X_test: np.ndarray,
                                     y_test: np.ndarray,
                                     n_iterations: int = 100) -> Tuple[float, float, float]:
        """
        估计偏差-方差-噪声分解
        
        Args:
            estimators: 在不同训练集上训练的模型列表
            X_test: 测试特征
            y_test: 测试标签
            n_iterations: 迭代次数
        
        Returns:
            (bias², variance, noise)
        """
        predictions = []
        
        for model in estimators[:n_iterations]:
            pred = model.predict(X_test.reshape(-1, 1))
            predictions.append(pred)
        
        predictions = np.array(predictions)
        mean_pred = np.mean(predictions, axis=0)
        
        # 偏差²
        bias_squared = np.mean((mean_pred - y_test) ** 2)
        
        # 方差
        variance = np.mean(np.var(predictions, axis=0))
        
        # 总误差（假设噪声为 0）
        total_error = np.mean((predictions - y_test) ** 2)
        
        return bias_squared, variance, total_error - bias_squared - variance
    
    @staticmethod
    def empirical_risk(y_true: np.ndarray, y_pred: np.ndarray, 
                       loss_fn: str = 'mse') -> float:
        """
        计算经验风险
        
        Args:
            loss_fn: 'mse', 'mae', 'hinge', 'log'
        """
        if loss_fn == 'mse':
            return np.mean((y_true - y_pred) ** 2)
        elif loss_fn == 'mae':
            return np.mean(np.abs(y_true - y_pred))
        elif loss_fn == 'hinge':
            return np.mean(np.maximum(0, 1 - y_true * y_pred))
        elif loss_fn == 'log':
            # 二元交叉熵
            epsilon = 1e-15
            y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
            return -np.mean(y_true * np.log(y_pred) + 
                           (1 - y_true) * np.log(1 - y_pred))
        else:
            raise ValueError(f"Unknown loss: {loss_fn}")
    
    @staticmethod
    def complexity_regularization(X: np.ndarray, y: np.ndarray,
                                   degrees: List[int] = None,
                                   alphas: List[float] = None):
        """
        演示模型复杂度与正则化的影响
        """
        if degrees is None:
            degrees = [1, 3, 5, 10, 15]
        if alphas is None:
            alphas = [0, 0.001, 0.01, 0.1, 1]
        
        results = {}
        
        for degree in degrees:
            for alpha in alphas:
                # 创建多项式回归模型
                model = make_pipeline(
                    PolynomialFeatures(degree),
                    Ridge(alpha=alpha)
                )
                
                # 学习曲线
                train_sizes, train_scores, val_scores = learning_curve(
                    model, X.reshape(-1, 1), y,
                    cv=5, train_sizes=np.linspace(0.1, 1.0, 10)
                )
                
                results[(degree, alpha)] = {
                    'train_sizes': train_sizes,
                    'train_scores': train_scores,
                    'val_scores': val_scores
                }
        
        return results
    
    @staticmethod
    def vc_dimension_estimate(model_name: str, params: dict) -> int:
        """
        估计常见模型的 VC 维（简化版）
        
        Returns:
            估计的 VC 维上界
        """
        if model_name == 'linear':
            # d 维线性分类器: d+1
            return params.get('n_features', 1) + 1
        elif model_name == 'polynomial':
            # k 次多项式在 d 维: C(d+k, k)
            d = params.get('n_features', 1)
            k = params.get('degree', 1)
            from math import comb
            return comb(d + k, k)
        elif model_name == 'neural_network':
            # 粗略估计：与参数数量相关
            layers = params.get('layers', [10])
            vc = 0
            for i in range(len(layers) - 1):
                vc += layers[i] * layers[i+1]
            return vc
        else:
            return float('inf')
    
    @staticmethod
    def sample_complexity(vc_dim: int, epsilon: float = 0.1, 
                          delta: float = 0.05) -> int:
        """
        基于 VC 维的样本复杂度估计
        
        公式: m ≥ (1/ε)(8·VC(H)·log(13/ε) + 4·log(2/δ))
        """
        import math
        return int((1/epsilon) * (8 * vc_dim * math.log(13/epsilon) + 
                                   4 * math.log(2/delta)))


# 使用示例
if __name__ == "__main__":
    sl = StatisticalLearning()
    
    # 生成数据
    np.random.seed(42)
    X = np.linspace(0, 10, 100)
    y = np.sin(X) + 0.1 * np.random.randn(100)
    
    print("=== 经验风险计算 ===")
    y_pred_simple = np.sin(X)  # 理想预测
    risk = sl.empirical_risk(y, y_pred_simple, 'mse')
    print(f"MSE 经验风险: {risk:.4f}")
    
    print("\n=== VC 维估计 ===")
    vc_linear = sl.vc_dimension_estimate('linear', {'n_features': 10})
    vc_poly = sl.vc_dimension_estimate('polynomial', {'n_features': 2, 'degree': 3})
    print(f"10维线性模型 VC 维: {vc_linear}")
    print(f"2维3次多项式 VC 维: {vc_poly}")
    
    print("\n=== 样本复杂度 ===")
    for vc in [10, 100, 1000]:
        m = sl.sample_complexity(vc, epsilon=0.1, delta=0.05)
        print(f"VC={vc}: 需要约 {m} 个样本")
    
    print("\n=== 正则化效果 ===")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    for alpha in [0, 0.01, 0.1, 1, 10]:
        model = make_pipeline(PolynomialFeatures(10), Ridge(alpha=alpha))
        model.fit(X_train.reshape(-1, 1), y_train)
        train_err = np.mean((model.predict(X_train.reshape(-1, 1)) - y_train) ** 2)
        test_err = np.mean((model.predict(X_test.reshape(-1, 1)) - y_test) ** 2)
        print(f"α={alpha:5.2f}: 训练误差={train_err:.4f}, 测试误差={test_err:.4f}")
```

## 应用场景

### 1. 模型选择
- **交叉验证**：基于泛化误差选择模型
- **信息准则**：AIC、BIC 权衡拟合与复杂度
- **结构风险最小化**：SRM 原则

### 2. 深度学习理论
- **过参数化**：双下降现象
- **隐式正则化**：SGD 的泛化效果
- **神经正切核**：宽网络的极限行为

### 3. 强化学习
- **样本效率**：探索-利用权衡的理论分析
- **遗憾界（Regret Bound）**：算法性能保证

### 4. 在线学习
- **遗憾分析**：累积损失与最佳固定假设的比较
- **专家算法**：加权多数算法的理论保证

## 面试要点

**Q1: 什么是经验风险最小化（ERM）？**
A: 在训练集上最小化平均损失。但可能导致过拟合，需要结构风险最小化（SRM）加入正则化。

**Q2: 解释偏差-方差权衡。**
A: 复杂模型方差高（对训练数据敏感）、偏差低；简单模型偏差高（欠拟合）、方差低。需要在两者间找到平衡。

**Q3: VC 维的意义是什么？**
A: 衡量假设空间的复杂度。VC 维越大，模型越复杂，需要更多样本才能保证泛化。

**Q4: 正则化的统计解释？**
A: L2 正则化对应高斯先验（权重小），L1 对应拉普拉斯先验（稀疏）。是 MAP 估计的体现。

**Q5: 深度学习的泛化之谜是什么？**
A: 传统理论认为过参数化会过拟合，但深度学习实践中大模型往往泛化好。可能与隐式正则化、解的平坦性有关。

## 相关概念

### 数据结构
- [矩阵](../data-structures/matrix.md) - 数据表示
- [向量](../data-structures/vector.md) - 特征空间

### 算法
- [梯度下降](./gradient-descent.md) - 优化方法
- [交叉验证](./cross-validation.md) - 模型评估
- [贝叶斯推断](./bayesian-statistics.md) - 概率视角

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 计算复杂度
- [样本复杂度](../../references/sample-complexity.md) - 数据需求

### 系统实现
- [Scikit-learn](../../references/scikit-learn.md) - 机器学习库
- [TensorFlow/PyTorch](../../references/deep-learning-frameworks.md) - 深度学习
- [AutoML](../../references/automl.md) - 自动模型选择
