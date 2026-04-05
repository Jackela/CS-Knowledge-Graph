# 抽样方法 (Sampling Methods)

## 简介
抽样方法是从总体中选择子集以进行统计推断的技术。良好的抽样设计能够在控制成本的同时保证样本代表性，是A/B测试、调查研究和机器学习数据收集的基础，直接影响推断的有效性和结论的可靠性。

## 核心概念

### 基本抽样原理

**总体与样本：**
- **总体 (Population)**：研究对象的全体集合
- **样本 (Sample)**：从总体中抽取的子集
- **抽样框 (Sampling Frame)**：用于抽取样本的总体单位列表
- **样本量 (Sample Size)**：样本中的单位数量，记为 $n$

**抽样误差与非抽样误差：**
- **抽样误差**：由于只观察样本而非总体造成的变异，随样本量增加而减小
- **非抽样误差**：覆盖误差、无应答误差、测量误差等

**代表性原则：**
样本应能反映总体的关键特征，避免系统性偏差。

### 概率抽样方法

**简单随机抽样 (Simple Random Sampling)：**
每个样本单位有相同的被抽中概率，每次抽取相互独立。

$$P(\text{单位 } i \text{ 被选中}) = \frac{n}{N}$$

优点：无偏、方差易计算；缺点：可能需要完整的抽样框。

**分层抽样 (Stratified Sampling)：**
将总体分成互不重叠的层（strata），每层内独立抽样。

**比例分配：**
$$n_h = n \times \frac{N_h}{N}$$

**最优分配（Neyman分配）：**
$$n_h = n \times \frac{N_h S_h}{\sum_{k} N_k S_k}$$

其中 $S_h$ 为第 $h$ 层的标准差。适用于层间差异大、层内差异小的情况。

**整群抽样 (Cluster Sampling)：**
将总体分成若干群（cluster），随机抽取部分群，对选中群进行普查或二次抽样。

优点：实施成本低，适合地理分散的总体；缺点：群内相似导致效率降低。

设计效应 (DEFF)：
$$DEFF = \frac{\text{整群抽样方差}}{\text{简单随机抽样方差}}$$

**系统抽样 (Systematic Sampling)：**
按固定间隔 $k = N/n$ 抽取样本，随机选择起始点。

优点：操作简单，可能隐含分层效果；缺点：若总体有周期性模式，可能产生严重偏差。

**多阶段抽样 (Multistage Sampling)：**
分多个阶段逐步缩小抽样范围，如：省→市→区→个人。

大型调查常用，平衡成本与代表性。

### 非概率抽样方法

**方便抽样 (Convenience Sampling)：**
选择最容易获得的单位。成本低但代表性差。

**判断抽样 (Judgmental Sampling)：**
基于专家判断选择"典型"单位。依赖主观判断。

**雪球抽样 (Snowball Sampling)：**
通过已有样本推荐新样本。适合稀有群体研究。

**配额抽样 (Quota Sampling)：**
按预设比例在各类别中方便抽样。类似分层但非随机。

### 样本量确定

**估计均值的样本量：**
$$n = \left(\frac{z_{\alpha/2} \cdot \sigma}{E}\right)^2$$

其中 $E$ 为允许误差，$\sigma$ 为总体标准差。

**估计比例的样本量：**
$$n = \frac{z_{\alpha/2}^2 \cdot p(1-p)}{E^2}$$

保守估计取 $p = 0.5$。

**考虑有限总体修正：**
当抽样比 $n/N > 0.05$ 时：
$$n_{adj} = \frac{n}{1 + \frac{n-1}{N}}$$

**A/B测试样本量：**
$$n = \frac{2(z_{\alpha/2} + z_{\beta})^2 \sigma^2}{\delta^2}$$

其中 $\delta$ 为最小可检测差异，$\beta$ 为第二类错误概率。

### 重采样方法

**Bootstrap：**
从原始样本中有放回地重复抽样，用于：
- 估计标准误
- 构建置信区间
- 评估模型稳定性

