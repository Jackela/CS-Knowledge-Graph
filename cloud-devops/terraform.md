# Terraform (基础设施即代码)

## 简介

Terraform 是 HashiCorp 开发的开源基础设施即代码（IaC）工具，允许用户使用声明式配置语言 HCL 来定义和预置基础设施资源。Terraform 支持多种云服务提供商，能够实现基础设施的版本控制、协作和自动化管理。

## 核心概念

### 1. HCL 语法
- **Block**: 资源、变量、输出等的基本结构
- **Argument**: 块内的键值对配置
- **Expression**: 动态值计算和引用
- **Interpolation**: `${var.name}` 语法引用变量

### 2. Providers
- **云提供商**: AWS、Azure、GCP、阿里云等
- **SaaS 服务**: Kubernetes、GitHub、Datadog 等
- **自定义 Provider**: 支持自定义 API 集成

### 3. Resources
- **基础设施组件**: 虚拟机、网络、存储、数据库等
- **依赖管理**: 自动处理资源间的依赖关系
- **生命周期**: 创建、读取、更新、删除（CRUD）

### 4. Modules
- **模块化**: 可复用的基础设施代码包
- **Input/Output**: 模块参数和输出定义
- **Registry**: Terraform Registry 共享模块

### 5. State 管理
- **State 文件**: 记录实际基础设施状态
- **Backend**: 本地或远程存储（S3、Consul、Terraform Cloud）
- **State Locking**: 防止并发修改冲突

### 6. Workspaces
- **环境隔离**: dev、staging、prod 环境分离
- **State 隔离**: 每个 Workspace 独立 State
- **工作流**: 多环境部署策略

## 实现方式

### 基础配置示例

```hcl
# main.tf - 基础资源配置
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "terraform-state-bucket"
    key    = "app/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC 资源
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
  }
}

# 子网资源
resource "aws_subnet" "public" {
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-${count.index + 1}"
  }
}
```

### 变量定义

```hcl
# variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "instance_config" {
  description = "EC2 instance configuration"
  type = object({
    instance_type = string
    count         = number
    ami_id        = string
  })
  default = {
    instance_type = "t3.micro"
    count         = 2
    ami_id        = "ami-12345678"
  }
}
```

### 模块封装

```hcl
# modules/ec2/main.tf
resource "aws_instance" "web" {
  count         = var.instance_count
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id

  user_data = templatefile("${path.module}/user_data.sh", {
    app_version = var.app_version
  })

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-web-${count.index + 1}"
  })
}

# modules/ec2/variables.tf
variable "instance_count" {
  type    = number
  default = 1
}

variable "ami_id" {
  type = string
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "subnet_id" {
  type = string
}

variable "name_prefix" {
  type = string
}

variable "app_version" {
  type = string
}

variable "common_tags" {
  type    = map(string)
  default = {}
}

# modules/ec2/outputs.tf
output "instance_ids" {
  value = aws_instance.web[*].id
}

output "private_ips" {
  value = aws_instance.web[*].private_ip
}
```

### 使用模块

```hcl
# main.tf - 调用模块
module "web_servers" {
  source = "./modules/ec2"

  instance_count = 3
  ami_id         = data.aws_ami.ubuntu.id
  instance_type  = "t3.medium"
  subnet_id      = aws_subnet.public[0].id
  name_prefix    = var.project_name
  app_version    = "v1.2.3"

  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# 数据源
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }
}
```

### Python 自动化脚本

