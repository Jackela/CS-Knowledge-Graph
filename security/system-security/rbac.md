# 基于角色的访问控制 (RBAC)

RBAC (Role-Based Access Control) 是一种访问控制机制，通过角色来管理用户权限，实现最小权限原则。

## 核心概念

### RBAC 三要素

```
┌─────────────────────────────────────────────────────────────┐
│                     RBAC 模型                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    用户 (User)          角色 (Role)         权限 (Permission) │
│       │                    │                    │            │
│       └────────────────────┼────────────────────┘            │
│                            │                                 │
│                            ▼                                 │
│                      角色绑定                                │
│                   (Role Binding)                             │
│                                                             │
│  • 用户被分配角色                                           │
│  • 角色拥有特定权限                                         │
│  • 用户通过角色获得权限                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Kubernetes RBAC

### Role (命名空间级别)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: developer
rules:
- apiGroups: ["", "apps"]
  resources: ["pods", "services", "deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
```

### ClusterRole (集群级别)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

### RoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: default
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io
- kind: ServiceAccount
  name: ci-bot
  namespace: default
roleRef:
  kind: Role
  name: developer
  apiGroup: rbac.authorization.k8s.io
```

## RBAC 最佳实践

### 1. 最小权限原则

```yaml
# ❌ 过度授权
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]

# ✅ 精确授权
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
  resourceNames: ["my-pod"]
```

### 2. 使用聚合角色

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.example.com/aggregate-to-monitoring: "true"
rules: []
```

## 应用场景

### 多租户隔离

```
团队 A                    团队 B
  │                        │
  ▼                        ▼
┌─────────┐            ┌─────────┐
│ Namespace│            │ Namespace│
│   team-a │            │   team-b │
│          │            │          │
│ Role:    │            │ Role:    │
│  editor  │            │  editor  │
└─────────┘            └─────────┘
```

### CI/CD 权限

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cicd
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployer
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "update", "patch"]
```

## 面试要点

**Q: RBAC 和 ABAC 的区别？**

**A:** 
- **RBAC**: 基于角色，权限与角色绑定，用户通过角色获得权限
- **ABAC**: 基于属性，权限由用户、资源、环境等属性动态决定

**Q: Role 和 ClusterRole 的区别？**

**A:**
- **Role**: 命名空间级别，权限仅限于特定命名空间
- **ClusterRole**: 集群级别，权限可跨命名空间，也可用于非命名空间资源

## 相关概念

- [Kubernetes 安全](./kubernetes-security.md) - K8s 安全实践
- [访问控制](../access-control.md) - 访问控制基础
- [身份认证](../authentication.md) - 用户身份验证
- [容器安全](../application-security/container-security.md) - 容器运行时安全

## 参考资料

1. [Kubernetes RBAC Documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
2. [RBAC vs ABAC](https://www.okta.com/identity-101/rbac-vs-abac/)
