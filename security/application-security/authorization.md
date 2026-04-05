# 授权 (Authorization)

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料、业界最佳实践及官方文档。引用内容均已标注来源。如有侵权请联系作者移除。
> 
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 简介

**授权 (Authorization)** 是确定"谁可以做什么"的安全机制。与身份认证（验证"你是谁"）不同，授权发生在认证之后，决定已认证用户能访问哪些资源、执行哪些操作。现代授权模型主要包括 RBAC（基于角色的访问控制）和 ABAC（基于属性的访问控制），二者从粗粒度到细粒度满足不同场景的安全需求。

```
┌─────────────────────────────────────────────────────────────────┐
│                   访问控制决策流程                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   用户请求                                                       │
│      │                                                          │
│      ▼                                                          │
│   ┌─────────────┐                                               │
│   │ 身份认证    │── No ──▶ 拒绝访问                             │
│   │ 验证身份   │                                               │
│   └──────┬──────┘                                               │
│          │ Yes                                                  │
│          ▼                                                      │
│   ┌─────────────┐     ┌───────────────────────────────┐        │
│   │  授权决策   │────▶│ Subject + Action + Resource   │        │
│   │             │     │ • 谁 (用户/角色/属性)         │        │
│   │  策略引擎   │     │ • 做什么 (操作:读/写/删)      │        │
│   │  评估策略   │     │ • 对谁 (资源:文档/数据/API)   │        │
│   └──────┬──────┘     └───────────────────────────────┘        │
│          │                                                      │
│     ┌────┴────┐                                                 │
│     ▼         ▼                                                 │
│   Permit    Deny                                                │
│     │         │                                                 │
│     ▼         ▼                                                 │
│  允许访问   拒绝访问                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心概念

### 授权模型演进

```
┌─────────────────────────────────────────────────────────────────┐
│                   授权模型演进路线                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ACL (访问控制列表)                                              │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ 资源直接关联用户列表                                  │       │
│  │ User1: Read, User2: Read+Write                       │       │
│  │ 缺点: 用户多时难以管理                                 │       │
│  └─────────────────────────────────────────────────────┘       │
│                              │                                  │
│                              ▼                                  │
│  RBAC (基于角色的访问控制)                                       │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ 用户 ←→ 角色 ←→ 权限 ←→ 资源                        │       │
│  │ User1 → Admin → [Read,Write,Delete] → 所有资源      │       │
│  │ 优点: 简化管理，适合组织架构                          │       │
│  └─────────────────────────────────────────────────────┘       │
│                              │                                  │
│                              ▼                                  │
│  ABAC (基于属性的访问控制)                                       │
│     │                                                           │
│     ▼                                                           │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ 策略基于属性动态评估                                  │       │
│  │ IF user.dept == 'Finance'                           │       │
│  │    AND time.hour BETWEEN 9 AND 18                   │       │
│  │    AND resource.classification == 'Internal'        │       │
│  │ THEN PERMIT                                         │       │
│  │ 优点: 细粒度、上下文感知、灵活                        │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 核心术语

| 术语 | 定义 | 示例 |
|------|------|------|
| **Subject** | 访问主体，请求访问的实体 | 用户、服务、进程 |
| **Resource** | 被访问的资源 | 文件、API、数据库记录 |
| **Action** | 对资源执行的操作 | 读、写、删除、执行 |
| **Permission** | 执行某项操作的许可 | user:read, document:write |
| **Role** | 一组权限的集合 | Admin, Editor, Viewer |
| **Policy** | 定义访问规则 | IF...THEN PERMIT/DENY |
| **Attribute** | 描述主体的特征 | 部门、职级、地理位置 |

---

## 实现方式

### 1. RBAC (Role-Based Access Control)

RBAC 是目前最广泛使用的授权模型，通过角色将用户与权限解耦：