```python
#!/usr/bin/env python3
"""Terraform 自动化管理脚本"""
import subprocess
import json
import os
from pathlib import Path

class TerraformManager:
    def __init__(self, working_dir: str):
        self.working_dir = Path(working_dir)
    
    def init(self, backend_config: dict = None):
        """初始化 Terraform"""
        cmd = ["terraform", "init"]
        if backend_config:
            for key, value in backend_config.items():
                cmd.extend(["-backend-config", f"{key}={value}"])
        return self._run(cmd)
    
    def plan(self, var_file: str = None, target: str = None):
        """执行 Plan"""
        cmd = ["terraform", "plan", "-out=tfplan"]
        if var_file:
            cmd.extend(["-var-file", var_file])
        if target:
            cmd.extend(["-target", target])
        return self._run(cmd)
    
    def apply(self, auto_approve: bool = False):
        """执行 Apply"""
        cmd = ["terraform", "apply"]
        if auto_approve:
            cmd.append("-auto-approve")
        else:
            cmd.append("tfplan")
        return self._run(cmd)
    
    def destroy(self, auto_approve: bool = False):
        """销毁资源"""
        cmd = ["terraform", "destroy"]
        if auto_approve:
            cmd.append("-auto-approve")
        return self._run(cmd)
    
    def output(self, name: str = None):
        """获取输出值"""
        cmd = ["terraform", "output", "-json"]
        if name:
            cmd.append(name)
        result = self._run(cmd, capture_output=True)
        return json.loads(result.stdout)
    
    def workspace_list(self):
        """列出工作区"""
        result = self._run(["terraform", "workspace", "list"], 
                          capture_output=True)
        return result.stdout.strip().split('\n')
    
    def workspace_select(self, name: str):
        """切换工作区"""
        return self._run(["terraform", "workspace", "select", name])
    
    def workspace_new(self, name: str):
        """创建工作区"""
        return self._run(["terraform", "workspace", "new", name])
    
    def validate(self):
        """验证配置"""
        return self._run(["terraform", "validate"])
    
    def fmt(self, check: bool = False):
        """格式化代码"""
        cmd = ["terraform", "fmt"]
        if check:
            cmd.append("-check")
        return self._run(cmd)
    
    def _run(self, cmd: list, capture_output: bool = False):
        """执行命令"""
        result = subprocess.run(
            cmd,
            cwd=self.working_dir,
            capture_output=capture_output,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stderr}")
        return result

# 使用示例
if __name__ == "__main__":
    tf = TerraformManager("./infrastructure")
    
    # 初始化并切换到 dev 环境
    tf.init()
    tf.workspace_select("dev")
    
    # Plan 和 Apply
    tf.plan(var_file="dev.tfvars")
    tf.apply()
    
    # 获取输出
    outputs = tf.output()
    print(f"VPC ID: {outputs['vpc_id']['value']}")
```

### Shell 工作流脚本

```bash
#!/bin/bash
# Terraform CI/CD 工作流脚本

set -e

ENVIRONMENT=${1:-dev}
WORKSPACE="${ENVIRONMENT}"
TF_DIR="./terraform"

cd "$TF_DIR"

echo "=== Terraform 工作流: $ENVIRONMENT ==="

# 格式化检查
echo "→ 检查代码格式..."
terraform fmt -check -diff || {
    echo "错误: 代码格式不正确，运行 'terraform fmt' 修复"
    exit 1
}

# 验证配置
echo "→ 验证配置..."
terraform validate

# 选择/创建工作区
echo "→ 切换到工作区: $WORKSPACE..."
terraform workspace select "$WORKSPACE" || terraform workspace new "$WORKSPACE"

# 初始化
echo "→ 初始化 Terraform..."
terraform init -input=false

# Plan
echo "→ 执行 Plan..."
terraform plan \
    -var-file="environments/${ENVIRONMENT}.tfvars" \
    -out="tfplan-${ENVIRONMENT}" \
    -input=false

# 显示 Plan 摘要
terraform show -json "tfplan-${ENVIRONMENT}" | jq '.resource_changes | length' | xargs echo "预计变更资源数:"

# 自动应用（CI 环境）
if [ "$AUTO_APPLY" = "true" ]; then
    echo "→ 自动应用变更..."
    terraform apply -input=false "tfplan-${ENVIRONMENT}"
fi

echo "=== 工作流完成 ==="
```

## 示例

### 完整项目结构

