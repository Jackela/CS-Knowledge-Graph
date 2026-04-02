# 贝叶斯统计 (Bayesian Statistics)

## 简介
贝叶斯统计是基于贝叶斯定理的统计推断框架，将概率解释为信念程度的度量。与频率学派不同，贝叶斯方法允许将先验知识与新证据结合，通过后验分布进行推断，在机器学习、A/B测试和不确定性量化中具有广泛应用。

## 核心概念

### 贝叶斯定理

贝叶斯定理描述了在观察到新证据后如何更新信念：

$$P(\theta | D) = \frac{P(D | \theta) \cdot P(\theta)}{P(D)}$$

其中：
- $P(\theta)$：先验概率（Prior）——观察数据前对参数的信念
- $P(D | \theta)$：似然函数（Likelihood）——给定参数下观察到数据的概率
- $P(D)$：证据（Evidence）——数据的边缘概率
- $P(\theta | D)$：后验概率（Posterior）——观察数据后对参数的更新信念

**比例形式（更常用）：**
$$P(\theta | D) \propto P(D | \theta) \cdot P(\theta)$$

### 先验分布

**无信息先验（Non-informative Prior）：**
- 均匀先验：$P(\theta) = \text{constant}$
- Jeffreys先验：与参数化方式无关
- 尽量让数据"自己说话"

**共轭先验（Conjugate Prior）：**
当先验与似然共轭时，后验与先验属于同一分布族，计算简化：

| 似然 | 共轭先验 | 后验 |
|------|----------|------|
| 二项分布 | Beta分布 | Beta分布 |
| 正态分布（已知方差） | 正态分布 | 正态分布 |
| 泊松分布 | Gamma分布 | Gamma分布 |
| 正态分布（已知均值） | 逆Gamma分布 | 逆Gamma分布 |

**Beta分布：**
$$f(p; \alpha, \beta) = \frac{p^{\alpha-1}(1-p)^{\beta-1}}{B(\alpha, \beta)}$$

用于建模0到1之间的概率参数，是二项似然的共轭先验。

### 贝叶斯推断

**点估计：**
- 后验均值：$E[\theta | D]$
- 后验中位数
- 最大后验估计（MAP）：$\hat{\theta}_{MAP} = \arg\max_\theta P(\theta | D)$

**区间估计：**
可信区间（Credible Interval）：$P(a \leq \theta \leq b | D) = 1 - \alpha$

与置信区间的区别：可信区间是对参数的概率陈述，置信区间是对区间的频率陈述。

**预测分布：**
$$P(x_{new} | D) = \int P(x_{new} | \theta) P(\theta | D) d\theta$$

### 贝叶斯模型选择

**贝叶斯因子（Bayes Factor）：**
$$BF_{10} = \frac{P(D | M_1)}{P(D | M_0)} = \frac{\int P(D | \theta_1, M_1) P(\theta_1 | M_1) d\theta_1}{\int P(D | \theta_0, M_0) P(\theta_0 | M_0) d\theta_0}$$

| BF范围 | 证据强度 |
|--------|----------|
| 1-3 | 弱 |
| 3-10 | 中等 |
| 10-30 | 强 |
| >30 | 很强 |

**贝叶斯信息准则（BIC）：**
近似边际似然，平衡拟合优度与模型复杂度：
$$BIC = -2 \ln \hat{L} + k \ln n$$

### MCMC方法

当后验分布没有解析解时，使用马尔可夫链蒙特卡洛方法采样：

**Metropolis-Hastings算法：**
1. 从提议分布 $q(\theta^* | \theta^{(t)})$ 生成候选值
2. 计算接受概率 $\alpha = \min\left(1, \frac{P(\theta^* | D) q(\theta^{(t)} | \theta^*)}{P(\theta^{(t)} | D) q(\theta^* | \theta^{(t)})}\right)$
3. 以概率 $\alpha$ 接受 $\theta^*$

**Gibbs采样：**
轮流从条件分布采样：
$$\theta_i^{(t+1)} \sim P(\theta_i | \theta_{-i}^{(t)}, D)$$

## 实现方式