```python
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional
from functools import wraps
import json

class Permission(Enum):
    """权限枚举"""
    # 用户管理
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    
    # 文档管理
    DOC_CREATE = "document:create"
    DOC_READ = "document:read"
    DOC_UPDATE = "document:update"
    DOC_DELETE = "document:delete"
    DOC_SHARE = "document:share"
    
    # 系统管理
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"
    SYSTEM_BACKUP = "system:backup"


@dataclass
class Role:
    """角色定义"""
    name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    parent_roles: Set[str] = field(default_factory=set)  # 角色继承
    
    def get_all_permissions(self, role_registry: Dict[str, 'Role']) -> Set[Permission]:
        """获取所有权限（包括继承的）"""
        all_perms = set(self.permissions)
        
        for parent_name in self.parent_roles:
            if parent_name in role_registry:
                parent = role_registry[parent_name]
                all_perms.update(parent.get_all_permissions(role_registry))
        
        return all_perms


@dataclass  
class User:
    """用户定义"""
    user_id: str
    username: str
    roles: Set[str] = field(default_factory=set)
    direct_permissions: Set[Permission] = field(default_factory=set)
    attributes: Dict = field(default_factory=dict)  # 用于 ABAC 扩展
    
    def has_permission(self, permission: Permission,
                      role_registry: Dict[str, Role]) -> bool:
        """检查用户是否有指定权限"""
        # 检查直接权限
        if permission in self.direct_permissions:
            return True
        
        # 检查角色权限
        for role_name in self.roles:
            if role_name in role_registry:
                role = role_registry[role_name]
                if permission in role.get_all_permissions(role_registry):
                    return True
        
        return False


class RBACManager:
    """RBAC 权限管理器"""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self.resource_permissions: Dict[str, Set[str]] = {}  # 资源级权限
    
    def create_role(self, name: str, description: str,
                   permissions: Set[Permission],
                   parent_roles: Set[str] = None) -> Role:
        """创建角色"""
        if parent_roles is None:
            parent_roles = set()
        
        # 检查父角色是否存在
        for parent in parent_roles:
            if parent not in self.roles:
                raise ValueError(f"Parent role '{parent}' does not exist")
        
        role = Role(
            name=name,
            description=description,
            permissions=permissions,
            parent_roles=parent_roles
        )
        self.roles[name] = role
        return role
    
    def assign_role_to_user(self, user_id: str, role_name: str):
        """为用户分配角色"""
        if user_id not in self.users:
            raise ValueError(f"User '{user_id}' does not exist")
        if role_name not in self.roles:
            raise ValueError(f"Role '{role_name}' does not exist")
        
        self.users[user_id].roles.add(role_name)
    
    def check_access(self, user_id: str, permission: Permission) -> bool:
        """检查用户是否有权限"""
        if user_id not in self.users:
            return False
        
        return self.users[user_id].has_permission(permission, self.roles)
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """获取用户的所有权限"""
        if user_id not in self.users:
            return set()
        
        user = self.users[user_id]
        all_perms = set(user.direct_permissions)
        
        for role_name in user.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                all_perms.update(role.get_all_permissions(self.roles))
        
        return all_perms


# 初始化 RBAC 系统
rbac = RBACManager()

# 定义角色层次结构
rbac.create_role(
    "Viewer",
    "只读用户",
    {Permission.DOC_READ, Permission.USER_READ}
)

rbac.create_role(
    "Editor", 
    "编辑者",
    {Permission.DOC_CREATE, Permission.DOC_UPDATE, Permission.DOC_SHARE},
    parent_roles={"Viewer"}  # 继承 Viewer 权限
)

rbac.create_role(
    "Admin",
    "管理员",
    {
        Permission.DOC_DELETE, Permission.USER_CREATE,
        Permission.USER_UPDATE, Permission.USER_DELETE,
        Permission.SYSTEM_CONFIG
    },
    parent_roles={"Editor"}  # 继承 Editor 权限
)

rbac.create_role(
    "SuperAdmin",
    "超级管理员",
    {Permission.SYSTEM_BACKUP, Permission.SYSTEM_LOGS}
)

# 创建用户
rbac.users["user1"] = User(user_id="user1", username="alice")
rbac.users["user2"] = User(user_id="user2", username="bob")  
rbac.users["user3"] = User(user_id="user3", username="charlie")

# 分配角色
rbac.assign_role_to_user("user1", "Viewer")
rbac.assign_role_to_user("user2", "Editor")
rbac.assign_role_to_user("user3", "Admin")

# 添加额外直接权限
rbac.users["user1"].direct_permissions.add(Permission.DOC_SHARE)


# 装饰器实现权限检查
def require_permission(permission: Permission):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(user_id: str, *args, **kwargs):
            if not rbac.check_access(user_id, permission):
                raise PermissionError(
                    f"User '{user_id}' does not have permission '{permission.value}'"
                )
            return func(user_id, *args, **kwargs)
        return wrapper
    return decorator


# API 端点使用示例
class DocumentAPI:
    
    @staticmethod
    @require_permission(Permission.DOC_READ)
    def get_document(user_id: str, doc_id: str) -> dict:
        """读取文档"""
        return {"doc_id": doc_id, "content": "Document content..."}
    
    @staticmethod
    @require_permission(Permission.DOC_CREATE)
    def create_document(user_id: str, title: str, content: str) -> dict:
        """创建文档"""
        return {"doc_id": "new_doc_123", "title": title}
    
    @staticmethod
    @require_permission(Permission.DOC_DELETE)
    def delete_document(user_id: str, doc_id: str) -> bool:
        """删除文档"""
        print(f"Document {doc_id} deleted by {user_id}")
        return True


# 使用示例
print("=== RBAC 权限检查 ===")
print(f"user1 (Viewer) 可读文档: {rbac.check_access('user1', Permission.DOC_READ)}")
print(f"user1 (Viewer) 可创建文档: {rbac.check_access('user1', Permission.DOC_CREATE)}")
print(f"user2 (Editor) 可创建文档: {rbac.check_access('user2', Permission.DOC_CREATE)}")
print(f"user3 (Admin) 可删除文档: {rbac.check_access('user3', Permission.DOC_DELETE)}")

# 角色权限继承示例
print(f"\nuser3 (Admin) 所有权限: ")
for perm in rbac.get_user_permissions("user3"):
    print(f"  - {perm.value}")
```

