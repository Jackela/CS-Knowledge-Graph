# 积分 (Integrals)

**积分 (Integral)** 是微积分的另一个核心概念，包括**不定积分 (Indefinite Integral)** 和**定积分 (Definite Integral)**。不定积分是求导的逆运算，而定积分则用于计算曲线下的面积、体积等累积量。

## 原理 (Principles)

### 不定积分

```
不定积分（反导数）：

若 F'(x) = f(x)，则 ∫f(x)dx = F(x) + C

其中：
- f(x) 称为被积函数
- F(x) 称为原函数
- C 为任意常数（积分常数）
- dx 表示积分变量
```

**基本积分公式：**

```
∫xⁿ dx = xⁿ⁺¹/(n+1) + C  (n ≠ -1)
∫1/x dx = ln|x| + C
∫eˣ dx = eˣ + C
∫aˣ dx = aˣ/ln(a) + C
∫sin x dx = -cos x + C
∫cos x dx = sin x + C
∫sec²x dx = tan x + C
∫1/(1+x²) dx = arctan x + C
∫1/√(1-x²) dx = arcsin x + C
```

### 定积分

```
定积分的定义（黎曼积分）：

∫ₐᵇ f(x)dx = lim Σ f(ξᵢ)Δxᵢ
            λ→0

其中：
- [a, b] 为积分区间
- a 为积分下限，b 为积分上限
- λ = max{Δxᵢ}

几何意义：曲边梯形的面积（f(x) ≥ 0 时）
```

**定积分的性质：**

```
1. 线性性：∫ₐᵇ [αf(x) + βg(x)]dx = α∫ₐᵇ f(x)dx + β∫ₐᵇ g(x)dx

2. 区间可加性：∫ₐᵇ f(x)dx + ∫ᵇᶜ f(x)dx = ∫ₐᶜ f(x)dx

3. 积分方向：∫ₐᵇ f(x)dx = -∫ᵇₐ f(x)dx

4. 常数积分：∫ₐᵇ 1 dx = b - a

5. 比较定理：若 f(x) ≤ g(x)，则 ∫ₐᵇ f(x)dx ≤ ∫ₐᵇ g(x)dx

6. 积分中值定理：存在 ξ ∈ [a,b]，使 ∫ₐᵇ f(x)dx = f(ξ)(b-a)
```

### 微积分基本定理

```
牛顿-莱布尼茨公式：

若 F(x) 是 f(x) 的一个原函数，则：

∫ₐᵇ f(x)dx = F(b) - F(a) = F(x)|ₐᵇ

这是连接微分学和积分学的桥梁。
```

**变上限积分：**
```
Φ(x) = ∫ₐˣ f(t)dt

则：Φ'(x) = f(x)

更一般地：d/dx ∫ᵤ₍ₓ₎ᵛ₍ₓ₎ f(t)dt = f(v(x))v'(x) - f(u(x))u'(x)
```

### 积分方法

**换元积分法（第一类）：**
```
∫f(φ(x))φ'(x)dx = ∫f(u)du = F(u) + C = F(φ(x)) + C

其中 u = φ(x)

示例：∫2x cos(x²)dx = ∫cos(u)du = sin(x²) + C  （令 u = x²）
```

**换元积分法（第二类）：**
```
∫ₐᵇ f(x)dx = ∫ᵦᵅ f(φ(t))φ'(t)dt

其中 x = φ(t)，当 x=a 时 t=α，x=b 时 t=β

常用换元：
- 三角换元：√(a²-x²) → x = a sin t
- 根式换元：ⁿ√(ax+b) → t = ⁿ√(ax+b)
- 倒代换：x = 1/t
```

**分部积分法：**
```
∫u dv = uv - ∫v du

或：∫u(x)v'(x)dx = u(x)v(x) - ∫v(x)u'(x)dx

选择 u 的 LIATE 法则：
L - 对数函数
I - 反三角函数
A - 代数函数
T - 三角函数
E - 指数函数

优先级高的选作 u
```

### 反常积分

**无穷区间上的积分：**
```
∫ₐ^∞ f(x)dx = lim ∫ₐᵇ f(x)dx
            b→∞

∫_(-∞)^ᵇ f(x)dx = lim ∫ₐᵇ f(x)dx
              a→-∞

∫_(-∞)^∞ f(x)dx = ∫_(-∞)^ᶜ f(x)dx + ∫ᶜ^∞ f(x)dx
```

**无界函数的积分：**
```
若 f(x) 在 a 点附近无界：

∫ₐᵇ f(x)dx = lim ∫_(a+ε)ᵇ f(x)dx
           ε→0⁺
```

**收敛判别：**
- 比较判别法
- p-积分：∫₁^∞ 1/xᵖ dx 当 p > 1 时收敛
- p-积分：∫₀¹ 1/xᵖ dx 当 p < 1 时收敛

