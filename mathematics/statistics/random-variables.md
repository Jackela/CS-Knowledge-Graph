# 随机变量 (Random Variables)

## 简介

**随机变量**（Random Variables）是概率论的核心概念，将随机试验的结果映射为数值。分为离散型（如抛硬币次数）和连续型（如测量误差），通过概率分布函数、期望、方差等数字特征描述其统计规律，是统计推断和机器学习的基础。

## 核心概念

### 定义与分类

**随机变量：** 定义在样本空间 Ω 上的函数 X: Ω → ℝ

**离散型随机变量：**
- 取值可数（有限或可数无限）
- 用概率质量函数（PMF）描述：P(X = x)
- 例子：二项分布、泊松分布、几何分布

**连续型随机变量：**
- 取值不可数（实数区间）
- 用概率密度函数（PDF）描述：f(x)
- P(a ≤ X ≤ b) = ∫[a,b] f(x)dx
- 例子：正态分布、均匀分布、指数分布

### 数字特征

**期望（Expectation/Mean）：**
```
离散: E[X] = Σ x · P(X=x)
连续: E[X] = ∫ x · f(x) dx
```

**方差（Variance）：**
```
Var(X) = E[(X - E[X])²] = E[X²] - E[X]²
```

**标准差：** σ = √Var(X)

**协方差（Covariance）：**
```
Cov(X,Y) = E[(X-E[X])(Y-E[Y])] = E[XY] - E[X]E[Y]
```

**相关系数：**
```
ρ(X,Y) = Cov(X,Y) / (σ_X · σ_Y)
```

### 常见分布

**离散分布：**

| 分布 | PMF | 期望 | 方差 |
|------|-----|------|------|
| 伯努利 Bernoulli(p) | p^k(1-p)^(1-k) | p | p(1-p) |
| 二项 Binomial(n,p) | C(n,k)p^k(1-p)^(n-k) | np | np(1-p) |
| 泊松 Poisson(λ) | λ^k e^(-λ)/k! | λ | λ |
| 几何 Geometric(p) | (1-p)^(k-1)p | 1/p | (1-p)/p² |

**连续分布：**

| 分布 | PDF | 期望 | 方差 |
|------|-----|------|------|
| 均匀 Uniform(a,b) | 1/(b-a) | (a+b)/2 | (b-a)²/12 |
| 正态 Normal(μ,σ²) | (1/√(2πσ²))e^(-(x-μ)²/2σ²) | μ | σ² |
| 指数 Exponential(λ) | λe^(-λx) | 1/λ | 1/λ² |

## 实现方式

