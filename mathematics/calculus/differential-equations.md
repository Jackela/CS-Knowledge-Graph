# 微分方程 (Differential Equations)

**微分方程 (Differential Equation)** 是含有未知函数及其导数的方程，是描述自然界变化规律的强大数学工具。根据未知函数的个数和自变量的个数，可分为常微分方程（ODE）和偏微分方程（PDE）。

## 原理 (Principles)

### 微分方程的分类

```
按自变量个数分类：
- 常微分方程（ODE）：只有一个自变量
  例：y'' + y' + y = 0

- 偏微分方程（PDE）：多个自变量
  例：∂u/∂t = ∂²u/∂x²（热传导方程）

按阶数分类：
- 一阶：y' = f(x,y)
- 二阶：y'' = f(x,y,y')
- n 阶：含有 n 阶导数

按线性分类：
- 线性：关于 y 及其导数都是一次的
- 非线性：含有 y 或其导数的高次项
```

### 一阶微分方程

**可分离变量方程：**
```
dy/dx = f(x)g(y)

解法：∫ dy/g(y) = ∫ f(x) dx
```

**齐次方程：**
```
dy/dx = f(y/x)

解法：令 u = y/x，化为可分离变量方程
```

**一阶线性方程：**
```
dy/dx + P(x)y = Q(x)

通解公式：
y = e^(-∫P dx) [∫ Q e^(∫P dx) dx + C]

或：y = y_h + y_p
其中 y_h 是对应齐次方程的解，y_p 是特解
```

**伯努利方程：**
```
dy/dx + P(x)y = Q(x)yⁿ  (n ≠ 0,1)

解法：令 z = y^(1-n)，化为一阶线性方程
```

### 二阶线性微分方程

**常系数齐次方程：**
```
ay'' + by' + cy = 0

特征方程：ar² + br + c = 0

根据判别式 Δ = b² - 4ac：

1. Δ > 0（两不等实根 r₁, r₂）：
   y = C₁e^(r₁x) + C₂e^(r₂x)

2. Δ = 0（重根 r）：
   y = (C₁ + C₂x)e^(rx)

3. Δ < 0（共轭复根 α ± βi）：
   y = e^(αx)(C₁cos βx + C₂sin βx)
```

**常系数非齐次方程：**
```
ay'' + by' + cy = f(x)

通解结构：y = y_h + y_p
- y_h：对应齐次方程的通解
- y_p：非齐次方程的特解

待定系数法求 y_p：
若 f(x) = Pₙ(x)e^(λx)
设 y_p = x^k Qₙ(x)e^(λx)
其中 k 是 λ 作为特征根的重数（0,1,2）
```

**欧拉方程：**
```
x²y'' + pxy' + qy = f(x)  (x > 0)

解法：令 x = e^t，化为常系数方程
```

### 高阶微分方程

**n 阶常系数齐次方程：**
```
y⁽ⁿ⁾ + a₁y⁽ⁿ⁻¹⁾ + ... + aₙy = 0

特征方程：rⁿ + a₁rⁿ⁻¹ + ... + aₙ = 0

若特征根为 r₁, r₂, ..., rₙ：
- 单实根 r：对应项 Ce^(rx)
- k 重实根 r：对应项 (C₁ + C₂x + ... + Cₖx^(k-1))e^(rx)
- 单复根 α ± βi：对应项 e^(αx)(C₁cos βx + C₂sin βx)
```

### 微分方程组

**线性微分方程组：**
```
dY/dx = AY + F(x)

其中 Y = [y₁, y₂, ..., yₙ]ᵀ，A 是 n×n 矩阵

齐次方程的解：
若 A 有 n 个线性无关特征向量，则通解为：
Y = C₁e^(λ₁x)v₁ + C₂e^(λ₂x)v₂ + ... + Cₙe^(λₙx)vₙ
```

### 偏微分方程基础