### 定积分的几何应用

**平面图形面积：**
```
由 y=f(x)，y=g(x)，x=a，x=b 围成的区域：
S = ∫ₐᵇ |f(x) - g(x)| dx

极坐标下：S = ½∫ₐᵝ r²(θ)dθ
```

**旋转体体积：**
```
圆盘法（绕 x 轴）：V = π∫ₐᵇ [f(x)]² dx

壳法（绕 y 轴）：V = 2π∫ₐᵇ x f(x) dx
```

**曲线弧长：**
```
y = f(x)：L = ∫ₐᵇ √(1 + [f'(x)]²) dx

参数方程：L = ∫ₐᵝ √([φ'(t)]² + [ψ'(t)]²) dt

极坐标：L = ∫ₐᵝ √(r² + [r'(θ)]²) dθ
```

## 关键性质

- **线性性**：积分运算满足线性性质
- **区间可加性**：大区间积分可分解为小区间积分之和
- **保号性**：非负函数的积分非负
- **积分中值定理**：定积分等于某点函数值乘以区间长度
- **微积分基本定理**：揭示了微分和积分的互逆关系

## 复杂度分析 (Complexity Analysis)

积分计算的时间复杂度：
- 基本积分查表：O(1)
- 多项式积分：O(n)（n 为次数）
- 数值积分（梯形法/辛普森法）：O(n)（n 为子区间数）
- 蒙特卡洛积分：O(n)（n 为采样点数，精度 ε=O(1/√n)）

数值积分的精度：
- 矩形法：O(h)
- 梯形法：O(h²)
- 辛普森法：O(h⁴)

其中 h 为步长

## 实现示例 (Implementation)

```python
import numpy as np
import sympy as sp
from sympy import symbols, integrate, sin, cos, exp, log, sqrt, oo, pi
from scipy import integrate as sci_integrate

# 符号积分
x = symbols('x')

# 不定积分
f = x**2
integral = integrate(f, x)
print(f"∫x²dx = {integral} + C")  # x**3/3

# 定积分
f = x**2
result = integrate(f, (x, 0, 1))
print(f"∫₀¹ x²dx = {result}")  # 1/3

# 三角函数积分
f = sin(x)**2
integral = integrate(f, x)
print(f"∫sin²x dx = {integral}")

# 分部积分示例
f = x * exp(x)
integral = integrate(f, x)
print(f"∫xeˣdx = {integral}")  # (x-1)*e^x

# 反常积分
f = exp(-x**2)
result = integrate(f, (x, 0, oo))
print(f"∫₀^∞ e^(-x²)dx = {result}")  # √π/2

# 数值积分 - 梯形法
def trapezoidal_rule(f, a, b, n=1000):
    """梯形法数值积分"""
    x = np.linspace(a, b, n+1)
    y = f(x)
    h = (b - a) / n
    return h * (0.5*y[0] + np.sum(y[1:-1]) + 0.5*y[-1])

# 示例：计算 ∫₀^π sin(x)dx
f = np.sin
result = trapezoidal_rule(f, 0, np.pi, n=1000)
print(f"梯形法计算 ∫₀^π sin(x)dx ≈ {result}")  # 接近 2.0

# 数值积分 - 辛普森法
def simpson_rule(f, a, b, n=1000):
    """辛普森法数值积分（n 必须为偶数）"""
    if n % 2 == 1:
        n += 1
    x = np.linspace(a, b, n+1)
    y = f(x)
    h = (b - a) / n
    
    return h/3 * (y[0] + 4*np.sum(y[1:-1:2]) + 2*np.sum(y[2:-2:2]) + y[-1])

result = simpson_rule(f, 0, np.pi, n=1000)
print(f"辛普森法计算 ∫₀^π sin(x)dx ≈ {result}")  # 更接近 2.0

# 使用 scipy 进行数值积分
def integrand(x):
    return np.exp(-x**2)

result, error = sci_integrate.quad(integrand, 0, np.inf)
print(f"scipy 计算 ∫₀^∞ e^(-x²)dx = {result:.10f} ± {error:.2e}")

# 蒙特卡洛积分
def monte_carlo_integral(f, a, b, n=100000):
    """蒙特卡洛方法估计积分"""
    x = np.random.uniform(a, b, n)
    y = f(x)
    return (b - a) * np.mean(y), (b - a) * np.std(y) / np.sqrt(n)

# 计算 ∫₀¹ x² dx = 1/3
result, error = monte_carlo_integral(lambda x: x**2, 0, 1)
print(f"蒙特卡洛估计 ∫₀¹ x²dx = {result:.6f} ± {error:.6f}")

# 多重积分
from scipy.integrate import dblquad

def integrand2d(y, x):
    return x * y

result, error = dblquad(integrand2d, 0, 1, lambda x: 0, lambda x: 1)
print(f"二重积分 ∫₀¹∫₀¹ xy dxdy = {result}")  # 0.25

# 计算曲线下面积（可视化）
def plot_integration():
    import matplotlib.pyplot as plt
    
    x = np.linspace(0, 2, 100)
    y = x**2
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', linewidth=2, label='$f(x) = x^2$')
    plt.fill_between(x, 0, y, alpha=0.3)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Area under curve: $\int_0^2 x^2 dx = 8/3$')
    plt.legend()
    plt.grid(True)
    plt.savefig('integral_area.png')
    plt.close()

# 概率论应用：期望值计算
def expected_value_continuous(pdf, x_range, n=10000):
    """
    计算连续随机变量的期望值
    E[X] = ∫ x·f(x) dx
    """
    x = np.linspace(x_range[0], x_range[1], n)
    dx = x[1] - x[0]
    return np.sum(x * pdf(x) * dx)

# 标准正态分布的期望
pdf = lambda x: np.exp(-x**2/2) / np.sqrt(2*np.pi)
ex = expected_value_continuous(pdf, (-5, 5))
print(f"标准正态分布 E[X] ≈ {ex:.6f}")  # 接近 0

# 积分在物理中的应用：计算功
def work_integral(force_func, x_start, x_end):
    """
    计算变力做功：W = ∫ F(x) dx
    """
    result, _ = sci_integrate.quad(force_func, x_start, x_end)
    return result

# 胡克定律 F = kx，k=10，从 x=0 拉伸到 x=0.1
k = 10
work = work_integral(lambda x: k*x, 0, 0.1)
print(f"弹簧做功 = {work} J")  # 0.05 J
```

