# 置信区间 (Confidence Intervals)

## 简介
置信区间是基于样本统计量构造的区间估计，用于量化估计的不确定性。它给出了一个范围，使得在重复抽样下，该区间以特定概率（置信水平）包含真实的总体参数，是统计推断和不确定性量化的核心工具。

## 核心概念

### 基本定义

对于总体参数 $\theta$，置信水平为 $1-\alpha$ 的置信区间 $(L, U)$ 满足：
$$P(L \leq \theta \leq U) = 1 - \alpha$$

**常用置信水平：**
- 90%：$\alpha = 0.10$，$z_{0.05} = 1.645$
- 95%：$\alpha = 0.05$，$z_{0.025} = 1.96$
- 99%：$\alpha = 0.01$，$z_{0.005} = 2.576$

**正确理解：**
置信区间不是说"参数有95%的概率落在这个区间内"（参数是固定的），而是说"如果我们重复抽样100次，大约有95次构造的区间会包含真实参数"。

### 均值的置信区间

**大样本或方差已知的正态总体：**
$$\bar{x} \pm z_{\alpha/2} \cdot \frac{\sigma}{\sqrt{n}}$$

**小样本且方差未知：**
使用t分布：
$$\bar{x} \pm t_{\alpha/2, n-1} \cdot \frac{s}{\sqrt{n}}$$

**样本量对区间宽度的影响：**
区间宽度 $\propto \frac{1}{\sqrt{n}}$，要使区间宽度减半，需要4倍样本量。

### 比例的置信区间

**Wald区间（大样本近似）：**
$$\hat{p} \pm z_{\alpha/2} \sqrt{\frac{\hat{p}(1-\hat{p})}{n}}$$

**Wilson区间（更准确，尤其小样本）：**
$$
\frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}
$$

**Clopper-Pearson精确区间：**
基于二项分布的精确区间，保守但保证覆盖概率。

### 方差的置信区间

对于正态总体，使用卡方分布：
$$
\left(\frac{(n-1)s^2}{\chi^2_{\alpha/2, n-1}}, \frac{(n-1)s^2}{\chi^2_{1-\alpha/2, n-1}}\right)
$$

### 两样本差异的置信区间

**两独立样本均值差：**
$$(\bar{x}_1 - \bar{x}_2) \pm t_{\alpha/2, df} \cdot \sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}$$

**两比例差：**
$$(\hat{p}_1 - \hat{p}_2) \pm z_{\alpha/2} \sqrt{\frac{\hat{p}_1(1-\hat{p}_1)}{n_1} + \frac{\hat{p}_2(1-\hat{p}_2)}{n_2}}$$

### Bootstrap置信区间

当理论分布复杂或未知时，使用重采样方法：

1. **百分位法**：从Bootstrap分布的 $\alpha/2$ 和 $1-\alpha/2$ 分位数取区间
2. **基本Bootstrap法**：基于估计量的分布对称性
3. **BCa法**（偏差校正加速）：调整偏差和偏度

## 实现方式

