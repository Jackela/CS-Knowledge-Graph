# 假设检验 (Hypothesis Testing)

## 简介
假设检验是统计学中用于判断样本数据是否支持某个统计假设的推断方法。通过计算检验统计量和p值，我们可以在给定的显著性水平下决定是否拒绝原假设，是A/B测试、质量控制和科学实验的核心工具。

## 核心概念

### 基本概念

**原假设 ($H_0$) 与备择假设 ($H_1$)：**
- $H_0$：默认假设，通常表示"无效果"或"无差异"
- $H_1$：研究想要证明的假设

**两类错误：**
- **第一类错误 (Type I Error)**：$H_0$ 为真时拒绝 $H_0$，概率为 $\alpha$（显著性水平）
- **第二类错误 (Type II Error)**：$H_0$ 为假时接受 $H_0$，概率为 $\beta$
- **检验功效 (Power)**：$1 - \beta$，正确拒绝 $H_0$ 的概率

**p值：**
在原假设为真的假设下，观察到当前样本或更极端结果的概率：
$$p = P(\text{观察值} \geq \text{实际值} | H_0 \text{为真})$$

当 $p < \alpha$ 时，拒绝原假设。

### t检验 (t-Test)

用于检验均值差异，适用于小样本或总体方差未知的情况。

**单样本t检验：**
检验样本均值是否等于某个特定值：
$$t = \frac{\bar{x} - \mu_0}{s / \sqrt{n}}$$
自由度 $df = n - 1$

**独立样本t检验：**
检验两组独立样本的均值是否相等：
$$t = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{s_p^2(\frac{1}{n_1} + \frac{1}{n_2})}}$$
其中 $s_p^2 = \frac{(n_1-1)s_1^2 + (n_2-1)s_2^2}{n_1 + n_2 - 2}$ 为合并方差

**配对样本t检验：**
检验配对样本差值的均值是否为零：
$$t = \frac{\bar{d}}{s_d / \sqrt{n}}$$

### 卡方检验 (Chi-Square Test)

用于检验分类变量的分布或独立性。

**卡方拟合优度检验：**
检验观测频数是否符合期望分布：
$$\chi^2 = \sum_{i=1}^{k} \frac{(O_i - E_i)^2}{E_i}$$
自由度 $df = k - 1 - m$（$m$ 为估计参数个数）

**卡方独立性检验：**
检验两个分类变量是否独立：
$$\chi^2 = \sum_{i=1}^{r} \sum_{j=1}^{c} \frac{(O_{ij} - E_{ij})^2}{E_{ij}}$$
其中 $E_{ij} = \frac{(\text{行总计}) \times (\text{列总计})}{\text{总样本数}}$
自由度 $df = (r-1)(c-1)$

### 其他常用检验

**Z检验：**
大样本或总体方差已知时的均值检验：
$$z = \frac{\bar{x} - \mu_0}{\sigma / \sqrt{n}}$$

**F检验：**
检验两个正态总体方差是否相等：
$$F = \frac{s_1^2}{s_2^2}$$

**Mann-Whitney U检验：**
非参数检验，比较两组独立样本的分布（不假设正态性）。

**Kolmogorov-Smirnov检验：**
检验样本是否来自特定分布，或两个样本是否来自同一分布。

## 实现方式

```python
import numpy as np
from scipy import stats

# ========== t检验 ==========

# 单样本t检验
sample = np.random.normal(5.2, 1.5, 30)  # 实际均值为5.2
t_stat, p_value = stats.ttest_1samp(sample, popmean=5.0)
print(f"One-sample t-test: t={t_stat:.3f}, p={p_value:.3f}")

# 独立样本t检验
group1 = np.random.normal(100, 15, 50)
group2 = np.random.normal(105, 15, 50)
t_stat, p_value = stats.ttest_ind(group1, group2)
print(f"Independent t-test: t={t_stat:.3f}, p={p_value:.3f}")

#  Welch's t-test（方差不齐时使用）
t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)
print(f"Welch's t-test: t={t_stat:.3f}, p={p_value:.3f}")

# 配对样本t检验
before = np.random.normal(100, 10, 30)
after = before + np.random.normal(5, 5, 30)  # 平均增加5
t_stat, p_value = stats.ttest_rel(before, after)
print(f"Paired t-test: t={t_stat:.3f}, p={p_value:.3f}")

# ========== 卡方检验 ==========

# 卡方拟合优度检验
observed = [45, 35, 20]  # 观测频数
expected = [33.3, 33.3, 33.3]  # 期望频数（均匀分布）
chi2_stat, p_value = stats.chisquare(observed, expected)
print(f"Chi-square goodness-of-fit: χ²={chi2_stat:.3f}, p={p_value:.3f}")

# 卡方独立性检验（列联表）
# 2x2列联表：[[男-吸烟, 男-不吸烟], [女-吸烟, 女-不吸烟]]
contingency_table = np.array([[30, 70], [20, 80]])
chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)
print(f"Chi-square independence: χ²={chi2_stat:.3f}, p={p_value:.3f}, df={dof}")
print(f"Expected frequencies:\n{expected}")

# ========== 其他检验 ==========

# 单因素方差分析 (ANOVA)
group_a = np.random.normal(100, 10, 30)
group_b = np.random.normal(105, 10, 30)
group_c = np.random.normal(110, 10, 30)
f_stat, p_value = stats.f_oneway(group_a, group_b, group_c)
print(f"One-way ANOVA: F={f_stat:.3f}, p={p_value:.3f}")

# Shapiro-Wilk正态性检验
sample = np.random.normal(0, 1, 100)
w_stat, p_value = stats.shapiro(sample)
print(f"Shapiro-Wilk test: W={w_stat:.3f}, p={p_value:.3f}")

# Mann-Whitney U检验（非参数）
group1 = np.random.exponential(2, 30)
group2 = np.random.exponential(2.5, 30)
u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
print(f"Mann-Whitney U test: U={u_stat:.3f}, p={p_value:.3f}")

# Kolmogorov-Smirnov检验
sample = np.random.normal(0, 1, 100)
ks_stat, p_value = stats.kstest(sample, 'norm', args=(0, 1))
print(f"KS test: statistic={ks_stat:.3f}, p={p_value:.3f}")

# ========== 功效分析 ==========
from statsmodels.stats.power import TTestIndPower

# 计算所需样本量
power_analysis = TTestIndPower()
sample_size = power_analysis.solve_power(
    effect_size=0.5,  # 中等效应量
    power=0.8,        # 期望功效
    alpha=0.05        # 显著性水平
)
print(f"Required sample size per group: {sample_size:.0f}")
```

