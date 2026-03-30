# 哈希函数 (Hash Functions)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概念

**哈希函数 (Hash Function)** 是一种将任意长度输入（消息）转换为固定长度输出（哈希值/摘要）的函数。密码学哈希函数具有特殊的数学性质，使其在信息安全领域有广泛应用。

```
┌─────────────────────────────────────────────────────────────────┐
│                   哈希函数原理                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   输入（任意长度）                                               │
│   ┌───────────────────────────────────────────────────────┐    │
│   │ "Hello, World!"                                       │    │
│   │ "The quick brown fox jumps over the lazy dog..."      │    │
│   │ 二进制文件（GB级）                                     │    │
│   └───────────────────────────────────────────────────────┘    │
│                            │                                    │
│                            ▼                                    │
│                    ┌───────────────┐                           │
│                    │   哈希函数     │                           │
│                    │   Hash()      │                           │
│                    └───────┬───────┘                           │
│                            │                                    │
│                            ▼                                    │
│   输出（固定长度）                                              │
│   ┌───────────────────────────────────────────────────────┐    │
│   │ SHA-256: 256位 (64字符十六进制)                        │    │
│   │ a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b...    │    │
│   └───────────────────────────────────────────────────────┘    │
│                                                                 │
│   特点：                                                         │
│   • 单向性：无法从哈希值反推输入                                │
│   • 固定输出：无论输入多长，输出长度固定                        │
│   • 确定性：相同输入产生相同输出                                │
│   • 抗碰撞：难以找到两个不同输入产生相同输出                    │
│   • 雪崩效应：输入微小改变导致输出大幅变化                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 密码学哈希函数性质

```
┌─────────────────────────────────────────────────────────────────┐
│                   密码学哈希函数的安全性质                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. 单向性 (Preimage Resistance)                               │
│      ┌───────────────────────────────────────────────┐         │
│      │  已知 h = H(m)                               │         │
│      │  难以找到 m' 使得 H(m') = h                  │         │
│      │                                               │         │
│      │  比喻：容易打碎鸡蛋，难以复原                │         │
│      └───────────────────────────────────────────────┘         │
│                                                                 │
│   2. 第二原像抗性 (Second Preimage Resistance)                  │
│      ┌───────────────────────────────────────────────┐         │
│      │  已知 m，难以找到 m' ≠ m                     │         │
│      │  使得 H(m') = H(m)                           │         │
│      │                                               │         │
│      │  应用：防止消息被替换                        │         │
│      └───────────────────────────────────────────────┘         │
│                                                                 │
│   3. 抗碰撞性 (Collision Resistance)                            │
│      ┌───────────────────────────────────────────────┐         │
│      │  难以找到任意 m₁ ≠ m₂                        │         │
│      │  使得 H(m₁) = H(m₂)                          │         │
│      │                                               │         │
│      │  生日攻击：需要约 2^(n/2) 次尝试             │         │
│      │  SHA-256: 需要约 2^128 次                    │         │
│      └───────────────────────────────────────────────┘         │
│                                                                 │
│   4. 雪崩效应 (Avalanche Effect)                                │
│      ┌───────────────────────────────────────────────┐         │
│      │  输入: "Hello"                               │         │
│      │  SHA256: 185f8db32271fe25f561a6fc938b2e26...│         │
│      │                                               │         │
│      │  输入: "hello" (小写h)                       │         │
│      │  SHA256: 2cf24dba5fb0a30e26e83b2ac5b9e29e...│         │
│      │                                               │         │
│      │  仅1位差异，输出完全不同                     │         │
│      └───────────────────────────────────────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 常见哈希算法

### SHA-2 家族

```
┌─────────────────────────────────────────────────────────────────┐
│                   SHA-2 哈希算法家族                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   算法          输出长度    内部状态    安全性      状态         │
│   ─────────────────────────────────────────────────────────    │
│   SHA-224       224位      256位       112位      ✅ 安全      │
│   SHA-256       256位      256位       128位      ✅ 推荐      │
│   SHA-384       384位      512位       192位      ✅ 安全      │
│   SHA-512       512位      512位       256位      ✅ 安全      │
│   SHA-512/224   224位      512位       112位      ✅ 安全      │
│   SHA-512/256   256位      512位       128位      ✅ 安全      │
│                                                                 │
│   SHA-256 结构：                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  消息填充 → 分块(512位) → 压缩函数迭代                  │  │
│   │                                                         │  │
│   │  压缩函数：                                              │  │
│   │  ┌─────────────────────────────────────────────────┐   │  │
│   │  │  64轮处理，每轮使用不同的常量                    │   │  │
│   │  │  使用位运算：AND, OR, XOR, NOT, 移位             │   │  │
│   │  │  非线性函数提供混淆                              │   │  │
│   │  └─────────────────────────────────────────────────┘   │  │
│   │                                                         │  │
│   │  应用：                                                 │  │
│   │  • 比特币使用 SHA-256d (双重SHA-256)                  │  │
│   │  • TLS/SSL 证书签名                                    │  │
│   │  • 代码签名                                            │  │
│   │  • 数据完整性验证                                      │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### SHA-3 和 Keccak

```
┌─────────────────────────────────────────────────────────────────┐
│                   SHA-3 (Keccak)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   背景：                                                         │
│   • NIST 2015年发布，替代 SHA-2 的备选方案                      │
│   • 基于 Keccak 算法，使用海绵结构 (Sponge Construction)        │
│   • 与 SHA-2 完全不同的设计，提供算法多样性                     │
│                                                                 │
│   海绵结构：                                                     │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                                                         │  │
│   │   输入数据 ──▶ 吸收阶段 ──▶ 挤压阶段 ──▶ 输出          │  │
│   │                 │            │                         │  │
│   │              ┌──┴──┐      ┌──┴──┐                      │  │
│   │              │ 异或 │      │ 读取 │                      │  │
│   │              └──┬──┘      └──┬──┘                      │  │
│   │                 │            │                         │  │
│   │         ┌───────┴───────┐    │                         │  │
│   │         │   f 函数      │◀───┘                         │  │
│   │         │  (置换函数)    │                              │  │
│   │         └───────────────┘                              │  │
│   │                                                         │  │
│   │  1600位内部状态，24轮置换                               │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   变体：                                                         │
│   • SHA3-224, SHA3-256, SHA3-384, SHA3-512                    │
│   • SHAKE128, SHAKE256 (可扩展输出函数 XOF)                    │
│                                                                 │
│   优势：                                                         │
│   • 对长度扩展攻击天然免疫                                       │
│   • 简单的安全证明                                               │
│   • 灵活的输出长度 (SHAKE)                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### MD5 - 已废弃

```
┌─────────────────────────────────────────────────────────────────┐
│                   MD5 - 不再安全                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   历史：                                                         │
│   • 1992年由 Ron Rivest 设计                                    │
│   • 曾是最广泛使用的哈希算法                                     │
│   • 128位输出                                                   │
│                                                                 │
│   破解历程：                                                     │
│   • 1996年：发现设计缺陷                                         │
│   • 2004年：王小云团队发现碰撞攻击方法                          │
│   • 2008年：MD5 碰撞攻击可在数小时内完成                        │
│   • 2010年：CMU 软件工程研究所建议停止使用                      │
│                                                                 │
│   ❌ 绝对不要使用 MD5 用于：                                     │
│      • 密码存储                                                 │
│      • 数字签名                                                 │
│      • SSL 证书                                                 │
│      • 任何安全敏感场景                                          │
│                                                                 │
│   ⚠️ 唯一可接受用途：                                            │
│      • 非安全的完整性检查（文件校验和）                          │
│      • 哈希表键值                                               │
│      • 数据分片                                                 │
│                                                                 │
│   碰撞攻击示例：                                                 │
│   • 2008年：攻击者创建了具有相同 MD5 哈希的不同 SSL 证书        │
│   • 2012年：Flame 恶意软件利用 MD5 碰撞伪造 Windows 更新        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 代码示例

### Python 哈希计算

```python
import hashlib
import hmac
import secrets

# 基本哈希计算
def compute_hash(data: bytes, algorithm: str = 'sha256') -> str:
    """计算数据的哈希值"""
    if algorithm == 'sha256':
        return hashlib.sha256(data).hexdigest()
    elif algorithm == 'sha384':
        return hashlib.sha384(data).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data).hexdigest()
    elif algorithm == 'sha3_256':
        return hashlib.sha3_256(data).hexdigest()
    else:
        raise ValueError(f"不支持的算法: {algorithm}")

