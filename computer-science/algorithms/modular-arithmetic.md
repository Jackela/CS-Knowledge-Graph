# 模运算 (Modular Arithmetic)

## 简介

**模运算**（Modular Arithmetic）是数论的核心工具，研究整数在模 n 下的运算规律。它在密码学、哈希算法、竞赛编程中有广泛应用。关键操作包括快速幂、模逆元、中国剩余定理等，能够高效处理大数运算和周期性规律。

## 核心概念

### 基本运算

**模运算性质：**
```
(a + b) mod m = ((a mod m) + (b mod m)) mod m
(a - b) mod m = ((a mod m) - (b mod m) + m) mod m
(a * b) mod m = ((a mod m) * (b mod m)) mod m
```

**注意：** 除法需要乘逆元，(a / b) mod m = (a * b^(-1)) mod m

### 快速幂

**原理：**
```
a^b mod m = (a^(b/2))^2 mod m       (b 偶数)
a^b mod m = a * (a^((b-1)/2))^2 mod m (b 奇数)
```

**时间复杂度：** O(log b)

### 模逆元

**定义：** a^(-1) mod m 是满足 a * x ≡ 1 (mod m) 的 x

**存在条件：** gcd(a, m) = 1

**计算方法：**
- 扩展欧几里得算法：O(log m)
- 费马小定理（m 为素数）：a^(-1) ≡ a^(m-2) (mod m)

### 中国剩余定理

**问题：** 解同余方程组
```
x ≡ a1 (mod n1)
x ≡ a2 (mod n2)
...
x ≡ ak (mod nk)
```

**条件：** n1, n2, ..., nk 两两互质

**解：**
```
N = n1 * n2 * ... * nk
Ni = N / ni
xi = Ni^(-1) mod ni  (模逆元)
x = Σ(ai * Ni * xi) mod N
```

## 实现方式

```python
from typing import List, Tuple
from functools import reduce

class ModularArithmetic:
    """模运算工具类"""
    
    @staticmethod
    def power_mod(base: int, exp: int, mod: int) -> int:
        """
        快速幂取模
        计算 (base^exp) % mod
        
        时间: O(log exp)
        """
        if mod == 1:
            return 0
        
        result = 1
        base = base % mod
        
        while exp > 0:
            # 如果 exp 是奇数
            if exp & 1:
                result = (result * base) % mod
            
            # exp 右移一位，base 平方
            exp >>= 1
            base = (base * base) % mod
        
        return result
    
    @staticmethod
    def mod_inverse(a: int, m: int) -> int:
        """
        求模逆元 a^(-1) mod m
        使用扩展欧几里得算法
        
        存在条件: gcd(a, m) = 1
        
        时间: O(log m)
        """
        def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
            if b == 0:
                return (a, 1, 0)
            g, x1, y1 = extended_gcd(b, a % b)
            x = y1
            y = x1 - (a // b) * y1
            return (g, x, y)
        
        g, x, _ = extended_gcd(a % m, m)
        if g != 1:
            raise ValueError(f"逆元不存在，gcd({a},{m}) = {g}")
        
        return (x % m + m) % m
    
    @staticmethod
    def mod_inverse_fermat(a: int, p: int) -> int:
        """
        费马小定理求逆元（p 必须是素数）
        a^(-1) ≡ a^(p-2) (mod p)
        
        时间: O(log p)
        """
        return ModularArithmetic.power_mod(a, p - 2, p)
    
    @staticmethod
    def chinese_remainder(remainders: List[int], moduli: List[int]) -> int:
        """
        中国剩余定理（CRT）
        
        解方程组: x ≡ remainders[i] (mod moduli[i])
        条件: moduli 两两互质
        
        时间: O(k * log(max(moduli)))
        
        Args:
            remainders: 余数列表 [a1, a2, ..., ak]
            moduli: 模数列表 [n1, n2, ..., nk]
        
        Returns:
            最小正整数解 x
        """
        if len(remainders) != len(moduli):
            raise ValueError("余数和模数数量必须相同")
        
        # 计算 N = n1 * n2 * ... * nk
        N = reduce(lambda x, y: x * y, moduli)
        
        result = 0
        for ai, ni in zip(remainders, moduli):
            Ni = N // ni
            # 求 Ni 在模 ni 下的逆元
            xi = ModularArithmetic.mod_inverse(Ni % ni, ni)
            result = (result + ai * Ni * xi) % N
        
        return result
    
    @staticmethod
    def factorial_mod(n: int, mod: int) -> int:
        """计算 n! mod mod"""
        result = 1
        for i in range(2, n + 1):
            result = (result * i) % mod
        return result
    
    @staticmethod
    def nCr_mod(n: int, r: int, mod: int) -> int:
        """
        计算组合数 C(n,r) mod mod
        使用乘法公式和模逆元
        
        时间: O(r * log mod)
        """
        if r < 0 or r > n:
            return 0
        if r == 0 or r == n:
            return 1
        
        r = min(r, n - r)  # 利用对称性
        
        numerator = 1  # 分子: n * (n-1) * ... * (n-r+1)
        denominator = 1  # 分母: r!
        
        for i in range(r):
            numerator = (numerator * (n - i)) % mod
            denominator = (denominator * (i + 1)) % mod
        
        # 分母求逆元
        return (numerator * ModularArithmetic.mod_inverse(denominator, mod)) % mod
    
    @staticmethod
    def discrete_log(a: int, b: int, m: int) -> int:
        """
        离散对数: 找 x 使得 a^x ≡ b (mod m)
        使用 Baby-step Giant-step 算法
        
        时间: O(√m)
        
        Returns:
            最小非负整数解，无解返回 -1
        """
        n = int(m**0.5) + 1
        
        # Baby steps: a^j mod m
        value_to_j = {}
        curr = 1
        for j in range(n):
            if curr not in value_to_j:
                value_to_j[curr] = j
            curr = (curr * a) % m
        
        # Giant steps: b * a^(-n*i) mod m
        a_n_inv = ModularArithmetic.mod_inverse(
            ModularArithmetic.power_mod(a, n, m), m
        )
        curr = b
        for i in range(n):
            if curr in value_to_j:
                ans = i * n + value_to_j[curr]
                if ans < m:
                    return ans
            curr = (curr * a_n_inv) % m
        
        return -1


# 使用示例
if __name__ == "__main__":
    ma = ModularArithmetic()
    
    # 快速幂
    print("快速幂:")
    print(f"2^100 mod 1000 = {ma.power_mod(2, 100, 1000)}")
    print(f"3^1000 mod 1000000007 = {ma.power_mod(3, 1000, 1000000007)}")
    
    # 模逆元
    print("\n模逆元:")
    a, m = 3, 11
    inv = ma.mod_inverse(a, m)
    print(f"{a}^(-1) mod {m} = {inv}")
    print(f"验证: {a} * {inv} mod {m} = {(a * inv) % m}")
    
    # 中国剩余定理
    print("\n中国剩余定理:")
    # x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)
    remainders = [2, 3, 2]
    moduli = [3, 5, 7]
    x = ma.chinese_remainder(remainders, moduli)
    print(f"x ≡ {remainders} mod {moduli}")
    print(f"解: x = {x}")
    for r, m in zip(remainders, moduli):
        print(f"  {x} mod {m} = {x % m}")
    
    # 组合数
    print("\n组合数:")
    mod = 1000000007
    print(f"C(1000, 500) mod {mod} = {ma.nCr_mod(1000, 500, mod)}")
    
    # 离散对数
    print("\n离散对数:")
    a, b, m = 2, 9, 13
    x = ma.discrete_log(a, b, m)
    print(f"{a}^x ≡ {b} (mod {m})")
    print(f"x = {x}")
    print(f"验证: {a}^{x} mod {m} = {ma.power_mod(a, x, m)}")
```

