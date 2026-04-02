# ArgoCD

## 概念

**ArgoCD** 是一个用于 Kubernetes 的声明式持续交付（CD）工具，采用 GitOps 理念，将应用的期望状态存储在 Git 仓库中，自动同步到集群。

> **核心思想**: Git 作为唯一事实来源，自动同步集群状态。

---

## GitOps 理念

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Git仓库    │────→│   ArgoCD    │────→│  Kubernetes │
│  (期望状态)  │     │  (同步引擎)  │     │  (实际状态)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   自动/手动  │
                    │   同步状态   │
                    └─────────────┘
```

### GitOps 原则

1. **声明式**: 用 YAML 描述期望状态
2. **版本化**: Git 记录所有变更历史
3. **自动同步**: 检测偏差自动修复
4. **回滚**: Git 历史支持快速回滚

---

## 核心组件

### Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/repo.git
    targetRevision: HEAD
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true      # 自动删除资源
      selfHeal: true   # 自动修复偏差
    syncOptions:
      - CreateNamespace=true
```

### ApplicationSet

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: multi-cluster
spec:
  generators:
    - list:
        elements:
          - cluster: production
            url: https://prod-cluster
          - cluster: staging
            url: https://staging-cluster
  template:
    metadata:
      name: '{{cluster}}-app'
    spec:
      source:
        repoURL: https://github.com/org/repo.git
        targetRevision: HEAD
        path: 'apps/{{cluster}}'
      destination:
        server: '{{url}}'
        namespace: default
```

---

## 同步策略

| 策略 | 说明 |
|------|------|
| **Manual** | 手动触发同步 |
| **Auto-Sync** | 检测 Git 变更自动同步 |
| **Prune** | 删除 Git 中不存在的资源 |
| **Self-Heal** | 修复手动修改导致的偏差 |

---

## ArgoCD 架构

```
┌─────────────────────────────────────────────────────────┐
│                      ArgoCD Server                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ API服务   │  │ 仓库服务  │  │ 应用控制  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Dex认证   │  │ Redis缓存 │  │ Postgres │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes集群                        │
│              (自动部署和管理应用)                         │
└─────────────────────────────────────────────────────────┘
```

---

## 多环境管理

```
repo/
├── base/                    # 基础配置
│   ├── deployment.yaml
│   └── service.yaml
└── overlays/                # 环境覆盖
    ├── development/
    │   └── kustomization.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── production/
        └── kustomization.yaml
```

---

## 面试要点

### Q1: ArgoCD vs 传统CD
- ArgoCD: 拉取模式（Pull），GitOps，声明式
- Jenkins/Spinnaker: 推送模式（Push），命令式

### Q2: 处理 Secret
- Sealed Secrets
- External Secrets Operator
- Vault 集成

### Q3: 回滚策略
- Git revert + 同步
- Argo Rollouts (金丝雀/蓝绿部署)

---

## 相关概念

### CI/CD
- [GitHub Actions](./cicd/github-actions.md) - CI 部分
- [GitLab CI](./gitlab-ci.md) - 替代 CI 方案

### Kubernetes
- [Kubernetes](./kubernetes.md) - 部署目标
- [Helm](./kubernetes.md) - 包管理
- [GitOps](../software-engineering/architecture-patterns/event-driven.md) - 运维理念

### 架构
- [GitOps](./gitops.md) - 运维理念
- [微服务](../software-engineering/architecture-patterns/microservices.md) - 部署单元
