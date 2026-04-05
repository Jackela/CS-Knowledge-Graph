# 多元微积分 (Multivariable Calculus)

**多元微积分 (Multivariable Calculus)** 研究多元函数的微分和积分，将单变量微积分的概念推广到多变量情形。它是物理学、工程学和机器学习中的重要数学工具。

## 原理 (Principles)

### 多元函数的极限与连续

```
二元函数极限的定义：

lim f(x,y) = L  ⟺  ∀ε > 0, ∃δ > 0，当 0 < √[(x-x₀)² + (y-y₀)²] < δ 时，
(x,y)→(x₀,y₀)

|f(x,y) - L| < ε

注意：极限存在要求沿所有路径趋近时极限都相同
```

**连续性：**
```
f(x,y) 在 (x₀,y₀) 连续 ⟺ lim f(x,y) = f(x₀,y₀)
                          (x,y)→(x₀,y₀)
```

### 偏导数

```
偏导数定义：

∂f/∂x = lim [f(x+h, y) - f(x, y)] / h
       h→0

∂f/∂y = lim [f(x, y+h) - f(x, y)] / h
       h→0

几何意义：沿坐标轴方向的变化率
```

**高阶偏导数：**
```
∂²f/∂x², ∂²f/∂y², ∂²f/∂x∂y, ∂²f/∂y∂x

施瓦茨定理：若二阶混合偏导数连续，则：
∂²f/∂x∂y = ∂²f/∂y∂x
```

### 全微分

```
全微分定义：

df = (∂f/∂x)dx + (∂f/∂y)dy

或：Δf ≈ (∂f/∂x)Δx + (∂f/∂y)Δy

可微的充分条件：偏导数存在且连续
```

### 方向导数与梯度

```
方向导数（沿单位向量 u = (cos α, sin α)）：

∂f/∂u = (∂f/∂x)cos α + (∂f/∂y)sin α

梯度（Gradient）：
∇f = (∂f/∂x, ∂f/∂y)

方向导数与梯度的关系：
∂f/∂u = ∇f · u = |∇f| cos θ

最大变化率：|∇f|（沿梯度方向）
```

### 多元复合函数求导

```
链式法则（一元复合）：
若 z = f(x,y)，x = φ(t)，y = ψ(t)

dz/dt = (∂z/∂x)(dx/dt) + (∂z/∂y)(dy/dt)

链式法则（多元复合）：
若 z = f(u,v)，u = u(x,y)，v = v(x,y)

∂z/∂x = (∂z/∂u)(∂u/∂x) + (∂z/∂v)(∂v/∂x)
∂z/∂y = (∂z/∂u)(∂u/∂y) + (∂z/∂v)(∂v/∂y)
```

### 隐函数求导

```
由 F(x,y,z) = 0 确定的隐函数 z = z(x,y)：

∂z/∂x = -(∂F/∂x) / (∂F/∂z)
∂z/∂y = -(∂F/∂y) / (∂F/∂z)

要求 ∂F/∂z ≠ 0
```

### 多元函数的极值

**无条件极值：**
```
必要条件（驻点）：
∂f/∂x = 0，∂f/∂y = 0

充分条件：
设 A = ∂²f/∂x², B = ∂²f/∂x∂y, C = ∂²f/∂y²
判别式 Δ = AC - B²

- Δ > 0 且 A > 0：极小值
- Δ > 0 且 A < 0：极大值
- Δ < 0：鞍点
- Δ = 0：无法判断
```

**条件极值（拉格朗日乘数法）：**
```
求 f(x,y) 在约束 g(x,y) = 0 下的极值：

构造拉格朗日函数：
L(x,y,λ) = f(x,y) - λg(x,y)

解方程组：
∂L/∂x = 0
∂L/∂y = 0
∂L/∂λ = 0  （即 g(x,y) = 0）
```

### 多重积分

**二重积分：**
```
∬_D f(x,y) dσ = lim Σ f(ξᵢ, ηᵢ)Δσᵢ
               λ→0

直角坐标：dσ = dx dy
极坐标：dσ = r dr dθ

计算：化为累次积分
∬_D f(x,y) dxdy = ∫ₐᵇ dx ∫ᵩ₁₍ₓ₎ᵩ₂₍ₓ₎ f(x,y) dy
```

