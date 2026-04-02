# 导数 (Derivatives)

**导数 (Derivative)** 是描述函数变化率的数学工具，表示函数在某一点处的瞬时变化率。导数是微积分的核心概念，广泛应用于物理、工程、经济学和机器学习等领域。

## 原理 (Principles)

### 导数的定义

```
函数 f(x) 在点 x₀ 处的导数：

f'(x₀) = lim  [f(x₀ + Δx) - f(x₀)] / Δx
        Δx→0

或等价地：

f'(x₀) = lim  [f(x) - f(x₀)] / (x - x₀)
        x→x₀

几何意义：切线的斜率
```

**导数的等价定义：**
- 差商形式：Δy/Δx = [f(x+Δx) - f(x)] / Δx
- 增量形式：f'(x) = dy/dx
- 莱布尼茨记法：df/dx

### 求导法则

```
基本求导法则：

1. 常数：d/dx [c] = 0

2. 幂函数：d/dx [xⁿ] = nxⁿ⁻¹

3. 和差：d/dx [u ± v] = u' ± v'

4. 积法则：d/dx [uv] = u'v + uv'

5. 商法则：d/dx [u/v] = (u'v - uv') / v²

6. 链式法则：d/dx [f(g(x))] = f'(g(x)) · g'(x)
```

**常见函数的导数：**

```
- d/dx [sin x] = cos x
- d/dx [cos x] = -sin x
- d/dx [tan x] = sec²x
- d/dx [eˣ] = eˣ
- d/dx [aˣ] = aˣ ln a
- d/dx [ln x] = 1/x
- d/dx [logₐx] = 1/(x ln a)
- d/dx [arcsin x] = 1/√(1-x²)
- d/dx [arctan x] = 1/(1+x²)
```

### 高阶导数

```
二阶导数：f''(x) = d²f/dx² = (f')'

n 阶导数：f⁽ⁿ⁾(x) = dⁿf/dxⁿ

莱布尼茨公式（乘积的 n 阶导数）：
(uv)⁽ⁿ⁾ = Σ C(n,k) u⁽ⁿ⁻ᵏ⁾ v⁽ᵏ⁾
          k=0

常用高阶导数：
- (eˣ)⁽ⁿ⁾ = eˣ
- (sin x)⁽ⁿ⁾ = sin(x + nπ/2)
- (cos x)⁽ⁿ⁾ = cos(x + nπ/2)
- (1/x)⁽ⁿ⁾ = (-1)ⁿ n! / xⁿ⁺¹
```

### 隐函数求导

```
由 F(x,y) = 0 确定的隐函数 y = y(x)：

对方程两边关于 x 求导，然后解出 dy/dx

示例：x² + y² = 1
两边求导：2x + 2y(dy/dx) = 0
解得：dy/dx = -x/y
```

### 参数方程求导

```
参数方程：x = φ(t), y = ψ(t)

dy/dx = (dy/dt) / (dx/dt) = ψ'(t) / φ'(t)

d²y/dx² = d/dx(dy/dx) = [d/dt(dy/dx)] / (dx/dt)
```

### 导数的应用

**函数的单调性：**
```
- f'(x) > 0 ⟹ f(x) 单调递增
- f'(x) < 0 ⟹ f(x) 单调递减
- f'(x) = 0 ⟹ 驻点（可能为极值点）
```

**极值判定：**
```
一阶导数判别法：
- f'(x) 由正变负 ⟹ 极大值
- f'(x) 由负变正 ⟹ 极小值

二阶导数判别法：
- f'(x₀) = 0 且 f''(x₀) < 0 ⟹ 极大值
- f'(x₀) = 0 且 f''(x₀) > 0 ⟹ 极小值
- f'(x₀) = 0 且 f''(x₀) = 0 ⟹ 需进一步判断
```

**凹凸性与拐点：**
```
- f''(x) > 0 ⟹ 函数在该区间下凸（凹函数）
- f''(x) < 0 ⟹ 函数在该区间上凸（凸函数）
- f''(x) = 0 且变号 ⟹ 拐点
```

