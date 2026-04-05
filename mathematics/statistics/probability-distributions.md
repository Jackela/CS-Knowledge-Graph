# 概率分布 (Probability Distributions)

## 简介
概率分布描述了随机变量取不同值的概率规律，是统计学和机器学习的基础。常见分布包括正态分布、泊松分布、二项分布和指数分布，每种分布都有其特定的应用场景和数学特性。

## 核心概念

### 正态分布 (Normal/Gaussian Distribution)

正态分布是最重要的连续概率分布，其概率密度函数为：

$$f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$$

其中 $\mu$ 为均值，$\sigma$ 为标准差。

**性质：**
- 对称分布，均值=中位数=众数
- 68-95-99.7 法则：约68%数据在 $\mu \pm \sigma$ 内，95%在 $\mu \pm 2\sigma$ 内，99.7%在 $\mu \pm 3\sigma$ 内
- 中心极限定理的基础
- 许多自然现象近似服从正态分布

### 泊松分布 (Poisson Distribution)

描述单位时间或单位空间内随机事件发生次数的离散分布：

$$P(X=k) = \frac{\lambda^k e^{-\lambda}}{k!}, \quad k = 0, 1, 2, ...$$

其中 $\lambda$ 为单位时间（或空间）内事件的平均发生次数。

**性质：**
- 期望和方差都等于 $\lambda$
- 适用于描述稀有事件
- 当 $n$ 很大、$p$ 很小时，二项分布近似于泊松分布
- 独立增量性：不相交区间的事件数相互独立

### 二项分布 (Binomial Distribution)

描述 $n$ 次独立伯努利试验中成功次数的离散分布：

$$P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}, \quad k = 0, 1, ..., n$$

其中 $n$ 为试验次数，$p$ 为每次试验成功的概率。

**性质：**
- 期望 $E[X] = np$
- 方差 $Var(X) = np(1-p)$
- 当 $n=1$ 时退化为伯努利分布
- 当 $n \to \infty$ 时，可用正态分布近似

### 指数分布 (Exponential Distribution)

描述泊松过程中事件间隔时间的连续分布：

$$f(x) = \lambda e^{-\lambda x}, \quad x \geq 0$$

其中 $\lambda$ 为率参数（单位时间内事件发生的平均次数）。

**性质：**
- 无记忆性：$P(X > s+t | X > s) = P(X > t)$
- 期望 $E[X] = \frac{1}{\lambda}$
- 方差 $Var(X) = \frac{1}{\lambda^2}$
- 与泊松分布的关系：泊松过程的事件间隔服从指数分布

### 其他重要分布

**均匀分布 (Uniform Distribution)：**
$$f(x) = \frac{1}{b-a}, \quad a \leq x \leq b$$

**卡方分布 (Chi-Square Distribution)：**
$n$ 个独立标准正态随机变量平方和的分布，自由度为 $n$。

