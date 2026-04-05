# 最大公约数 (Greatest Common Divisor - GCD)

## 简介

**最大公约数**（Greatest Common Divisor，GCD）和**最小公倍数**（Least Common Multiple，LCM）是数论中的基础概念。欧几里得算法（辗转相除法）是计算 GCD 的高效方法，时间复杂度为 O(log min(a,b))，广泛应用于分数化简、模逆元、线性丢番图方程求解等问题。

## 核心概念

### 欧几里得算法

**原理：**
```
gcd(a, b) = gcd(b, a mod b)
直到 b = 0，此时 gcd = a
```

**数学证明：**
- 设 d = gcd(a, b)，则 d|a 且 d|b
- a = bq + r，所以 r = a - bq
- d|r，因此 d 也是 b 和 r 的公约数
- 反之亦然，所以 gcd(a,b) = gcd(b,r)

**时间复杂度：** O(log min(a,b))

### 扩展欧几里得算法

**求解：** 找到 x, y 使得 ax + by = gcd(a,b)

**递归关系：**
```
若 gcd(b, a%b) = b·x' + (a%b)·y'
则 a·x + b·y = b·x' + (a - ⌊a/b⌋·b)·y'
            = a·y' + b·(x' - ⌊a/b⌋·y')
所以 x = y', y = x' - ⌊a/b⌋·y'
```

### LCM 计算

**公式：**
```
lcm(a, b) = |a × b| / gcd(a, b)
```

**多个数的 LCM：**
```
lcm(a, b, c) = lcm(lcm(a, b), c)
```

## 实现方式

```python
from typing import Tuple, List

class GCAlgorithms:
    """GCD 和 LCM 算法实现"""
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """
        欧几里得算法（辗转相除法）
        时间: O(log min(a,b))
        """
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def gcd_recursive(a: int, b: int) -> int:
        """递归版欧几里得算法"""
        return a if b == 0 else GCAlgorithms.gcd_recursive(b, a % b)
    
    @staticmethod
    def gcd_subtraction(a: int, b: int) -> int:
        """
        更相减损术（基于减法）
        时间: O(max(a,b))
        适合大整数（无除法）
        """
        if a == b:
            return a
        if a < b:
            return GCAlgorithms.gcd_subtraction(b - a, a)
        return GCAlgorithms.gcd_subtraction(a - b, b)
    
    @staticmethod
    def gcd_binary(a: int, b: int) -> int:
        """
        Stein 算法（二进制 GCD）
        使用位运算，避免除法
        适合大整数和硬件实现
        """
        if a == 0:
            return b
        if b == 0:
            return a
        
        # 提取公因子 2
        shift = 0
        while ((a | b) & 1) == 0:
            a >>= 1
            b >>= 1
            shift += 1
        
        # 去除 a 的所有因子 2
        while (a & 1) == 0:
            a >>= 1
        
        do:
            # 去除 b 的所有因子 2
            while (b & 1) == 0:
                b >>= 1
            
            # 确保 a <= b
            if a > b:
                a, b = b, a
            
            b = b - a
        while b != 0
        
        return a << shift
    
    @staticmethod
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """
        扩展欧几里得算法
        返回: (g, x, y) 满足 ax + by = g = gcd(a,b)
        
        应用:
        1. 求模逆元
        2. 解线性丢番图方程
        3. 中国剩余定理
        """
        if b == 0:
            return (a, 1, 0)
        
        g, x1, y1 = GCAlgorithms.extended_gcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        
        return (g, x, y)
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """
        最小公倍数
        lcm(a,b) = |a*b| / gcd(a,b)
        
        注意: 防止溢出，先除再乘
        """
        return a // GCAlgorithms.gcd(a, b) * b
    
    @staticmethod
    def lcm_multiple(numbers: List[int]) -> int:
        """多个数的最小公倍数"""
        result = 1
        for num in numbers:
            result = GCAlgorithms.lcm(result, num)
        return result
    
    @staticmethod
    def mod_inverse(a: int, m: int) -> int:
        """
        求模逆元 a^(-1) mod m
        
        存在条件: gcd(a,m) = 1
        使用扩展欧几里得: ax + my = 1，则 x 就是逆元
        """
        g, x, _ = GCAlgorithms.extended_gcd(a % m, m)
        if g != 1:
            raise ValueError(f"逆元不存在，gcd({a},{m}) = {g}")
        return (x % m + m) % m
    
    @staticmethod
    def solve_linear_diophantine(a: int, b: int, c: int) -> Tuple[int, int, int]:
        """
        解线性丢番图方程: ax + by = c
        
        返回: (g, x0, y0)
        - 如果 g | c，则方程有解，通解为:
          x = x0 * (c/g) + (b/g) * t
          y = y0 * (c/g) - (a/g) * t
        - 如果 g ∤ c，则无解
        
        Args:
            a, b, c: 方程系数
        
        Returns:
            (gcd(a,b), 特解x, 特解y)
        """
        g, x0, y0 = GCAlgorithms.extended_gcd(abs(a), abs(b))
        
        if c % g != 0:
            return (g, None, None)  # 无解
        
        # 调整符号
        if a < 0:
            x0 = -x0
        if b < 0:
            y0 = -y0
        
        # 缩放
        x0 *= c // g
        y0 *= c // g
        
        return (g, x0, y0)


# 使用示例
if __name__ == "__main__":
    gcd_alg = GCAlgorithms()
    
    # GCD 测试
    a, b = 48, 18
    print(f"gcd({a}, {b}) = {gcd_alg.gcd(a, b)}")
    
    # 扩展 GCD
    g, x, y = gcd_alg.extended_gcd(35, 15)
    print(f"\n35*{x} + 15*{y} = {g}")
    print(f"验证: {35*x + 15*y}")
    
    # LCM
    print(f"\nlcm(4, 6) = {gcd_alg.lcm(4, 6)}")
    print(f"lcm([2,3,4,5]) = {gcd_alg.lcm_multiple([2,3,4,5])}")
    
    # 模逆元
    try:
        inv = gcd_alg.mod_inverse(3, 11)
        print(f"\n3^(-1) mod 11 = {inv}")
        print(f"验证: (3 * {inv}) % 11 = {(3 * inv) % 11}")
    except ValueError as e:
        print(e)
    
    # 线性丢番图方程
    a, b, c = 6, 9, 3
    g, x, y = gcd_alg.solve_linear_diophantine(a, b, c)
    if x is not None:
        print(f"\n{a}x + {b}y = {c}")
        print(f"特解: x={x}, y={y}")
        print(f"验证: {a}*{x} + {b}*{y} = {a*x + b*y}")
    else:
        print(f"\n方程 {a}x + {b}y = {c} 无解")
```