## 应用场景

### 1. 密码学
- **RSA**：大数模幂运算
- **Diffie-Hellman**：离散对数问题
- **ECC**：椭圆曲线上的模运算

### 2. 哈希算法
- **一致性哈希**：模运算映射
- **布隆过滤器**：多个哈希函数
- **指纹算法**：大整数取模

### 3. 竞赛编程
- **大数处理**：中间结果取模防溢出
- **计数问题**：组合数、卡特兰数
- **矩阵快速幂**：线性递推加速

### 4. 校验和
- **ISBN/UPC 校验码**：加权和取模
- **Luhn 算法**：信用卡号验证
- **CRC**：循环冗余校验

## 面试要点

**Q1: 为什么模运算中除法要转成乘法？**
A: 整数在模 m 下不一定有除法封闭性。必须乘以模逆元，相当于除法。逆元存在的条件是除数与模互质。

**Q2: 快速幂的时间复杂度？为什么？**
A: O(log n)。每次将指数折半，最多 log₂n 次乘法。例如 2^100 只需约 7 次乘法而非 99 次。

**Q3: 中国剩余定理的应用场景？**
A: (1) 大数模分解为多个小数模；(2) 密码学中的秘密共享；(3) 多传感器数据融合。

**Q4: 费马小定理的条件？**
A: p 必须是素数，且 a 不是 p 的倍数。此时 a^(p-1) ≡ 1 (mod p)，所以 a^(-1) ≡ a^(p-2) (mod p)。

**Q5: 如何计算大组合数 mod p？**
A: 使用乘法公式和模逆元。C(n,k) = n!/(k!(n-k)!)，分别计算分子、分母的模，然后乘以分母的模逆元。

## 相关概念

### 数据结构
- [大整数](../data-structures/big-integer.md) - 大数表示

### 算法
- [GCD/LCM](./gcd-lcm.md) - 扩展欧几里得求逆元
- [素性测试](./primality-test.md) - 逆元存在性
- [矩阵快速幂](./matrix-exponentiation.md) - 递推加速

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - O(log n)
- [数论函数](../../references/number-theoretic-functions.md) - 欧拉函数、莫比乌斯函数

### 系统实现
- [密码学](../../references/cryptography.md) - RSA、DH
- [密码库](../../references/crypto-libraries.md) - OpenSSL、libsodium
