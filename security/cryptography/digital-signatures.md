# 数字签名 (Digital Signatures)

## 简介

数字签名是公钥密码学的重要应用，用于验证消息来源的真实性和完整性。它模拟了手写签名的法律效力，但提供了更强的安全保证：不可否认性、身份认证、数据完整性。

数字签名的核心原理是使用**私钥签名**，**公钥验证**。只有私钥持有者能生成有效签名，任何人都可以用公钥验证签名，但无法伪造。

数字签名广泛应用于：软件发布验证、代码签名、文档签署、区块链交易、TLS证书链等场景。

## 核心概念

### 1. 数字签名流程

```
发送方:                            接收方:
┌─────────┐    ┌─────────┐         ┌─────────┐    ┌─────────┐
│ 消息 M  │───>│ 哈希 H  │────────>│ 签名 Σ  │───>│ 发送    │
└─────────┘    └─────────┘         └─────────┘    └─────────┘
     │                                ▲                │
     │         ┌─────────┐            │                │
     └────────>│ 私钥签名 │────────────┘                │
               └─────────┘                             │
                                                       ▼
                                               ┌─────────────┐
                                               │  消息 M     │
                                               │  签名 Σ     │
                                               └─────────────┘
                                                       │
┌─────────┐    ┌─────────┐         ┌─────────┐    ┌─────────┐
│ 验证 OK │<───│ 比较    │<────────│ 哈希 H' │<───│ 哈希 M  │
└─────────┘    └─────────┘         └─────────┘    └─────────┘
     ▲                                ▲
     │         ┌─────────┐            │
     └─────────│ 公钥验证 │<───────────┘
               └─────────┘
```

### 2. 签名算法分类

| 算法类型 | 代表算法 | 密钥长度 | 特点 |
|---------|---------|----------|------|
| RSA | RSA-PSS | 2048-4096位 | 广泛使用，标准化程度高 |
| DSA | DSA | 1024-3072位 | 美国政府标准，已较少使用 |
| ECDSA | secp256k1, P-256 | 256-521位 | 短密钥，高性能，区块链主流 |
| EdDSA | Ed25519, Ed448 | 256-456位 | 确定性签名，抵抗侧信道 |

### 3. 签名方案

**RSA-PSS (Probabilistic Signature Scheme)**:
- 使用随机盐值
- 可证明安全性
- 推荐用于新系统

**ECDSA (Elliptic Curve DSA)**:
- 基于椭圆曲线离散对数
- 比特币、以太坊使用secp256k1
- 签名包含r, s两个值

**EdDSA (Edwards-curve DSA)**:
- 基于Edwards曲线
- 确定性签名(无需随机数)
- 更快的验证速度

### 4. 攻击方式

| 攻击类型 | 目标 | 防御措施 |
|---------|------|---------|
| 密钥恢复 | 从签名推导私钥 | 使用足够长的密钥 |
| 签名伪造 | 无密钥生成有效签名 | 强哈希函数，正确填充 |
| 重放攻击 | 重复使用旧签名 | 时间戳、nonce |
| 盲签名攻击 | 获取对未知消息的签名 | 慎用盲签名 |

## 实现方式

### RSA-PSS 签名

