# Web安全 (Web Security)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、OWASP指南及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**Web安全**是保护Web应用程序、服务和用户数据免受各种攻击的实践。随着Web应用的复杂性和重要性增加，Web安全已成为软件工程的核心关注点。

```
┌─────────────────────────────────────────────────────────────────┐
│                   Web安全层次                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   应用层 ────────────────────────────────────────────────      │
│   ├─ 输入验证 / 输出编码                                         │
│   ├─ 认证与授权                                                  │
│   └─ 业务逻辑安全                                                │
│                                                                 │
│   会话层 ────────────────────────────────────────────────      │
│   ├─ Session管理 / Token安全                                     │
│   ├─ Cookie安全属性                                              │
│   └─ CSRF防护                                                    │
│                                                                 │
│   传输层 ────────────────────────────────────────────────      │
│   ├─ HTTPS / TLS配置                                             │
│   ├─ 证书管理                                                    │
│   └─ HSTS                                                        │
│                                                                 │
│   网络层 ────────────────────────────────────────────────      │
│   ├─ 防火墙 / WAF                                                │
│   ├─ 入侵检测                                                    │
│   └─ DDoS防护                                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## HTTPS/TLS

### TLS握手过程

```
┌─────────────────────────────────────────────────────────────────┐
│                   TLS 1.3 握手过程                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Client                          Server                        │
│     │                               │                           │
│     │ ───── ClientHello ──────────▶ │                           │
│     │  [支持的密码套件]              │                           │
│     │  [Client Random]              │                           │
│     │  [Key Share]                  │                           │
│     │                               │                           │
│     │ ◀──── ServerHello ─────────── │                           │
│     │  [选定的密码套件]              │                           │
│     │  [Server Random]              │                           │
│     │  [Key Share]                  │                           │
│     │                               │                           │
│     │ ◀──── {EncryptedExtensions} ─ │                           │
│     │ ◀──── {Certificate} ───────── │                           │
│     │ ◀──── {CertificateVerify} ─── │                           │
│     │ ◀──── {Finished} ──────────── │                           │
│     │                               │                           │
│     │ ───── {Finished} ──────────▶  │                           │
│     │                               │                           │
│     │ ═════ 应用数据 (加密) ═══════ │                           │
│     │                               │                           │
│                                                                 │
│   {} 表示加密的消息                                              │
│   TLS 1.3将握手优化为1-RTT (0-RTT支持会话恢复)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 证书与HSTS

```python
# HSTS (HTTP Strict Transport Security) 头部
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload

# Nginx配置
server {
    listen 443 ssl http2;
    server_name example.com;
    
    # SSL证书
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 强制TLS版本
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # 其他安全头部
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 内容安全策略 (CSP)

**CSP**通过定义允许加载的资源来源，有效防止XSS等代码注入攻击。

```http
Content-Security-Policy: 
    default-src 'self';
    script-src 'self' 'nonce-abc123' https://cdn.example.com;
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    font-src 'self' https://fonts.gstatic.com;
    connect-src 'self' https://api.example.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
    upgrade-insecure-requests;
```

### CSP指令说明

| 指令 | 说明 | 示例 |
|------|------|------|
| default-src | 默认资源策略 | 'self' |
| script-src | JavaScript来源 | 'self' 'nonce-xxx' |
| style-src | CSS来源 | 'self' 'unsafe-inline' |
| img-src | 图片来源 | 'self' data: https: |
| connect-src | XHR/WebSocket | 'self' api.example.com |
| frame-ancestors | 允许嵌入的父页面 | 'none' (防点击劫持) |
| report-uri | 违规报告地址 | /csp-report |

```python
# Flask CSP示例
from flask import Flask, render_template

app = Flask(__name__)

@app.after_request
def set_security_headers(response):
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'nonce-{nonce}' https://cdn.example.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "frame-ancestors 'none';"
    ).format(nonce=get_nonce())
    
    response.headers['Content-Security-Policy'] = csp
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response
```

---

## Cookie安全

### Cookie安全属性

```
Set-Cookie: session=abc123; 
    HttpOnly;      # 禁止JavaScript访问，防XSS
    Secure;        # 仅HTTPS传输
    SameSite=Strict;  # 防CSRF
    Max-Age=3600;  # 1小时过期
    Path=/;        # 路径限制
    Domain=.example.com  # 域名限制
