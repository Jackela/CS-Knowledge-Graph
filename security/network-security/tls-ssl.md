# TLS/SSL协议 (Transport Layer Security)

## 简介

TLS(Transport Layer Security)及其前身SSL(Secure Sockets Layer)是为网络通信提供安全性的加密协议。TLS位于应用层和传输层之间，为HTTP、SMTP、FTP等应用协议提供加密、身份认证和数据完整性保护。

TLS 1.3(2018年发布)是当前最新版本，相比TLS 1.2大幅简化了握手过程，移除了不安全的算法，强制实现前向安全性。现代互联网安全的基础HTTPS就是HTTP over TLS。

## 核心概念

### 1. TLS协议栈

```
┌─────────────────────────────────────┐
│           应用层 (HTTP/FTP/SMTP)      │
├─────────────────────────────────────┤
│           TLS握手协议                │  ← 认证和密钥交换
│           TLS记录协议                │  ← 分段、压缩、加密
│           TLS告警协议                │  ← 错误通知
│           TLS更改密码规格协议         │  ← 切换加密状态
├─────────────────────────────────────┤
│           传输层 (TCP)               │
└─────────────────────────────────────┘
```

### 2. TLS 1.2 握手流程

```
客户端                                                              服务端
   │                                                                    │
   │ ─────────────── ClientHello ─────────────────────────────────────> │
   │  [支持的版本、密码套件、随机数、Session ID、扩展]                      │
   │                                                                    │
   │ <────────────── ServerHello ────────────────────────────────────── │
   │  [选定版本、密码套件、随机数]                                         │
   │ <────────────── Certificate ────────────────────────────────────── │
   │  [服务端证书链]                                                      │
   │ <────────────── ServerKeyExchange ──────────────────────────────── │
   │  [DH/ECDH参数，签名]                                                 │
   │ <────────────── ServerHelloDone ────────────────────────────────── │
   │                                                                    │
   │ ─────────────── ClientKeyExchange ───────────────────────────────> │
   │  [预主密钥，用服务端公钥加密]                                          │
   │ ─────────────── [ChangeCipherSpec] ──────────────────────────────> │
   │ ─────────────── Finished ────────────────────────────────────────> │
   │  [加密握手消息验证]                                                   │
   │                                                                    │
   │ <────────────── [ChangeCipherSpec] ─────────────────────────────── │
   │ <────────────── Finished ───────────────────────────────────────── │
   │                                                                    │
   │ <────────────── 加密应用数据 ─────────────────────────────────────> │
```

### 3. TLS 1.3 握手流程 (1-RTT)

```
客户端                                                              服务端
   │                                                                    │
   │ ─────────────── ClientHello ─────────────────────────────────────> │
   │  [密钥共享、支持的组、签名算法、随机数]                                │
   │  {早期数据}                                                         │
   │                                                                    │
   │ <────────────── ServerHello ────────────────────────────────────── │
   │  [选定参数、密钥共享、随机数] ──────────────┐                        │
   │ <────────────── {EncryptedExtensions} ──────────────────────────── │
   │ <────────────── {CertificateRequest} ───────────────────────────── │
   │ <────────────── {Certificate} ──────────────────────────────────── │
   │ <────────────── {CertificateVerify} ────────────────────────────── │
   │ <────────────── {Finished} ─────────────────────────────────────── │
   │                                            │ 派生密钥               │
   │                                            ▼                       │
   │ ─────────────── {Certificate} ───────────────────────────────────> │
   │ ─────────────── {CertificateVerify} ─────────────────────────────> │
   │ ─────────────── {Finished} ──────────────────────────────────────> │
   │                                                                    │
   │ <────────────── 加密应用数据 ─────────────────────────────────────> │
   │                                                                    │
   {} = 加密消息
```

### 4. 密码套件

TLS 1.3支持的密码套件(简化):

