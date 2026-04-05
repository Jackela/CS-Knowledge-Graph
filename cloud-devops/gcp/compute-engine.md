# 计算引擎 (Compute Engine)

## 简介

Google Compute Engine 是 Google Cloud Platform (GCP) 提供的基础设施即服务 (IaaS)，允许用户在 Google 的基础设施上创建和运行虚拟机实例。提供高性能、可扩展、安全的计算资源，支持多种机器类型和操作系统。

## 核心概念

### 虚拟机实例 (VM Instances)
- **机器类型**: 预定义（标准、高内存、高 CPU）和自定义机器类型
- **操作系统**: Linux (Debian, Ubuntu, CentOS, RHEL, SUSE) 和 Windows Server
- **启动磁盘**: 持久化磁盘或本地 SSD
- **区域和可用区**: 全球分布式部署

### 磁盘和存储
- **持久化磁盘 (PD)**: 标准 (HDD) 和 SSD 选项
- **本地 SSD**: 高性能临时存储
- **磁盘镜像**: 公共镜像、自定义镜像、社区镜像
- **快照**: 增量备份和恢复机制

### 实例管理
- **实例模板**: 预配置的 VM 配置模板
- **托管实例组 (MIG)**: 自动扩缩容、自动修复、滚动更新
- **非托管实例组**: 手动管理的 VM 集合

### 网络与负载均衡
- **VPC 网络**: 软件定义网络，全球范围
- **防火墙规则**: 基于标签和服务的访问控制
- **负载均衡**: HTTP(S)、SSL Proxy、TCP Proxy、Network LB
- **静态/临时 IP**: 外部和内部 IP 地址管理

## 实现方式

### 创建 VM 实例
```bash
# 使用 gcloud CLI 创建实例
gcloud compute instances create my-vm \
  --machine-type=e2-medium \
  --zone=us-central1-a \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-ssd \
  --tags=http-server,https-server

# 使用 Terraform
resource "google_compute_instance" "vm_instance" {
  name         = "my-vm"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 20
      type  = "pd-ssd"
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral public IP
    }
  }

  tags = ["http-server", "https-server"]
}
```

### 托管实例组配置
```bash
# 创建实例模板
gcloud compute instance-templates create web-template \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --tags=http-server \
  --metadata-from-file startup-script=startup.sh

# 创建托管实例组
gcloud compute instance-groups managed create web-mig \
  --template=web-template \
  --size=2 \
  --zone=us-central1-a

# 配置自动扩缩容
gcloud compute instance-groups managed set-autoscaling web-mig \
  --max-num-replicas=10 \
  --min-num-replicas=2 \
  --target-cpu-utilization=0.6 \
  --cool-down-period=60 \
  --zone=us-central1-a
```

### 负载均衡器配置
```bash
# 创建健康检查
gcloud compute health-checks create http web-health-check \
  --port=80 \
  --check-interval=5s \
  --timeout=5s \
  --healthy-threshold=2 \
  --unhealthy-threshold=2

# 创建后端服务
gcloud compute backend-services create web-backend \
  --protocol=HTTP \
  --health-checks=web-health-check \
  --global

# 添加实例组到后端服务
gcloud compute backend-services add-backend web-backend \
  --instance-group=web-mig \
  --instance-group-zone=us-central1-a \
  --balancing-mode=UTILIZATION \
  --max-utilization=0.8 \
  --global

# 创建 URL 映射和转发规则
gcloud compute url-maps create web-map --default-service=web-backend
gcloud compute target-http-proxies create web-proxy --url-map=web-map
gcloud compute forwarding-rules create web-rule \
  --global \
  --target-http-proxy=web-proxy \
  --ports=80
```

## 示例

### 高可用 Web 应用架构
```
                              ┌─────────────────┐
                              │   Cloud DNS     │
                              └────────┬────────┘
                                       │
                              ┌────────▼────────┐
                              │  HTTP(S) LB     │
                              │  (Global)       │
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
           ┌────────▼────────┐ ┌───────▼────────┐ ┌──────▼───────┐
           │   MIG (us-east) │ │ MIG (us-west)  │ │ MIG (europe) │
           │   3 instances   │ │  3 instances   │ │ 3 instances  │
           └────────┬────────┘ └───────┬────────┘ └──────┬───────┘
                    │                  │                 │
           ┌────────▼────────┐ ┌───────▼────────┐ ┌──────▼───────┐
           │  Cloud SQL      │ │  Cloud SQL     │ │ Cloud SQL    │
           │  (Read Replica) │ │  (Read Replica)│ │ (Primary)    │
           └─────────────────┘ └────────────────┘ └──────────────┘
```

