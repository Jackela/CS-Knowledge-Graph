# CI/CD 安全

CI/CD 安全是保护持续集成和持续部署流水线免受攻击的安全实践，确保软件交付过程的可信度和完整性。

## 安全风险

```
CI/CD 常见安全风险：

1. 凭证泄露
   - 硬编码密钥在代码中
   - 环境变量泄露
   - 日志中打印敏感信息

2. 供应链攻击
   - 依赖包被篡改
   - 构建工具被植入恶意代码
   - 镜像源被污染

3. 权限滥用
   - CI/CD 系统过度授权
   - 未及时回收离职员工权限
   - 缺乏审批流程

4. 配置漂移
   - 生产与测试环境配置不一致
   - 基础设施配置未版本化
```

## 安全实践

### 1. 密钥管理
```yaml
# ❌ 错误：硬编码密钥
deploy:
  script:
    - echo "AKIAIOSFODNN7EXAMPLE"  # 危险！

# ✅ 正确：使用密钥管理
secrets:
  AWS_ACCESS_KEY_ID:
    vault: aws/creds/access-key
  
deploy:
  script:
    - echo "$AWS_ACCESS_KEY_ID"  # 从Vault动态获取
```

### 2. 流水线安全
```yaml
# GitHub Actions 安全配置
name: Secure Build

on:
  push:
    branches: [main]
  
jobs:
  build:
    runs-on: ubuntu-latest
    
    # 最小权限原则
    permissions:
      contents: read
      packages: write
      
    steps:
      - uses: actions/checkout@v3
        with:
          # 防止权限升级攻击
          persist-credentials: false
          
      # 依赖扫描
      - name: Scan dependencies
        uses: snyk/actions/node@master
        
      # 使用固定版本
      - name: Setup Node
        uses: actions/setup-node@v3.8.1  # 固定版本
```

### 3. 镜像安全
```dockerfile
# Dockerfile 安全最佳实践

# 使用官方、最小化基础镜像
FROM node:18-alpine

# 创建非root用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# 仅复制必要的文件
COPY --chown=nextjs:nodejs .next/standalone ./
COPY --chown=nextjs:nodejs .next/static ./.next/static

# 切换到非root用户
USER nextjs

EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

## 安全检查清单

| 检查项 | 说明 | 优先级 |
|--------|------|--------|
| 密钥扫描 | 预提交时扫描硬编码密钥 | 高 |
| SAST | 静态应用安全测试 | 高 |
| SCA | 软件成分分析 | 高 |
| 镜像扫描 | 容器镜像漏洞扫描 | 高 |
| 签名验证 | 镜像和制品签名验证 | 中 |
| 合规检查 | 基础设施即代码合规扫描 | 中 |

## 相关概念

### DevOps
- [DevSecOps](./devsecops.md) - 安全左移实践
- [容器安全](./container-security.md) - 容器化安全
- [Secrets 管理](./secrets-management.md) - 敏感信息安全管理

### 工具与实践

### 工具与实践
- [GitHub Actions](../../cloud-devops/cicd/github-actions.md) - CI/CD 平台
- [GitLab CI](../../cloud-devops/gitlab-ci.md) - CI/CD 平台
