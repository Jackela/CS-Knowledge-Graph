# 身份认证 (Authentication)

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**身份认证 (Authentication)** 是验证用户或实体身份的过程，确保系统知道"你是谁"。它是信息安全的基石，是授权和访问控制的前提。现代身份认证体系包括从传统的密码认证到现代的 OAuth、JWT 和 SSO 等多种机制。

```
┌─────────────────────────────────────────────────────────────────┐
│                   身份认证体系架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │   凭证层     │───▶│   验证层     │───▶│   会话层     │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│          │                  │                  │               │
│          ▼                  ▼                  ▼               │
│   • 密码/OTP          • 本地验证          • Session            │
│   • 生物特征          • LDAP/AD           • JWT Token          │
│   • 硬件密钥          • OAuth/OpenID      • Refresh Token      │
│   • 数字证书          • 多因素(MFA)       • SSO Ticket         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心概念

### 认证三要素

身份认证基于三个核心要素，安全性随要素数量增加而增强：

```
┌─────────────────────────────────────────────────────────────────┐
│                   身份认证三要素                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│   │ 所知      │  │ 所有      │  │ 所是      │                     │
│   │Something │  │Something │  │Something │                     │
│   │you know  │  │you have  │  │you are   │                     │
│   └──────────┘  └──────────┘  └──────────┘                     │
│                                                                 │
│   • 密码            • 手机/令牌        • 指纹                    │
│   • PIN码           • 智能卡           • 面部识别                │
│   • 安全问题        • 安全密钥         • 虹膜/声纹               │
│                                                                 │
│   单因素(1FA) ◄── 双因素(2FA) ◄── 多因素(MFA)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 认证机制对比

| 机制 | 安全性 | 用户体验 | 适用场景 | 实现复杂度 |
|------|--------|----------|----------|------------|
| 密码认证 | 中 | 高 | 通用场景 | 低 |
| JWT Token | 中 | 高 | 分布式系统 | 中 |
| Session + Cookie | 中 | 高 | 传统Web应用 | 低 |
| OAuth 2.0 | 高 | 高 | 第三方授权 | 高 |
| SSO (SAML/OIDC) | 高 | 极高 | 企业应用 | 高 |
| MFA/2FA | 高 | 中 | 高安全场景 | 中 |
| WebAuthn/FIDO2 | 极高 | 高 | 防钓鱼场景 | 中 |

---

## 实现方式

### 1. JWT (JSON Web Token)

JWT 是现代分布式系统中广泛使用的无状态认证机制：

```python
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class JWTAuthManager:
    """JWT 认证管理器"""
    
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.refresh_secret = secrets.token_urlsafe(32)  # 独立的refresh密钥
    
    def generate_tokens(self, user_id: str, claims: Dict = None,
                       access_expiry: int = 15,  # 15分钟
                       refresh_expiry: int = 7 * 24 * 60) -> Tuple[str, str]:
        """生成访问令牌和刷新令牌"""
        
        now = datetime.utcnow()
        
        # Access Token - 短期有效，包含用户 claims
        access_payload = {
            'sub': user_id,  # subject (用户标识)
            'iat': now,      # issued at
            'type': 'access',
            'jti': secrets.token_urlsafe(16),  # JWT ID，用于撤销
            'exp': now + timedelta(minutes=access_expiry)
        }
        if claims:
            access_payload.update(claims)
        
        access_token = jwt.encode(
            access_payload, 
            self.secret_key, 
            algorithm=self.algorithm
        )
        
        # Refresh Token - 长期有效，仅用于获取新访问令牌
        refresh_payload = {
            'sub': user_id,
            'iat': now,
            'type': 'refresh',
            'jti': secrets.token_urlsafe(16),
            'exp': now + timedelta(minutes=refresh_expiry),
            'token_family': secrets.token_urlsafe(8)  # 令牌家族，检测重放
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            self.refresh_secret,
            algorithm=self.algorithm
        )
        
        return access_token, refresh_token
    
    def verify_access_token(self, token: str) -> Optional[Dict]:
        """验证访问令牌"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # 验证类型
            if payload.get('type') != 'access':
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            return None  # 过期
        except jwt.InvalidTokenError:
            return None  # 无效
    
    def refresh_access_token(self, refresh_token: str,
                            revoked_tokens: set = None) -> Optional[Tuple[str, str]]:
        """使用刷新令牌获取新的访问令牌"""
        try:
            payload = jwt.decode(
                refresh_token,
                self.refresh_secret,
                algorithms=[self.algorithm]
            )
            
            if payload.get('type') != 'refresh':
                return None
            
            # 检查是否已被撤销
            if revoked_tokens and payload.get('jti') in revoked_tokens:
                return None
            
            # 生成新令牌对
            user_id = payload['sub']
            return self.generate_tokens(user_id)
            
        except jwt.InvalidTokenError:
            return None


# 使用示例
auth_manager = JWTAuthManager(secret_key="your-256-bit-secret")

# 登录时生成令牌
access_token, refresh_token = auth_manager.generate_tokens(
    user_id="user_123",
    claims={"role": "admin", "permissions": ["read", "write"]}
)

# API 请求时验证
decoded = auth_manager.verify_access_token(access_token)
if decoded:
    print(f"用户 {decoded['sub']} 已认证，角色: {decoded.get('role')}")
```

