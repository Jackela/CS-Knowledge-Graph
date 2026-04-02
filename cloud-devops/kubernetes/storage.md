# Kubernetes 存储 (K8s Storage)

## 简介

**Kubernetes 存储系统** 为容器化应用提供数据持久化能力。与容器本身的临时存储不同，Kubernetes 提供了从临时存储到持久化存储的完整解决方案，支持有状态应用（Stateful Applications）的运行。存储系统解决了容器重启或迁移后的数据保留问题，是运行数据库、消息队列等有状态服务的基础。

## 核心概念

| 概念 | 英文 | 说明 |
|------|------|------|
| **Volume** | 卷 | Pod 级别的共享存储，生命周期与 Pod 相同 |
| **PersistentVolume (PV)** | 持久卷 | 集群级别的存储资源，由管理员配置 |
| **PersistentVolumeClaim (PVC)** | 持久卷声明 | 用户对存储的请求，绑定到 PV |
| **StorageClass** | 存储类 | 定义动态存储供给的参数和 provisioner |
| **StatefulSet** | 有状态集 | 管理有状态应用的 workload，提供稳定的网络标识和存储 |
| **CSI** | 容器存储接口 | 标准化的存储插件接口，允许第三方存储系统接入 |

## 存储类型对比

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes 存储体系                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │  临时存储    │    │  半持久化    │    │  持久化存储  │     │
│   │  Ephemeral   │    │  Semi-Persist│    │  Persistent  │     │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
│          │                   │                   │              │
│          ▼                   ▼                   ▼              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │ emptyDir     │    │ hostPath     │    │ PV/PVC       │     │
│   │ configMap    │    │ local PV     │    │ StorageClass │     │
│   │ secret       │    │              │    │ CSI Driver   │     │
│   │ downwardAPI  │    │              │    │ Cloud Disk   │     │
│   └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                                 │
│   容器重启数据丢失      节点相关                  独立于 Pod     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 实现方式

### 1. 临时卷 (emptyDir)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-demo
spec:
  containers:
    - name: writer
      image: busybox
      command: ["sh", "-c", "while true; do echo $(date) >> /data/log.txt; sleep 5; done"]
      volumeMounts:
        - name: cache-volume
          mountPath: /data
    
    - name: reader
      image: busybox
      command: ["sh", "-c", "tail -f /data/log.txt"]
      volumeMounts:
        - name: cache-volume
          mountPath: /data
  
  volumes:
    - name: cache-volume
      emptyDir:
        medium: Memory          # 使用内存（tmpfs），默认使用磁盘
        sizeLimit: 256Mi        # 限制大小
```

### 2. ConfigMap 和 Secret 卷

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        # 挂载 ConfigMap
        - name: config-vol
          mountPath: /etc/config
        # 挂载单个文件
        - name: nginx-conf
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf
        # 挂载 Secret
        - name: secret-vol
          mountPath: /etc/secrets
          readOnly: true
  
  volumes:
    - name: config-vol
      configMap:
        name: app-config
        items:
          - key: app.properties
            path: application.properties
    
    - name: nginx-conf
      configMap:
        name: nginx-config
        items:
          - key: nginx.conf
            path: nginx.conf
    
    - name: secret-vol
      secret:
        secretName: tls-secret
        items:
          - key: tls.crt
            path: cert.pem
          - key: tls.key
            path: key.pem
        defaultMode: 0400
```

### 3. PersistentVolume (PV) 定义

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs
  labels:
    type: nfs
    env: production
spec:
  capacity:
    storage: 10Gi                    # 存储容量
  volumeMode: Filesystem             # Filesystem 或 Block
  accessModes:
    - ReadWriteMany                  # RWO/RWX/ROX
  persistentVolumeReclaimPolicy: Retain  # Retain/Recycle/Delete
  storageClassName: nfs-storage
  mountOptions:
    - hard
    - nfsvers=4.1
  nfs:
    server: 192.168.1.100
    path: /exports/data
---
# AWS EBS 示例
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-ebs
spec:
  capacity:
    storage: 50Gi
  accessModes:
    - ReadWriteOnce
  awsElasticBlockStore:
    volumeID: vol-0a1b2c3d4e5f6g7h8
    fsType: ext4
