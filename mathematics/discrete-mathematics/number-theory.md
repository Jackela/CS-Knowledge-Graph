# 数论 (Number Theory)

## 简介

数论（Number Theory）是数学的一个分支，研究整数的性质和关系。作为离散数学的重要组成部分，数论在计算机科学中有广泛应用，包括密码学、算法设计、哈希函数、随机数生成等领域。现代计算机安全体系很大程度上建立在数论的基础之上。

## 核心概念

### 整除与模运算

```python
class NumberTheory:
    """数论基础运算"""
    
    @staticmethod
    def gcd(a, b):
        """
        最大公约数（Greatest Common Divisor）
        欧几里得算法
        """
        a, b = abs(a), abs(b)
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def lcm(a, b):
        """
        最小公倍数（Least Common Multiple）
        """
        if a == 0 or b == 0:
            return 0
        return abs(a * b) // NumberTheory.gcd(a, b)
    
    @staticmethod
    def extended_gcd(a, b):
        """
        扩展欧几里得算法
        返回 (g, x, y) 使得 ax + by = gcd(a, b)
        """
        if b == 0:
            return (a, 1, 0)
        
        g, x1, y1 = NumberTheory.extended_gcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return (g, x, y)
    
    @staticmethod
    def mod_inverse(a, m):
        """
        模逆元
        求 x 使得 (a * x) % m = 1
        仅当 gcd(a, m) = 1 时存在
        """
        g, x, _ = NumberTheory.extended_gcd(a, m)
        if g != 1:
            raise ValueError("Modular inverse does not exist")
        return (x % m + m) % m

# 示例
nt = NumberTheory()
print(nt.gcd(48, 18))  # 6
print(nt.lcm(4, 6))    # 12
print(nt.mod_inverse(3, 11))  # 4 (因为 3 * 4 = 12 ≡ 1 mod 11)
```

### 素数相关算法

```python
class PrimeNumbers:
    """素数算法"""
    
    @staticmethod
    def is_prime(n):
        """
        素数判定 - 试除法
        时间复杂度: O(√n)
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    @staticmethod
    def sieve_of_eratosthenes(limit):
        """
        埃拉托斯特尼筛法
        找出所有小于等于limit的素数
        时间复杂度: O(n log log n)
        """
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        
        for i in range(2, int(limit**0.5) + 1):
            if is_prime[i]:
                for j in range(i * i, limit + 1, i):
                    is_prime[j] = False
        
        return [i for i in range(2, limit + 1) if is_prime[i]]
    
    @staticmethod
    def prime_factorization(n):
        """
        质因数分解
        """
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        
        if n > 1:
            factors.append(n)
        
        return factors

# 示例
pn = PrimeNumbers()
print(pn.sieve_of_eratosthenes(30))
# [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

print(pn.prime_factorization(84))
# [2, 2, 3, 7] = 2² × 3 × 7
```

## 实现方式

### 模幂运算与RSA

```python
class ModularArithmetic:
    """模运算"""
    
    @staticmethod
    def mod_pow(base, exp, mod):
        """
        快速模幂运算
        计算 (base^exp) % mod
        时间复杂度: O(log exp)
        
        用于RSA加密等场景
        """
        result = 1
        base = base % mod
        
        while exp > 0:
            if exp % 2 == 1:
                result = (result * base) % mod
            exp = exp >> 1
            base = (base * base) % mod
        
        return result
    
    @staticmethod
    def euler_phi(n):
        """
        欧拉函数 φ(n)
        小于等于n且与n互质的正整数的个数
        """
        result = n
        p = 2
        
        while p * p <= n:
            if n % p == 0:
                while n % p == 0:
                    n //= p
                result -= result // p
            p += 1
        
        if n > 1:
            result -= result // n
        
        return result

# RSA算法示例
class RSA:
    """RSA加密算法"""
    
    def __init__(self, p, q):
        """
        p, q: 两个大素数
        """
        self.n = p * q
        self.phi = (p - 1) * (q - 1)
        
        # 选择公钥e
        self.e = 65537  # 常用值
        assert NumberTheory.gcd(self.e, self.phi) == 1
        
        # 计算私钥d
        self.d = NumberTheory.mod_inverse(self.e, self.phi)
    
    def encrypt(self, message):
        """加密"""
        return ModularArithmetic.mod_pow(message, self.e, self.n)
    
    def decrypt(self, ciphertext):
        """解密"""
        return ModularArithmetic.mod_pow(ciphertext, self.d, self.n)

# 示例（使用小素数便于演示）
rSA = RSA(61, 53)
message = 42
cipher = rSA.encrypt(message)
print(f"Encrypted: {cipher}")
decrypted = rSA.decrypt(cipher)
print(f"Decrypted: {decrypted}")
```

