# 哈希函数 (Hash Functions)

## 概念

**哈希函数（Hash Function）** 是一种将任意长度输入映射为固定长度输出的函数。在计算机科学中广泛应用于数据结构、密码学、数据校验等领域。

> **核心特性**: 确定性、快速计算、均匀分布。

---

## 哈希函数特性

### 基本性质

| 特性 | 描述 |
|------|------|
| **确定性** | 相同输入产生相同输出 |
| **快速计算** | 计算复杂度O(1)或O(n) |
| **均匀分布** | 输出均匀分布在值域 |
| **敏感性** | 微小输入变化导致输出大幅变化（雪崩效应）|

### 密码学哈希额外特性

| 特性 | 描述 |
|------|------|
| **单向性** | 难以从输出反推输入 |
| **抗碰撞** | 难以找到两个不同输入产生相同输出 |
| **抗原像** | 难以找到产生特定输出的输入 |

---

## 常见哈希算法

### 1. 除法取余法

```python
def hash_division(key: int, table_size: int) -> int:
    """除法取余哈希"""
    return key % table_size

# 选择素数作为表大小，分布更均匀
# table_size = 97（素数）
```

### 2. 乘法取整法

```python
def hash_multiplication(key: int, table_size: int) -> int:
    """乘法哈希"""
    A = 0.6180339887  # (√5 - 1) / 2
    fractional = (key * A) % 1
    return int(table_size * fractional)
```

### 3. 字符串哈希

```python
def djb2(string: str) -> int:
    """DJB2哈希算法"""
    hash_val = 5381
    for char in string:
        hash_val = ((hash_val << 5) + hash_val) + ord(char)
    return hash_val & 0xFFFFFFFF

def sdbm(string: str) -> int:
    """SDBM哈希算法"""
    hash_val = 0
    for char in string:
        hash_val = ord(char) + (hash_val << 6) + (hash_val << 16) - hash_val
    return hash_val & 0xFFFFFFFF
```

### 4. 密码学哈希

```python
import hashlib

# MD5（已不安全，不推荐）
md5_hash = hashlib.md5(b"hello").hexdigest()

# SHA-256（推荐）
sha256_hash = hashlib.sha256(b"hello").hexdigest()

# SHA-3
sha3_hash = hashlib.sha3_256(b"hello").hexdigest()
```

---

## 哈希函数应用

### 1. 哈希表

```python
# 数据结构中的哈希
hash_table = {}
hash_table["key"] = "value"  # 哈希函数确定存储位置
```

### 2. 数据校验

```python
# 文件完整性校验
def file_hash(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()
```

### 3. 一致性哈希

```python
# 分布式系统中用于负载均衡
import hashlib

def consistent_hash(key: str, nodes: int) -> int:
    """一致性哈希"""
    hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return hash_val % nodes
```

---

## 哈希冲突

### 冲突原因

- 输入空间 >> 输出空间
- 鸽巢原理：必然存在冲突

### 冲突处理

- [链地址法](../data-structures/hash-table.md) - 链表存储冲突元素
- [开放寻址法](./collision-resolution.md) - 寻找下一个空槽

---

## 密码学哈希 vs 数据结构哈希

| 特性 | 数据结构哈希 | 密码学哈希 |
|------|-------------|-----------|
| 速度 | 快 | 较慢（有意设计）|
| 安全性 | 无要求 | 高要求 |
| 输出长度 | 固定（表大小）| 固定（算法决定）|
| 用途 | 快速查找 | 数据完整性、密码存储 |

---

## 面试要点

1. **好的哈希函数**: 快速、均匀分布、最小冲突
2. **一致性哈希**: 分布式系统中节点增删时的数据迁移
3. **布隆过滤器**: 基于哈希的概率数据结构

---

## 相关概念

### 数据结构
- [哈希表](../data-structures/hash-table.md) - 哈希函数的主要应用
- [冲突解决](./collision-resolution.md) - 处理哈希冲突

### 算法
- [字符串匹配](./string-matching.md) - Rabin-Karp算法
- [布隆过滤器](../data-structures/bloom-filter.md) - 概率数据结构

### 安全
- [密码学基础](../../security/cryptography-basics.md) - 安全哈希
