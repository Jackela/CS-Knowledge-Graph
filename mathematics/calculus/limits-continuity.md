# 极限与连续 (Limits and Continuity)

**极限 (Limit)** 是微积分的基础概念，描述函数在某一点附近的行为趋势。**连续性 (Continuity)** 则描述函数图像无间断、可一笔画出的性质。这两个概念构成了微积分的严格数学基础。

## 原理 (Principles)

### 极限的定义

```
函数极限的 ε-δ 定义：

lim f(x) = L  ⟺  ∀ε > 0, ∃δ > 0, 当 0 < |x - a| < δ 时，|f(x) - L| < ε
x→a

直观理解：当 x 无限接近 a 时，f(x) 无限接近 L
```

**单侧极限：**
- 左极限：lim f(x) = L⁻ (x 从左侧趋近 a)
      x→a⁻
- 右极限：lim f(x) = L⁺ (x 从右侧趋近 a)
      x→a⁺
- 极限存在：当且仅当 L⁻ = L⁺

### 极限运算法则

```
若 lim f(x) = L，lim g(x) = M
    x→a        x→a

则：
1. 和差：lim [f(x) ± g(x)] = L ± M
        x→a
2. 积：lim [f(x) × g(x)] = L × M
       x→a
3. 商：lim [f(x) / g(x)] = L / M  (M ≠ 0)
       x→a
4. 幂：lim [f(x)]ⁿ = Lⁿ
       x→a
```

### 重要极限

```
基本极限：

1. lim (sin x) / x = 1
   x→0

2. lim (1 + 1/x)ˣ = e  或  lim (1 + x)^(1/x) = e
   x→∞                      x→0

3. lim (eˣ - 1) / x = 1
   x→0

4. lim ln(1 + x) / x = 1
   x→0

5. lim (aˣ - 1) / x = ln(a)
   x→0
```

### 无穷小与无穷大

```
无穷小：极限为 0 的变量
无穷大：绝对值无限增大的变量

无穷小的比较：
- 高阶无穷小：lim α/β = 0，记作 α = o(β)
- 同阶无穷小：lim α/β = C ≠ 0
- 等价无穷小：lim α/β = 1，记作 α ~ β

常用等价无穷小（x→0）：
- sin x ~ x
- tan x ~ x
- arcsin x ~ x
- arctan x ~ x
- eˣ - 1 ~ x
- ln(1 + x) ~ x
- (1 + x)ᵃ - 1 ~ ax
- 1 - cos x ~ x²/2
```

### 连续性

```
函数 f(x) 在点 a 连续的定义：

1. f(a) 有定义
2. lim f(x) 存在
   x→a
3. lim f(x) = f(a)
   x→a

等价表述：lim [f(x) - f(a)] = 0  或  lim Δy = 0
        x→a                          Δx→0
```

**间断点分类：**

```
第一类间断点（左右极限都存在）：
- 可去间断点：左右极限相等但不等于函数值
- 跳跃间断点：左右极限不相等

第二类间断点（至少一侧极限不存在）：
- 无穷间断点：极限为无穷大
- 振荡间断点：极限不存在且不趋于无穷
```

### 闭区间上连续函数的性质

```
1. 有界性定理：闭区间上的连续函数必有界

2. 最值定理：闭区间上的连续函数必存在最大值和最小值

3. 介值定理：若 f 在 [a,b] 连续，f(a) ≠ f(b)，
   则对任意 μ 介于 f(a) 和 f(b) 之间，存在 c ∈ (a,b) 使 f(c) = μ

4. 零点定理：若 f 在 [a,b] 连续，f(a)f(b) < 0，
   则存在 c ∈ (a,b) 使 f(c) = 0
```

## 关键性质

- **唯一性**：若极限存在，则极限值唯一
- **局部有界性**：若极限存在，则函数在该点的某去心邻域内有界
- **保号性**：若 lim f(x) = L > 0，则存在邻域使 f(x) > 0
- **夹逼定理**：若 g(x) ≤ f(x) ≤ h(x) 且 lim g(x) = lim h(x) = L，则 lim f(x) = L
- **连续性运算**：连续函数的和、差、积、商（分母非零）仍连续

## 复杂度分析 (Complexity Analysis)

极限计算的时间复杂度：
- 直接代入法：O(1)
- 因式分解法：O(n)（n 为多项式次数）
- 洛必达法则：O(k)（k 为求导次数）
- 泰勒展开法：O(m)（m 为展开项数）

## 实现示例 (Implementation)

