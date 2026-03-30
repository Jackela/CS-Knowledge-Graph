# 授权 (Authorization)

## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、NIST标准及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概述

**授权 (Authorization)** 是在身份认证之后，决定"你能做什么"的过程。如果说认证是验证"你是谁"，那么授权就是确定"你能访问什么资源、执行什么操作"。授权是访问控制的核心机制，确保用户只能访问其被允许的资源。

```
┌─────────────────────────────────────────────────────────────────┐
│                   认证 vs 授权                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   用户 ───▶ 认证 (Authentication)                               │
│   "你是谁？"                                                    │
│      │                                                          │
│      │ 验证身份                                                 │
│      ▼                                                          │
│   身份凭证 (Token/Session)                                      │
│      │                                                          │
│      ▼                                                          │
│   授权 (Authorization)                                          │
│   "你能做什么？"                                                │
│      │                                                          │
│      │ 检查权限                                                 │
│      ▼                                                          │
│   允许/拒绝访问                                                 │
│                                                                 │
│   比喻：                                                        │
│   • 认证 = 出示身份证进入大楼                                   │
│   • 授权 = 门禁卡决定能进入哪些楼层                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 访问控制模型

### 1. DAC (Discretionary Access Control) - 自主访问控制

**DAC** 允许资源的所有者自主决定谁可以访问其资源。这是最灵活的访问控制模型。

```
┌─────────────────────────────────────────────────────────────────┐
│                   DAC 模型 - Unix文件权限示例                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   文件所有者决定访问权限：                                      │
│                                                                 │
│   ┌─────────────┐                                               │
│   │  document   │  ← 文件所有者：Alice                          │
│   │  .txt       │                                               │
│   └─────────────┘                                               │
│         │                                                       │
│         │ 权限设置：-rw-r--r--                                  │
│         │                                                       │
│    ┌────┴────┬────────┬────────┐                               │
│    ▼         ▼        ▼        ▼                               │
│  所有者    用户组    其他用户                                    │
│  rw-       r--       r--                                       │
│  读+写     只读      只读                                       │
│                                                                 │
│   特点：                                                        │
│   ✓ 灵活性高，所有者自主控制                                    │
│   ✗ 安全性相对较低（权限可能过度授权）                          │
│   ✗ 难以审计和统一管理                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Python实现示例**：

```python
class DACResource:
    """DAC资源模型"""
    def __init__(self, owner_id, resource_id):
        self.owner_id = owner_id
        self.resource_id = resource_id
        # 权限表: {user_id: permissions}
        self.acl = {
            owner_id: ['read', 'write', 'delete', 'grant']
        }
    
    def grant_permission(self, granter_id, grantee_id, permissions):
        """授权 - 只有所有者可授权"""
        if granter_id != self.owner_id:
            raise PermissionError("Only owner can grant permissions")
        
        self.acl[grantee_id] = permissions
    
    def revoke_permission(self, revoker_id, grantee_id):
        """撤销权限"""
        if revoker_id != self.owner_id:
            raise PermissionError("Only owner can revoke permissions")
        
        if grantee_id in self.acl:
            del self.acl[grantee_id]
    
    def check_permission(self, user_id, action):
        """检查权限"""
        user_perms = self.acl.get(user_id, [])
        return action in user_perms

# 使用
resource = DACResource(owner_id="alice", resource_id="doc1")
resource.grant_permission("alice", "bob", ["read"])
resource.grant_permission("alice", "carol", ["read", "write"])

print(resource.check_permission("bob", "read"))      # True
print(resource.check_permission("bob", "write"))     # False
```

---

### 2. MAC (Mandatory Access Control) - 强制访问控制

**MAC** 由系统强制实施访问控制策略，用户不能改变。常用于高安全要求的环境（军事、政府）。