## 应用场景

### 1. 分数运算
- **分数化简**：分子分母除以 GCD
- **分数加减**：通分需要 LCM
- **连分数**：GCD 与连分数展开

### 2. 密码学
- **RSA**：选择互质的 e 和 φ(n)
- **模逆元**：扩展 GCD 求私钥
- **中国剩余定理**：解同余方程组

### 3. 数论问题
- **Bezout 定理**：ax + by = c 有解条件
- **原根存在性**：gcd(指数, φ(n)) = 1
- **Legendre 符号**：二次剩余判定

### 4. 计算机图形学
- **纹理映射**：有理数坐标简化
- **像素对齐**：网格 GCD 计算

## 面试要点

**Q1: 欧几里得算法的时间复杂度？**
A: O(log min(a,b))。实际上比 log₂ 更快，对于斐波那契数对是最坏情况。

**Q2: 扩展 GCD 有什么应用？**
A: (1) 求模逆元（RSA私钥）；(2) 解线性丢番图方程；(3) 中国剩余定理。

**Q3: 为什么 LCM 要先除后乘？**
A: 防止中间结果溢出。a * b 可能溢出，但 a / gcd * b 不会（因为 gcd 整除 a）。

**Q4: Stein 算法（二进制 GCD）优势？**
A: 只使用减法和位移，避免除法。适合大整数库和硬件实现，位运算更快。

**Q5: 模逆元存在的条件？**
A: a 在模 m 下有逆元 ⟺ gcd(a,m) = 1。即 a 和 m 互质。

## 相关概念

### 数据结构
- [大整数](../data-structures/big-integer.md) - 大数运算

### 算法
- [模运算](./modular-arithmetic.md) - 模逆元应用
- [素性测试](./primality-test.md) - 互质判定
- [中国剩余定理](./chinese-remainder-theorem.md) - GCD 应用

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - O(log min(a,b))
- [欧几里得算法分析](../../references/euclidean-analysis.md) - 斐波那契最坏情况

### 系统实现
- [密码学](../../references/cryptography.md) - RSA、ECC 实现
- [大数库](../../references/bignum-libraries.md) - GMP、OpenSSL