```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import base64
import os

class RSASignature:
    """RSA-PSS 数字签名实现"""
    
    def __init__(self, private_key=None):
        self.private_key = private_key
        self.public_key = private_key.public_key() if private_key else None
        self.backend = default_backend()
    
    @staticmethod
    def generate_key_pair(key_size=2048):
        """生成RSA密钥对"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        return RSASignature(private_key=private_key)
    
    def sign(self, message: bytes, hash_algorithm=hashes.SHA256()) -> bytes:
        """
        RSA-PSS 签名
        
        PSS填充提供可证明安全性
        salt_length=MAX_LENGTH提供最大熵
        """
        if not self.private_key:
            raise ValueError("Private key required for signing")
        
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hash_algorithm),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hash_algorithm
        )
        return signature
    
    def verify(self, message: bytes, signature: bytes, 
               hash_algorithm=hashes.SHA256()) -> bool:
        """
        RSA-PSS 签名验证
        
        使用try/except捕获InvalidSignature异常
        避免信息泄露
        """
        if not self.public_key:
            raise ValueError("Public key required for verification")
        
        try:
            self.public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hash_algorithm),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hash_algorithm
            )
            return True
        except InvalidSignature:
            return False
    
    def export_keys(self, private_password: bytes = None) -> tuple:
        """导出密钥对"""
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=(
                serialization.BestAvailableEncryption(private_password)
                if private_password else serialization.NoEncryption()
            )
        )
        
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @classmethod
    def load_from_pem(cls, private_pem: bytes = None, 
                      public_pem: bytes = None,
                      private_password: bytes = None):
        """从PEM加载密钥"""
        private_key = None
        if private_pem:
            private_key = serialization.load_pem_private_key(
                private_pem, password=private_password, backend=default_backend()
            )
        
        public_key = None
        if public_pem:
            public_key = serialization.load_pem_public_key(
                public_pem, backend=default_backend()
            )
        
        instance = cls.__new__(cls)
        instance.private_key = private_key
        instance.public_key = public_key or (private_key.public_key() if private_key else None)
        instance.backend = default_backend()
        return instance
```

### ECDSA 签名

```python
from cryptography.hazmat.primitives.asymmetric import ec

class ECDSASignature:
    """ECDSA 数字签名实现"""
    
    CURVES = {
        'secp256r1': ec.SECP256R1(),  # NIST P-256, 最常用
        'secp384r1': ec.SECP384R1(),  # NIST P-384
        'secp521r1': ec.SECP521R1(),  # NIST P-521
        'secp256k1': ec.SECP256K1(),  # 比特币/以太坊
    }
    
    def __init__(self, private_key=None, curve_name='secp256r1'):
        self.private_key = private_key
        self.public_key = private_key.public_key() if private_key else None
        self.curve = self.CURVES.get(curve_name, ec.SECP256R1())
        self.backend = default_backend()
    
    @staticmethod
    def generate_key_pair(curve_name='secp256r1'):
        """生成ECDSA密钥对"""
        instance = ECDSASignature(curve_name=curve_name)
        instance.private_key = ec.generate_private_key(
            instance.curve,
            default_backend()
        )
        instance.public_key = instance.private_key.public_key()
        return instance
    
    def sign(self, message: bytes, hash_algorithm=hashes.SHA256()) -> bytes:
        """
        ECDSA 签名
        
        签名值为DER编码的(r, s)对
        """
        if not self.private_key:
            raise ValueError("Private key required")
        
        signature = self.private_key.sign(
            message,
            ec.ECDSA(hash_algorithm)
        )
        return signature
    
    def verify(self, message: bytes, signature: bytes,
               hash_algorithm=hashes.SHA256()) -> bool:
        """ECDSA 签名验证"""
        if not self.public_key:
            raise ValueError("Public key required")
        
        try:
            self.public_key.verify(
                signature,
                message,
                ec.ECDSA(hash_algorithm)
            )
            return True
        except InvalidSignature:
            return False
    
    def sign_deterministic(self, message: bytes, 
                          hash_algorithm=hashes.SHA256()) -> bytes:
        """
        确定性ECDSA签名 (RFC 6979)
        
        使用HMAC-SHA2生成k值，而非随机数
        防止因弱随机数导致的私钥泄露
        """
        import hmac
        import hashlib
        
        # 获取私钥数值
        private_value = self.private_key.private_numbers().private_value
        curve_order = self.private_key.curve.key_size
        
        # 消息哈希
        hash_func = hashlib.sha256 if hash_algorithm == hashes.SHA256() else hashlib.sha384
        h1 = hash_func(message).digest()
        
        # RFC 6979 确定性k生成
        V = b'\x01' * 32
        K = b'\x00' * 32
        
        # 这里简化实现，实际应使用库实现
        # cryptography库暂不支持确定性ECDSA
        return self.sign(message, hash_algorithm)
```

### Ed25519 签名