### 2. ABAC (Attribute-Based Access Control)

ABAC 使用属性动态评估访问策略，支持更细粒度的控制：

```python
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
import operator
import time
from datetime import datetime

class Effect(Enum):
    """策略效果"""
    PERMIT = "Permit"
    DENY = "Deny"
    NOT_APPLICABLE = "NotApplicable"


@dataclass
class AttributeValue:
    """属性值封装"""
    name: str
    value: Any
    
    def compare(self, op: str, target: Any) -> bool:
        """比较操作"""
        ops = {
            'eq': operator.eq,
            'ne': operator.ne,
            'gt': operator.gt,
            'ge': operator.ge,
            'lt': operator.lt,
            'le': operator.le,
            'in': lambda x, y: x in y,
            'contains': lambda x, y: y in x if isinstance(x, (list, str)) else False,
            'starts_with': lambda x, y: str(x).startswith(str(y)),
            'ends_with': lambda x, y: str(x).endswith(str(y)),
        }
        
        if op not in ops:
            raise ValueError(f"Unknown operator: {op}")
        
        return ops[op](self.value, target)


@dataclass
class Subject:
    """访问主体"""
    id: str
    attributes: Dict[str, Any]  # 用户属性
    roles: List[str] = None
    
    def __post_init__(self):
        if self.roles is None:
            self.roles = []


@dataclass
class Resource:
    """被访问资源"""
    id: str
    type: str
    attributes: Dict[str, Any]  # 资源属性
    owner: str = None


@dataclass
class Action:
    """操作"""
    type: str
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


@dataclass
class Environment:
    """环境上下文"""
    attributes: Dict[str, Any]
    
    @classmethod
    def current(cls) -> 'Environment':
        """创建当前环境"""
        now = datetime.now()
        return cls(attributes={
            'time': now,
            'hour': now.hour,
            'weekday': now.weekday(),
            'timestamp': time.time(),
            'ip_address': None,  # 需要外部注入
            'location': None,    # 需要外部注入
        })


class PolicyRule:
    """策略规则"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.target_conditions: List[Callable] = []
        self.condition: Callable = None
        self.effect: Effect = Effect.PERMIT
        self.obligations: List[Callable] = []  # 义务/建议
    
    def match_target(self, subject: Subject, resource: Resource,
                    action: Action, env: Environment) -> bool:
        """检查是否匹配目标"""
        for condition in self.target_conditions:
            if not condition(subject, resource, action, env):
                return False
        return True
    
    def evaluate(self, subject: Subject, resource: Resource,
                action: Action, env: Environment) -> Effect:
        """评估规则"""
        if not self.match_target(subject, resource, action, env):
            return Effect.NOT_APPLICABLE
        
        if self.condition is None:
            return self.effect
        
        try:
            result = self.condition(subject, resource, action, env)
            return self.effect if result else Effect.NOT_APPLICABLE
        except Exception:
            return Effect.NOT_APPLICABLE


class ABACPolicyEngine:
    """ABAC 策略引擎"""
    
    def __init__(self):
        self.policies: List[PolicyRule] = []
        self.combining_algorithm: str = "deny_overrides"  # 默认: 拒绝优先
    
    def add_policy(self, policy: PolicyRule):
        """添加策略"""
        self.policies.append(policy)
    
    def evaluate(self, subject: Subject, resource: Resource,
                action: Action, env: Environment = None) -> tuple:
        """
        评估访问请求
        返回: (decision, obligations)
        """
        if env is None:
            env = Environment.current()
        
        decisions = []
        applicable_obligations = []
        
        for policy in self.policies:
            effect = policy.evaluate(subject, resource, action, env)
            
            if effect != Effect.NOT_APPLICABLE:
                decisions.append(effect)
                applicable_obligations.extend(policy.obligations)
        
        # 应用组合算法
        final_decision = self._combine_decisions(decisions)
        
        return final_decision, applicable_obligations
    
    def _combine_decisions(self, decisions: List[Effect]) -> Effect:
        """组合多个策略决策"""
        if not decisions:
            return Effect.NOT_APPLICABLE
        
        if self.combining_algorithm == "deny_overrides":
            # 拒绝优先: 任一 DENY = DENY
            if Effect.DENY in decisions:
                return Effect.DENY
            if Effect.PERMIT in decisions:
                return Effect.PERMIT
            return Effect.NOT_APPLICABLE
        
        elif self.combining_algorithm == "permit_overrides":
            # 允许优先: 任一 PERMIT = PERMIT
            if Effect.PERMIT in decisions:
                return Effect.PERMIT
            if Effect.DENY in decisions:
                return Effect.DENY
            return Effect.NOT_APPLICABLE
        
        elif self.combining_algorithm == "first_applicable":
            # 第一个适用的
            for d in decisions:
                if d != Effect.NOT_APPLICABLE:
                    return d
            return Effect.NOT_APPLICABLE
        
        return Effect.NOT_APPLICABLE
    
    def authorize(self, subject: Subject, resource: Resource,
                 action: Action, env: Environment = None) -> bool:
        """简化授权接口"""
        decision, _ = self.evaluate(subject, resource, action, env)
        return decision == Effect.PERMIT


# 创建 ABAC 策略引擎
abac_engine = ABACPolicyEngine()

# 策略 1: 允许员工在工作时间访问内部文档
policy1 = PolicyRule("work_hours_access", "工作时间访问内部文档")
policy1.target_conditions = [
    # 目标是文档资源
    lambda s, r, a, e: r.type == "document",
    # 操作是读取
    lambda s, r, a, e: a.type == "read",
]
policy1.condition = lambda s, r, a, e: (
    # 用户是员工
    s.attributes.get('employment_type') == 'employee' and
    # 资源是内部文档
    r.attributes.get('classification') in ['internal', 'public'] and
    # 工作时间 (9-18)
    9 <= e.attributes.get('hour', 0) <= 18 and
    # 工作日 (0=周一, 6=周日)
    e.attributes.get('weekday', 0) < 5
)
policy1.effect = Effect.PERMIT
abac_engine.add_policy(policy1)

# 策略 2: 允许文档所有者随时访问自己的文档
policy2 = PolicyRule("owner_access", "所有者访问权限")
policy2.target_conditions = [
    lambda s, r, a, e: r.type == "document",
]
policy2.condition = lambda s, r, a, e: s.id == r.owner
policy2.effect = Effect.PERMIT
abac_engine.add_policy(policy2)

# 策略 3: 禁止访问机密文档（除非有 clearance）
policy3 = PolicyRule("classified_deny", "机密文档访问限制")
policy3.target_conditions = [
    lambda s, r, a, e: r.type == "document",
]
policy3.condition = lambda s, r, a, e: (
    r.attributes.get('classification') == 'confidential' and
    s.attributes.get('clearance_level', 0) < r.attributes.get('required_clearance', 5)
)
policy3.effect = Effect.DENY
abac_engine.add_policy(policy3)

# 策略 4: 允许经理访问所有文档
policy4 = PolicyRule("manager_access", "经理访问权限")
policy4.target_conditions = [
    lambda s, r, a, e: r.type == "document",
]
policy4.condition = lambda s, r, a, e: (
    'manager' in s.attributes.get('roles', [])
)
policy4.effect = Effect.PERMIT
abac_engine.add_policy(policy4)

# 策略 5: 允许财务部门访问财务文档
policy5 = PolicyRule("dept_access", "部门文档访问")
policy5.target_conditions = [
    lambda s, r, a, e: r.type == "document",
    lambda s, r, a, e: r.attributes.get('department') is not None,
]
policy5.condition = lambda s, r, a, e: (
    s.attributes.get('department') == r.attributes.get('department')
)
policy5.effect = Effect.PERMIT
abac_engine.add_policy(policy5)


# 使用示例
print("\n=== ABAC 策略评估 ===")

# 场景 1: 普通员工工作时间访问内部文档
subject1 = Subject(
    id="user1",
    attributes={
        'employment_type': 'employee',
        'department': 'engineering',
        'roles': ['developer'],
        'clearance_level': 3
    }
)
resource1 = Resource(
    id="doc1",
    type="document",
    attributes={'classification': 'internal'},
    owner="user2"
)
action1 = Action(type="read")

# 模拟工作时间
env_work_hours = Environment(attributes={'hour': 10, 'weekday': 2})

result1 = abac_engine.authorize(subject1, resource1, action1, env_work_hours)
print(f"场景1 - 员工工作时间访问内部文档: {'允许' if result1 else '拒绝'}")

# 场景 2: 员工非工作时间访问
env_after_hours = Environment(attributes={'hour': 20, 'weekday': 2})
result2 = abac_engine.authorize(subject1, resource1, action1, env_after_hours)
print(f"场景2 - 员工非工作时间访问内部文档: {'允许' if result2 else '拒绝'}")

# 场景 3: 文档所有者访问自己的文档
resource3 = Resource(
    id="doc3",
    type="document", 
    attributes={'classification': 'internal'},
    owner="user1"  # 所有者就是 user1
)
result3 = abac_engine.authorize(subject1, resource3, action1, env_after_hours)
print(f"场景3 - 所有者非工作时间访问自己的文档: {'允许' if result3 else '拒绝'}")

# 场景 4: 无权限访问机密文档
resource4 = Resource(
    id="doc4",
    type="document",
    attributes={
        'classification': 'confidential',
        'required_clearance': 5
    },
    owner="user5"
)
result4 = abac_engine.authorize(subject1, resource4, action1, env_work_hours)
print(f"场景4 - 低权限用户访问高密级文档: {'允许' if result4 else '拒绝'}")

# 场景 5: 经理访问任何文档
subject5 = Subject(
    id="user5",
    attributes={
        'employment_type': 'employee',
        'roles': ['manager'],
        'clearance_level': 5
    }
)
result5 = abac_engine.authorize(subject5, resource4, action1, env_after_hours)
print(f"场景5 - 经理访问机密文档: {'允许' if result5 else '拒绝'}")
```

