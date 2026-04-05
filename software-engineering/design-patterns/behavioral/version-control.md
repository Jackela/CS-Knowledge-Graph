# 版本控制 (Version Control)

版本控制是追踪和管理文件变更的系统，允许开发者查看历史版本、协作开发和回滚更改。

## 核心概念

### 版本控制类型

```
┌─────────────────────────────────────────────────────────────┐
│                  版本控制类型                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  本地版本控制                                                │
│  ├── RCS (Revision Control System)                          │
│  └── 仅本地存储历史                                          │
│                                                             │
│  集中式版本控制 (Centralized)                                 │
│  ├── SVN (Subversion)                                       │
│  ├── Perforce                                               │
│  └── 中央服务器存储所有版本                                   │
│                                                             │
│  分布式版本控制 (Distributed)                                 │
│  ├── Git                                                    │
│  ├── Mercurial                                              │
│  └── 每个副本都是完整仓库                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Git 工作流

### 基本命令

```bash
# 初始化仓库
git init

# 添加文件
git add filename
git add .

# 提交更改
git commit -m "提交信息"

# 查看历史
git log --oneline --graph

# 分支操作
git branch feature-branch
git checkout feature-branch
git merge feature-branch

# 远程操作
git clone <url>
git push origin main
git pull origin main
```

### Git 工作流模型

```
┌─────────┐    ┌─────────┐    ┌─────────┐
│  main   │◀───│ develop │◀───│ feature │
│  主干   │    │  开发   │    │  功能   │
└─────────┘    └─────────┘    └─────────┘
      ▲              ▲
      │              │
┌─────────┐    ┌─────────┐
│  hotfix │    │ release │
│  热修复  │    │  发布   │
└─────────┘    └─────────┘
```

## 版本控制策略

### 分支策略

| 策略 | 特点 | 适用场景 |
|------|------|----------|
| Git Flow | 严格的分支模型 | 大型项目 |
| GitHub Flow | 简单，PR驱动 | 持续部署 |
| GitLab Flow | 环境分支 | 多环境部署 |
| Trunk-based | 主干开发 | 小型团队 |

### 提交规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**: feat, fix, docs, style, refactor, test, chore

## 应用场景

### 协作开发

```
开发者A              远程仓库              开发者B
   │                    │                    │
   │ push ─────────────▶│◀─────── push       │
   │                    │                    │
   │◀─────── pull ──────┼─────── pull ──────▶│
```

### 代码审查

1. 创建功能分支
2. 提交更改
3. 发起 Pull Request
4. 代码审查
5. 合并到主分支

## 相关概念

- [Git](../../git.md) - 分布式版本控制系统
- [GitHub Actions](../../../cloud-devops/cicd/github-actions.md) - CI/CD 与版本控制集成
- [代码审查](../../code-review.md) - 基于版本的代码审查
- [分支策略](../../branching-strategy.md) - 团队分支管理策略

## 参考资料

1. Pro Git Book
2. GitHub Flow Guide
3. Conventional Commits