```python
class Ed25519Signature:
    """
    Ed25519 数字签名
    
    特点:
    - 确定性签名(无随机数问题)
    - 快速验证
    - 短签名(64字节)
    - 短密钥(32字节私钥，32字节公钥)
    - 抵抗侧信道攻击
    """
    
    def __init__(self, private_key=None):
        self.private_key = private_key
        self.public_key = private_key.public_key() if private_key else None
    
    @staticmethod
    def generate_key_pair():
        """生成Ed25519密钥对"""
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        
        instance = Ed25519Signature()
        instance.private_key = Ed25519PrivateKey.generate()
        instance.public_key = instance.private_key.public_key()
        return instance
    
    def sign(self, message: bytes) -> bytes:
        """Ed25519 签名"""
        if not self.private_key:
            raise ValueError("Private key required")
        
        return self.private_key.sign(message)
    
    def verify(self, message: bytes, signature: bytes) -> bool:
        """Ed25519 签名验证"""
        if not self.public_key:
            raise ValueError("Public key required")
        
        try:
            self.public_key.verify(signature, message)
            return True
        except InvalidSignature:
            return False
```

### 带时间戳的签名

```python
import time
import json

class TimestampedSignature:
    """带时间戳和防重放的数字签名"""
    
    def __init__(self, signer, tolerance_seconds: int = 300):
        self.signer = signer
        self.tolerance = tolerance_seconds
        self.used_nonces = set()  # 防重放
    
    def sign(self, message: bytes, include_nonce: bool = True) -> dict:
        """
        创建带时间戳的签名
        
        结构: { payload: {...}, signature: "..." }
        """
        payload = {
            'message': base64.b64encode(message).decode(),
            'timestamp': int(time.time()),
            'algorithm': self._get_algorithm()
        }
        
        if include_nonce:
            payload['nonce'] = base64.b64encode(os.urandom(16)).decode()
        
        # 签名payload的规范化JSON
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        signature = self.signer.sign(payload_json.encode())
        
        return {
            'payload': payload,
            'signature': base64.b64encode(signature).decode()
        }
    
    def verify(self, signed_message: dict) -> bool:
        """
        验证带时间戳的签名
        
        检查:
        1. 时间戳有效性
        2. nonce未被使用
        3. 签名有效性
        """
        payload = signed_message['payload']
        signature = base64.b64decode(signed_message['signature'])
        
        # 检查时间戳
        current_time = int(time.time())
        message_time = payload['timestamp']
        if abs(current_time - message_time) > self.tolerance:
            return False
        
        # 检查nonce防重放
        if 'nonce' in payload:
            nonce = payload['nonce']
            if nonce in self.used_nonces:
                return False
            self.used_nonces.add(nonce)
        
        # 验证签名
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return self.signer.verify(payload_json.encode(), signature)
    
    def _get_algorithm(self) -> str:
        """获取算法名称"""
        key_type = type(self.signer).__name__
        return key_type.replace('Signature', '').lower()
```

### 多重签名

```python
from typing import List

class MultiSignature:
    """
    M-of-N 多重签名
    
    需要M个签名者中的至少N个签名才有效
    用于: 多签钱包、共识机制、阈值签名
    """
    
    def __init__(self, threshold: int, public_keys: List):
        """
        Args:
            threshold: 需要的签名数量(M)
            public_keys: 公钥列表(N个)
        """
        if threshold > len(public_keys):
            raise ValueError("Threshold cannot exceed number of public keys")
        
        self.threshold = threshold
        self.public_keys = public_keys
    
    def verify_multi_sig(self, message: bytes, signatures: List[bytes],
                        signers: List[int]) -> bool:
        """
        验证多重签名
        
        Args:
            message: 原始消息
            signatures: 签名列表
            signers: 签名者索引列表
        
        Returns:
            bool: 是否满足阈值要求且所有签名有效
        """
        if len(signatures) < self.threshold:
            return False
        
        if len(signatures) != len(signers):
            return False
        
        # 验证每个签名
        valid_count = 0
        used_signers = set()
        
        for sig, signer_idx in zip(signatures, signers):
            # 防止同一签名者被重复使用
            if signer_idx in used_signers:
                continue
            used_signers.add(signer_idx)
            
            # 获取对应公钥
            if signer_idx >= len(self.public_keys):
                continue
            
            public_key = self.public_keys[signer_idx]
            
            # 创建临时验证器
            if isinstance(public_key, rsa.RSAPublicKey):
                verifier = RSASignature(public_key=public_key)
            elif isinstance(public_key, ec.EllipticCurvePublicKey):
                verifier = ECDSASignature(public_key=public_key)
            else:
                continue
            
            if verifier.verify(message, sig):
                valid_count += 1
        
        return valid_count >= self.threshold
```