# 使用示例
data = b"Hello, World!"
print(f"SHA-256: {compute_hash(data, 'sha256')}")
print(f"SHA-512: {compute_hash(data, 'sha512')}")
print(f"SHA3-256: {compute_hash(data, 'sha3_256')}")

# 增量哈希（处理大文件）
def hash_file(filepath: str, algorithm: str = 'sha256') -> str:
    """计算文件的哈希值，适合大文件"""
    hasher = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

# 使用示例
# file_hash = hash_file('/path/to/large/file.iso')
```

### HMAC (哈希消息认证码)

```python
# HMAC 用于消息认证
def compute_hmac(key: bytes, message: bytes, algorithm: str = 'sha256') -> str:
    """计算 HMAC"""
    return hmac.new(key, message, algorithm).hexdigest()

def verify_hmac(key: bytes, message: bytes, expected_hmac: str, algorithm: str = 'sha256') -> bool:
    """验证 HMAC - 使用恒定时间比较防止时序攻击"""
    computed = hmac.new(key, message, algorithm).hexdigest()
    return hmac.compare_digest(computed, expected_hmac)

# 使用示例
key = secrets.token_bytes(32)
message = b"Important message"

# 计算 HMAC
mac = compute_hmac(key, message)
print(f"HMAC: {mac}")