---
# hostPath 示例（仅单节点测试使用）
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-hostpath
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /data/pv-data
    type: DirectoryOrCreate
```

### 4. PersistentVolumeClaim (PVC)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-data-pvc
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard        # 指定 StorageClass
  volumeName: pv-nfs               # 可选：绑定特定 PV
  selector:
    matchLabels:
      type: nfs
      env: production
```

### 5. StorageClass（动态供给）

```yaml
# AWS EBS gp3 StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
  kmsKeyId: "arn:aws:kms:us-east-1:123456789:key/abcd1234"
reclaimPolicy: Delete              # Delete 或 Retain
allowVolumeExpansion: true         # 允许扩容
mountOptions:
  - debug
volumeBindingMode: WaitForFirstConsumer  # Immediate 或 WaitForFirstConsumer
allowedTopologies:
  - matchLabelExpressions:
      - key: topology.ebs.csi.aws.com/zone
        values:
          - us-east-1a
          - us-east-1b
---
# NFS 动态供给
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-client
provisioner: cluster.local/nfs-subdir-external-provisioner
parameters:
  archiveOnDelete: "false"
reclaimPolicy: Delete
allowVolumeExpansion: true
```

### 6. Deployment 使用 PVC

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-deployment
spec:
  replicas: 1                      # 单副本，避免数据冲突
  strategy:
    type: Recreate                 # 先停止旧 Pod 再创建新 Pod
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15-alpine
          env:
            - name: POSTGRES_DB
              value: myapp
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: password
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-pvc
```

### 7. StatefulSet（有状态应用）

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-sts
spec:
  serviceName: mysql-headless      # 必须配合 Headless Service
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          ports:
            - containerPort: 3306
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: root-password
          volumeMounts:
            - name: data
              mountPath: /var/lib/mysql
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
  # 关键：volumeClaimTemplates 为每个 Pod 创建独立 PVC
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: ebs-gp3
        resources:
          requests:
            storage: 20Gi
---
# 配套 Headless Service
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
spec:
  clusterIP: None                  # Headless 服务
  selector:
    app: mysql
  ports:
    - port: 3306
```

### 8. Pod 直接使用 CSI 卷

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: csi-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        - name: csi-volume
          mountPath: /data
  volumes:
    - name: csi-volume
      csi:
        driver: ebs.csi.aws.com
        volumeAttributes:
          type: gp3
          encrypted: "true"
        volumeHandle: vol-abc123
        fsType: ext4
```

## 访问模式 (Access Modes)

| 模式 | 缩写 | 说明 | 典型存储 |
|------|------|------|----------|
| ReadWriteOnce | RWO | 单节点读写 | EBS、Azure Disk、hostPath |
| ReadOnlyMany | ROX | 多节点只读 | NFS、EFS、Azure Files |
| ReadWriteMany | RWX | 多节点读写 | NFS、EFS、Azure Files、CephFS |
| ReadWriteOncePod | RWOP | 单 Pod 读写 (1.22+) | 特定 CSI 驱动 |

## 回收策略 (Reclaim Policy)

```
┌─────────────────────────────────────────────────────────────┐
│                    PV 回收策略                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │  Retain  │    │  Delete  │    │ Recycle  │             │
│   │ (保留)   │    │ (删除)   │    │ (回收)   │             │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘             │
│        │               │               │                    │
│        ▼               ▼               ▼                    │
│   PVC 删除后       PVC 删除后       PVC 删除后               │
│   PV 保留，      PV 和底层存储   清除数据，                  │
│   状态为 Released   都被删除     PV 变为 Available          │
│   需手动回收                                                │
│                                                             │
│   生产环境推荐     动态供给默认    已弃用，                   │
│                  测试环境可用    使用动态供给替代            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 存储扩容

```yaml
# 1. StorageClass 允许扩容
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expandable-storage
provisioner: ebs.csi.aws.com
allowVolumeExpansion: true

# 2. 修改 PVC 大小
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi    # 从 10Gi 扩容到 20Gi
```

