# Docker

## 简介

**Docker**是一个开源的应用容器引擎，允许开发者将应用及其依赖打包到一个可移植的容器中，然后发布到任何流行的Linux或Windows机器上。Docker解决了"在我的机器上可以运行"的环境不一致问题。

## 核心概念

- **镜像（Image）**：只读模板，包含运行应用所需的代码、库、环境变量和配置文件
- **容器（Container）**：镜像的运行实例，是独立运行的应用进程
- **仓库（Repository）**：存储和分发镜像的地方，如Docker Hub
- **Dockerfile**：定义镜像构建步骤的文本文件

## 主要优势

- **环境一致性**：开发、测试、生产环境完全一致
- **快速部署**：秒级启动和停止
- **资源隔离**：容器间相互隔离，互不影响
- **轻量级**：相比虚拟机，共享宿主机内核，资源占用少

## 常用命令

```bash
# 镜像操作
docker pull nginx
docker build -t myapp .
docker images

# 容器操作
docker run -d -p 80:80 nginx
docker ps
docker stop container_id
docker rm container_id
```

## 相关概念

- [Kubernetes](./kubernetes.md) - 容器编排平台
- [GitHub Actions](./cicd/github-actions.md) - CI/CD 持续集成
- [微服务](../software-engineering/architecture-patterns/microservices.md) - Docker擅长的架构模式
- [CI/CD](./cicd/) - 持续集成与持续部署

### AI与数据
- [机器学习概述](../ai-data-systems/ml-overview.md) - ML模型容器化
- [向量数据库](../ai-data-systems/vector-db.md) - 数据服务容器部署