# 验证 HMAC
is_valid = verify_hmac(key, message, mac)
print(f"验证结果: {is_valid}")
```

### 密码哈希（Argon2）

```python
# 使用 Argon2 进行密码哈希（推荐）
# pip install argon2-cffi

from argon2 import PasswordHasher
from argon2.low_level import Type

ph = PasswordHasher(
    time_cost=3,      # 迭代次数
    memory_cost=65536, # 64MB
    parallelism=4,    # 并行度
    hash_len=32,      # 哈希长度
    salt_len=16       # 盐长度
)

# 哈希密码
def hash_password(password: str) -> str:
    """安全地哈希密码"""
    return ph.hash(password)

# 验证密码
def verify_password(password: str, hash_string: str) -> bool:
    """验证密码"""
    try:
        ph.verify(hash_string, password)
        return True
    except Exception:
        return False

# 检查是否需要重新哈希
def needs_rehash(hash_string: str) -> bool:
    """检查是否需要使用新参数重新哈希"""
    return ph.check_needs_rehash(hash_string)

# 使用示例
password = "user_password_123"
password_hash = hash_password(password)
print(f"密码哈希: {password_hash}")

# 验证
is_valid = verify_password(password, password_hash)
print(f"密码验证: {is_valid}")
```

---

## 哈希应用

### 数据完整性验证

```python
import hashlib
import json

def verify_data_integrity(data: dict, expected_hash: str) -> bool:
    """验证数据完整性"""
    # 将数据标准化（排序键，确保一致性）
    canonical_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
    computed_hash = hashlib.sha256(canonical_data.encode()).hexdigest()
    return computed_hash == expected_hash

# 使用示例
data = {"user": "alice", "action": "transfer", "amount": 100}
data_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

# 传输数据和哈希
# ...

# 验证
is_intact = verify_data_integrity(data, data_hash)
```

### 哈希表和布隆过滤器

```python
# 布隆过滤器实现
import hashlib
import math