### 2. OAuth 2.0 / OpenID Connect

OAuth 2.0 是业界标准的授权协议，OpenID Connect (OIDC) 在其之上构建身份认证层：

```python
from dataclasses import dataclass
from typing import Optional, List
import secrets
import hashlib
import base64

@dataclass
class OAuth2Client:
    """OAuth 2.0 客户端配置"""
    client_id: str
    client_secret: str
    redirect_uris: List[str]
    allowed_scopes: List[str] = None
    grant_types: List[str] = None
    
    def __post_init__(self):
        if self.allowed_scopes is None:
            self.allowed_scopes = ['openid', 'profile', 'email']
        if self.grant_types is None:
            self.grant_types = ['authorization_code', 'refresh_token']


class OAuth2AuthorizationServer:
    """OAuth 2.0 授权服务器实现"""
    
    def __init__(self):
        self.clients: Dict[str, OAuth2Client] = {}
        self.auth_codes: Dict[str, Dict] = {}  # 授权码存储
        self.access_tokens: Dict[str, Dict] = {}  # 访问令牌存储
    
    def register_client(self, client: OAuth2Client):
        """注册客户端应用"""
        self.clients[client.client_id] = client
    
    def create_authorization_code(self, client_id: str, user_id: str,
                                   redirect_uri: str, scope: str,
                                   code_challenge: str = None,
                                   code_challenge_method: str = 'S256') -> str:
        """
        创建授权码 (Authorization Code Flow with PKCE)
        PKCE (Proof Key for Code Exchange) 防止授权码拦截攻击
        """
        if client_id not in self.clients:
            raise ValueError("Invalid client_id")
        
        client = self.clients[client_id]
        if redirect_uri not in client.redirect_uris:
            raise ValueError("Invalid redirect_uri")
        
        # 生成随机授权码
        auth_code = secrets.token_urlsafe(32)
        
        self.auth_codes[auth_code] = {
            'client_id': client_id,
            'user_id': user_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'code_challenge': code_challenge,
            'expires_at': datetime.utcnow() + timedelta(minutes=10),
            'used': False
        }
        
        return auth_code
    
    def exchange_code_for_token(self, auth_code: str, client_id: str,
                                 client_secret: str, redirect_uri: str,
                                 code_verifier: str = None) -> Dict:
        """用授权码交换访问令牌"""
        
        # 验证客户端凭证
        client = self.clients.get(client_id)
        if not client or client.client_secret != client_secret:
            raise ValueError("Invalid client credentials")
        
        # 验证授权码
        code_data = self.auth_codes.get(auth_code)
        if not code_data:
            raise ValueError("Invalid authorization code")
        
        if code_data['used']:
            raise ValueError("Authorization code already used")
        
        if code_data['expires_at'] < datetime.utcnow():
            raise ValueError("Authorization code expired")
        
        if code_data['redirect_uri'] != redirect_uri:
            raise ValueError("Redirect URI mismatch")
        
        # PKCE 验证
        if code_data.get('code_challenge') and code_verifier:
            challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            ).decode().rstrip('=')
            
            if challenge != code_data['code_challenge']:
                raise ValueError("Invalid code_verifier")
        
        # 标记授权码已使用
        code_data['used'] = True
        
        # 生成令牌
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        
        self.access_tokens[access_token] = {
            'user_id': code_data['user_id'],
            'client_id': client_id,
            'scope': code_data['scope'],
            'expires_at': datetime.utcnow() + timedelta(hours=1)
        }
        
        # 构建 OIDC ID Token (JWT)
        id_token_payload = {
            'iss': 'https://auth.example.com',  # 签发者
            'sub': code_data['user_id'],         # 用户唯一标识
            'aud': client_id,                    # 受众
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iat': datetime.utcnow(),
            'auth_time': datetime.utcnow().timestamp(),
        }
        
        # 根据 scope 添加 claims
        if 'email' in code_data['scope']:
            id_token_payload['email'] = f"{code_data['user_id']}@example.com"
            id_token_payload['email_verified'] = True
        
        if 'profile' in code_data['scope']:
            id_token_payload['name'] = f"User {code_data['user_id']}"
        
        id_token = jwt.encode(id_token_payload, 'secret', algorithm='HS256')
        
        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': refresh_token,
            'id_token': id_token,  # OIDC 特有
            'scope': code_data['scope']
        }
```

