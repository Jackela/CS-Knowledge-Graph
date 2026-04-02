# 函数 (Functions)

## 简介

函数（Functions）是数学中最基本的概念之一，描述了输入与输出之间的确定性映射关系。在离散数学中，函数是一种特殊的关系，满足每个输入对应唯一输出的特性。函数理论是理解算法、计算复杂性、密码学等计算机科学核心领域的基础。

## 核心概念

### 函数的定义

设 A 和 B 是两个集合，函数 f: A → B 是从 A 到 B 的关系，满足：
- ∀a ∈ A, ∃! b ∈ B，使得 (a, b) ∈ f

```python
class Function:
    """函数的基本实现"""
    
    def __init__(self, mapping, domain, codomain):
        """
        mapping: dict 表示的映射关系
        domain: 定义域
        codomain: 陪域
        """
        self.mapping = mapping
        self.domain = set(domain)
        self.codomain = set(codomain)
        
        # 验证是合法函数
        assert set(mapping.keys()) == self.domain
        assert all(v in self.codomain for v in mapping.values())
    
    def __call__(self, x):
        """函数求值"""
        if x not in self.domain:
            raise ValueError(f"{x} not in domain")
        return self.mapping[x]
    
    def image(self):
        """求值域（像集）"""
        return set(self.mapping.values())
    
    def preimage(self, y):
        """求原像"""
        return {x for x, v in self.mapping.items() if v == y}

# 示例：字符长度函数
length_func = Function(
    mapping={"a": 1, "ab": 2, "abc": 3},
    domain={"a", "ab", "abc"},
    codomain={1, 2, 3, 4, 5}
)
print(length_func("ab"))  # 2
print(length_func.image())  # {1, 2, 3}
```

### 函数类型

```python
class FunctionProperties:
    """函数性质检查"""
    
    @staticmethod
    def is_injective(func):
        """
        单射（Injective/One-to-One）：
        ∀a,b ∈ domain, f(a) = f(b) → a = b
        不同的输入产生不同的输出
        """
        values = list(func.mapping.values())
        return len(values) == len(set(values))
    
    @staticmethod
    def is_surjective(func):
        """
        满射（Surjective/Onto）：
        ∀y ∈ codomain, ∃x ∈ domain, f(x) = y
        陪域中每个元素都被映射到
        """
        return func.image() == func.codomain
    
    @staticmethod
    def is_bijective(func):
        """
        双射（Bijective）：
        既是单射又是满射
        存在逆函数
        """
        return (FunctionProperties.is_injective(func) and 
                FunctionProperties.is_surjective(func))

# 示例检查
f1 = Function({1: 'a', 2: 'b', 3: 'c'}, {1, 2, 3}, {'a', 'b', 'c'})
print(FunctionProperties.is_bijective(f1))  # True

f2 = Function({1: 'a', 2: 'a'}, {1, 2}, {'a', 'b'})
print(FunctionProperties.is_injective(f2))  # False
```

## 实现方式

### 函数的组合与逆

```python
class FunctionOperations:
    """函数运算"""
    
    @staticmethod
    def compose(f, g):
        """
        函数复合：(g ∘ f)(x) = g(f(x))
        要求：f的值域 ⊆ g的定义域
        """
        if not f.image().issubset(g.domain):
            raise ValueError("Cannot compose: codomain of f not in domain of g")
        
        new_mapping = {
            x: g(f(x)) for x in f.domain
        }
        return Function(new_mapping, f.domain, g.codomain)
    
    @staticmethod
    def inverse(func):
        """
        求逆函数
        仅当函数是双射时才存在
        """
        if not FunctionProperties.is_bijective(func):
            raise ValueError("Only bijective functions have inverses")
        
        inverse_mapping = {v: k for k, v in func.mapping.items()}
        return Function(
            inverse_mapping, 
            func.codomain,  # 原陪域变成定义域
            func.domain     # 原定义域变成陪域
        )

# 示例：函数复合
f = Function({1: 2, 2: 3, 3: 4}, {1, 2, 3}, {2, 3, 4})
g = Function({2: 20, 3: 30, 4: 40}, {2, 3, 4}, {20, 30, 40})
h = FunctionOperations.compose(f, g)
print(h.mapping)  # {1: 20, 2: 30, 3: 40}
```

### 特征函数与指示函数