class BloomFilter:
    """布隆过滤器 - 用于高效的存在性查询"""
    
    def __init__(self, size: int, hash_count: int):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [0] * size
    
    def _hashes(self, item: str):
        """生成多个哈希值"""
        for i in range(self.hash_count):
            yield (hash(f"{item}{i}") + hash(item)) % self.size
    
    def add(self, item: str):
        """添加元素"""
        for index in self._hashes(item):
            self.bit_array[index] = 1
    
    def __contains__(self, item: str) -> bool:
        """检查元素可能存在或肯定不存在"""
        return all(self.bit_array[index] for index in self._hashes(item))

# 使用示例
bf = BloomFilter(size=1000, hash_count=3)
bf.add("user1@example.com")
bf.add("user2@example.com")

print("user1@example.com" in bf)  # True
print("user3@example.com" in bf)  # 可能是 False 或 True（误报）
```

---

## 面试要点

### Q1: 为什么 MD5 不安全？

**答:** MD5 已被破解，存在以下问题：
1. **碰撞攻击**：2004年王小云团队证明可以在数小时内找到碰撞
2. **长度扩展攻击**：可以构造 `H(message || padding || extension)` 而不知道原消息
3. **彩虹表攻击**：无盐的 MD5 哈希容易被预计算表攻击

**绝对不要使用 MD5 用于密码存储或数字签名。**

### Q2: SHA-256 和 SHA-3 有什么区别？

**答:**

| 特性 | SHA-256 | SHA-3 |
|------|---------|-------|
| 设计 | Merkle-Damgård | 海绵结构 |
| 状态大小 | 256位 | 1600位 |
| 长度扩展攻击 | 易受攻击 | 天然免疫 |
| 性能 | 硬件加速快 | 软件实现好 |
| 设计目标 | 替代 SHA-1 | 提供算法多样性 |

两者都安全，SHA-256 更常用，SHA-3 提供不同设计的安全保证。

### Q3: 什么是盐 (Salt)？为什么需要它？

**答:** 盐是随机数据，与密码一起哈希，解决以下问题：

1. **彩虹表攻击**：预计算的哈希表失效
2. **相同密码识别**：相同密码产生不同哈希
3. **并行攻击难度**：每个哈希需要单独计算

**最佳实践**：
- 每个密码使用不同的随机盐
- 盐长度至少 16 字节
- 盐与哈希一起存储

### Q4: HMAC 和普通哈希有什么区别？

**答:** HMAC (Hash-based Message Authentication Code) 使用密钥，提供：

1. **认证**：只有持有密钥才能生成有效 HMAC
2. **完整性**：消息被篡改会导致 HMAC 验证失败

HMAC 计算：`HMAC(K, m) = H((K' ⊕ opad) || H((K' ⊕ ipad) || m))`

**永远不要用 H(K||m) 或 H(m||K) 代替 HMAC**，它们都有安全缺陷。

### Q5: 如何选择密码哈希算法？

**答:** 推荐优先级：

1. **Argon2** (winner of Password Hashing Competition) - 首选
2. **bcrypt** - 广泛使用，安全
3. **scrypt** - 内存困难型，抗硬件攻击
4. **PBKDF2** - NIST 推荐，但较慢

**绝对不要使用**：MD5, SHA1, SHA256（没有密钥拉伸）

---

## 相关概念

- [对称加密](./symmetric-encryption.md) - 数据加密
- [数字签名](./digital-signatures.md) - 消息认证和不可否认性
- [身份认证](../application-security/authentication.md) - 密码存储

---

## 参考资料

1. NIST FIPS 180-4 - Secure Hash Standard (SHS)
2. NIST FIPS 202 - SHA-3 Standard
3. RFC 2104 - HMAC: Keyed-Hashing for Message Authentication
4. Password Hashing Competition - https://password-hashing.net/
5. "Cryptography Engineering" by Ferguson, Schneier, Kohno
