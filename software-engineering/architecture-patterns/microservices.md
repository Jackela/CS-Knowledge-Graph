# 微服务架构 (Microservices Architecture)

## 概念

微服务架构（Microservices Architecture）是一种**架构风格**，将应用拆分为小型、独立部署的服务，每个服务围绕业务能力构建。

> **核心思想**: 高内聚、低耦合，服务自治。

---

## 特征

### 九大特征

1. **服务组件化**: 独立代码库、独立部署
2. **按业务能力组织**: 团队对产品负责
3. **去中心化治理**: 技术栈多样性
4. **去中心化数据管理**: 每个服务有自己的数据库
5. **基础设施自动化**: CI/CD、容器化
6. **容错设计**: 熔断、降级
7. **设计演进**: 持续重构
8. **智能端点**: 轻量通信
9. **独立部署**: 蓝绿部署、金丝雀发布

---

## 服务通信

### 同步通信

```python
# REST API
import requests

def get_user_orders(user_id):
    response = requests.get(f"http://order-service/orders?user_id={user_id}")
    return response.json()

# gRPC
import grpc
from user_pb2 import UserRequest
from user_pb2_grpc import UserServiceStub

channel = grpc.insecure_channel('user-service:50051')
stub = UserServiceStub(channel)
response = stub.GetUser(UserRequest(id=user_id))
```

### 异步通信

```python
# 消息队列
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='order_queue')

# 生产者
channel.basic_publish(exchange='', routing_key='order_queue', body='order_data')

# 消费者
def callback(ch, method, properties, body):
    process_order(body)

channel.basic_consume(queue='order_queue', on_message_callback=callback, auto_ack=True)
```

---

## 服务发现

```yaml
# Eureka / Consul / Nacos
services:
  user-service:
    instances:
      - id: user-1
        host: 192.168.1.10
        port: 8080
        status: UP
      - id: user-2
        host: 192.168.1.11
        port: 8080
        status: UP
```

---

## 优缺点

**优点**:
- 独立扩展
- 技术异构
- 故障隔离
- 团队自治

**缺点**:
- 分布式复杂度
- 数据一致性挑战
- 运维成本高
- 网络延迟

---

## 面试要点

1. **vs 单体**: 拆分时机、团队规模
2. **数据一致性**: Saga 模式、最终一致性
3. **服务划分**: DDD 限界上下文

---

## 相关概念

- [服务网格](./service-mesh.md)
- [事件驱动架构](./event-driven.md)
- [API 网关](../api-gateway.md)
