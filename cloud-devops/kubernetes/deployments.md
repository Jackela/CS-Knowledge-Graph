# Kubernetes Deployments (K8s 部署)

## 简介

**Deployment** 是 Kubernetes 中用于声明式管理 Pod 副本集的控制器。它提供了应用的声明式更新能力，支持滚动更新、回滚、扩缩容等功能。Deployment 通过管理 ReplicaSet 来间接管理 Pod，确保指定数量的 Pod 副本始终运行，并在更新时以受控方式替换旧版本 Pod。

## 核心概念

- **副本集（ReplicaSet）**：确保指定数量的 Pod 副本运行，提供基本的扩缩容和自愈能力
- **滚动更新（Rolling Update）**：逐步替换旧版本 Pod，实现零停机部署
- **回滚（Rollback）**：回退到之前的稳定版本
- **修订版本（Revision）**：每次更新都会创建一个新的 ReplicaSet 并记录为历史版本
- **策略（Strategy）**：定义更新方式，如 RollingUpdate 或 Recreate
- **进度截止时间（Progress Deadline）**：标记更新失败的超时时间
- **暂停/恢复（Pause/Resume）**：暂停更新以便进行多批次修改

## Deployment 架构

```
┌──────────────────────────────────────────────────────┐
│                    Deployment                         │
│               (Declarative Update)                    │
└──────────────────┬───────────────────────────────────┘
                   │ manages
        ┌──────────┴──────────┐
        ▼                     ▼
┌───────────────┐    ┌───────────────┐
│  ReplicaSet   │    │  ReplicaSet   │
│   (v1.0)      │    │   (v1.1)      │
│  revision: 1  │    │  revision: 2  │
└───────┬───────┘    └───────┬───────┘
        │                     │
    ┌───┴───┐             ┌───┴───┐
    ▼       ▼             ▼       ▼
┌─────┐ ┌─────┐       ┌─────┐ ┌─────┐
│Pod 1│ │Pod 2│       │Pod 3│ │Pod 4│
│v1.0 │ │v1.0 │       │v1.1 │ │v1.1 │
└─────┘ └─────┘       └─────┘ └─────┘
```

## 实现方式

### 基础 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
  namespace: default
  labels:
    app: web
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
        version: v1
    spec:
      containers:
        - name: web-server
          image: nginx:1.25-alpine
          ports:
            - containerPort: 80
              name: http
          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "128Mi"
              cpu: "200m"
          livenessProbe:
            httpGet:
              path: /health
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 5
```

### 滚动更新策略配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
  namespace: production
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2          # 更新时可超出副本数的最大数量
      maxUnavailable: 1    # 更新时可不可用的最大数量
  minReadySeconds: 30      # Pod 就绪后等待时间，确保服务稳定
  progressDeadlineSeconds: 600  # 更新进度超时时间
  revisionHistoryLimit: 10      # 保留的历史版本数
  
  selector:
    matchLabels:
      app: api
  
  template:
    metadata:
      labels:
        app: api
        version: "2.1.0"
    spec:
      containers:
        - name: api-server
          image: myapp/api:v2.1.0
          ports:
            - containerPort: 8080
          env:
            - name: LOG_LEVEL
              value: "info"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: database-url
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - api
                topologyKey: kubernetes.io/hostname
```

### 蓝绿部署配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
  labels:
    app: myapp
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
        - name: app
          image: myapp:v1
          ports:
            - containerPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
  labels:
    app: myapp
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
        - name: app
          image: myapp:v2
          ports:
            - containerPort: 8080
```

### 金丝雀部署配置

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
  labels:
    app: myapp
    track: stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
      track: stable
  template:
    metadata:
      labels:
        app: myapp
        track: stable
    spec:
      containers:
        - name: app
          image: myapp:v1
          ports:
            - containerPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
  labels:
    app: myapp
    track: canary
spec:
  replicas: 1  # 10% 流量
  selector:
    matchLabels:
      app: myapp
      track: canary
  template:
    metadata:
      labels:
        app: myapp
        track: canary
    spec:
      containers:
        - name: app
          image: myapp:v2
          ports:
            - containerPort: 8080
```

### 有状态应用部署（配合 PVC）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stateful-app
  namespace: default
spec:
  replicas: 1  # 单副本避免数据冲突
  strategy:
    type: Recreate  # 先停止旧 Pod 再创建新 Pod
  selector:
    matchLabels:
      app: stateful-app
  template:
    metadata:
      labels:
        app: stateful-app
    spec:
      containers:
        - name: app
          image: postgres:15-alpine
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: myapp
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: password
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: postgres-pvc
```

### 带有 Init 容器的 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-with-init
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      initContainers:
        - name: init-db-schema
          image: myapp/migrate:latest
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: url
          command:
            - /bin/sh
            - -c
            - |
              echo "Running database migrations..."
              migrate -path /migrations -database "$DATABASE_URL" up
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "200m"
        
        - name: init-cache
          image: busybox:1.36
          command:
            - sh
            - -c
            - |
              until nc -z redis 6379; do
                echo "Waiting for Redis..."
                sleep 2
              done
      
      containers:
        - name: web
          image: myapp/web:latest
          ports:
            - containerPort: 8080
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
```

