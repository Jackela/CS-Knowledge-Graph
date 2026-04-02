# GitLab CI

## 概念

**GitLab CI/CD** 是 GitLab 内置的持续集成/持续部署工具，通过 `.gitlab-ci.yml` 配置文件定义流水线，实现从代码提交到部署的自动化。

> **核心特点**: 与 GitLab 深度集成、Runner 分布式执行、丰富的生态。

---

## 核心概念

### Pipeline（流水线）

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

build_job:
  stage: build
  script:
    - echo "Building..."
    - npm run build

test_job:
  stage: test
  script:
    - echo "Testing..."
    - npm test

deploy_job:
  stage: deploy
  script:
    - echo "Deploying..."
    - npm run deploy
```

### 关键术语

| 术语 | 说明 |
|------|------|
| **Pipeline** | 完整的 CI/CD 流程 |
| **Stage** | 阶段（build/test/deploy）|
| **Job** | 具体任务 |
| **Runner** | 执行 Job 的代理 |
| **Executor** | Runner 的执行环境（Docker/Shell/K8s）|

---

## 配置详解

### 基础配置

```yaml
image: node:18  # 默认镜像

variables:
  NPM_CONFIG_CACHE: "$CI_PROJECT_DIR/.npm"
  NODE_ENV: "production"

before_script:
  - npm ci --cache .npm --prefer-offline

cache:
  paths:
    - .npm/
    - node_modules/

stages:
  - build
  - test
  - deploy
```

### 并行与依赖

```yaml
# 并行测试
unit_tests:
  stage: test
  script:
    - npm run test:unit

integration_tests:
  stage: test
  script:
    - npm run test:integration

e2e_tests:
  stage: test
  script:
    - npm run test:e2e

# 依赖关系
deploy_staging:
  stage: deploy
  dependencies:
    - build_job
  only:
    - develop

deploy_production:
  stage: deploy
  dependencies:
    - build_job
  only:
    - main
  when: manual  # 手动触发
```

### 矩阵构建

```yaml
# 多版本、多平台测试
test:
  parallel:
    matrix:
      - NODE_VERSION: ["16", "18", "20"]
        OS: ["alpine", "ubuntu"]
  image: node:${NODE_VERSION}-${OS}
  script:
    - node --version
    - npm test
```

---

## Runner 类型

| 类型 | 说明 |
|------|------|
| **Shared** | 共享 Runner，所有项目可用 |
| **Group** | 组内项目共享 |
| **Specific** | 特定项目专用 |

### Runner 执行器

```yaml
# Docker 执行器（默认）
[runners.docker]
  image = "alpine:latest"
  privileged = true
  volumes = ["/cache"]

# Kubernetes 执行器
[runners.kubernetes]
  namespace = "gitlab-runner"
  image = "alpine"
```

---

## 高级特性

### 环境管理

```yaml
deploy:
  stage: deploy
  script:
    - deploy-script.sh
  environment:
    name: production
    url: https://example.com
    on_stop: stop_production
  only:
    - main

stop_production:
  stage: deploy
  script:
    - stop-script.sh
  environment:
    name: production
    action: stop
  when: manual
```

### 制品与报告

```yaml
build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

test:
  stage: test
  script:
    - npm run test:coverage
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'
  artifacts:
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
```

### 安全扫描

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml
  - template: Security/Container-Scanning.gitlab-ci.yml

sast:
  variables:
    SAST_EXCLUDED_PATHS: "spec, test, tests, tmp"
```

---

## 与 GitHub Actions 对比

| 特性 | GitLab CI | GitHub Actions |
|------|-----------|----------------|
| 集成 | 深度集成 | 开放平台 |
| 配置 | YAML 单文件 | YAML 工作流 |
| Runner | 自建 Runner | 托管/自建 |
| 生态 | GitLab 生态 | Marketplace |
| 自托管 | 完整支持 | 部分支持 |

---

## 面试要点

1. **Runner 注册**: `gitlab-runner register`
2. **缓存策略**: 依赖缓存加速构建
3. **条件执行**: `only/except/rules` 控制 Job 执行

---

## 相关概念

### CI/CD
- [GitHub Actions](./cicd/github-actions.md) - 替代方案
- [ArgoCD](./argocd.md) - GitOps CD

### 安全
- [常见漏洞](../security/common-vulnerabilities.md) - 安全扫描
- [容器安全](../security/application-security/container-security.md) - 镜像扫描

### DevOps
- [Docker](./docker.md) - 容器化构建
- [Kubernetes](./kubernetes.md) - 部署目标