**三重积分：**
```
∭_Ω f(x,y,z) dV

直角坐标：dV = dx dy dz
柱坐标：dV = r dr dθ dz
球坐标：dV = r² sin φ dr dθ dφ
```

### 曲线积分与曲面积分

**第一类曲线积分（对弧长）：**
```
∫_L f(x,y) ds

计算：若 L: x=φ(t), y=ψ(t), a≤t≤b
∫_L f(x,y) ds = ∫ₐᵇ f(φ(t),ψ(t))√[φ'(t)² + ψ'(t)²] dt
```

**第二类曲线积分（对坐标）：**
```
∫_L P(x,y)dx + Q(x,y)dy

格林公式（平面）：
∮_L Pdx + Qdy = ∬_D (∂Q/∂x - ∂P/∂y) dxdy

D 是 L 围成的区域，L 取正向
```

**斯托克斯公式：**
```
∮_Γ Pdx + Qdy + Rdz = ∬_Σ (∇ × F) · dS

其中 F = (P, Q, R)，∇ × F 是旋度
```

**高斯公式（散度定理）：**
```
∭_Ω (∂P/∂x + ∂Q/∂y + ∂R/∂z) dV = ∯_Σ (Pdy dz + Qdz dx + Rdx dy)

或：∭_Ω ∇ · F dV = ∯_Σ F · n dS
```

### 场论初步

**梯度场：**
```
梯度：∇f = (∂f/∂x, ∂f/∂y, ∂f/∂z)

性质：
- 指向函数增长最快的方向
- 大小等于最大变化率
- 等值面的法向量
```

**散度：**
```
∇ · F = ∂P/∂x + ∂Q/∂y + ∂R/∂z

物理意义：单位体积内通量的发散程度
```

**旋度：**
```
     | i     j     k    |
∇ × F = | ∂/∂x  ∂/∂y  ∂/∂z |
     | P     Q     R    |\n
物理意义：流体在某点的旋转程度
```

## 关键性质

- **可微性蕴含连续性**：若函数可微，则必连续
- **偏导数存在不一定可微**：偏导数存在且连续才可微
- **混合偏导数相等**：在一定条件下，求导顺序可交换
- **梯度正交于等值面**：梯度方向是等值面的法线方向
- **保守场判别**：旋度为零的向量场是保守场

## 复杂度分析 (Complexity Analysis)

多元微积分计算的复杂度：
- 偏导数计算：O(n)（n 为变量数）
- 梯度计算：O(n)（对每个变量求偏导）
- 雅可比矩阵计算：O(mn)（m 个函数，n 个变量）
- 二重数值积分：O(n²)（n 为每维分割数）
- 多重数值积分：O(nᵈ)（d 为维数，维数灾难）

蒙特卡洛积分在高维的优势：
- 传统网格法：O(nᵈ)
- 蒙特卡洛：O(n)（与维数无关，误差 O(1/√n)）

## 实现示例 (Implementation)