## 应用场景

### A/B测试
- **转化率比较**：使用卡方检验或Z检验比较两组的转化率
- **均值比较**：使用t检验比较两组的平均收入、使用时长等指标
- **样本量计算**：基于期望效应量和功效确定实验所需样本量

### 机器学习
- **特征选择**：使用卡方检验选择与目标变量相关的分类特征
- **模型比较**：使用配对t检验比较两个模型在交叉验证上的表现
- **分布检验**：验证数据是否满足算法的分布假设（如正态性）

### 数据质量控制
- **异常检测**：识别偏离预期分布的数据点
- **数据漂移检测**：监测生产数据与训练数据的分布差异
- **假设验证**：验证业务假设，支持数据驱动决策

### 产品分析
- **用户行为分析**：检验不同用户群体的行为差异
- **功能效果评估**：验证新功能是否显著改善用户体验
- **留存率分析**：比较不同策略对用户留存的影响

## 面试要点

1. **Q: p值的真正含义是什么？如何正确理解"p < 0.05"？**  
   A: p值是在原假设为真的条件下，观察到当前样本或更极端结果的概率，而非原假设为假的概率。p < 0.05表示如果原假设为真，只有不到5%的概率会观察到这样的结果，因此我们有理由拒绝原假设。注意：p值不是效应大小，也不能说明实际重要性。

2. **Q: 什么时候使用t检验，什么时候使用Z检验？**  
   A: t检验适用于小样本（n < 30）或总体方差未知的情况；Z检验适用于大样本（n ≥ 30）且总体方差已知的情况。在实际应用中，由于总体方差通常未知，t检验更为常用。当样本量较大时，t分布趋近正态分布，两者结果相近。

3. **Q: 第一类错误和第二类错误如何权衡？如何选择显著性水平？**  
   A: 降低$\alpha$会减少第一类错误但增加第二类错误。通常选择$\alpha$=0.05作为平衡。在要求严格的场景（如药物安全性测试），可能选择更小的$\alpha$（如0.01）；在探索性分析中，可能放宽到0.1。可通过增加样本量同时降低两类错误。

4. **Q: 卡方检验的前提条件是什么？如果条件不满足怎么办？**  
   A: 卡方检验要求：(1) 观测值独立；(2) 期望频数至少为5（或至少80%的格子期望频数≥5）。如果期望频数过小，可使用：(1) Fisher精确检验（2×2表）；(2) 合并类别；(3) 使用连续性校正；(4) 增加样本量。

## 相关概念

### 数据结构
- [数组](../../computer-science/data-structures/array.md) - 存储样本数据
- [哈希表](../../computer-science/data-structures/hash-table.md) - 频数统计

### 算法
- [采样算法](../../computer-science/algorithms/sampling.md) - 实验设计中的抽样
- [排序算法](../../computer-science/algorithms/sorting.md) - 数据预处理

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 检验计算复杂度

### 系统实现
- [A/B测试](../../ai-data-systems/ab-testing.md) - 假设检验的工程应用
- [日志系统](../../computer-science/systems/logging.md) - 实验数据收集

### 数学基础
- [概率分布](./probability-distributions.md) - 检验统计量的分布
- [置信区间](./confidence-intervals.md) - 与假设检验的对偶关系
- [抽样方法](./sampling-methods.md) - 样本收集方法
- [描述统计](./descriptive-statistics.md) - 样本统计量计算
- [线性代数](../linear-algebra/matrix-operations.md) - 多元检验基础
- [微积分](../calculus/derivatives.md) - 似然函数优化