**Jackknife：**
每次留出一个观测，用于偏差校正和方差估计。

**交叉验证：**
将数据分成K份，轮流作为验证集，评估模型泛化能力。

## 实现方式

```python
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split, StratifiedKFold

# 创建示例数据集
np.random.seed(42)
n_population = 10000

# 模拟一个总体：年龄、性别、收入
data = pd.DataFrame({
    'age': np.random.normal(35, 12, n_population).clip(18, 80).astype(int),
    'gender': np.random.choice(['M', 'F'], n_population, p=[0.48, 0.52]),
    'income': np.random.lognormal(10.5, 0.8, n_population),
    'city': np.random.choice(['A', 'B', 'C', 'D'], n_population, p=[0.4, 0.3, 0.2, 0.1])
})

# 添加分层变量
data['age_group'] = pd.cut(data['age'], bins=[0, 30, 50, 100], labels=['Young', 'Middle', 'Senior'])

print("Population characteristics:")
print(f"Size: {len(data)}")
print(f"Mean income: ${data['income'].mean():.2f}")
print(f"Gender distribution:\n{data['gender'].value_counts(normalize=True)}")
print(f"Age group distribution:\n{data['age_group'].value_counts(normalize=True)}")

# ========== 简单随机抽样 ==========

def simple_random_sampling(df, n):
    """简单随机抽样"""
    return df.sample(n=n, replace=False)

sample_srs = simple_random_sampling(data, n=500)
print(f"\n=== Simple Random Sampling (n=500) ===")
print(f"Sample mean income: ${sample_srs['income'].mean():.2f}")
print(f"Gender distribution:\n{sample_srs['gender'].value_counts(normalize=True)}")

# ========== 分层抽样 ==========

def stratified_sampling(df, strata_col, n_total, proportional=True):
    """分层抽样"""
    strata = df[strata_col].unique()
    samples = []
    
    for stratum in strata:
        stratum_data = df[df[strata_col] == stratum]
        
        if proportional:
            # 比例分配
            n_stratum = int(n_total * len(stratum_data) / len(df))
        else:
            # 等额分配
            n_stratum = n_total // len(strata)
        
        stratum_sample = stratum_data.sample(n=n_stratum, replace=False)
        samples.append(stratum_sample)
    
    return pd.concat(samples, ignore_index=True)

# 按性别分层
sample_strat = stratified_sampling(data, 'gender', n=500, proportional=True)
print(f"\n=== Stratified Sampling by Gender ===")
print(f"Sample mean income: ${sample_strat['income'].mean():.2f}")
print(f"Gender distribution:\n{sample_strat['gender'].value_counts(normalize=True)}")

# ========== 系统抽样 ==========

def systematic_sampling(df, n):
    """系统抽样"""
    k = len(df) // n
    start = np.random.randint(0, k)
    indices = range(start, len(df), k)
    return df.iloc[list(indices)[:n]]

sample_sys = systematic_sampling(data, n=500)
print(f"\n=== Systematic Sampling ===")
print(f"Sample mean income: ${sample_sys['income'].mean():.2f}")

# ========== 整群抽样 ==========

def cluster_sampling(df, cluster_col, n_clusters):
    """整群抽样"""
    clusters = df[cluster_col].unique()
    selected_clusters = np.random.choice(clusters, size=n_clusters, replace=False)
    return df[df[cluster_col].isin(selected_clusters)]

sample_cluster = cluster_sampling(data, 'city', n_clusters=2)
print(f"\n=== Cluster Sampling (2 cities) ===")
print(f"Sample size: {len(sample_cluster)}")
print(f"Sample mean income: ${sample_cluster['income'].mean():.2f}")
print(f"Selected cities: {sample_cluster['city'].unique()}")

# ========== 样本量计算 ==========

def calculate_sample_size_mean(sigma, margin_error, confidence=0.95):
    """估计均值所需样本量"""
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    n = (z * sigma / margin_error) ** 2
    return int(np.ceil(n))

def calculate_sample_size_proportion(p=0.5, margin_error=0.05, confidence=0.95):
    """估计比例所需样本量"""
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    n = (z ** 2 * p * (1 - p)) / (margin_error ** 2)
    return int(np.ceil(n))

def calculate_ab_test_sample_size(p1, p2, alpha=0.05, beta=0.2):
    """A/B测试样本量（每组）"""
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(1 - beta)
    
    p_avg = (p1 + p2) / 2
    delta = abs(p2 - p1)
    
    n = (2 * z_alpha * np.sqrt(p_avg * (1 - p_avg)) + 
         z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / delta ** 2
    return int(np.ceil(n))

# 示例计算
sigma_income = data['income'].std()
n_mean = calculate_sample_size_mean(sigma_income, margin_error=100, confidence=0.95)
print(f"\n=== Sample Size Calculations ===")
print(f"For mean income (margin=100, 95% CI): n = {n_mean}")

n_prop = calculate_sample_size_proportion(p=0.5, margin_error=0.05)
print(f"For proportion (margin=0.05, 95% CI): n = {n_prop}")

n_ab = calculate_ab_test_sample_size(p1=0.10, p2=0.12, alpha=0.05, beta=0.2)
print(f"A/B test (10% vs 12%, 80% power): n = {n_ab} per group")

# ========== Bootstrap ==========

def bootstrap_statistic(data, statistic_func, n_bootstrap=1000, ci=0.95):
    """Bootstrap估计统计量的置信区间"""
    n = len(data)
    bootstrap_stats = []
    
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_stats.append(statistic_func(sample))
    
    alpha = 1 - ci
    lower = np.percentile(bootstrap_stats, alpha/2 * 100)
    upper = np.percentile(bootstrap_stats, (1 - alpha/2) * 100)
    
    return {
        'estimate': statistic_func(data),
        'bootstrap_mean': np.mean(bootstrap_stats),
        'bootstrap_std': np.std(bootstrap_stats),
        'ci_lower': lower,
        'ci_upper': upper
    }

# 对样本进行Bootstrap
income_sample = sample_srs['income'].values
bootstrap_result = bootstrap_statistic(income_sample, np.mean, n_bootstrap=5000)
print(f"\n=== Bootstrap (n={len(income_sample)}) ===")
print(f"Sample mean: ${bootstrap_result['estimate']:.2f}")
print(f"Bootstrap SE: ${bootstrap_result['bootstrap_std']:.2f}")
print(f"95% CI: (${bootstrap_result['ci_lower']:.2f}, ${bootstrap_result['ci_upper']:.2f})")

# ========== 分层估计与标准误 ==========

def stratified_mean_estimate(sample, strata_col, value_col, population_counts):
    """分层抽样的总体均值估计"""
    strata_means = sample.groupby(strata_col)[value_col].mean()
    strata_vars = sample.groupby(strata_col)[value_col].var()
    strata_ns = sample.groupby(strata_col)[value_col].count()
    
    total_pop = sum(population_counts.values())
    weights = {s: population_counts[s] / total_pop for s in population_counts}
    
    # 加权均值
    mean_estimate = sum(weights[s] * strata_means[s] for s in weights)
    
    # 标准误
    variance_estimate = sum(
        weights[s]**2 * strata_vars[s] / strata_ns[s] * 
        (population_counts[s] - strata_ns[s]) / population_counts[s]
        for s in weights
    )
    
    return mean_estimate, np.sqrt(variance_estimate)

# 计算总体各层数量
pop_gender_counts = data['gender'].value_counts().to_dict()
strat_mean, strat_se = stratified_mean_estimate(
    sample_strat, 'gender', 'income', pop_gender_counts
)
print(f"\n=== Stratified Estimation ===")
print(f"Stratified mean estimate: ${strat_mean:.2f}")
print(f"Standard error: ${strat_se:.2f}")

# 与简单随机抽样的标准误比较
srs_se = sample_srs['income'].sem()
print(f"SRS standard error: ${srs_se:.2f}")
print(f"Design effect: {(strat_se/srs_se)**2:.3f}")
```

