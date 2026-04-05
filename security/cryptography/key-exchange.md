# 密钥交换 (Key Exchange)

## 简介

密钥交换(Key Exchange)是在不安全通信信道上安全协商共享密钥的密码学协议。它解决了对称加密中的核心难题：如何在不预先共享密钥的情况下建立安全通信。

Diffie-Hellman密钥交换(1976)是首个实用的公钥密码学方案，开创了现代密码学的新纪元。后续的ECDH(椭圆曲线Diffie-Hellman)、Post-Quantum密钥交换等不断增强了安全性和效率。

密钥交换协议必须抵抗中间人攻击(Man-in-the-Middle Attack)，通常结合数字签名或预共享密钥进行身份认证。

## 核心概念

### 1. Diffie-Hellman密钥交换

```
Alice                          公开信道                         Bob
┌─────────┐                                                   ┌─────────┐
│ 选择 a  │                                                   │ 选择 b  │
│ (私钥)  │                                                   │ (私钥)  │
└────┬────┘                                                   └────┬────┘
     │                                                             │
     │  A = gᵃ mod p                                               │  B = gᵇ mod p
     │  (公钥)                                                     │  (公钥)
     │                                                             │
     └────────────────────>  A, B  <───────────────────────────────┘
                           (交换公钥)
     │                                                             │
     │  s = Bᵃ mod p                                               │  s = Aᵇ mod p
     │    = (gᵇ)ᵃ mod p                                            │    = (gᵃ)ᵇ mod p
     │    = gᵃᵇ mod p                                              │    = gᵃᵇ mod p
     │                                                             │
     └────────────────────────  s  ────────────────────────────────┘
                           (共享密钥)

攻击者Eve看到: g, p, A, B，但计算gᵃᵇ mod p是困难的(离散对数问题)
```

### 2. 离散对数问题

给定素数p，生成元g，和gᵃ mod p，求a在计算上是不可行的。

| 问题类型 | 数学基础 | 经典难度 | 量子威胁 |
|---------|---------|---------|---------|
| 整数分解 | n = pq | RSA安全 | Shor算法破解 |
| 离散对数 | gᵃ ≡ b (mod p) | DH/DSA安全 | Shor算法破解 |
| 椭圆曲线离散对数 | aG = Q | ECC安全 | Shor算法破解 |

### 3. ECDH (椭圆曲线Diffie-Hellman)

```
Alice私钥: dₐ (随机数)
Alice公钥: Qₐ = dₐ × G

Bob私钥: dᵦ (随机数)
Bob公钥: Qᵦ = dᵦ × G

共享密钥: s = dₐ × Qᵦ = dᵦ × Qₐ = dₐ × dᵦ × G
```

**优势**: 相同安全级别下，ECC密钥比DH短得多(256位ECC ≈ 3072位DH)

### 4. 密钥派生

原始共享密钥不能直接用于加密，需要通过KDF派生：

```
共享密钥 s
     ↓
[HKDF] 或 [PBKDF2] 或 [Argon2]
     ↓
加密密钥 + IV + MAC密钥
```

## 实现方式

### 基础Diffie-Hellman

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dh, ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import os

class DiffieHellman:
    """Diffie-Hellman 密钥交换实现"""
    
    def __init__(self):
        self.backend = default_backend()
        self.private_key = None
        self.public_key = None
        self.shared_secret = None
    
    @staticmethod
    def generate_parameters(key_size=2048):
        """
        生成DH参数 (通常由服务器预设)
        
        标准参数: RFC 3526 (MODP groups)
        """
        parameters = dh.generate_parameters(
            generator=2,
            key_size=key_size,
            backend=default_backend()
        )
        return parameters
    
    @classmethod
    def generate_key_pair(cls, parameters=None, key_size=2048):
        """生成DH密钥对"""
        instance = cls()
        
        if parameters is None:
            parameters = cls.generate_parameters(key_size)
        
        instance.private_key = parameters.generate_private_key()
        instance.public_key = instance.private_key.public_key()
        
        return instance
    
    def compute_shared_secret(self, peer_public_key) -> bytes:
        """
        计算共享密钥
        
        返回原始共享密钥(大整数)
        """
        if not self.private_key:
            raise ValueError("Private key required")
        
        self.shared_secret = self.private_key.exchange(peer_public_key)
        return self.shared_secret
    
    def derive_key(self, length=32, info=b'handshake data') -> bytes:
        """
        使用HKDF派生加密密钥
        
        HKDF: HMAC-based Extract-and-Expand Key Derivation Function
        """
        if not self.shared_secret:
            raise ValueError("Must compute shared secret first")
        
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=None,
            info=info,
            backend=self.backend
        ).derive(self.shared_secret)
        
        return derived_key