```python
import numpy as np
from scipy import stats
from scipy.special import beta as beta_func
import warnings
warnings.filterwarnings('ignore')

# ========== Beta-Binomial 共轭模型 ==========

# 先验：Beta(1, 1) = Uniform(0, 1)
alpha_prior = 1
beta_prior = 1

# 观测数据：n次试验中k次成功
n_trials = 100
k_successes = 35

# 后验：Beta(alpha + k, beta + n - k)
alpha_post = alpha_prior + k_successes
beta_post = beta_prior + n_trials - k_successes

print(f"Prior: Beta({alpha_prior}, {beta_prior})")
print(f"Posterior: Beta({alpha_post}, {beta_post})")

# 后验统计量
posterior_mean = alpha_post / (alpha_post + beta_post)
posterior_mode = (alpha_post - 1) / (alpha_post + beta_post - 2)
posterior_var = (alpha_post * beta_post) / ((alpha_post + beta_post)**2 * (alpha_post + beta_post + 1))

print(f"Posterior mean: {posterior_mean:.4f}")
print(f"Posterior mode (MAP): {posterior_mode:.4f}")
print(f"Posterior variance: {posterior_var:.6f}")

# 95% 可信区间
 credible_interval = stats.beta.ppf([0.025, 0.975], alpha_post, beta_post)
print(f"95% Credible Interval: ({credible_interval[0]:.4f}, {credible_interval[1]:.4f})")

# ========== 不同先验的比较 ==========

priors = [
    ("Uniform", 1, 1),
    ("Weakly Informative", 2, 2),
    ("Strong Prior (p=0.5)", 50, 50),
    ("Optimistic (p=0.4)", 4, 6)
]

print("\nEffect of different priors:")
for name, a, b in priors:
    a_post = a + k_successes
    b_post = b + n_trials - k_successes
    mean_post = a_post / (a_post + b_post)
    ci = stats.beta.ppf([0.025, 0.975], a_post, b_post)
    print(f"{name}: mean={mean_post:.4f}, 95%CI=({ci[0]:.4f}, {ci[1]:.4f})")

# ========== 正态-正态共轭模型 ==========

# 已知方差的正态分布，正态先验
# 先验：N(mu_0, tau_0^2)
mu_0 = 0      # 先验均值
tau_0 = 10    # 先验标准差

# 数据
sample = np.random.normal(5, 2, 30)  # 真实均值5，标准差2
sigma = 2     # 已知数据标准差
n = len(sample)
sample_mean = np.mean(sample)

# 后验参数
# 精度（方差的倒数）加权平均
precision_prior = 1 / tau_0**2
precision_data = n / sigma**2
precision_post = precision_prior + precision_data

tau_post = np.sqrt(1 / precision_post)
mu_post = (precision_prior * mu_0 + precision_data * sample_mean) / precision_post

print(f"\nNormal-Normal Conjugate:")
print(f"Prior: N({mu_0}, {tau_0}^2)")
print(f"Data: mean={sample_mean:.4f}, n={n}")
print(f"Posterior: N({mu_post:.4f}, {tau_post:.4f}^2)")

# ========== MAP估计（数值优化） ==========

from scipy.optimize import minimize

# 定义负对数后验（用于最小化）
def neg_log_posterior(params, data):
    mu, sigma = params
    if sigma <= 0:
        return 1e10
    
    # 对数似然
    log_likelihood = np.sum(stats.norm.logpdf(data, mu, sigma))
    
    # 对数先验（弱先验）
    log_prior_mu = stats.norm.logpdf(mu, 0, 10)  # mu ~ N(0, 100)
    log_prior_sigma = stats.expon.logpdf(sigma, scale=10)  # sigma ~ Exp(1/10)
    
    return -(log_likelihood + log_prior_mu + log_prior_sigma)

# 优化
result = minimize(neg_log_posterior, x0=[np.mean(sample), np.std(sample)], 
                  args=(sample,), method='L-BFGS-B',
                  bounds=[(None, None), (0.001, None)])

map_mu, map_sigma = result.x
print(f"\nMAP estimates: μ={map_mu:.4f}, σ={map_sigma:.4f}")

# ========== 贝叶斯A/B测试 ==========

# 对照组：1000次访问，50次转化
# 实验组：1000次访问，65次转化

alpha_prior_ab = 1
beta_prior_ab = 1

# 对照组
n_a, conv_a = 1000, 50
alpha_a = alpha_prior_ab + conv_a
beta_a = beta_prior_ab + n_a - conv_a

# 实验组  
n_b, conv_b = 1000, 65
alpha_b = alpha_prior_ab + conv_b
beta_b = beta_prior_ab + n_b - conv_b

# 从后验采样
np.random.seed(42)
samples_a = np.random.beta(alpha_a, beta_a, 100000)
samples_b = np.random.beta(alpha_b, beta_b, 100000)

# B优于A的概率
prob_b_better = np.mean(samples_b > samples_a)
print(f"\nA/B Test Results:")
print(f"P(conv_B > conv_A) = {prob_b_better:.4f}")

# 提升率的分布
lift = (samples_b - samples_a) / samples_a
print(f"Expected lift: {np.mean(lift)*100:.2f}%")
print(f"95% CI for lift: ({np.percentile(lift, 2.5)*100:.2f}%, {np.percentile(lift, 97.5)*100:.2f}%)")

# ========== PyMC3/NumPyro风格的手动MCMC ==========

def metropolis_hastings(log_posterior, initial, n_samples=10000, proposal_std=0.1):
    """简单的Metropolis-Hastings MCMC实现"""
    samples = [initial]
    current = initial
    current_log_prob = log_posterior(current)
    
    for _ in range(n_samples):
        # 提议新值
        proposal = current + np.random.normal(0, proposal_std, size=len(current))
        proposal_log_prob = log_posterior(proposal)
        
        # 计算接受概率
        log_alpha = proposal_log_prob - current_log_prob
        
        if np.log(np.random.uniform()) < log_alpha:
            current = proposal
            current_log_prob = proposal_log_prob
        
        samples.append(current.copy())
    
    return np.array(samples[1000:])  # 丢弃burn-in

# 定义对数后验（正态分布参数）
def log_posterior_normal(params):
    mu, log_sigma = params
    sigma = np.exp(log_sigma)  # 保证sigma为正
    
    # 似然
    log_lik = np.sum(stats.norm.logpdf(sample, mu, sigma))
    
    # 先验
    log_prior = stats.norm.logpdf(mu, 0, 10) + stats.norm.logpdf(log_sigma, 0, 2)
    
    return log_lik + log_prior

# 运行MCMC
print("\nRunning MCMC...")
mcmc_samples = metropolis_hastings(log_posterior_normal, [0, 0], n_samples=5000)

print(f"MCMC Results (after burn-in):")
print(f"μ: mean={np.mean(mcmc_samples[:, 0]):.4f}, std={np.std(mcmc_samples[:, 0]):.4f}")
print(f"σ: mean={np.exp(np.mean(mcmc_samples[:, 1])):.4f}")
```

