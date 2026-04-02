# 会话管理 (Session Management)

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、OWASP 指南及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**会话管理 (Session Management)** 是 Web 安全的核心机制，用于在 HTTP 无状态协议上维护用户的认证状态。安全的会话管理涉及会话标识的生成、传输、存储和销毁的全生命周期管理。会话劫持、固定攻击和预测攻击是常见的会话安全威胁，需要通过安全的令牌生成、Cookie 属性设置和会话超时策略来防御。

```
┌─────────────────────────────────────────────────────────────────┐
│                   会话生命周期管理                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐        │
│   │ 创建    │──▶│ 维护    │──▶│ 验证    │──▶│ 销毁    │        │
│   └─────────┘   └─────────┘   └─────────┘   └─────────┘        │
│        │             │             │             │             │
│        ▼             ▼             ▼             ▼             │
│   • 安全随机    • Cookie属性   • 签名验证    • 服务端删除      │
│     生成ID      • 传输安全     • 过期检查    • 客户端清除      │
│   • 绑定IP/UA   • 定期刷新     • 权限检查    • 登出通知        │
│   • 设置过期    • 并发控制     • 异常检测    • 全局失效        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心概念

### 会话 vs Token

```
┌─────────────────────────────────────────────────────────────────┐
│              Session-Based vs Token-Based 对比                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Session-Based (Stateful)                                      │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                                                         │  │
│   │  Client          Server (Session Store)                │  │
│   │    │                    │                              │  │
│   │    │── Session ID ─────▶│  1. 验证ID                   │  │
│   │    │   (in Cookie)      │  2. 查询Session数据          │  │
│   │    │◀── Response ───────│  3. 执行业务逻辑             │  │
│   │    │                    │                              │  │
│   │  存储: Cookie           存储: Server (Memory/Redis/DB) │  │
│   │                                                         │  │
│   │  优点: 可立即撤销、可存储大量数据、易于管理             │  │
│   │  缺点: 服务端有状态、跨域复杂、需要共享存储             │  │
│   │                                                         │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   Token-Based (Stateless)                                       │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                                                         │  │
│   │  Client          Server                                 │  │
│   │    │                    │                              │  │
│   │    │── JWT Token ──────▶│  1. 验证签名                 │  │
│   │    │   (in Header)      │  2. 解析Token获取用户信息    │  │
│   │    │◀── Response ───────│  3. 执行业务逻辑             │  │
│   │    │                    │  (无需查询存储)              │  │
│   │  存储: localStorage/    存储: 无 (或仅黑名单)          │  │
│   │        Cookie                                           │  │
│   │                                                         │  │
│   │  优点: 无状态、跨域友好、适合微服务、性能好             │  │
│   │  缺点: 无法立即撤销、Token体积大、需处理续期            │  │
│   │                                                         │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Cookie 安全属性

```
┌─────────────────────────────────────────────────────────────────┐
│                   Cookie 安全属性详解                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Set-Cookie: session=xxx; Expires=Wed, 21 Oct 2026 07:28:00 GMT│
│                            Max-Age=3600                         │
│                            Domain=.example.com                  │
│                            Path=/                               │
│                            Secure                               │
│                            HttpOnly                             │
│                            SameSite=Strict                      │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Secure                                                        │
│   • 仅通过 HTTPS 传输 Cookie                                     │
│   • 防止中间人窃听会话 ID                                        │
│   • 生产环境必须启用                                             │
│                                                                 │
│   HttpOnly                                                      │
│   • 禁止 JavaScript 访问 Cookie                                  │
│   • 防止 XSS 攻击窃取会话 ID                                     │
│   • 防御 document.cookie 读取                                    │
│                                                                 │
│   SameSite                                                      │
│   • Strict: 仅同站请求发送 Cookie                                │
│   • Lax:   顶级导航 GET 请求可发送 (推荐默认)                    │
│   • None:  所有请求发送 (需配合 Secure)                          │
│   • 主要防御 CSRF 攻击                                           │
│                                                                 │
│   Domain / Path                                                 │
│   • 限制 Cookie 的作用域                                         │
│   • 最小权限原则，精确限定                                       │
│                                                                 │
│   Expires / Max-Age                                             │
│   • 设置合理的过期时间                                           │
│   • 敏感操作使用短会话                                           │
│   • 记住我功能使用长期令牌                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 实现方式

### 1. 安全的 Session 管理

```python
import secrets
import hashlib
import hmac
import json
import redis
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class SessionStoreType(Enum):
    MEMORY = "memory"
    REDIS = "redis"
    DATABASE = "database"

