# Kubernetes ConfigMaps & Secrets (K8s 配置与密钥管理)

## 简介

**ConfigMap** 和 **Secret** 是 Kubernetes 中用于分离配置与容器镜像的 API 对象。ConfigMap 存储非敏感的配置数据（如配置文件、环境变量），Secret 存储敏感信息（如密码、API 密钥、TLS 证书）。通过这种方式，可以在不重新构建镜像的情况下更新应用配置，实现配置的动态注入和版本管理。

## 核心概念

### ConfigMap

- **数据存储**：键值对形式的配置数据，value 可以是字符串或多行文本
- **容量限制**：数据总量不能超过 1MB（etcd 限制）
- **不可变性**：可通过 immutable: true 设置为不可变，提高性能
- **使用方式**：环境变量注入、命令行参数、挂载为文件
- **热更新**：挂载为卷时可自动更新，环境变量方式需要重启 Pod

### Secret

- **数据存储**：Base64 编码的敏感数据，建议限制在 1MB 以内
- **内置类型**：Opaque（通用）、tls（TLS 证书）、docker-registry（镜像仓库认证）、basic-auth（HTTP 基本认证）、service-account-token（ServiceAccount 令牌）
- **加密存储**：etcd 中数据默认 Base64 编码，可通过 KMS 或静态加密增强安全性
- **访问控制**：通过 RBAC 限制 Secret 的读取权限
- **内存存储**：Secret 可以挂载为 tmpfs（内存文件系统），避免写入磁盘

## 实现方式

### ConfigMap 创建与使用

```yaml
# ConfigMap 定义
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
  labels:
    app: myapp
    environment: production
data:
  # 简单键值对
  database.host: "postgres.default.svc.cluster.local"
  database.port: "5432"
  database.name: "myapp"
  cache.enabled: "true"
  log.level: "info"
  
  # 多行配置文件
  application.properties: |
    server.port=8080
    server.compression.enabled=true
    spring.datasource.hikari.maximum-pool-size=20
    spring.jpa.hibernate.ddl-auto=validate
    management.endpoints.web.exposure.include=health,metrics,prometheus
    
  nginx.conf: |
    server {
      listen 80;
      server_name localhost;
      
      location / {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
      }
      
      location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
      }
    }
  
  # JSON 配置
  feature-flags.json: |
    {
      "newDashboard": true,
      "darkMode": false,
      "betaFeature": false,
      "maintenanceMode": false
    }

# 不可变 ConfigMap
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: immutable-config
  namespace: default
immutable: true
data:
  config.version: "1.0.0"
  app.name: "production-app"
```

### Secret 创建与使用

```yaml
# 通用 Secret（Opaque）
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: default
type: Opaque
data:
  # 使用 base64 编码的数据
  # echo -n 'mysecretpassword' | base64
  database.password: bXlzZWNyZXRwYXNzd29yZA==
  api.key: YXBpLWtleS0xMjM0NTY=
  jwt.secret: c2VjcmV0LWtleS1mb3Itand0LXNpZ25pbmc=

# TLS Secret
---
apiVersion: v1
kind: Secret
metadata:
  name: tls-secret
  namespace: default
type: kubernetes.io/tls
data:
  # base64 编码的证书和私钥
  # cat cert.pem | base64 -w 0
  tls.crt: LS0tLS1CRUdJTi...（证书内容）
  tls.key: LS0tLS1CRUdJTi...（私钥内容）

# Docker Registry Secret
---
apiVersion: v1
kind: Secret
metadata:
  name: regcred
  namespace: default
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: eyJhdXRocyI6eyJodHRwczovL2luZGV4L...（配置内容）

# 或使用命令创建
# kubectl create secret docker-registry regcred \
#   --docker-server=https://index.docker.io/v1/ \
#   --docker-username=username \
#   --docker-password=password \
#   --docker-email=email@example.com
```

