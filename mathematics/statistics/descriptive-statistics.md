# 描述统计 (Descriptive Statistics)

## 简介
描述统计是对数据进行汇总和可视化的统计方法，通过数值指标和图形展示数据的集中趋势、离散程度和分布形状。它是数据分析的第一步，为后续的推断统计和机器学习建模提供基础洞察。

## 核心概念

### 集中趋势度量

**均值 (Mean)：**
算术平均值，最常用的集中趋势度量：
$$\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i$$

加权均值：
$$\bar{x}_w = \frac{\sum_{i=1}^{n} w_i x_i}{\sum_{i=1}^{n} w_i}$$

**中位数 (Median)：**
将数据排序后位于中间位置的值：
$$\text{Median} = \begin{cases} x_{(n+1)/2} & n \text{为奇数} \\ \frac{x_{n/2} + x_{n/2+1}}{2} & n \text{为偶数} \end{cases}$$

**众数 (Mode)：**
数据中出现频率最高的值。适用于分类数据和数值数据。

**三者的比较：**
| 特性 | 均值 | 中位数 | 众数 |
|------|------|--------|------|
| 敏感性 | 受异常值影响大 | 稳健 | 可能不唯一 |
| 数据类型 | 数值型 | 数值型/序数型 | 任意类型 |
| 数学性质 | 良好（可导） | 较差 | 较差 |
| 适用场景 | 对称分布 | 偏态分布 | 分类数据 |

### 离散程度度量

**方差 (Variance)：**
$$s^2 = \frac{1}{n-1} \sum_{i=1}^{n} (x_i - \bar{x})^2$$

使用 $n-1$（而非 $n$）作为分母是为了得到总体方差的无偏估计。

**标准差 (Standard Deviation)：**
$$s = \sqrt{s^2}$$

与原始数据同单位，更直观。

**极差 (Range)：**
$$R = x_{\max} - x_{\min}$$

对异常值敏感，仅使用两个极端值。

**四分位距 (IQR)：**
$$IQR = Q_3 - Q_1$$

其中 $Q_1$ 为第25百分位数，$Q_3$ 为第75百分位数。对异常值稳健。

**变异系数 (CV)：**
$$CV = \frac{s}{\bar{x}} \times 100\%$$

用于比较不同量纲或不同均值的数据集的离散程度。

### 分位数

**百分位数 (Percentiles)：**
第 $p$ 百分位数表示有 $p\%$ 的数据小于等于该值。

**四分位数：**
- $Q_1$（第一四分位数）：第25百分位数
- $Q_2$（第二四分位数）：中位数，第50百分位数
- $Q_3$（第三四分位数）：第75百分位数

**五数概括法：**
最小值、$Q_1$、中位数、$Q_3$、最大值

### 分布形状度量

**偏度 (Skewness)：**
衡量分布的不对称性：
$$g_1 = \frac{1}{n} \sum_{i=1}^{n} \left(\frac{x_i - \bar{x}}{s}\right)^3$$

- $g_1 > 0$：右偏（正偏），长尾在右
- $g_1 < 0$：左偏（负偏），长尾在左
- $g_1 = 0$：对称分布

**峰度 (Kurtosis)：**
衡量分布的尖锐程度（相对于正态分布）：
$$g_2 = \frac{1}{n} \sum_{i=1}^{n} \left(\frac{x_i - \bar{x}}{s}\right)^4 - 3$$

- $g_2 > 0$：尖峰（leptokurtic）
- $g_2 < 0$：平峰（platykurtic）
- $g_2 = 0$：常峰（mesokurtic，正态分布）

### 异常值检测

**IQR方法：**
$$\text{异常值} < Q_1 - 1.5 \times IQR \quad \text{或} \quad \text{异常值} > Q_3 + 1.5 \times IQR$$

**Z-score方法：**
$$Z = \frac{x - \bar{x}}{s}, \quad |Z| > 3 \text{ 视为异常值}$$

**修正Z-score（使用中位数）：**
$$MAD = \text{median}(|x_i - \text{median}(x)|)$$

## 实现方式

