# 对称加密 (Symmetric Encryption)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概念

**对称加密 (Symmetric Encryption)** 是指加密和解密使用相同密钥的加密算法。对称加密的主要特点是运算速度快，适合加密大量数据，但密钥分发和管理是主要挑战。

```
┌─────────────────────────────────────────────────────────────────┐
│                   对称加密原理                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   明文 (Plaintext)                                              │
│      │                                                          │
│      ▼                                                          │
│   ┌─────────────┐                                               │
│   │  加密算法    │◀──── 共享密钥 (Shared Key)                    │
│   │  Encryption │                                               │
│   └─────────────┘                                               │
│      │                                                          │
│      ▼                                                          │
│   密文 (Ciphertext) ─────────────▶ 传输                         │
│                                      │                          │
│                                      ▼                          │
│   ┌─────────────┐                                               │
│   │  解密算法    │◀──── 共享密钥 (Shared Key)                    │
│   │  Decryption │                                               │
│   └─────────────┘                                               │
│      │                                                          │
│      ▼                                                          │
│   明文 (Plaintext)                                              │
│                                                                 │
│   特点：                                                        │
│   • 加密解密使用同一密钥                                         │
│   • 运算速度快                                                   │
│   • 密钥分发是主要挑战                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 常见对称加密算法

### 1. AES (Advanced Encryption Standard)

AES 是目前最广泛使用的对称加密算法，由美国国家标准与技术研究院 (NIST) 于2001年确立为标准，取代 DES。

```
┌─────────────────────────────────────────────────────────────────┐
│                   AES 算法结构                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   密钥长度：128/192/256 位                                       │
│   分组长度：128 位（16字节）                                     │
│   轮数：10/12/14 轮（根据密钥长度）                              │
│                                                                 │
│   每轮操作：                                                     │
│   ┌─────────────┐                                               │
│   │ SubBytes    │  字节替换（S盒）                               │
│   │ ShiftRows   │  行移位                                        │
│   │ MixColumns  │  列混淆                                        │
│   │ AddRoundKey │  轮密钥加                                      │
│   └─────────────┘                                               │
│                                                                 │
│   安全性：                                                       │
│   • AES-256 提供军事级加密                                       │
│   • 目前无实用攻击方法                                           │
│   • 量子计算攻击需要 Grover 算法（平方根加速）                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2. DES 和 3DES

DES (Data Encryption Standard) 是1977年确立的旧标准，现已被破解，不再安全。3DES (Triple DES) 通过三次 DES 运算提高安全性。

```
┌─────────────────────────────────────────────────────────────────┐
│                   DES vs 3DES                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   DES：                                                         │
│   • 密钥长度：56位（过短）                                       │
│   • 1999年被分布式计算破解                                       │
│   • 2016年NIST宣布不再批准使用                                   │
│                                                                 │
│   3DES (Triple DES)：                                           │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                    │
│   │  DES    │───▶│  DES⁻¹  │───▶│  DES    │                    │
│   │ 加密    │    │ 解密    │    │ 加密    │                    │
│   └─────────┘    └─────────┘    └─────────┘                    │
│      K1             K2             K1 或 K3                     │
│                                                                 │
│   • 有效密钥长度：112位                                          │
│   • 运算速度慢（3倍 DES）                                        │
│   • 2017年Sweet32攻击证明了64位分组密码的弱点                   │
│   • 已逐步被淘汰                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3. ChaCha20

ChaCha20 是 Salsa20 的改进版本，由 Daniel J. Bernstein 设计。它在软件实现中比 AES 更快，且能抵抗时序攻击。

```
┌─────────────────────────────────────────────────────────────────┐
│                   ChaCha20 特点                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   设计优势：                                                     │
│   • 纯软件实现，无硬件依赖                                       │
│   • 在移动设备上比 AES 快                                        │
│   • 天然抵抗时序攻击                                             │
│   • 简单的算法结构，易于审计                                     │
│                                                                 │
│   使用场景：                                                     │
│   • Google 用于 QUIC 协议和 TLS                                  │
│   • WireGuard VPN 的默认加密算法                                 │
│   • OpenSSH 的现代加密选项                                       │
│   • TLS 1.3 的 AEAD 选项                                         │
│                                                                 │
│   与 Poly1305 组合使用形成 ChaCha20-Poly1305                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 加密模式

### 分组密码模式