| 套件名称 | 密钥交换 | 认证 | 加密 | 哈希 |
|---------|---------|------|------|------|
| TLS_AES_256_GCM_SHA384 | ECDHE | RSA/ECDSA | AES-256-GCM | SHA384 |
| TLS_AES_128_GCM_SHA256 | ECDHE | RSA/ECDSA | AES-128-GCM | SHA256 |
| TLS_CHACHA20_POLY1305_SHA256 | ECDHE | RSA/ECDSA | ChaCha20-Poly1305 | SHA256 |
| TLS_AES_128_CCM_SHA256 | ECDHE | RSA/ECDSA | AES-128-CCM | SHA256 |

## 实现方式

### Python TLS客户端

```python
import ssl
import socket
import certifi
from urllib.parse import urlparse

class TLSClient:
    """TLS安全客户端实现"""
    
    # TLS 1.3密码套件优先级
    CIPHERS = ':'.join([
        'TLS_AES_256_GCM_SHA384',
        'TLS_CHACHA20_POLY1305_SHA256',
        'TLS_AES_128_GCM_SHA256',
    ])
    
    def __init__(self, verify_mode=ssl.CERT_REQUIRED):
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # 安全配置
        self.context.verify_mode = verify_mode
        self.context.load_verify_locations(certifi.where())
        
        # 强制前向安全
        self.context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        self.context.options |= ssl.OP_NO_COMPRESSION  # 防止CRIME攻击
        
        # 设置密码套件(如果支持)
        if hasattr(ssl, 'SSLContext_set_ciphers'):
            self.context.set_ciphers(self.CIPHERS)
    
    def connect(self, host: str, port: int = 443) -> ssl.SSLSocket:
        """
        建立TLS连接
        
        返回SSLSocket，可像普通socket一样使用
        """
        sock = socket.create_connection((host, port))
        
        # 包装为TLS socket
        tls_sock = self.context.wrap_socket(
            sock,
            server_hostname=host  # SNI扩展
        )
        
        # 验证证书
        self._verify_connection(tls_sock, host)
        
        return tls_sock
    
    def _verify_connection(self, tls_sock: ssl.SSLSocket, expected_host: str):
        """验证TLS连接安全属性"""
        # 获取证书
        cert = tls_sock.getpeercert()
        
        # 检查协议版本
        version = tls_sock.version()
        if version not in ['TLSv1.2', 'TLSv1.3']:
            raise ssl.SSLError(f"不安全的TLS版本: {version}")
        
        # 验证主机名
        ssl.match_hostname(cert, expected_host)
        
        # 检查证书有效期
        import datetime
        not_after = cert.get('notAfter')
        # 解析并验证...
        
        print(f"连接安全: {version}, 密码套件: {tls_sock.cipher()[0]}")
    
    def get_cipher_info(self, tls_sock: ssl.SSLSocket) -> dict:
        """获取连接加密信息"""
        return {
            'version': tls_sock.version(),
            'cipher': tls_sock.cipher(),
            'alpn_protocol': tls_sock.selected_alpn_protocol(),
            'compression': tls_sock.compression(),
            'shared_ciphers': tls_sock.shared_ciphers()[:5] if hasattr(tls_sock, 'shared_ciphers') else None
        }

# 使用示例
def demo_tls_client():
    """TLS客户端示例"""
    client = TLSClient()
    
    try:
        tls_sock = client.connect('www.google.com', 443)
        
        # 发送HTTP请求
        request = b"GET / HTTP/1.1\r\nHost: www.google.com\r\nConnection: close\r\n\r\n"
        tls_sock.sendall(request)
        
        # 接收响应
        response = b''
        while True:
            data = tls_sock.recv(4096)
            if not data:
                break
            response += data
        
        print(f"收到 {len(response)} 字节加密数据")
        print(f"协议: {tls_sock.version()}")
        
        tls_sock.close()
        
    except ssl.SSLError as e:
        print(f"TLS错误: {e}")
```

### TLS服务端实现

