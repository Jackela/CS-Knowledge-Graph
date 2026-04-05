# GitOps

GitOps 是一种运维方法论，以 Git 仓库作为基础设施和应用配置的单一事实来源，通过自动化工具将声明式配置同步到实际运行环境中。

## 核心概念

### GitOps 原则

```
GitOps 工作流：

┌─────────────────────────────────────────────────────────────┐
│                     GitOps 原则                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 声明式配置 (Declarative)                                 │
│     ├── 所有基础设施和应用状态用声明式配置描述                │
│     └── 存储在版本控制系统中                                 │
│                                                             │
│  2. 版本化与不可变 (Versioned & Immutable)                   │
│     ├── Git 记录所有变更历史                                 │
│     └── 支持快速回滚到任意版本                               │
│                                                             │
│  3. 自动拉取 (Pulled Automatically)                          │
│     ├── 自动化工具持续监控 Git 仓库                          │
│     └── 检测到变更后自动应用到目标环境                       │
│                                                             │
│  4. 持续调和 (Continuously Reconciled)                       │
│     ├── 持续比较实际状态与期望状态                           │
│     └── 自动修复偏离，确保一致性                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 推拉模式对比

```
传统 CI/CD (推送模式)：              GitOps (拉取模式)：

CI/CD 工具 ──▶ 部署到集群           Git 仓库 ──▶ 集群代理
                                    (ArgoCD/Flux)
                                    
缺点：                              优点：
- 需要集群访问凭证                  - 集群内运行，无需外部访问
- 难以跟踪实际状态                  - 实时状态同步与监控
- 回滚复杂                          - Git 历史即回滚点
```

## 架构组件

### 典型 GitOps 架构

```
┌─────────────────────────────────────────────────────────────┐
│                     GitOps 架构                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│   │   Git 仓库   │────▶│  GitOps 控制器│────▶│ Kubernetes │   │
│   │             │     │             │     │  集群        │   │
│   ├─────────────┤     ├─────────────┤     ├─────────────┤   │
│   │ • 应用配置   │     │ • 监控变更   │     │ • 应用工作负载│   │
│   │ • 基础设施   │     │ • 同步状态   │     │ • 服务网格   │   │
│   │ • 策略配置   │     │ • 健康检查   │     │ • 配置映射   │   │
│   └─────────────┘     └─────────────┘     └─────────────┘   │
│          │                    │                   │         │
│          │                    ▼                   │         │
│          │            ┌─────────────┐             │         │
│          │            │  状态反馈    │─────────────│         │
│          │            │ • 同步状态   │   实际状态              │
│          │            │ • 差异检测   │                         │
│          │            └─────────────┘                         │
│          │                                                    │
│          └──────────────▶ (UI/API 查看)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 目录结构

```
gitops-repo/
├── apps/                          # 应用配置
│   ├── frontend/
│   │   ├── base/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── kustomization.yaml
│   │   └── overlays/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── production/
│   └── backend/
│       └── ...
├── infrastructure/                # 基础设施
│   ├── monitoring/
│   ├── ingress/
│   └── storage/
├── policies/                      # 策略配置
│   ├── network-policies/
│   └── rbac/
└── clusters/                      # 集群配置
    ├── production/
    └── staging/
```

## 主流工具

### ArgoCD

```
ArgoCD 特点：
- 声明式 GitOps 持续交付
- 支持多种配置管理工具（Helm、Kustomize、Jsonnet）
- 可视化界面和 CLI
- 自动同步和回滚
- 多集群管理
```

### Flux

```
Flux 特点：
- CNCF 毕业项目
- 云原生设计，GitOps 原生
- 与 Kubernetes 深度集成
- 模块化架构（可单独使用组件）
- 支持 OCI 仓库和 Helm
```

### 工具对比

| 特性 | ArgoCD | Flux |
|------|--------|------|
| 用户界面 | ✅ 丰富 | ⚠️ 基础 |
| 多集群 | ✅ 原生支持 | ✅ 原生支持 |
| Helm 支持 | ✅ 完整 | ✅ 完整 |
| 镜像自动更新 | ⚠️ 需扩展 | ✅ 内置 |
| 通知系统 | ✅ 内置 | ✅ 内置 |
| Secrets 管理 | ⚠️ 需集成 | ✅ 内置 SOPS |

## 应用场景

### 多环境管理

```
单一 Git 仓库管理多环境：

Git Repo
├── base/                    # 基础配置
├── overlays/
│   ├── dev/                 # 开发环境
│   ├── staging/             # 预发布环境
│   └── production/          # 生产环境

不同环境自动同步到不同集群
```

### 灾难恢复

```
灾难恢复流程：

集群故障
    │
    ▼
新集群启动
    │
    ▼
GitOps 控制器安装
    │
    ▼
自动从 Git 恢复所有配置
    │
    ▼
服务恢复正常运行
```

### 合规审计

```
GitOps 提供完整审计链：

Git 提交记录 ← 谁在什么时间做了什么变更
    │
    ▼
GitOps 同步日志 ← 变更何时应用到集群
    │
    ▼
集群状态历史 ← 变更的实际效果
```

## 最佳实践

### 仓库组织

```
推荐结构：

1. 单一仓库 vs 多仓库
   - 小团队：单一仓库
   - 大团队：按团队/应用分仓库

2. 分支策略
   - trunk-based：main 分支即生产
   - PR 工作流：审查后合并到 main

3. 环境隔离
   - 不同目录：overlays/dev, overlays/prod
   - 不同分支：dev 分支、prod 分支
```

### Secrets 管理

```
GitOps 中安全处理 Secrets：

1. 外部 Secrets 管理器
   └── 如：Vault、AWS Secrets Manager
   
2. Sealed Secrets
   └── 加密后存储在 Git
   
3. SOPS + Age
   └── Mozilla SOPS 加密配置文件
   
4. External Secrets Operator
   └── 自动从外部同步 Secrets
```

## 相关概念 (Related Concepts)

### DevOps 与 CI/CD
- [ArgoCD](./argocd.md) - 声明式 GitOps CD 工具
- [GitLab CI](./gitlab-ci.md) - CI/CD 流水线

### Kubernetes
- [Kubernetes](./kubernetes.md) - GitOps 主要目标平台

### 基础设施
- [Docker](./docker.md) - 容器化基础
- [Secrets 管理](../security/application-security/secrets-management.md) - GitOps 中的 Secrets 管理

## 参考资料

1. "GitOps: Operations by Pull Request" - Weaveworks
2. OpenGitOps - CNCF GitOps 工作组
3. ArgoCD 官方文档: https://argo-cd.readthedocs.io/
4. Flux 官方文档: https://fluxcd.io/
5. "The GitOps Journey" - GitOps 成熟度模型
