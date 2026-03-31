# GitHub Actions CI/CD

## 概念

GitHub Actions 是 GitHub 提供的**持续集成/持续部署 (CI/CD)** 平台，通过 YAML 配置文件定义自动化工作流。

> **核心特点**: 事件驱动、矩阵构建、丰富生态。

---

## 核心概念

### 1. Workflow (工作流)

```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test
      - run: npm run build
```

### 2. Job (任务)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm test

  deploy:
    needs: test  # 依赖 test 任务
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying..."
```

### 3. Matrix (矩阵构建)

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node: [16, 18, 20]
    
runs-on: ${{ matrix.os }}
steps:
  - uses: actions/setup-node@v3
    with:
      node-version: ${{ matrix.node }}
```

---

## 完整示例

```yaml
name: Full Pipeline

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  NODE_VERSION: '18'
  REGISTRY: ghcr.io

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: |
          docker build -t ${{ env.REGISTRY }}/${{ github.repository }}:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker push ${{ env.REGISTRY }}/${{ github.repository }}:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            docker pull ${{ env.REGISTRY }}/${{ github.repository }}:${{ github.sha }}
            docker-compose up -d
```

---

## Secrets 管理

```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}

jobs:
  deploy:
    steps:
      - name: Use secret
        run: echo "Using ${{ secrets.DATABASE_URL }}"
```

---

## 面试要点

1. **vs Jenkins**: 托管服务 vs 自建，YAML vs Groovy
2. **Self-hosted runners**: 私有运行器
3. **Reusable workflows**: 可复用工作流

---

## 相关概念

### 持续集成/部署
- [重构](../../software-engineering/refactoring.md) - 代码重构自动化
- [单元测试](../../software-engineering/testing/unit-testing.md) - 测试自动化
- [Docker](../docker.md) - 容器化构建

### 安全
- [认证](../../security/authentication.md) - Secrets管理
- [Web安全](../../security/web-security.md) - 代码安全检查

### 系统实现
- [进程](../../computer-science/systems/process.md) - 工作流进程管理
- [调度](../../computer-science/systems/scheduling.md) - 任务调度优化
- [内存管理](../../computer-science/systems/memory-management.md) - 构建资源管理

- [GitLab CI](../gitlab-ci.md)
- [ArgoCD](../argocd.md)