```
terraform-project/
├── main.tf              # 主配置
├── variables.tf         # 变量定义
├── outputs.tf           # 输出定义
├── terraform.tfvars     # 变量值
├── versions.tf          # 版本约束
├── backend.tf           # 后端配置
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ecs/
│   └── rds/
└── environments/
    ├── dev.tfvars
    ├── staging.tfvars
    └── prod.tfvars
```

### 输出配置示例

```hcl
# outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "web_server_ips" {
  description = "Web server private IPs"
  value       = module.web_servers.private_ips
  sensitive   = false
}

output "database_password" {
  description = "Database password"
  value       = aws_db_instance.main.password
  sensitive   = true  # 不会在控制台显示
}
```

## 应用场景

1. **多云基础设施管理**: 统一管理 AWS、Azure、GCP 资源
2. **环境一致性**: 确保 dev/staging/prod 环境一致
3. **灾难恢复**: 快速重建完整基础设施
4. **合规审计**: 基础设施变更可追溯
5. **成本优化**: 自动清理测试环境资源

## 面试要点

Q: Terraform 的 State 文件有什么作用？
A: State 文件记录实际部署的基础设施状态，用于：
   - 映射配置资源到实际资源
   - 追踪资源元数据和依赖关系
   - 支持增量更新和变更检测
   - 多人协作时的状态同步
   - 建议远程存储（S3）并启用状态锁定

Q: Terraform 如何处理资源依赖？
A: Terraform 支持两种依赖方式：
   - 隐式依赖：通过资源引用自动推断（如 `aws_instance.web.subnet_id`）
   - 显式依赖：使用 `depends_on` 元参数声明
   - 依赖图计算确保资源按正确顺序创建/销毁

Q: Terraform 与 Ansible 的区别是什么？
A: 主要区别：
   - **Terraform**: 基础设施编排（Provisioning），声明式，擅长创建/销毁资源
   - **Ansible**: 配置管理（Configuration），过程式，擅长软件安装和配置
   - 最佳实践：Terraform 创建基础设施，Ansible 配置应用

Q: 如何实现 Terraform 多环境管理？
A: 三种常用方式：
   - **Workspaces**: 适合结构相似的环境，State 隔离
   - **文件结构**: `environments/dev/`、`environments/prod/`，完全隔离
   - **变量文件**: 相同代码，不同 `.tfvars` 文件
   - 生产环境建议使用文件结构，确保完全隔离

Q: 如何保护 Terraform State 中的敏感数据？
A: 保护措施：
   - 使用 `sensitive = true` 标记敏感输出
   - 启用远程 State 加密（S3 服务端加密）
   - 限制 State 文件访问权限（IAM 策略）
   - 使用 Vault 或 AWS Secrets Manager 管理密钥
   - 避免在代码中硬编码敏感信息


## 相关概念

### 数据结构
- **图（Graph）**：Terraform 内部使用有向无环图（DAG）管理资源依赖关系
- **映射表（Map）**：State 文件使用 JSON 格式存储资源映射

### 算法
- **拓扑排序**：解析资源依赖顺序，确保创建顺序正确
- **差异算法**：对比期望状态与实际状态，生成最小变更集

### 复杂度分析
| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| 依赖解析 | O(V + E) | V=资源数，E=依赖边数 |
| State 读取 | O(1) | 哈希表查找 |
| Plan 生成 | O(n) | n=资源数量 |

### 系统实现
- **插件架构**：基于 gRPC 的 provider 通信协议
- **状态锁定**：分布式锁（DynamoDB、Consul、PostgreSQL）
- **后端存储**：支持 S3、GCS、Azure Blob、本地文件等

### 关联文件
- [Kubernetes](./kubernetes/README.md) - 容器编排平台，可通过 Terraform 部署
- [Docker](./docker.md) - 容器技术，与 Terraform 结合实现完整交付
- [分布式系统](../distributed-systems/README.md) - Terraform 可用于部署分布式架构
- [安全](../security/README.md) - 基础设施安全配置