**泰勒公式：**
```
f(x) = f(x₀) + f'(x₀)(x-x₀) + f''(x₀)(x-x₀)²/2! + ... + f⁽ⁿ⁾(x₀)(x-x₀)ⁿ/n! + Rₙ(x)

其中 Rₙ(x) = f⁽ⁿ⁺¹⁾(ξ)(x-x₀)ⁿ⁺¹/(n+1)! （拉格朗日余项）

麦克劳林公式（x₀ = 0）：
eˣ = 1 + x + x²/2! + x³/3! + ...
sin x = x - x³/3! + x⁵/5! - ...
cos x = 1 - x²/2! + x⁴/4! - ...
ln(1+x) = x - x²/2 + x³/3 - ...
```

**洛必达法则：**
```
若 lim f(x) = lim g(x) = 0 或 ∞
   x→a       x→a

且 lim f'(x)/g'(x) 存在，则：
   x→a

lim f(x)/g(x) = lim f'(x)/g'(x)
x→a           x→a
```

## 关键性质

- **线性性**：导数运算满足线性性质，(af + bg)' = af' + bg'
- **局部性**：导数只与函数在该点附近的性质有关
- **连续性**：可导必连续，但连续不一定可导
- **可导的充要条件**：左导数等于右导数
- **中值定理**：若 f 在 [a,b] 连续，在 (a,b) 可导，则存在 ξ ∈ (a,b) 使 f'(ξ) = [f(b)-f(a)]/(b-a)

## 复杂度分析 (Complexity Analysis)

求导运算的时间复杂度：
- 基本函数求导：O(1)
- 多项式求导：O(n)（n 为次数）
- 复合函数求导（链式法则）：O(depth)（depth 为嵌套深度）
- 符号微分（自动微分）：O(n)（n 为计算图节点数）

自动微分的空间复杂度：
- 前向模式：O(1)
- 反向模式：O(n)（需要存储中间结果）

## 实现示例 (Implementation)

```python
import numpy as np
import sympy as sp
from sympy import symbols, diff, sin, cos, exp, log, sqrt

# 符号计算
x = symbols('x')

# 基本求导
f = x**3 + 2*x**2 - 5*x + 1
f_prime = diff(f, x)
print(f"f'(x) = {f_prime}")  # 3*x**2 + 4*x - 5

# 乘积法则验证
u = x**2
v = sin(x)
product_rule = diff(u*v, x)
manual = diff(u, x)*v + u*diff(v, x)
print(f"乘积法则：{product_rule} = {manual}？{product_rule == manual}")

# 链式法则
f = sin(x**2)
f_prime = diff(f, x)
print(f"d/dx[sin(x²)] = {f_prime}")  # 2*x*cos(x**2)

# 高阶导数
f = exp(x)
for n in range(1, 5):
    print(f"f⁽{n}⁾(x) = {diff(f, x, n)}")

# 数值微分
def numerical_derivative(f, x, h=1e-7):
    """中心差分法求导"""
    return (f(x + h) - f(x - h)) / (2 * h)

# 示例：f(x) = x² 在 x=2 的导数
f = lambda x: x**2
result = numerical_derivative(f, 2)
print(f"数值导数 f'(2) ≈ {result}")  # 接近 4.0

# 梯度下降中的导数应用
def gradient_descent(f, df, x0, lr=0.1, epochs=100):
    """
    梯度下降优化
    f: 目标函数
    df: 导数函数
    x0: 初始值
    lr: 学习率
    epochs: 迭代次数
    """
    x = x0
    history = [x]
    
    for _ in range(epochs):
        gradient = df(x)
        x = x - lr * gradient
        history.append(x)
    
    return x, history

# 最小化 f(x) = x² - 4x + 4 = (x-2)²
f = lambda x: x**2 - 4*x + 4
df = lambda x: 2*x - 4

minimum, history = gradient_descent(f, df, x0=0, lr=0.3, epochs=20)
print(f"最小值点: x = {minimum:.4f}")  # 接近 2.0

# 使用自动微分（JAX 风格）
try:
    import jax
    import jax.numpy as jnp
    from jax import grad
    
    def f_jax(x):
        return jnp.sin(x) * jnp.exp(-x**2)
    
    df_jax = grad(f_jax)
    result = df_jax(1.0)
    print(f"JAX 自动微分结果: {result}")
except ImportError:
    print("JAX 未安装，跳过自动微分示例")

# 数值微分的误差分析
def derivative_error_analysis():
    f = lambda x: np.sin(x)
    df_exact = lambda x: np.cos(x)
    x0 = 1.0
    
    hs = [10**(-i) for i in range(1, 15)]
    errors = []
    
    for h in hs:
        df_approx = (f(x0 + h) - f(x0 - h)) / (2 * h)
        error = abs(df_approx - df_exact(x0))
        errors.append(error)
        print(f"h={h:.0e}: 误差={error:.2e}")
    
    return hs, errors

# derivative_error_analysis()
```

