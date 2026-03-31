# 身份认证 (Authentication)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**身份认证 (Authentication)** 是验证用户或实体身份的过程，确保系统知道"你是谁"。身份认证是信息安全的第一道防线，是访问控制的基础。

```
┌─────────────────────────────────────────────────────────────┐
│                   身份认证三要素                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│   │ 所知 (Something │ 所有 (Something │ 所是 (Something │
│   │  you know)      │  you have)      │  you are)       │
│   └──────────┘  └──────────┘  └──────────┘                 │
│                                                             │
│   • 密码            • 手机              • 指纹              │
│   • PIN码           • 安全密钥          • 面部识别          │
│   • 密保问题        • 智能卡            • 虹膜识别          │
│   • 口令            • 令牌              • 声纹              │
│                                                             │
│   单因素认证：使用1种                                         │
│   双因素认证 (2FA)：使用2种不同因素                            │
│   多因素认证 (MFA)：使用2种以上不同因素                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 密码认证

### 密码存储

```
密码安全存储原则：

❌ 绝不明文存储
❌ 绝不简单哈希（MD5/SHA1可被彩虹表攻击）

✅ 正确做法：加盐哈希

存储格式：salt + hash(password + salt)

推荐算法：
- bcrypt：自适应成本因子，内置盐
- scrypt：内存困难型，抗硬件攻击
- Argon2：密码哈希竞赛 winner
- PBKDF2：NIST推荐

Python示例（bcrypt）：
import bcrypt

# 注册时生成哈希
password = b"super secret password"
salt = bcrypt.gensalt(rounds=12)  # 成本因子12
hashed = bcrypt.hashpw(password, salt)
# 存储 hashed

# 登录时验证
if bcrypt.checkpw(password, stored_hash):
    print("密码正确")
```

### 密码策略

```
强密码要求：
- 最小长度：12位以上
- 字符种类：大小写、数字、特殊字符
- 不常见：不在常见密码列表中
- 不个人信息：不包含用户名、生日等
- 定期更换：90-180天（有争议）

密码管理器推荐：
- 为用户生成随机强密码
- 唯一密码：每个服务不同密码
- 主密码保护密码库

常见密码攻击：
- 暴力破解：尝试所有组合
- 字典攻击：使用常见密码列表
- 彩虹表：预计算的哈希表
- 凭证填充：使用泄露的密码组合
```

## 会话管理

### Session与Cookie

```
基于Session的认证：

1. 用户登录验证
2. 服务器创建Session，生成Session ID
3. Session ID通过Cookie发送给客户端
4. 后续请求携带Cookie
5. 服务器根据Session ID查找Session

Session存储方式：
- 内存：速度快，但无法分布式
- 数据库：持久化，可共享
- Redis：高性能，支持过期

安全考虑：
- HttpOnly Cookie：防止XSS窃取
- Secure标志：仅HTTPS传输
- SameSite：防止CSRF
- 过期时间：平衡安全与便利
```

### Token认证

```
JWT (JSON Web Token)：

结构：header.payload.signature

Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload（声明）：
{
  "sub": "user123",      // 主题
  "iat": 1516239022,     // 签发时间
  "exp": 1516242622,     // 过期时间
  "role": "admin"        // 自定义
}

Signature:
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret
)

优点：
- 无状态，可扩展
- 跨服务共享
- 包含用户信息，减少查询

缺点：
- 无法提前撤销（除非使用黑名单）
- Payload大小限制
- 需要处理续期
```

```python
import jwt
from datetime import datetime, timedelta

# 生成JWT
def generate_token(user_id, secret_key):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

# 验证JWT
def verify_token(token, secret_key):
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # 过期
    except jwt.InvalidTokenError:
        return None  # 无效
```

## 双因素认证 (2FA)

### TOTP (基于时间的一次性密码)

```
TOTP算法：

1. 服务器生成随机密钥（Base32编码）
2. 用户将密钥输入认证器应用（如Google Authenticator）
3. 认证器计算：
   TOTP = Truncate(HMAC-SHA1(Key, Time/30))
   
