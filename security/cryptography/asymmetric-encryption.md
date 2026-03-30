# 非对称加密 (Asymmetric Encryption)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概念

**非对称加密 (Asymmetric Encryption)**，又称公钥密码学 (Public-Key Cryptography)，使用一对数学上相关联的密钥：公钥 (Public Key) 用于加密，私钥 (Private Key) 用于解密。这对密钥是独特的，从公钥无法推导出私钥。

```
┌─────────────────────────────────────────────────────────────────┐
│                   非对称加密原理                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   密钥对生成：                                                   │
│   ┌─────────────┐                                               │
│   │  密钥生成器  │───▶ 公钥 (Public Key) ───▶ 公开分发           │
│   │  Key Gen    │───▶ 私钥 (Private Key) ──▶ 保密存储           │
│   └─────────────┘                                               │
│                                                                 │
│   加密过程：                                                     │
│   明文 ───▶ [公钥加密] ───▶ 密文 ───▶ 传输 ───▶ [私钥解密]      │
│                                                          ▼      │
│                                                     明文        │
│                                                                 │
│   特点：                                                        │
│   • 使用密钥对（公钥 + 私钥）                                    │
│   • 公钥可公开，私钥必须保密                                     │
│   • 解决了密钥分发问题                                           │
│   • 运算速度慢（比对称加密慢100-1000倍）                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## RSA 算法

### 原理

RSA (Rivest-Shamir-Adleman) 于1977年提出，是最早的实用非对称加密算法，基于大整数分解的数学难题。

```
┌─────────────────────────────────────────────────────────────────┐
│                   RSA 算法原理                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   数学基础：                                                     │
│   • 选择两个大素数 p 和 q                                       │
│   • 计算 n = p × q （模数，通常2048位或更大）                    │
│   • 计算 φ(n) = (p-1)(q-1)                                      │
│   • 选择 e 使得 1 < e < φ(n) 且 gcd(e, φ(n)) = 1               │
│   • 计算 d ≡ e⁻¹ (mod φ(n))                                     │
│                                                                 │
│   密钥：                                                         │
│   • 公钥: (n, e)                                                │
│   • 私钥: (n, d)                                                │
│                                                                 │
│   加密：c = m^e mod n                                           │
│   解密：m = c^d mod n                                           │
│                                                                 │
│   安全性基于：                                                   │
│   • 大整数分解难题                                               │
│   • 已知 n，难以分解出 p 和 q                                   │
│                                                                 │
│   推荐密钥长度：                                                 │
│   • 2048位：当前最小推荐                                         │
│   • 3072位：长期安全                                             │
│   • 4096位：超高安全                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Python 实现

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# 生成 RSA 密钥对
def generate_rsa_keypair(key_size=2048):
    """生成 RSA 密钥对"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # 常用的公钥指数
        key_size=key_size
    )
    public_key = private_key.public_key()
    return private_key, public_key

# RSA 加密
def rsa_encrypt(public_key, plaintext: bytes) -> bytes:
    """使用公钥加密"""
    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# RSA 解密
def rsa_decrypt(private_key, ciphertext: bytes) -> bytes:
    """使用私钥解密"""
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

# 密钥序列化
def serialize_keys(private_key, public_key):
    """序列化密钥为 PEM 格式"""
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem

# 使用示例
private_key, public_key = generate_rsa_keypair(2048)
message = b"Hello, RSA Encryption!"

encrypted = rsa_encrypt(public_key, message)
decrypted = rsa_decrypt(private_key, encrypted)

print(f"原始消息: {message.decode()}")
print(f"解密消息: {decrypted.decode()}")
```

---

## ECC 椭圆曲线加密

### 原理

ECC (Elliptic Curve Cryptography) 基于椭圆曲线离散对数问题，在相同安全级别下使用更短的密钥。

```
┌─────────────────────────────────────────────────────────────────┐
│                   ECC 椭圆曲线加密                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   椭圆曲线方程：y² = x³ + ax + b (mod p)                        │
│                                                                 │
│   曲线上的点运算：                                               │
│   • 点加法：P + Q = R                                           │
│   • 点倍乘：k × P = P + P + ... + P (k次)                       │
│                                                                 │
│   ┌──────────────────────────────────────────────┐             │
│   │                                              │             │
│   │           P + Q = R                          │             │
│   │             \                                │             │
│   │              \                               │             │
│   │       P       \       Q                      │             │
│   │        ●       \       ●                     │             │
│   │         \       \     /                      │             │
│   │          \       \   /                       │             │
│   │           \       \ /                        │             │
│   │            \       X                         │             │
│   │             \     / \                        │             │
│   │              \   /   \                       │             │
│   │               \ /     \                      │             │
│   │                ●───────● (延长线交曲线于 -R) │             │
│   │                 R                            │             │
│   │                                              │             │
│   └──────────────────────────────────────────────┘             │
│                                                                 │
│   安全性：                                                       │
│   • 已知 P 和 k×P，难以计算 k（椭圆曲线离散对数问题）           │
│                                                                 │
│   密钥长度对比（相同安全级别）：                                 │
│   ┌─────────────┬─────────────┬─────────────────┐              │
│   │ 安全级别    │ RSA         │ ECC             │              │
│   ├─────────────┼─────────────┼─────────────────┤              │
│   │ 128-bit     │ 3072-bit    │ 256-bit         │              │
│   │ 192-bit     │ 7680-bit    │ 384-bit         │              │
│   │ 256-bit     │ 15360-bit   │ 521-bit         │              │
│   └─────────────┴─────────────┴─────────────────┘              │
│                                                                 │
│   优势：                                                         │
│   • 更短的密钥，更快的运算                                       │
│   • 更低的带宽和存储需求                                         │
│   • 更适合移动设备和物联网                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 常用椭圆曲线

```python
from cryptography.hazmat.primitives.asymmetric import ec

# 常用曲线：
# - SECP256R1 (P-256)：最常用，128位安全级别
# - SECP384R1 (P-384)：192位安全级别
# - SECP521R1 (P-521)：256位安全级别
# - Curve25519：现代设计，高性能
# - Curve448：更高安全级别

# ECC 密钥生成
def generate_ecc_keypair(curve=ec.SECP256R1()):
    """生成 ECC 密钥对"""
    private_key = ec.generate_private_key(curve)
    public_key = private_key.public_key()
    return private_key, public_key

# ECC 加密（使用 ECIES 方案）
def ecc_encrypt(public_key, plaintext: bytes) -> bytes:
    """ECC 加密 - 使用临时密钥对生成共享密钥"""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import os
    
    # 生成临时密钥对
    temp_private_key = ec.generate_private_key(ec.SECP256R1())
    temp_public_key = temp_private_key.public_key()
    
    # 计算共享密钥
    shared_key = temp_private_key.exchange(ec.ECDH(), public_key)
    
    # 使用共享密钥派生加密密钥
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data'
    ).derive(shared_key)
    
    # AES-GCM 加密
    nonce = os.urandom(12)
    aesgcm = AESGCM(derived_key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    # 返回临时公钥 + nonce + 密文
    temp_public_bytes = temp_public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    return temp_public_bytes + nonce + ciphertext
```

---

## Diffie-Hellman 密钥交换

### 原理

Diffie-Hellman (DH) 允许两方在不安全的信道上协商共享密钥，是建立安全连接的基础。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Diffie-Hellman 密钥交换                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   公开参数：大素数 p，生成元 g                                   │
│                                                                 │
│   Alice                          Bob                            │
│   ─────                          ────                           │
│                                                                 │
│   选择私钥 a                     选择私钥 b                     │
│   计算 A = g^a mod p             计算 B = g^b mod p             │
│                                                                 │
│        ┌───────────────────────────────┐                        │
│        │         A ───────────▶        │                        │
│        │         ◀─────────── B        │                        │
│        │     （公开信道传输）          │                        │
│        └───────────────────────────────┘                        │
│                                                                 │
│   计算 s = B^a mod p             计算 s = A^b mod p             │
│        = (g^b)^a mod p                = (g^a)^b mod p           │
│        = g^(ab) mod p                 = g^(ab) mod p            │
│                                                                 │
│   ═══════════════════════════════════════                       │
│   s 是相同的共享密钥！                                           │
│   ═══════════════════════════════════════                       │
│                                                                 │
│   安全性：窃听者知道 p, g, A, B，但无法计算 g^(ab)              │
│   （离散对数难题）                                               │
│                                                                 │
│   ECDH (Elliptic Curve Diffie-Hellman)：                        │
│   • 使用椭圆曲线代替模运算                                       │
│   • 更高效，密钥更短                                             │
│   • TLS 1.3 的主要密钥交换方式                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Python 实现

```python
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# DH 密钥交换示例
def dh_key_exchange():
    """Diffie-Hellman 密钥交换示例"""
    # 生成 DH 参数
    parameters = dh.generate_parameters(generator=2, key_size=2048)
    
    # Alice 生成密钥对
    alice_private = parameters.generate_private_key()
    alice_public = alice_private.public_key()
    
    # Bob 生成密钥对
    bob_private = parameters.generate_private_key()
    bob_public = bob_private.public_key()
    
    # 交换公钥并计算共享密钥
    alice_shared = alice_private.exchange(bob_public)
    bob_shared = bob_private.exchange(alice_public)
    
    # 验证共享密钥相同
    assert alice_shared == bob_shared
    
    # 使用 HKDF 派生最终密钥
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data'
    ).derive(alice_shared)
    
    return derived_key

# ECDH 密钥交换
def ecdh_key_exchange():
    """ECDH 密钥交换示例"""
    # Alice
    alice_private = ec.generate_private_key(ec.SECP256R1())
    alice_public = alice_private.public_key()
    
    # Bob
    bob_private = ec.generate_private_key(ec.SECP256R1())
    bob_public = bob_private.public_key()
    
    # 交换公钥
    alice_shared = alice_private.exchange(ec.ECDH(), bob_public)
    bob_shared = bob_private.exchange(ec.ECDH(), alice_public)
    
    # 派生密钥
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data'
    ).derive(alice_shared)
    
    return derived_key
```

---

## 混合加密系统

实际应用中，通常结合对称和非对称加密的优点：

```
┌─────────────────────────────────────────────────────────────────┐
│                   混合加密系统                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   加密过程：                                                     │
│   1. 生成随机会话密钥 (对称密钥)                                 │
│   2. 用对称加密加密大数据                                        │
│   3. 用接收方公钥加密会话密钥                                    │
│   4. 发送：加密数据 + 加密的会话密钥                             │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  明文数据                                               │   │
│   │     │                                                   │   │
│   │     ▼                                                   │   │
│   │  ┌─────────────┐    ┌─────────────┐                    │   │
│   │  │  随机生成    │    │  对称加密    │                    │   │
│   │  │  会话密钥 K  │───▶│  AES-GCM    │───▶ 加密数据       │   │
│   │  └─────────────┘    └─────────────┘                    │   │
│   │         │                                               │   │
│   │         ▼                                               │   │
│   │  ┌─────────────┐    ┌─────────────┐                    │   │
│   │  │  接收方公钥  │───▶│  非对称加密  │───▶ 加密密钥       │   │
│   │  │  Public Key │    │  RSA/ECC    │                    │   │
│   │  └─────────────┘    └─────────────┘                    │   │
│   │                                                         │   │
│   │  传输: [加密数据] + [加密密钥]                           │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   解密过程：                                                     │
│   1. 用私钥解密获取会话密钥                                      │
│   2. 用会话密钥解密数据                                          │
│                                                                 │
│   应用：PGP/GPG、TLS/SSL、S/MIME 等都使用混合加密               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

### Q1: RSA 和 ECC 的主要区别？

**答:**

| 特性 | RSA | ECC |
|------|-----|-----|
| 数学基础 | 大整数分解 | 椭圆曲线离散对数 |
| 密钥长度（128位安全） | 3072位 | 256位 |
| 性能 | 较慢 | 更快 |
| 签名长度 | 与密钥等长 | 更短 |
| 成熟度 | 更成熟 | 较新但已广泛采用 |
| 量子抗性 | 易被 Shor 算法破解 | 易被 Shor 算法破解 |

ECC 在资源受限环境（移动设备、物联网）更有优势。

### Q2: 为什么非对称加密不直接加密大量数据？

**答:** 
1. **性能问题**：非对称加密比对称加密慢 100-1000 倍
2. **数据限制**：RSA 最多只能加密密钥长度减去填充长度的数据
3. **最佳实践**：使用混合加密——非对称加密交换对称密钥，对称加密加密实际数据

### Q3: 什么是前向保密 (Forward Secrecy)？

**答:** 前向保密是指即使长期私钥在未来被泄露，过去的会话密钥也不会被破解。

实现方式：
- 每次会话使用临时的 DH/ECDH 密钥交换
- 会话密钥不存储
- 即使私钥泄露，也无法解密历史流量

TLS 1.3 强制要求前向保密。

### Q4: 中间人攻击如何防御？

**答:** 
1. **公钥认证**：使用数字证书绑定身份和公钥
2. **证书链验证**：验证证书由可信 CA 签发
3. **证书固定**：预先知道服务器公钥或证书指纹
4. **透明证书**：Certificate Transparency 日志监控

---

## 相关概念

- [对称加密](./symmetric-encryption.md) - 共享密钥加密
- [数字签名](./digital-signatures.md) - 消息认证和不可否认性
- [PKI](./pki.md) - 公钥基础设施
- [SSL/TLS](./ssl-tls.md) - 安全传输协议

---

## 参考资料

1. RFC 8017 - RSA Cryptography Specifications Version 2.2
2. NIST SP 800-56A - Recommendation for Pair-Wise Key-Establishment Schemes
3. SEC 1 - Elliptic Curve Cryptography Standards
4. "Introduction to Modern Cryptography" by Katz and Lindell
5. OWASP Cryptographic Storage Cheat Sheet