```python
import numpy as np
from scipy import stats
import pandas as pd

# 生成示例数据
np.random.seed(42)
data = np.random.normal(100, 15, 1000)
# 添加一些异常值
data = np.concatenate([data, [150, 155, 40, 45]])

# ========== 集中趋势 ==========

# 均值
mean = np.mean(data)
print(f"Mean: {mean:.3f}")

# 加权均值
weights = np.random.uniform(0.5, 1.5, len(data))
weighted_mean = np.average(data, weights=weights)
print(f"Weighted Mean: {weighted_mean:.3f}")

# 中位数
median = np.median(data)
print(f"Median: {median:.3f}")

# 众数
mode_result = stats.mode(data, keepdims=True)
print(f"Mode: {mode_result.mode[0]:.3f} (count: {mode_result.count[0]})")

# 截尾均值（去除极端值）
trimmed_mean = stats.trim_mean(data, 0.05)  # 去除两端各5%
print(f"Trimmed Mean (5%): {trimmed_mean:.3f}")

# ========== 离散程度 ==========

# 方差（样本方差，ddof=1）
variance = np.var(data, ddof=1)
print(f"\nVariance: {variance:.3f}")

# 标准差
std_dev = np.std(data, ddof=1)
print(f"Standard Deviation: {std_dev:.3f}")

# 极差
range_val = np.max(data) - np.min(data)
print(f"Range: {range_val:.3f}")

# 四分位距
q1, q3 = np.percentile(data, [25, 75])
iqr = q3 - q1
print(f"IQR: {iqr:.3f}")

# 变异系数
cv = (std_dev / mean) * 100
print(f"Coefficient of Variation: {cv:.2f}%")

# 平均绝对偏差
mad = np.mean(np.abs(data - np.mean(data)))
print(f"Mean Absolute Deviation: {mad:.3f}")

# 中位数绝对偏差（MAD）
median_absolute_deviation = np.median(np.abs(data - np.median(data)))
print(f"Median Absolute Deviation: {median_absolute_deviation:.3f}")

# ========== 分位数 ==========

# 百分位数
percentiles = [5, 10, 25, 50, 75, 90, 95]
quantiles = np.percentile(data, percentiles)
print(f"\nPercentiles:")
for p, q in zip(percentiles, quantiles):
    print(f"  {p}th: {q:.3f}")

# 五数概括
five_number = [np.min(data), q1, median, q3, np.max(data)]
print(f"\nFive-number summary: {five_number}")

# ========== 分布形状 ==========

# 偏度
skewness = stats.skew(data)
print(f"\nSkewness: {skewness:.3f}")
if skewness > 0.5:
    print("  Distribution is right-skewed")
elif skewness < -0.5:
    print("  Distribution is left-skewed")
else:
    print("  Distribution is approximately symmetric")

# 峰度（Fisher定义，正态分布为0）
kurtosis = stats.kurtosis(data, fisher=True)
print(f"Kurtosis: {kurtosis:.3f}")
if kurtosis > 0:
    print("  Distribution is leptokurtic (heavy-tailed)")
elif kurtosis < 0:
    print("  Distribution is platykurtic (light-tailed)")

# ========== 异常值检测 ==========

# IQR方法
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
outliers_iqr = data[(data < lower_bound) | (data > upper_bound)]
print(f"\nOutliers (IQR method): {len(outliers_iqr)} values")

# Z-score方法
z_scores = np.abs(stats.zscore(data))
outliers_zscore = data[z_scores > 3]
print(f"Outliers (Z-score method): {len(outliers_zscore)} values")

# 修正Z-score（使用MAD）
modified_z_scores = 0.6745 * (data - np.median(data)) / median_absolute_deviation
outliers_modified = data[np.abs(modified_z_scores) > 3.5]
print(f"Outliers (Modified Z-score): {len(outliers_modified)} values")

# ========== pandas描述统计 ==========

df = pd.DataFrame({'value': data})
describe_result = df['value'].describe()
print(f"\nPandas describe():")
print(describe_result)

# 自定义更全面的描述统计
def comprehensive_describe(data):
    """全面的描述统计"""
    stats_dict = {
        'count': len(data),
        'mean': np.mean(data),
        'std': np.std(data, ddof=1),
        'min': np.min(data),
        '25%': np.percentile(data, 25),
        '50%': np.median(data),
        '75%': np.percentile(data, 75),
        'max': np.max(data),
        'skewness': stats.skew(data),
        'kurtosis': stats.kurtosis(data),
        'iqr': np.percentile(data, 75) - np.percentile(data, 25),
        'cv': (np.std(data, ddof=1) / np.mean(data)) * 100,
        'mad': np.median(np.abs(data - np.median(data)))
    }
    return pd.Series(stats_dict)

print(f"\nComprehensive description:")
print(comprehensive_describe(data))
```