### 启动脚本示例
```bash
#!/bin/bash
# startup.sh - 实例启动时执行

# 安装 Nginx
apt-get update
apt-get install -y nginx

# 配置防火墙
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# 启动服务
systemctl start nginx
systemctl enable nginx

# 写入实例信息到首页
echo "<h1>Server: $(hostname)</h1>" > /var/www/html/index.html
echo "<p>Zone: $(curl -s "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google")</p>" >> /var/www/html/index.html
```

## 应用场景

| 场景 | 方案 | 优势 |
|------|------|------|
| **Web 应用托管** | MIG + HTTP LB | 自动扩缩容，全球负载均衡 |
| **批处理计算** | 抢占式实例 + 实例模板 | 成本降低 60-91% |
| **高性能计算** | C2/M2 机器类型 + 本地 SSD | 高 CPU/内存性能 |
| **Windows 工作负载** | Windows Server 实例 + AD | 无缝迁移 Windows 应用 |
| **容器托管** | Container-Optimized OS | 轻量级，专为容器优化 |
| **开发测试环境** | 自定义镜像 + 快照 | 快速环境复制和恢复 |

## 面试要点

Q: Compute Engine 与 AWS EC2 的主要区别是什么？
A: GCE 提供按分钟计费（最少1分钟）、自定义机器类型（精确配置 CPU/内存）、全球 VPC 网络（跨区域通信不收费）、实时迁移（维护期间不停机）和抢占式实例的固定价格。

Q: 什么是托管实例组 (MIG) 的核心功能？
A: MIG 提供自动扩缩容（基于 CPU/负载/指标）、自动修复（健康检查失败自动重建）、滚动更新（逐步替换实例）、负载均衡集成和多区域部署能力。

Q: 持久化磁盘 (PD) 和本地 SSD 的区别？
A: PD 是网络存储，数据持久化，支持快照，可独立存在；本地 SSD 物理附加到主机，性能更高（高 IOPS/吞吐），但数据非持久化（实例停止即丢失），适合临时缓存。

Q: 如何实现零停机部署？
A: 使用 MIG 的滚动更新策略，设置 maxSurge（可同时创建的新实例数）和 maxUnavailable（可同时不可用的实例数），配合健康检查和负载均衡器逐步替换实例。

Q: 抢占式实例适用于什么场景？
A: 适用于容错性强、可中断的工作负载，如批处理作业、数据预处理、CI/CD 构建、渲染农场，可节省 60-91% 成本，但可能在24小时内被抢占。

## 相关概念

### 数据结构
- **一致性哈希**: 分布式负载均衡中的请求路由
- **B树/B+树**: 持久化磁盘文件系统索引

### 算法
- **自动扩缩容算法**: 目标追踪、步进策略、预测式扩缩容
- **健康检查算法**: HTTP/TCP 探测，指数退避重试

### 复杂度分析
- **磁盘 I/O 复杂度**: 顺序读写 O(n) vs 随机读写 O(n log n)
- **网络延迟**: 跨区域通信延迟开销

### 系统实现
- **虚拟化技术**: KVM/QEMU，嵌套虚拟化支持
- **实时迁移**: 内存预拷贝算法，无缝热迁移
- **软件定义网络**: Andromeda 网络虚拟化栈

### 对比参考
- [AWS EC2](../aws/ec2.md) - AWS 的虚拟机服务对比
- [AWS Auto Scaling](../aws/auto-scaling.md) - AWS 自动扩缩容
- [Kubernetes Pods](../kubernetes/pods.md) - 容器化计算资源
- [Kubernetes Deployment](../kubernetes/deployment.md) - 容器编排部署策略
- [负载均衡](../../distributed-systems/load-balancing.md) - 负载均衡原理
- [虚拟化技术](../../distributed-systems/virtualization.md) - 虚拟化基础