## 应用场景

### 1. 软件代码签名

```python
import zipfile
from pathlib import Path

class CodeSigner:
    """软件代码签名工具"""
    
    def __init__(self, signer):
        self.signer = signer
    
    def sign_release(self, release_dir: str, output_path: str) -> dict:
        """
        签名软件发布包
        
        类似: Authenticode, GPG签名
        """
        release_path = Path(release_dir)
        manifest = {}
        
        # 收集所有文件哈希
        for file_path in release_path.rglob('*'):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(release_path))
                file_hash = self._hash_file(file_path)
                manifest[relative_path] = file_hash
        
        # 创建签名清单
        manifest_json = json.dumps(manifest, sort_keys=True, indent=2)
        manifest_bytes = manifest_json.encode('utf-8')
        
        # 签名清单
        signature = self.signer.sign(manifest_bytes)
        
        # 打包
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 添加原始文件
            for file_path in release_path.rglob('*'):
                if file_path.is_file():
                    zf.write(file_path, file_path.relative_to(release_path))
            
            # 添加清单和签名
            zf.writestr('.manifest.json', manifest_bytes)
            zf.writestr('.signature', base64.b64encode(signature))
        
        return {
            'release_path': output_path,
            'manifest_hash': hashlib.sha256(manifest_bytes).hexdigest()[:16],
            'file_count': len(manifest)
        }
    
    def verify_release(self, release_path: str, public_key) -> dict:
        """验证签名发布包"""
        results = {'valid': False, 'files_ok': 0, 'files_modified': []}
        
        with zipfile.ZipFile(release_path, 'r') as zf:
            # 读取清单和签名
            manifest_bytes = zf.read('.manifest.json')
            signature = base64.b64decode(zf.read('.signature'))
            
            # 验证签名
            if isinstance(public_key, rsa.RSAPublicKey):
                verifier = RSASignature(public_key=public_key)
            else:
                verifier = ECDSASignature(public_key=public_key)
            
            if not verifier.verify(manifest_bytes, signature):
                return results
            
            # 验证文件完整性
            manifest = json.loads(manifest_bytes)
            for file_name, expected_hash in manifest.items():
                try:
                    file_content = zf.read(file_name)
                    actual_hash = hashlib.sha256(file_content).hexdigest()
                    
                    if actual_hash == expected_hash:
                        results['files_ok'] += 1
                    else:
                        results['files_modified'].append(file_name)
                except KeyError:
                    results['files_modified'].append(file_name)
            
            results['valid'] = len(results['files_modified']) == 0
        
        return results
    
    def _hash_file(self, file_path: Path) -> str:
        """计算文件SHA256哈希"""
        h = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
```

### 2. 区块链交易签名