```
┌─────────────────────────────────────────────────────────────────┐
│                   MAC 模型 - Bell-LaPadula                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   安全级别 (Security Levels):                                   │
│                                                                 │
│   Top Secret (绝密)      ╱╲                                     │
│   Secret (机密)         ╱  ╲    向上读 (Read Up) - 禁止         │
│   Confidential (秘密)  ╱    ╲   向下写 (Write Down) - 禁止      │
│   Unclassified (公开) ╱______╲                                  │
│                                                                 │
│   Bell-LaPadula 规则：                                          │
│   • 简单安全规则：主体只能读同级或低级客体 (No Read Up)         │
│   • *-属性规则：主体只能写同级或高级客体 (No Write Down)        │
│                                                                 │
│   目的：防止信息从高安全级别流向低安全级别                      │
│                                                                 │
│   示例：                                                        │
│   Secret级别的用户可以：                                        │
│   ✓ 读取 Confidential、Unclassified 文档                      │
│   ✓ 写入 Secret、Top Secret 文档                              │
│   ✗ 读取 Top Secret 文档                                      │
│   ✗ 写入 Unclassified 文档                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3. RBAC (Role-Based Access Control) - 基于角色的访问控制

**RBAC** 是目前最常用的访问控制模型。用户通过角色获得权限，角色是权限的集合。

```
┌─────────────────────────────────────────────────────────────────┐
│                   RBAC 模型                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   User ──────▶ Role ──────▶ Permission                         │
│   用户          角色           权限                              │
│                                                                 │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐                │
│   │  Alice  │─────▶│  Admin  │─────▶│  create │                │
│   │  Bob    │─────▶│  Editor │─────▶│  read   │                │
│   │  Carol  │─────▶│  Viewer │─────▶│  update │                │
│   └─────────┘      └─────────┘      │  delete │                │
│                                     └─────────┘                │
│                                                                 │
│   角色层次 (Role Hierarchy):                                    │
│                                                                 │
│         Admin (所有权限)                                        │
│           │                                                     │
│      Editor (读写权限)                                          │
│           │                                                     │
│      Viewer (只读权限)                                          │
│                                                                 │
│   NIST RBAC 标准级别：                                          │
│   • Core RBAC - 基本RBAC                                        │
│   • Hierarchical RBAC - 支持角色层次                            │
│   • Constrained RBAC - 支持职责分离 (SSD/DSD)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**RBAC Python实现**：

```python
from enum import Enum, auto
from typing import Set, Dict, List
from dataclasses import dataclass, field

class Permission(Enum):
    """权限枚举"""
    CREATE = auto()
    READ = auto()
    UPDATE = auto()
    DELETE = auto()
    ADMIN = auto()

@dataclass
class Role:
    """角色"""
    name: str
    permissions: Set[Permission] = field(default_factory=set)
    parent_roles: List['Role'] = field(default_factory=list)
    
    def get_all_permissions(self) -> Set[Permission]:
        """获取所有权限（包含继承的）"""
        all_perms = set(self.permissions)
        for parent in self.parent_roles:
            all_perms.update(parent.get_all_permissions())
        return all_perms

@dataclass
class User:
    """用户"""
    user_id: str
    username: str
    roles: List[Role] = field(default_factory=list)
    
    def get_permissions(self) -> Set[Permission]:
        """获取用户的所有权限"""
        perms = set()
        for role in self.roles:
            perms.update(role.get_all_permissions())
        return perms
    
    def has_permission(self, permission: Permission) -> bool:
        """检查是否有某权限"""
        return permission in self.get_permissions()

# 定义角色层次
viewer = Role("Viewer", {Permission.READ})
editor = Role("Editor", {Permission.CREATE, Permission.UPDATE}, parent_roles=[viewer])
admin = Role("Admin", {Permission.DELETE, Permission.ADMIN}, parent_roles=[editor])

# 创建用户
alice = User("1", "Alice", [admin])
bob = User("2", "Bob", [editor])
carol = User("3", "Carol", [viewer])

# 权限检查
print(alice.has_permission(Permission.READ))    # True (继承)
print(alice.has_permission(Permission.DELETE))  # True
print(bob.has_permission(Permission.READ))      # True (继承)
print(bob.has_permission(Permission.DELETE))    # False
print(carol.has_permission(Permission.READ))    # True
print(carol.has_permission(Permission.CREATE))  # False
```

**RBAC with Decorators**：

```python
from functools import wraps

def require_permission(permission: Permission):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(user: User, *args, **kwargs):
            if not user.has_permission(permission):
                raise PermissionError(
                    f"User {user.username} lacks permission: {permission.name}"
                )
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

# 使用装饰器保护函数
class DocumentService:
    @staticmethod
    @require_permission(Permission.READ)
    def read_document(user: User, doc_id: str):
        return f"Document {doc_id} content"
    
    @staticmethod
    @require_permission(Permission.UPDATE)
    def update_document(user: User, doc_id: str, content: str):
        return f"Document {doc_id} updated"
    
    @staticmethod
    @require_permission(Permission.DELETE)
    def delete_document(user: User, doc_id: str):
        return f"Document {doc_id} deleted"

# 使用
try:
    DocumentService.read_document(alice, "doc1")    # ✓ 成功
    DocumentService.delete_document(bob, "doc1")    # ✗ 失败，抛出PermissionError
except PermissionError as e:
    print(e)
```

---

### 4. ABAC (Attribute-Based Access Control) - 基于属性的访问控制

**ABAC** 根据主体、资源、环境的属性动态决定访问权限，是最灵活的访问控制模型。

