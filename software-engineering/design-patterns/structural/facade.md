## 版权声明

> **Copyright Notice**: 本文档为个人学习笔记，内容整理自公开技术资料及业界最佳实践。引用内容均已标注来源。如有侵权请联系作者移除。
>
> **License**: 本笔记采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 知识共享许可协议 - 非商业性使用 - 相同方式共享。

---

## 概念 (Concept)

**外观模式 (Facade Pattern)** 是一种结构型设计模式，它为复杂的子系统提供一个统一的、简化的接口。外观模式定义了一个高层接口，使子系统更易于使用。

外观模式的核心思想是**简化接口**。当子系统变得复杂时，外观模式为客户端提供一个简单的入口点，隐藏内部的复杂性。

```
┌─────────────────────────────────────────────────────────────┐
│                    外观模式 (Facade)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Client                                   │
│                      │                                      │
│                      ▼                                      │
│   ┌──────────────────────────────────────┐                  │
│   │           Facade                     │                  │
│   │  ├─ simplified_operation()           │                  │
│   │  │  ├─ subsystem1.operation()        │                  │
│   │  │  ├─ subsystem2.operation()        │                  │
│   │  │  └─ subsystem3.operation()        │                  │
│   └──────────────────────────────────────┘                  │
│           │              │              │                   │
│           ▼              ▼              ▼                   │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│   │ Subsystem1  │ │ Subsystem2  │ │ Subsystem3  │          │
│   │ (复杂实现)  │ │ (复杂实现)  │ │ (复杂实现)  │          │
│   └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                             │
│   目的：简化复杂系统的使用，提供统一入口                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 设计原则 (Principle)

外观模式遵循以下设计原则：

1. **迪米特法则 (Law of Demeter)**：最少知识原则，客户端只需与外观交互
2. **单一职责原则 (Single Responsibility Principle)**：外观负责协调，子系统负责实现
3. **依赖倒置原则 (Dependency Inversion Principle)**：客户端依赖于外观接口而非具体子系统

**外观模式 vs 适配器模式**：
- **外观模式**：简化复杂接口，提供高层接口
- **适配器模式**：转换不兼容接口，保持功能等价

---

## 实现示例 (Example)

### 1. 家庭影院系统

```python
# ============== 子系统：复杂的音视频组件 ==============

class Amplifier:
    """功放"""
    def __init__(self):
        self.volume = 0
    
    def on(self):
        print("功放: 开启")
    
    def off(self):
        print("功放: 关闭")
    
    def set_volume(self, level: int):
        self.volume = level
        print(f"功放: 音量设置为 {level}")
    
    def set_dvd(self, dvd):
        print(f"功放: 切换到DVD播放器 - {dvd}")
    
    def set_surround_sound(self):
        print("功放: 开启环绕立体声")

class DVDPlayer:
    """DVD播放器"""
    def __init__(self):
        self.movie = None
    
    def on(self):
        print("DVD: 开启")
    
    def off(self):
        print("DVD: 关闭")
    
    def play(self, movie: str):
        self.movie = movie
        print(f"DVD: 播放 '{movie}'")
    
    def stop(self):
        print(f"DVD: 停止播放 '{self.movie}'")
    
    def eject(self):
        print("DVD: 弹出光盘")

class Projector:
    """投影仪"""
    def on(self):
        print("投影仪: 开启")
    
    def off(self):
        print("投影仪: 关闭")
    
    def wide_screen_mode(self):
        print("投影仪: 设置为宽屏模式 (16:9)")

class TheaterLights:
    """影院灯光"""
    def dim(self, level: int):
        print(f"灯光: 调暗到 {level}%")
    
    def on(self):
        print("灯光: 开启")

class Screen:
    """屏幕"""
    def down(self):
        print("屏幕: 放下")
    
    def up(self):
        print("屏幕: 升起")

class PopcornPopper:
    """爆米花机"""
    def on(self):
        print("爆米花机: 开启")
    
    def off(self):
        print("爆米花机: 关闭")
    
    def pop(self):
        print("爆米花机: 正在爆爆米花！")

# ============== 外观：简化接口 ==============

