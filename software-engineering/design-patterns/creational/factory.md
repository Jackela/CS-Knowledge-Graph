# 工厂模式 (Factory Pattern)



## 概念



工厂模式（Factory Pattern）是一种**创建型设计模式**，定义了一个创建对象的接口，让子类决定实例化哪个类。工厂方法使类的实例化推迟到子类。



> **核心思想**: 将对象的创建与使用分离，客户端无需知道具体类的名称，只需知道所需产品的接口。



```

┌─────────────────┐         ┌─────────────────┐

│     Client      │────────▶│  Product(接口)  │

└─────────────────┘         └────────┬────────┘

                                     │

                      ┌──────────────┼──────────────┐

                      ▼              ▼              ▼

               ┌──────────┐   ┌──────────┐   ┌──────────┐

               │ ProductA │   │ ProductB │   │ ProductC │

               └──────────┘   └──────────┘   └──────────┘

```



---



## 原理



### 为什么需要工厂模式？



1. **解耦**: 将对象创建逻辑与业务逻辑分离

2. **扩展性**: 新增产品只需添加新工厂，无需修改现有代码（开闭原则）

3. **隐藏复杂性**: 客户端不需要知道创建对象的复杂过程

4. **统一管理**: 集中管理对象创建，便于统计和监控



### 三种工厂模式



| 模式 | 复杂度 | 适用场景 |

|------|--------|----------|

| 简单工厂 | 低 | 产品种类少，变化不频繁 |

| 工厂方法 | 中 | 单一产品族，多产品等级 |

| 抽象工厂 | 高 | 多产品族，产品等级结构复杂 |



---



## 实现方式



### 1. 简单工厂模式（静态工厂）



```python

from abc import ABC, abstractmethod

from enum import Enum



# 产品接口

class PaymentMethod(ABC):

    @abstractmethod

    def pay(self, amount: float):

        pass



# 具体产品

class AliPay(PaymentMethod):

    def pay(self, amount: float):

        return f"支付宝支付 {amount} 元"



class WeChatPay(PaymentMethod):

    def pay(self, amount: float):

        return f"微信支付 {amount} 元"



class CreditCardPay(PaymentMethod):

    def pay(self, amount: float):

        return f"信用卡支付 {amount} 元"



# 简单工厂

class PaymentFactory:

    @staticmethod

    def create_payment(payment_type: str) -> PaymentMethod:

        if payment_type == "alipay":

            return AliPay()

        elif payment_type == "wechat":

            return WeChatPay()

        elif payment_type == "creditcard":

            return CreditCardPay()

        else:

            raise ValueError(f"不支持的支付方式: {payment_type}")



# 使用

payment = PaymentFactory.create_payment("alipay")

result = payment.pay(100.0)

```



### 2. 工厂方法模式



```python

from abc import ABC, abstractmethod



# 产品接口

class Document(ABC):

    @abstractmethod

    def open(self):

        pass



    @abstractmethod

    def save(self):

        pass



# 具体产品

class PDFDocument(Document):

    def open(self):

        return "打开 PDF 文档"



    def save(self):

        return "保存 PDF 文档"



class WordDocument(Document):

    def open(self):

        return "打开 Word 文档"



    def save(self):

        return "保存 Word 文档"



class ExcelDocument(Document):

    def open(self):

        return "打开 Excel 文档"



    def save(self):

        return "保存 Excel 文档"



# 工厂接口

class DocumentFactory(ABC):

    @abstractmethod

    def create_document(self) -> Document:

        pass



# 具体工厂

class PDFFactory(DocumentFactory):

    def create_document(self) -> Document:

        return PDFDocument()



class WordFactory(DocumentFactory):

    def create_document(self) -> Document:

        return WordDocument()



class ExcelFactory(DocumentFactory):

    def create_document(self) -> Document:

        return ExcelDocument()



# 使用

factory = PDFFactory()

doc = factory.create_document()

doc.open()

```



### 3. Java 实现示例