```
┌─────────────────────────────────────────────────────────────────┐
│                   ABAC 模型                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   策略评估：IF 条件 THEN 允许/拒绝                               │
│                                                                 │
│   条件可以包含：                                                │
│                                                                 │
│   主体属性 (Subject)        资源属性 (Resource)                 │
│   ├─ user.role = "manager"  ├─ resource.type = "document"       │
│   ├─ user.department = "IT" ├─ resource.classification = "internal"│
│   ├─ user.clearance = 3     ├─ resource.owner = "alice"         │
│   └─ user.location = "office"└─ resource.created_date           │
│                                                                 │
│   环境属性 (Environment)                                        │
│   ├─ time = "09:00-18:00"                                       │
│   ├─ day = "weekday"                                            │
│   ├─ location = "company_network"                               │
│   └─ threat_level = "low"                                       │
│                                                                 │
│   示例策略：                                                    │
│   "允许 IF user.department == resource.department               │
│        AND time.hour >= 9 AND time.hour <= 18                  │
│        AND user.level >= resource.confidentiality_level"       │
│                                                                 │
│   XACML (eXtensible Access Control Markup Language) 标准        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**ABAC Python实现**：

```python
from dataclasses import dataclass
from typing import Dict, Any, Callable
from datetime import datetime

@dataclass
class Subject:
    """主体"""
    user_id: str
    role: str
    department: str
    clearance_level: int
    attributes: Dict[str, Any]

@dataclass
class Resource:
    """资源"""
    resource_id: str
    resource_type: str
    owner: str
    department: str
    classification_level: int
    attributes: Dict[str, Any]

@dataclass
class Environment:
    """环境"""
    timestamp: datetime
    location: str
    device_type: str

# 策略规则
PolicyRule = Callable[[Subject, Resource, Environment], bool]

class ABACEngine:
    """ABAC决策引擎"""
    def __init__(self):
        self.policies: List[PolicyRule] = []
    
    def add_policy(self, policy: PolicyRule):
        self.policies.append(policy)
    
    def evaluate(self, subject: Subject, resource: Resource, 
                 env: Environment, action: str) -> bool:
        """评估访问请求"""
        for policy in self.policies:
            if not policy(subject, resource, env, action):
                return False
        return True

# 定义策略
def same_department_policy(subject, resource, env, action):
    """同部门访问策略"""
    return subject.department == resource.department

def business_hours_policy(subject, resource, env, action):
    """工作时间策略"""
    hour = env.timestamp.hour
    return 9 <= hour <= 18

def clearance_policy(subject, resource, env, action):
    """密级策略"""
    return subject.clearance_level >= resource.classification_level

def owner_override_policy(subject, resource, env, action):
    """所有者特权"""
    if subject.user_id == resource.owner:
        return True
    # 非所有者需要检查其他策略
    return None  # 继续检查

# 使用
engine = ABACEngine()
engine.add_policy(same_department_policy)
engine.add_policy(business_hours_policy)
engine.add_policy(clearance_policy)

subject = Subject("1", "engineer", "IT", 2, {})
resource = Resource("doc1", "document", "2", "IT", 1, {})
env = Environment(datetime.now(), "office", "desktop")

allowed = engine.evaluate(subject, resource, env, "read")
print(f"Access {'granted' if allowed else 'denied'}")
```

---

### 5. 访问控制模型对比

| 特性 | DAC | MAC | RBAC | ABAC |
|------|-----|-----|------|------|
| 控制方式 | 自主 | 强制 | 基于角色 | 基于属性 |
| 灵活性 | 高 | 低 | 中 | 极高 |
| 管理复杂度 | 高 | 低 | 中 | 高 |
| 适用场景 | 一般企业 | 军事/政府 | 大多数应用 | 动态/复杂场景 |
| 可扩展性 | 差 | 差 | 好 | 极好 |
| 审计能力 | 弱 | 强 | 强 | 中 |

---

## OAuth 2.0授权框架

**OAuth 2.0** 是行业标准的授权协议，允许第三方应用获取用户资源的有限访问权限。

```
┌─────────────────────────────────────────────────────────────────┐
│                   OAuth 2.0 授权码模式                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐                                    ┌───────────┐  │
│   │  用户   │                                    │  授权服务器│  │
│   └────┬────┘                                    └─────┬─────┘  │
│        │                                               │        │
│        │ 1. 请求授权                                   │        │
│        │──────────────────────────────────────────────▶│        │
│        │                                               │        │
│        │ 2. 用户登录并授权                             │        │
│        │◀──────────────────────────────────────────────│        │
│        │                                               │        │
│        │ 3. 返回授权码 (Authorization Code)            │        │
│        │──────────────────────────────────────────────▶        │
│        │                                               │        │
│   ┌────┴────┐                                         │        │
│   │ 客户端  │ 4. 用授权码换取访问令牌                   │        │
│   │ 应用    │─────────────────────────────────────────▶│        │
│   └────┬────┘                                         │        │
│        │                                               │        │
│        │ 5. 返回访问令牌 (Access Token)                │        │
│        │◀──────────────────────────────────────────────│        │
│        │                                               │        │
│        │ 6. 使用访问令牌访问资源                       │        │
│        │─────────────────────▶┌───────────┐           │        │
│        │                      │ 资源服务器│           │        │
│        │◀─────────────────────└───────────┘           │        │
│                                                                 │
│   安全要点：                                                    │
│   • 授权码只能使用一次                                          │
│   • 授权码与客户端ID绑定                                        │
│   • 所有通信使用HTTPS                                           │
│   • Access Token有有效期                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**OAuth 2.0 Scope设计**：