# 使用示例
def demo_dh_exchange():
    """演示完整的DH密钥交换"""
    # 生成参数 (实际中服务端预生成)
    params = DiffieHellman.generate_parameters(2048)
    
    # Alice生成密钥对
    alice = DiffieHellman.generate_key_pair(params)
    
    # Bob生成密钥对
    bob = DiffieHellman.generate_key_pair(params)
    
    # 交换公钥并计算共享密钥
    alice_shared = alice.compute_shared_secret(bob.public_key)
    bob_shared = bob.compute_shared_secret(alice.public_key)
    
    # 验证共享密钥相同
    assert alice_shared == bob_shared
    
    # 派生加密密钥
    alice_key = alice.derive_key(length=32, info=b'encryption')
    bob_key = bob.derive_key(length=32, info=b'encryption')
    
    assert alice_key == bob_key
    print("DH密钥交换成功!")
    return alice_key
```

### ECDH 椭圆曲线密钥交换

```python
class ECDHKeyExchange:
    """ECDH 椭圆曲线密钥交换"""
    
    CURVES = {
        'secp256r1': ec.SECP256R1(),  # NIST P-256, 最常用
        'secp384r1': ec.SECP384R1(),  # NIST P-384, 高安全
        'secp521r1': ec.SECP521R1(),  # NIST P-521, 最高
        'secp256k1': ec.SECP256K1(),  # 比特币
        'x25519': ec.X25519(),        # Curve25519, 现代推荐
        'x448': ec.X448(),            # Curve448, 高安全
    }
    
    def __init__(self, curve_name='secp256r1'):
        self.backend = default_backend()
        self.curve = self.CURVES.get(curve_name, ec.SECP256R1())
        self.private_key = None
        self.public_key = None
        self.shared_secret = None
    
    @classmethod
    def generate_key_pair(cls, curve_name='secp256r1'):
        """生成ECDH密钥对"""
        instance = cls(curve_name=curve_name)
        
        if curve_name in ['x25519', 'x448']:
            # X25519/X448使用不同的API
            from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
            from cryptography.hazmat.primitives.asymmetric.x448 import X448PrivateKey
            
            if curve_name == 'x25519':
                instance.private_key = X25519PrivateKey.generate()
            else:
                instance.private_key = X448PrivateKey.generate()
        else:
            instance.private_key = ec.generate_private_key(
                instance.curve,
                instance.backend
            )
        
        instance.public_key = instance.private_key.public_key()
        return instance
    
    def compute_shared_secret(self, peer_public_key) -> bytes:
        """计算ECDH共享密钥"""
        if not self.private_key:
            raise ValueError("Private key required")
        
        self.shared_secret = self.private_key.exchange(
            ec.ECDH(),
            peer_public_key
        )
        return self.shared_secret
    
    def derive_keys(self, info=b'handshake') -> dict:
        """
        派生多个密钥
        
        产生: 加密密钥, MAC密钥, IV
        """
        if not self.shared_secret:
            raise ValueError("Must compute shared secret first")
        
        # 派生64字节，分割为多个密钥
        master_key = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=None,
            info=info,
            backend=self.backend
        ).derive(self.shared_secret)
        
        return {
            'encryption_key': master_key[:32],
            'mac_key': master_key[32:48],
            'iv_seed': master_key[48:64]
        }

# X25519现代实现
def modern_ecdh():
    """使用X25519的现代密钥交换"""
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
    
    # Alice
    alice_private = X25519PrivateKey.generate()
    alice_public = alice_private.public_key()
    
    # Bob
    bob_private = X25519PrivateKey.generate()
    bob_public = bob_private.public_key()
    
    # 共享密钥
    alice_shared = alice_private.exchange(bob_public)
    bob_shared = bob_private.exchange(alice_public)
    
    assert alice_shared == bob_shared
    
    # 派生AES密钥
    key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'X25519 key exchange',
        backend=default_backend()
    ).derive(alice_shared)
    
    return key