4. 每30秒生成新的6位数字

Python实现：
import pyotp
import time

# 生成密钥
secret = pyotp.random_base32()

# 创建TOTP对象
totp = pyotp.TOTP(secret)

# 生成当前验证码
code = totp.now()

# 验证
is_valid = totp.verify(code)

# 生成二维码URL（供手机扫描）
provisioning_uri = totp.provisioning_uri(
    name="user@example.com",
    issuer_name="MyApp"
)
```

### 其他2FA方法

```
短信验证码：
- 优点：普及度高
- 缺点：SIM卡交换攻击、拦截
- 建议：作为备选，而非主要方式

邮件验证码：
- 类似短信，延迟更高
- 邮箱本身需要强保护

硬件安全密钥：
- YubiKey, Google Titan
- 基于FIDO2/WebAuthn
- 防钓鱼攻击
- 最高安全性

推送通知：
- 手机应用确认登录
- 需要解锁手机确认
- 用户体验好
```

## 生物识别认证

### 生物识别技术对比

| 技术 | 准确性 | 便利性 | 安全性 | 成本 |
|------|--------|--------|--------|------|
| 指纹 | 高 | 高 | 中 | 低 |
| 面部 | 中 | 高 | 中 | 低 |
| 虹膜 | 极高 | 中 | 高 | 高 |
| 声纹 | 中 | 高 | 低 | 低 |
| 步态 | 中 | 极高 | 低 | 中 |
| 静脉 | 高 | 中 | 高 | 中 |

### 生物识别安全考虑

```
生物识别特性：
- 唯一性：每个人都不同
- 持久性：相对稳定
- 可采集性：容易测量
- 不可撤销性：⚠️ 一旦泄露无法更换

安全建议：
1. 生物特征数据本地存储，不传输
2. 使用模板而非原始图像
3. 生物识别 + 其他因素（多因素）
4. 活体检测防止欺骗
5. 提供备用认证方式

隐私考虑：
- 生物数据属于敏感个人信息
- 遵守GDPR等隐私法规
- 明确告知收集目的
```

## 单点登录 (SSO)

### OAuth 2.0

```
OAuth 2.0授权流程：

用户 ──────▶ 客户端应用 ──────▶ 授权服务器
  │                              │
  │ 1. 请求授权                  │
  │◀─────────────────────────────│
  │                              │
  │ 2. 用户授权                  │
  │─────────────────────────────▶│
  │                              │
  │ 3. 返回授权码                │
  │◀─────────────────────────────│
  │                              │
  │ 4. 用授权码换取令牌          │
  │─────────────────────────────▶│
  │                              │
  │ 5. 返回访问令牌              │
  │◀─────────────────────────────│
  │                              │
  │ 6. 用令牌访问资源            │
  │─────────────────────────────▶ 资源服务器

授权模式：
- 授权码模式（最安全，推荐）
- 隐式授权（已不推荐使用）
- 密码凭证
- 客户端凭证
```

### OpenID Connect

```
OpenID Connect (OIDC)：
基于OAuth 2.0的身份层

相比OAuth的区别：
- OAuth：授权（你能做什么）
- OIDC：认证（你是谁）

ID Token：
JWT格式的用户身份信息

包含：
- iss：签发者
- sub：用户唯一标识
- aud：受众
- exp：过期时间
- name, email, picture等

流程：
与OAuth相同，但scope包含openid
```

## 常见攻击与防御

### 认证相关攻击

```
暴力破解：
- 攻击：尝试大量密码组合
- 防御：速率限制、CAPTCHA、账户锁定

凭证填充：
- 攻击：使用泄露的密码组合
- 防御：密码黑名单、2FA、异常登录检测

会话劫持：
- 攻击：窃取Session ID或Token
- 防御：HttpOnly、Secure、短过期时间、IP绑定

中间人攻击：
- 攻击：拦截通信获取凭证
- 防御：HTTPS、证书固定