```java

// 产品接口

public interface DatabaseConnection {

    void connect();

    void disconnect();

}



// 具体产品

public class MySQLConnection implements DatabaseConnection {

    @Override

    public void connect() {

        System.out.println("连接到 MySQL 数据库");

    }



    @Override

    public void disconnect() {

        System.out.println("断开 MySQL 连接");

    }

}



public class PostgreSQLConnection implements DatabaseConnection {

    @Override

    public void connect() {

        System.out.println("连接到 PostgreSQL 数据库");

    }



    @Override

    public void disconnect() {

        System.out.println("断开 PostgreSQL 连接");

    }

}



// 工厂接口

public interface ConnectionFactory {

    DatabaseConnection createConnection();

}



// 具体工厂

public class MySQLFactory implements ConnectionFactory {

    @Override

    public DatabaseConnection createConnection() {

        return new MySQLConnection();

    }

}



public class PostgreSQLFactory implements ConnectionFactory {

    @Override

    public DatabaseConnection createConnection() {

        return new PostgreSQLConnection();

    }

}



// 使用

ConnectionFactory factory = new MySQLFactory();

DatabaseConnection conn = factory.createConnection();

conn.connect();

```



---



## 示例



### 日志记录器工厂



```python

from abc import ABC, abstractmethod

from datetime import datetime



# 产品接口

class Logger(ABC):

    @abstractmethod

    def log(self, message: str):

        pass



# 具体产品

class FileLogger(Logger):

    def __init__(self, filename: str):

        self.filename = filename



    def log(self, message: str):

        with open(self.filename, 'a') as f:

            f.write(f"[{datetime.now()}] {message}\n")



class ConsoleLogger(Logger):

    def log(self, message: str):

        print(f"[{datetime.now()}] {message}")



class DatabaseLogger(Logger):

    def log(self, message: str):

        # 写入数据库

        print(f"写入数据库: {message}")



# 工厂

class LoggerFactory:

    _loggers = {}



    @classmethod

    def get_logger(cls, logger_type: str, **kwargs) -> Logger:

        if logger_type not in cls._loggers:

            if logger_type == "file":

                cls._loggers[logger_type] = FileLogger(kwargs.get('filename', 'app.log'))

            elif logger_type == "console":

                cls._loggers[logger_type] = ConsoleLogger()

            elif logger_type == "database":

                cls._loggers[logger_type] = DatabaseLogger()

        return cls._loggers[logger_type]



# 使用

logger = LoggerFactory.get_logger("console")

logger.log("应用程序启动")

```



---



## 面试要点



1. **三种工厂模式的区别**

   - 简单工厂：一个工厂类创建所有产品，违反开闭原则

   - 工厂方法：每个产品对应一个工厂，符合开闭原则

   - 抽象工厂：创建产品族，适合多维度产品



2. **优缺点**

   - **优点**: 解耦、易于扩展、符合单一职责原则

   - **缺点**: 增加类的数量、代码复杂度提高



3. **适用场景**

   - 对象创建逻辑复杂

   - 需要根据不同条件创建不同对象

   - 需要隐藏对象创建细节



4. **与抽象工厂的区别**

   - 工厂方法：针对单一产品等级结构

   - 抽象工厂：针对产品族（多个产品等级结构）



---



## 相关概念



### 数据结构

- [接口与抽象类](../../oop-design.md) - 多态的基础

- [Hash Table](../../../computer-science/data-structures/hash-table.md) - 工厂注册表实现



### 设计模式

- [抽象工厂](./abstract-factory.md) - 产品族创建

- [单例模式](./singleton.md) - 工厂本身常使用单例

- [建造者模式](./builder.md) - 复杂对象构建

- [策略模式](../behavioral/strategy.md) - 运行时选择算法



### 复杂度分析

- [时间复杂度](../../../references/time-complexity.md) - 对象创建开销

- [空间复杂度](../../../references/space-complexity.md) - 工厂类内存占用



### 系统实现

- [依赖注入](../../architecture-patterns/dependency-injection.md) - 现代框架中的工厂应用

- [数据库连接池](../../../computer-science/databases/indexing.md) - 连接工厂