@dataclass
class SessionConfig:
    """会话配置"""
    session_timeout: int = 3600  # 1小时
    absolute_timeout: int = 86400  # 24小时绝对超时
    idle_timeout: int = 1800  # 30分钟空闲超时
    regenerate_id_on_auth: bool = True  # 登录后重新生成ID
    bind_to_ip: bool = False  # 绑定IP
    bind_to_user_agent: bool = True  # 绑定UA
    max_concurrent_sessions: int = 5  # 最大并发会话数
    secure_cookie: bool = True
    httponly_cookie: bool = True
    samesite_cookie: str = "Lax"


class SessionData:
    """会话数据结构"""
    
    def __init__(self, session_id: str, user_id: Optional[str] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        self.ip_address: Optional[str] = None
        self.user_agent: Optional[str] = None
        self.data: Dict[str, Any] = {}
        self.is_valid = True
    
    def to_dict(self) -> Dict:
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'data': self.data,
            'is_valid': self.is_valid
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SessionData':
        session = cls(data['session_id'], data.get('user_id'))
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.last_accessed = datetime.fromisoformat(data['last_accessed'])
        session.ip_address = data.get('ip_address')
        session.user_agent = data.get('user_agent')
        session.data = data.get('data', {})
        session.is_valid = data.get('is_valid', True)
        return session


class SecureSessionManager:
    """安全会话管理器"""
    
    def __init__(self, config: SessionConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis = redis_client
        self._memory_store: Dict[str, SessionData] = {}
        self._secret_key = secrets.token_bytes(32)
    
    def _generate_session_id(self) -> str:
        """生成加密安全的会话 ID"""
        # 256-bit 随机数，URL-safe base64 编码
        return secrets.token_urlsafe(32)
    
    def _hash_session_id(self, session_id: str) -> str:
        """
        对会话 ID 进行哈希（存储时使用）
        防止会话 ID 泄露导致会话劫持
        """
        return hashlib.sha256(session_id.encode()).hexdigest()
    
    def _sign_session(self, session_id: str) -> str:
        """对会话 ID 进行签名（用于 Cookie）"""
        signature = hmac.new(
            self._secret_key,
            session_id.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        return f"{session_id}.{signature}"
    
    def _verify_session_signature(self, signed_session: str) -> Optional[str]:
        """验证会话签名"""
        try:
            session_id, signature = signed_session.rsplit('.', 1)
            expected = hmac.new(
                self._secret_key,
                session_id.encode(),
                hashlib.sha256
            ).hexdigest()[:16]
            
            if hmac.compare_digest(signature, expected):
                return session_id
            return None
        except ValueError:
            return None
    
    def create_session(self, user_id: Optional[str] = None,
                      ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None) -> Tuple[str, SessionData]:
        """创建新会话"""
        session_id = self._generate_session_id()
        session = SessionData(session_id, user_id)
        session.ip_address = ip_address
        session.user_agent = user_agent
        
        # 存储会话
        self._store_session(session)
        
        # 限制用户并发会话数
        if user_id:
            self._limit_concurrent_sessions(user_id)
        
        return session_id, session
    
    def _store_session(self, session: SessionData):
        """存储会话"""
        hashed_id = self._hash_session_id(session.session_id)
        
        if self.redis:
            # Redis 存储，设置过期时间
            ttl = self.config.session_timeout
            self.redis.setex(
                f"session:{hashed_id}",
                ttl,
                json.dumps(session.to_dict())
            )
        else:
            # 内存存储
            self._memory_store[hashed_id] = session
    
    def _limit_concurrent_sessions(self, user_id: str):
        """限制用户并发会话数"""
        user_sessions = self._get_user_sessions(user_id)
        
        if len(user_sessions) > self.config.max_concurrent_sessions:
            # 删除最旧的会话
            sorted_sessions = sorted(
                user_sessions,
                key=lambda s: s.last_accessed
            )
            for old_session in sorted_sessions[:-self.config.max_concurrent_sessions]:
                self.invalidate_session(old_session.session_id)
    
    def _get_user_sessions(self, user_id: str) -> list:
        """获取用户的所有会话"""
        sessions = []
        
        if self.redis:
            # 需要维护用户到会话的映射
            session_ids = self.redis.smembers(f"user_sessions:{user_id}")
            for sid in session_ids:
                session_data = self.redis.get(f"session:{sid.decode()}")
                if session_data:
                    sessions.append(SessionData.from_dict(json.loads(session_data)))
        else:
            for session in self._memory_store.values():
                if session.user_id == user_id and session.is_valid:
                    sessions.append(session)
        
        return sessions
    
    def validate_session(self, session_id: str,
                        ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None) -> Optional[SessionData]:
        """
        验证会话有效性
        包括超时检查、绑定检查等
        """
        hashed_id = self._hash_session_id(session_id)
        
        # 获取会话数据
        if self.redis:
            data = self.redis.get(f"session:{hashed_id}")
            if not data:
                return None
            session = SessionData.from_dict(json.loads(data))
        else:
            session = self._memory_store.get(hashed_id)
        
        if not session or not session.is_valid:
            return None
        
        # 检查绝对超时
        session_age = (datetime.utcnow() - session.created_at).total_seconds()
        if session_age > self.config.absolute_timeout:
            self.invalidate_session(session_id)
            return None
        
        # 检查空闲超时
        idle_time = (datetime.utcnow() - session.last_accessed).total_seconds()
        if idle_time > self.config.idle_timeout:
            self.invalidate_session(session_id)
            return None
        
        # 检查 IP 绑定
        if self.config.bind_to_ip and ip_address:
            if session.ip_address != ip_address:
                # IP 变化，可能是会话劫持
                self._handle_suspicious_activity(session, "IP mismatch")
                return None
        
        # 检查 UA 绑定
        if self.config.bind_to_user_agent and user_agent:
            if session.user_agent != user_agent:
                self._handle_suspicious_activity(session, "UA mismatch")
                return None
        
        # 更新最后访问时间
        session.last_accessed = datetime.utcnow()
        self._store_session(session)
        
        return session
    
    def _handle_suspicious_activity(self, session: SessionData, reason: str):
        """处理可疑活动"""
        # 记录安全日志
        print(f"Security Alert: Session {session.session_id} - {reason}")
        # 可选：立即失效会话
        self.invalidate_session(session.session_id)
    
    def regenerate_session_id(self, old_session_id: str) -> Optional[str]:
        """
        重新生成会话 ID（防止会话固定攻击）
        通常在权限变更（如登录）后调用
        """
        session = self.validate_session(old_session_id)
        if not session:
            return None
        
        # 删除旧会话
        self.invalidate_session(old_session_id)
        
        # 创建新 ID，保留数据
        new_session_id = self._generate_session_id()
        session.session_id = new_session_id
        session.created_at = datetime.utcnow()
        
        self._store_session(session)
        
        return new_session_id
    
    def invalidate_session(self, session_id: str):
        """使会话失效（登出）"""
        hashed_id = self._hash_session_id(session_id)
        
        if self.redis:
            self.redis.delete(f"session:{hashed_id}")
        else:
            if hashed_id in self._memory_store:
                self._memory_store[hashed_id].is_valid = False
                del self._memory_store[hashed_id]
    
    def invalidate_all_user_sessions(self, user_id: str):
        """使用户所有会话失效（全局登出）"""
        sessions = self._get_user_sessions(user_id)
        for session in sessions:
            self.invalidate_session(session.session_id)
    
    def get_session_cookie(self, session_id: str) -> Dict[str, Any]:
        """获取用于设置 Cookie 的参数"""
        signed_session = self._sign_session(session_id)
        
        return {
            'key': 'session_id',
            'value': signed_session,
            'max_age': self.config.session_timeout,
            'secure': self.config.secure_cookie,
            'httponly': self.config.httponly_cookie,
            'samesite': self.config.samesite_cookie,
            'path': '/'
        }


# Flask 集成示例
from flask import Flask, request, session as flask_session, make_response

app = Flask(__name__)

# 配置
session_config = SessionConfig(
    session_timeout=3600,
    bind_to_user_agent=True,
    secure_cookie=True,
    httponly_cookie=True,
    samesite_cookie='Lax'
)

# 初始化（生产环境使用 Redis）
redis_client = redis.Redis(host='localhost', port=6379, db=0)
session_manager = SecureSessionManager(session_config, redis_client)


@app.route('/login', methods=['POST'])
def login():
    """用户登录"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # 验证凭证（简化示例）
    if verify_credentials(username, password):
        user_id = get_user_id(username)
        
        # 创建会话
        session_id, session_data = session_manager.create_session(
            user_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        # 设置 Cookie
        cookie_params = session_manager.get_session_cookie(session_id)
        response = make_response({'status': 'success'})
        response.set_cookie(**cookie_params)
        
        return response
    
    return {'error': 'Invalid credentials'}, 401


@app.route('/api/protected')
def protected_resource():
    """受保护资源"""
    signed_session = request.cookies.get('session_id')
    if not signed_session:
        return {'error': 'No session'}, 401
    
    # 验证签名
    session_id = session_manager._verify_session_signature(signed_session)
    if not session_id:
        return {'error': 'Invalid session'}, 401
    
    # 验证会话
    session = session_manager.validate_session(
        session_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    if not session:
        return {'error': 'Session expired or invalid'}, 401
    
    return {'user_id': session.user_id, 'data': 'protected'}


@app.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    signed_session = request.cookies.get('session_id')
    if signed_session:
        session_id = session_manager._verify_session_signature(signed_session)
        if session_id:
            session_manager.invalidate_session(session_id)
    
    response = make_response({'status': 'logged out'})
    response.delete_cookie('session_id')
    return response
```

### 2. JWT 会话管理

```python
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Set, Tuple, Any

class JWTSessionManager:
    """基于 JWT 的会话管理"""
    
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.refresh_secret = secrets.token_urlsafe(32)
        # 用于撤销的 Token 黑名单
        self.revoked_tokens: Set[str] = set()
    
    def create_session(self, user_id: str, claims: Dict = None,
                      access_expiry_minutes: int = 15,
                      refresh_expiry_days: int = 7) -> Tuple[str, str, Dict]:
        """
        创建会话（Access Token + Refresh Token）
        """
        now = datetime.utcnow()
        jti = secrets.token_urlsafe(16)
        
        # Access Token - 短期有效
        access_payload = {
            'sub': user_id,
            'jti': jti,
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(minutes=access_expiry_minutes),
            'token_family': secrets.token_urlsafe(8)
        }
        if claims:
            access_payload.update(claims)
        
        access_token = jwt.encode(
            access_payload,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        # Refresh Token - 长期有效，仅用于获取新 Access Token
        refresh_payload = {
            'sub': user_id,
            'jti': secrets.token_urlsafe(16),
            'type': 'refresh',
            'access_jti': jti,  # 关联 Access Token
            'token_family': access_payload['token_family'],
            'iat': now,
            'exp': now + timedelta(days=refresh_expiry_days)
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            self.refresh_secret,
            algorithm=self.algorithm
        )
        
        return access_token, refresh_token, access_payload
    
    def validate_access_token(self, token: str) -> Optional[Dict]:
        """验证 Access Token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # 检查类型
            if payload.get('type') != 'access':
                return None
            
            # 检查是否在黑名单
            if payload.get('jti') in self.revoked_tokens:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_session(self, refresh_token: str) -> Optional[Tuple[str, str, Dict]]:
        """
        使用 Refresh Token 获取新的 Token 对
        实现 Refresh Token 轮换增加安全性
        """
        try:
            payload = jwt.decode(
                refresh_token,
                self.refresh_secret,
                algorithms=[self.algorithm]
            )
            
            if payload.get('type') != 'refresh':
                return None
            
            # 检查是否在黑名单（检测重放）
            if payload.get('jti') in self.revoked_tokens:
                # 可能检测到 Token 被盗用
                # 使整个 Token Family 失效
                self._revoke_token_family(payload.get('token_family'))
                return None
            
            # 撤销旧的 Refresh Token
            self.revoked_tokens.add(payload['jti'])
            
            # 可选：撤销关联的 Access Token
            if payload.get('access_jti'):
                self.revoked_tokens.add(payload['access_jti'])
            
            # 创建新的 Token 对
            user_id = payload['sub']
            return self.create_session(
                user_id,
                token_family=payload.get('token_family')
            )
            
        except jwt.InvalidTokenError:
            return None
    
    def _revoke_token_family(self, token_family: str):
        """撤销整个 Token Family（检测到盗用时）"""
        # 在实际实现中，需要查询并撤销该 family 的所有 token
        print(f"Revoking token family: {token_family}")
    
    def revoke_token(self, token: str, token_type: str = 'access'):
        """撤销 Token（登出）"""
        try:
            if token_type == 'access':
                payload = jwt.decode(
                    token,
                    self.secret_key,
                    algorithms=[self.algorithm],
                    options={'verify_exp': False}
                )
            else:
                payload = jwt.decode(
                    token,
                    self.refresh_secret,
                    algorithms=[self.algorithm],
                    options={'verify_exp': False}
                )
            
            self.revoked_tokens.add(payload.get('jti'))
        except jwt.InvalidTokenError:
            pass


# 双 Token 存储策略
class SecureTokenStorage:
    """安全的 Token 存储方案"""
    
    @staticmethod
    def set_access_token_cookie(response, token: str, max_age: int = 900):
        """
        Access Token 存储在内存中（不作为 Cookie）
        或设置短生命周期的 Cookie
        """
        response.set_cookie(
            'access_token',
            token,
            max_age=max_age,
            secure=True,
            httponly=True,
            samesite='Strict'
        )
    
    @staticmethod
    def set_refresh_token_cookie(response, token: str, max_age: int = 604800):
        """
        Refresh Token 使用严格的安全属性
        或存储在 httpOnly Cookie 中
        """
        response.set_cookie(
            'refresh_token',
            token,
            max_age=max_age,
            secure=True,
            httponly=True,
            samesite='Strict',
            path='/api/refresh'  # 限制路径
        )
```

### 3. 会话安全监控

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import ipaddress

@dataclass
class SessionEvent:
    """会话安全事件"""
    timestamp: datetime
    session_id: str
    user_id: Optional[str]
    event_type: str  # login, logout, suspicious, hijack_attempt
    ip_address: str
    user_agent: Optional[str]
    details: dict


class SessionSecurityMonitor:
    """会话安全监控"""
    
    def __init__(self):
        self.events: List[SessionEvent] = []
        self.suspicious_ips: set = set()
    
    def detect_anomalies(self, session: SessionData, 
                        current_ip: str,
                        current_ua: str) -> List[str]:
        """检测会话异常"""
        alerts = []
        
        # 检测 IP 变化
        if session.ip_address and session.ip_address != current_ip:
            # 检查是否为正常切换（如移动网络）
            if not self._is_ip_change_reasonable(session.ip_address, current_ip):
                alerts.append("IP_CHANGE_SUSPICIOUS")
        
        # 检测 UA 变化
        if session.user_agent and session.user_agent != current_ua:
            alerts.append("USER_AGENT_CHANGE")
        
        # 检测时间异常（如半夜登录）
        hour = datetime.utcnow().hour
        if hour < 6 or hour > 23:
            alerts.append("UNUSUAL_HOUR")
        
        # 检测并发会话异常
        # ...
        
        return alerts
    
    def _is_ip_change_reasonable(self, old_ip: str, new_ip: str) -> bool:
        """判断 IP 变化是否合理"""
        try:
            old = ipaddress.ip_address(old_ip)
            new = ipaddress.ip_address(new_ip)
            
            # 同一 /24 网段认为是合理的
            if isinstance(old, ipaddress.IPv4Address):
                old_network = ipaddress.ip_network(f"{old}/24", strict=False)
                return new in old_network
            
            return False
        except ValueError:
            return False
    
    def record_event(self, event: SessionEvent):
        """记录安全事件"""
        self.events.append(event)
        
        # 触发告警
        if event.event_type in ['suspicious', 'hijack_attempt']:
            self._send_alert(event)
    
    def _send_alert(self, event: SessionEvent):
        """发送安全告警"""
        print(f"SECURITY ALERT: {event.event_type} from {event.ip_address}")
        # 实际实现：发送邮件、短信、SIEM 等


def verify_credentials(username: str, password: str) -> bool:
    """验证用户凭证（占位）"""
    # 实际实现应查询数据库并验证密码哈希
    return True

def get_user_id(username: str) -> str:
    """获取用户 ID（占位）"""
    return f"user_{username}"
```

---

## 应用场景

### 场景 1: 多端会话管理

```
┌─────────────────────────────────────────────────────────────────┐
│                   多端会话管理架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   用户                                                           │
│     │                                                            │
│     ├────────────┬────────────┬────────────┐                   │
│     ▼            ▼            ▼            ▼                   │
│   ┌────┐      ┌────┐      ┌────┐      ┌────┐                  │
│   │Web │      │iOS │      │And │      │SPA │                  │
│   │浏览器│      │App │      │App │      │    │                  │
│   └──┬─┘      └──┬─┘      └──┬─┘      └──┬─┘                  │
│      │            │            │            │                   │
│      └────────────┴────────────┴────────────┘                   │
│                   │                                             │
│                   ▼                                             │
│         ┌─────────────────┐                                    │
│         │  Auth Server    │                                    │
│         │  • 统一认证     │                                    │
│         │  • Token 颁发   │                                    │
│         │  • 会话管理     │                                    │
│         └────────┬────────┘                                    │
│                  │                                              │
│         ┌────────┴────────┐                                    │
│         ▼                 ▼                                    │
│   ┌──────────┐      ┌──────────┐                              │
│   │ Session  │      │  Token   │                              │
│   │ Store    │      │  Store   │                              │
│   │ (Redis)  │      │ (内存/DB)│                              │
│   └──────────┘      └──────────┘                              │
│                                                                 │
│   特性:                                                         │
│   • 支持多端同时登录                                            │
│   • 一端登出可选全局登出                                        │
│   • 设备管理和信任设备                                          │
│   • 异常登录检测                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

### Q1: Session 和 JWT 如何选择？各自的优缺点？

**A:**

| 特性 | Session | JWT |
|------|---------|-----|
| 状态 | 服务端有状态 | 无状态 |
| 撤销 | 即时（删除即可） | 困难（需黑名单） |
| 跨域 | 需要额外处理 | 天然支持 |
| 存储 | Cookie | Header/Cookie |
| 大小 | 小（仅 ID） | 大（包含 claims） |
| 扩展性 | 需共享存储 | 无需共享 |

**选择建议:**
- 使用 Session: 需要即时撤销、会话数据多、单体应用
- 使用 JWT: 微服务、移动端 API、跨域场景、高并发读
- 混合方案: JWT + Session（JWT 用于 API，Session 用于敏感操作）

### Q2: 如何防止会话固定攻击 (Session Fixation)？

**A:**

会话固定攻击：攻击者让用户使用攻击者已知的 Session ID 登录，从而劫持会话。

**防御措施:**

1. **登录后重新生成 Session ID**
   ```python
   # 登录前
   old_session = request.cookies.get('session_id')
   
   # 验证凭证...
   
   # 登录后 - 重新生成 ID
   new_session_id = session_manager.regenerate_session_id(old_session)
   ```

2. **不接受 URL 中的 Session ID**
   - 仅接受 Cookie 中的 Session ID
   - 禁用 URL 重写

3. **设置合理的 Cookie 属性**
   - HttpOnly、Secure、SameSite

### Q3: Cookie 的 SameSite 属性有什么作用？

**A:**

SameSite 控制 Cookie 在跨站请求时是否发送，用于防御 CSRF 攻击：

| 值 | 行为 | 场景 |
|----|------|------|
| Strict | 仅同站请求发送 | 高安全场景（银行） |
| Lax | 顶级导航 GET 可发送 | 一般网站（推荐） |
| None | 所有请求发送 | 需要配合 Secure |

**Lax 的具体行为:**
- 加载图片/CSS/JS：不发送
- 点击链接（顶级导航）：发送
- POST 表单提交：不发送
- iframe 内请求：不发送

### Q4: 如何实现安全的"记住我"功能？

**A:**

```python
def create_remember_me_token(user_id: str) -> str:
    """
    安全的记住我实现
    使用持久化 Cookie + 服务端存储 Selector + Validator
    """
    import secrets
    import hashlib
    
    # 生成两部分：selector（查询用）和 validator（验证用）
    selector = secrets.token_urlsafe(12)
    validator = secrets.token_urlsafe(32)
    
    # 存储哈希后的 validator
    validator_hash = hashlib.sha256(validator.encode()).hexdigest()
    
    # 存储到数据库
    store_remember_me_token(
        selector=selector,
        validator_hash=validator_hash,
        user_id=user_id,
        expires=datetime.utcnow() + timedelta(days=30)
    )
    
    # 返回给客户端: selector:validator
    return f"{selector}:{validator}"

def verify_remember_me_token(token: str) -> Optional[str]:
    """验证记住我令牌"""
    try:
        selector, validator = token.split(':')
        
        # 查询数据库
        stored = get_remember_me_token(selector)
        if not stored or stored.expires < datetime.utcnow():
            return None
        
        # 验证 validator
        validator_hash = hashlib.sha256(validator.encode()).hexdigest()
        if not hmac.compare_digest(stored.validator_hash, validator_hash):
            # 可能被盗用，删除所有该用户的记住我令牌
            delete_all_user_remember_me_tokens(stored.user_id)
            return None
        
        # 使用后轮换（防止重放）
        rotate_remember_me_token(selector)
        
        return stored.user_id
    except ValueError:
        return None
```

**关键点:**
- 使用双令牌（selector + validator）机制
- 服务端存储 validator 的哈希
- 验证成功后轮换令牌
- 检测到异常立即失效所有令牌
- 设置合理的过期时间（如 30 天）

---

## 相关概念

### 数据结构
- [哈希表](../computer-science/data-structures/hash-table.md)：会话存储和查找
- [缓存](../computer-science/systems/cache.md)：分布式会话缓存

### 算法
- [加密算法](../cryptography/symmetric-encryption.md)：会话加密
- [哈希算法](../cryptography/hash-functions.md)：会话 ID 哈希

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)：会话验证性能
- [空间复杂度](../references/space-complexity.md)：会话存储空间

### 系统实现
- [身份认证](./authentication.md)：会话的前提
- [授权](./authorization.md)：会话中的权限
- [Web 安全](./web-security.md)：Cookie 安全
- [输入验证](./input-validation.md)：会话 ID 验证

### 安全领域
- [CSRF 防护](../application-security/csrf.md)：SameSite Cookie
- [XSS 防护](../application-security/input-validation.md)：HttpOnly Cookie
- [安全编码](./secure-coding.md)：安全会话实践

---

## 参考资料

1. [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
2. [RFC 6265 - HTTP State Management Mechanism](https://tools.ietf.org/html/rfc6265)
3. [SameSite Cookie Explained](https://web.dev/samesite-cookies-explained/)
4. [OWASP Testing for Session Management](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/README)