### 3. SSO (Single Sign-On) 单点登录

SSO 允许用户使用一组凭证访问多个相关但独立的系统：

```python
class SSOManager:
    """SSO 单点登录管理器"""
    
    def __init__(self):
        self.service_providers: Dict[str, Dict] = {}  # 服务提供商
        self.tickets: Dict[str, Dict] = {}  # CAS 风格票据
        self.sessions: Dict[str, Dict] = {}  # 全局会话
    
    def register_service_provider(self, sp_id: str, sp_name: str,
                                   sp_url: str, saml_metadata: str = None):
        """注册服务提供商"""
        self.service_providers[sp_id] = {
            'name': sp_name,
            'url': sp_url,
            'saml_metadata': saml_metadata,
            'registered_at': datetime.utcnow()
        }
    
    def create_global_session(self, user_id: str, auth_method: str) -> str:
        """创建全局 SSO 会话"""
        session_id = secrets.token_urlsafe(32)
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'auth_method': auth_method,
            'created_at': datetime.utcnow(),
            'last_active': datetime.utcnow(),
            'service_tickets': set()  # 已访问的服务
        }
        
        return session_id
    
    def issue_service_ticket(self, session_id: str, 
                             service_id: str) -> Optional[str]:
        """签发服务票据 (CAS 协议风格)"""
        
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # 检查会话有效性
        if self._is_session_expired(session):
            return None
        
        # 生成服务票据
        ticket = f"ST-{secrets.token_urlsafe(32)}"
        
        self.tickets[ticket] = {
            'session_id': session_id,
            'user_id': session['user_id'],
            'service_id': service_id,
            'created_at': datetime.utcnow(),
            'used': False,
            'expires_at': datetime.utcnow() + timedelta(minutes=5)
        }
        
        session['service_tickets'].add(ticket)
        
        return ticket
    
    def validate_service_ticket(self, ticket: str, service_id: str) -> Optional[Dict]:
        """验证服务票据"""
        
        if ticket not in self.tickets:
            return None
        
        ticket_data = self.tickets[ticket]
        
        # 验证条件
        if ticket_data['used']:
            return None  # 已使用
        
        if ticket_data['expires_at'] < datetime.utcnow():
            return None  # 已过期
        
        if ticket_data['service_id'] != service_id:
            return None  # 服务不匹配
        
        # 标记为已使用（一次性票据）
        ticket_data['used'] = True
        
        # 更新会话活动
        session = self.sessions.get(ticket_data['session_id'])
        if session:
            session['last_active'] = datetime.utcnow()
        
        return {
            'user_id': ticket_data['user_id'],
            'authenticated': True,
            'auth_method': session.get('auth_method') if session else None
        }
    
    def _is_session_expired(self, session: Dict, max_idle: int = 3600) -> bool:
        """检查会话是否过期（基于空闲时间）"""
        idle_time = (datetime.utcnow() - session['last_active']).total_seconds()
        return idle_time > max_idle
    
    def logout_global_session(self, session_id: str) -> List[str]:
        """全局登出 - 通知所有已访问服务"""
        
        if session_id not in self.sessions:
            return []
        
        session = self.sessions[session_id]
        affected_services = []
        
        # 收集需要通知的服务
        for ticket_id in session['service_tickets']:
            if ticket_id in self.tickets:
                service_id = self.tickets[ticket_id]['service_id']
                if service_id in self.service_providers:
                    affected_services.append({
                        'service_id': service_id,
                        'logout_url': f"{self.service_providers[service_id]['url']}/logout"
                    })
                del self.tickets[ticket_id]
        
        # 删除全局会话
        del self.sessions[session_id]
        
        return affected_services


# SAML Assertion 生成示例
class SAMLIdentityProvider:
    """SAML 2.0 IdP 简化实现"""
    
    def create_saml_assertion(self, user_id: str, 
                             service_provider_entity_id: str,
                             attributes: Dict = None) -> str:
        """创建 SAML Assertion (XML)"""
        
        import xml.etree.ElementTree as ET
        
        # SAML命名空间
        NS = {
            'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
            'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol'
        }
        
        issue_instant = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        assertion_id = f"_{secrets.token_hex(16)}"
        
        # 构建 SAML Assertion XML
        assertion = f'''<?xml version="1.0" encoding="UTF-8"?>
<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                ID="{assertion_id}"
                IssueInstant="{issue_instant}"
                Version="2.0">
    <saml:Issuer>https://idp.example.com</saml:Issuer>
    <saml:Subject>
        <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">
            {user_id}@example.com
        </saml:NameID>
        <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
            <saml:SubjectConfirmationData
                NotOnOrAfter="{(datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')}"
                Recipient="{service_provider_entity_id}"/>
        </saml:SubjectConfirmation>
    </saml:Subject>
    <saml:Conditions NotBefore="{issue_instant}"
                     NotOnOrAfter="{(datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')}">
        <saml:AudienceRestriction>
            <saml:Audience>{service_provider_entity_id}</saml:Audience>
        </saml:AudienceRestriction>
    </saml:Conditions>
    <saml:AuthnStatement AuthnInstant="{issue_instant}">
        <saml:AuthnContext>
            <saml:AuthnContextClassRef>
                urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport
            </saml:AuthnContextClassRef>
        </saml:AuthnContext>
    </saml:AuthnStatement>
    <saml:AttributeStatement>
        <saml:Attribute Name="user_id">
            <saml:AttributeValue xsi:type="xs:string">{user_id}</saml:AttributeValue>
        </saml:Attribute>
        {self._build_attributes(attributes)}
    </saml:AttributeStatement>
</saml:Assertion>'''
        
        return assertion
    
    def _build_attributes(self, attributes: Dict) -> str:
        """构建 SAML 属性节点"""
        if not attributes:
            return ""
        
        attr_xml = ""
        for name, value in attributes.items():
            attr_xml += f'''
        <saml:Attribute Name="{name}">
            <saml:AttributeValue xsi:type="xs:string">{value}</saml:AttributeValue>
        </saml:Attribute>'''
        return attr_xml
```

