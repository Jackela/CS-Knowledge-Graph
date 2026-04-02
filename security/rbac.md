# RBAC (Role-Based Access Control)

RBAC（基于角色的访问控制）是一种通过角色来管理用户权限的访问控制模型。用户与角色关联，角色与权限关联，从而实现灵活的权限管理。

## 核心概念

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  用户   │────▶│  角色   │────▶│  权限   │
└─────────┘     └─────────┘     └─────────┘

用户-角色关系：多对多（一个用户可拥有多个角色）
角色-权限关系：多对多（一个角色可包含多个权限）
```

## RBAC 层级

### RBAC0 - 基础模型
```
核心实体：
- 用户 (User)
- 角色 (Role)  
- 权限 (Permission)
- 会话 (Session)
```

### RBAC1 - 角色继承
```
角色层次结构：

        ┌──────────┐
        │  超级管理员 │
        └────┬─────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
┌───────┐ ┌───────┐ ┌───────┐
│ 管理员 │ │ 审计员 │ │ 运维员 │
└───┬───┘ └───────┘ └───────┘
    │
    ▼
┌───────┐
│ 普通用户 │
└───────┘

下级角色继承上级角色的所有权限
```

### RBAC2 - 约束模型
```
约束类型：

1. 互斥角色 (Mutual Exclusion)
   - 用户不能同时拥有互斥的角色
   - 例：会计和审计不能由同一人担任

2. 基数约束 (Cardinality)
   - 限制角色的用户数量
   - 例：CEO角色只能分配给1人

3. 先决条件 (Prerequisite)
   - 拥有角色A的前提是拥有角色B
   - 例：成为"高级开发者"前必须是"开发者"
```

## 实践示例

### 企业系统角色设计
```yaml
角色定义:
  系统管理员:
    权限:
      - user:*
      - system:*
      - config:*
    
  部门经理:
    权限:
      - department:read
      - department:write
      - employee:read
      - report:read
      
  普通员工:
    权限:
      - profile:read
      - profile:write
      - leave:apply
```

### 数据库实现
```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- 角色表
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- 权限表
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    UNIQUE(resource, action)
);

-- 用户-角色关联
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- 角色-权限关联
CREATE TABLE role_permissions (
    role_id INTEGER REFERENCES roles(id),
    permission_id INTEGER REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);
```

## 相关概念

### 访问控制
- [访问控制](./access-control.md) - 访问控制概述
- [身份认证](./authentication.md) - 用户身份验证
- [授权](./authorization.md) - 权限授予机制

### 系统实现
- [Kubernetes 安全](./system-security/kubernetes-security.md) - K8s 安全实践
- [权限管理](./authorization.md) - 权限管理最佳实践