```
┌─────────────────────────────────────────────────────────────────┐
│                   分组密码工作模式                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ECB (Electronic Codebook) - 电子密码本模式：                  │
│   ┌─────┐  ┌─────┐  ┌─────┐                                    │
│   │ P1  │  │ P2  │  │ P3  │  相同明文 → 相同密文               │
│   └──┬──┘  └──┬──┘  └──┬──┘  ❌ 不安全，不推荐                 │
│      ▼        ▼        ▼                                       │
│   ┌─────┐  ┌─────┐  ┌─────┐                                    │
│   │ EK  │  │ EK  │  │ EK  │                                    │
│   └──┬──┘  └──┬──┘  └──┬──┘                                    │
│      ▼        ▼        ▼                                       │
│   ┌─────┐  ┌─────┐  ┌─────┐                                    │
│   │ C1  │  │ C2  │  │ C3  │                                    │
│   └─────┘  └─────┘  └─────┘                                    │
│                                                                 │
│   CBC (Cipher Block Chaining) - 密码块链接模式：                │
│   ┌─────┐  ┌─────┐  ┌─────┐                                    │
│   │ P1  │  │ P2  │  │ P3  │                                    │
│   └──┬──┘  └──┬──┘  └──┬──┘                                    │
│   IV│▼     ┌──┴──┐  ┌──┴──┐                                    │
│   ┌─┴───┐  │ ⊕   │  │ ⊕   │  前一个密文块与当前明文异或         │
│   │ EK  │  └──┬──┘  └──┬──┘  ✅ 常用，需要填充                 │
│   └──┬──┘     ▼        ▼                                       │
│      └─────▶┌───┐   ┌───┐                                      │
│   ┌─────┐   │EK │   │EK │                                      │
│   │ C1  │◀──┴───┘   └───┘                                      │
│   └──┬──┘        └──────▶┌───┐                                 │
│      └──────────────────▶│ C3│                                 │
│                          └───┘                                 │
│                                                                 │
│   CTR (Counter) - 计数器模式：                                  │
│   ┌─────┐  ┌─────┐  ┌─────┐                                    │
│   │ IV  │  │IV+1 │  │IV+2 │  计数器加密后与明文异或             │
│   └──┬──┘  └──┬──┘  └──┬──┘  ✅ 并行加密，无需填充             │
│      ▼        ▼        ▼                                       │
│   ┌─────┐  ┌─────┐  ┌─────┐                                    │
│   │ EK  │  │ EK  │  │ EK  │                                    │
│   └──┬──┘  └──┬──┘  └──┬──┘                                    │
│      ▼        ▼        ▼                                       │
│   ┌─────┐  ┌─────┐  ┌─────┐                                    │
│   │ K1  │  │ K2  │  │ K3  │  密钥流                            │
│   └──┬──┘  └──┬──┘  └──┬──┘                                    │
│   P1 │▼     P2│▼     P3│▼                                       │
│   ┌──┴──┐  ┌──┴──┐  ┌──┴──┐                                    │
│   │ ⊕   │  │ ⊕   │  │ ⊕   │                                    │
│   └──┬──┘  └──┬──┘  └──┬──┘                                    │
│      ▼        ▼        ▼                                       │
│   ┌─────┐  ┌─────┐  ┌─────┐                                    │
│   │ C1  │  │ C2  │  │ C3  │                                    │
│   └─────┘  └─────┘  └─────┘                                    │
│                                                                 │
│   GCM (Galois/Counter Mode) - 认证加密模式：                    │
│   • 提供加密和认证（完整性保护）                                 │
│   • 同时输出密文和认证标签 (Authentication Tag)                  │
│   • TLS 1.3 的推荐模式                                           │
│   • 并行处理，性能优秀                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 代码示例

### Python 使用 cryptography 库

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# AES-256-GCM 加密示例
def aes_gcm_encrypt(plaintext: bytes, key: bytes) -> tuple:
    """AES-256-GCM 加密"""
    # 生成随机 IV（12字节是 GCM 推荐值）
    iv = os.urandom(12)
    
    # 创建加密器
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()
    
    # 加密数据
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    
    # 返回密文、IV 和认证标签
    return ciphertext, iv, encryptor.tag

def aes_gcm_decrypt(ciphertext: bytes, key: bytes, iv: bytes, tag: bytes) -> bytes:
    """AES-256-GCM 解密"""
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    
    return decryptor.update(ciphertext) + decryptor.finalize()

# 使用示例
key = os.urandom(32)  # 256位密钥
plaintext = b"Hello, World! This is a secret message."

# 加密
ciphertext, iv, tag = aes_gcm_encrypt(plaintext, key)
print(f"密文: {ciphertext.hex()}")

# 解密
decrypted = aes_gcm_decrypt(ciphertext, key, iv, tag)
print(f"解密: {decrypted.decode()}")
```

### ChaCha20-Poly1305 示例

```python
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

# ChaCha20-Poly1305 加密
def chacha_encrypt(plaintext: bytes, key: bytes, aad: bytes = None) -> tuple:
    """ChaCha20-Poly1305 加密"""
    nonce = os.urandom(12)  # 96位 nonce
    chacha = ChaCha20Poly1305(key)
    ciphertext = chacha.encrypt(nonce, plaintext, aad)
    return ciphertext, nonce

def chacha_decrypt(ciphertext: bytes, key: bytes, nonce: bytes, aad: bytes = None) -> bytes:
    """ChaCha20-Poly1305 解密"""
    chacha = ChaCha20Poly1305(key)
    return chacha.decrypt(nonce, ciphertext, aad)

# 使用示例
key = os.urandom(32)  # 256位密钥
plaintext = b"Secret data"
aad = b"additional authenticated data"

ciphertext, nonce = chacha_encrypt(plaintext, key, aad)
decrypted = chacha_decrypt(ciphertext, key, nonce, aad)
```

