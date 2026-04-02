# Docker Compose (多容器编排工具)

## 简介

**Docker Compose** 是 Docker 官方提供的多容器应用编排工具，允许开发者使用 YAML 文件定义和运行多容器 Docker 应用程序。通过一个 `docker-compose.yml` 文件，可以一次性配置应用所需的所有服务、网络和存储卷。

## 核心概念

- **服务（Service）**：应用中的单个容器组件，如 Web 服务器、数据库、缓存等
- **项目（Project）**：由一组关联服务组成的完整应用，通常对应一个 `docker-compose.yml` 文件
- **网络（Network）**：服务间通信的虚拟网络，Compose 会自动创建默认网络
- **卷（Volume）**：持久化数据存储，独立于容器生命周期
- **依赖（Depends_on）**：定义服务启动顺序和依赖关系

## 主要优势

- **声明式配置**：通过 YAML 文件描述整个应用架构
- **一键启动**：`docker-compose up` 启动所有服务
- **环境隔离**：轻松创建独立的开发、测试、生产环境
- **版本控制**：配置即代码，可纳入版本管理系统
- **开发友好**：本地开发环境与生产环境保持一致

## 实现方式

### 基础配置示例

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
    depends_on:
      - api

  api:
    build: ./api
    environment:
      - NODE_ENV=production
      - DB_HOST=db
    ports:
      - "3000:3000"
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:

networks:
  default:
    driver: bridge
```

### 生产环境配置

```yaml
version: '3.8'

services:
  app:
    image: myapp:${VERSION:-latest}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - frontend
      - backend

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - frontend

volumes:
  redis_data:
    driver: local

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

### 开发环境配置

```yaml
version: '3.8'

services:
  web:
    build:
      context: ./web
      dockerfile: Dockerfile.dev
    volumes:
      - ./web:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - CHOKIDAR_USEPOLLING=true
      - REACT_APP_API_URL=http://localhost:8000
    command: npm start

  api:
    build:
      context: ./api
      dockerfile: Dockerfile.dev
    volumes:
      - ./api:/app
      - /app/__pycache__
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - DATABASE_URL=postgresql://dev:dev@db:5432/devdb
    command: uvicorn main:app --reload --host 0.0.0.0

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
      POSTGRES_DB: devdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev:/var/lib/postgresql/data

  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"
      - "8025:8025"

volumes:
  postgres_dev:
```

## 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 构建镜像
docker-compose build

# 执行命令
docker-compose exec web sh

# 水平扩展
docker-compose up -d --scale web=3

# 指定配置文件
docker-compose -f docker-compose.prod.yml up -d
```

## 应用场景

- **本地开发环境**：快速搭建包含前后端、数据库、缓存的完整开发环境
- **集成测试**：在 CI/CD 管道中启动依赖服务进行自动化测试
- **演示部署**：快速部署演示环境供客户或团队 review
- **微服务原型**：验证微服务架构的服务间通信和依赖关系
- **数据库迁移**：管理数据库 Schema 变更和数据迁移流程

## 最佳实践

### 1. 多环境配置管理

```yaml
# docker-compose.yml - 基础配置
version: '3.8'
services:
  web:
    image: nginx:alpine

# docker-compose.override.yml - 开发环境覆盖
version: '3.8'
services:
  web:
    volumes:
      - ./src:/usr/share/nginx/html

# docker-compose.prod.yml - 生产环境配置
version: '3.8'
services:
  web:
    deploy:
      replicas: 3
```

### 2. 健康检查配置

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 3. 环境变量管理

```yaml
services:
  app:
    env_file:
      - .env
      - .env.local
    environment:
      - NODE_ENV=${NODE_ENV:-development}
      - API_KEY=${API_KEY}
```

## 面试要点

1. **Q: Docker Compose 与 Docker Swarm 的区别是什么？**
   A: Docker Compose 是单机多容器编排工具，适用于开发和测试环境；Docker Swarm 是 Docker 的原生集群管理工具，支持多主机容器编排，适用于生产环境。Compose 使用 docker-compose.yml，Swarm 使用 docker stack deploy。

2. **Q: 如何在 Compose 中实现服务间的通信？**
   A: Compose 自动创建默认网络，服务间可通过服务名进行 DNS 解析通信。例如，web 服务可以通过 `http://api:3000` 访问 api 服务。也可以自定义网络实现更复杂的网络隔离。

3. **Q: depends_on 是否能保证服务完全就绪？**
   A: depends_on 只保证启动顺序，不保证服务完全就绪。需要配合 healthcheck 和 condition: service_healthy 确保依赖服务真正可用后再启动依赖它的服务。

4. **Q: 如何实现 Compose 配置的复用？**
   A: 可以使用 extends 关键字继承配置，或通过多个 compose 文件组合（-f 参数）。Docker Compose v2.20+ 支持 include 语法引入外部 compose 文件。

5. **Q: Compose 中的数据持久化有哪些方式？**
   A: 三种主要方式：(1) 命名卷（volumes）- 由 Docker 管理，推荐用于数据库；(2) 绑定挂载（bind mount）- 直接挂载主机路径，适合开发；(3) tmpfs 挂载 - 存储在内存中，适合敏感数据或临时文件。

6. **Q: 如何管理不同环境的配置差异？**
   A: 使用 docker-compose.override.yml 自动覆盖基础配置，或使用 -f 参数指定多个配置文件（如 docker-compose.yml docker-compose.prod.yml）。配合 .env 文件管理环境变量。

7. **Q: Compose 如何处理容器重启策略？**
   A: 通过 restart 或 deploy.restart_policy 配置：(1) no - 不重启；(2) always - 总是重启；(3) on-failure - 退出码非0时重启；(4) unless-stopped - 除非手动停止，否则总是重启。

## 相关概念

### Cloud & DevOps
- [Docker](./docker.md) - 容器运行时基础
- [Kubernetes](./kubernetes.md) - 生产级容器编排平台
- [Helm Charts](./helm.md) - Kubernetes 包管理工具
- [CI/CD](./cicd/) - 持续集成与持续部署
- [ArgoCD](./argocd.md) - GitOps 持续交付工具

### 系统实现
- [进程管理](../computer-science/systems/process.md) - 容器进程隔离原理
- [网络协议](../computer-science/systems/network-security.md) - 容器网络通信基础
- [文件系统](../computer-science/systems/file-systems.md) - 容器存储层实现
- [日志系统](../computer-science/systems/logging.md) - 容器日志收集与管理