```

### SameSite属性详解

| SameSite值 | 行为 | 适用场景 |
|------------|------|----------|
| Strict | 仅同站请求发送Cookie | 高安全性需求 |
| Lax | 顶级导航GET请求可发送 | 一般网站（推荐） |
| None | 所有请求发送Cookie | 需配合Secure，第三方嵌入 |

```python
# Flask Cookie设置
from flask import Flask, session
from datetime import timedelta

app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,      # HttpOnly
    SESSION_COOKIE_SECURE=True,        # Secure
    SESSION_COOKIE_SAMESITE='Lax',     # SameSite
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)  # 过期时间
)

# 手动设置Cookie
@app.route('/set-cookie')
def set_cookie():
    resp = make_response('Cookie set')
    resp.set_cookie(
        'token',
        'secret_value',
        httponly=True,
        secure=True,
        samesite='Strict',
        max_age=3600
    )
    return resp
```

---

## CORS (跨域资源共享)

```
┌─────────────────────────────────────────────────────────────────┐
│                   CORS 工作原理                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   简单请求 (Simple Request):                                    │
│   ┌─────────┐ GET /data ──────▶ ┌─────────┐                    │
│   │  site-a │  Origin: site-a   │  site-b │                    │
│   │ .com    │◀──── 200 OK ─────│ .com    │                    │
│   └─────────┘  Access-Control-Allow-Origin: site-a.com         │
│                                                                 │
│   预检请求 (Preflight):                                         │
│   ┌─────────┐ OPTIONS /data ──▶ ┌─────────┐                    │
│   │  site-a │  Origin: site-a   │  site-b │                    │
│   │ .com    │  Access-Control-Request-Method: POST             │
│   │         │◀──── 200 OK ─────│ .com    │                    │
│   │         │  Access-Control-Allow-Origin: site-a.com         │
│   │         │  Access-Control-Allow-Methods: POST, GET         │
│   │         │  Access-Control-Allow-Headers: Content-Type      │
│   └─────────┘ POST /data ─────▶ └─────────┘                    │
│               Origin: site-a.com                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

```python
# Flask-CORS配置
from flask_cors import CORS

# 允许特定来源
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://app.example.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True  # 允许携带Cookie
    }
})

# 手动处理CORS
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    allowed_origins = ['https://app.example.com']
    
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    
    return response
```

---

## 安全HTTP头部

### 推荐的安全头部配置

```python
# 完整的Flask安全头部中间件
@app.after_request
def security_headers(response):
    # 防止页面被嵌入iframe（点击劫持）
    response.headers['X-Frame-Options'] = 'DENY'
    
    # 防止MIME类型嗅探
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS保护（浏览器内置）
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 引用策略
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # 权限策略（控制浏览器API）
    response.headers['Permissions-Policy'] = (
        'camera=(), microphone=(), geolocation=(self), '
        'payment=(), usb=(), magnetometer=(), gyroscope=()'
    )
    
    # 内容安全策略
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'nonce-{nonce}'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    
    return response
```

---

## Web认证机制

### Session-based认证

```python
from flask import Flask, session, request
from functools import wraps
import redis

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Redis存储Session
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get('session_id')
        if not session_id or not redis_client.exists(f"session:{session_id}"):
            return {"error": "Unauthorized"}, 401
        
        # 刷新Session过期时间
        redis_client.expire(f"session:{session_id}", 3600)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if verify_credentials(username, password):
        import secrets
        session_id = secrets.token_urlsafe(32)
        
        # 存储Session
        redis_client.hset(f"session:{session_id}", mapping={
            'user_id': user.id,
            'username': user.username
        })
        redis_client.expire(f"session:{session_id}", 3600)
        
        resp = make_response({"message": "Logged in"})
        resp.set_cookie(
            'session_id', 
            session_id, 
            httponly=True, 
            secure=True, 
            samesite='Strict',
            max_age=3600
        )
        return resp
    
    return {"error": "Invalid credentials"}, 401
```