**波动方程：**
```
∂²u/∂t² = c²∂²u/∂x²

描述：弦的振动、电磁波传播
通解：u(x,t) = f(x-ct) + g(x+ct)
```

**热传导方程：**
```
∂u/∂t = k∂²u/∂x²

描述：热量传导、扩散过程
```

**拉普拉斯方程：**
```
∇²u = ∂²u/∂x² + ∂²u/∂y² + ∂²u/∂z² = 0

描述：稳态温度分布、电势分布、不可压缩无旋流
```

**泊松方程：**
```
∇²u = f(x,y,z)

描述：有源场中的势分布
```

### 数值解法

**欧拉法：**
```
y_{n+1} = y_n + h·f(x_n, y_n)

局部截断误差：O(h²)
全局误差：O(h)
```

**改进欧拉法（梯形法）：**
```
y_{n+1} = y_n + h/2·[f(x_n, y_n) + f(x_{n+1}, y_{n+1})]

 predictor-corrector 形式：
 y* = y_n + h·f(x_n, y_n)          （预测）
 y_{n+1} = y_n + h/2·[f(x_n,y_n) + f(x_{n+1},y*)]  （校正）

局部截断误差：O(h³)
```

**龙格-库塔法（RK4）：**
```
y_{n+1} = y_n + h/6·(k₁ + 2k₂ + 2k₃ + k₄)

其中：
k₁ = f(x_n, y_n)
k₂ = f(x_n + h/2, y_n + hk₁/2)
k₃ = f(x_n + h/2, y_n + hk₂/2)
k₄ = f(x_n + h, y_n + hk₃)

局部截断误差：O(h⁵)
全局误差：O(h⁴)
```

## 关键性质

- **解的存在唯一性**：在一定条件下，初值问题有唯一解
- **叠加原理**：线性齐次方程的解的线性组合仍是解
- **通解结构**：n 阶线性方程的通解含 n 个任意常数
- **稳定性**：解对初值或参数的敏感程度
- **渐近行为**：t→∞ 时解的极限行为

## 复杂度分析 (Complexity Analysis)

解析求解的复杂度：
- 可分离变量方程：O(1)（直接积分）
- 一阶线性方程：O(1)（套公式）
- 常系数线性方程：O(n)（n 为阶数，求特征根）

数值求解的复杂度（每步）：
- 欧拉法：O(1)
- 改进欧拉法：O(1)
- RK4：O(1)（4 次函数求值）
- 刚性方程隐式方法：O(n³)（需解线性方程组）

## 实现示例 (Implementation)

