# 无服务器架构 (Serverless Architecture)

## 简介

**无服务器架构**（Serverless Architecture）是一种云计算执行模型，云提供商动态管理服务器资源的分配和扩展。开发者只需关注业务代码，无需管理服务器、操作系统或运行时环境。主要包括 FaaS（函数即服务）和 BaaS（后端即服务）两种模式。

## 核心概念

| 概念 | 英文 | 说明 |
|------|------|------|
| **FaaS** | Function as a Service | 函数即服务，事件触发的代码执行 |
| **BaaS** | Backend as a Service | 后端即服务，托管的数据库、认证等服务 |
| **Cold Start** | 冷启动 | 函数首次调用时的初始化延迟 |
| **Event Source** | 事件源 | 触发函数执行的事件来源 |
| **Statelessness** | 无状态 | 函数不保存请求间的状态 |
| **Ephemeral** | 临时的 | 函数执行环境是临时的，执行后销毁 |

## 架构组件

```
┌─────────────────────────────────────────┐
│           Client (Web/Mobile)           │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         API Gateway / CDN               │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │Function │ │Function │ │Function │   │
│  │   A     │ │   B     │ │   C     │   │
│  └────┬────┘ └────┬────┘ └────┬────┘   │
│       │           │           │         │
│       └───────────┼───────────┘         │
│                   │                     │
│  ┌────────────────▼────────────────┐    │
│  │     Event Bus / Queue           │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│  Database │ Object Storage │ Auth      │
│  (DynamoDB│   (S3)         │ (Cognito) │
└─────────────────────────────────────────┘
```

## 实现方式

### 1. AWS Lambda 函数

```python
# lambda_handler.py
import json
import boto3
from decimal import Decimal

# DynamoDB 客户端
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

def lambda_handler(event, context):
    \"\"\"\n    AWS Lambda 处理程序\n    创建订单示例\n    \"\"\"\n    print(f\"Request ID: {context.aws_request_id}\")\n    print(f\"Remaining time: {context.get_remaining_time_in_millis()}ms\")\n    \n    try:\n        # 解析请求\n        body = json.loads(event['body'])\n        order_id = body['order_id']\n        customer_id = body['customer_id']\n        items = body['items']\n        \n        # 计算总价\n        total = sum(item['price'] * item['quantity'] for item in items)\n        \n        # 存储到 DynamoDB\n        order = {\n            'order_id': order_id,\n            'customer_id': customer_id,\n            'items': items,\n            'total': Decimal(str(total)),\n            'status': 'PENDING'\n        }\n        \n        table.put_item(Item=order)\n        \n        return {\n            'statusCode': 201,\n            'headers': {\n                'Content-Type': 'application/json',\n                'Access-Control-Allow-Origin': '*'\n            },\n            'body': json.dumps({\n                'message': 'Order created',\n                'order_id': order_id\n            })\n        }\n    \n    except Exception as e:\n        print(f\"Error: {str(e)}\")\n        return {\n            'statusCode': 500,\n            'body': json.dumps({'error': str(e)})\n        }\n```

### 2. Serverless Framework 配置

```yaml\n# serverless.yml\nservice: order-service\n\nprovider:\n  name: aws\n  runtime: python3.9\n  region: us-east-1\n  environment:\n    TABLE_NAME: Orders\n  iam:\n    role:\n      statements:\n        - Effect: Allow\n          Action:\n            - dynamodb:PutItem\n            - dynamodb:GetItem\n          Resource: 
            - !GetAtt OrdersTable.Arn\n\nfunctions:\n  createOrder:\n    handler: handler.lambda_handler\n    events:\n      - http:\n          path: orders\n          method: post\n          cors: true\n    timeout: 10\n    memorySize: 256\n  \n  processOrder:\n    handler: process_handler.lambda_handler\n    events:\n      - sqs:\n          arn:\n            Fn::GetAtt:\n              - OrderQueue\n              - Arn\n    reservedConcurrency: 10\n\nresources:\n  Resources:\n    OrdersTable:\n      Type: AWS::DynamoDB::Table\n      Properties:\n        TableName: Orders\n        AttributeDefinitions:\n          - AttributeName: order_id\n            AttributeType: S\n        KeySchema:\n          - AttributeName: order_id\n            KeyType: HASH\n        BillingMode: PAY_PER_REQUEST\n    \n    OrderQueue:\n      Type: AWS::SQS::Queue\n      Properties:\n        QueueName: order-processing-queue\n        VisibilityTimeout: 300\n```

### 3. 本地测试