```python
class BlockchainTransaction:
    """区块链交易签名"""
    
    def __init__(self, signer: ECDSASignature):
        self.signer = signer
    
    def create_transaction(self, from_addr: str, to_addr: str, 
                          amount: float, nonce: int) -> dict:
        """
        创建签名交易
        
        类似以太坊交易结构
        """
        tx = {
            'from': from_addr,
            'to': to_addr,
            'amount': amount,
            'nonce': nonce,  # 防重放
            'timestamp': int(time.time()),
            'chain_id': 1
        }
        
        # 序列化交易
        tx_bytes = self._serialize_tx(tx)
        
        # 双重哈希 (类似比特币)
        tx_hash = hashlib.sha256(hashlib.sha256(tx_bytes).digest()).digest()
        
        # 签名
        signature = self.signer.sign(tx_hash)
        
        # 解码r, s值
        r, s = self._decode_signature(signature)
        
        tx['hash'] = tx_hash.hex()
        tx['signature'] = {
            'r': hex(r),
            's': hex(s),
            'v': 27  # 恢复标识
        }
        
        return tx
    
    def verify_transaction(self, tx: dict) -> bool:
        """验证交易签名"""
        # 提取签名
        sig_data = tx.pop('signature')
        tx_hash = bytes.fromhex(tx.pop('hash'))
        
        # 重新序列化
        tx_bytes = self._serialize_tx(tx)
        computed_hash = hashlib.sha256(hashlib.sha256(tx_bytes).digest()).digest()
        
        if computed_hash != tx_hash:
            return False
        
        # 验证签名
        # 这里简化处理，实际需要重构DER签名
        return True
    
    def _serialize_tx(self, tx: dict) -> bytes:
        """RLP-like序列化"""
        items = [
            tx['from'].encode(),
            tx['to'].encode(),
            str(tx['amount']).encode(),
            str(tx['nonce']).encode(),
            str(tx['timestamp']).encode(),
            str(tx['chain_id']).encode()
        ]
        return b'|'.join(items)
    
    def _decode_signature(self, signature: bytes) -> tuple:
        """从DER解码r, s"""
        # 简化实现
        mid = len(signature) // 2
        r = int.from_bytes(signature[:mid], 'big')
        s = int.from_bytes(signature[mid:], 'big')
        return r, s
```

### 3. 文档数字签名

```python
from datetime import datetime

class DocumentSignature:
    """文档数字签名系统"""
    
    def __init__(self, signer, timestamp_authority_url: str = None):
        self.signer = signer
        self.tsa_url = timestamp_authority_url
    
    def sign_document(self, document_path: str, 
                     reason: str = None,
                     location: str = None) -> dict:
        """
        签名文档
        
        类似PDF数字签名
        """
        from pathlib import Path
        
        doc_path = Path(document_path)
        document_hash = self._hash_document(document_path)
        
        signature_data = {
            'document': {
                'name': doc_path.name,
                'hash': document_hash,
                'size': doc_path.stat().st_size
            },
            'signer': {
                'algorithm': type(self.signer).__name__,
                'public_key_fingerprint': self._get_key_fingerprint()
            },
            'metadata': {
                'signed_at': datetime.utcnow().isoformat(),
                'reason': reason,
                'location': location
            }
        }
        
        # 添加时间戳
        if self.tsa_url:
            signature_data['timestamp'] = self._get_timestamp(document_hash)
        
        # 签名数据
        data_to_sign = json.dumps(signature_data, sort_keys=True).encode()
        signature = self.signer.sign(data_to_sign)
        
        # 保存签名文件
        sig_path = doc_path.with_suffix(doc_path.suffix + '.sig')
        signed_doc = {
            'signature_data': signature_data,
            'signature': base64.b64encode(signature).decode()
        }
        
        with open(sig_path, 'w') as f:
            json.dump(signed_doc, f, indent=2)
        
        return {
            'document_path': str(doc_path),
            'signature_path': str(sig_path),
            'hash': document_hash[:16]
        }
    
    def verify_document(self, document_path: str, 
                       signature_path: str = None) -> dict:
        """验证文档签名"""
        from pathlib import Path
        
        doc_path = Path(document_path)
        if signature_path is None:
            sig_path = doc_path.with_suffix(doc_path.suffix + '.sig')
        else:
            sig_path = Path(signature_path)
        
        # 读取签名
        with open(sig_path, 'r') as f:
            signed_doc = json.load(f)
        
        signature_data = signed_doc['signature_data']
        signature = base64.b64decode(signed_doc['signature'])
        
        # 验证文档哈希
        current_hash = self._hash_document(document_path)
        if current_hash != signature_data['document']['hash']:
            return {'valid': False, 'reason': 'Document modified'}
        
        # 验证签名
        data_to_verify = json.dumps(signature_data, sort_keys=True).encode()
        if not self.signer.verify(data_to_verify, signature):
            return {'valid': False, 'reason': 'Invalid signature'}
        
        return {
            'valid': True,
            'signed_at': signature_data['metadata']['signed_at'],
            'signer_fingerprint': signature_data['signer']['public_key_fingerprint']
        }
    
    def _hash_document(self, path: str) -> str:
        """计算文档哈希"""
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    
    def _get_key_fingerprint(self) -> str:
        """获取公钥指纹"""
        public_key_bytes = self.signer.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return hashlib.sha256(public_key_bytes).hexdigest()[:16]
    
    def _get_timestamp(self, data_hash: str) -> dict:
        """从TSA获取RFC 3161时间戳"""
        # 简化实现
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'tsa': self.tsa_url,
            'hash': data_hash[:16]
        }
```