```python
import numpy as np
import sympy as sp
from sympy import symbols, diff, integrate, cos, sin, exp, sqrt
from scipy import integrate as sci_integrate
from scipy.optimize import minimize

# 符号计算
x, y, z = symbols('x y z')

# 偏导数
f = x**2 * y + y**3 * sin(x)
df_dx = diff(f, x)
df_dy = diff(f, y)
print(f"∂f/∂x = {df_dx}")
print(f"∂f/∂y = {df_dy}")

# 高阶偏导数
d2f_dxdy = diff(f, x, y)
print(f"∂²f/∂x∂y = {d2f_dxdy}")

# 梯度计算
def gradient(f, vars):
    """计算函数 f 关于 vars 的梯度"""
    return [diff(f, var) for var in vars]

f = x**2 + y**2
grad = gradient(f, [x, y])
print(f"∇f = {grad}")  # [2x, 2y]

# 方向导数
def directional_derivative(f, point, direction, vars):
    """
    计算方向导数
    f: 函数
    point: 点坐标
    direction: 方向向量（会被归一化）
    vars: 变量列表
    """
    grad = [diff(f, var) for var in vars]
    
    # 归一化方向向量
    direction = np.array(direction, dtype=float)
    direction = direction / np.linalg.norm(direction)
    
    # 计算梯度在点的值
    subs = {var: val for var, val in zip(vars, point)}
    grad_val = np.array([g.subs(subs) for g in grad], dtype=float)
    
    return np.dot(grad_val, direction)

# 示例：f(x,y) = x² + y² 在 (1,1) 沿 (1,1) 方向的方向导数
f = x**2 + y**2
dd = directional_derivative(f, [1, 1], [1, 1], [x, y])
print(f"方向导数 = {dd:.4f}")

# 链式法则示例
# z = x² + y², x = t, y = t²
t = symbols('t')
x_t = t
y_t = t**2
z = x_t**2 + y_t**2
dz_dt = diff(z, t)
print(f"dz/dt = {dz_dt}")  # 2t + 4t³

# 二重积分
f = x * y
result = integrate(integrate(f, (y, 0, x)), (x, 0, 1))
print(f"∫₀¹∫₀ˣ xy dy dx = {result}")  # 1/8

# 极坐标下的积分
r, theta = symbols('r theta', positive=True)
f_polar = r**2  # x² + y² = r²，雅可比行列式为 r
result = integrate(integrate(f_polar * r, (r, 0, 1)), (theta, 0, 2*sp.pi))
print(f"圆域上 ∬(x²+y²) dxdy = {result}")  # π/2

# 数值二重积分
def integrand(y, x):
    return x * y

result, error = sci_integrate.dblquad(integrand, 0, 1, lambda x: 0, lambda x: x)
print(f"数值二重积分结果: {result:.6f}")

# 梯度下降优化（多元）
def gradient_descent_2d(f_func, grad_func, x0, lr=0.1, epochs=100):
    """
    二元函数的梯度下降
    f_func: 目标函数
    grad_func: 梯度函数，返回 [∂f/∂x, ∂f/∂y]
    x0: 初始点 [x, y]
    """
    x = np.array(x0, dtype=float)
    history = [x.copy()]
    
    for _ in range(epochs):
        grad = np.array(grad_func(x[0], x[1]))
        x = x - lr * grad
        history.append(x.copy())
    
    return x, history

# 最小化 f(x,y) = x² + 2y²
f_func = lambda x, y: x**2 + 2*y**2
grad_func = lambda x, y: [2*x, 4*y]

minimum, history = gradient_descent_2d(f_func, grad_func, [5, 5], lr=0.1, epochs=50)
print(f"最小值点: ({minimum[0]:.4f}, {minimum[1]:.4f})")

# 使用 scipy 优化
result = minimize(lambda xy: xy[0]**2 + 2*xy[1]**2, [5, 5], method='BFGS')
print(f"scipy 优化结果: {result.x}")

# 拉格朗日乘数法（使用 scipy 的约束优化）
def objective(xy):
    return xy[0]**2 + xy[1]**2  # 最小化 x² + y²

def constraint(xy):
    return xy[0] + xy[1] - 1  # 约束: x + y = 1

cons = {'type': 'eq', 'fun': constraint}
result = minimize(objective, [0.5, 0.5], method='SLSQP', constraints=cons)
print(f"约束优化解: x={result.x[0]:.4f}, y={result.x[1]:.4f}")

# 雅可比矩阵
def jacobian(f_vec, vars):
    """
    计算雅可比矩阵
    f_vec: 函数向量 [f₁, f₂, ...]
    vars: 变量列表
    """
    return [[diff(f, var) for var in vars] for f in f_vec]

f1 = x**2 + y**2
f2 = x * y
J = jacobian([f1, f2], [x, y])
print(f"雅可比矩阵:\n{J}")

# 数值梯度计算
def numerical_gradient(f, point, h=1e-5):
    """数值方法计算梯度"""
    point = np.array(point, dtype=float)
    n = len(point)
    grad = np.zeros(n)
    
    for i in range(n):
        point_plus = point.copy()
        point_minus = point.copy()
        point_plus[i] += h
        point_minus[i] -= h
        grad[i] = (f(point_plus) - f(point_minus)) / (2 * h)
    
    return grad

# 示例
f = lambda xy: xy[0]**2 + xy[1]**2
grad_num = numerical_gradient(f, [1.0, 2.0])
print(f"数值梯度: {grad_num}")  # 接近 [2, 4]

# 三维可视化
def plot_gradient_field():
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        
        # 创建网格
        x = np.linspace(-2, 2, 20)
        y = np.linspace(-2, 2, 20)
        X, Y = np.meshgrid(x, y)
        
        # 函数 f(x,y) = x² + y²
        Z = X**2 + Y**2
        
        # 梯度场
        U = 2*X
        V = 2*Y
        
        fig = plt.figure(figsize=(12, 5))
        
        # 3D 曲面
        ax1 = fig.add_subplot(121, projection='3d')
        ax1.plot_surface(X, Y, Z, alpha=0.7, cmap='viridis')
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')
        ax1.set_zlabel('z')
        ax1.set_title('f(x,y) = x² + y²')
        
        # 等高线和梯度场
        ax2 = fig.add_subplot(122)
        contour = ax2.contour(X, Y, Z, levels=10)
        ax2.clabel(contour)
        ax2.quiver(X[::2, ::2], Y[::2, ::2], 
                  U[::2, ::2], V[::2, ::2], alpha=0.6)
        ax2.set_xlabel('x')
        ax2.set_ylabel('y')
        ax2.set_title('Contour and Gradient Field')
        ax2.set_aspect('equal')
        
        plt.tight_layout()
        plt.savefig('multivariable_calculus.png')
        plt.close()
        print("图像已保存")
    except ImportError:
        print("matplotlib 未安装")

# plot_gradient_field()
```