```python
import ssl
import socket
from pathlib import Path

class TLSServer:
    """TLS安全服务端实现"""
    
    def __init__(self, cert_path: str, key_path: str):
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # 加载证书和私钥
        self.context.load_cert_chain(cert_path, key_path)
        
        # 安全配置
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2
        self.context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        self.context.options |= ssl.OP_NO_COMPRESSION
        self.context.options |= ssl.OP_SINGLE_ECDH_USE  # 每次握手新密钥
        
        # 设置密码套件优先级
        self.context.set_ciphers(
            'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:!aNULL:!MD5:!DSS'
        )
        
        # 设置曲线偏好
        self.context.set_ecdh_curve('prime256v1')
    
    def start_server(self, host: str = '0.0.0.0', port: int = 8443):
        """启动TLS服务端"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            sock.listen(5)
            
            print(f"TLS服务端监听 {host}:{port}")
            
            while True:
                client_sock, addr = sock.accept()
                print(f"客户端连接: {addr}")
                
                try:
                    # 包装为TLS socket
                    tls_sock = self.context.wrap_socket(
                        client_sock,
                        server_side=True
                    )
                    
                    # 处理连接
                    self._handle_client(tls_sock, addr)
                    
                except ssl.SSLError as e:
                    print(f"TLS握手失败: {e}")
                    client_sock.close()
    
    def _handle_client(self, tls_sock: ssl.SSLSocket, addr):
        """处理客户端请求"""
        try:
            # 获取客户端证书(如果要求)
            client_cert = tls_sock.getpeercert()
            
            print(f"协议: {tls_sock.version()}")
            print(f"密码套件: {tls_sock.cipher()[0]}")
            
            # 简单的HTTP响应
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                "Connection: close\r\n"
                "\r\n"
                "Hello, Secure World!\r\n"
            )
            
            tls_sock.sendall(response.encode())
            
        finally:
            tls_sock.close()
```

### 证书验证与解析

```python
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from datetime import datetime
import requests

class CertificateAnalyzer:
    """TLS证书分析工具"""
    
    def __init__(self):
        self.backend = default_backend()
    
    def fetch_certificate(self, hostname: str, port: int = 443) -> x509.Certificate:
        """获取远程服务器证书"""
        import socket
        import ssl
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
                cert_der = tls_sock.getpeercert(binary_form=True)
                return x509.load_der_x509_certificate(cert_der, self.backend)
    
    def analyze_certificate(self, cert: x509.Certificate) -> dict:
        """分析证书详情"""
        analysis = {
            'subject': self._get_name_dict(cert.subject),
            'issuer': self._get_name_dict(cert.issuer),
            'serial_number': hex(cert.serial_number),
            'not_before': cert.not_valid_before.isoformat(),
            'not_after': cert.not_valid_after.isoformat(),
            'is_expired': cert.not_valid_after < datetime.utcnow(),
            'signature_algorithm': cert.signature_algorithm_oid._name,
            'key_size': cert.public_key().key_size if hasattr(cert.public_key(), 'key_size') else None,
            'subject_alt_names': [],
            'extensions': []
        }
        
        # 提取SAN
        try:
            san_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            analysis['subject_alt_names'] = [
                name.value for name in san_ext.value
            ]
        except x509.ExtensionNotFound:
            pass
        
        # 关键扩展
        critical_exts = [
            x509.oid.ExtensionOID.BASIC_CONSTRAINTS,
            x509.oid.ExtensionOID.KEY_USAGE,
            x509.oid.ExtensionOID.EXTENDED_KEY_USAGE,
        ]
        
        for ext_oid in critical_exts:
            try:
                ext = cert.extensions.get_extension_for_oid(ext_oid)
                analysis['extensions'].append({
                    'name': ext_oid._name,
                    'critical': ext.critical,
                    'value': str(ext.value)
                })
            except x509.ExtensionNotFound:
                pass
        
        return analysis
    
    def verify_certificate_chain(self, cert: x509.Certificate, 
                                  trusted_certs: list) -> bool:
        """验证证书链"""
        # 简化实现，实际应使用完整链验证
        try:
            # 检查自签名
            if cert.issuer == cert.subject:
                return False  # 自签名证书不信任
            
            # 检查有效期
            now = datetime.utcnow()
            if not (cert.not_valid_before <= now <= cert.not_valid_after):
                return False
            
            # 检查密钥用法
            try:
                key_usage = cert.extensions.get_extension_for_oid(
                    x509.oid.ExtensionOID.KEY_USAGE
                )
                if not key_usage.value.digital_signature:
                    return False
            except x509.ExtensionNotFound:
                pass
            
            return True
            
        except Exception as e:
            print(f"验证失败: {e}")
            return False
    
    def _get_name_dict(self, name: x509.Name) -> dict:
        """将Name对象转为字典"""
        return {
            attr.oid._name: attr.value
            for attr in name
        }

# 证书透明度检查
def check_ct_transparency(hostname: str) -> dict:
    """检查证书透明度(CT)"""
    try:
        import subprocess
        
        # 使用openssl检查SCT
        result = subprocess.run(
            ['openssl', 's_client', '-connect', f'{hostname}:443', 
             '-servername', hostname, '-status'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        has_sct = 'SCT' in result.stdout or 'sct' in result.stdout.lower()
        
        return {
            'hostname': hostname,
            'has_sct': has_sct,
            'ct_compliant': has_sct  # 简化判断
        }
        
    except Exception as e:
        return {'error': str(e)}
```