### 中国剩余定理

```python
class ChineseRemainderTheorem:
    """中国剩余定理"""
    
    @staticmethod
    def solve(remainders, moduli):
        """
        求解同余方程组：
        x ≡ r₁ (mod m₁)
        x ≡ r₂ (mod m₂)
        ...
        
        要求：m₁, m₂, ... 两两互质
        """
        # 验证互质
        for i in range(len(moduli)):
            for j in range(i + 1, len(moduli)):
                if NumberTheory.gcd(moduli[i], moduli[j]) != 1:
                    raise ValueError("Moduli must be pairwise coprime")
        
        total = 0
        prod = 1
        for m in moduli:
            prod *= m
        
        for r, m in zip(remainders, moduli):
            p = prod // m
            total += r * NumberTheory.mod_inverse(p, m) * p
        
        return total % prod

# 示例："三人同行七十稀，五树梅花廿一枝，七子团圆月正半"
# x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)
crt = ChineseRemainderTheorem()
result = crt.solve([2, 3, 2], [3, 5, 7])
print(result)  # 23
```

## 示例

### 费马小定理与素性测试

```python
class PrimalityTest:
    """素性测试"""
    
    @staticmethod
    def fermat_test(n, k=5):
        """
        费马素性测试
        基于费马小定理：若p是素数，则对于任意a，a^(p-1) ≡ 1 (mod p)
        
        可能有伪素数，需多次测试
        """
        import random
        
        if n < 2:
            return False
        if n in (2, 3):
            return True
        
        for _ in range(k):
            a = random.randint(2, n - 2)
            if ModularArithmetic.mod_pow(a, n - 1, n) != 1:
                return False
        
        return True
    
    @staticmethod
    def miller_rabin(n, k=5):
        """
        Miller-Rabin素性测试
        更可靠的概率测试
        """
        import random
        
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
        
        # 将n-1写成2^r * d的形式
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        for _ in range(k):
            a = random.randint(2, n - 2)
            x = ModularArithmetic.mod_pow(a, d, n)
            
            if x == 1 or x == n - 1:
                continue
            
            for _ in range(r - 1):
                x = ModularArithmetic.mod_pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        
        return True

# 测试
test = PrimalityTest()
print(test.miller_rabin(104729))  # True (第10000个素数)
print(test.miller_rabin(104730))  # False
```

## 应用场景

### 数论在计算机科学中的应用

1. **密码学**：RSA、椭圆曲线加密
2. **哈希函数**：模运算设计
3. **随机数生成**：线性同余生成器
4. **纠错码**：基于有限域理论
5. **算法优化**：数论变换(NTT)

## 面试要点

**Q: 为什么RSA算法是安全的？**
A: RSA的安全性基于大整数分解的困难性。将两个大素数相乘很容易，但将大合数分解为素因数极其困难。

**Q: 欧拉函数φ(n)的性质？**
A: 
- 若p是素数，φ(p) = p - 1
- 若gcd(m,n)=1，φ(mn) = φ(m)φ(n)
- 对于素数幂p^k，φ(p^k) = p^k - p^(k-1)

**Q: 费马小定理与欧拉定理的区别？**
A: 费马小定理要求p是素数，a^(p-1) ≡ 1 (mod p)；欧拉定理是推广形式，对于任意互质的a和n，a^φ(n) ≡ 1 (mod n)。

## 相关概念

### 数据结构
- [大整数运算](../computer-science/algorithms/big-integer.md) - 大数处理

### 算法
- [快速幂](../computer-science/algorithms/fast-power.md) - 模幂运算优化

### 复杂度分析
- [计算复杂性](../computer-science/algorithms/computational-complexity.md) - 算法复杂度类

### 系统实现
- [公钥加密](../security/cryptography/asymmetric-encryption.md) - RSA应用
- [哈希函数](../security/cryptography/hash-functions.md) - 数论基础
