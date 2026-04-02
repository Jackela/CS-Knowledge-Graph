# Secrets 管理 (Secrets Management)

Secrets 管理是安全存储、分发和使用敏感信息（如密码、API 密钥、证书）的实践。

## 核心概念

### Secrets 类型

```
┌─────────────────────────────────────────────────────────────┐
│                   Secrets 类型                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  静态 Secrets (Static)                                      │
│  ├── 数据库密码                                              │
│  ├── API 密钥                                               │
│  └── 配置文件中的凭证                                         │
│                                                             │
│  动态 Secrets (Dynamic)                                     │
│  ├── 临时数据库凭证                                          │
│  ├── 短期访问令牌                                            │
│  └── 自动轮换的证书                                          │
│                                                             │
│  传输中的 Secrets (In-Transit)                              │
│  ├── TLS 证书                                               │
│  ├── 会话令牌                                               │
│  └── 加密密钥交换                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Kubernetes Secrets

### 创建 Secret

```bash
# 命令行创建
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password='secret123'

# 从文件创建
kubectl create secret generic tls-cert \
  --from-file=tls.crt=server.crt \
  --from-file=tls.key=server.key
```

### 使用 Secret

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
    volumeMounts:
    - name: tls
      mountPath: "/etc/tls"
      readOnly: true
  volumes:
  - name: tls
    secret:
      secretName: tls-cert
```

## 安全管理最佳实践

### 1. 避免硬编码

```python
# ❌ 不安全：硬编码凭证
DB_PASSWORD = "secret123"

# ✅ 安全：从环境变量读取
import os
DB_PASSWORD = os.environ.get('DB_PASSWORD')

# ✅ 更安全：使用 Secret 管理工具
from vault import Client
client = Client()
DB_PASSWORD = client.get_secret('db/password')
```

### 2. 密钥轮换

```yaml
# 自动轮换策略
apiVersion: secrets.hashicorp.com/v1beta1
kind: VaultDynamicSecret
metadata:
  name: db-credentials
spec:
  vaultAuthRef: default
  mount: database
  path: creds/readonly
  # 自动轮换
  renewalPercent: 67
```

### 3. 最小权限

```yaml
# RBAC 限制 Secret 访问
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["app-secret"]  # 只允许访问特定 Secret
  verbs: ["get"]
```

## 工具对比

| 工具 | 特点 | 适用场景 |
|------|------|----------|
| Kubernetes Secrets | 原生支持，免费 | K8s 环境基础使用 |
| HashiCorp Vault | 功能全面，企业级 | 大规模多云环境 |
| AWS Secrets Manager | 托管服务，与 AWS 集成 | AWS 生态 |
| Azure Key Vault | 托管服务，与 Azure 集成 | Azure 生态 |
| Sealed Secrets | 加密存储于 Git | GitOps 工作流 |

## Vault 集成示例

### 部署 Vault

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vault
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vault
  template:
    metadata:
      labels:
        app: vault
    spec:
      containers:
      - name: vault
        image: vault:1.13
        ports:
        - containerPort: 8200
```

### 应用集成

```python
import hvac

# 连接 Vault
client = hvac.Client(url='http://vault:8200')
client.token = 'root-token'

# 读取 Secret
secret = client.secrets.kv.v2.read_secret_version(
    path='database/creds'
)
username = secret['data']['data']['username']
password = secret['data']['data']['password']
```

## 安全审计

### 审计日志

```json
{
  "time": "2024-01-15T10:30:00Z",
  "type": "secret-access",
  "user": "dev-team",
  "secret": "db-credentials",
  "action": "read",
  "source_ip": "10.0.1.100"
}
```

### 监控告警

```yaml
# 异常访问检测
alert: SecretAccessAnomaly
expr: |
  increase(secret_access_total[1h]) > 100
labels:
  severity: warning
annotations:
  summary: "异常 Secrets 访问频率"
```

## 相关概念

- [Kubernetes 安全](../system-security/kubernetes-security.md) - K8s 安全实践
- [容器安全](./container-security.md) - 容器 Secrets 管理
- [身份认证](../authentication.md) - 身份验证机制
- [加密](./../cryptography/symmetric-encryption.md) - 数据加密保护

## 参考资料

1. [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
2. [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs)
3. OWASP Secrets Management Cheat Sheet