### TLS安全配置扫描

```python
import socket
import ssl

class TLSSecurityScanner:
    """TLS安全配置扫描器"""
    
    WEAK_CIPHERS = [
        'RC4', 'DES', '3DES', 'MD5', 'NULL',
        'EXPORT', 'anon', 'CBC'
    ]
    
    WEAK_PROTOCOLS = [
        ssl.PROTOCOL_SSLv2,
        ssl.PROTOCOL_SSLv3,
        ssl.PROTOCOL_TLSv1,
        ssl.PROTOCOL_TLSv1_1,
    ]
    
    def __init__(self):
        self.results = {}
    
    def scan(self, hostname: str, port: int = 443) -> dict:
        """全面扫描TLS配置"""
        self.results = {
            'hostname': hostname,
            'port': port,
            'protocols': {},
            'ciphers': {},
            'certificate': {},
            'vulnerabilities': []
        }
        
        # 检查协议支持
        self._check_protocols(hostname, port)
        
        # 检查密码套件
        self._check_ciphers(hostname, port)
        
        # 检查证书
        self._check_certificate(hostname, port)
        
        # 检查漏洞
        self._check_vulnerabilities(hostname, port)
        
        return self.results
    
    def _check_protocols(self, hostname: str, port: int):
        """检查支持的TLS版本"""
        protocols = [
            ('SSLv2', ssl.PROTOCOL_SSLv2 if hasattr(ssl, 'PROTOCOL_SSLv2') else None),
            ('SSLv3', ssl.PROTOCOL_SSLv3 if hasattr(ssl, 'PROTOCOL_SSLv3') else None),
            ('TLSv1.0', ssl.PROTOCOL_TLSv1 if hasattr(ssl, 'PROTOCOL_TLSv1') else None),
            ('TLSv1.1', ssl.PROTOCOL_TLSv1_1 if hasattr(ssl, 'PROTOCOL_TLSv1_1') else None),
            ('TLSv1.2', ssl.PROTOCOL_TLSv1_2 if hasattr(ssl, 'PROTOCOL_TLSv1_2') else None),
        ]
        
        for name, proto in protocols:
            if proto is None:
                continue
            
            try:
                context = ssl.SSLContext(proto)
                with socket.create_connection((hostname, port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
                        self.results['protocols'][name] = 'SUPPORTED'
                        if name in ['SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1']:
                            self.results['vulnerabilities'].append(f'支持不安全的协议: {name}')
            except Exception:
                self.results['protocols'][name] = 'NOT_SUPPORTED'
    
    def _check_ciphers(self, hostname: str, port: int):
        """检查支持的密码套件"""
        # 测试常见弱密码
        for cipher in ['RC4-SHA', 'DES-CBC3-SHA', 'NULL-SHA']:
            try:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.set_ciphers(cipher)
                
                with socket.create_connection((hostname, port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
                        self.results['ciphers'][cipher] = 'SUPPORTED'
                        self.results['vulnerabilities'].append(f'支持弱密码: {cipher}')
            except Exception:
                self.results['ciphers'][cipher] = 'NOT_SUPPORTED'
    
    def _check_certificate(self, hostname: str, port: int):
        """检查证书配置"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
                    cert = tls_sock.getpeercert()
                    cipher = tls_sock.cipher()
                    
                    self.results['certificate'] = {
                        'subject': cert.get('subject'),
                        'issuer': cert.get('issuer'),
                        'not_after': cert.get('notAfter'),
                        'cipher': cipher[0],
                        'tls_version': tls_sock.version()
                    }
        except Exception as e:
            self.results['certificate']['error'] = str(e)
    
    def _check_vulnerabilities(self, hostname: str, port: int):
        """检查已知漏洞"""
        # Heartbleed检查简化版
        # POODLE检查
        # etc.
        pass
    
    def generate_report(self) -> str:
        """生成扫描报告"""
        lines = [
            f"TLS安全扫描报告: {self.results['hostname']}",
            "=" * 50,
            "",
            "协议支持:",
        ]
        
        for proto, status in self.results['protocols'].items():
            indicator = "⚠️" if status == 'SUPPORTED' and proto not in ['TLSv1.2', 'TLSv1.3'] else "✓"
            lines.append(f"  {indicator} {proto}: {status}")
        
        lines.extend([
            "",
            "发现的漏洞:",
        ])
        
        if self.results['vulnerabilities']:
            for vuln in self.results['vulnerabilities']:
                lines.append(f"  ⚠️ {vuln}")
        else:
            lines.append("  ✓ 未发现明显漏洞")
        
        return '\n'.join(lines)
```