```bash
# 在线扩容（CSI 支持）
kubectl patch pvc my-pvc -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# 查看扩容状态
kubectl get pvc my-pvc
kubectl describe pvc my-pvc
```

## 常用命令

```bash
# ========== PV 操作 ==========
kubectl get pv
kubectl get pv -o wide
kubectl describe pv <pv-name>
kubectl delete pv <pv-name>

# ========== PVC 操作 ==========
kubectl get pvc
kubectl get pvc -n <namespace>
kubectl describe pvc <pvc-name>
kubectl delete pvc <pvc-name>

# 查看 PVC 绑定状态
kubectl get pvc --all-namespaces

# ========== StorageClass ==========
kubectl get storageclass
kubectl get sc
kubectl describe sc <sc-name>
kubectl delete sc <sc-name>

# 设置默认 StorageClass
kubectl patch storageclass <sc-name> -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# ========== StatefulSet 存储 ==========
# 查看 StatefulSet 创建的 PVC
kubectl get pvc -l app=mysql

# 查看 Pod 与 PVC 的对应关系
kubectl get pod -o yaml | grep -A 5 claimName
```

## 面试要点

**Q: PV 和 PVC 的关系是什么？**
A: PV（PersistentVolume）是集群级别的存储资源，由管理员预先配置或动态供给；PVC（PersistentVolumeClaim）是用户对存储的请求声明。PVC 会绑定到满足条件的 PV，Pod 通过 PVC 使用存储。这种分离实现了存储的供给和使用的解耦。

**Q: StorageClass 的作用是什么？**
A: StorageClass 定义了动态存储供给的类别，包含 provisioner（供给者）、parameters（参数）、reclaimPolicy（回收策略）等。管理员可以定义多个 StorageClass（如 ssd、standard、archive），用户根据需求选择，实现按需自动创建 PV。

**Q: StatefulSet 与 Deployment 在存储方面有什么区别？**
A: (1) StatefulSet 使用 volumeClaimTemplates 为每个 Pod 创建独立的 PVC，Pod 重新调度后仍能绑定到原来的存储；(2) StatefulSet 配合 Headless Service 提供稳定的网络标识（如 mysql-0.mysql-headless）；(3) Deployment 的所有副本共享同一个 PVC（RWM 模式）或使用 emptyDir，不适合有状态应用。

**Q: emptyDir 和 hostPath 有什么区别？**
A: emptyDir 在 Pod 创建时初始化，Pod 删除时清空，可用于容器间共享数据；hostPath 挂载宿主机目录，数据持久化在节点上，Pod 跨节点调度后无法访问原数据。hostPath 一般仅用于单节点测试或需要访问宿主机资源的特殊场景。

**Q: 如何在 Kubernetes 中实现共享存储？**
A: 使用支持 RWX（ReadWriteMany）访问模式的存储，如 NFS、EFS、Azure Files、CephFS。创建对应的 PV/PVC，多个 Pod 可以同时挂载并读写。

**Q: volumeBindingMode: WaitForFirstConsumer 有什么作用？**
A: 延迟 PV 的绑定和供给，直到 Pod 被调度到节点后才创建/绑定 PV。适用于拓扑感知的存储（如本地 SSD、区域化云盘），确保存储创建在 Pod 所在的可用区或节点。

**Q: CSI 是什么？**
A: CSI（Container Storage Interface）是 Kubernetes 的标准存储插件接口，允许第三方存储厂商开发驱动接入 K8s，无需修改 K8s 核心代码。主流云厂商和存储系统都提供 CSI 驱动。

## 相关概念

### Cloud & DevOps
- [Kubernetes](../kubernetes.md) - 容器编排平台
- [Pods](./pods.md) - 存储的使用者
- [Deployments](./deployments.md) - 无状态应用部署
- [StatefulSet](./statefulset.md) - 有状态应用部署
- [ConfigMaps & Secrets](./configmaps-secrets.md) - 配置数据存储

### 计算机科学
- [文件系统](../../computer-science/systems/file-systems.md) - 存储底层原理
- [磁盘 I/O](../../computer-science/systems/os.md) - 存储性能基础
- [数据库](../../computer-science/databases/) - 持久化数据管理