```python
import numpy as np
from scipy import stats
from typing import Union, List

class RandomVariable:
    """随机变量操作类"""
    
    @staticmethod
    def expected_value(values: List[float], probabilities: List[float] = None) -> float:
        """
        计算离散随机变量的期望
        
        Args:
            values: 取值
            probabilities: 对应概率（为 None 时假设均匀分布）
        
        Returns:
            期望值
        """
        if probabilities is None:
            return np.mean(values)
        
        return sum(v * p for v, p in zip(values, probabilities))
    
    @staticmethod
    def variance(values: List[float], probabilities: List[float] = None, 
                 ddof: int = 0) -> float:
        """
        计算方差
        
        Args:
            ddof: Delta Degrees of Freedom（样本方差用 1）
        """
        if probabilities is None:
            return np.var(values, ddof=ddof)
        
        mean = RandomVariable.expected_value(values, probabilities)
        return sum(p * (v - mean) ** 2 for v, p in zip(values, probabilities))
    
    @staticmethod
    def covariance(x: List[float], y: List[float]) -> float:
        """计算协方差"""
        return np.cov(x, y, bias=True)[0][1]
    
    @staticmethod
    def correlation(x: List[float], y: List[float]) -> float:
        """计算皮尔逊相关系数"""
        return np.corrcoef(x, y)[0][1]
    
    @staticmethod
    def moment(values: List[float], k: int, 
               probabilities: List[float] = None) -> float:
        """
        计算 k 阶原点矩 E[X^k]
        """
        if probabilities is None:
            return np.mean([v**k for v in values])
        return sum(p * (v**k) for v, p in zip(values, probabilities))
    
    @staticmethod
    def skewness(values: List[float]) -> float:
        """
        计算偏度（Skewness）
        衡量分布的不对称性
        """
        return stats.skew(values)
    
    @staticmethod
    def kurtosis(values: List[float]) -> float:
        """
        计算峰度（Kurtosis）
        衡量分布的尖锐程度
        """
        return stats.kurtosis(values)


# 常见分布的随机变量生成
class DistributionExamples:
    """常见分布示例"""
    
    @staticmethod
    def bernoulli(p: float = 0.5, size: int = 1000) -> np.ndarray:
        """伯努利分布"""
        return np.random.choice([0, 1], size=size, p=[1-p, p])
    
    @staticmethod
    def binomial(n: int = 10, p: float = 0.5, size: int = 1000) -> np.ndarray:
        """二项分布"""
        return np.random.binomial(n, p, size)
    
    @staticmethod
    def poisson(lam: float = 3.0, size: int = 1000) -> np.ndarray:
        """泊松分布"""
        return np.random.poisson(lam, size)
    
    @staticmethod
    def normal(mu: float = 0, sigma: float = 1, size: int = 1000) -> np.ndarray:
        """正态分布"""
        return np.random.normal(mu, sigma, size)
    
    @staticmethod
    def exponential(scale: float = 1.0, size: int = 1000) -> np.ndarray:
        """指数分布（scale = 1/λ）"""
        return np.random.exponential(scale, size)
    
    @staticmethod
    def uniform(low: float = 0, high: float = 1, size: int = 1000) -> np.ndarray:
        """均匀分布"""
        return np.random.uniform(low, high, size)


# 使用示例
if __name__ == "__main__":
    rv = RandomVariable()
    
    # 离散随机变量示例
    print("=== 离散随机变量 ===")
    values = [1, 2, 3, 4, 5, 6]
    probs = [1/6] * 6  # 公平骰子
    
    mean = rv.expected_value(values, probs)
    var = rv.variance(values, probs)
    print(f"骰子期望: {mean:.4f}")
    print(f"骰子方差: {var:.4f}")
    
    # 连续分布示例
    print("\n=== 正态分布 ===")
    data = DistributionExamples.normal(mu=100, sigma=15, size=10000)
    print(f"生成数据: 均值={np.mean(data):.2f}, 标准差={np.std(data):.2f}")
    print(f"偏度: {rv.skewness(data):.4f}")
    print(f"峰度: {rv.kurtosis(data):.4f}")
    
    # 协方差和相关系数
    print("\n=== 相关性分析 ===")
    x = np.random.normal(0, 1, 1000)
    y = 2 * x + np.random.normal(0, 0.5, 1000)  # y 与 x 相关
    
    cov = rv.covariance(x.tolist(), y.tolist())
    corr = rv.correlation(x.tolist(), y.tolist())
    print(f"协方差: {cov:.4f}")
    print(f"相关系数: {corr:.4f}")
    
    # 不同分布的比较
    print("\n=== 分布比较 ===")
    distributions = [
        ("正态", DistributionExamples.normal(0, 1, 1000)),
        ("指数", DistributionExamples.exponential(1, 1000)),
        ("均匀", DistributionExamples.uniform(-1, 1, 1000)),
    ]
    
    for name, data in distributions:
        print(f"{name}: 均值={np.mean(data):.3f}, 标准差={np.std(data):.3f}")
```

## 应用场景

### 1. 机器学习
- **特征工程**：数据分布分析、异常值检测
- **概率模型**：朴素贝叶斯、高斯混合模型
- **随机初始化**：权重初始化策略（Xavier、He）

### 2. 金融工程
- **风险度量**：VaR（Value at Risk）计算
- **期权定价**：Black-Scholes 模型
- **投资组合**：马科维茨均值-方差优化

### 3. 质量工程
- **六西格玛**：过程能力分析
- **可靠性工程**：寿命分布建模
- **A/B 测试**：统计显著性检验

### 4. 通信系统
- **信号处理**：噪声建模（高斯白噪声）
- **信道容量**：香农公式中的随机变量
- **编码理论**：错误概率分析

## 面试要点

**Q1: 离散型和连续型随机变量的区别？**
A: 离散型取值可数，用 PMF 描述；连续型取值不可数，用 PDF 描述，单点概率为 0，区间概率用积分计算。

**Q2: 期望和方差的物理意义？**
A: 期望是分布的中心位置（一阶矩），方差是分布的离散程度（二阶中心矩）。标准差与原始数据同量纲。

**Q3: 协方差和相关系数的区别？**
A: 协方差有量纲，受变量尺度影响；相关系数标准化到 [-1,1]，无量纲，反映线性相关程度。

**Q4: 大数定律和中心极限定理的区别？**
A: 大数定律：样本均值收敛于期望（一致性）。中心极限定理：样本均值的分布趋近正态（渐近正态性）。

**Q5: 常见分布的应用场景？**
A: 二项-重复试验成功次数；泊松-稀有事件发生次数；正态-测量误差、自然现象；指数-等待时间、寿命。

## 相关概念

### 数据结构
- [数组](../data-structures/array.md) - 数据存储
- [向量](../data-structures/vector.md) - 多维随机变量

### 算法
- [概率分布](./probability-distributions.md) - 具体分布实现
- [蒙特卡洛方法](./monte-carlo.md) - 随机采样
- [假设检验](./hypothesis-testing.md) - 统计推断

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 采样复杂度
- [空间复杂度](../../references/space-complexity.md) - 存储需求

### 系统实现
- [NumPy](../../references/numpy.md) - 数值计算
- [SciPy](../../references/scipy.md) - 统计分布
- [概率编程](../../references/probabilistic-programming.md) - PyMC, Stan