```

### 带认证的密钥交换 (Authenticated DH)

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class AuthenticatedDH:
    """
    带认证的Diffie-Hellman
    
    防止中间人攻击，通过数字签名验证身份
    """
    
    def __init__(self, dh_params=None):
        self.dh = DiffieHellman()
        self.dh_params = dh_params
        self.signature_key = None  # 长期签名密钥
    
    def generate_identity_key(self):
        """生成长期身份密钥(用于签名)"""
        self.signature_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        return self.signature_key.public_key()
    
    def initiate_handshake(self) -> dict:
        """
        发起密钥交换握手
        
        返回: DH公钥 + 签名
        """
        # 生成临时DH密钥对
        ephemeral = DiffieHellman.generate_key_pair(self.dh_params)
        
        # 签名DH公钥
        dh_public_bytes = ephemeral.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        signature = self.signature_key.sign(
            dh_public_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        self.ephemeral = ephemeral
        
        return {
            'dh_public': dh_public_bytes,
            'signature': signature,
            'identity_cert': self._get_identity_certificate()
        }
    
    def complete_handshake(self, peer_message: dict, 
                          peer_identity_key) -> bytes:
        """
        完成密钥交换
        
        验证签名后计算共享密钥
        """
        # 验证身份证书
        dh_public_bytes = peer_message['dh_public']
        signature = peer_message['signature']
        
        # 验证签名
        try:
            peer_identity_key.verify(
                signature,
                dh_public_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except Exception:
            raise ValueError("Invalid signature - possible MITM attack!")
        
        # 加载对方DH公钥
        peer_public_key = serialization.load_pem_public_key(
            dh_public_bytes,
            backend=default_backend()
        )
        
        # 计算共享密钥
        return self.ephemeral.compute_shared_secret(peer_public_key)
    
    def _get_identity_certificate(self):
        """获取身份证书(简化)"""
        return self.signature_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
```

### TLS 1.3风格密钥交换

```python
class TLS13KeyExchange:
    """
    TLS 1.3风格的密钥交换
    
    特点:
    - 1-RTT握手
    - 前向安全性
    - 密钥分离
    """
    
    def __init__(self):
        self.client_private = None
        self.server_private = None
        self.handshake_keys = {}
        self.application_keys = {}
    
    def client_hello(self) -> dict:
        """客户端发送ClientHello"""
        # 生成X25519密钥对
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
        
        self.client_private = X25519PrivateKey.generate()
        client_public = self.client_private.public_key()
        
        return {
            'client_public': client_public.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            ),
            'supported_groups': ['x25519', 'secp256r1'],
            'key_share': True
        }
    
    def server_hello(self, client_hello: dict) -> dict:
        """服务端响应ServerHello"""
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
        
        # 加载客户端公钥
        client_public = X25519PublicKey.from_public_bytes(
            client_hello['client_public']
        )
        
        # 生成服务端密钥对
        self.server_private = X25519PrivateKey.generate()
        server_public = self.server_private.public_key()
        
        # 计算共享密钥
        shared_secret = self.server_private.exchange(client_public)
        
        # 派生握手密钥
        self.handshake_keys = self._derive_handshake_keys(shared_secret)
        
        return {
            'server_public': server_public.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            ),
            'selected_group': 'x25519'
        }
    
    def client_finish(self, server_hello: dict) -> bytes:
        """客户端完成握手"""
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
        
        # 加载服务端公钥
        server_public = X25519PublicKey.from_public_bytes(
            server_hello['server_public']
        )
        
        # 计算共享密钥
        shared_secret = self.client_private.exchange(server_public)
        
        # 派生密钥
        self.handshake_keys = self._derive_handshake_keys(shared_secret)
        
        # 派生应用密钥
        self.application_keys = self._derive_application_keys()
        
        return self.application_keys['client_write_key']
    
    def _derive_handshake_keys(self, shared_secret: bytes) -> dict:
        """派生握手阶段密钥"""
        key_material = HKDF(
            algorithm=hashes.SHA256(),
            length=56,
            salt=None,
            info=b'tls13 handshake keys',
            backend=default_backend()
        ).derive(shared_secret)
        
        return {
            'client_write_key': key_material[:16],
            'server_write_key': key_material[16:32],
            'client_iv': key_material[32:44],
            'server_iv': key_material[44:56]
        }
    
    def _derive_application_keys(self) -> dict:
        """派生应用数据密钥"""
        # 简化实现
        return {
            'client_write_key': os.urandom(16),
            'server_write_key': os.urandom(16)
        }
```

## 应用场景

