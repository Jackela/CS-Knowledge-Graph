# 建造者模式 (Builder Pattern)



## 概念



建造者模式（Builder Pattern）是一种**创建型设计模式**，用于将一个复杂对象的构建与其表示分离，使得同样的构建过程可以创建不同的表示。



> **核心思想**: 分步骤构建对象，将复杂对象的构建过程分解为多个简单步骤。



```

┌─────────────────────────────────────────────────────────────────┐

│                         建造者模式                              │

├─────────────────────────────────────────────────────────────────┤

│                                                                 │

│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │

│   │   Director  │─────▶│   Builder   │◀─────│  Concrete   │    │

│   │   (指挥者)   │      │   (抽象)    │      │   Builder   │    │

│   │             │      │             │      │   (具体)    │    │

│   │ construct() │      │ buildPart() │      │ buildPart() │    │

│   └─────────────┘      └─────────────┘      └──────┬──────┘    │

│                                                    │            │

│                                                    ▼            │

│                                             ┌─────────────┐    │

│                                             │   Product   │    │

│                                             │   (产品)    │    │

│                                             └─────────────┘    │

└─────────────────────────────────────────────────────────────────┘

```



---



## 原理



### 为什么需要建造者模式？



1. **参数过多**: 构造函数参数超过4-5个时，可读性差

2. **可选参数**: 大量可选参数，组合爆炸

3. **构建顺序**: 对象构建需要特定步骤顺序

4. **不可变对象**: 构建完成后对象不可修改



### 四种实现方式



| 方式 | 特点 | 适用场景 |

|------|------|----------|

| 经典建造者 | Director + Builder + Product | 复杂构建流程 |

| 流式接口 | 链式调用，返回 this | 简单配置对象 |

| 静态内部类 | 产品类内含 Builder | Java 常用 |

| 分步工厂 | 多个工厂方法逐步构建 | 复杂状态机 |



---



## 实现方式



### 1. 经典建造者模式



```python

from abc import ABC, abstractmethod



# 产品：计算机

class Computer:

    def __init__(self):

        self.cpu = None

        self.memory = None

        self.storage = None

        self.gpu = None



    def __str__(self):

        return f"Computer(CPU={self.cpu}, Memory={self.memory}, Storage={self.storage}, GPU={self.gpu})"



# 抽象建造者

class ComputerBuilder(ABC):

    @abstractmethod

    def build_cpu(self):

        pass



    @abstractmethod

    def build_memory(self):

        pass



    @abstractmethod

    def build_storage(self):

        pass



    @abstractmethod

    def build_gpu(self):

        pass



    @abstractmethod

    def get_result(self) -> Computer:

        pass



# 具体建造者：游戏电脑

class GamingComputerBuilder(ComputerBuilder):

    def __init__(self):

        self.computer = Computer()



    def build_cpu(self):

        self.computer.cpu = "Intel i9-13900K"



    def build_memory(self):

        self.computer.memory = "64GB DDR5"



    def build_storage(self):

        self.computer.storage = "2TB NVMe SSD"



    def build_gpu(self):

        self.computer.gpu = "RTX 4090"



    def get_result(self) -> Computer:

        return self.computer



# 具体建造者：办公电脑

class OfficeComputerBuilder(ComputerBuilder):

    def __init__(self):

        self.computer = Computer()



    def build_cpu(self):

        self.computer.cpu = "Intel i5-13400"



    def build_memory(self):

        self.computer.memory = "16GB DDR4"



    def build_storage(self):

        self.computer.storage = "512GB SSD"



    def build_gpu(self):

        self.computer.gpu = "Integrated"



    def get_result(self) -> Computer:

        return self.computer



# 指挥者

class ComputerDirector:

    def __init__(self, builder: ComputerBuilder):

        self.builder = builder



    def construct(self) -> Computer:

        self.builder.build_cpu()

        self.builder.build_memory()

        self.builder.build_storage()

        self.builder.build_gpu()

        return self.builder.get_result()



# 使用

gaming_builder = GamingComputerBuilder()

director = ComputerDirector(gaming_builder)

gaming_pc = director.construct()

print(gaming_pc)

```



### 2. 流式接口（Fluent Interface）



```python

class HttpRequest:

    def __init__(self):

        self.method = "GET"

        self.url = ""

        self.headers = {}

        self.body = None

        self.timeout = 30



    class Builder:

        def __init__(self):

            self._request = HttpRequest()



        def method(self, method: str):

            self._request.method = method

            return self



        def url(self, url: str):

            self._request.url = url

            return self



        def header(self, key: str, value: str):

            self._request.headers[key] = value

            return self



        def body(self, body: str):

            self._request.body = body

            return self



        def timeout(self, seconds: int):

            self._request.timeout = seconds

            return self



        def build(self):

            return self._request



    def __str__(self):

        return f"{self.method} {self.url} (timeout={self.timeout}s)"



# 使用

request = (HttpRequest.Builder()

           .method("POST")

           .url("https://api.example.com/users")

           .header("Content-Type", "application/json")

           .header("Authorization", "Bearer token123")

           .body('{"name": "John"}')

           .timeout(60)

           .build())



print(request)

```