### 3. 基于策略的访问控制 (PBAC) 和 ReBAC

```python
class RelationshipBasedAccessControl:
    """
    ReBAC: Relationship-Based Access Control
    用于社交/协作场景，如 Google Drive、Notion
    """
    
    def __init__(self):
        # 关系图: 用户与资源之间的关系
        self.relationships: Dict[str, Dict[str, str]] = {}
        # 关系传递规则
        self.transitive_rules: Dict[str, List[str]] = {
            'owner': ['editor', 'viewer'],  # owner 隐含 editor 和 viewer
            'editor': ['viewer'],            # editor 隐含 viewer
        }
    
    def add_relationship(self, user_id: str, resource_id: str, relation: str):
        """添加用户-资源关系"""
        key = f"{user_id}:{resource_id}"
        self.relationships[key] = relation
    
    def check_permission(self, user_id: str, resource_id: str,
                        required: str) -> bool:
        """检查用户是否有指定关系（或更高）"""
        key = f"{user_id}:{resource_id}"
        actual = self.relationships.get(key)
        
        if not actual:
            return False
        
        if actual == required:
            return True
        
        # 检查关系传递
        if actual in self.transitive_rules:
            if required in self.transitive_rules[actual]:
                return True
        
        return False


class PolicyBasedAccessControl:
    """
    PBAC: Policy-Based Access Control
    企业级策略管理，支持策略组合和版本控制
    """
    
    def __init__(self):
        self.policy_sets: Dict[str, Dict] = {}
        self.policy_store: Dict[str, str] = {}  # 持久化存储路径
    
    def define_policy_set(self, name: str, policies: List[str],
                         combining_algo: str = "deny_overrides"):
        """定义策略集"""
        self.policy_sets[name] = {
            'policies': policies,
            'combining_algorithm': combining_algo,
            'version': 1,
            'created_at': datetime.now()
        }
    
    def evaluate_policy_set(self, set_name: str, context: Dict) -> str:
        """评估策略集"""
        if set_name not in self.policy_sets:
            return "NotApplicable"
        
        policy_set = self.policy_sets[set_name]
        results = []
        
        for policy_ref in policy_set['policies']:
            result = self._evaluate_single_policy(policy_ref, context)
            results.append(result)
        
        return self._apply_combining_algo(
            results, 
            policy_set['combining_algorithm']
        )
    
    def _evaluate_single_policy(self, policy_ref: str, context: Dict) -> str:
        """评估单个策略 (XACML 风格)"""
        # 简化实现
        return "Permit"  # 实际应解析 XACML/Rego 等策略语言
    
    def _apply_combining_algo(self, results: List[str], algo: str) -> str:
        """应用组合算法"""
        if algo == "deny_overrides":
            if "Deny" in results:
                return "Deny"
            return "Permit" if "Permit" in results else "NotApplicable"
        return "NotApplicable"
```

