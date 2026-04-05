# Git 版本控制

Git 是一个分布式版本控制系统，用于跟踪文件变化，协调多人协作开发。

## 核心概念

### 工作区、暂存区、仓库
```
┌─────────────────────────────────────────────────────────────┐
│                    Git 工作流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  工作区 (Working Directory)                                  │
│  ├── 文件修改、创建、删除                                     │
│  └── git status 查看状态                                    │
│            │                                                │
│            ▼ git add                                        │
│  暂存区 (Staging Area)                                       │
│  ├── 准备提交的更改                                          │
│  └── git diff --cached 查看暂存差异                         │
│            │                                                │
│            ▼ git commit                                     │
│  本地仓库 (Local Repository)                                 │
│  ├── 提交历史                                                │
│  └── git log 查看提交记录                                   │
│            │                                                │
│            ▼ git push                                       │
│  远程仓库 (Remote Repository)                                │
│  └── GitHub, GitLab, 自建 Git 服务器                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 常用命令

### 基本操作
```bash
# 初始化仓库
git init

# 克隆仓库
git clone <repository-url>

# 查看状态
git status

# 添加文件到暂存区
git add <file>           # 添加特定文件
git add .                # 添加所有更改

# 提交更改
git commit -m "提交信息"
git commit -am "提交信息"  # 添加并提交

# 推送到远程
git push origin <branch>

# 拉取更新
git pull origin <branch>
```

### 分支操作
```bash
# 创建分支
git branch <branch-name>

# 切换分支
git checkout <branch-name>
git switch <branch-name>     # 新版本

# 创建并切换分支
git checkout -b <branch-name>
git switch -c <branch-name>  # 新版本

# 合并分支
git merge <branch-name>

# 删除分支
git branch -d <branch-name>   # 已合并
git branch -D <branch-name>   # 强制删除
```

## 分支策略

### Git Flow
```
main/master    ●────────────────●────────────────●
               │                │                │
hotfix         │           ●────┴────●           │
               │           │         │           │
develop ───────┼───────────┼─────────┼───────────┼──────▶
               │    ●──────┘         │    ●──────┘
feature/A      │    │                │    │
               ●────┘                ●────┘
               │    ●──────┐              ●──────┐
feature/B      │    │      │              │      │
               ●────┘      ●──────────────┘      ●
               │                           ●──────┤
release        │                           │      │
               │                      ●────┴──────┘
```

### 分支说明
| 分支 | 用途 | 生命周期 |
|------|------|----------|
| main/master | 生产环境 | 永久 |
| develop | 开发集成 | 永久 |
| feature/* | 功能开发 | 临时 |
| release/* | 版本发布 | 临时 |
| hotfix/* | 紧急修复 | 临时 |

## 协作工作流

### Pull Request 流程
```
1. 从 main 创建功能分支
   git checkout -b feature/login

2. 开发并提交代码
   git add .
   git commit -m "feat: 实现用户登录"

3. 推送到远程
   git push origin feature/login

4. 创建 Pull Request
   - 代码审查
   - CI 检查
   - 合并到 main
```

## 高级特性

### 交互式变基
```bash
# 修改最近3次提交
git rebase -i HEAD~3

# 常用操作：
# p, pick = 保留提交
# r, reword = 修改提交信息
# e, edit = 修改提交内容
# s, squash = 合并到上一个提交
# d, drop = 删除提交
```

### 储藏更改
```bash
# 储藏当前更改
git stash

# 查看储藏列表
git stash list

# 应用最近储藏
git stash pop

# 应用特定储藏
git stash apply stash@{1}
```

## 相关概念

### 版本控制
- [分支策略](./branching-strategy.md) - 团队协作分支管理
- [代码审查](./code-review.md) - 代码质量控制

### DevOps
- [GitHub Actions](../cloud-devops/cicd/github-actions.md) - CI/CD 自动化
- [GitLab CI](../cloud-devops/gitlab-ci.md) - CI/CD 自动化
- [GitOps](../cloud-devops/gitops.md) - Git 驱动的运维