## 应用场景

### A/B测试
- **随机化**：确保实验组和对照组可比
- **样本量规划**：基于MDE和功效确定实验规模
- **分层随机化**：按用户特征分层，减少方差
- **多变量测试**：拉丁方设计、正交数组

### 机器学习
- **训练/验证/测试划分**：分层抽样保持类别比例
- **交叉验证**：K折分层交叉验证
- **Bootstrap聚合(Bagging)**：集成学习方法
- **不平衡数据处理**：过采样、欠采样策略

### 调查研究
- **市场调研**：配额抽样快速获取样本
- **民意调查**：分层抽样确保人口代表性
- **质量控制**：验收抽样方案设计
- **医学研究**：整群抽样在 multicenter trial 中的应用

### 大数据抽样
- **近似查询**：从大表抽样加速分析
- **流数据抽样**：水库抽样处理未知总量
- **分层存储**：热数据/冷数据分层

## 面试要点

1. **Q: 分层抽样和整群抽样有什么区别？什么时候用哪个？**  
   A: 分层抽样：层间差异大、层内差异小，每层都抽；目的是提高估计精度。整群抽样：群间差异小、群内差异大，抽部分群；目的是降低实施成本。选择依据：如果群内相似度高（如学校内的学生），用整群抽样经济但效率低；如果层间差异大（如不同年龄组），用分层抽样可提高精度。