class HomeTheaterFacade:
    """家庭影院外观"""
    
    def __init__(self, amp: Amplifier, dvd: DVDPlayer, projector: Projector,
                 lights: TheaterLights, screen: Screen, popper: PopcornPopper):
        self.amp = amp
        self.dvd = dvd
        self.projector = projector
        self.lights = lights
        self.screen = screen
        self.popper = popper
    
    def watch_movie(self, movie: str):
        """一键开始看电影"""
        print("\n=== 准备看电影 ===")
        self.popper.on()
        self.popper.pop()
        
        self.lights.dim(10)
        
        self.screen.down()
        
        self.projector.on()
        self.projector.wide_screen_mode()
        
        self.amp.on()
        self.amp.set_dvd(self.dvd)
        self.amp.set_surround_sound()
        self.amp.set_volume(5)
        
        self.dvd.on()
        self.dvd.play(movie)
        print("=== 电影开始！享受吧！===\n")
    
    def end_movie(self):
        """一键结束看电影"""
        print("\n=== 关闭家庭影院 ===")
        self.popper.off()
        
        self.lights.on()
        
        self.screen.up()
        
        self.projector.off()
        
        self.amp.off()
        
        self.dvd.stop()
        self.dvd.eject()
        self.dvd.off()
        print("=== 已关闭，欢迎下次观影 ===\n")

# ============== 使用示例 ==============

# 创建子系统组件
amp = Amplifier()
dvd = DVDPlayer()
projector = Projector()
lights = TheaterLights()
screen = Screen()
popper = PopcornPopper()

# 创建外观
home_theater = HomeTheaterFacade(amp, dvd, projector, lights, screen, popper)

# 使用简化接口
home_theater.watch_movie("星际穿越")
home_theater.end_movie()
```

### 2. 订单处理系统

```python
from typing import List, Dict

# ============== 复杂的子系统 ==============

class InventorySystem:
    """库存系统"""
    def check_stock(self, product_id: str, quantity: int) -> bool:
        print(f"库存系统: 检查商品 {product_id} 库存 ({quantity}件)")
        return True  # 假设有库存
    
    def reserve(self, product_id: str, quantity: int):
        print(f"库存系统: 预留商品 {product_id} ({quantity}件)")
    
    def release(self, product_id: str, quantity: int):
        print(f"库存系统: 释放商品 {product_id} ({quantity}件)")

class PaymentGateway:
    """支付网关"""
    def process_payment(self, amount: float, card_number: str) -> Dict:
        print(f"支付网关: 处理支付 ¥{amount}")
        return {"success": True, "transaction_id": "TXN123456"}
    
    def refund(self, transaction_id: str):
        print(f"支付网关: 退款 {transaction_id}")

class ShippingService:
    """物流服务"""
    def calculate_shipping(self, address: Dict, weight: float) -> float:
        print(f"物流: 计算运费到 {address['city']}")
        return 10.0
    
    def create_shipment(self, order_id: str, address: Dict) -> str:
        print(f"物流: 创建运单 - 订单 {order_id}")
        return f"TRACK_{order_id}"

class NotificationService:
    """通知服务"""
    def send_email(self, to: str, subject: str, content: str):
        print(f"通知: 发送邮件至 {to} - {subject}")
    
    def send_sms(self, phone: str, message: str):
        print(f"通知: 发送短信至 {phone}")

class OrderRepository:
    """订单存储"""
    def save(self, order: Dict) -> str:
        order_id = f"ORD{hash(str(order)) % 100000}"
        print(f"存储: 保存订单 {order_id}")
        return order_id
    
    def update_status(self, order_id: str, status: str):
        print(f"存储: 更新订单 {order_id} 状态为 {status}")

# ============== 外观 ==============