## 应用场景

### 1. HTTPS客户端库

```python
import urllib.request

class SecureHTTPClient:
    """安全的HTTP客户端"""
    
    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # 证书固定(Certificate Pinning)
        self.pinned_hashes = set()
    
    def add_pin(self, cert_hash: str):
        """添加固定证书哈希"""
        self.pinned_hashes.add(cert_hash)
    
    def request(self, url: str, method: str = 'GET', 
                data: bytes = None, headers: dict = None) -> dict:
        """发送安全HTTP请求"""
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers=headers or {}
        )
        
        # 自定义SSL上下文
        handler = urllib.request.HTTPSHandler(
            context=self.ssl_context
        )
        
        opener = urllib.request.build_opener(handler)
        
        with opener.open(req, timeout=30) as response:
            return {
                'status': response.status,
                'headers': dict(response.headers),
                'data': response.read()
            }
```

### 2. mTLS双向认证

```python
class MTLSClient:
    """双向TLS认证客户端"""
    
    def __init__(self, 
                 ca_cert: str,
                 client_cert: str,
                 client_key: str):
        """
        mTLS配置
        
        Args:
            ca_cert: CA证书路径
            client_cert: 客户端证书路径
            client_key: 客户端私钥路径
        """
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        
        # 加载CA证书(验证服务端)
        self.context.load_verify_locations(ca_cert)
        
        # 加载客户端证书(服务端验证)
        self.context.load_cert_chain(client_cert, client_key)
        
        # 强制双向认证
        self.context.verify_mode = ssl.CERT_REQUIRED
    
    def connect(self, host: str, port: int) -> ssl.SSLSocket:
        """建立mTLS连接"""
        sock = socket.create_connection((host, port))
        tls_sock = self.context.wrap_socket(sock, server_hostname=host)
        
        # 验证对端证书
        peer_cert = tls_sock.getpeercert()
        print(f"服务端证书: {peer_cert.get('subject')}")
        
        return tls_sock
```

### 3. TLS会话恢复