### 4. WebAuthn / FIDO2

WebAuthn 是现代防钓鱼的强认证标准：

```python
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.exceptions import InvalidSignature

class WebAuthnServer:
    """WebAuthn (FIDO2) 服务器实现"""
    
    def __init__(self, rp_id: str, rp_name: str, origin: str):
        """
        RP = Relying Party (依赖方，即服务提供方)
        rp_id: 依赖方标识 (e.g., "example.com")
        rp_name: 显示名称
        origin: 允许的源 (e.g., "https://example.com")
        """
        self.rp_id = rp_id
        self.rp_name = rp_name
        self.origin = origin
        self.credentials: Dict[str, Dict] = {}  # 存储用户凭证
        self.challenges: Dict[str, Dict] = {}  # 临时挑战
    
    def generate_registration_options(self, user_id: str, 
                                      user_name: str,
                                      user_display_name: str) -> Dict:
        """生成注册选项"""
        
        challenge = secrets.token_bytes(32)
        challenge_b64 = base64.urlsafe_b64encode(challenge).rstrip(b'=').decode()
        
        # 存储挑战，用于后续验证
        self.challenges[challenge_b64] = {
            'type': 'registration',
            'user_id': user_id,
            'expires': datetime.utcnow() + timedelta(minutes=5)
        }
        
        return {
            'publicKey': {
                'challenge': challenge_b64,
                'rp': {
                    'name': self.rp_name,
                    'id': self.rp_id
                },
                'user': {
                    'id': base64.urlsafe_b64encode(user_id.encode()).rstrip(b'=').decode(),
                    'name': user_name,
                    'displayName': user_display_name
                },
                'pubKeyCredParams': [
                    {'type': 'public-key', 'alg': -7},   # ES256
                    {'type': 'public-key', 'alg': -257}  # RS256
                ],
                'authenticatorSelection': {
                    'authenticatorAttachment': 'platform',  # 或 'cross-platform'
                    'userVerification': 'preferred',
                    'residentKey': 'preferred'
                },
                'attestation': 'direct',  # 请求认证器证明
                'timeout': 60000
            }
        }
    
    def verify_registration(self, client_data_json: str,
                           attestation_object: str,
                           challenge: str) -> bool:
        """验证注册响应"""
        
        # 验证挑战有效性
        if challenge not in self.challenges:
            return False
        
        challenge_data = self.challenges[challenge]
        if challenge_data['type'] != 'registration':
            return False
        
        if challenge_data['expires'] < datetime.utcnow():
            return False
        
        # 解析 client data
        client_data = json.loads(base64.urlsafe_b64decode(
            client_data_json + '=='
        ))
        
        # 验证 origin
        if client_data.get('origin') != self.origin:
            return False
        
        # 验证 challenge
        received_challenge = base64.urlsafe_b64decode(
            client_data.get('challenge', '') + '=='
        )
        expected_challenge = base64.urlsafe_b64decode(challenge + '==')
        
        if received_challenge != expected_challenge:
            return False
        
        # 存储凭证（简化，实际需要解析 attestation_object）
        user_id = challenge_data['user_id']
        self.credentials[user_id] = {
            'registered_at': datetime.utcnow(),
            'client_data': client_data
        }
        
        # 清理挑战
        del self.challenges[challenge]
        
        return True
    
    def generate_authentication_options(self, user_id: str) -> Dict:
        """生成认证选项"""
        
        challenge = secrets.token_bytes(32)
        challenge_b64 = base64.urlsafe_b64encode(challenge).rstrip(b'=').decode()
        
        self.challenges[challenge_b64] = {
            'type': 'authentication',
            'user_id': user_id,
            'expires': datetime.utcnow() + timedelta(minutes=5)
        }
        
        return {
            'publicKey': {
                'challenge': challenge_b64,
                'rpId': self.rp_id,
                'allowCredentials': [
                    {
                        'type': 'public-key',
                        'id': self._get_credential_id(user_id)
                    }
                ],
                'userVerification': 'preferred',
                'timeout': 60000
            }
        }
    
    def _get_credential_id(self, user_id: str) -> str:
        """获取用户的凭证 ID"""
        # 简化实现
        return base64.urlsafe_b64encode(
            f"credential_{user_id}".encode()
        ).rstrip(b'=').decode()
```

