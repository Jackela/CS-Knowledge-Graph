# API 安全 (API Security)

API 安全是保护应用程序编程接口免受攻击和滥用的安全实践，确保 API 的机密性、完整性和可用性。

## 常见 API 安全风险

### OWASP API Security Top 10

| 排名 | 风险 | 说明 |
|------|------|------|
| 1 | 失效的对象级授权 | 攻击者访问其他用户的资源 |
| 2 | 失效的用户认证 | 弱认证机制被绕过 |
| 3 | 过度的数据暴露 | API 返回过多的敏感数据 |
| 4 | 缺乏资源和速率限制 | 资源耗尽或暴力攻击 |
| 5 | 失效的功能级授权 | 普通用户执行管理员操作 |
| 6 | 批量赋值 | 客户端设置不应修改的字段 |
| 7 | 安全配置错误 | 默认配置、错误头等 |
| 8 | 注入 | SQL、NoSQL、命令注入 |
| 9 | 资产管理不当 | 旧版本 API 未下线 |
| 10 | 日志记录和监控不足 | 无法检测和响应攻击 |

## 安全实践

### 1. 认证与授权
```python
# JWT 认证示例
from functools import wraps
import jwt

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'error': '缺少认证令牌'}, 401
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = payload
        except jwt.InvalidTokenError:
            return {'error': '无效的令牌'}, 401
            
        return f(*args, **kwargs)
    return decorated

@app.route('/api/users/<int:user_id>')
@require_auth
def get_user(user_id):
    # 验证对象级授权
    if request.user['id'] != user_id and not request.user.get('is_admin'):
        return {'error': '无权访问此资源'}, 403
    
    user = User.query.get(user_id)
    return user.to_json()
```

### 2. 速率限制
```python
# Flask-Limiter 示例
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")  # 登录接口严格限制
def login():
    # 登录逻辑
    pass

@app.route("/api/public")
@limiter.limit("100 per hour")  # 公开接口宽松限制
def public():
    pass
```

### 3. 输入验证
```python
# 使用 Pydantic 进行严格的输入验证
from pydantic import BaseModel, validator

class CreateUserRequest(BaseModel):
    username: str
    email: str
    role: str = "user"  # 默认值，不允许批量赋值
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 20:
            raise ValueError('用户名长度必须在3-20之间')
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        # 防止客户端自行提升权限
        allowed_roles = ['user', 'viewer']
        if v not in allowed_roles:
            raise ValueError('无效的角色')
        return v
```

### 4. HTTPS 强制
```python
# Flask-Talisman 安全头部
from flask_talisman import Talisman

Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self'",
    }
)

# 安全响应头
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response
```

## API 网关安全

```
┌─────────────────────────────────────────────────────────┐
│                      API 网关                            │
├─────────────────────────────────────────────────────────┤
│  SSL/TLS 终止                                            │
│  认证（OAuth2/JWT/API Key）                              │
│  速率限制                                                │
│  请求/响应校验                                           │
│  WAF 防护                                                │
│  日志记录                                                │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   后端服务     │
                    └───────────────┘
```

## 相关概念

### Web 安全
- [Web 安全](../web-security.md) - Web 应用安全概述
- [常见漏洞](../common-vulnerabilities.md) - OWASP Top 10
- [认证](../authentication.md) - 身份认证机制

### 加密与传输
- [HTTPS/TLS](../../computer-science/networks/https-tls.md) - 传输层安全
- [JWT](../authentication.md) - JSON Web Token