### 密钥派生示例

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes

# 从密码派生密钥
def derive_key(password: str, salt: bytes, iterations: int = 100000) -> bytes:
    """使用 PBKDF2 从密码派生密钥"""
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode())

# 使用示例
password = "user_password"
salt = os.urandom(16)
key = derive_key(password, salt)
print(f"派生密钥: {key.hex()}")
```

---

## 密钥管理最佳实践

```
┌─────────────────────────────────────────────────────────────────┐
│                   密钥管理原则                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. 密钥生成：                                                  │
│      • 使用密码学安全的随机数生成器 (CSPRNG)                     │
│      • Python: os.urandom() 或 secrets.token_bytes()           │
│      • 避免使用弱随机源 (random.random())                       │
│                                                                 │
│   2. 密钥存储：                                                  │
│      • 从不硬编码密钥在源代码中                                  │
│      • 使用密钥管理系统 (KMS) 或硬件安全模块 (HSM)              │
│      • 环境变量或密钥管理服务优于配置文件                        │
│                                                                 │
│   3. 密钥轮换：                                                  │
│      • 定期更换加密密钥                                          │
│      • 实施密钥版本控制                                          │
│      • 保留旧密钥用于解密历史数据                                │
│                                                                 │
│   4. 密钥销毁：                                                  │
│      • 安全擦除内存中的密钥                                      │
│      • 覆盖而非仅仅释放内存                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

### Q1: 对称加密和非对称加密的区别？

**答:**

| 特性 | 对称加密 | 非对称加密 |
|------|----------|------------|
| 密钥 | 单密钥，加密解密相同 | 密钥对（公钥/私钥） |
| 速度 | 快（适合大数据） | 慢（适合小数据） |
| 用途 | 数据加密 | 密钥交换、数字签名 |
| 算法 | AES, ChaCha20 | RSA, ECC |
| 密钥分发 | 困难 | 容易（公钥可公开） |

### Q2: 为什么不推荐使用 ECB 模式？

**答:** ECB (Electronic Codebook) 模式将每个数据块独立加密，相同明文块产生相同密文块。这会导致：
1. **模式泄露**：密文中的模式反映了明文中的模式
2. **重放攻击**：攻击者可以识别和替换密文块
3. **缺乏语义安全**：无法抵抗选择明文攻击

推荐使用 CBC、CTR 或 GCM 模式。GCM 还提供认证功能。

### Q3: AES-256 比 AES-128 安全多少？

**答:** AES-256 使用 256 位密钥，而 AES-128 使用 128 位密钥。从数学角度：
- AES-128：2^128 次尝试才能暴力破解
- AES-256：2^256 次尝试才能暴力破解

实际上两者都非常安全，AES-128 已经足够抵抗所有已知的攻击。AES-256 主要用于：
- 高安全要求的场景（军事、政府）
- 需要抵抗量子计算的长期保密（Grover 算法将搜索空间减半，AES-256 仍有 2^128 的安全性）

### Q4: ChaCha20 相比 AES 有什么优势？

**答:** 
1. **软件性能**：ChaCha20 在纯软件实现中通常比 AES 快，特别是在没有 AES-NI 指令集的设备上
2. **时序安全**：ChaCha20 自然抵抗时序攻击，AES 需要小心实现
3. **简单性**：算法结构简单，更容易正确实现和审计
4. **移动端优势**：在 ARM 架构上表现优异

---

## 相关概念

- [非对称加密](./asymmetric-encryption.md) - 公钥密码学
- [哈希函数](./hash-functions.md) - 单向散列
- [数字签名](./digital-signatures.md) - 消息认证
- [证书](./certificates.md) - 数字证书与公钥绑定
- [PKI](./pki.md) - 公钥基础设施
- [身份认证](../authentication.md) - 用户身份验证
- [授权](../authorization.md) - 访问权限控制
- [HTTPS/TLS](../https-tls.md) - 传输层安全协议
- [内存寻址](../computer-science/systems/memory-addressing.md) - 内存与加密密钥存储
- [授权](../network-security/authorization.md) - 访问权限控制
- [HTTPS/TLS](../network-security/https-tls.md) - 传输层安全协议
- [内存寻址](../../computer-science/systems/memory-addressing.md) - 内存与加密密钥存储
---

## 参考资料

1. NIST FIPS 197 - Advanced Encryption Standard (AES)
2. RFC 8439 - ChaCha20 and Poly1305 for IETF Protocols
3. "Cryptography Engineering" by Ferguson, Schneier, Kohno
4. OWASP Cryptographic Storage Cheat Sheet
5. IETF TLS 1.3 RFC 8446