### 在 Pod 中使用 ConfigMap 和 Secret

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-pod
spec:
  # 使用 Secret 拉取私有镜像
  imagePullSecrets:
    - name: regcred
  
  containers:
    - name: app
      image: myapp:v1
      
      # 方式1：环境变量 - 单个值
      env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: database.host
        
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database.password
        
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: api.key
              optional: true  # 可选，不存在不报错
      
      # 方式2：envFrom - 批量注入所有键值
      envFrom:
        - configMapRef:
            name: app-config
            optional: false
        - secretRef:
            name: app-secrets
            optional: false
        # 前缀区分来源
        - configMapRef:
            name: feature-config
          prefix: FEATURE_
      
      # 方式3：卷挂载 - 配置文件
      volumeMounts:
        # 挂载整个 ConfigMap 为目录
        - name: config-vol
          mountPath: /etc/config
          readOnly: true
        
        # 挂载特定文件
        - name: nginx-config
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: nginx.conf
          readOnly: true
        
        # 挂载 Secret 为文件（内存存储）
        - name: secret-vol
          mountPath: /etc/secrets
          readOnly: true
        
        # 挂载 TLS 证书
        - name: tls-vol
          mountPath: /etc/tls
          readOnly: true
      
      # 使用 ConfigMap 值作为命令参数
      command:
        - /bin/sh
        - -c
      args:
        - |
          echo "Starting with log level: $LOG_LEVEL"
          java -jar app.jar --server.port=$SERVER_PORT
  
  volumes:
    # ConfigMap 卷
    - name: config-vol
      configMap:
        name: app-config
        defaultMode: 0644
        items:
          - key: application.properties
            path: app.properties
          - key: feature-flags.json
            path: features.json
    
    # 单独挂载 nginx 配置
    - name: nginx-config
      configMap:
        name: app-config
        items:
          - key: nginx.conf
            path: nginx.conf
    
    # Secret 卷（自动挂载为 tmpfs）
    - name: secret-vol
      secret:
        secretName: app-secrets
        defaultMode: 0400
        items:
          - key: database.password
            path: db-password.txt
          - key: api.key
            path: api-key.txt
    
    # TLS Secret 卷
    - name: tls-vol
      secret:
        secretName: tls-secret
        defaultMode: 0400
```

### Deployment 中统一使用

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: app
          image: myapp:v2.1.0
          ports:
            - containerPort: 8080
          
          # 混合使用 ConfigMap 和 Secret
          envFrom:
            - configMapRef:
                name: app-config
            - secretRef:
                name: app-secrets
          
          volumeMounts:
            - name: config
              mountPath: /app/config
              readOnly: true
            - name: secrets
              mountPath: /app/secrets
              readOnly: true
      
      volumes:
        - name: config
          projected:
            sources:
              - configMap:
                  name: app-config
                  items:
                    - key: application.properties
                      path: application.properties
              - configMap:
                  name: logging-config
                  items:
                    - key: logback.xml
                      path: logback.xml
        
        - name: secrets
          projected:
            sources:
              - secret:
                  name: db-credentials
                  items:
                    - key: username
                      path: db-username
                    - key: password
                      path: db-password
              - secret:
                  name: api-credentials
                  items:
                    - key: api-key
                      path: api-key
```

## 安全最佳实践

### 1. Secret 加密存储

```yaml
# 启用静态加密（EncryptionConfiguration）
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <base64-encoded-32-byte-key>
      - identity: {}
```

### 2. RBAC 访问控制

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: secret-reader
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get", "list"]
    resourceNames: ["app-secrets"]  # 仅允许访问特定 Secret
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secret-reader-binding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: app-service-account
    namespace: production
roleRef:
  kind: Role
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

### 3. 限制 Secret 访问

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  serviceAccountName: limited-sa  # 使用受限的 ServiceAccount
  automountServiceAccountToken: false  # 不自动挂载 API Token
  
  containers:
    - name: app
      image: myapp:v1
      volumeMounts:
        - name: secrets
          mountPath: /etc/secrets
          readOnly: true
      # 限制容器能力
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
  
  volumes:
    - name: secrets
      secret:
        secretName: app-secrets
        # Secret 自动以 tmpfs（内存）挂载，不落盘
```

## 常用命令

```bash
# ConfigMap 操作
kubectl create configmap app-config --from-literal=key1=value1 --from-literal=key2=value2
kubectl create configmap app-config --from-file=application.properties
kubectl create configmap app-config --from-file=config/

kubectl get configmaps
kubectl describe configmap app-config
kubectl get configmap app-config -o yaml

# Secret 操作
kubectl create secret generic app-secrets \
  --from-literal=password=mysecret \
  --from-literal=api-key=12345

kubectl create secret tls tls-secret \
  --cert=cert.pem \
  --key=key.pem

kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=user \
  --docker-password=pass

