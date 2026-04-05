# 素性测试 (Primality Testing)

## 简介

**素性测试**（Primality Testing）用于判断一个数是否为素数。在密码学、数论和竞赛编程中有重要应用。从简单的试除法到高效的 Miller-Rabin 概率算法，再到确定性算法 AKS，不同场景需要不同的权衡。

## 核心概念

### 试除法

**朴素方法：**
```
检查 2 到 n-1 是否能整除 n
时间: O(n)
```

**优化到 O(√n)：**
```
如果 n 有因子大于 √n，则必有对应因子小于 √n
只需检查 2 到 √n
```

**进一步优化：**
- 先检查 2, 3
- 然后检查 6k±1 形式的数
- 排除所有 2 和 3 的倍数

### Fermat 素性测试

**费马小定理：**
```
如果 p 是素数，则对于任意 a (1 < a < p):
a^(p-1) ≡ 1 (mod p)
```

**费马测试：**
- 随机选择 a，检查 a^(p-1) mod p == 1
- 若不相等，p 一定是合数
- 若相等，p 可能是素数（费马伪素数）

**缺陷：** 存在 Carmichael 数，对所有 a 都通过测试但仍是合数

### Miller-Rabin 测试

**基于以下性质：**
如果 p 是素数，则 x² ≡ 1 (mod p) 的解只有 x ≡ ±1

**算法步骤：**
1. 将 n-1 写成 2^r × d 的形式（d 为奇数）
2. 随机选择 a，计算 x = a^d mod n
3. 如果 x == 1 或 x == n-1，可能为素数
4. 重复平方 r-1 次，检查是否出现 n-1
5. 如果没有出现 n-1，一定是合数

**时间复杂度：** O(k × log³n)，k 为测试轮数

**错误率：** 每轮 ≤ 1/4，k 轮后 ≤ 4^(-k)

## 实现方式

```python
import random
from typing import List

class PrimalityTest:
    """素性测试算法"""
    
    @staticmethod
    def is_prime_trial(n: int) -> bool:
        """
        试除法
        时间: O(√n)
        适合: n < 10^12
        """
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
        
        # 只需检查到 √n
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        
        return True
    
    @staticmethod
    def is_prime_optimized(n: int) -> bool:
        """
        优化试除法 - 6k±1 优化
        时间: O(√n/3)
        """
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        
        # 检查 6k±1 形式的数
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        
        return True
    
    @staticmethod
    def _power_mod(base: int, exp: int, mod: int) -> int:
        """快速幂取模"""
        result = 1
        base = base % mod
        while exp > 0:
            if exp & 1:
                result = (result * base) % mod
            base = (base * base) % mod
            exp >>= 1
        return result
    
    @staticmethod
    def is_prime_miller_rabin(n: int, k: int = 10) -> bool:
        """
        Miller-Rabin 素性测试
        时间: O(k × log³n)
        错误率: ≤ 4^(-k)
        
        Args:
            n: 待测试的数
            k: 测试轮数（默认10轮，错误率 < 10^-6）
        """
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
        
        # 将 n-1 写成 2^r × d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        #  witnesses 对于 n < 2^64 足够
        witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        
        for a in witnesses[:k]:
            if a >= n:
                continue
            
            x = PrimalityTest._power_mod(a, d, n)
            
            if x == 1 or x == n - 1:
                continue
            
            for _ in range(r - 1):
                x = (x * x) % n
                if x == n - 1:
                    break
            else:
                return False
        
        return True
    
    @staticmethod
    def is_prime_deterministic(n: int) -> bool:
        """
        确定性 Miller-Rabin（对于 n < 2^64）
        使用确定的 witness 集合
        """
        if n < 2:
            return False
        
        # 小素数检查
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for p in small_primes:
            if n == p:
                return True
            if n % p == 0:
                return False
        
        # 对于 n < 2^64，这些 witness 足够
        witnesses = [2, 325, 9375, 28178, 450775, 9780504, 1795265022]
        
        # 将 n-1 写成 2^r × d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        for a in witnesses:
            if a % n == 0:
                continue
            
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            
            for _ in range(r - 1):
                x = (x * x) % n
                if x == n - 1:
                    break
            else:
                return False
        
        return True


# 使用示例
if __name__ == "__main__":
    tester = PrimalityTest()
    
    # 测试一些数
    test_numbers = [2, 17, 25, 97, 100, 104729, 2147483647]
    
    print("素性测试结果:")
    for n in test_numbers:
        result_trial = tester.is_prime_trial(n)
        result_mr = tester.is_prime_miller_rabin(n)
        print(f"  {n}: 试除法={result_trial}, Miller-Rabin={result_mr}")
    
    # 大数测试
    big_prime = 10**18 + 3
    print(f"\n{big_prime} 是素数? {tester.is_prime_miller_rabin(big_prime, k=20)}")
    
    # 生成随机大素数
    print("\n生成 100 位随机素数...")
    while True:
        candidate = random.getrandbits(100) | 1  # 确保奇数
        if tester.is_prime_miller_rabin(candidate, k=20):
            print(f"找到素数: {candidate}")
            break
```

## 应用场景

### 1. 密码学
- **RSA 密钥生成**：生成大素数 p, q
- **DH 密钥交换**：选择大素数模数
- **椭圆曲线**：定义有限域的特征

### 2. 数论研究
- **素数分布**：π(x) 的研究
- **Goldbach 猜想验证**：大偶数分解
- **Riemann 假设**：相关计算

### 3. 哈希表
- **哈希函数**：选择素数大小的表
- **冲突减少**：素数取模分布更均匀

### 4. 随机数生成
- **线性同余**：模数为素数时周期更长
- **梅森素数**：MT19937 随机数生成器

## 面试要点

**Q1: 试除法优化到 O(√n) 的原理？**
A: 如果 n 有大于 √n 的因子 d，则 n/d 是小于 √n 的因子。所以只需检查到 √n。

**Q2: 什么是费马伪素数？**
A: 合数 n 满足 a^(n-1) ≡ 1 (mod n) 对于某个 a。Carmichael 数对所有与 n 互质的 a 都满足。

**Q3: Miller-Rabin 为什么比 Fermat 可靠？**
A: Miller-Rabin 利用了更强的性质：若 n 是素数，则 x² ≡ 1 只有 ±1 解。这排除了所有 Carmichael 数。

**Q4: 实际应用中选择多少轮测试？**
A: 密码学应用通常 40-50 轮，错误率 2^-80。一般应用 10-20 轮足够。

**Q5: 如何生成大素数？**
A: 随机生成奇数，用小素数试除预筛选，然后用 Miller-Rabin 测试。期望尝试 O(log n) 次。

## 相关概念

### 数据结构
- [大整数](../data-structures/big-integer.md) - 大数运算

### 算法
- [快速幂](./modular-arithmetic.md) - Miller-Rabin 核心
- [欧几里得算法](./gcd-lcm.md) - 最大公约数
- [Pollard Rho](./integer-factorization.md) - 因数分解

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md) - O(k log³n)
- [概率算法](../../references/randomized-algorithms.md) - 概率保证

### 系统实现
- [密码学](../../references/cryptography.md) - RSA、DH 实现
- [OpenSSL](../../references/openssl.md) - 大数库