## 面试要点

### Q1: RSA-PSS和RSA-PKCS#1 v1.5签名的区别？

**A:**
- **PSS**: 概率签名方案，引入随机盐值，提供可证明安全性，推荐用于新系统
- **PKCS#1 v1.5**: 确定性签名，存在实现漏洞(Bleichenbacher攻击)，但广泛兼容
- **选择**: 新项目用PSS，旧系统兼容用v1.5

### Q2: ECDSA签名为什么需要随机数k？重用k有什么风险？

**A:**
- **签名公式**: r = kG, s = k⁻¹(H(m) + dr)
- **风险**: 如果两个签名使用相同的k，可通过方程组解出私钥d
- **Sony PS3事件**: 因固件重用k，私钥被破解
- **解决方案**: RFC 6979确定性签名，或用Ed25519

### Q3: Ed25519相比ECDSA的优势？

**A:**
- **确定性**: 不需要随机数，避免随机数失败风险
- **性能**: 验证速度比ECDSA快约2倍
- **安全**: 抵抗侧信道攻击，实现更简单
- **紧凑**: 64字节签名，32字节公钥

### Q4: 如何验证证书链？

**A:**
- **链结构**: 叶证书 → 中间CA → 根CA
- **验证步骤**:
  1. 验证每个证书的签名(用上一级公钥)
  2. 检查有效期
  3. 验证证书用途(Key Usage)
  4. 检查吊销状态(CRL/OCSP)
  5. 验证域名匹配
  6. 锚定到受信任根证书

### Q5: 什么是盲签名(Blind Signature)？应用场景？

**A:**
- **原理**: 签名者对盲化后的消息签名，无法知道实际内容
- **应用**: 电子现金(Chaumian e-cash)、匿名投票
- **风险**: 可能签署恶意内容，需配合协议限制

### Q6: 如何防止签名重放攻击？

**A:**
- **时间戳**: 包含签名时间，验证时检查时效性
- **Nonce**: 一次性随机数，服务端记录已用nonce
- **序列号**: 递增序列号，拒绝乱序或重复
- **挑战-响应**: 服务端先发送挑战值，客户端签名包含挑战

### Q7: 阈值签名(Threshold Signature)的优势？

**A:**
- **分布式信任**: 私钥分片，无需完整私钥即可签名
- **容错**: t-of-n中，少于t个分片无法签名，最多容忍n-t个分片丢失
- **效率**: 产生单一签名，验证与普通签名一样快
- **应用**: 多签钱包、分布式CA、共识协议

### Q8: 数字签名和MAC的区别？

**A:**
| 特性 | 数字签名 | MAC |
|------|---------|-----|
| 密钥 | 非对称(公私钥对) | 对称(共享密钥) |
| 不可否认 | 是 | 否 |
| 计算成本 | 高 | 低 |
| 密钥分发 | 公钥可公开 | 需要安全通道 |
| 用途 | 外部通信、法律证据 | 内部系统、性能敏感 |

## 相关概念

### 数据结构
- [链表](../computer-science/data-structures/linked-list.md)
- [树](../computer-science/data-structures/tree.md)

### 算法
- [大数运算](../computer-science/algorithms/number-theory.md)
- [字符串匹配](../computer-science/algorithms/string-matching.md)

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)
- [空间复杂度](../references/space-complexity.md)

### 系统实现
- [证书管理](../computer-science/systems/certificate-management.md)
- [密钥管理](../computer-science/systems/key-management.md)

### 安全领域
- [非对称加密](./asymmetric-encryption.md)
- [哈希函数](./hash-functions.md)
- [密钥交换](./key-exchange.md)
- [TLS/SSL协议](../network-security/tls-ssl.md)
- [公钥基础设施(PKI)](../network-security/pki.md)