### 1. 安全聊天应用

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SecureChat:
    """端到端加密聊天"""
    
    def __init__(self):
        self.ecdh = None
        self.session_key = None
        self.message_counter = 0
    
    def initiate_chat(self) -> bytes:
        """发起加密会话"""
        self.ecdh = ECDHKeyExchange.generate_key_pair('x25519')
        
        # 返回公钥给对方
        return self.ecdh.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    def accept_chat(self, peer_public_bytes: bytes) -> bytes:
        """接受加密会话"""
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
        
        self.ecdh = ECDHKeyExchange.generate_key_pair('x25519')
        
        # 加载对方公钥
        peer_public = X25519PublicKey.from_public_bytes(peer_public_bytes)
        
        # 计算共享密钥
        shared = self.ecdh.compute_shared_secret(peer_public)
        self.session_key = self.ecdh.derive_keys(info=b'secure chat v1')
        
        # 返回自己的公钥
        return self.ecdh.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    def complete_chat(self, peer_public_bytes: bytes):
        """完成会话建立"""
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
        
        peer_public = X25519PublicKey.from_public_bytes(peer_public_bytes)
        shared = self.ecdh.compute_shared_secret(peer_public)
        self.session_key = self.ecdh.derive_keys(info=b'secure chat v1')
    
    def encrypt_message(self, plaintext: str) -> dict:
        """加密消息"""
        if not self.session_key:
            raise ValueError("Session not established")
        
        aesgcm = AESGCM(self.session_key['encryption_key'])
        
        # 使用计数器作为nonce
        nonce = self.message_counter.to_bytes(12, 'big')
        self.message_counter += 1
        
        ciphertext = aesgcm.encrypt(
            nonce, 
            plaintext.encode(),
            None
        )
        
        return {
            'nonce': nonce.hex(),
            'ciphertext': ciphertext.hex()
        }
    
    def decrypt_message(self, encrypted: dict) -> str:
        """解密消息"""
        aesgcm = AESGCM(self.session_key['encryption_key'])
        
        nonce = bytes.fromhex(encrypted['nonce'])
        ciphertext = bytes.fromhex(encrypted['ciphertext'])
        
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()
```

### 2. 文件加密传输

```python
class SecureFileTransfer:
    """安全文件传输"""
    
    def __init__(self):
        self.ecdh = None
        self.keys = None
    
    def sender_handshake(self) -> bytes:
        """发送方握手"""
        self.ecdh = ECDHKeyExchange.generate_key_pair('secp256r1')
        
        return self.ecdh.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
    
    def receiver_handshake(self, sender_public: bytes) -> bytes:
        """接收方握手"""
        # 加载发送方公钥
        peer_public = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256R1(),
            sender_public
        )
        
        # 生成密钥对
        self.ecdh = ECDHKeyExchange.generate_key_pair('secp256r1')
        
        # 计算共享密钥
        shared = self.ecdh.compute_shared_secret(peer_public)
        self.keys = self.ecdh.derive_keys(info=b'file transfer')
        
        return self.ecdh.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
    
    def sender_complete(self, receiver_public: bytes):
        """发送方完成"""
        peer_public = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256R1(),
            receiver_public
        )
        
        shared = self.ecdh.compute_shared_secret(peer_public)
        self.keys = self.ecdh.derive_keys(info=b'file transfer')
    
    def encrypt_file(self, file_path: str, output_path: str):
        """加密文件"""
        from pathlib import Path
        
        # 读取文件
        plaintext = Path(file_path).read_bytes()
        
        # 加密
        aesgcm = AESGCM(self.keys['encryption_key'])
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # 写入: nonce + ciphertext
        with open(output_path, 'wb') as f:
            f.write(nonce)
            f.write(ciphertext)
    
    def decrypt_file(self, encrypted_path: str, output_path: str):
        """解密文件"""
        with open(encrypted_path, 'rb') as f:
            nonce = f.read(12)
            ciphertext = f.read()
        
        aesgcm = AESGCM(self.keys['encryption_key'])
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        with open(output_path, 'wb') as f:
            f.write(plaintext)