---

## 应用场景

### 场景 1: SaaS 多租户权限系统

```
┌─────────────────────────────────────────────────────────────────┐
│              SaaS 多租户权限架构                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    租户 A                                │  │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │  │
│   │  │Admin    │  │Manager  │  │Editor   │  │Viewer   │   │  │
│   │  │租户管理  │  │团队管理  │  │内容编辑  │  │只读访问  │   │  │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│   ┌──────────────────────────┼──────────────────────────────┐  │
│   │                    租户 B │                               │  │
│   │  ┌─────────┐  ┌─────────┐│ ┌─────────┐  ┌─────────┐    │  │
│   │  │Admin    │  │Manager  ││ │Editor   │  │Viewer   │    │  │
│   │  │(隔离)   │  │(隔离)   ││ │(隔离)   │  │(隔离)   │    │  │
│   │  └─────────┘  └─────────┘│ └─────────┘  └─────────┘    │  │
│   └──────────────────────────┴──────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                 权限服务层                               │  │
│   │  • 租户隔离策略                                          │  │
│   │  • 角色模板管理                                          │  │
│   │  • 权限继承与传播                                        │  │
│   │  • 资源级权限控制                                        │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 场景 2: API 网关权限控制

```
┌─────────────────────────────────────────────────────────────────┐
│                   API 网关权限控制                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  客户端请求                                                      │
│     │                                                           │
│     ▼                                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     API Gateway                          │  │
│  │                                                          │  │
│  │  1. 提取 Token ──▶ 2. 验证 Token ──▶ 3. 提取用户信息    │  │
│  │                                                          │  │
│  │  4. 权限检查:                                            │  │
│  │     ┌─────────────────────────────────────────────────┐  │  │
│  │     │ 用户: {user_id: "u123", roles: ["premium"]}    │  │  │
│  │     │ 资源: /api/v1/premium-content                  │  │  │
│  │     │ 操作: GET                                        │  │  │
│  │     │                                                  │  │  │
│  │     │ 策略: IF 'premium' in user.roles               │  │  │
│  │     │       AND resource.path.startswith('/premium')  │  │  │
│  │     │       THEN PERMIT                                │  │  │
│  │     └─────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  5. 决策: PERMIT ──▶ 6. 路由到后端服务                   │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│                        后端微服务                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 面试要点