class OrderFacade:
    """订单处理外观"""
    
    def __init__(self):
        self.inventory = InventorySystem()
        self.payment = PaymentGateway()
        self.shipping = ShippingService()
        self.notification = NotificationService()
        self.repository = OrderRepository()
    
    def place_order(self, customer: Dict, items: List[Dict], 
                    payment_info: Dict) -> Dict:
        """
        一键下单流程：
        1. 检查库存
        2. 预留库存
        3. 计算总价
        4. 处理支付
        5. 创建订单
        6. 安排物流
        7. 发送通知
        """
        try:
            # 1. 检查并预留库存
            total_weight = 0
            for item in items:
                if not self.inventory.check_stock(item['product_id'], item['quantity']):
                    return {"success": False, "error": f"商品 {item['product_id']} 库存不足"}
                self.inventory.reserve(item['product_id'], item['quantity'])
                total_weight += item.get('weight', 0.5) * item['quantity']
            
            # 2. 计算总价
            subtotal = sum(item['price'] * item['quantity'] for item in items)
            shipping_cost = self.shipping.calculate_shipping(customer['address'], total_weight)
            total = subtotal + shipping_cost
            
            # 3. 处理支付
            payment_result = self.payment.process_payment(total, payment_info['card_number'])
            if not payment_result['success']:
                # 支付失败，释放库存
                for item in items:
                    self.inventory.release(item['product_id'], item['quantity'])
                return {"success": False, "error": "支付失败"}
            
            # 4. 创建订单
            order = {
                "customer": customer,
                "items": items,
                "subtotal": subtotal,
                "shipping": shipping_cost,
                "total": total,
                "payment_id": payment_result['transaction_id'],
                "status": "confirmed"
            }
            order_id = self.repository.save(order)
            
            # 5. 安排物流
            tracking_number = self.shipping.create_shipment(order_id, customer['address'])
            
            # 6. 发送通知
            self.notification.send_email(
                customer['email'],
                "订单确认",
                f"您的订单 {order_id} 已确认，运单号: {tracking_number}"
            )
            
            return {
                "success": True,
                "order_id": order_id,
                "tracking_number": tracking_number,
                "total": total
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cancel_order(self, order_id: str, transaction_id: str, items: List[Dict]):
        """一键取消订单"""
        # 1. 退款
        self.payment.refund(transaction_id)
        
        # 2. 释放库存
        for item in items:
            self.inventory.release(item['product_id'], item['quantity'])
        
        # 3. 更新订单状态
        self.repository.update_status(order_id, "cancelled")
        
        print(f"订单 {order_id} 已取消")

# ============== 使用示例 ==============

order_facade = OrderFacade()

customer = {
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "13800138000",
    "address": {"city": "上海", "street": "南京路100号"}
}

items = [
    {"product_id": "BOOK001", "quantity": 2, "price": 50.0, "weight": 0.5},
    {"product_id": "ELEC002", "quantity": 1, "price": 999.0, "weight": 1.5}
]

payment_info = {"card_number": "****1234"}

# 一键下单
result = order_facade.place_order(customer, items, payment_info)
print(f"\n下单结果: {result}\n")
```

### 3. 数据库操作外观

```python
from typing import List, Dict, Optional
import sqlite3

class DatabaseConnection:
    """数据库连接"""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        return self.connection
    
    def close(self):
        if self.connection:
            self.connection.close()

class QueryBuilder:
    """查询构建器"""
    def build_select(self, table: str, columns: List[str], 
                     where: Optional[Dict] = None) -> str:
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table}"
        if where:
            conditions = " AND ".join([f"{k} = ?" for k in where.keys()])
            query += f" WHERE {conditions}"
        return query
    
    def build_insert(self, table: str, data: Dict) -> tuple:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return query, list(data.values())

class CacheLayer:
    """缓存层"""
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str):
        return self.cache.get(key)
    
    def set(self, key: str, value):
        self.cache[key] = value
    
    def invalidate(self, key: str):
        if key in self.cache:
            del self.cache[key]

# ============== 数据库外观 ==============

class DatabaseFacade:
    """数据库操作外观 - 简化数据库操作"""
    
    def __init__(self, db_path: str):
        self.db = DatabaseConnection(db_path)
        self.query_builder = QueryBuilder()
        self.cache = CacheLayer()
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        """执行查询"""
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        # 获取列名
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # 转换为字典列表
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        conn.commit()
        return results
    
    def find_one(self, table: str, where: Dict) -> Optional[Dict]:
        """查找单条记录"""
        cache_key = f"{table}:{where}"
        cached = self.cache.get(cache_key)
        if cached:
            print("[Cache Hit]")
            return cached
        
        query = self.query_builder.build_select(table, [], where)
        results = self.execute(query, tuple(where.values()))
        
        result = results[0] if results else None
        if result:
            self.cache.set(cache_key, result)
        
        return result
    
    def find_all(self, table: str, columns: List[str] = None) -> List[Dict]:
        """查找所有记录"""
        query = self.query_builder.build_select(table, columns or [])
        return self.execute(query)
    
    def insert(self, table: str, data: Dict) -> int:
        """插入记录"""
        query, values = self.query_builder.build_insert(table, data)
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        
        # 使相关缓存失效
        self.cache.invalidate(f"{table}:*")
        
        return cursor.lastrowid
    
    def update(self, table: str, data: Dict, where: Dict):
        """更新记录"""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        
        params = list(data.values()) + list(where.values())
        self.execute(query, tuple(params))
        
        # 使缓存失效
        self.cache.invalidate(f"{table}:{where}")
    
    def delete(self, table: str, where: Dict):
        """删除记录"""
        where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        self.execute(query, tuple(where.values()))
        
        # 使缓存失效
        self.cache.invalidate(f"{table}:{where}")
    
    def transaction(self, operations: List[tuple]):
        """执行事务"""
        conn = self.db.connect()
        try:
            for query, params in operations:
                conn.execute(query, params)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
    
    def close(self):
        """关闭连接"""
        self.db.close()