## 应用场景 (Applications)

- **机器学习**：梯度下降优化、反向传播、雅可比矩阵
- **物理学**：热传导方程、波动方程、电磁场理论
- **计算机图形学**：曲面渲染、光照模型、物理模拟
- **经济学**：多变量优化、生产函数分析
- **工程学**：结构分析、流体力学、热力学
- **数据科学**：主成分分析（PCA）、多变量统计
- **机器人学**：运动学、路径规划
- **图像处理**：图像梯度、边缘检测

## 面试要点 (Interview Questions)

**Q1: 偏导数和方向导数有什么区别？**
> 偏导数是沿坐标轴方向的导数（如 ∂f/∂x 是沿 x 轴方向）；方向导数是沿任意方向的导数。方向导数可以用梯度表示：∂f/∂u = ∇f · u，其中 u 是单位方向向量。

**Q2: 梯度有什么几何意义？**
> 梯度 ∇f 指向函数增长最快的方向，其大小等于最大增长率。梯度垂直于等值面（或等值线），是等值面的法向量。沿梯度方向移动，函数值增加最快；沿负梯度方向移动，函数值减小最快（梯度下降的基础）。

**Q3: 什么是拉格朗日乘数法？**
> 拉格朗日乘数法用于求解带约束条件的极值问题。通过引入拉格朗日乘子 λ，将有约束问题转化为无约束问题。构造拉格朗日函数 L = f - λg，其中 g(x)=0 是约束条件。极值点满足 ∂L/∂x = 0，∂L/∂y = 0，∂L/∂λ = 0。

**Q4: 格林公式、斯托克斯公式、高斯公式的物理意义是什么？**
> 格林公式：平面上的曲线积分与二重积分的联系，表示环流与旋度的关系。斯托克斯公式：空间曲线积分与曲面积分的联系，推广了格林公式。高斯公式（散度定理）：体积分与面积分的联系，表示通量与散度的关系。这三个公式统一了微分和积分的关系。

**Q5: 为什么在高维空间中蒙特卡洛积分比传统方法更有效？**
> 传统网格法的误差为 O(n^(-2/d))，其中 d 是维数；蒙特卡洛法的误差为 O(1/√n)，与维数无关。当 d > 4 时，要达到相同精度，蒙特卡洛所需的样本数远少于网格点数量，这称为"维数灾难"的克服。

## 相关概念 (Related Concepts)

- [极限与连续](./limits-continuity.md) - 多元函数极限的基础
- [导数](./derivatives.md) - 偏导数是单变量导数的推广
- [积分](./integrals.md) - 重积分的计算基础
- [微分方程](./differential-equations.md) - 偏微分方程
- [线性代数](../linear-algebra.md) - 雅可比矩阵、海森矩阵
- [优化理论](../../ai-data-systems/ml-overview.md) - 多元优化算法
- [神经网络](../../ai-data-systems/cnn.md) - 反向传播中的梯度计算

## 参考资料 (References)

- 《高等数学》同济大学数学系（多元函数微积分部分）
- 《数学分析》华东师范大学数学系
- 3Blue1Brown《微积分的本质》系列（YouTube）
- MIT OpenCourseWare 18.02 Multivariable Calculus
- 《Deep Learning》Goodfellow et al.（优化章节）