### Q1: RBAC 和 ABAC 的区别？如何选择？

**A:**

| 维度 | RBAC | ABAC |
|------|------|------|
| 粒度 | 粗粒度（角色级别） | 细粒度（属性级别） |
| 复杂度 | 简单，易于理解 | 复杂，需要策略引擎 |
| 灵活性 | 较低，需要预定义角色 | 极高，动态评估 |
| 性能 | 高，可缓存 | 较低，实时评估 |
| 管理成本 | 中等 | 较高 |
| 场景 | 组织架构清晰 | 复杂业务规则、合规要求 |

**选择建议:**
- 使用 RBAC: 中小型应用、组织架构稳定、权限变更不频繁
- 使用 ABAC: 大型企业、多租户 SaaS、需要上下文感知（时间、地点）、严格合规要求
- 混合使用: RBAC 作为基础，ABAC 用于例外和细粒度控制

### Q2: 如何处理角色爆炸问题（Role Explosion）？

**A:**

角色爆炸发生在需要为不同资源/部门创建大量相似角色时（如 "财务部管理员"、"销售部管理员"...）。

**解决方案:**

1. **角色层次结构**: 定义基础角色，通过继承扩展
   ```
   Admin (基础权限)
     └── DepartmentAdmin (部门级权限)
           ├── FinanceAdmin
           └── SalesAdmin
   ```