# ============== 使用示例 ==============

# db = DatabaseFacade("app.db")

# 简单插入
# db.insert("users", {"name": "张三", "email": "zs@example.com"})

# 简单查询
# user = db.find_one("users", {"id": 1})

# 关闭
# db.close()
```

---

## 使用场景 (Use Cases)

| 场景 | 说明 |
|------|------|
| 复杂子系统 | 为复杂的类库或框架提供简化接口 |
| 分层架构 | 为各层提供统一的访问点 |
| 遗留系统 | 为遗留代码提供现代接口 |
| 多系统整合 | 统一多个系统的访问方式 |
| 测试 | 为测试提供简化的Mock接口 |

---

## 面试要点 (Interview Points)

**Q1: 外观模式和适配器模式的区别？**

> - **外观模式**：简化复杂接口，提供高层接口，目的是"简化"
> - **适配器模式**：转换不兼容接口，保持功能等价，目的是"适配"
>
> 外观是"统一入口"，适配器是"翻译官"。

**Q2: 外观模式和中介者模式的区别？**

> - **外观模式**：单向简化，客户端通过外观访问子系统，子系统不感知外观
> - **中介者模式**：双向协调，组件通过中介者互相通信，组件解耦
>
> 外观是"简化接口"，中介者是"协调通信"。

**Q3: 外观模式的优缺点？**

> **优点**：
> - 简化复杂系统的使用
> - 将客户端与子系统解耦
> - 分层架构更清晰
>
> **缺点**：
> - 可能成为上帝对象
> - 可能限制客户端使用子系统的高级功能
> - 需要维护外观类和子系统的同步

**Q4: 何时不应该使用外观模式？**

> 当：
> 1. 子系统本身很简单
> 2. 需要直接使用子系统的灵活性和高级功能
> 3. 外观会频繁变更，难以维护

---

## 相关概念 (Related Concepts)

外观模式与其他设计模式和软件工程概念的关联：

### 结构型模式 (Structural Patterns)

外观模式属于结构型设计模式，与其他结构型模式密切相关：

- **[适配器模式](./adapter.md)** - 接口转换，外观模式用于简化接口，适配器用于转换不兼容接口
- **[桥接模式](./bridge.md)** - 抽象与实现分离，外观模式在此基础上提供统一入口
- **[组合模式](./composite.md)** - 树形结构统一处理，外观模式可简化对复杂组合结构的访问
- **[装饰器模式](./decorator.md)** - 动态添加职责，外观模式可与装饰器结合提供更丰富的简化接口
- **[享元模式](./flyweight.md)** - 共享对象减少内存，外观模式可管理享元对象的创建和访问
- **[代理模式](./proxy.md)** - 控制对象访问，外观模式关注简化接口，代理模式关注访问控制

### 行为型模式 (Behavioral Patterns)

- **[中介者模式](../behavioral/mediator.md)** - 对象间协调通信，与外观模式都起到简化交互的作用，但中介者是双向协调
- **[策略模式](../behavioral/strategy.md)** - 算法封装，外观模式内部可使用策略模式处理不同子系统的行为
- **[观察者模式](../behavioral/observer.md)** - 事件订阅机制，外观模式可封装复杂的观察者注册和通知逻辑

### 创建型模式 (Creational Patterns)

- **[单例模式](../creational/singleton.md)** - 外观类通常设计为单例，确保系统中只有一个统一入口
- **[工厂模式](../creational/factory.md)** - 用于创建外观对象或外观管理的子系统对象

### 设计原则与架构

- **[SOLID原则](../../solid-principles.md)** - 外观模式体现了单一职责原则(SRP)和依赖倒置原则(DIP)
- **[设计模式总览](../../design-patterns.md)** - 了解外观模式在整个设计模式体系中的位置
- **[分层架构](../../architecture-patterns.md)** - 外观模式常用于分层架构中作为层与层之间的接口

### 软件工程概念

- **迪米特法则 (Law of Demeter)** - 外观模式的核心原则，最少知识原则的体现
- **API设计** - 外观模式是良好API设计的重要实践，提供清晰、简洁的接口
- **封装与抽象** - 外观模式通过封装子系统复杂性实现更高层次的抽象


## 相关引用 (References)

- 返回：[设计模式总览](../../design-patterns.md)
- 相关：[适配器模式](./adapter.md) - 接口转换
- 相关：[中介者模式](../behavioral/mediator.md) - 对象协调
- 原理：[SOLID原则](../../solid-principles.md)
