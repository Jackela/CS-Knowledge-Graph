# Helm (Kubernetes 包管理器)

## 简介

**Helm** 是 Kubernetes 的包管理工具，被称为 "Kubernetes 的 apt/yum"。它允许开发者将 Kubernetes 应用打包成 **Chart**（图表/包），实现应用的版本化管理、依赖管理和一键部署。Helm 简化了在 Kubernetes 上定义、安装和升级复杂应用的过程。

## 核心概念

| 概念 | 说明 |
|------|------|
| **Chart** | Helm 包，包含一组 Kubernetes 资源模板和配置 |
| **Release** | Chart 在 Kubernetes 集群中的运行实例，可多次安装同一 Chart 创建多个 Release |
| **Repository** | Chart 的远程或本地存储仓库，用于分享和分发 Charts |
| **values.yaml** | Chart 的默认配置文件，定义可覆盖的变量值 |
| **Templates** | 使用 Go template 语法编写的 Kubernetes 资源 YAML 模板 |
| **Helm Hub** | 官方 Chart 仓库，包含大量预构建的应用 Charts |

## 架构原理

```
┌─────────────────────────────────────────────────────────┐
│                      Helm Client                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  helm repo  │  │ helm search │  │ helm install    │  │
│  │  helm pull  │  │ helm show   │  │ helm upgrade    │  │
│  └─────────────┘  └─────────────┘  │ helm uninstall  │  │
│                                    └─────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP/gRPC
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Helm Repository                        │
│         (Chart Museum / Artifact Hub / OCI)              │
│              Charts 压缩包 (.tgz)                         │
└─────────────────────────────────────────────────────────┘
                          │ helm install/upgrade
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 Kubernetes Cluster                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Tiller (Helm v2) /                  │    │
│  │         Helm SDK in Client (Helm v3)             │    │
│  │                                                   │    │
│  │  Template Rendering → Values Injection → Apply   │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│                          ▼                               │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Release Secret (v3) / ConfigMap (v2)           │    │
│  │  存储 release 状态和修订版本                      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Chart 目录结构

```
mychart/                    # Chart 根目录
├── Chart.yaml              # Chart 元数据（名称、版本、描述、依赖等）
├── values.yaml             # 默认配置值
├── values.schema.json      # values 的 JSON Schema 验证（可选）
├── charts/                 # 依赖的 Charts 目录
│   └── mysql-1.6.9.tgz
├── crds/                   # CustomResourceDefinitions
│   └── crd.yaml
├── templates/              # Kubernetes 资源模板目录
│   ├── _helpers.tpl        # 命名模板和辅助函数
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── serviceaccount.yaml
│   ├── hpa.yaml
│   ├── NOTES.txt           # 安装后的提示信息
│   └── tests/              # 测试 Pod 模板
│       └── test-connection.yaml
└── README.md               # Chart 文档
```

## 实现方式

### Chart.yaml 示例

```yaml
apiVersion: v2              # v2 对应 Helm 3, v1 对应 Helm 2
name: my-webapp
description: A Helm chart for Kubernetes web application
type: application           # application 或 library
version: 1.2.3              # Chart 版本（语义化版本）
appVersion: "2.0.0"         # 应用版本
kubeVersion: ">=1.19.0-0"   # 要求的 K8s 版本
keywords:
  - web
  - frontend
  - nginx
home: https://example.com
sources:
  - https://github.com/example/my-webapp
maintainers:
  - name: John Doe
    email: john@example.com
icon: https://example.com/icon.png

# Chart 依赖
dependencies:
  - name: mysql
    version: "9.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: mysql.enabled
    alias: db
  
  - name: redis
    version: "17.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
```

### values.yaml 示例

```yaml
# 全局配置
global:
  imageRegistry: "registry.example.com"
  storageClass: "fast-ssd"

# 应用副本数
replicaCount: 3

# 镜像配置
image:
  repository: nginx
  tag: "1.25-alpine"
  pullPolicy: IfNotPresent
  pullSecrets: []

# 服务配置
service:
  type: ClusterIP
  port: 80
  targetPort: 8080
  annotations: {}

# Ingress 配置
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt"
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: app-tls
      hosts:
        - app.example.com

# 资源限制
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"

# 自动扩缩容
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

# Pod 安全上下文
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000

# 环境变量
env:
  - name: LOG_LEVEL
    value: "info"
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: database-url

# 持久化存储
persistence:
  enabled: true
  storageClass: "standard"
  accessMode: ReadWriteOnce
  size: 10Gi
  mountPath: /data

# 节点选择和亲和性
nodeSelector: {}
tolerations: []
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
                  - my-webapp
          topologyKey: kubernetes.io/hostname
```

### 模板文件示例 (templates/deployment.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mychart.fullname" . }}
  labels:
    {{- include "mychart.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "mychart.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels:
        {{- include "mychart.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "mychart.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          env:
            {{- toYaml .Values.env | nindent 12 }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          volumeMounts:
            - name: data
              mountPath: {{ .Values.persistence.mountPath }}
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
      volumes:
        - name: data
          {{- if .Values.persistence.enabled }}
          persistentVolumeClaim:
            claimName: {{ include "mychart.fullname" . }}
          {{- else }}
          emptyDir: {}
          {{- end }}
```

### _helpers.tpl 命名模板

```yaml
{{/* 生成完整名称 */}}
{{- define "mychart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/* 生成 Chart 标签 */}}
{{- define "mychart.labels" -}}
helm.sh/chart: {{ include "mychart.chart" . }}
{{ include "mychart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/* 选择器标签 */}}
{{- define "mychart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mychart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

## 常用命令

```bash
# ========== 仓库管理 ==========
# 添加仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add stable https://charts.helm.sh/stable