---

## 应用场景

### 场景 1: 微服务架构认证

```
┌─────────────────────────────────────────────────────────────────┐
│                   微服务认证架构                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Client          API Gateway           Auth Service           │
│     │                 │                       │                │
│     │  1. Login       │                       │                │
│     │────────────────▶│                       │                │
│     │                 │  2. Validate          │                │
│     │                 │──────────────────────▶│                │
│     │                 │                       │                │
│     │                 │  3. JWT Token         │                │
│     │                 │◀──────────────────────│                │
│     │                 │                       │                │
│     │  4. Token       │                       │                │
│     │◀────────────────│                       │                │
│     │                 │                       │                │
│     │  5. API + Token │                       │                │
│     │────────────────▶│                       │                │
│     │                 │  6. Verify Token      │                │
│     │                 │──────────────────────▶│                │
│     │                 │                       │                │
│     │                 │  7. Valid             │                │
│     │                 │◀──────────────────────│                │
│     │                 │                       │                │
│     │                 │────── 8. Route ──────▶│  Service A     │
│     │                 │                       │                │
│     │                 │◀───── 9. Response ────│                │
│     │                 │                       │                │
│     │  10. Result     │                       │                │
│     │◀────────────────│                       │                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 场景 2: 企业 SSO 集成

```
┌─────────────────────────────────────────────────────────────────┐
│                   企业 SSO 架构                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   用户                                                           │
│     │                                                           │
│     ▼                                                           │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐      │
│   │   邮箱系统   │     │   CRM系统   │     │   财务系统   │      │
│   │  (Service)  │     │  (Service)  │     │  (Service)  │      │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘      │
│          │                   │                   │              │
│          └───────────────────┼───────────────────┘              │
│                              │                                 │
│                              ▼                                 │
│                    ┌─────────────────┐                         │
│                    │  Identity Provider │                       │
│                    │  (IdP/SSO Server) │                       │
│                    │                 │                         │
│                    │  • Azure AD     │                         │
│                    │  • Okta         │                         │
│                    │  • Keycloak     │                         │
│                    │  • Auth0        │                         │
│                    └─────────────────┘                         │
│                              │                                 │
│                              ▼                                 │
│                    ┌─────────────────┐                         │
│                    │  LDAP / AD      │                         │
│                    │  用户目录        │                         │
│                    └─────────────────┘                         │
│                                                                 │
│   登录一次，访问所有系统                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