```python
import numpy as np
import sympy as sp
from sympy import symbols, Function, dsolve, Eq, exp, sin, cos, sqrt
from scipy.integrate import odeint, solve_ivp
import matplotlib.pyplot as plt

# 符号求解
x = symbols('x')
y = Function('y')

# 一阶线性方程：y' + y = 0
eq = Eq(y(x).diff(x) + y(x), 0)
solution = dsolve(eq, y(x))
print(f"y' + y = 0 的解: {solution}")  # y = C1*exp(-x)

# 二阶常系数：y'' + y = 0
eq = Eq(y(x).diff(x, 2) + y(x), 0)
solution = dsolve(eq, y(x))
print(f"y'' + y = 0 的解: {solution}")  # y = C1*sin(x) + C2*cos(x)

# 带初值条件
eq = Eq(y(x).diff(x), y(x))
ics = {y(0): 1}
solution = dsolve(eq, y(x), ics=ics)
print(f"y' = y, y(0)=1 的解: {solution}")  # y = exp(x)

# 数值求解 - 简单 ODE
def exponential_decay(y, t, k):
    """指数衰减：dy/dt = -ky"""
    return -k * y

k = 0.5
y0 = [1.0]
t = np.linspace(0, 10, 100)
solution = odeint(exponential_decay, y0, t, args=(k,))

# 解析解：y = e^(-kt)
analytical = np.exp(-k * t)
print(f"数值解与解析解的最大误差: {np.max(np.abs(solution.flatten() - analytical)):.2e}")

# 使用 solve_ivp（更现代的接口）
def decay_system(t, y):
    return [-0.5 * y[0]]

sol = solve_ivp(decay_system, [0, 10], [1.0], t_eval=t, method='RK45')

# 二阶 ODE 转化为一阶方程组
# y'' = -y，令 z = y'，则：
# y' = z
# z' = -y

def harmonic_oscillator(t, state):
    """简谐振子"""
    y, z = state
    return [z, -y]

y0 = [1.0, 0.0]  # y(0)=1, y'(0)=0
t_span = [0, 4*np.pi]
t_eval = np.linspace(0, 4*np.pi, 1000)

sol = solve_ivp(harmonic_oscillator, t_span, y0, t_eval=t_eval, method='RK45')

# 解析解：y = cos(t)
analytical = np.cos(t_eval)
print(f"简谐振子数值误差: {np.max(np.abs(sol.y[0] - analytical)):.2e}")

# 龙格-库塔法手动实现
def rk4_step(f, t, y, h):
    """RK4 单步"""
    k1 = f(t, y)
    k2 = f(t + h/2, y + h*k1/2)
    k3 = f(t + h/2, y + h*k2/2)
    k4 = f(t + h, y + h*k3)
    return y + h/6 * (k1 + 2*k2 + 2*k3 + k4)

def solve_rk4(f, y0, t_span, h=0.01):
    """RK4 求解器"""
    t0, tf = t_span
    t = np.arange(t0, tf + h, h)
    y = np.zeros((len(t), len(y0) if hasattr(y0, '__len__') else 1))
    y[0] = y0
    
    for i in range(len(t) - 1):
        y[i+1] = rk4_step(f, t[i], y[i], h)
    
    return t, y

# 测试 RK4
f = lambda t, y: -0.5 * y
t_rk4, y_rk4 = solve_rk4(f, [1.0], [0, 10], h=0.1)
analytical_rk4 = np.exp(-0.5 * t_rk4)
print(f"RK4 误差: {np.max(np.abs(y_rk4.flatten() - analytical_rk4)):.2e}")

# 阻尼振动系统
def damped_oscillator(t, state, omega0, zeta):
    """
    阻尼振动系统
    state = [x, v]（位移和速度）
    omega0：固有频率
    zeta：阻尼比
    """
    x, v = state
    dxdt = v
    dvdt = -2*zeta*omega0*v - omega0**2*x
    return [dxdt, dvdt]

# 不同阻尼情况的比较
t_eval = np.linspace(0, 20, 1000)
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
zetas = [0.1, 0.5, 1.0, 2.0]
titles = ['Underdamped', 'Underdamped', 'Critically Damped', 'Overdamped']

for i, (zeta, title) in enumerate(zip(zetas, titles)):
    ax = axes[i//2, i%2]
    sol = solve_ivp(lambda t, y: damped_oscillator(t, y, 1.0, zeta), 
                   [0, 20], [1.0, 0.0], t_eval=t_eval)
    ax.plot(t_eval, sol.y[0])
    ax.set_title(f'{title} (ζ={zeta})')
    ax.set_xlabel('t')
    ax.set_ylabel('x')
    ax.grid(True)

plt.tight_layout()
plt.savefig('damped_oscillator.png')
plt.close()
print("阻尼振动图像已保存")

# 种群动力学模型（Lotka-Volterra）
def lotka_volterra(t, state, alpha, beta, gamma, delta):
    """
    捕食者-猎物模型
    state = [prey, predator]
    """
    x, y = state
    dxdt = alpha*x - beta*x*y
    dydt = delta*x*y - gamma*y
    return [dxdt, dydt]

# 参数
alpha, beta, gamma, delta = 1.0, 0.1, 1.5, 0.075

# 初始条件（猎物，捕食者）
state0 = [10.0, 5.0]
t_span = [0, 15]
t_eval = np.linspace(0, 15, 1000)

sol = solve_ivp(lambda t, y: lotka_volterra(t, y, alpha, beta, gamma, delta),
               t_span, state0, t_eval=t_eval, method='RK45')

# 相图（Phase Portrait）
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.plot(sol.y[0], sol.y[1])
plt.xlabel('Prey')
plt.ylabel('Predator')
plt.title('Phase Portrait')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(sol.t, sol.y[0], label='Prey')
plt.plot(sol.t, sol.y[1], label='Predator')
plt.xlabel('Time')
plt.ylabel('Population')
plt.title('Population vs Time')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('lotka_volterra.png')
plt.close()
print("Lotka-Volterra 图像已保存")

# 机器学习中的应用：神经网络 ODE（Neural ODE）
def neural_ode_simple(t, h, params):
    """
    简化版神经网络 ODE
    dh/dt = f(h, t, θ)
    这里用一个简单的线性变换作为示例
    """
    W, b = params
    return np.tanh(W @ h + b)

# 示例参数
W = np.array([[0.1, -0.2], [0.3, 0.4]])
b = np.array([0.1, -0.1])
params = (W, b)

h0 = np.array([1.0, 0.5])
t_eval = np.linspace(0, 5, 100)

sol = solve_ivp(lambda t, h: neural_ode_simple(t, h, params), 
               [0, 5], h0, t_eval=t_eval, method='RK45')

print(f"Neural ODE 最终状态: {sol.y[:, -1]}")

# 物理仿真：抛体运动
def projectile_motion(t, state, g=9.81, Cd=0.0, rho=1.225, A=0.01, m=1.0):
    """
    考虑空气阻力的抛体运动
    state = [x, y, vx, vy]
    """
    x, y, vx, vy = state
    v = np.sqrt(vx**2 + vy**2)
    
    # 阻力
    Fd = 0.5 * rho * v**2 * Cd * A
    Fdx = -Fd * vx / v if v > 0 else 0
    Fdy = -Fd * vy / v if v > 0 else 0
    
    dxdt = vx
    dydt = vy
    dvxdt = Fdx / m
    dvydt = -g + Fdy / m
    
    return [dxdt, dydt, dvxdt, dvydt]

# 初始条件：v0 = 50 m/s，角度 45 度
v0 = 50
angle = np.pi / 4
state0 = [0, 0, v0*np.cos(angle), v0*np.sin(angle)]

# 无阻力
sol_no_drag = solve_ivp(lambda t, y: projectile_motion(t, y, Cd=0.0),
                       [0, 10], state0, t_eval=np.linspace(0, 7, 1000),
                       events=lambda t, y: y[1])  # 当 y=0 时停止

# 有阻力
sol_with_drag = solve_ivp(lambda t, y: projectile_motion(t, y, Cd=0.5),
                         [0, 10], state0, t_eval=np.linspace(0, 5, 1000),
                         events=lambda t, y: y[1])

print(f"无阻力射程: {sol_no_drag.y[0][-1]:.2f} m")
print(f"有阻力射程: {sol_with_drag.y[0][-1]:.2f} m")

# 稳定性分析（数值稳定性）
def stability_analysis():
    """分析不同方法的稳定性"""
    # 刚性方程：y' = -1000y
    # 精确解：y = exp(-1000t)
    
    def stiff_eq(t, y):
        return -1000 * y
    
    y0 = [1.0]
    t_span = [0, 0.01]
    
    # 显式方法需要很小的步长
    try:
        sol_explicit = solve_ivp(stiff_eq, t_span, y0, method='RK45')
        print(f"RK45 步数: {len(sol_explicit.t)}")
    except:
        print("RK45 失败")
    
    # 隐式方法更适合刚性方程
    sol_implicit = solve_ivp(stiff_eq, t_span, y0, method='Radau')
    print(f"Radau（隐式）步数: {len(sol_implicit.t)}")
    
    return sol_explicit, sol_implicit

# stability_analysis()
```