---

## 防御常见攻击

### XSS防御

```python
from markupsafe import Markup, escape

# 输出编码
def safe_render(user_input):
    # 自动转义HTML特殊字符
    return escape(user_input)

# 使用模板自动转义
from flask import render_template_string

@app.route('/greet')
def greet():
    name = request.args.get('name', '')
    # 模板自动转义
    return render_template_string('<h1>Hello {{ name }}</h1>', name=name)

# 富文本输入处理（使用白名单）
import bleach

ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3']
ALLOWED_ATTRIBUTES = {}

def sanitize_html(html):
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
```

### CSRF防御

```python
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # Token有效期

csrf = CSRFProtect(app)

# 手动验证CSRF（API场景）
import secrets

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']

def validate_csrf_token(token):
    return token == session.get('csrf_token')

@app.route('/api/action', methods=['POST'])
def api_action():
    token = request.headers.get('X-CSRF-Token')
    if not validate_csrf_token(token):
        return {"error": "Invalid CSRF token"}, 403
    # 处理请求...
```

### SQL注入防御

```python
# ❌ 危险 - 字符串拼接
query = f"SELECT * FROM users WHERE username = '{username}'"

# ✅ 安全 - 参数化查询
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))

# ✅ 使用ORM
user = User.query.filter_by(username=username).first()

# ✅ 使用SQLAlchemy参数绑定
from sqlalchemy import text
result = db.session.execute(
    text("SELECT * FROM users WHERE username = :username"),
    {"username": username}
)
```

---

## 最佳实践

### 安全开发检查清单

```
□ 传输安全
  □ 全站HTTPS
  □ HSTS启用
  □ TLS 1.2+ only

□ 认证与会话
  □ 强密码策略
  □ 多因素认证
  □ Session超时
  □ 安全Cookie属性

□ 输入处理
  □ 所有输入验证
  □ 输出编码
  □ 参数化查询
  □ 文件上传限制

□ 访问控制
  □ 最小权限原则
  □ 权限验证在每个端点
  □ 水平越权检查

□ 安全头部
  □ CSP配置
  □ X-Frame-Options
  □ X-Content-Type-Options
  □ Secure Cookies

□ 监控与日志
  □ 安全事件记录
  □ 异常访问检测
  □ 定期安全扫描
```

---

## 面试要点

**Q1: HTTPS握手过程是怎样的？**> TLS 1.3握手：1) ClientHello发送支持的算法和密钥共享；2) ServerHello选择算法并发送证书；3) 双方生成会话密钥；4) 加密通信。相比TLS 1.2减少了往返次数。

**Q2: CSP如何防止XSS？**> CSP通过白名单机制限制页面可加载的资源（脚本、样式等）。即使攻击者注入恶意脚本，如果脚本来源不在CSP白名单中，浏览器也不会执行。配合nonce或hash可允许特定内联脚本。

**Q3: SameSite Cookie的作用？**> SameSite控制Cookie在跨站请求时是否发送。Strict最严格（完全禁止），Lax允许顶级GET导航（用户体验好），None允许所有但需Secure。有效防止CSRF攻击。

---

## 相关概念 (Related Concepts)

### 数据结构
- [哈希表](../computer-science/data-structures/hash-table.md)：安全令牌存储
- [树](../computer-science/data-structures/tree.md)：DOM 树与安全扫描

### 算法

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)：安全检测的时间效率
- [空间复杂度](../references/space-complexity.md)：安全扫描的资源消耗

### 系统实现
- [身份认证](./authentication.md)：Web 认证机制
- [授权](./authorization.md)：访问控制
- [常见漏洞](./common-vulnerabilities.md)：Web 安全漏洞详解


---

## 参考资料

1. OWASP Web Security Testing Guide
2. Mozilla Web Security Guidelines
3. MDN Web Security: https://developer.mozilla.org/en-US/docs/Web/Security
4. Google Web Fundamentals - Security
5. Security Headers: https://securityheaders.com/

### 安全审计与日志

系统的[安全审计](./system-security/audit-logging.md)和日志记录是安全运营的基础，用于监控、取证和合规。