```python
class CharacteristicFunction:
    """特征函数（集合的指示函数）"""
    
    def __init__(self, subset, universe):
        self.subset = set(subset)
        self.universe = set(universe)
        assert self.subset.issubset(self.universe)
    
    def __call__(self, x):
        """1 if x in subset, 0 otherwise"""
        return 1 if x in self.subset else 0
    
    def set_operations(self, other):
        """
        利用特征函数进行集合运算
        """
        # 交集：min(χ_A, χ_B)
        intersection = {
            x: min(self(x), other(x)) 
            for x in self.universe
        }
        
        # 并集：max(χ_A, χ_B)
        union = {
            x: max(self(x), other(x))
            for x in self.universe
        }
        
        # 补集：1 - χ_A
        complement = {
            x: 1 - self(x)
            for x in self.universe
        }
        
        return intersection, union, complement

# 示例
A = CharacteristicFunction({1, 2, 3}, {1, 2, 3, 4, 5})
print(A(2))  # 1
print(A(4))  # 0
```

## 示例

### 哈希函数

```python
import hashlib

class HashFunction:
    """
    哈希函数示例
    将任意输入映射到固定大小的输出空间
    """
    
    def __init__(self, size):
        self.size = size
    
    def __call__(self, key):
        """计算哈希值"""
        if isinstance(key, str):
            key = key.encode('utf-8')
        elif not isinstance(key, bytes):
            key = str(key).encode('utf-8')
        
        # 使用SHA-256然后取模
        hash_value = hashlib.sha256(key).hexdigest()
        return int(hash_value, 16) % self.size
    
    def demonstrate_collision(self, num_keys):
        """演示碰撞"""
        values = {}
        for i in range(num_keys):
            h = self(i)
            if h not in values:
                values[h] = []
            values[h].append(i)
        
        collisions = {k: v for k, v in values.items() if len(v) > 1}
        return collisions

# 示例
hash_func = HashFunction(100)
print(hash_func("hello"))
print(hash_func("world"))

# 观察生日悖论
collisions = hash_func.demonstrate_collision(50)
print(f"Collisions found: {len(collisions)}")
```

### 递归函数

```python
class RecursiveFunctions:
    """经典递归函数示例"""
    
    @staticmethod
    def factorial(n):
        """阶乘函数"""
        if n <= 1:
            return 1
        return n * RecursiveFunctions.factorial(n - 1)
    
    @staticmethod
    def fibonacci(n):
        """斐波那契数列"""
        if n <= 1:
            return n
        return (RecursiveFunctions.fibonacci(n - 1) + 
                RecursiveFunctions.fibonacci(n - 2))
    
    @staticmethod
    def ackermann(m, n):
        """
        阿克曼函数
        不是原始递归的可计算全函数
        增长极其迅速
        """
        if m == 0:
            return n + 1
        elif n == 0:
            return RecursiveFunctions.ackermann(m - 1, 1)
        else:
            return RecursiveFunctions.ackermann(
                m - 1, 
                RecursiveFunctions.ackermann(m, n - 1)
            )

# 示例
print(RecursiveFunctions.factorial(5))  # 120
print(RecursiveFunctions.fibonacci(10))  # 55
print(RecursiveFunctions.ackermann(3, 2))  # 29
```

## 应用场景

### 函数在计算机科学中的应用

1. **哈希表**：哈希函数将键映射到数组索引
2. **加密**：单向函数用于密码学
3. **压缩**：压缩函数减少数据大小
4. **机器学习**：激活函数、损失函数
5. **函数式编程**：纯函数、高阶函数

## 面试要点

**Q: 单射、满射、双射的区别是什么？**
A: 
- 单射：一对一，不同输入有不同输出
- 满射：覆盖整个陪域，每个输出都有对应输入
- 双射：既是单射又是满射，存在逆函数

**Q: 如何证明两个集合的基数相同？**
A: 构造它们之间的双射函数。如果存在双射，则两个集合等势。

**Q: 什么是偏函数（Partial Function）？**
A: 偏函数是定义域的子集上有定义的函数。与全函数（Total Function）相对，偏函数对某些输入没有定义。

## 相关概念

### 数据结构
- [哈希表](../computer-science/data-structures/hash-table.md) - 哈希函数的应用
- [映射](../computer-science/data-structures/map.md) - 函数的数据结构实现

### 算法
- [递归](../computer-science/algorithms/recursion.md) - 递归函数

### 复杂度分析
- [计算复杂性](../computer-science/algorithms/computational-complexity.md) - 函数可计算性

### 系统实现
- [密码学哈希](../security/cryptography/hash-functions.md) - 单向函数应用
