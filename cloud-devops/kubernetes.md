# Kubernetes

## 简介

**Kubernetes（K8s）**是一个开源的容器编排平台，用于自动化容器的部署、扩展和管理。它由Google设计并捐赠给Cloud Native Computing Foundation（CNCF），现已成为容器编排领域的事实标准。

## 核心概念

- **Pod**：最小的部署单元，包含一个或多个容器
- **Service**：定义一组Pod的访问策略，提供稳定的网络端点
- **Deployment**：声明式管理Pod的副本集，支持滚动更新
- **Namespace**：用于隔离资源和环境的逻辑分区
- **Ingress**：管理集群外部访问的HTTP路由规则

## 主要功能

- **自动扩缩容**：根据负载自动调整Pod数量（HPA）
- **服务发现与负载均衡**：自动分配IP和DNS名，平衡流量
- **存储编排**：自动挂载本地、云存储或网络存储
- **自动部署与回滚**：支持滚动更新，失败自动回滚
- **自我修复**：容器失败时自动重启、替换

## 常用命令

```bash
# 查看资源
kubectl get pods
kubectl get services
kubectl get deployments

# 部署应用
kubectl apply -f deployment.yaml
kubectl scale deployment myapp --replicas=3

# 查看日志
kubectl logs pod_name
kubectl exec -it pod_name -- /bin/bash
```

## 相关概念

- [Docker](./docker.md) - 容器运行时
- [负载均衡](../computer-science/distributed-systems/load-balancing.md) - Kubernetes的核心功能
- [服务网格](../software-engineering/architecture-patterns/service-mesh.md) - 与Kubernetes配合的高级流量管理
- [负载均衡算法](../computer-science/algorithms/greedy.md) - 调度算法
- [LLM](../ai-data-systems/llm.md) - 大模型在Kubernetes上的部署
- [线性代数](../mathematics/linear-algebra.md) - 负载均衡的数学基础
