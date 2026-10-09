# EC2 (Amazon Elastic Compute Cloud)

## 简介

Amazon EC2 是 AWS 提供的**弹性计算云服务**，允许用户在云中快速启动虚拟服务器，并按需扩展计算能力。它消除了硬件采购的前期投入，让服务器部署从数周缩短到几分钟。

## 核心概念

### 实例类型
| 类型 | 适用场景 | 特点 |
|------|----------|------|
| **t3/t4g** | 开发测试、轻量应用 | 突发性能，成本最低 |
| **m5/m6i** | 通用计算 | 平衡计算、内存、网络 |
| **c5/c6i** | 计算密集型 | CPU 性能优化 |
| **r5/r6i** | 内存密集型 | 大内存，数据库适用 |
| **g4/g5** | GPU 实例 | 机器学习、图形渲染 |

### 购买选项
- **On-Demand**: 按小时/秒计费，灵活无承诺
- **Reserved**: 1-3 年预留，最高节省 72%
- **Spot**: 竞价实例，最高节省 90%，但可能被中断
- **Savings Plans**: 灵活的预留模式，基于使用量承诺

### 存储选项
- **EBS (Elastic Block Store)**: 持久化块存储，可快照备份
- **Instance Store**: 本地临时存储，高性能但数据不持久
- **EFS (Elastic File System)**: 托管 NFS，多实例共享

## 实现方式

### 使用 AWS CLI 创建实例

```bash
# 启动 EC2 实例
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.micro \
    --key-name my-key-pair \
    --security-group-ids sg-903004f8 \
    --subnet-id subnet-6e7f829e \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=web-server}]'

# 查看实例状态
aws ec2 describe-instances --instance-ids i-1234567890abcdef0

# 停止实例
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# 终止实例
aws ec2 terminate-instances --instance-ids i-1234567890abcdef0
```

### 使用 CloudFormation (基础设施即代码)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: EC2 Instance with Security Group

Resources:
  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Enable HTTP and SSH
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/24

  WebServerInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c55b159cbfafe1f0
      InstanceType: t3.micro
      SecurityGroups:
        - !Ref WebServerSecurityGroup
      UserData:
        Fn::Base64: |
          #!/bin/bash
          yum update -y
          yum install -y httpd
          systemctl start httpd
          systemctl enable httpd
          echo "<h1>Hello from EC2</h1>" > /var/www/html/index.html
      Tags:
        - Key: Name
          Value: WebServer
```

### Auto Scaling 配置

```yaml
# Auto Scaling Group 配置
Resources:
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: web-server-template
      LaunchTemplateData:
        ImageId: ami-0c55b159cbfafe1f0
        InstanceType: t3.micro
        SecurityGroupIds:
          - sg-903004f8

  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      VPCZoneIdentifier:
        - subnet-12345678
        - subnet-87654321
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: 2
      MaxSize: 10
      DesiredCapacity: 2
      TargetGroupARNs:
        - !Ref ALBTargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
```

## 应用场景

- **Web 应用托管**: 部署网站、API 服务、微服务
- **批处理计算**: 大规模数据处理、视频转码
- **开发与测试环境**: 快速创建和销毁临时环境
- **高性能计算 (HPC)**: 科学计算、金融建模

## 面试要点

1. **Q: EC2 的 Spot 实例适合什么场景？**  
   A: 适合容错性强、可中断的任务，如批处理、CI/CD 构建、机器学习训练。利用 Spot 实例可节省高达 90% 成本。

2. **Q: EBS 和 Instance Store 的区别？**  
   A: EBS 是持久化网络存储，数据在实例终止后保留，支持快照；Instance Store 是本地物理存储，性能更高但实例终止后数据丢失。

3. **Q: 如何确保 EC2 实例的高可用性？**  
   A: 使用 Auto Scaling Group 配合 ELB，跨多个可用区 (AZ) 部署；使用健康检查自动替换故障实例；定期创建 AMI 和 EBS 快照。

4. **Q: EC2 的 User Data 是什么？**  
   A: 实例首次启动时执行的脚本，常用于安装软件、配置环境、运行初始化任务。仅在实例首次启动时执行一次。

5. **Q: 如何优化 EC2 成本？**  
   A: 使用 Reserved Instances 或 Savings Plans 降低长期成本；使用 Spot 实例处理可中断工作负载；合理选择实例类型；使用 Auto Scaling 按需扩缩容；定期清理闲置资源。

## 相关概念

### Cloud & DevOps
- [AWS S3](./s3.md) - 对象存储服务
- [AWS RDS](./rds.md) - 托管关系型数据库
- [AWS Lambda](./lambda.md) - 无服务器计算
- [负载均衡](../../computer-science/distributed-systems/load-balancing.md) - 流量分发

### 系统实现
- [虚拟内存](../../computer-science/systems/virtual-memory.md) - 虚拟化基础
- [进程](../../computer-science/systems/process.md) - 进程管理
- [Docker](../../docker.md) - 容器化部署