## 应用场景

### 机器学习
- **贝叶斯线性回归**：提供预测的不确定性估计
- **高斯过程**：非参数化的贝叶斯方法，用于回归和分类
- **变分推断**：近似复杂后验分布，用于深度学习（VAE）
- **贝叶斯神经网络**：权重的不确定性量化

### A/B测试
- **早期停止**：使用贝叶斯方法可以更早做出决策
- **连续监控**：无需预设样本量，可动态决策
- **业务价值量化**：直接估计"B优于A"的概率和提升率分布

### 推荐系统
- **汤普森采样**：平衡探索与利用的多臂老虎机算法
- **贝叶斯个性化排序**：结合先验知识的协同过滤

### 异常检测
- **贝叶斯变点检测**：检测时间序列中的突变点
- **新颖性检测**：基于预测分布的异常识别

## 面试要点

1. **Q: 贝叶斯方法与频率学派方法的核心区别是什么？**  
   A: (1) 概率解释：贝叶斯将概率视为信念程度，频率学派视为长期频率；(2) 参数视角：贝叶斯视参数为随机变量，频率学派视参数为固定未知常数；(3) 推断方式：贝叶斯结合先验和似然得到后验，频率学派仅基于样本数据；(4) 结果形式：贝叶斯给出后验分布/概率，频率学派给出点估计和置信区间。实践中两种方法在样本量很大时结果趋于一致。

2. **Q: 如何选择先验分布？如果没有先验知识怎么办？**  
   A: 选择原则：(1) 共轭先验简化计算；(2) 信息先验反映领域知识；(3) 无信息先验让数据主导。无先验知识时：(1) 使用均匀分布（平坦先验）；(2) 使用Jeffreys先验（与参数化无关）；(3) 使用弱信息先验（如N(0, 1000)）保证数值稳定性。注意：即使使用无信息先验，选择仍可能影响小样本结果。

3. **Q: 可信区间(Credible Interval)和置信区间(Confidence Interval)有什么区别？**  
   A: 可信区间是贝叶斯概念，表示"给定数据，参数落在这个区间内的概率为95%"，是对参数的概率陈述。置信区间是频率学派概念，表示"如果我们重复抽样100次，大约95次构造的区间会包含真实参数"，是对区间的频率陈述。置信区间不表示参数有95%概率在区间内（参数是固定的）。

4. **Q: MCMC方法的基本思想是什么？为什么需要它？**  
   A: 许多贝叶斯模型的后验分布没有解析解，MCMC通过构建马尔可夫链，使其平稳分布为目标后验分布，从链中采样近似后验。核心思想：从提议分布生成候选，按接受概率决定是否采纳，最终样本服从目标分布。需要MCMC的场景：复杂模型（混合模型、分层模型）、高维参数空间、非共轭先验。

## 相关概念

### 数据结构
- [数组](../../computer-science/data-structures/array.md) - 样本数据存储
- [树](../../computer-science/data-structures/tree.md) - 决策树的贝叶斯方法

### 算法
- [采样算法](../../computer-science/algorithms/sampling.md) - MCMC基础
- [优化算法](../../computer-science/algorithms/optimization.md) - MAP估计

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - MCMC计算复杂度

### 系统实现
- [A/B测试](../../ai-data-systems/ab-testing.md) - 贝叶斯实验方法
- [推荐系统](../../ai-data-systems/recommendation-systems.md) - 汤普森采样

### 数学基础
- [概率分布](./probability-distributions.md) - 先验与后验分布
- [假设检验](./hypothesis-testing.md) - 贝叶斯因子
- [置信区间](./confidence-intervals.md) - 可信区间对比
- [描述统计](./descriptive-statistics.md) - 后验统计量
- [线性代数](../linear-algebra/matrix-operations.md) - 多元正态分布
- [微积分](../calculus/derivatives.md) - 积分计算