```

### 3. IoT设备认证

```python
class IoTDeviceAuth:
    """IoT设备密钥交换认证"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.ecdh = None
        self.session_key = None
    
    def device_register(self, server_public_key) -> dict:
        """设备注册并建立密钥"""
        self.ecdh = ECDHKeyExchange.generate_key_pair('x25519')
        
        # 计算共享密钥
        shared = self.ecdh.compute_shared_secret(server_public_key)
        
        # 派生注册密钥
        reg_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=f'{self.device_id} registration'.encode(),
            backend=default_backend()
        ).derive(shared)
        
        return {
            'device_id': self.device_id,
            'public_key': self.ecdh.public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            ).hex(),
            'auth_token': reg_key.hex()[:16]  # 简化示例
        }
    
    def server_establish_session(self, device_public: bytes, 
                                  device_id: str) -> bytes:
        """服务端建立会话"""
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
        
        peer_public = X25519PublicKey.from_public_bytes(device_public)
        
        self.ecdh = ECDHKeyExchange.generate_key_pair('x25519')
        shared = self.ecdh.compute_shared_secret(peer_public)
        
        self.session_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=f'{device_id} session'.encode(),
            backend=default_backend()
        ).derive(shared)
        
        return self.ecdh.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
```

## 面试要点

### Q1: 什么是中间人攻击？DH如何防御？

**A:**
- **攻击**: 攻击者拦截通信，分别与双方建立独立密钥
- **防御**: 
  - 数字签名认证(带认证的DH)
  - 预共享密钥
  - 证书链验证(TLS)
  - 公钥指纹比对(SSH)

### Q2: 前向安全性(Forward Secrecy)是什么？

**A:**
- **定义**: 长期私钥泄露不会泄露过去的会话密钥
- **实现**: 使用临时(ephemeral)DH密钥，每次会话生成新密钥对
- **优势**: 即使服务器私钥被破解，历史通信仍安全
- **协议**: TLS 1.3强制前向安全，TLS 1.2可选

### Q3: ECDH相比DH的优势？

**A:**
- **密钥长度**: 256位ECC ≈ 3072位DH，节省带宽和存储
- **计算速度**: ECDH更快，特别是软件实现
- **能耗**: 更适合移动设备和IoT
- **安全性**: 相同密钥长度下，ECDLP比DLP更难

### Q4: 为什么共享密钥需要KDF派生？

**A:**
- **熵分布**: DH输出可能不均匀
- **多密钥**: 需要加密密钥、MAC密钥、IV等
- **协议绑定**: 将密钥绑定到特定上下文
- **安全增强**: HKDF提取阶段增强熵

### Q5: X25519相比P-256的优势？

**A:**
- **实现安全**: 抵抗时序攻击，常量时间实现更简单
- **性能**: 通常比NIST曲线更快
- **设计透明**: Curve25519参数选择有明确理由
- **无专利**: 完全开放
- **标准化**: RFC 7748

### Q6: 量子计算对密钥交换的威胁？如何应对？

**A:**
- **威胁**: Shor算法可破解DH、ECDH、RSA
- **后量子方案**: 
  - **格基**: CRYSTALS-Kyber (NIST标准化)
  - **编码**: Classic McEliece
  - **哈希**: SPHINCS+
- **混合方案**: 当前算法+后量子算法同时使用

### Q7: TLS 1.3相比1.2在密钥交换上的改进？

**A:**
- **握手简化**: 1-RTT完成握手(1.2需要2-RTT)
- **前向安全**: 强制使用临时密钥
- **密钥分离**: 握手密钥和应用密钥分离
- **删除旧算法**: 移除RSA密钥传输、静态DH
- **0-RTT**: 支持会话恢复(牺牲部分前向安全)

### Q8: 密钥交换中的拒绝服务攻击如何防范？

**A:**
- **参数验证**: 验证对端公钥在有效曲线上
- **小额子群攻击**: 验证公钥不在小阶子群中
- **速率限制**: 限制握手请求频率
- **Puzzle**: 要求客户端先计算难题(如Bitcoin)
- **Cookie**: 状态less cookie验证

## 相关概念

### 数据结构
- [树](../computer-science/data-structures/tree.md)
- [图](../computer-science/data-structures/graph.md)

### 算法
- [大数运算](../computer-science/algorithms/number-theory.md)
- [模幂运算](../computer-science/algorithms/modular-exponentiation.md)

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)
- [空间复杂度](../references/space-complexity.md)

### 系统实现
- [网络协议](../computer-science/systems/network-protocols.md)
- [密钥管理](../computer-science/systems/key-management.md)

### 安全领域
- [对称加密](./symmetric-encryption.md)
- [非对称加密](./asymmetric-encryption.md)
- [TLS/SSL协议](../network-security/tls-ssl.md)
- [数字签名](./digital-signatures.md)
- [VPN](../network-security/vpn.md)