2. **Q: 为什么A/B测试需要随机化？分层随机化有什么好处？**  
   A: 随机化确保实验组和对照组在期望意义下可比，消除选择偏差和混杂因素。分层随机化的好处：(1) 确保各层在组间均衡分布；(2) 减少抽样误差（方差降低）；(3) 提高统计功效；(4) 允许层特定的效应估计。例如按用户价值分层，确保高低价值用户在实验组对照组均衡。

3. **Q: Bootstrap的原理是什么？为什么它有效？**  
   A: Bootstrap通过有放回重采样从原始样本生成大量"伪样本"，用这些伪样本的统计量分布近似真实抽样分布。它有效的原因：经验分布函数是总体分布的相合估计；大数定律保证bootstrap统计量收敛。适用于：标准误估计、置信区间构建、模型稳定性评估。不适用于：极端分位数、依赖结构复杂的数据。

4. **Q: 样本量计算的假设不满足时怎么办？**  
   A: 实际应用中：(1) 总体方差未知时，用试点研究或历史数据估计；(2) 效应大小不确定时，计算不同场景下的样本量，或进行中期分析；(3) 多终点指标时，考虑Bonferroni校正或主要终点；(4) 存在缺失数据时，适当扩大样本量；(5) 复杂的试验设计（如整群）考虑设计效应。建议进行敏感性分析。

## 相关概念

### 数据结构
- [数组](../../computer-science/data-structures/array.md) - 数据集存储
- [哈希表](../../computer-science/data-structures/hash-table.md) - 分层索引

### 算法
- [随机数生成](../../computer-science/algorithms/random.md) - 抽样基础
- [排序算法](../../computer-science/algorithms/sorting.md) - 系统抽样

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 重采样复杂度

### 系统实现
- [A/B测试](../../ai-data-systems/ab-testing.md) - 随机化实验
- [数据仓库](../../ai-data-systems/data-warehouse.md) - 数据采样查询

### 数学基础
- [概率分布](./probability-distributions.md) - 抽样分布理论
- [中心极限定理](./central-limit-theorem.md) - 大样本近似
- [置信区间](./confidence-intervals.md) - 样本量计算基础
- [描述统计](./descriptive-statistics.md) - 估计量性质
- [假设检验](./hypothesis-testing.md) - 功效分析
- [线性代数](../linear-algebra/matrix-operations.md) - 协方差矩阵
- [微积分](../calculus/derivatives.md) - 优化基础