### Q1: JWT 和 Session 的区别？各自的优缺点？

**A:**

| 特性 | Session | JWT |
|------|---------|-----|
| 存储位置 | 服务器端 | 客户端 |
| 状态 | 有状态 | 无状态 |
| 可扩展性 | 需要共享存储 (Redis) | 天然分布式友好 |
| 撤销难度 | 易（服务器删除即可） | 难（需要黑名单或短过期时间） |
| 跨域支持 | 需配合 CORS | 天然支持 |
| 令牌大小 | 小 (Session ID) | 较大（包含用户信息） |
| 性能 | 需查询存储 | 验证签名即可 |

**适用场景:**
- Session: 单体应用、需要频繁撤销会话、存储大量会话数据
- JWT: 微服务架构、移动端 API、需要跨域访问

### Q2: OAuth 2.0 的授权码模式为什么最安全？

**A:**

授权码模式的安全性来自以下设计：

1. **分离用户凭证和访问令牌**：用户凭证只在授权服务器输入，不经过客户端应用
2. **授权码一次性使用**：防止重放攻击
3. **服务端交换**：授权码换令牌的过程需要 client_secret，只在服务端完成
4. **PKCE 扩展**：移动端必须使用 PKCE，防止授权码被拦截

```
流程对比:

隐式授权 (不安全):
用户 ──▶ 授权服务器 ──▶ 返回 Token (URL hash) ──▶ 可能被泄露

授权码模式 (安全):
用户 ──▶ 授权服务器 ──▶ 返回 Code ──▶ 服务端换 Token ──▶ 安全存储
```

