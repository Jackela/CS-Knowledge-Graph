# Kubernetes Pods (K8s 容器组)

## 简介

**Pod** 是 Kubernetes 中最小的可部署单元，是一组共享网络和存储的容器的集合。Pod 封装了应用容器、存储资源、网络 IP 以及管理容器运行方式的选项。每个 Pod 有唯一的 IP 地址，内部容器通过 localhost 通信，共享相同的存储卷。

## 核心概念

- **容器（Containers）**：Pod 中运行的实际应用进程，通常一个 Pod 运行一个主容器
- **Init 容器**：在应用容器启动前运行的初始化容器，按顺序执行
- **Pause 容器**：Pod 的基础容器，维护网络命名空间，用户不可见
- **共享存储（Volumes）**：Pod 内所有容器可访问的共享存储卷
- **网络命名空间**：Pod 内容器共享 IP、端口空间和网络接口
- **生命周期**：Pending → Running → Succeeded/Failed → Unknown
- **重启策略**：Always、OnFailure、Never

## Pod 架构

```
┌─────────────────────────────────────────────────────┐
│                       Pod                            │
│  ┌─────────────────────────────────────────────┐    │
│  │          Pause Container (infra)             │    │
│  │         IP: 10.244.1.5                       │    │
│  │         Network Namespace                    │    │
│  └─────────────────────────────────────────────┘    │
│           │                 │                       │
│  ┌────────▼────────┐ ┌──────▼────────┐             │
│  │   Container A   │ │  Container B  │             │
│  │   (Main App)    │ │  (Sidecar)    │             │
│  │                 │ │               │             │
│  │  localhost:8080 │ │  localhost:9090             │
│  └─────────────────┘ └───────────────┘             │
│           │                 │                       │
│  ┌────────▼─────────────────▼────────┐             │
│  │       Shared Volumes               │             │
│  │  /data, /config, /logs             │             │
│  └────────────────────────────────────┘             │
└─────────────────────────────────────────────────────┘
```

## 实现方式

### 基础 Pod 配置

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: simple-pod
  namespace: default
  labels:
    app: web
    tier: frontend
    version: v1
spec:
  containers:
    - name: web-server
      image: nginx:alpine
      ports:
        - containerPort: 80
          name: http
          protocol: TCP
      resources:
        requests:
          memory: "64Mi"
          cpu: "250m"
        limits:
          memory: "128Mi"
          cpu: "500m"
```

### 多容器 Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
  labels:
    app: web-logger
spec:
  containers:
    - name: web-server
      image: nginx:alpine
      ports:
        - containerPort: 80
      volumeMounts:
        - name: shared-logs
          mountPath: /var/log/nginx
      resources:
        requests:
          memory: "128Mi"
          cpu: "250m"
        limits:
          memory: "256Mi"
          cpu: "500m"
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

    - name: log-aggregator
      image: fluentd:v1.16
      volumeMounts:
        - name: shared-logs
          mountPath: /var/log/nginx
          readOnly: true
        - name: fluentd-config
          mountPath: /fluentd/etc
      resources:
        requests:
          memory: "64Mi"
          cpu: "100m"
        limits:
          memory: "128Mi"
          cpu: "200m"

  volumes:
    - name: shared-logs
      emptyDir: {}
    - name: fluentd-config
      configMap:
        name: fluentd-config
```

### Init 容器配置

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  initContainers:
    - name: init-myservice
      image: busybox:1.36
      command:
        - sh
        - -c
        - |
          until nslookup myservice; do
            echo waiting for myservice;
            sleep 2;
          done
      resources:
        requests:
          memory: "32Mi"
          cpu: "50m"

    - name: init-mydb
      image: busybox:1.36
      command:
        - sh
        - -c
        - |
          until nc -z mydb 3306; do
            echo waiting for mydb;
            sleep 2;
          done
      resources:
        requests:
          memory: "32Mi"
          cpu: "50m"

  containers:
    - name: myapp
      image: myapp:v1
      ports:
        - containerPort: 8080
      env:
        - name: DB_HOST
          value: mydb
        - name: SERVICE_URL
          value: http://myservice
      resources:
        requests:
          memory: "128Mi"
          cpu: "250m"
        limits:
          memory: "256Mi"
          cpu: "500m"
```

### 带有配置的 Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-pod
spec:
  containers:
    - name: app
      image: myapp:v1
      ports:
        - containerPort: 8080
      env:
        # 直接设置环境变量
        - name: ENVIRONMENT
          value: "production"
        
        # 从 ConfigMap 引用
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: database.url
        
        # 从 Secret 引用
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: api.key
        
        # 注入所有 ConfigMap 键值
        - name: APP_CONFIG
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: app.config

      envFrom:
        # 注入整个 ConfigMap
        - configMapRef:
            name: app-config
        # 注入整个 Secret
        - secretRef:
            name: app-secrets

      volumeMounts:
        # 挂载 ConfigMap 为文件
        - name: config-vol
          mountPath: /etc/config
        
        # 挂载 Secret 为文件
        - name: secret-vol
          mountPath: /etc/secrets
          readOnly: true
        
        # 挂载 PVC
        - name: data-vol
          mountPath: /data

  volumes:
    - name: config-vol
      configMap:
        name: app-config
        items:
          - key: app.properties
            path: application.properties
    
    - name: secret-vol
      secret:
        secretName: app-secrets
        items:
          - key: tls.crt
            path: cert.pem
          - key: tls.key
            path: key.pem
    
    - name: data-vol
      persistentVolumeClaim:
        claimName: app-data-pvc
```