# 列出已添加的仓库
helm repo list

# 更新仓库索引
helm repo update

# 搜索 Chart
helm search repo nginx
helm search hub prometheus

# ========== Chart 操作 ==========
# 创建新 Chart
helm create mychart

# 打包 Chart
helm package mychart

# 验证 Chart
helm lint mychart

# 查看 Chart 信息
helm show chart bitnami/mysql
helm show values bitnami/mysql
helm show readme bitnami/mysql

# 模板渲染（测试，不实际部署）
helm template mychart
helm template mychart --values custom-values.yaml

# ========== Release 管理 ==========
# 安装 Chart
helm install my-release bitnami/mysql
helm install my-release ./mychart
helm install my-release ./mychart --values custom-values.yaml
helm install my-release ./mychart --set replicaCount=5,image.tag=latest

# 查看 Release
helm list
helm list --all-namespaces
helm status my-release

# 升级 Release
helm upgrade my-release ./mychart
helm upgrade --install my-release ./mychart  # 如果不存在则安装
helm upgrade my-release bitnami/mysql --version 9.0.0

# 回滚 Release
helm rollback my-release 1  # 回滚到修订版本 1
helm history my-release     # 查看修订历史

# 卸载 Release
helm uninstall my-release
helm delete my-release --purge  # Helm 2 需要 --purge

# ========== 调试 ==========
# 获取 Release 的 values
helm get values my-release
helm get values my-release --all  # 包含默认值

# 获取 Release 的 manifest
helm get manifest my-release

# 测试 Release
helm test my-release
```

## Helm 3 vs Helm 2

| 特性 | Helm 2 | Helm 3 |
|------|--------|--------|
| 架构 | Client-Server (Tiller) | 纯客户端 |
| 安全性 | Tiller 权限过大 | 使用 kubeconfig 权限 |
| 存储 | ConfigMap | Secret |
| 库 Chart | 不支持 | 支持 library 类型 |
| 发布日期 | 2015 | 2019 |
| 维护状态 | 已停止维护 | 推荐使用 |

## 应用场景

1. **标准化应用部署**：将应用配置模板化，支持多环境部署（dev/staging/prod）
2. **依赖管理**：自动安装应用依赖的数据库、缓存等服务
3. **版本控制**：追踪应用部署历史，支持快速回滚
4. **配置复用**：通过 values.yaml 覆盖，一套模板支持多种配置
5. **CI/CD 集成**：在流水线中自动部署和升级应用
6. **多租户管理**：同一 Chart 可安装多个 Release，服务不同团队

## 最佳实践

```yaml
# 1. 语义化版本控制
version: 1.2.3  # MAJOR.MINOR.PATCH

# 2. 合理的默认值
# values.yaml 中设置适合大多数场景的默认值

# 3. 使用命名模板
# 在 _helpers.tpl 中定义可复用的模板片段

# 4. 资源限制
resources:
  requests:
    memory: "64Mi"
    cpu: "50m"
  limits:
    memory: "128Mi"
    cpu: "100m"

# 5. 健康检查探针
livenessProbe:
  httpGet:
    path: /health
    port: http
readinessProbe:
  httpGet:
    path: /ready
    port: http

# 6. 安全上下文
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
```

## 面试要点

**Q: Helm 3 相比 Helm 2 有什么主要改进？**
A: (1) 移除 Tiller 服务端组件，改为纯客户端架构，使用 kubeconfig 权限，更安全；(2) 状态存储从 ConfigMap 改为 Secret；(3) 支持 library 类型的 Chart；(4) 支持 JSON Schema 验证 values；(5) 改进了 CRD 管理方式。

**Q: Chart、Release、Repository 之间的关系是什么？**
A: Chart 是应用包模板；Repository 是存储和分发 Chart 的仓库；Release 是 Chart 在集群中的运行实例。一个 Chart 可以从 Repository 下载，安装多次产生多个 Release。

**Q: Helm 如何实现配置覆盖？**
A: 通过 values.yaml 文件层级覆盖：(1) Chart 内置的 values.yaml；(2) 父 Chart 通过 dependencies 传递的值；(3) 命令行 -f 指定的 values 文件；(4) 命令行 --set 设置的值。优先级从低到高。

**Q: helm upgrade 和 helm rollback 的原理是什么？**
A: Helm 每次操作会创建一个新的 Revision，将 Release 状态存储在 Secret（Helm 3）中。upgrade 会创建新 Revision 并应用变更；rollback 会读取历史 Revision 的配置，重新应用到当前。

**Q: 如何在 Helm 模板中使用条件判断？**
A: 使用 Go template 语法：`{{- if .Values.ingress.enabled }}...{{- end }}`，支持 if/else if/else、eq、ne、lt、gt 等比较操作，以及 and、or 逻辑运算。

**Q: Helm 如何处理 Chart 依赖？**
A: 在 Chart.yaml 中声明 dependencies，运行 `helm dependency update` 下载依赖到 charts/ 目录。支持条件启用（condition）、别名（alias）覆盖子 Chart 的 values。

## 相关概念

### Cloud & DevOps
- [Kubernetes](../kubernetes.md) - 容器编排平台
- [Pods](./pods.md) - Helm 部署的基本单元
- [Deployments](./deployments.md) - 无状态应用部署
- [Services](./services.md) - 服务发现和负载均衡
- [ConfigMaps & Secrets](./configmaps-secrets.md) - 配置管理

### 系统实现
- [模板引擎](../../software-engineering/design-patterns/template-method.md) - 模板渲染原理
- [CI/CD](./cicd.md) - 持续集成与部署
- [GitOps](./gitops.md) - Git 驱动的部署模式