2. **引入资源级权限**: 用户-角色关系 + 用户-资源关系
   - `user1` 有 `Editor` 角色
   - `user1` 对 `projectA` 有额外权限

3. **使用 ABAC 属性**: 用属性替代特定角色
   ```
   IF user.role == 'Admin' AND user.department == resource.department
   ```

4. **动态角色/权限**: 根据上下文动态计算有效权限

### Q3: 如何设计一个支持 10 万用户、1000 权限点的权限系统？

**A:**

**架构设计:**

```
1. 数据层:
   - 用户表: 10万记录
   - 角色表: 数百记录  
   - 权限表: 1000记录
   - 用户-角色关联表: 索引优化
   - 角色-权限关联表: 索引优化

2. 缓存层 (Redis):
   - 用户权限缓存: user:{id}:perms → Set<perm_id>
   - 角色权限缓存: role:{id}:perms → Set<perm_id>
   - TTL: 5分钟，变更时主动失效

3. 计算层:
   - 用户登录时计算全部权限 → 缓存
   - 权限检查: 先查缓存 → 再查DB
   - 批量加载: Pipeline 减少网络往返

4. 策略:
   - 权限变更: 更新DB + 删除缓存
   - 定期全量同步: 防止缓存穿透
   - 热点权限: 本地 Caffeine 缓存
```