kubectl get secrets
kubectl describe secret app-secrets
kubectl get secret app-secrets -o jsonpath='{.data.password}' | base64 -d

# 编辑和更新
kubectl edit configmap app-config
kubectl patch configmap app-config --patch '{"data":{"key":"value"}}'

# 验证 Pod 中配置
kubectl exec pod-name -- env | grep DB_
kubectl exec pod-name -- cat /etc/config/application.properties
```

## 应用场景

- **环境配置分离**：开发、测试、生产使用相同的镜像，不同的 ConfigMap
- **敏感信息管理**：数据库密码、API 密钥、TLS 证书的安全存储
- **应用配置热更新**：通过卷挂载实现配置文件的动态更新
- **功能开关管理**：使用 ConfigMap 存储特性标志，动态控制功能启用
- **多租户配置隔离**：不同命名空间使用独立的 ConfigMap 和 Secret
- **CI/CD 集成**：通过命令行工具在部署流水线中创建和更新配置

## 面试要点

1. **Q: ConfigMap 和 Secret 的主要区别是什么？**
   A: (1) 数据敏感性：ConfigMap 存非敏感数据，Secret 存敏感数据；(2) 存储大小：都限制 1MB；(3) 编码方式：ConfigMap 明文存储，Secret Base64 编码；(4) 挂载行为：Secret 默认以 tmpfs 内存挂载；(5) 访问控制：Secret 通常需要更严格的 RBAC 限制。

2. **Q: Secret 的数据在 etcd 中是如何存储的？如何增强安全性？**
   A: 默认使用 Base64 编码（非加密）存储在 etcd 中。增强安全性的方法：(1) 启用 EncryptionConfiguration 进行静态加密；(2) 使用外部 KMS 提供商；(3) 配置 RBAC 限制访问；(4) 启用审计日志；(5) 考虑使用外部 Secrets 管理器（如 Vault）。

3. **Q: ConfigMap 和 Secret 更新后，已挂载的 Pod 会自动更新吗？**
   A: 以卷（Volume）方式挂载的配置会自动更新（有延迟，约 kubelet 同步周期）；以环境变量（env/envFrom）方式注入的配置不会自动更新，需要重启 Pod。Secret 更新后建议进行滚动更新以确保一致性。

4. **Q: 如何安全地管理大规模集群中的 Secret？**
   A: (1) 使用专用工具如 HashiCorp Vault、AWS Secrets Manager、Azure Key Vault；(2) 实现 Secret 轮换机制；(3) 使用 Sealed Secrets 或 External Secrets Operator 进行 GitOps 管理；(4) 启用 etcd 加密；(5) 严格的 RBAC 和网络策略；(6) 定期审计 Secret 访问。

5. **Q: immutable ConfigMap/Secret 有什么优势？**
   A: 设置 immutable: true 后，配置不可修改，具有以下优势：(1) 显著提升性能，kubelet 无需监视变更；(2) 降低 apiserver 负载；(3) 防止意外修改；(4) 适用于不常变更的配置。需要修改时必须删除重建。

6. **Q: 如何在 GitOps 工作流中安全管理 Secret？**
   A: (1) 使用 Sealed Secrets：将 Secret 加密后存储在 Git 中；(2) 使用 External Secrets Operator：引用外部 Secrets 管理器；(3) 使用 SOPS 加密；(4) 在 CI/CD 中动态注入；(5) 避免将 Secret 明文提交到 Git。

7. **Q: projected 卷有什么用途？**
   A: projected 卷允许将多个 ConfigMap、Secret、ServiceAccount Token 挂载到同一个目录，支持更灵活的文件组织。例如将来自不同来源的配置文件聚合到 /app/config 目录，而不必分别挂载多个卷。

## 相关概念

### Cloud & DevOps
- [Kubernetes](../kubernetes.md) - 容器编排平台
- [Pods](./pods.md) - 配置的使用方
- [Deployments](./deployments.md) - 应用部署管理
- [Helm](./helm.md) - 配置模板化管理
- [Vault Integration](../../security/secrets-management.md) - 外部密钥管理

### 系统实现
- [访问控制](../../computer-science/systems/network-security.md) - RBAC 权限管理
- [加密原理](../../security/cryptography.md) - 数据加密基础
- [文件系统](../../computer-science/systems/file-systems.md) - tmpfs 内存文件系统
- [进程安全](../../computer-science/systems/process.md) - 容器安全上下文