```python
import numpy as np
from scipy import stats
from scipy.stats import bootstrap

# ========== 均值的置信区间 ==========

# 生成样本数据
np.random.seed(42)
sample = np.random.normal(100, 15, 50)
n = len(sample)
mean = np.mean(sample)
std_err = stats.sem(sample)  # 标准误 = s/√n

# 95%置信区间（t分布，小样本）
confidence_level = 0.95
alpha = 1 - confidence_level
degrees_freedom = n - 1
t_critical = stats.t.ppf(1 - alpha/2, degrees_freedom)

margin_of_error = t_critical * std_err
ci_lower = mean - margin_of_error
ci_upper = mean + margin_of_error

print(f"Sample mean: {mean:.3f}")
print(f"95% CI using t-distribution: ({ci_lower:.3f}, {ci_upper:.3f})")

# 使用scipy直接计算
ci = stats.t.interval(confidence_level, degrees_freedom, loc=mean, scale=std_err)
print(f"95% CI (scipy): ({ci[0]:.3f}, {ci[1]:.3f})")

# 大样本时使用正态分布（z检验）
z_critical = stats.norm.ppf(1 - alpha/2)
margin_of_error_z = z_critical * std_err
ci_z_lower = mean - margin_of_error_z
ci_z_upper = mean + margin_of_error_z
print(f"95% CI using z-distribution: ({ci_z_lower:.3f}, {ci_z_upper:.3f})")

# ========== 比例的置信区间 ==========

# 样本比例：1000次试验中成功350次
successes = 350
n_trials = 1000
p_hat = successes / n_trials

# Wald区间
se_prop = np.sqrt(p_hat * (1 - p_hat) / n_trials)
ci_prop_wald = (p_hat - z_critical * se_prop, p_hat + z_critical * se_prop)
print(f"\nSample proportion: {p_hat:.3f}")
print(f"95% CI (Wald): ({ci_prop_wald[0]:.3f}, {ci_prop_wald[1]:.3f})")

# Wilson区间
z_sq = z_critical ** 2
denominator = 1 + z_sq / n_trials
center = (p_hat + z_sq / (2 * n_trials)) / denominator
margin = z_critical * np.sqrt((p_hat * (1 - p_hat) + z_sq / (4 * n_trials)) / n_trials) / denominator
ci_wilson = (center - margin, center + margin)
print(f"95% CI (Wilson): ({ci_wilson[0]:.3f}, {ci_wilson[1]:.3f})")

# 使用statsmodels计算精确区间
from statsmodels.stats.proportion import proportion_confint
ci_exact = proportion_confint(successes, n_trials, alpha=0.05, method='wilson')
print(f"95% CI (statsmodels Wilson): ({ci_exact[0]:.3f}, {ci_exact[1]:.3f})")

# ========== 方差的置信区间 ==========

sample_var = np.var(sample, ddof=1)  # 样本方差
chi2_lower = stats.chi2.ppf(alpha/2, degrees_freedom)
chi2_upper = stats.chi2.ppf(1 - alpha/2, degrees_freedom)

ci_var_lower = (degrees_freedom * sample_var) / chi2_upper
ci_var_upper = (degrees_freedom * sample_var) / chi2_lower

print(f"\nSample variance: {sample_var:.3f}")
print(f"95% CI for variance: ({ci_var_lower:.3f}, {ci_var_upper:.3f})")

# 标准差的置信区间
ci_std_lower = np.sqrt(ci_var_lower)
ci_std_upper = np.sqrt(ci_var_upper)
print(f"95% CI for std dev: ({ci_std_lower:.3f}, {ci_std_upper:.3f})")

# ========== Bootstrap置信区间 ==========

# 使用scipy的bootstrap函数
data = (sample,)  # 注意：需要是元组
res = bootstrap(data, np.mean, n_resamples=10000, confidence_level=0.95)
print(f"\nBootstrap 95% CI: ({res.confidence_interval.low:.3f}, {res.confidence_interval.high:.3f})")

# 手动实现Bootstrap
def bootstrap_ci(data, func, n_bootstrap=10000, ci=0.95):
    """计算Bootstrap置信区间"""
    bootstrap_statistics = []
    n = len(data)
    
    for _ in range(n_bootstrap):
        # 有放回抽样
        sample_boot = np.random.choice(data, size=n, replace=True)
        bootstrap_statistics.append(func(sample_boot))
    
    alpha = 1 - ci
    lower = np.percentile(bootstrap_statistics, alpha/2 * 100)
    upper = np.percentile(bootstrap_statistics, (1 - alpha/2) * 100)
    return lower, upper

ci_boot = bootstrap_ci(sample, np.mean, n_bootstrap=10000)
print(f"Manual Bootstrap 95% CI: ({ci_boot[0]:.3f}, {ci_boot[1]:.3f})")

# ========== 两样本均值差的置信区间 ==========

sample1 = np.random.normal(100, 15, 50)
sample2 = np.random.normal(105, 15, 50)

diff_mean = np.mean(sample1) - np.mean(sample2)
se_diff = np.sqrt(np.var(sample1, ddof=1)/len(sample1) + np.var(sample2, ddof=1)/len(sample2))

# Welch's t区间（不假设等方差）
df_welch = (np.var(sample1, ddof=1)/len(sample1) + np.var(sample2, ddof=1)/len(sample2))**2 / \
           ((np.var(sample1, ddof=1)/len(sample1))**2/(len(sample1)-1) + 
            (np.var(sample2, ddof=1)/len(sample2))**2/(len(sample2)-1))
t_critical_welch = stats.t.ppf(1 - alpha/2, df_welch)

margin_diff = t_critical_welch * se_diff
ci_diff = (diff_mean - margin_diff, diff_mean + margin_diff)

print(f"\nDifference in means: {diff_mean:.3f}")
print(f"95% CI for difference: ({ci_diff[0]:.3f}, {ci_diff[1]:.3f})")
```