## 常用命令

```bash
# 创建 Deployment
kubectl apply -f deployment.yaml

# 查看 Deployment
kubectl get deployments
kubectl get deploy -o wide
kubectl describe deployment web-deployment

# 扩缩容
kubectl scale deployment web-deployment --replicas=5
kubectl autoscale deployment web-deployment --min=2 --max=10 --cpu-percent=80

# 更新镜像
kubectl set image deployment/web-deployment web-server=nginx:1.26-alpine
kubectl edit deployment web-deployment

# 查看滚动更新状态
kubectl rollout status deployment/web-deployment
kubectl rollout history deployment/web-deployment

# 回滚
kubectl rollout undo deployment/web-deployment
kubectl rollout undo deployment/web-deployment --to-revision=2

# 暂停/恢复更新
kubectl rollout pause deployment/web-deployment
kubectl rollout resume deployment/web-deployment

# 查看 Pod 分布
kubectl get pods -l app=web -o wide
```

## 滚动更新策略详解

### maxSurge 和 maxUnavailable

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%        # 可以是绝对数值或百分比
    maxUnavailable: 25%  # 可以是绝对数值或百分比
```

- **maxSurge**：更新过程中可以创建的超出期望副本数的 Pod 数量
  - 设置值：确保有足够的资源进行更新
  - 设置百分比：根据副本数动态计算

- **maxUnavailable**：更新过程中可以不可用的 Pod 数量
  - 设置为 0：确保所有旧 Pod 都在新 Pod 就绪后才终止
  - 设置值：允许一定程度的容量损失以换取更快的更新速度

### Recreate 策略

```yaml
strategy:
  type: Recreate
```

- 先终止所有旧 Pod，再创建新 Pod
- 适用于不接受同时运行多个版本的应用（如数据库）
- 会有短暂的停机时间

## 面试要点

1. **Q: Deployment 和 ReplicaSet 的关系是什么？**
   A: Deployment 管理 ReplicaSet，ReplicaSet 管理 Pod。Deployment 通过创建新的 ReplicaSet 来实现滚动更新，保留旧 ReplicaSet 用于回滚。这是分层控制的设计模式。

2. **Q: 滚动更新的 maxSurge 和 maxUnavailable 如何配合使用？**
   A: maxSurge 控制可额外创建的 Pod 数量，maxUnavailable 控制可容忍的不可用 Pod 数量。两者之和决定了更新过程中的资源需求和可用性保证。例如 replicas=10, maxSurge=2, maxUnavailable=1，更新时最多有 12 个 Pod，最少有 9 个可用。

3. **Q: 如何实现零停机部署？**
   A: (1) 使用 RollingUpdate 策略；(2) 配置合适的 maxSurge 和 maxUnavailable；(3) 确保 Pod 有就绪探针；(4) 设置 minReadySeconds 确保服务稳定；(5) 使用 Service 的滚动更新配合；(6) 考虑优雅终止（preStop hook 和 terminationGracePeriodSeconds）。

4. **Q: Deployment 回滚是如何实现的？**
   A: 每次更新会创建新的 ReplicaSet 并保留旧的（受 revisionHistoryLimit 限制）。回滚时将当前 ReplicaSet 缩容到 0，将目标版本的 ReplicaSet 扩容到期望副本数。回滚本身也会创建一个新的 revision。

5. **Q: 什么情况下应该使用 Recreate 而不是 RollingUpdate？**
   A: 当应用不能同时运行多个版本时（如数据库 schema 变更）、资源受限无法同时运行新旧版本、或者应用启动时需要独占资源（如端口绑定）。

6. **Q: 如何监控 Deployment 的更新进度？**
   A: 使用 kubectl rollout status 查看实时进度；通过 progressDeadlineSeconds 设置超时检测；查看 Pod 状态和资源事件；使用 metrics-server 监控资源使用；结合 Prometheus/Grafana 进行可视化监控。

7. **Q: Deployment 的状态有哪些？如何进行故障排查？**
   A: Progressing（更新进行中）、Complete（更新完成）、Failed（更新失败）。排查方法：kubectl describe deployment 查看 Events；kubectl get pods 查看 Pod 状态；kubectl logs 查看容器日志；检查资源配额和节点资源；验证镜像拉取和配置正确性。

## 相关概念

### Cloud & DevOps
- [Kubernetes](../kubernetes.md) - 容器编排平台
- [Pods](./pods.md) - Deployment 管理的对象
- [Services](./services.md) - 暴露 Deployment
- [ConfigMaps & Secrets](./configmaps-secrets.md) - 配置注入
- [StatefulSet](./storage.md) - 有状态应用管理

### 系统实现
- [进程管理](../../computer-science/systems/process.md) - 应用进程管理
- [调度算法](../../computer-science/systems/scheduling.md) - Pod 调度原理
- [高可用架构](../../computer-science/distributed-systems/load-balancing.md) - 应用高可用设计
- [版本控制](../../software-engineering/git-basics.md) - 部署版本管理