```python
# 权限范围 (Scope) 定义
SCOPES = {
    # 只读权限
    'profile:read': '读取用户基本信息',
    'email:read': '读取用户邮箱',
    'documents:read': '读取文档',
    
    # 读写权限
    'profile:write': '修改用户信息',
    'documents:write': '创建和修改文档',
    
    # 管理权限
    'admin': '完全管理权限',
    'users:manage': '用户管理',
}

# Scope验证
def validate_scope(requested_scope: str, allowed_scopes: list) -> bool:
    """验证请求的scope是否在允许的范围内"""
    requested = set(requested_scope.split())
    allowed = set(allowed_scopes)
    return requested.issubset(allowed)

# 示例
allowed = ['profile:read', 'email:read', 'documents:read']
print(validate_scope('profile:read email:read', allowed))  # True
print(validate_scope('profile:read admin', allowed))       # False
```

---

## 权限设计最佳实践

### 最小权限原则 (Principle of Least Privilege)

```
✓ 只授予完成任务所需的最小权限集合
✗ 不要为了方便而授予过多权限

示例：
✓ 客服角色：订单:查看, 退款:处理
✗ 客服角色：订单:完全控制, 用户:管理, 系统:配置
```

### 职责分离 (Separation of Duties)

```python
# 静态职责分离 (SSD)
# 互斥角色不能同时授予同一用户
MUTUALLY_EXCLUSIVE_ROLES = [
    {'会计', '审计'},      # 不能既当会计又当审计
    {'采购员', '验收员'},  # 不能既采购又验收
]

def check_ssd_violation(user_roles: set) -> bool:
    for exclusive_set in MUTUALLY_EXCLUSIVE_ROLES:
        if len(user_roles & exclusive_set) > 1:
            return True
    return False

# 动态职责分离 (DSD)
# 同一用户在一次会话中不能激活互斥角色
```

---

## 最佳实践

```
□ 权限设计
  □ 使用RBAC作为基础，复杂场景用ABAC补充
  □ 角色设计符合业务职责，避免过度细分
  □ 定期审查和清理无用权限

□ 安全实施
  □ 默认拒绝 (Default Deny)
  □ 权限验证在服务器端执行
  □ 不信任客户端传来的权限信息
  □ 敏感操作需要额外确认

□ 审计和监控
  □ 记录所有授权决策
  □ 监控异常访问模式
  □ 定期权限审计报告

□ 用户体验
  □ 权限错误提示友好但不过度暴露信息
  □ 提供权限申请流程
```

---

## 面试要点

**Q1: RBAC和ABAC的区别？**
> RBAC基于静态角色，ABAC基于动态属性。RBAC更易管理但不够灵活；ABAC极灵活但复杂度高。实际中常结合使用：RBAC作为基础，ABAC处理复杂场景。

**Q2: 什么是OAuth 2.0？授权码模式的优势？**
> OAuth 2.0是授权框架，允许第三方应用有限访问用户资源。授权码模式的优势：Access Token不经过用户浏览器，减少泄露风险；支持刷新令牌；最安全的OAuth流程。

**Q3: 如何实现权限系统的可扩展性？**
> 1) 使用策略模式封装不同授权逻辑；2) 缓存权限决策；3) 异步权限计算；4) 分布式权限服务；5) 预计算角色-权限映射。

---

## 相关概念

- [身份认证](./authentication.md) - 授权的前置步骤
- [Web安全](./web-security.md) - 授权在安全体系中的位置
- [常见漏洞](./common-vulnerabilities.md) - 授权相关的安全漏洞

---

## 参考资料

1. NIST RBAC Standard (ANSI/INCITS 359-2004)
2. OAuth 2.0 RFC 6749
3. XACML (eXtensible Access Control Markup Language) Standard
4. OWASP Authorization Cheat Sheet
5. "Authorization in Software" by Dominick Baier