**性能优化:**
- 使用位图 (Bitmap) 存储权限，1000 权限 = 125 字节/用户
- 权限预计算 + 增量更新
- 读写分离，权限校验走从库

### Q4: 如何实现权限的实时撤销？

**A:**

**方案 1: JWT 黑名单 (短 Token + 黑名单)**
```python
# 用户被禁用后，将其 Token ID 加入黑名单
redis.sadd('token:blacklist', token_jti)
redis.expire('token:blacklist', token_remaining_ttl)

# 验证时检查
if token_jti in redis.smembers('token:blacklist'):
    raise Unauthorized()
```

**方案 2: Token 版本号**
```python
# 用户表添加 token_version 字段
# Token 中包含版本号
# 验证时比对版本号
if token_version != user.current_token_version:
    raise Unauthorized()  # 用户登出或密码修改后版本号增加
```

**方案 3: Session 存储 (Stateful)**
- 服务端存储 Session 状态
- 直接删除/修改 Session 记录即可立即生效
- 适合需要立即生效的高安全场景

**方案 4: 短期 Token (默认安全)**
- Access Token: 5-15 分钟过期
- Refresh Token: 可撤销
- 权限变更等待 Token 自然过期

---

## 相关概念

### 数据结构
- [哈希表](../computer-science/data-structures/hash-table.md)：用户-权限映射快速查找
- [树](../computer-science/data-structures/tree.md)：角色继承层次结构
- [图](../computer-science/data-structures/graph.md)：ReBAC 关系图

### 算法
- [位运算](../computer-science/algorithms/bit-manipulation.md)：权限位图优化存储
- [缓存策略](../computer-science/systems/cache.md)：权限缓存与失效策略

### 复杂度分析
- [时间复杂度](../references/time-complexity.md)：权限检查 O(1) vs O(n)
- [空间复杂度](../references/space-complexity.md)：权限存储空间优化

### 系统实现
- [身份认证](./authentication.md)：授权的前提
- [访问控制](./system-security/access-control.md)：系统级访问控制
- [会话管理](./session-management.md)：权限与会话绑定
- [API 安全](../web-security.md)：API 层权限控制

### 安全领域
- [RBAC 详细实现](../system-security/rbac.md)：系统级 RBAC
- [安全审计](./audit-logging.md)：权限使用审计
- [输入验证](./input-validation.md)：防止权限绕过
- [Web 安全](../common-vulnerabilities.md)：权限相关漏洞

---

## 参考资料

1. [NIST RBAC Standard](https://csrc.nist.gov/projects/role-based-access-control)
2. [XACML 3.0 Specification](http://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html)
3. [AWS IAM Policy Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)
4. [Google Zanzibar Paper](https://research.google/pubs/pub48190/)
5. [Open Policy Agent (OPA)](https://www.openpolicyagent.org/)
