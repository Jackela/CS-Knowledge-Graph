# CSRF 跨站请求伪造

## 概念

**CSRF（Cross-Site Request Forgery，跨站请求伪造）** 是一种攻击者诱导已认证用户在不知情的情况下执行非预期操作的Web安全漏洞。

> **核心原理**: 利用用户已认证的会话，伪造用户请求。

---

## 攻击原理

### 攻击流程

```
1. 用户登录银行网站A，获取会话Cookie
2. 用户未退出，访问恶意网站B
3. 网站B包含指向银行A的请求（自动提交表单或图片）
4. 浏览器自动带上A的Cookie发送请求
5. 银行A认为请求来自合法用户，执行操作
```

### 攻击示例

```html
<!-- 恶意网站上的自动提交表单 -->
<form action="https://bank.com/transfer" method="POST" id="csrf">
    <input type="hidden" name="to" value="attacker">
    <input type="hidden" name="amount" value="10000">
</form>
<script>document.getElementById('csrf').submit();</script>

<!-- 或通过图片标签 -->
<img src="https://bank.com/transfer?to=attacker&amount=10000" width="0" height="0">
```

---

## 防御措施

### 1. CSRF Token（推荐）

```python
# 服务端生成Token
import secrets

def generate_csrf_token(session):
    token = secrets.token_urlsafe(32)
    session['csrf_token'] = token
    return token

def validate_csrf_token(request, session):
    token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
    return token == session.get('csrf_token')

# 前端使用
# <form>
#     <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
# </form>
```

### 2. SameSite Cookie

```python
# 设置SameSite属性
response.set_cookie(
    'session_id',
    value=session_id,
    secure=True,
    httponly=True,
    samesite='Strict'  # 或 'Lax'
)
```

| SameSite值 | 说明 |
|-----------|------|
| Strict | 完全禁止第三方Cookie |
| Lax | 允许安全的顶级导航GET请求 |
| None | 允许第三方Cookie（需配合Secure）|

### 3. 验证Referer/Origin

```python
def check_origin(request):
    allowed_origin = "https://example.com"
    origin = request.headers.get('Origin') or request.headers.get('Referer')
    return origin and origin.startswith(allowed_origin)
```

### 4. 双重Cookie验证

```javascript
// 随机值同时存在于Cookie和请求参数中
fetch('/api/action', {
    headers: {
        'X-CSRF-Token': getCookie('csrf_token')
    }
});
```

---

## CSRF vs XSS

| 特性 | CSRF | XSS |
|------|------|-----|
| 利用对象 | 用户会话 | 浏览器执行环境 |
| 需要用户交互 | 需要（访问恶意页面）| 可能不需要 |
| 攻击目标 | 执行用户操作 | 窃取数据/执行脚本 |
| 防御重点 | Token验证 | 输入过滤/输出编码 |

---

## 面试要点

1. **CSRF Token原理**: 攻击者无法获取Token，无法构造有效请求
2. **SameSite限制**: 不支持旧版浏览器（IE）
3. **GET请求安全**: GET不应有副作用，降低CSRF风险

---

## 相关概念

### Web安全
- [Web安全](../web-security.md) - 综合安全防护
- [XSS](../common-vulnerabilities.md) - 跨站脚本攻击
- [CORS](../web-security.md) - 跨域资源共享

### 安全机制
- [认证](../authentication.md) - 身份验证
- [会话管理](../authentication.md) - Cookie安全
- [HTTPS](../../computer-science/networks/https-tls.md) - 传输层安全
