# 访问控制 (Access Control)

访问控制是限制用户对系统资源访问的安全机制，确保只有授权用户才能访问特定资源。

## 核心概念

### 访问控制模型

```
┌─────────────────────────────────────────────────────────────┐
│                   访问控制模型                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  主体 (Subject)          访问控制           客体 (Object)     │
│     │                      机制                 │            │
│     │    ───────────────────────────────▶      │            │
│     │                      │                   │            │
│  ┌─────┐              ┌─────────┐          ┌─────┐         │
│  │用户 │              │ 认证    │          │资源 │         │
│  │进程 │─────────────▶│ 授权    │─────────▶│数据 │         │
│  │服务 │              │ 审计    │          │文件 │         │
│  └─────┘              └─────────┘          └─────┘         │
│                                                             │
│  认证(Authentication): 验证身份                               │
│  授权(Authorization): 验证权限                                │
│  审计(Auditing): 记录访问                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 访问控制模型

### 1. 自主访问控制 (DAC)

```
特点：
- 资源所有者决定谁可以访问
- 灵活但难以管理
- 常见于文件系统

示例：
-rw-r--r-- 1 owner group file.txt
  │   │   │
  │   │   └── 其他用户权限
  │   └────── 组权限
  └────────── 所有者权限
```

### 2. 强制访问控制 (MAC)

```
特点：
- 系统强制实施访问策略
- 高安全性，如军事/政府
- 基于安全标签

示例：
用户标签: { 机密, 财务 }
文件标签: { 机密 }

访问规则: 用户标签 ⊇ 文件标签 → 允许读取
```

### 3. 基于角色的访问控制 (RBAC)

```
用户 ──▶ 角色 ──▶ 权限

示例：
┌─────────┐   ┌─────────┐   ┌─────────┐
│  Alice  │──▶│  开发者 │──▶│ 代码仓库 │
│  Bob    │──▶│         │   │ 部署权限 │
└─────────┘   └─────────┘   └─────────┘
┌─────────┐   ┌─────────┐   ┌─────────┐
│  Carol  │──▶│  运维   │──▶│ 生产环境 │
└─────────┘   └─────────┘   │ 监控权限 │
                            └─────────┘
```

## 实现机制

### 访问控制列表 (ACL)

```yaml
# AWS S3 Bucket Policy (ACL 示例)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789:user/alice"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::mybucket/*"
    }
  ]
}
```

### 基于属性的访问控制 (ABAC)

```yaml
# 策略示例
policy:
  - effect: Allow
    action: ["document:read"]
    resource: "document:*"
    condition:
      - attribute: user.department
        operator: equals
        value: resource.department
      - attribute: time.hour
        operator: between
        value: [9, 18]
```

## 最佳实践

### 1. 最小权限原则

```python
# ❌ 过度授权
role_permissions = ["*"]  # 允许所有

# ✅ 精确授权
role_permissions = [
    "user:read",
    "user:write",
    "order:read"  # 没有 order:delete
]
```

### 2. 职责分离

```
财务系统：
┌─────────────┐      ┌─────────────┐
│  会计角色    │      │  审计角色    │
│  (录入数据)  │ ◀──▶ │  (审核数据)  │
└─────────────┘      └─────────────┘
        
        同一人不能同时拥有两个角色
```

### 3. 定期审查

```
访问审查流程：

1. 季度审查
   - 检查不活跃账户
   - 确认角色分配合理性
   
2. 离职处理
   - 立即撤销所有权限
   - 转移资源所有权
   
3. 权限变更
   - 记录变更原因
   - 审批流程留痕
```

## 应用场景

### Web 应用访问控制

```python
from functools import wraps

def require_permission(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user.has_permission(permission):
                raise Forbidden("缺少权限")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/admin/users')
@require_permission('user:admin')
def admin_users():
    return render_users()
```

### 数据库访问控制

```sql
-- 创建只读角色
CREATE ROLE readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

-- 创建读写角色
CREATE ROLE readwrite;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES TO readwrite;

-- 分配角色给用户
GRANT readonly TO analyst_user;
GRANT readwrite TO app_user;
```

## 相关概念

- [RBAC](./rbac.md) - 基于角色的访问控制详解
- [身份认证](./authentication.md) - 用户身份验证
- [授权](./authorization.md) - 权限授予机制
- [Kubernetes RBAC](./rbac.md) - K8s 访问控制实现

## 参考资料

1. NIST SP 800-53 - Access Control Guidelines
2. OWASP Access Control Cheat Sheet
3. ABAC - OASIS Standard