钓鱼攻击：
- 攻击：伪造登录页面
- 防御：用户教育、硬件密钥、异常检测
```

## 最佳实践

```
认证系统设计清单：

□ 密码要求
  □ 最小长度12位
  □ 复杂度要求
  □ 常见密码黑名单
  □ 使用bcrypt/Argon2存储

□ 会话管理
  □ 随机Session ID
  □ 合理过期时间
  □ HttpOnly + Secure Cookie
  □ 登录后重新生成ID

□ 多因素认证
  □ 支持TOTP
  □ 支持硬件密钥
  □ 提供备用恢复码

□ 安全监控
  □ 登录日志
  □ 异常检测
  □ 失败尝试限制

□ 用户体验
  □ 记住我选项
  □ 密码重置流程
  □ 设备管理
```

## 面试要点

### 常见问题

**Q1: 为什么密码不能用MD5存储？**
> MD5计算速度快，容易被暴力破解和彩虹表攻击。应使用专门设计的密码哈希算法如bcrypt、Argon2，它们有成本因子可以调节计算难度，且内置盐值。

**Q2: JWT和Session的区别？**> Session是服务器端存储状态，通过Cookie传递Session ID；JWT是客户端存储状态，自包含用户信息。Session可撤销，JWT无法提前失效（除非黑名单）。JWT适合分布式微服务，Session适合单体应用。

**Q3: 什么是CSRF攻击，如何防御？**> 跨站请求伪造：攻击者诱导用户在已登录状态下执行非预期操作。防御：SameSite Cookie、CSRF Token、验证Referer。

**Q4: OAuth和OIDC的区别？**> OAuth是授权框架，解决"第三方应用能否访问我的资源"；OIDC是认证层，解决"第三方应用能否知道我是谁"。OIDC在OAuth基础上增加了ID Token。

**Q5: 生物识别的最大风险是什么？**> 生物特征不可撤销。如果生物模板泄露，无法像改密码一样"更换指纹"。解决方案：本地存储、使用模板而非原始数据、多因素认证。

## 相关概念 (Related Concepts)

### 数据结构
- [哈希表](../../data-structures/hash-table.md)：密码哈希存储
- [树](../../data-structures/tree.md)：证书链验证的树结构
- [树](../data-structures/tree.md)：证书链验证的树结构

### 算法
- [哈希算法](./cryptography/hash-functions.md)：密码存储与完整性验证
- [加密算法](./cryptography/symmetric-encryption.md)：会话安全与数据传输
- [数字签名](./cryptography/digital-signatures.md)：身份验证与不可否认性
- [加密算法](./encryption.md)：会话安全与数据传输
- [数字签名](./digital-signature.md)：身份验证与不可否认性

### 复杂度分析
- [时间复杂度](../../references/time-complexity.md)：认证验证的时间效率
- [空间复杂度](../../references/space-complexity.md)：会话存储的空间评估

### 系统实现
- [授权](./authorization.md)：权限控制
- [访问控制](./access-control.md)：认证后的权限管理
- [Web安全](./web-security.md)：Web 应用安全
- [常见漏洞](./common-vulnerabilities.md)：安全漏洞与防护

- [授权](./authorization.md) - 权限控制
- [访问控制](./access-control.md) - 认证后的权限管理
- [Web安全](./web-security.md) - Web应用安全
- [常见漏洞](./common-vulnerabilities.md) - 安全漏洞

## 参考资料

1. OWASP Authentication Cheat Sheet
2. NIST Digital Identity Guidelines (SP 800-63)
3. "Real-World Cryptography" by David Wong
4. RFC 6749 (OAuth 2.0)

### 防范特权提升

认证机制设计不当可能导致[权限提升攻击](./privilege-escalation.md)。实施最小权限原则和定期审计是防范措施。
5. RFC 7519 (JWT)

### 认证审计

认证系统的操作应当被记录在[安全审计日志](./audit-logging.md)中，用于安全监控和事件响应。
