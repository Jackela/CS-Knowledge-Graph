# 网络安全 (Network Security)

## 简介
网络安全是保护计算机网络及其数据免受未授权访问、攻击和破坏的技术与实践，涵盖加密、认证、访问控制等多个层面。

## 核心概念
- **机密性 (Confidentiality)**: 防止未授权的信息泄露
- **完整性 (Integrity)**: 防止数据被篡改
- **可用性 (Availability)**: 确保授权用户能正常访问
- **认证 (Authentication)**: 验证身份真实性
- **授权 (Authorization)**: 确定访问权限

## 实现方式 / 工作原理

### 加密通信流程 (TLS/SSL)

```python
import ssl
import socket

class SecureConnection:
    def __init__(self):
        self.context = ssl.create_default_context()
    
    def tls_handshake(self, client_hello):
        """
        TLS握手过程：
        1. Client Hello - 客户端支持的加密套件
        2. Server Hello - 服务端选择加密套件
        3. Certificate - 服务端发送证书
        4. Key Exchange - 密钥交换 (ECDHE/RSA)
        5. Finished - 双方确认握手完成
        """
        # 协商加密算法
        cipher_suite = self.negotiate_cipher(client_hello)
        
        # 生成会话密钥
        session_key = self.generate_session_key()
        
        # 后续通信使用对称加密
        return self.establish_secure_channel(session_key)
    
    def encrypt_message(self, plaintext, key):
        """AES-GCM加密示例"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext
```

### 防火墙规则配置

```yaml
# iptables/netfilter 规则示例
firewall_rules:
  - chain: INPUT
    action: DROP
    protocol: tcp
    dport: 22
    source: !192.168.1.0/24  # 仅允许内网SSH
  
  - chain: INPUT
    action: ACCEPT
    protocol: tcp
    dport: [80, 443]  # 允许HTTP/HTTPS
    state: NEW,ESTABLISHED
  
  - chain: INPUT
    action: DROP
    protocol: all  # 默认拒绝
```

### 常见攻击与防御

| 攻击类型 | 原理 | 防御措施 |
|----------|------|----------|
| DDoS | 耗尽带宽/资源 | CDN、WAF、流量清洗 |
| SQL注入 | 注入恶意SQL | 参数化查询、WAF |
| XSS | 注入恶意脚本 | CSP、输入过滤、编码 |
| CSRF | 伪造用户请求 | CSRF Token、SameSite Cookie |
| MITM | 中间人拦截 | TLS证书固定、HSTS |

## 应用场景
- **HTTPS网站**: TLS加密保护用户数据传输
- **VPN连接**: 建立安全隧道访问内网资源
- **API安全**: OAuth2/JWT认证授权
- **零信任架构**: 永不信任、始终验证

## 面试要点

1. **Q: 对称加密和非对称加密的区别及应用场景？**  
   A: 对称加密（AES/ChaCha20）速度快但密钥分发困难，适合大数据量加密；非对称加密（RSA/ECDSA）速度慢但无需共享密钥，适合密钥交换和数字签名。实际使用混合加密：非对称加密会话密钥，对称加密数据。

2. **Q: 什么是中间人攻击？如何防御？**  
   A: MITM攻击者截获并可能篡改通信双方的数据。防御措施包括：TLS加密、证书链验证、HSTS强制HTTPS、证书固定（Certificate Pinning）。

3. **Q: HTTPS和HTTP的区别？TLS握手过程？**  
   A: HTTPS在HTTP下层添加TLS/SSL加密。TLS握手：①Client Hello（支持的加密套件）；②Server Hello + Certificate；③密钥交换（生成会话密钥）；④Finished消息验证握手成功。后续使用对称加密通信。

4. **Q: JWT的结构和安全注意事项？**  
   A: JWT由Header.Payload.Signature组成。安全注意：使用强签名算法（RS256/ES256而非HS256）、设置过期时间、敏感信息不要放Payload（仅Base64编码）、使用HTTPS传输。

## 相关概念

### 数据结构
- [哈希表](../data-structures/hash-table.md)
- [树](../data-structures/tree.md)

### 算法
- [加密算法](../algorithms/encryption-algorithms.md)
- [哈希算法](../algorithms/hash-algorithms.md)

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)

### 系统实现
- [拥塞控制](congestion-control.md)
- [网络协议栈](network-protocol-stack.md)
