# 单体架构 (Monolithic Architecture)

## 简介

单体架构（Monolithic Architecture）是一种将所有功能模块打包在一起并作为一个单一单元部署的软件架构风格。在单体应用中，用户界面、业务逻辑和数据访问层都紧密耦合在同一个代码库中，作为一个独立的应用程序运行。

虽然微服务架构近年来备受推崇，但单体架构仍然是许多成功产品的起点，具有开发简单、部署方便、调试容易等优势。

## 核心概念

### 单体架构特征
- **单一部署单元**：所有组件打包为一个可执行文件或归档文件
- **共享代码库**：所有模块在同一个代码仓库中开发
- **统一技术栈**：整个应用使用相同的技术和框架
- **集中式数据管理**：通常使用单一数据库

### 模块化单体 (Modular Monolith)
- 在单体架构内部实现清晰的模块边界
- 模块间通过定义良好的接口通信
- 为未来可能的拆分奠定基础

### 分层架构在单体中的应用
```
┌─────────────────────────────────────┐
│         表示层 (Presentation)        │
├─────────────────────────────────────┤
│         业务逻辑层 (Business)        │
├─────────────────────────────────────┤
│         数据访问层 (Data Access)     │
├─────────────────────────────────────┤
│         数据库 (Database)            │
└─────────────────────────────────────┘
```

## 实现方式

### 典型项目结构
```
monolithic-app/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   ├── controller/     # 控制器层
│   │   │   ├── service/        # 业务逻辑层
│   │   │   ├── repository/     # 数据访问层
│   │   │   ├── model/          # 领域模型
│   │   │   └── config/         # 配置类
│   │   └── resources/
│   └── test/
├── pom.xml / build.gradle       # 构建配置
└── Dockerfile                   # 容器化配置
```

### 模块化实现示例

**模块接口定义：**
```python
# 订单模块接口
from abc import ABC, abstractmethod

class OrderService(ABC):
    @abstractmethod
    def create_order(self, user_id: str, items: list) -> dict:
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass

# 库存模块接口
class InventoryService(ABC):
    @abstractmethod
    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        pass
    
    @abstractmethod
    def release_stock(self, product_id: str, quantity: int) -> None:
        pass
```

**模块实现：**
```python
# order_service_impl.py
class OrderServiceImpl(OrderService):
    def __init__(self, inventory_service: InventoryService, 
                 order_repository, event_publisher):
        self.inventory = inventory_service
        self.repository = order_repository
        self.event_publisher = event_publisher
    
    def create_order(self, user_id: str, items: list) -> dict:
        # 1. 预留库存
        for item in items:
            if not self.inventory.reserve_stock(item['product_id'], 
                                                 item['quantity']):
                raise InsufficientStockException()
        
        # 2. 创建订单
        order = self.repository.save({
            'user_id': user_id,
            'items': items,
            'status': 'CREATED'
        })
        
        # 3. 发布事件
        self.event_publisher.publish('order.created', order)
        
        return order
```

## 示例

### 电商单体应用

```python
# app.py - Flask 单体应用示例
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
db = SQLAlchemy(app)

# 数据模型
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='PENDING')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, nullable=False)

# API 端点
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        data = request.json
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return jsonify({'id': product.id}), 201
    
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price} 
                    for p in products])

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    user_id = data['user_id']
    items = data['items']
    
    # 计算总价并检查库存
    total = 0
    for item in items:
        product = Product.query.get(item['product_id'])
        if product.stock < item['quantity']:
            return jsonify({'error': 'Insufficient stock'}), 400
        total += product.price * item['quantity']
    
    # 创建订单
    order = Order(user_id=user_id, total=total)
    db.session.add(order)
    db.session.flush()
    
    # 创建订单项并扣减库存
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            quantity=item['quantity']
        )
        db.session.add(order_item)
        
        product = Product.query.get(item['product_id'])
        product.stock -= item['quantity']
    
    db.session.commit()
    return jsonify({'order_id': order.id, 'total': total}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

### 部署配置

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://db:5432/ecommerce
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
```

## 应用场景

### 适合单体架构的场景
- **初创项目**：团队规模小，需要快速迭代和验证想法
- **中小型应用**：功能相对简单，预计用户量可控
- **概念验证 (PoC)**：快速构建原型验证业务可行性
- **内部工具**：面向特定团队的管理后台或工具系统

### 不适合的场景
- **超大规模应用**：代码库过于庞大，编译和部署时间过长
- **多团队并行开发**：代码冲突频繁，部署协调困难
- **异构技术需求**：不同模块需要完全不同的技术栈
- **独立扩展需求**：某些模块需要独立水平扩展

## 面试要点

**Q: 单体架构和微服务架构如何选择？**
A: 选择应基于团队规模、业务复杂度和发展阶段：
- 初创阶段优先选择单体架构，降低认知成本和运维复杂度
- 当团队超过一定规模（如康威定律阈值），或某些模块需要独立扩展时，考虑拆分为微服务
- 模块化单体是一种折中方案，在保持单体部署的同时实现代码层面的模块化

**Q: 单体架构的主要优缺点是什么？**
A: 
优点：
- 开发简单，无需处理分布式复杂性
- 测试方便，可以端到端测试
- 部署简单，单个部署单元
- 调试容易，可以本地复现完整系统

缺点：
- 技术栈锁定，难以引入新技术
- 扩展受限，必须整体扩展
- 部署风险高，小改动也需要全量部署
- 代码耦合，随着规模增长维护成本上升

**Q: 什么是模块化单体？有什么好处？**
A: 模块化单体是在单体架构内部实现清晰模块边界的设计。好处包括：
- 代码组织清晰，降低维护成本
- 为未来可能的微服务拆分做准备
- 保持单体部署的简单性
- 通过定义良好的接口降低模块间耦合

**Q: 单体应用如何实现水平扩展？**
A: 可以通过以下方式：
- 无状态设计，支持多实例部署
- 使用负载均衡器（如 Nginx）分发请求
- 共享会话存储（如 Redis）
- 数据库读写分离或使用缓存
- 静态资源使用 CDN

**Q: 单体架构演进为微服务的时机和策略？**
A: 
时机：
- 代码库过于庞大，影响开发效率
- 特定模块需要独立扩展
- 团队规模增长，需要更清晰的职责边界

策略：
- 渐进式拆分，先拆分边界最清晰的模块
- 使用 Strangler Fig 模式逐步替换
- 确保监控和可观测性到位
- 先实现模块化单体，再逐步解耦

## 相关概念

### 数据结构
- 无直接关联

### 算法
- 无直接关联

### 复杂度分析
- [系统复杂度](../system-design/system-complexity.md) - 架构演进中的复杂度管理

### 系统实现
- [微服务架构](./microservices.md) - 单体架构的演进方向
- [分层架构](./layered-architecture.md) - 单体应用常用组织方式
- [清洁架构](./clean-architecture.md) - 单体应用的设计原则
- [六边形架构](./hexagonal-architecture.md) - 模块化单体的实现参考
- [领域驱动设计](../ddd.md) - 模块化边界划分的理论指导
- [Docker](../../cloud-devops/docker.md) - 单体应用的容器化部署