### 节点选择与亲和性

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: affinity-pod
spec:
  nodeSelector:
    disktype: ssd
    environment: production
  
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: kubernetes.io/os
                operator: In
                values:
                  - linux
              - key: node-type
                operator: In
                values:
                  - compute
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          preference:
            matchExpressions:
              - key: zone
                operator: In
                values:
                  - zone-a
    
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: app
                operator: In
                values:
                  - cache
          topologyKey: kubernetes.io/hostname
    
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchExpressions:
                - key: app
                  operator: In
                  values:
                    - web
            topologyKey: kubernetes.io/hostname

  tolerations:
    - key: "dedicated"
      operator: "Equal"
      value: "web"
      effect: "NoSchedule"
    - key: "special"
      operator: "Exists"
      effect: "NoExecute"
      tolerationSeconds: 3600

  containers:
    - name: app
      image: myapp:v1
```

## Pod 生命周期

```
Pending → Running → Succeeded/Failed
   ↓         ↓           ↓
Creating  Ready      Terminating
   ↓         ↓           ↓
Scheduled Containers    Unknown
          Running
```

### 容器状态

```yaml
containerStatuses:
  - name: web-server
    state:
      running:
        startedAt: "2024-01-15T10:30:00Z"
    lastState:
      terminated:
        exitCode: 137
        reason: OOMKilled
        startedAt: "2024-01-15T10:25:00Z"
        finishedAt: "2024-01-15T10:30:00Z"
    ready: true
    restartCount: 1
```

## 健康检查探针

### 存活探针（Liveness）

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
    httpHeaders:
      - name: Custom-Header
        value: liveness
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
  successThreshold: 1
```

### 就绪探针（Readiness）

```yaml
readinessProbe:
  tcpSocket:
    port: 3306
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
  successThreshold: 1
```

### 启动探针（Startup）

```yaml
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 30  # 30 * 5 = 150s 最大启动时间
```

## 安全上下文

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
    sysctls:
      - name: net.core.somaxconn
        value: "1024"
  
  containers:
    - name: app
      image: myapp:v1
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
          add:
            - NET_BIND_SERVICE
        seLinuxOptions:
          level: "s0:c123,c456"
      volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /var/cache
  
  volumes:
    - name: tmp
      emptyDir: {}
    - name: cache
      emptyDir: {}
```

## 面试要点

1. **Q: Pod 和容器的区别是什么？**
   A: 容器是应用运行的隔离环境；Pod 是 Kubernetes 的最小调度单元，可包含一个或多个容器，这些容器共享网络和存储。Pod 是对容器的封装，增加了编排能力。

2. **Q: 为什么 Kubernetes 不直接调度容器而是调度 Pod？**
   A: Pod 提供了必要的共享机制（网络、存储）和生命周期管理。某些场景需要多个紧密耦合的容器协同工作（如主应用 + Sidecar），Pod 是这种协作的基本单位。

3. **Q: Init 容器和普通容器有什么区别？**
   A: Init 容器按顺序执行，全部成功完成后普通容器才会启动；Init 容器不支持就绪探针、存活探针；每个 Init 容器必须成功退出才会执行下一个。

4. **Q: Pod 的三种探针有什么区别？**
   A: Liveness 检测容器是否存活，失败则重启容器；Readiness 检测容器是否准备好接收流量，失败则从 Service 端点移除；Startup 用于慢启动容器，禁用其他探针直到成功。

5. **Q: Pod 的 restartPolicy 有哪些选项？**
   A: Always（默认）：无论退出码如何都重启；OnFailure：退出码非0时重启；Never：不重启。适用于 Job/CronJob 等一次性任务。

6. **Q: 如何限制 Pod 的资源使用？**
   A: 通过 resources.requests 设置调度保证的资源，resources.limits 设置最大使用上限。超出 CPU limit 会被节流，超出内存 limit 会被 OOMKilled。

7. **Q: Pod 的 QoS 等级有哪些？如何确定？**
   A: Guaranteed（保证）：所有容器都设置了 requests 和 limits，且相等；Burstable（可突发）：至少一个容器设置了 requests；BestEffort（尽力）：没有设置 requests 和 limits。驱逐时按 BestEffort → Burstable → Guaranteed 的顺序。

## 相关概念

### Cloud & DevOps
- [Kubernetes](../kubernetes.md) - 容器编排平台
- [Deployments](./deployments.md) - Pod 控制器
- [Services](./services.md) - Pod 网络暴露
- [ConfigMaps & Secrets](./configmaps-secrets.md) - 配置管理
- [Storage](./storage.md) - 持久化存储

### 系统实现
- [进程管理](../../computer-science/systems/process.md) - 容器进程原理
- [命名空间](../../computer-science/systems/os.md) - Linux 命名空间隔离
- [Cgroups](../../computer-science/systems/os.md) - 资源限制实现
- [内存管理](../../computer-science/systems/memory-management.md) - 容器内存管理