```python\n# test_local.py\nimport pytest\nfrom lambda_handler import lambda_handler\n\nclass MockContext:\n    def __init__(self):\n        self.aws_request_id = 'test-request-id'\n        self.memory_limit_in_mb = 256\n        self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789:function:test'\n    \n    def get_remaining_time_in_millis(self):\n        return 30000\n\n@pytest.fixture\ndef mock_event():\n    return {\n        'body': '{\"order_id\": \"ORD-001\", \"customer_id\": \"CUST-001\", \"items\": [{\"product_id\": \"P1\", \"price\": 10.0, \"quantity\": 2}]}',\n        'httpMethod': 'POST',\n        'headers': {}\n    }\n\ndef test_lambda_handler(mock_event):\n    context = MockContext()\n    response = lambda_handler(mock_event, context)\n    \n    assert response['statusCode'] == 201\n    body = json.loads(response['body'])\n    assert body['order_id'] == 'ORD-001'\n```

### 4. 多提供商支持 (Serverless.com)

```python\n# multi_cloud_handler.py\nimport os\n\ndef get_provider():\n    return os.environ.get('SERVERLESS_PROVIDER', 'aws')\n\ndef handler(event, context):\n    provider = get_provider()\n    \n    if provider == 'aws':\n        return aws_handler(event, context)\n    elif provider == 'azure':\n        return azure_handler(event, context)\n    elif provider == 'gcp':\n        return gcp_handler(event, context)\n    else:\n        raise ValueError(f'Unknown provider: {provider}')\n\ndef aws_handler(event, context):\n    # AWS Lambda 特定实现\n    return {'statusCode': 200, 'body': 'AWS Lambda'}\n\ndef azure_handler(event, context):\n    # Azure Functions 特定实现\n    return 'Azure Functions'\n\ndef gcp_handler(event, context):\n    # Google Cloud Functions 特定实现\n    return 'Google Cloud Functions'\n```

## 应用场景

### 1. REST API 后端\n```\nAPI Gateway → Lambda → DynamoDB\n```

### 2. 文件处理管道\n```\nS3 Upload → Lambda (缩略图生成) → S3 → Lambda (元数据提取) → RDS\n```

### 3. 实时数据处理\n```\nIoT Device → Kinesis → Lambda (分析) → SNS (告警)\n```

### 4. 定时任务\n```yaml\nfunctions:\n  dailyReport:\n    handler: report.handler\n    events:\n      - schedule: rate(1 day)  # 每天执行\n```

## 冷启动优化

```python\n# cold_start_optimization.py\nimport json\n\n# 在模块级别初始化，只在冷启动时执行\ndb_client = None\n\ndef get_db_client():\n    global db_client\n    if db_client is None:\n        import boto3\n        db_client = boto3.client('dynamodb')\n    return db_client\n\ndef lambda_handler(event, context):\n    # 使用连接池或缓存客户端\n    db = get_db_client()\n    # ... 处理请求\n    return {'statusCode': 200}\n\n# 使用 Provisioned Concurrency 减少冷启动\n# serverless.yml\n# functions:\n#   myFunction:\n#     provisionedConcurrency: 10\n```

## 面试要点

**Q: 什么是冷启动？如何减少冷启动时间？**
A: 冷启动是指函数首次调用或长时间未调用后的初始化延迟。优化方法：1) 使用 Provisioned Concurrency 保持函数预热；2) 精简依赖包大小；3) 在模块级别初始化连接；4) 选择更快的运行时（如 Go、Rust）；5) 增加内存分配（同时增加 CPU）。

**Q: Serverless 的限制有哪些？**
A: 1) **执行时间限制**（通常 15 分钟）；2) **内存限制**（通常 10GB）；3) **包大小限制**（通常 250MB）；4) **并发限制**（默认 1000）；5) **状态管理**（无状态设计）；6) **调试困难**；7) **供应商锁定**。

**Q: 如何在 Serverless 中管理状态？**
A: 由于函数是无状态的，状态需要存储在外部服务：1) **DynamoDB**、CosmosDB 等 NoSQL 数据库；2) **Redis/ElastiCache** 缓存；3) **S3** 对象存储；4) **Step Functions** 工作流状态。

**Q: Serverless 的成本模型？**
A: 按实际执行付费：调用次数 × 执行时间（GB-秒）。空闲时间不收费。适合：流量波动大、间歇性任务、初创项目。不适合：持续高负载、长连接服务、大计算量任务。

**Q: 如何实现 Serverless 应用的本地开发？**
A: 1) **Serverless Framework** 的 `serverless-offline` 插件；2) **AWS SAM** CLI 本地测试；3) **LocalStack** 模拟云服务；4) **Docker** 容器化本地运行。

## 相关概念

### 数据结构
- [消息队列](../../computer-science/data-structures/queue.md) - 事件驱动架构

### 系统实现
- [微服务](./microservices.md) - 服务拆分策略
- [事件驱动架构](./event-driven.md) - 异步通信模式
- [API 网关](./api-gateway.md) - 请求路由和聚合

### 云服务商
- AWS Lambda - 最早的 FaaS 服务
- Azure Functions - 微软的 Serverless 平台
- Google Cloud Functions - GCP 的 Serverless 方案
- Cloudflare Workers - 边缘计算 Serverless
