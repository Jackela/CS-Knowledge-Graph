# HTTPS与TLS (HTTP Secure / Transport Layer Security)

## 简介

**HTTPS（HTTP Secure）**是HTTP协议的安全版本，通过**TLS（Transport Layer Security）**或其前身**SSL（Secure Sockets Layer）**提供加密通信。

```
HTTP vs HTTPS:

HTTP: 明文传输，端口80
HTTPS: 加密传输，端口443

┌─────────┐         ┌─────────┐
│  客户端  │←───────→│  服务器  │
│         │  TLS    │         │
│ HTTP数据 │←─加密──→│ HTTP数据 │
└─────────┘         └─────────┘
```

## TLS握手过程

### TLS 1.2 握手

```
客户端                              服务器
   │                                  │
   │──── ClientHello ───────────────→│
   │  支持的TLS版本、密码套件、随机数    │
   │                                  │
   │←─── ServerHello ────────────────│
   │  选择的TLS版本、密码套件、随机数    │
   │  服务器证书                      │
   │  [ServerKeyExchange]            │
   │  [CertificateRequest]           │
   │  ServerHelloDone                │
   │                                  │
   │──── ClientKeyExchange ─────────→│
   │  预主密钥（用服务器公钥加密）       │
   │  [Certificate]                  │
   │  [CertificateVerify]            │
   │  ChangeCipherSpec               │
   │  Finished (加密)                │
   │                                  │
   │←─── ChangeCipherSpec ───────────│
   │  Finished (加密)                │
   │                                  │
   │◄── 加密通信开始 ────────────────►│
```

### TLS 1.3 改进

```
TLS 1.3 握手（简化）:

客户端                              服务器
   │                                  │
   │──── ClientHello ───────────────→│
   │  密钥共享、支持的算法             │
   │                                  │
   │←─── ServerHello ────────────────│
   │  选择的算法、密钥共享             │
   │  {EncryptedExtensions}          │
   │  {Certificate}                  │
   │  {CertificateVerify}            │
   │  {Finished}                     │
   │                                  │
   │──── {Finished} ────────────────→│
   │                                  │
   │◄── 加密通信开始 ────────────────►│

{} 表示加密的消息
TLS 1.3: 1-RTT（单次往返），可选0-RTT
```

## 密码套件

```
TLS密码套件格式:
TLS_密钥交换算法_身份验证算法_WITH_对称加密算法_消息认证算法

示例: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384

- ECDHE: 临时椭圆曲线Diffie-Hellman密钥交换
- RSA: 证书身份验证
- AES_256_GCM: 256位AES Galois/Counter模式加密
- SHA384: 384位SHA哈希

完美前向保密（PFS）: ECDHE/DHE确保即使私钥泄露，历史会话不泄露
```

## 证书与PKI

### X.509证书结构

```
证书内容:
- 版本号
- 序列号
- 签名算法
- 颁发者
- 有效期
- 主题（域名/组织）
- 公钥
- 扩展（SAN、密钥用途等）
- 颁发者签名
```

### 证书链验证

```
根CA证书
    ↓ 签名
中间CA证书
    ↓ 签名
服务器证书（叶子）

验证:
1. 检查证书有效期
2. 验证签名链
3. 检查证书吊销（CRL/OCSP）
4. 域名匹配
```

## TLS 1.3 新特性

1. **更快的握手**: 1-RTT，可选0-RTT
2. **更强的安全性**: 废弃不安全算法（MD5、SHA-1、RSA密钥交换等）
3. **加密更多数据**: 除ClientHello外全部加密
4. **前向保密**: 强制使用ECDHE/DHE

## 常见攻击与防护

| 攻击 | 描述 | 防护 |
|------|------|------|
| 降级攻击 | 强制使用旧版本TLS | TLS 1.3废弃旧版本 |
| BEAST | CBC模式漏洞 | 使用TLS 1.2+ |
| POODLE | SSL 3.0漏洞 | 禁用SSL 3.0 |
| Heartbleed | OpenSSL缓冲区溢出 | 更新OpenSSL |
| CRIME | 压缩侧信道 | 禁用TLS压缩 |

## 面试要点

### Q1: HTTPS为什么安全？

1. **加密**：防止窃听
2. **完整性**：防止篡改（MAC验证）
3. **身份验证**：证书验证服务器身份

### Q2: 证书颁发流程

```
1. 申请者生成公钥对
2. 向CA提交CSR（证书签名请求）
3. CA验证身份
4. CA用私钥签名证书
5. 申请者安装证书
```

### Q3: 自签名证书 vs CA证书

| 特性 | 自签名 | CA签名 |
|------|--------|--------|
| 成本 | 免费 | 收费/免费 |
| 信任 | 需手动添加 | 系统自动信任 |
| 适用 | 内部测试 | 生产环境 |
| 安全性 | 同等 | 同等 |

## 相关概念

### 安全与密码学
- [密码学基础](../../security/cryptography-basics.md) - 加密算法与TLS的数学基础

### 网络协议
- [HTTP协议](./http.md) - TLS保护的传输协议


## 参考资料

1. 《计算机网络：自顶向下方法》第8章 - 网络安全
2. TLS 1.3 RFC 8446
3. Transport Layer Security - Wikipedia