## 应用场景

### 数据探索与清洗
- **快速数据概览**：使用describe()了解数据基本特征
- **异常值识别**：结合业务知识处理异常数据
- **数据分布判断**：决定是否需要数据变换（如对数变换处理右偏数据）
- **缺失值处理**：根据分布特征选择合适的填充策略

### 特征工程
- **特征标准化**：基于均值和标准差的标准化（Z-score）
- **异常特征标记**：使用统计指标创建异常指示特征
- **特征选择**：基于变异系数筛选低方差特征
- **分箱策略**：基于分位数进行等频分箱

### 业务指标监控
- **KPI追踪**：均值、中位数监控核心指标变化
- **波动性分析**：标准差、CV衡量业务稳定性
- **分位点监控**：关注长尾性能（如P95、P99响应时间）
- **异常告警**：基于统计阈值的自动告警

### 报告与可视化
- **箱线图**：五数概括的可视化
- **直方图**：展示数据分布形状
- **摘要统计表**：业务报告中的关键数字

## 面试要点

1. **Q: 均值和中位数有什么区别？什么时候用中位数更好？**  
   A: 均值是所有数据的平均值，对异常值敏感；中位数是中间位置的值，对异常值稳健。当数据存在极端值或严重偏态时，中位数能更好地代表"典型"值。例如收入数据通常右偏，中位数收入比均值更能反映普通人的收入水平。

2. **Q: 为什么要用n-1计算样本方差？（贝塞尔校正）**  
   A: 使用n作为分母会得到有偏估计（低估总体方差），因为样本均值本身就是从数据中估计的，比总体均值更接近数据点。除以n-1可以校正这个偏差，得到总体方差的无偏估计。从自由度角度理解：估计均值消耗了1个自由度。

3. **Q: 偏度和峰度如何影响数据分析？**  
   A: 偏度影响集中趋势的选择：右偏数据宜用中位数，对称数据可用均值。峰度影响极端值概率：尖峰分布（高 kurtosis）更可能有异常值。许多统计方法（如t检验、回归）假设数据近似正态，此时需要关注偏度和峰度。偏度>2或峰度>7通常认为严重偏离正态。

4. **Q: 如何选择异常值检测方法？**  
   A: (1) Z-score适用于近似正态分布，但对异常值敏感（均值和标准差会被拉偏）；(2) IQR方法对异常值稳健，适用于各种分布；(3) 修正Z-score结合了两者的优点；(4) 业务规则法基于领域知识设定阈值。实际应用中应结合可视化（箱线图）和业务理解综合判断，避免盲目删除"异常值"。

## 相关概念

### 数据结构
- [数组](../../computer-science/data-structures/array.md) - 数据存储基础
- [哈希表](../../computer-science/data-structures/hash-table.md) - 频数统计

### 算法
- [排序算法](../../computer-science/algorithms/sorting.md) - 分位数计算基础
- [采样算法](../../computer-science/algorithms/sampling.md) - 数据收集

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - 统计计算复杂度

### 系统实现
- [监控系统](../../cloud-devops/monitoring.md) - 指标统计
- [日志系统](../../computer-science/systems/logging.md) - 数据分析

### 数学基础
- [概率分布](./probability-distributions.md) - 描述统计的理论基础
- [假设检验](./hypothesis-testing.md) - 基于描述统计的推断
- [置信区间](./confidence-intervals.md) - 区间估计
- [抽样方法](./sampling-methods.md) - 样本与总体
- [线性代数](../linear-algebra/matrix-operations.md) - 多元统计
- [微积分](../calculus/derivatives.md) - 矩的概念