```python
class TLSSessionManager:
    """TLS会话管理(会话恢复)"""
    
    def __init__(self):
        self.sessions = {}  # host -> session_data
    
    def get_session(self, host: str) -> bytes:
        """获取缓存的会话数据"""
        return self.sessions.get(host)
    
    def save_session(self, host: str, session_data: bytes):
        """保存会话数据"""
        self.sessions[host] = session_data
    
    def create_resumption_context(self, host: str) -> ssl.SSLContext:
        """创建支持会话恢复的上下文"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        
        session_data = self.get_session(host)
        if session_data:
            # 设置会话ticket
            context.set_session_ticket_cb(
                self._session_ticket_cb
            )
        
        return context
    
    def _session_ticket_cb(self, sock, session, ticket, ctx):
        """会话ticket回调"""
        if session:
            host = sock.server_hostname
            self.save_session(host, session)
```

## 面试要点

### Q1: TLS 1.3相比1.2的主要改进？

**A:**
- **握手简化**: 1-RTT完成(1.2需要2-RTT)
- **移除旧算法**: 删除RSA密钥传输、CBC模式、SHA-1、MD5
- **前向安全**: 强制使用ECDHE
- **加密扩展**: ServerHello后全部加密
- **0-RTT**: 支持会话恢复(牺牲部分前向安全)

### Q2: 什么是中间人攻击？TLS如何防御？

**A:**
- **攻击**: 攻击者拦截并可能修改通信
- **防御**:
  - **证书验证**: 客户端验证服务端证书链
  - **CA体系**: 信任根CA颁发的证书
  - **证书固定**: 预置证书哈希
  - **HSTS**: 强制HTTPS

### Q3: 前向安全性(Forward Secrecy)如何实现？

**A:**
- **实现**: 使用临时Diffie-Hellman密钥(ECDHE)
- **原理**: 每次会话生成新密钥对，会话密钥不依赖长期私钥
- **优势**: 长期私钥泄露不影响历史会话
- **密码套件**: TLS_ECDHE_* 而非 TLS_RSA_*

### Q4: 证书链验证流程？

**A:**
1. 验证叶证书签名(用中间CA公钥)
2. 验证中间CA证书签名(用根CA公钥)
3. 验证根CA在信任库中
4. 检查每个证书有效期
5. 检查撤销状态(CRL/OCSP)
6. 验证域名匹配(SAN/CN)

### Q5: SNI扩展的作用？

**A:**
- **问题**: 同一IP多证书时，服务端不知道发送哪个证书
- **解决**: ClientHello包含SNI扩展，指明目标域名
- **隐私**: TLS 1.3加密SNI(ESNI/ECH)

### Q6: 如何防范TLS降级攻击？

**A:**
- **版本强制**: 配置最低TLS版本
- **SCSV**: 发送TLS_FALLBACK_SCSV防止强制降级
- **HSTS**: 防止HTTP降级
- **证书透明**: 检测恶意证书

### Q7: 什么是0-RTT？安全风险？

**A:**
- **作用**: 恢复会话时立即发送数据，无需等待握手
- **风险**: 重放攻击
- **缓解**: 0-RTT数据限制为幂等操作
- **前向安全**: 0-RTT密钥不具完全前向安全

### Q8: 证书固定(Certificate Pinning)的优缺点？

**A:**
- **优点**: 即使CA被攻破，攻击者也无法伪造证书
- **缺点**: 
  - 证书轮换困难
  - 证书过期导致应用崩溃
  - 灵活性差
- **现代替代**: CT(证书透明)日志监控

## 相关概念

### 数据结构
- [链表](../computer-science/data-structures/linked-list.md)
- [树](../computer-science/data-structures/tree.md)

### 算法
- [握手协议](../computer-science/algorithms/handshake-protocols.md)
- [状态机](../computer-science/algorithms/state-machines.md)

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)
- [网络延迟](../references/network-latency.md)

### 系统实现
- [网络协议](../computer-science/systems/network-protocols.md)
- [套接字编程](../computer-science/systems/socket-programming.md)

### 安全领域
- [密钥交换](../cryptography/key-exchange.md)
- [数字签名](../cryptography/digital-signatures.md)
- [对称加密](../cryptography/symmetric-encryption.md)
- [证书管理](./certificate-management.md)
- [VPN](./vpn.md)