## 应用场景 (Applications)

- **物理学**：牛顿运动定律、电路分析、振动系统、热传导
- **化学**：反应动力学、扩散过程
- **生物学**：种群动力学、流行病学模型（SIR 模型）、神经网络
- **经济学**：经济增长模型、期权定价（Black-Scholes 方程）
- **工程学**：控制系统、结构分析、信号处理
- **机器学习**：
  - Neural ODE：将神经网络视为连续动态系统
  - 残差网络（ResNet）与 ODE 的联系
  - 连续归一化流（Continuous Normalizing Flows）
- **计算机图形学**：物理仿真、粒子系统、流体模拟
- **天气预测**：大气动力学方程组

## 面试要点 (Interview Questions)

**Q1: 常微分方程和偏微分方程有什么区别？**
> 常微分方程（ODE）只有一个自变量（通常是时间 t），未知函数是一元函数；偏微分方程（PDE）有多个自变量（如时间和空间），未知函数是多元函数，含有偏导数。ODE 相对容易求解，PDE 通常需要数值方法或特殊技巧。

**Q2: 如何求解一阶线性微分方程？**
> 标准形式：y' + P(x)y = Q(x)。解法有两种：1）积分因子法：乘以 e^(∫Pdx)，左边变为 (ye^(∫Pdx))'；2）常数变易法：先求齐次方程解 y_h = Ce^(-∫Pdx)，再设特解 y_p = C(x)e^(-∫Pdx) 代入求 C(x)。