## 应用场景 (Applications)

- **物理学**：速度是位移的导数，加速度是速度的导数
- **经济学**：边际成本是总成本的导数，边际收益是总收益的导数
- **机器学习**：梯度下降法利用导数寻找损失函数的最小值
- **计算机图形学**：曲线和曲面的切线、法向量计算
- **优化问题**：利用导数寻找函数的极值点
- **信号处理**：滤波器设计中的频率响应分析
- **控制系统**：PID 控制器中的微分环节
- **数值分析**：牛顿迭代法求根

## 面试要点 (Interview Questions)

**Q1: 导数和微分有什么区别？**
> 导数是函数在某点的变化率（一个数），记作 f'(x)；微分是函数增量的线性主部（一个表达式），记作 dy = f'(x)dx。导数是微分的商，即 f'(x) = dy/dx。

**Q2: 链式法则是什么？为什么重要？**
> 链式法则是复合函数求导法则：d/dx[f(g(x))] = f'(g(x))·g'(x)。它是深度学习中反向传播算法的数学基础，使得可以高效计算多层神经网络的梯度。

**Q3: 什么是泰勒展开？有什么应用？**
> 泰勒公式将函数在某点附近展开为多项式：f(x) ≈ f(a) + f'(a)(x-a) + f''(a)(x-a)²/2! + ...。应用包括：近似计算、误差估计、数值算法设计、物理问题的线性化分析。

**Q4: 可导和连续的关系是什么？**
> 可导必连续，但连续不一定可导。例如 f(x) = |x| 在 x=0 处连续但不可导（左右导数不相等）。可导要求函数不仅连续，而且变化平滑。

**Q5: 梯度下降中为什么需要计算导数？**
> 导数指示了函数增长最快的方向，负梯度方向则是函数下降最快的方向。梯度下降通过沿负梯度方向更新参数，逐步逼近损失函数的最小值。导数的大小也决定了更新的步长。

## 相关概念 (Related Concepts)

- [极限与连续](./limits-continuity.md) - 导数定义的基础
- [积分](./integrals.md) - 微积分基本定理连接导数和积分
- [多元微积分](./multivariable-calculus.md) - 偏导数和梯度
- [微分方程](./differential-equations.md) - 包含未知函数导数的方程
- [线性代数](../linear-algebra.md) - 雅可比矩阵和海森矩阵
- [优化理论](../../ai-data-systems/ml-overview.md) - 梯度下降与凸优化
- [神经网络](../../ai-data-systems/cnn.md) - 反向传播与自动微分

## 参考资料 (References)

- 《高等数学》同济大学数学系
- 《普林斯顿微积分读本》Adrian Banner
- 3Blue1Brown《微积分的本质》系列（YouTube）
- MIT OpenCourseWare 18.01 Single Variable Calculus
- 《Deep Learning》Goodfellow et al.（优化章节）
