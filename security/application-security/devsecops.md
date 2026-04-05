# DevSecOps

DevSecOps 是将安全实践集成到 DevOps 流程中的方法论，强调"安全左移"（Shift Left Security），即在软件开发生命周期的早期阶段就引入安全考虑。

## 核心理念

```
传统模式：
开发 ──▶ 测试 ──▶ 部署 ──▶ 安全审查（太晚！）

DevSecOps：
安全 ──▶ 开发 ──▶ 安全 ──▶ 测试 ──▶ 安全 ──▶ 部署 ──▶ 安全
└────────────────────────────────────────────────────────────┘
                安全贯穿整个生命周期
```

## 关键实践

### 1. 安全即代码 (Security as Code)
```yaml
# 安全策略代码化示例
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: enforce
  rules:
  - name: check-for-labels
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Pod必须包含app和env标签"
      pattern:
        metadata:
          labels:
            app: "?*"
            env: "?*"
```

### 2. 自动化安全测试
```
CI/CD 流水线中的安全检查：

代码提交 ──▶ 静态分析(SAST) ──▶ 依赖扫描 ──▶ 构建 ──▶ 镜像扫描 ──▶ 部署
                │                  │               │
                ▼                  ▼               ▼
           代码漏洞检测      已知漏洞检查      容器安全扫描
```

### 3. 基础设施安全
```hcl
# Terraform 安全基线
resource "aws_security_group" "web" {
  name_prefix = "web-"
  
  # 仅开放必要端口
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # 禁止直接SSH访问
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # 仅限内网
  }
}
```

## 工具链

| 阶段 | 工具类型 | 代表工具 |
|------|---------|---------|
| 编码 | SAST | SonarQube, Checkmarx, CodeQL |
| 构建 | SCA | Snyk, OWASP Dependency-Check |
| 容器 | 镜像扫描 | Trivy, Clair, Anchore |
| 部署 | 配置扫描 | Checkov, tfsec, kube-bench |
| 运行 | 监控 | Falco, Aqua, Sysdig |

## 相关概念

### DevOps与安全
- [容器安全](./container-security.md) - 容器化环境的安全实践
- [CI/CD 安全](./cicd-security.md) - 持续集成/部署中的安全
- [访问控制](../access-control.md) - 权限管理与访问控制

### 云原生安全
- [Kubernetes 安全](../system-security/kubernetes-security.md) - K8s 安全实践
- [Pod 安全策略](./pod-security-policy.md) - Pod 安全配置