### Q3: SSO 单点登录的实现原理？

**A:**

SSO 的核心是共享的认证状态和票据传递机制：

1. **首次访问**：用户访问应用 A → 重定向到 IdP → 登录 → 创建全局会话 → 返回票据给 A → 创建局部会话
2. **访问应用 B**：用户访问应用 B → 重定向到 IdP → IdP 检测到全局会话有效 → 直接返回票据给 B → 免密登录
3. **票据验证**：各应用向 IdP 验证票据，获取用户身份信息

常见协议:
- **SAML**: 企业级，XML-based，功能丰富
- **OIDC**: 现代标准，基于 OAuth 2.0，JSON-based
- **CAS**: 简单票据协议， academia 常用

### Q4: 如何防范身份认证中的常见攻击？

**A:**

| 攻击类型 | 防范措施 |
|----------|----------|
| 暴力破解 | 速率限制、账户锁定、CAPTCHA |
| 凭证填充 | 密码黑名单、异常登录检测、2FA |
| 会话劫持 | HttpOnly/Secure Cookie、短过期时间、绑定 IP/设备 |
| 中间人攻击 | HTTPS 强制、HSTS、证书固定 |
| 重放攻击 | 使用 nonce、时间戳、一次性令牌 |
| 钓鱼攻击 | WebAuthn/FIDO2（防钓鱼）、用户教育 |
| JWT 窃取 | 短过期时间、Refresh Token 轮换、敏感操作二次验证 |

### Q5: OAuth 2.0 和 OpenID Connect 的区别？

**A:**

| 特性 | OAuth 2.0 | OpenID Connect |
|------|-----------|----------------|
| 定位 | 授权框架 | 认证层（建立在 OAuth 2.0 之上） |
| 解决问题 | "允许应用 X 访问我的资源" | "允许应用 X 知道我是谁" |
| 关键输出 | Access Token | ID Token (JWT) + Access Token |
| 用户信息 | 需额外调用 API | ID Token 直接包含标准 claims |
| 规范 | RFC 6749 | OpenID Connect Core 1.0 |

**OIDC 在 OAuth 基础上的扩展:**
- 添加 `openid` scope
- 引入 ID Token（包含用户身份信息的 JWT）
- 标准化用户信息 claims（sub, name, email 等）
- 提供 UserInfo Endpoint 获取用户信息

---

## 相关概念

### 数据结构
- [哈希表](../computer-science/data-structures/hash-table.md)：密码哈希存储与查找
- [树](../computer-science/data-structures/tree.md)：证书链验证的树结构

### 算法
- [哈希算法](../cryptography/hash-functions.md)：密码存储与完整性验证
- [加密算法](../cryptography/symmetric-encryption.md)：会话安全与数据传输
- [数字签名](../cryptography/asymmetric-encryption.md)：身份验证与不可否认性

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)：认证验证的时间效率
- [空间复杂度](../references/space-complexity.md)：会话存储的空间评估

### 系统实现
- [授权](./authorization.md)：权限控制与访问管理
- [访问控制](./system-security/access-control.md)：认证后的权限管理
- [会话管理](./session-management.md)：用户会话生命周期管理
- [Web 安全](./web-security.md)：Web 应用安全基础

### 安全领域
- [密码学基础](../cryptography-basics.md)：认证背后的密码学原理
- [网络安全](../network-security/tls-ssl.md)：传输层安全
- [应用安全](../common-vulnerabilities.md)：常见安全漏洞与防护
- [输入验证](./input-validation.md)：安全输入处理

---

## 参考资料

1. [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
2. [RFC 6749 - OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
3. [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
4. [Web Authentication API (WebAuthn)](https://www.w3.org/TR/webauthn/)
5. [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
6. NIST Digital Identity Guidelines (SP 800-63)