### 3. Java 静态内部类实现



```java

// 产品类

public class User {

    private final String username;

    private final String email;

    private final int age;

    private final String phone;

    private final String address;



    // 私有构造函数，只能通过 Builder 创建

    private User(Builder builder) {

        this.username = builder.username;

        this.email = builder.email;

        this.age = builder.age;

        this.phone = builder.phone;

        this.address = builder.address;

    }



    // 静态内部类 Builder

    public static class Builder {

        // 必需参数

        private final String username;

        private final String email;



        // 可选参数，设置默认值

        private int age = 0;

        private String phone = "";

        private String address = "";



        public Builder(String username, String email) {

            this.username = username;

            this.email = email;

        }



        public Builder age(int age) {

            this.age = age;

            return this;

        }



        public Builder phone(String phone) {

            this.phone = phone;

            return this;

        }



        public Builder address(String address) {

            this.address = address;

            return this;

        }



        public User build() {

            return new User(this);

        }

    }




    @Override

    public String toString() {

        return String.format("User{username='%s', email='%s', age=%d}", 

                           username, email, age);

    }

}



// 使用

User user = new User.Builder("john_doe", "john@example.com")

    .age(30)

    .phone("123-456-7890")

    .address("123 Main St")

    .build();

```



---



## 示例



### SQL 查询构建器



```python

class SQLQuery:

    def __init__(self):

        self.select = []

        self.from_table = ""

        self.where = []

        self.order_by = ""

        self.limit = 0



    class Builder:

        def __init__(self):

            self._query = SQLQuery()



        def select(self, *columns):

            self._query.select = list(columns) if columns else ["*"]

            return self



        def from_table(self, table: str):

            self._query.from_table = table

            return self



        def where(self, condition: str):

            self._query.where.append(condition)

            return self



        def order_by(self, column: str, direction="ASC"):

            self._query.order_by = f"{column} {direction}"

            return self



        def limit(self, n: int):

            self._query.limit = n

            return self



        def build(self):

            query = f"SELECT {', '.join(self._query.select)} FROM {self._query.from_table}"

            if self._query.where:

                query += " WHERE " + " AND ".join(self._query.where)

            if self._query.order_by:

                query += f" ORDER BY {self._query.order_by}"

            if self._query.limit:

                query += f" LIMIT {self._query.limit}"

            return query



# 使用

sql = (SQLQuery.Builder()

       .select("name", "email", "age")

       .from_table("users")

       .where("age > 18")

       .where("status = 'active'")

       .order_by("created_at", "DESC")

       .limit(10)

       .build())



print(sql)

# 输出: SELECT name, email, age FROM users WHERE age > 18 AND status = 'active' ORDER BY created_at DESC LIMIT 10

```



---



## 面试要点



1. **与工厂模式的区别**

   - 工厂：关注创建什么对象（what）

   - 建造者：关注如何创建对象（how），分步骤构建



2. **使用场景**

   - 构造函数参数过多（>4个）

   - 需要创建不可变对象

   - 对象构建有复杂步骤或顺序要求

   - 需要不同的表示（同一个构建过程创建不同形式）



3. **优缺点**

   - **优点**: 更好的可读性、可选参数灵活、可复用构建代码

   - **缺点**: 代码量增加、需要创建多个类



4. **实际应用**

   - Java StringBuilder

   - OkHttp Request.Builder

   - Retrofit 配置

   - Lombok @Builder



---



## 相关概念



### 数据结构

- [链表](../../../computer-science/data-structures/linked-list.md) - 构建过程的链式结构



### 设计模式

- [工厂模式](./factory.md) - 对象创建

- [单例模式](./singleton.md) - Builder 可返回单例

- [原型模式](./prototype.md) - 基于现有对象创建

- [策略模式](../behavioral/strategy.md) - 不同构建策略



### 复杂度分析

- [时间复杂度](../../../references/time-complexity.md) - 构建步骤的时间开销

- [空间复杂度](../../../references/space-complexity.md) - 中间对象内存占用



### 系统实现

- [Effective Java](https://www.oracle.com/java/technologies/effective-java.html) - Item 2: Builder Pattern

- [Lombok](../../../software-engineering/tools/lombok.md) - @Builder 注解

- [依赖注入](../../architecture-patterns/dependency-injection.md) - 对象配置