## 应用场景

### A/B测试
- **转化率估计**：报告"转化率提升20%（95%CI: 15%-25%）"比单纯说"提升20%"更有信息量
- **样本量规划**：根据期望的置信区间宽度确定实验样本量
- **实验停止准则**：当置信区间不包含零时，可认为有显著差异

### 机器学习
- **模型性能评估**：报告交叉验证得分的置信区间，如"准确率85% ± 3%"
- **超参数选择**：比较不同超参数下的性能置信区间
- **不确定性量化**：预测区间（Prediction Interval）与置信区间的区别应用

### 产品指标监控
- **KPI估计**：日活、留存率等指标的区间估计
- **趋势判断**：通过置信区间判断指标变化是信号还是噪声
- **目标设定**：基于历史数据的置信区间设定合理目标

### 业务决策
- **风险评估**：项目ROI的置信区间评估
- **容量规划**：基于置信区间预留安全余量
- **效果评估**：营销活动效果的不确定性量化

## 面试要点

1. **Q: 置信区间和置信水平有什么区别？如何正确解释95%置信区间？**  
   A: 置信水平（如95%）是长期频率的概念，表示重复抽样时区间包含真值的比例。置信区间是具体计算出的数值范围。正确解释："如果我们重复这个实验100次，大约有95次计算出的区间会包含真实的总体均值。"错误解释："真实均值有95%的概率落在这个区间内"（真值是固定的，不是随机的）。

2. **Q: 影响置信区间宽度的因素有哪些？如何缩小区间宽度？**  
   A: 三个主要因素：(1) 置信水平——提高置信水平会加宽区间；(2) 样本量——区间宽度与$\sqrt{n}$成反比，4倍样本量才能减半宽度；(3) 数据变异性——标准差越大，区间越宽。缩小区间的方法：增加样本量是最直接的，但需要权衡成本；降低置信水平（接受更大错误风险）；改进测量方法减少变异。

3. **Q: Bootstrap置信区间相比传统方法有什么优势？**  
   A: Bootstrap不需要知道总体分布形式，适用于：(1) 复杂统计量（如中位数、相关系数）；(2) 小样本且分布明显非正态；(3) 没有解析解的情况。缺点是计算量大，结果有随机性（可通过增加重采样次数减少）。百分位Bootstrap简单但可能有偏差，BCa方法更准确。

4. **Q: 置信区间和假设检验有什么关系？**  
   A: 两者是同一枚硬币的两面，存在对偶关系。对于双侧检验，如果$H_0: \theta = \theta_0$的p值$> \alpha$，则$\theta_0$落在$1-\alpha$置信区间内；反之亦然。置信区间提供更多信息（所有可接受的参数值范围），而假设检验只给出二元决策。实践中推荐报告置信区间。

## 相关概念

### 数据结构
- [数组](../../computer-science/data-structures/array.md) - 样本数据存储
- [哈希表](../../computer-science/data-structures/hash-table.md) - 频数统计

### 算法
- [采样算法](../../computer-science/algorithms/sampling.md) - 数据收集方法
- [排序算法](../../computer-science/algorithms/sorting.md) - 分位数计算

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - Bootstrap计算复杂度

### 系统实现
- [A/B测试](../../ai-data-systems/ab-testing.md) - 置信区间的工程应用
- [监控系统](../../cloud-devops/monitoring.md) - 指标区间估计

### 数学基础
- [假设检验](./hypothesis-testing.md) - 区间估计与检验的对偶性
- [概率分布](./probability-distributions.md) - 区间的理论基础
- [抽样方法](./sampling-methods.md) - 样本收集与区间精度
- [描述统计](./descriptive-statistics.md) - 统计量计算
- [中心极限定理](./central-limit-theorem.md) - 大样本区间的理论依据
- [线性代数](../linear-algebra/matrix-operations.md) - 多元置信区域
- [微积分](../calculus/derivatives.md) - Delta方法近似