**t分布 (Student's t-Distribution)：**
小样本统计推断中使用，当自由度趋于无穷时趋近标准正态分布。

**F分布 (F-Distribution)：**
两个独立卡方分布随机变量除以各自自由度之比的分布，用于方差分析。

## 实现方式

```python
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# 正态分布
mu, sigma = 0, 1
normal_samples = np.random.normal(mu, sigma, 1000)
print(f"Normal - Mean: {np.mean(normal_samples):.3f}, Std: {np.std(normal_samples):.3f}")

# 计算正态分布的概率密度
x = np.linspace(-5, 5, 100)
pdf = stats.norm.pdf(x, mu, sigma)
cdf = stats.norm.cdf(x, mu, sigma)

# 泊松分布
lambda_param = 3
poisson_samples = np.random.poisson(lambda_param, 1000)
print(f"Poisson - Mean: {np.mean(poisson_samples):.3f}, Var: {np.var(poisson_samples):.3f}")

# 计算泊松分布的概率质量函数
k = np.arange(0, 15)
pmf = stats.poisson.pmf(k, lambda_param)

# 二项分布
n, p = 10, 0.3
binomial_samples = np.random.binomial(n, p, 1000)
print(f"Binomial - Mean: {np.mean(binomial_samples):.3f}, Var: {np.var(binomial_samples):.3f}")

# 指数分布
scale = 2  # 1/lambda
exponential_samples = np.random.exponential(scale, 1000)
print(f"Exponential - Mean: {np.mean(exponential_samples):.3f}")

# 分位数计算（置信区间）
alpha = 0.05
z_critical = stats.norm.ppf(1 - alpha/2)  # 95%置信区间的Z值
print(f"Z-critical (95%): {z_critical:.3f}")

# 假设检验：检验样本是否来自正态分布
from scipy.stats import normaltest
stat, p_value = normaltest(normal_samples)
print(f"Normality test p-value: {p_value:.3f}")
```

## 应用场景

### 机器学习
- **正态分布**：假设检验、高斯混合模型、贝叶斯分类器中的类条件分布
- **二项分布**：二分类问题的概率建模、A/B测试中的转化率分析
- **泊松分布**：用户点击率建模、网站访问量预测、计数数据的回归分析
- **指数分布**：生存分析、可靠性工程、排队论中的服务时间建模

### 数据科学
- **异常检测**：基于正态分布的3σ原则识别异常值
- **A/B测试**：使用二项分布计算转化率置信区间
- **排队系统**：使用泊松-指数模型分析系统性能
- **风险评估**：使用各种分布建模不同风险场景

### 工程应用
- **质量控制**：正态分布用于过程能力分析
- **网络流量**：泊松过程建模网络请求到达
- **设备寿命**：指数分布和威布尔分布用于可靠性分析

## 面试要点

1. **Q: 正态分布为什么重要？**  
   A: 正态分布在自然界中广泛存在（中心极限定理保证大量独立随机变量和趋近正态分布），具有良好的数学性质，是许多统计方法的基础假设。机器学习中的高斯假设简化了许多算法的设计。

2. **Q: 泊松分布和二项分布的关系是什么？**  
   A: 当二项分布的 $n$ 很大、$p$ 很小，且 $np = \lambda$ 适中时，二项分布可用泊松分布近似。泊松分布是二项分布在稀有事件极限下的特例。

3. **Q: 指数分布的无记忆性有什么实际意义？**  
   A: 无记忆性意味着"未来与过去无关"，即已经等待了时间 $s$ 后，还需要等待时间 $t$ 的概率与刚开始等待 $t$ 时间的概率相同。这在设备故障分析、客服等待时间建模中有重要应用。

4. **Q: 如何选择合适的概率分布？**  
   A: 考虑以下因素：(1) 数据类型（连续/离散）；(2) 数据范围（有界/无界）；(3) 分布形状（对称/偏态）；(4) 理论背景（如泊松过程）；(5) 实际应用中的物理意义。可通过Q-Q图、K-S检验等方法验证分布拟合优度。

## 相关概念

### 数据结构
- [数组](../../computer-science/data-structures/array.md) - 存储采样数据
- [哈希表](../../computer-science/data-structures/hash-table.md) - 频率统计

### 算法
- [排序算法](../../computer-science/algorithms/sorting.md) - 数据预处理
- [采样算法](../../computer-science/algorithms/sampling.md) - 从分布中抽样

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 概率计算复杂度

### 系统实现
- [缓存系统](../../computer-science/systems/cache.md) - 访问模式建模
- [负载均衡](../../computer-science/distributed-systems/load-balancing.md) - 请求分布

### 数学基础
- [随机变量](./random-variables.md) - 分布的数学基础
- [中心极限定理](./central-limit-theorem.md) - 正态分布的理论基础
- [大数定律](./law-of-large-numbers.md) - 频率与概率的关系
- [描述统计](./descriptive-statistics.md) - 分布的数字特征
- [线性代数](../linear-algebra/matrix-operations.md) - 多元分布基础
- [微积分](../calculus/derivatives.md) - 连续分布的数学工具