**Q3: 二阶常系数线性微分方程的通解结构是什么？**
> 通解 = 齐次通解 + 非齐次特解。齐次通解由特征方程的根决定：不等实根 r₁,r₂ 对应 C₁e^(r₁x)+C₂e^(r₂x)；重根 r 对应 (C₁+C₂x)e^(rx)；共轭复根 α±βi 对应 e^(αx)(C₁cosβx+C₂sinβx)。

**Q4: 什么是龙格-库塔法？为什么比欧拉法好？**
> RK4 是一种四阶数值方法，通过计算 4 个点上的斜率加权平均来更新解。局部截断误差为 O(h⁵)，全局误差 O(h⁴)。相比欧拉法（一阶，O(h)），RK4 精度更高，允许使用更大的步长，计算效率更好。

**Q5: 微分方程在机器学习中有哪些应用？**
> 1）Neural ODE：将神经网络层间变换视为连续 ODE，用 ODE 求解器进行前向和后向传播；2）残差网络可看作欧拉离散化的 ODE；3）连续归一化流使用 ODE 建模概率分布变换；4）神经常微分方程在时序建模和生成模型中有应用。

## 相关概念 (Related Concepts)

- [极限与连续](./limits-continuity.md) - 解的存在性理论基础
- [导数](./derivatives.md) - 微分方程的核心组成
- [积分](./integrals.md) - 求解微分方程的基本工具
- [多元微积分](./multivariable-calculus.md) - 偏微分方程的基础
- [线性代数](../linear-algebra.md) - 线性微分方程组的矩阵表示
- [概率论](../probability.md) - 随机微分方程
- [神经网络](../../ai-data-systems/nn-basics.md) - Neural ODE
- [优化理论](../../ai-data-systems/ml-overview.md) - 动力系统视角

## 参考资料 (References)

- 《常微分方程》丁同仁、李承治
- 《Partial Differential Equations for Scientists and Engineers》Stanley J. Farlow
- 《Neural Ordinary Differential Equations》（NeurIPS 2018 Best Paper）
- MIT OpenCourseWare 18.03 Differential Equations
- SciPy Documentation（integrate.odeint, integrate.solve_ivp）