## 应用场景 (Applications)

- **物理学**：计算变力做功、质心、转动惯量、引力势能
- **工程学**：结构分析中的弯矩和剪力计算、流体流量
- **概率论**：概率密度函数的归一化、期望值和方差计算
- **经济学**：消费者剩余和生产者剩余的计算
- **信号处理**：傅里叶变换、频谱分析
- **机器学习**：概率模型的边缘化、变分推断
- **计算机图形学**：曲线长度、曲面面积、体积计算
- **统计学**：累积分布函数、生存分析

## 面试要点 (Interview Questions)

**Q1: 不定积分和定积分有什么区别？**
> 不定积分是求原函数，结果是一族函数（含任意常数 C）；定积分是求累积量（如面积），结果是一个数值。通过微积分基本定理，定积分可以用不定积分计算：∫ₐᵇf(x)dx = F(b) - F(a)。

**Q2: 换元积分法和分部积分法分别在什么情况下使用？**
> 换元积分法适用于被积函数含有复合函数的情况，通过变量替换简化积分。分部积分法适用于被积函数是两类函数乘积的情况，如多项式×指数、多项式×三角函数等，使用公式 ∫udv = uv - ∫vdu。

**Q3: 微积分基本定理的意义是什么？**
> 微积分基本定理揭示了微分和积分是互逆运算，建立了局部性质（导数）和整体性质（积分）之间的联系。它使得定积分计算不再需要求黎曼和的极限，而只需找到原函数即可。

**Q4: 反常积分什么时候收敛？**
> 反常积分分为无穷区间积分和无界函数积分。收敛性可以通过比较判别法判断，关键是看被积函数在无穷远处或奇点附近衰减/增长的快慢。例如 ∫₁^∞ 1/xᵖ dx 当 p>1 时收敛。

**Q5: 数值积分有哪些方法？各自的精度如何？**
> 常用的数值积分方法包括：矩形法（O(h)）、梯形法（O(h²)）、辛普森法（O(h⁴)）、高斯求积（精度更高）。精度随步长 h 减小而提高，但计算量也随之增加。实际应用中需要在精度和效率之间权衡。

## 相关概念 (Related Concepts)

- [极限与连续](./limits-continuity.md) - 积分定义的基础
- [导数](./derivatives.md) - 微积分基本定理连接导数和积分
- [多元微积分](./multivariable-calculus.md) - 多重积分
- [微分方程](./differential-equations.md) - 积分在求解微分方程中的应用
- [概率论](../probability.md) - 概率密度函数的积分
- [贝叶斯统计](../statistics/bayesian-statistics.md) - 后验分布的边缘化
- [机器学习概述](../../ai-data-systems/ml-overview.md) - 变分推断

## 参考资料 (References)

- 《高等数学》同济大学数学系
- 《数学分析》华东师范大学数学系
- 3Blue1Brown《微积分的本质》系列（YouTube）
- MIT OpenCourseWare 18.01 Single Variable Calculus
- 《Numerical Recipes》William H. Press et al.（数值积分章节）