```python
import numpy as np
import sympy as sp

# 使用 sympy 计算极限
x = sp.Symbol('x')

# 基本极限
f1 = sp.sin(x) / x
limit1 = sp.limit(f1, x, 0)
print(f"lim sin(x)/x (x→0) = {limit1}")  # 1

# 重要极限 e
f2 = (1 + 1/x)**x
limit2 = sp.limit(f2, x, sp.oo)
print(f"lim (1+1/x)^x (x→∞) = {limit2}")  # e

# 无穷小阶数比较
f3 = (sp.exp(x) - 1) / x
limit3 = sp.limit(f3, x, 0)
print(f"lim (e^x-1)/x (x→0) = {limit3}")  # 1，说明 e^x-1 ~ x

# 连续性检查
def is_continuous_at(f, a, epsilon=1e-6):
    """检查函数在点 a 是否连续"""
    try:
        left_limit = f(a - epsilon)
        right_limit = f(a + epsilon)
        func_value = f(a)
        
        return (abs(left_limit - func_value) < epsilon and 
                abs(right_limit - func_value) < epsilon)
    except:
        return False

# 示例：检查 f(x) = x² 在 x=2 处的连续性
f = lambda x: x**2
print(f"f(x)=x² 在 x=2 连续？{is_continuous_at(f, 2)}")  # True

# 数值逼近极限
def numerical_limit(f, a, h=1e-7):
    """数值方法近似计算极限"""
    return (f(a + h) - f(a - h)) / (2 * h) if a != 0 else f(h)

# 验证 sin(x)/x 在 x=0 的极限
result = numerical_limit(lambda x: np.sin(x)/x if x != 0 else 1, 0)
print(f"数值极限结果: {result}")  # 接近 1.0
```

## 应用场景 (Applications)

- **瞬时速度**：v = lim (Δs/Δt)，导数的前身
           Δt→0
- **曲线切线**：切线斜率是割线斜率的极限
- **面积计算**：曲边梯形面积是矩形面积和的极限
- **复利计算**：连续复利 A = Pe^(rt)
- **物理中的瞬时量**：瞬时电流、瞬时功率等
- **机器学习**：梯度下降中步长的选择涉及极限思想
- **数值分析**：迭代算法的收敛性分析

## 面试要点 (Interview Questions)

**Q1: 什么是 ε-δ 定义？它的直观含义是什么？**
> ε-δ 定义是极限的严格数学定义：对于任意小的误差 ε，总能找到一个范围 δ，使得当 x 与 a 的距离小于 δ（但不等于 a）时，f(x) 与 L 的距离小于 ε。直观含义是 x 越接近 a，f(x) 就越接近 L。

**Q2: 两个重要极限是什么？如何证明？**
> 1) lim(sin x)/x = 1 (x→0)：可用夹逼定理，利用单位圆中三角形和扇形面积关系证明。
> 2) lim(1+1/x)ˣ = e (x→∞)：可用单调有界原理证明数列 {(1+1/n)ⁿ} 收敛。

**Q3: 函数在某点连续的三个条件是什么？**
> 1) 函数在该点有定义；2) 函数在该点的极限存在；3) 极限值等于函数值。三者缺一不可。

**Q4: 间断点有哪些类型？举例说明。**
> 第一类间断点：可去间断点（如 f(x)=sinx/x 在 x=0）和跳跃间断点（如符号函数在 x=0）。
> 第二类间断点：无穷间断点（如 1/x 在 x=0）和振荡间断点（如 sin(1/x) 在 x=0）。

**Q5: 介值定理有什么应用？**
> 介值定理可用于证明方程根的存在性（零点定理），二分法求根的理论基础，以及证明某些函数必取到某个值。例如证明奇数次多项式必有实根。

## 相关概念 (Related Concepts)

- [导数](./derivatives.md) - 极限在变化率上的应用
- [积分](./integrals.md) - 极限在求和上的应用
- [多元微积分](./multivariable-calculus.md) - 多元函数的极限与连续性
- [微分方程](./differential-equations.md) - 涉及极限的渐近行为分析
- [概率论](../probability.md) - 大数定律、中心极限定理中的极限
- [机器学习概述](../../ai-data-systems/ml-overview.md) - 梯度下降的收敛性

## 参考资料 (References)

- 《高等数学》同济大学数学系
- 《数学分析》华东师范大学数学系
- 3Blue1Brown《微积分的本质》系列（YouTube）
- Khan Academy Calculus
- MIT OpenCourseWare 18.01 Single Variable Calculus
